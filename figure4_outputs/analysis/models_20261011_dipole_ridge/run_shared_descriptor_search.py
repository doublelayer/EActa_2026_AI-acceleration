#!/usr/bin/env python3
"""Nested grouped search with one descriptor set and model family for all targets."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from descriptor_catalog import catalog

HERE = Path(__file__).resolve().parent
OUT = HERE / "shared_descriptor_search"
TARGETS = ("G_OH", "G_O", "G_OOH")
SEED = 20261008
ALPHAS = (0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
COMPONENTS = (1, 2, 3, 4, 6, 8, 10, 12)
FAMILIES = ("ridge",)


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def key(row):
    return row["name"], row["ads_site"]


def folds(names, seed, count=4):
    names = sorted(set(names))
    np.random.default_rng(seed).shuffle(names)
    return [set(names[i::count]) for i in range(count)]


def preprocess(train, held):
    train, held = train.copy(), held.copy()
    finite = np.isfinite(train)
    medians = np.asarray([np.median(train[finite[:, j], j]) if finite[:, j].any() else 0.0
                          for j in range(train.shape[1])])
    train = np.where(finite, train, medians)
    held = np.where(np.isfinite(held), held, medians)
    means, scales = train.mean(axis=0), train.std(axis=0)
    scales = np.where(scales > 1e-12, scales, 1.0)
    return (train - means) / scales, (held - means) / scales, medians, means, scales


def spectral_coefficients(x, centered_y, alphas):
    u, singular, vt = np.linalg.svd(x, full_matrices=False)
    projection = u.T @ centered_y
    threshold = np.finfo(float).eps * max(x.shape) * (singular[0] if len(singular) else 1.0)
    coefficients = {}
    for alpha in alphas:
        if alpha == 0:
            factor = np.divide(1.0, singular, out=np.zeros_like(singular), where=singular > threshold)
        else:
            factor = singular / (singular ** 2 + alpha)
        coefficients[alpha] = vt.T @ (factor * projection)
    return coefficients


def pls_coefficients(x, centered_y, requested):
    # Single-response PLS with regression deflation (NIPALS/PLS1).
    residual_x, residual_y = x.copy(), centered_y.copy()
    weights, loadings, responses = [], [], []
    coefficients = {}
    for component in range(1, min(max(requested), x.shape[1], x.shape[0] - 1) + 1):
        weight = residual_x.T @ residual_y
        norm = np.linalg.norm(weight)
        if norm < 1e-12:
            break
        weight /= norm
        score = residual_x @ weight
        denominator = float(score @ score)
        if denominator < 1e-12:
            break
        loading = residual_x.T @ score / denominator
        response = float(residual_y @ score / denominator)
        weights.append(weight)
        loadings.append(loading)
        responses.append(response)
        residual_x -= np.outer(score, loading)
        residual_y -= score * response
        if component in requested:
            w, p = np.column_stack(weights), np.column_stack(loadings)
            coefficients[component] = w @ np.linalg.lstsq(p.T @ w, np.asarray(responses), rcond=None)[0]
    return coefficients


def fit_batch(raw_train, raw_held, y, families=FAMILIES):
    z, zh, median, mean, scale = preprocess(raw_train, raw_held)
    intercept = float(y.mean())
    centered_y = y - intercept
    coefficients, predictions = {}, {}
    if "ridge" in families or "ols" in families:
        alphas = ([0.0] if "ols" in families else []) + (list(ALPHAS) if "ridge" in families else [])
        for alpha, coefficient in spectral_coefficients(z, centered_y, alphas).items():
            setting = ("ols", 0.0) if alpha == 0 else ("ridge", alpha)
            coefficients[setting] = coefficient
            predictions[setting] = zh @ coefficient + intercept
    if "pls" in families:
        for count, coefficient in pls_coefficients(z, centered_y, COMPONENTS).items():
            setting = ("pls", count)
            coefficients[setting] = coefficient
            predictions[setting] = zh @ coefficient + intercept
    state = dict(intercept=intercept, median=median, mean=mean, scale=scale,
                 coefficients=coefficients)
    return predictions, state


def feature_sets(pool):
    selection = json.loads((HERE / "current_descriptor_selection.json").read_text(encoding="utf-8"))
    features = selection["shared_descriptors"]
    if len(features) != len(set(features)) or not set(features) <= set(pool):
        raise ValueError("selected descriptors must be unique members of the calculated pool")
    candidates = selection.get("candidate_descriptor_sets", {"current_shared_descriptors": features})
    if any(len(fs) != len(set(fs)) or not set(fs) <= set(pool) or "metal_metal_distance_A" not in fs
           for fs in candidates.values()):
        raise ValueError("candidate sets must have unique calculated inputs and metal separation")
    return candidates


def select_choice(choices, selection):
    reference = selection.get("selection_reference_set")
    if reference:
        baseline = next(c for c in choices if c["block"] == reference)
        choices = [c for c in choices if all(c["selected"][t]["mse"] <= baseline["selected"][t]["mse"] + 1e-12
                                            for t in TARGETS)]
    return choices[0]


def choose_targets(data, candidates, seeds, families=FAMILIES, allowed_parameters=None):
    union_names = {name for target in data.values() for name in target["names"]}
    partitions = [held for seed in seeds for held in folds(union_names, seed)]
    choices = []
    for block, columns in candidates.items():
        target_scores = {}
        for target, d in data.items():
            accumulated, counts = {}, {}
            for held_names in partitions:
                held = np.asarray([name in held_names for name in d["names"]])
                if not held.any() or held.all():
                    raise ValueError("empty inner grouped fold")
                pp, _ = fit_batch(d["x"][~held][:, columns], d["x"][held][:, columns], d["y"][~held], families)
                for setting, predicted in pp.items():
                    accumulated[setting] = accumulated.get(setting, 0.0) + float(np.sum((predicted - d["y"][held]) ** 2))
                    counts[setting] = counts.get(setting, 0) + len(predicted)
            expected = len(d["y"]) * len(seeds)
            target_scores[target] = {setting: value / expected for setting, value in accumulated.items()
                                     if counts[setting] == expected and np.isfinite(value)}
        for family in families:
            selected = {}
            for target in data:
                options = [(score, setting) for setting, score in target_scores[target].items()
                           if setting[0] == family and (allowed_parameters is None
                           or setting[1] in allowed_parameters[family])]
                if not options:
                    break
                mse, setting = min(options, key=lambda v: (v[0], v[1][1]))
                selected[target] = dict(setting=setting, mse=mse)
            if len(selected) != len(data):
                continue
            cost = float(np.mean([s["mse"] / np.var(data[t]["y"]) for t, s in selected.items()]))
            choices.append(dict(block=block, columns=columns, family=family, cost=cost, selected=selected))
    choices.sort(key=lambda c: (c["cost"], len(c["columns"]), FAMILIES.index(c["family"]), c["block"]))
    return choices


def metric(truth, predicted):
    truth, predicted = np.asarray(truth), np.asarray(predicted)
    errors = predicted - truth
    return dict(R2=float(1 - np.sum(errors ** 2) / np.sum((truth - truth.mean()) ** 2)),
                RMSE_eV=float(np.sqrt(np.mean(errors ** 2))), MAE_eV=float(np.mean(np.abs(errors))),
                pearson_r=float(np.corrcoef(truth, predicted)[0, 1]))


def prediction_rows(target, method, keys, truth, predicted, **extra):
    return [dict(target=target, method=method, name=k[0], ads_site=k[1], observed_eV=float(y),
                 predicted_eV=float(p), error_eV=float(p - y), **extra) for k, y, p in zip(keys, truth, predicted)]


def load_data():
    configuration = json.loads((HERE / "run_config.json").read_text(encoding="utf-8"))
    pool = configuration["feature_sets"]["G_OH"]["dipole"]
    if any("electronegativity" in f or "heteroatom_distance" in f for f in pool):
        raise ValueError("the search input must exclude empirical and raw ligand-distance predictors")
    definitions = catalog()
    if set(pool) != set(definitions):
        raise ValueError("descriptor catalogue and current full descriptor pool differ")
    if (HERE / "current_site_features.csv").exists():
        from analyze_descriptor_correlations import extended_catalog
        definitions = extended_catalog()
        pool = list(definitions)
    descriptor_rows = read(HERE / ("current_site_features.csv" if (HERE / "current_site_features.csv").exists() else "dipole_site_features.csv"))
    raw = {key(r): r for r in descriptor_rows}
    labels = {key(r): r for r in read(HERE.parents[1] / "extracted" / "orr_analysis_energies.csv")}
    cohort = read(HERE / "cohort_membership.csv")
    split = json.loads((HERE / "representative_split/split_config.json").read_text(encoding="utf-8"))
    quality_keys = {key(r) for r in read(HERE / "representative_split/data_quality_exclusion_ledger.csv")
                    if r["included_after_geometry_checks"] == "True"}
    forbidden_names = set(split.get("excluded_whole_structures", []))
    union_names = {r["name"] for r in cohort if r["role"] == "training"}
    saved_folds = {(repeat, name): i + 1 for repeat in (1, 2, 3)
                   for i, held in enumerate(folds(union_names, SEED + repeat * 10007, 5)) for name in held}
    data = {}
    cohort_sets = []
    for target in TARGETS:
        train_keys = sorted({key(r) for r in cohort if r["target"] == target and r["role"] == "training"})
        val_keys = sorted({key(r) for r in cohort if r["target"] == target and r["role"] == "validation"})
        if set(train_keys) | set(val_keys) != quality_keys:
            raise ValueError("model cohort must equal the complete eligible data-quality cohort")
        if {k[0] for k in train_keys + val_keys} & forbidden_names:
            raise ValueError("a structure excluded by the distance rule re-entered the model cohort")
        if {k[0] for k in train_keys} & {k[0] for k in val_keys}:
            raise ValueError("training/validation structure overlap")
        if (len(train_keys), len({k[0] for k in train_keys})) != (split["training_site_rows"], split["training_structures"]):
            raise ValueError("training cohort does not match the representative split")
        if len(val_keys) != split["validation_site_rows"] or {k[0] for k in val_keys} != set(split["validation_structures"]):
            raise ValueError("validation cohort does not match the representative split")
        cohort_sets.append((set(train_keys), set(val_keys)))
        data[target] = dict(keys=train_keys, names=[k[0] for k in train_keys],
            x=np.asarray([[float(raw[k].get(f) or "nan") for f in pool] for k in train_keys]),
            y=np.asarray([float(labels[k][target]) for k in train_keys]),
            validation_keys=val_keys,
            validation_x=np.asarray([[float(raw[k].get(f) or "nan") for f in pool] for k in val_keys]),
            validation_y=np.asarray([float(labels[k][target]) for k in val_keys]))
    if any(c != cohort_sets[0] for c in cohort_sets[1:]):
        raise ValueError("all targets must use the same training and validation sites")
    return pool, definitions, data, saved_folds, True, cohort


def main():
    OUT.mkdir(exist_ok=True)
    pool, definitions, data, outer_folds, aligned, cohort = load_data()
    sets = feature_sets(pool)
    selection_configuration = json.loads((HERE / "current_descriptor_selection.json").read_text(encoding="utf-8"))
    candidates = {name: [pool.index(f) for f in features] for name, features in sets.items()}
    print(f"Searching {len(candidates)} shared sets and {len(FAMILIES)} model families", flush=True)
    nested_predictions, selection_rows, inner_rows = [], [], []
    candidate_predictions = {}
    for repeat in (1, 2, 3):
        for fold in range(1, 6):
            masks = {t: np.asarray([outer_folds[(repeat, name)] == fold for name in d["names"]]) for t, d in data.items()}
            training = {t: dict(x=d["x"][~masks[t]], y=d["y"][~masks[t]],
                                names=[n for n, held in zip(d["names"], masks[t]) if not held]) for t, d in data.items()}
            seeds = [SEED + repeat * 10007 + fold * 101]
            choices = choose_targets(training, candidates, seeds)
            best = select_choice(choices, selection_configuration)
            print(f"Repeat {repeat}/3 fold {fold}/5: {best['family']}, {len(best['columns'])} shared descriptors, "
                  f"inner normalized MSE {best['cost']:.3f}", flush=True)
            for choice in choices:
                for target, selection in choice["selected"].items():
                    inner_rows.append(dict(repeat=repeat, fold=fold, target=target, descriptor_set=choice["block"],
                        family=choice["family"], parameter=selection["setting"][1], descriptor_count=len(choice["columns"]),
                        joint_normalized_MSE=choice["cost"], inner_RMSE_eV=float(np.sqrt(selection["mse"]))))
                    d, held = data[target], masks[target]
                    predicted, _ = fit_batch(d["x"][~held][:, choice["columns"]], d["x"][held][:, choice["columns"]],
                                             d["y"][~held], (choice["family"],))
                    pp = predicted[selection["setting"]]
                    bucket = candidate_predictions.setdefault((choice["block"], choice["family"], target, repeat), [[], []])
                    bucket[0].extend(d["y"][held]); bucket[1].extend(pp)
                    if choice is best:
                        selection_rows.append(dict(repeat=repeat, fold=fold, target=target,
                            descriptor_set=choice["block"], family=choice["family"], parameter=selection["setting"][1],
                            descriptor_count=len(choice["columns"]), joint_normalized_MSE=choice["cost"]))
                        nested_predictions.extend(prediction_rows(target, "nested_shared_search",
                            [k for k, h in zip(d["keys"], held) if h], d["y"][held], pp, repeat=repeat, fold=fold))
    print("Selecting final shared descriptor set and model family using training-only grouped CV", flush=True)
    final_choices = choose_targets(data, candidates, [SEED + 811 + i * 10007 for i in range(3)])
    selected = select_choice(final_choices, selection_configuration)
    features = [pool[i] for i in selected["columns"]]
    print(f"Final choice: {selected['family']}, {len(features)} descriptors, {selected['block']}", flush=True)
    final_scores = []
    for choice in final_choices:
        for target, selection in choice["selected"].items():
            final_scores.append(dict(target=target, descriptor_set=choice["block"], family=choice["family"],
                parameter=selection["setting"][1], descriptor_count=len(choice["columns"]),
                joint_normalized_MSE=choice["cost"], training_inner_RMSE_eV=float(np.sqrt(selection["mse"]))))
    write("final_training_search.csv", final_scores)
    coefficients, prep, validation_predictions, final_models = [], [], [], {}
    for target, d in data.items():
        setting = selected["selected"][target]["setting"]
        predictions, state = fit_batch(d["x"][:, selected["columns"]], d["validation_x"][:, selected["columns"]],
                                       d["y"], (selected["family"],))
        validation_predictions.extend(prediction_rows(target, "selected_shared_model", d["validation_keys"],
                                                      d["validation_y"], predictions[setting]))
        beta = state["coefficients"][setting]
        size = len(features)
        linear = beta[:size] / state["scale"]
        intercept = state["intercept"] - float(np.sum(beta[:size] * state["mean"] / state["scale"]))
        final_models[target] = dict(family=selected["family"], parameter=setting[1], descriptor_keys=features,
            descriptor_names=[definitions[f]["name"] for f in features], raw_intercept=intercept,
            raw_linear_coefficients=linear.tolist(),
            imputation_medians=state["median"].tolist(), standardized_intercept=state["intercept"],
            standardized_coefficients=beta.tolist(), training_structures=len(set(d["names"])), training_site_rows=len(d["y"]))
        coefficients.append(dict(target=target, index=0, readable_name="Intercept", descriptor_key="intercept",
                                 raw_linear_coefficient=intercept,
                                 standardized_linear_coefficient=state["intercept"]))
        for i, feature in enumerate(features):
            coefficients.append(dict(target=target, index=i + 1, readable_name=definitions[feature]["name"], descriptor_key=feature,
                raw_linear_coefficient=float(linear[i]),
                standardized_linear_coefficient=float(beta[i])))
            prep.append(dict(target=target, index=i + 1, readable_name=definitions[feature]["name"], descriptor_key=feature,
                median=float(state["median"][i]), mean=float(state["mean"][i]), scale=float(state["scale"][i])))
    metrics = []
    for method, rows in (("nested_shared_search", nested_predictions),):
        for target in TARGETS:
            repeats = [metric([r["observed_eV"] for r in rows if r["target"] == target and r["repeat"] == repeat],
                              [r["predicted_eV"] for r in rows if r["target"] == target and r["repeat"] == repeat]) for repeat in (1, 2, 3)]
            metrics.append(dict(target=target, method=method, **{f"CV_mean_{m}": float(np.mean([r[m] for r in repeats])) for m in repeats[0]},
                                CV_min_R2=min(r["R2"] for r in repeats)))
    for target in TARGETS:
        rows = [r for r in validation_predictions if r["target"] == target]
        metrics.append(dict(target=target, method="selected_shared_validation", **metric(
            [r["observed_eV"] for r in rows], [r["predicted_eV"] for r in rows])))
    candidate_metrics = [dict(descriptor_set=block, family=family, target=target, repeat=repeat,
                              descriptor_count=len(candidates[block]), **metric(y, p))
                         for (block, family, target, repeat), (y, p) in candidate_predictions.items()]
    for name, rows in (("model_metrics.csv", metrics), ("nested_cv_predictions.csv", nested_predictions),
                       ("validation_predictions.csv", validation_predictions),
                       ("nested_selections.csv", selection_rows), ("inner_search_scores.csv", inner_rows),
                       ("candidate_cv_metrics.csv", candidate_metrics), ("model_coefficients.csv", coefficients),
                       ("model_preprocessing.csv", prep), ("cohort_membership.csv", cohort),
                       ("selected_descriptors.csv", [dict(index=i + 1, **definitions[f]) for i, f in enumerate(features)])):
        write(name, rows)
    (OUT / "model_parameters.json").write_text(json.dumps(final_models, indent=2) + "\n", encoding="utf-8")
    paths = [Path(__file__), HERE / "descriptor_catalog.py", HERE / "build_shared_report.py",
             HERE / "build_current_report.py", HERE / "dipole_site_features.csv",
             HERE / "build_overpotential_report.py",
             HERE / "current_site_descriptors.py", HERE / "current_descriptor_selection.json",
             HERE / "try_two_descriptors.py",
             HERE / "select_representative_split.py", HERE / "representative_split/split_config.json",
             HERE / "run_config.json", HERE / "cv_predictions.csv", HERE / "cohort_membership.csv",
             HERE.parents[1] / "extracted" / "orr_analysis_energies.csv"]
    paths += [p for p in (HERE / "current_site_features.csv", HERE / "refine_shared_descriptors.py", HERE / "swap_validation_structures.py",
        HERE / "optimize_shared_descriptors.py",
        HERE / "apply_relative_distance_exclusions.py", HERE / "representative_split/relative_distance_exclusions.json",
        HERE / "representative_split/data_quality_exclusion_ledger.csv", HERE / "representative_split/selected_endpoint_geometry_checks.csv") if p.exists()]
    split = json.loads((HERE / "representative_split/split_config.json").read_text(encoding="utf-8"))
    config = dict(shared_descriptors=features, shared_model_family=selected["family"], descriptor_sets=sets,
        model_families=list(FAMILIES), ridge_alphas=ALPHAS,
        descriptor_set_count=len(candidates), outer_repeats=3, outer_folds=5, inner_folds=4,
        final_inner_repeats=3, final_joint_normalized_MSE=selected["cost"], selected_descriptor_set=selected["block"],
        objective=("common descriptor set and target-specific ridge strengths minimize grouped inner MSE"
                   if len(candidates) > 1 else f"fixed {len(features)} raw descriptors and linear ridge; target-specific alpha minimizes grouped OOF MSE"),
        descriptor_selection=("descriptor set and ridge strengths selected inside each outer training fold"
                              if len(candidates) > 1 else "current inputs fixed; exploratory selection record in current_descriptor_selection.json; CV conditional on chosen inputs"),
        descriptor_selection_in_outer_folds=len(candidates) > 1,
        selection_reference_set=selection_configuration.get("selection_reference_set"),
        selection_scores_are_conditional=True,
        required_descriptors=["metal_metal_distance_A"],
        target_specific_cohorts=False, additional_pruning=False, outer_folds_aligned=aligned,
        cohort_policy=split["policy"],
        split_configuration="representative_split/split_config.json",
        validation_used_for_selection=split["target_energies_used_for_split"], numpy_version=np.__version__,
        sha256={str(p.relative_to(HERE.parents[1])): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (OUT / "run_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    from build_shared_report import build_report
    build_report()
    for r in metrics:
        print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
