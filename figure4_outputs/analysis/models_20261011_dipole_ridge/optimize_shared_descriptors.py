#!/usr/bin/env python3
"""Evaluate replacements and exhaustive common subsets with grouped nested CV."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

import run_shared_descriptor_search as model

HERE = Path(__file__).resolve().parent
OUT = HERE / "shared_descriptor_optimization"
GEOMETRY = "metal_metal_distance_A"
CHARGE = ("site_terminal_ligand_charge_mean_e", "site_heteroatom_charge_min_e")
DIPOLE = ("site_heteroatom_charge_dipole_proxy_norm_eA", "site_heteroatom_dipole_contribution_max_eA")
SPIN = "spin_product_muB2"


def write(name, rows):
    previous = model.OUT
    try:
        model.OUT = OUT
        model.write(name, rows)
    finally:
        model.OUT = previous


def no_regression_choices(choices, reference):
    baseline = next(c for c in choices if c["block"] == reference)
    return [c for c in choices if all(c["selected"][t]["mse"] <= baseline["selected"][t]["mse"] + 1e-12
                                    for t in model.TARGETS)]


def summarize(rows):
    scores = {}
    for t in model.TARGETS:
        repeats = []
        for repeat in (1, 2, 3):
            rs = [r for r in rows if r["target"] == t and r["repeat"] == repeat]
            repeats.append(model.metric([r["observed_eV"] for r in rs], [r["predicted_eV"] for r in rs]))
        scores[t] = {k: float(np.mean([r[k] for r in repeats])) for k in repeats[0]}
        scores[t]["repeat_R2"] = [r["R2"] for r in repeats]
    return scores


def make_candidates(starting, pool, data):
    if not {GEOMETRY, CHARGE[0], DIPOLE[0]} <= set(starting):
        raise ValueError("saved starting descriptors do not contain the expected replacement inputs")
    other = [f for f in starting if f not in (GEOMETRY, CHARGE[0], DIPOLE[0])]
    order = list(starting) + [CHARGE[1], DIPOLE[1], SPIN]
    candidates, replacements = {}, set()
    baseline = "reference_8_inputs"
    candidates[baseline] = starting
    identity = {tuple(starting): baseline}
    matrix = data["G_OH"]["x"]
    held_matrix = data["G_OH"]["validation_x"]

    def add(features, replacement=False):
        wanted = set(features)
        features = [f for f in order if f in wanted]
        for f in features:
            j = pool.index(f)
            a, b = matrix[:, j], held_matrix[:, j]
            a, b = a[np.isfinite(a)], b[np.isfinite(b)]
            if not len(a) or len(b) and (b.min() < a.min() - 1e-10 or b.max() > a.max() + 1e-10):
                return
        for a, b in itertools.combinations(features, 2):
            x, y = matrix[:, pool.index(a)], matrix[:, pool.index(b)]
            good = np.isfinite(x) & np.isfinite(y)
            if good.sum() > 2 and np.std(x[good]) > 1e-12 and np.std(y[good]) > 1e-12:
                if abs(np.corrcoef(x[good], y[good])[0, 1]) >= .95:
                    return
        signature = tuple(features)
        name = identity.get(signature)
        if name is None:
            name = f"shared_set_{len(candidates):03d}"
            identity[signature] = name
            candidates[name] = features
        if replacement:
            replacements.add(name)

    for charge, dipole, spin in itertools.product(CHARGE, DIPOLE, (False, True)):
        add([*other, GEOMETRY, charge, dipole, *([SPIN] if spin else [])], replacement=True)
    for mask, charge, dipole, spin in itertools.product(range(2 ** len(other)), (None, *CHARGE), (None, *DIPOLE), (False, True)):
        features = [f for i, f in enumerate(other) if mask & (1 << i)] + [GEOMETRY]
        features += [f for f in (charge, dipole, SPIN if spin else None) if f]
        add(features)
    return candidates, replacements, baseline


def export_selected_candidate(data, definitions, features, choice, cv_rows, result):
    from build_shared_report import equation, plain_equation, scatter_svg
    from descriptor_catalog import definitions_for
    models, validation_rows, coefficients, preprocessing = {}, [], [], []
    for target, d in data.items():
        setting = choice["selected"][target]["setting"]
        pp, state = model.fit_batch(d["x"][:, choice["columns"]], d["validation_x"][:, choice["columns"]], d["y"])
        beta = state["coefficients"][setting]
        linear = beta / state["scale"]
        intercept = state["intercept"] - float(np.sum(beta * state["mean"] / state["scale"]))
        models[target] = dict(family="ridge", parameter=setting[1], descriptor_keys=features,
            descriptor_names=[definitions[f]["name"] for f in features], raw_intercept=intercept,
            raw_linear_coefficients=linear.tolist(), imputation_medians=state["median"].tolist(),
            standardized_intercept=state["intercept"], standardized_coefficients=beta.tolist(),
            training_structures=len(set(d["names"])), training_site_rows=len(d["keys"]))
        validation_rows.extend(model.prediction_rows(target, "selected_candidate_validation", d["validation_keys"],
            d["validation_y"], pp[setting]))
        coefficients.append(dict(target=target, index=0, name="Intercept", coefficient=intercept))
        for i, f in enumerate(features):
            coefficients.append(dict(target=target, index=i + 1, name=definitions[f]["name"], descriptor_key=f,
                coefficient=float(linear[i])))
            preprocessing.append(dict(target=target, index=i + 1, descriptor_key=f,
                median=float(state["median"][i]), mean=float(state["mean"][i]), scale=float(state["scale"][i])))
    candidate_validation = {t: model.metric([r["observed_eV"] for r in validation_rows if r["target"] == t],
        [r["predicted_eV"] for r in validation_rows if r["target"] == t]) for t in model.TARGETS}
    reference_validation = {r["target"]: {k: float(r[k]) for k in ("R2", "RMSE_eV", "MAE_eV", "pearson_r")}
        for r in model.read(model.OUT / "model_metrics.csv") if r["method"] == "selected_shared_validation"}
    result["selected_candidate_validation"] = candidate_validation
    result["reference_validation"] = reference_validation
    result["validation_evaluation"] = "one frozen-set evaluation after training-only final descriptor selection; not used to choose the candidate"
    write("selected_candidate_cv_predictions.csv", cv_rows)
    write("selected_candidate_validation_predictions.csv", validation_rows)
    write("selected_candidate_coefficients.csv", coefficients)
    write("selected_candidate_preprocessing.csv", preprocessing)
    write("selected_candidate_descriptors.csv", [dict(index=i + 1, **definitions[f]) for i, f in enumerate(features)])
    write("validation_comparison.csv", [dict(target=t, candidate=label, **scores[t])
        for label, scores in (("reference", reference_validation), ("selected_compact_candidate", candidate_validation))
        for t in model.TARGETS])
    (OUT / "selected_candidate_model_parameters.json").write_text(json.dumps(models, indent=2) + "\n", encoding="utf-8")
    lines = ["# Selected experimental adsorption-energy candidate", "",
        f"All three targets share {len(features)} descriptors and use linear ridge. The fixed cohort contains "
        f"{len(set(data['G_OH']['names']))} training structures / {len(data['G_OH']['keys'])} sites and "
        f"{len({k[0] for k in data['G_OH']['validation_keys']})} validation structures / {len(data['G_OH']['validation_keys'])} sites. "
        "The descriptors are selected using training data; validation is evaluated after the choice.", "",
        "## Descriptor definitions", "", definitions_for(features), "",
        "| Symbol | Name | Description | Formula | Units |", "|---|---|---|---|---|"]
    for i, f in enumerate(features, 1):
        d = definitions[f]
        lines.append(f"| $x_{{{i}}}$ | {d['name']} | {d['description']} | ${d['formula']}$ | {d['units']} |")
    lines += ["", "## Prediction equations", "",
        "Use the raw descriptor units. Missing values use the training medians in the preprocessing CSV. "
        "Scaling is already incorporated in these coefficients; energies are in eV.", ""]
    for t in model.TARGETS:
        lines += [f"### {t}", "", f"Ridge strength: {models[t]['parameter']:g}.", "", equation(t, models[t]), "", plain_equation(t, models[t]), ""]
    lines += ["## Performance", "", "| Target | Fixed-input CV R² | Fixed-input CV RMSE (eV) | Validation R² | Validation RMSE (eV) |",
        "|---|---:|---:|---:|---:|"]
    for t in model.TARGETS:
        c, v = result["selected_fixed_input_CV"][t], candidate_validation[t]
        lines.append(f"| {t} | {c['R2']:.4f} | {c['RMSE_eV']:.4f} | {v['R2']:.4f} | {v['RMSE_eV']:.4f} |")
    lines += ["", "The fixed-input CV scores hold the final selected descriptors constant and tune ridge strength within each "
        "outer training fold. Table scores average three repeat R² values; CV graphs pool their predictions. "
        "These fixed-input scores do not include the error of selecting descriptors. "
        "[The complete search report](report.md) gives the CV scores with descriptor selection inside the outer folds.", ""]
    graphs = OUT / "graphs"
    graphs.mkdir(exist_ok=True)
    for t in model.TARGETS:
        for kind, rows in (("cv", cv_rows), ("validation", validation_rows)):
            (graphs / f"{t}_{kind}.svg").write_text(scatter_svg([r for r in rows if r["target"] == t], t, kind), encoding="utf-8")
    lines += ["## Graphs", "", "| Target | Fixed-input CV | Validation |", "|---|---|---|"]
    for t in model.TARGETS:
        lines.append(f"| {t} | ![{t} CV](graphs/{t}_cv.svg) | ![{t} validation](graphs/{t}_validation.svg) |")
    lines += ["", "[Full-precision equations](selected_candidate_model_parameters.json); "
        "[preprocessing values](selected_candidate_preprocessing.csv); "
        "[validation predictions](selected_candidate_validation_predictions.csv).", ""]
    (OUT / "selected_candidate_model_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    input_path = OUT / "search_inputs.json"
    pool, definitions, data, partitions, _, cohort = model.load_data()
    if not input_path.exists():
        current = json.loads((HERE / "current_descriptor_selection.json").read_text(encoding="utf-8"))
        input_path.write_text(json.dumps(dict(starting_descriptors=current["shared_descriptors"],
            cohort=cohort, baseline_metrics=model.read(model.OUT / "model_metrics.csv"),
            sha256={str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
                HERE / "cohort_membership.csv", HERE / "current_site_features.csv",
                HERE / "representative_split/relative_distance_exclusions.json")}), indent=2) + "\n", encoding="utf-8")
    inputs = json.loads(input_path.read_text(encoding="utf-8"))
    if inputs["cohort"] != cohort:
        raise ValueError("the fixed cohort differs from the saved descriptor-search inputs")
    for name, digest in inputs["sha256"].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"fixed descriptor-search source changed: {name}")
    candidates, replacement_names, reference = make_candidates(inputs["starting_descriptors"], pool, data)
    columns = {name: [pool.index(f) for f in fs] for name, fs in candidates.items()}
    write("candidate_descriptors.csv", [dict(candidate=name, descriptor_count=len(fs),
        descriptors=";".join(fs), descriptor_names=";".join(definitions[f]["name"] for f in fs),
        full_replacement_trial=name in replacement_names) for name, fs in candidates.items()])
    (OUT / "candidate_descriptor_sets.json").write_text(json.dumps(candidates, indent=2) + "\n", encoding="utf-8")
    print(f"Evaluating {len(candidates)} shared sets, including {len(replacement_names)} full replacement/spin trials", flush=True)
    candidate_predictions = {name: [] for name in candidates}
    nested_rows, replacement_rows, selections = [], [], []
    for repeat in (1, 2, 3):
        for fold in range(1, 6):
            masks = {t: np.asarray([partitions[repeat, n] == fold for n in d["names"]]) for t, d in data.items()}
            training = {t: dict(x=d["x"][~masks[t]], y=d["y"][~masks[t]],
                names=[n for n, flag in zip(d["names"], masks[t]) if not flag]) for t, d in data.items()}
            choices = model.choose_targets(training, columns, [model.SEED + repeat * 10007 + fold * 101])
            allowed = no_regression_choices(choices, reference)
            best = allowed[0]
            replacement_best = next(c for c in allowed if c["block"] in replacement_names)
            for choice in choices:
                for t, d in data.items():
                    held = masks[t]
                    pp, _ = model.fit_batch(d["x"][~held][:, choice["columns"]],
                        d["x"][held][:, choice["columns"]], d["y"][~held])
                    rs = model.prediction_rows(t, "fixed_candidate_cv", [k for k, flag in zip(d["keys"], held) if flag],
                        d["y"][held], pp[choice["selected"][t]["setting"]], repeat=repeat, fold=fold)
                    candidate_predictions[choice["block"]].extend(rs)
                    if choice is best:
                        nested_rows.extend([dict(r, method="nested_descriptor_search") for r in rs])
                        selections.append(dict(repeat=repeat, fold=fold, target=t, candidate=choice["block"],
                            descriptor_count=len(choice["columns"]), alpha=choice["selected"][t]["setting"][1],
                            descriptors=";".join(candidates[choice["block"]]), joint_inner_normalized_MSE=choice["cost"]))
                    if choice is replacement_best:
                        replacement_rows.extend([dict(r, method="nested_replacement_search") for r in rs])
            print(f"Repeat {repeat}/3 fold {fold}/5: {best['block']}, {len(best['columns'])} descriptors", flush=True)
    fixed_scores = {name: summarize(rows) for name, rows in candidate_predictions.items()}
    baseline, nested, replacement_nested = fixed_scores[reference], summarize(nested_rows), summarize(replacement_rows)
    trial_rows = [dict(candidate=name, descriptor_count=len(candidates[name]), full_replacement_trial=name in replacement_names,
        **{t + "_CV_R2": score[t]["R2"] for t in model.TARGETS},
        **{t + "_CV_RMSE_eV": score[t]["RMSE_eV"] for t in model.TARGETS},
        all_targets_improve=all(score[t]["R2"] > baseline[t]["R2"] + 1e-6 for t in model.TARGETS))
        for name, score in fixed_scores.items()]
    trial_rows.sort(key=lambda r: (-sum(r[t + "_CV_R2"] for t in model.TARGETS), r["descriptor_count"], r["candidate"]))
    write("candidate_cv_metrics.csv", trial_rows)
    write("nested_cv_predictions.csv", nested_rows)
    write("nested_replacement_cv_predictions.csv", replacement_rows)
    write("nested_selections.csv", selections)
    print("Selecting the final descriptor set using training-only repeated grouped CV", flush=True)
    final_choices = model.choose_targets(data, columns, [model.SEED + 811 + i * 10007 for i in range(3)])
    best = no_regression_choices(final_choices, reference)[0]
    selected_features = candidates[best["block"]]
    accepted = all(nested[t]["R2"] > baseline[t]["R2"] + 1e-6 for t in model.TARGETS)
    result = dict(candidate_count=len(candidates), reference_candidate=reference, final_candidate=best["block"],
        selected_descriptors=selected_features, baseline_fixed_input_CV=baseline,
        nested_replacement_search_CV=replacement_nested, nested_full_search_CV=nested,
        selected_fixed_input_CV=fixed_scores[best["block"]], accepted=accepted,
        acceptance="descriptor-search nested CV R2 improves for every target versus the fixed starting inputs",
        validation_labels_used_for_selection=False, reference_constraint="no target inner MSE exceeds reference MSE",
        current_cohort={t: dict(structures=len(set(d["names"])), sites=len(d["keys"])) for t, d in data.items()})
    export_selected_candidate(data, definitions, selected_features, best, candidate_predictions[best["block"]], result)
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Shared descriptor replacement and subset search", "",
        f"The fixed cohort contains {len(set(data['G_OH']['names']))} training structures / {len(data['G_OH']['keys'])} sites. "
        "The validation membership and geometry exclusions remain fixed. Validation energies are excluded from selection.", "",
        f"The search evaluates {len(candidates)} common descriptor sets. Metal separation is mandatory. "
        "Ligand-charge choices are terminal mean, minimum, or absent; ligand-dipole choices are net magnitude, maximum "
        "individual magnitude, or absent. The signed metal spin product is optional. Every combination of the remaining "
        "inputs is considered. A pair with absolute training Pearson correlation at least 0.95 is disallowed. "
        "Every retained validation input remains within its training range.", "",
        "In each of three repeats of five outer structure-grouped folds, four inner grouped folds choose the common "
        "descriptor set and each target's ridge strength. Candidates must have no higher inner MSE than the reference "
        "set for any target; eligible candidates minimize mean target-variance-normalized inner MSE. "
        "The final set uses three repeats of four grouped folds on the full training cohort.", "",
        "## Descriptor-selection procedure scores", "",
        "| Procedure | OH CV R² | O CV R² | OOH CV R² |", "|---|---:|---:|---:|"]
    for label, scores in (("Reference fixed inputs", baseline), ("Full replacements and optional spin: nested selection", replacement_nested),
                          ("Replacements and exhaustive subsets: nested selection", nested)):
        lines.append(f"| {label} | " + " | ".join(f"{scores[t]['R2']:.4f}" for t in model.TARGETS) + " |")
    lines += ["", "## Full replacement trials", "",
        "These scores hold candidate inputs fixed; ridge strengths are selected inside each outer training fold.", "",
        "| Ligand charge summary | Ligand dipole summary | Signed metal spin product | OH CV R² | O CV R² | OOH CV R² |",
        "|---|---|---|---:|---:|---:|"]
    for name in sorted(replacement_names):
        fs, scores = candidates[name], fixed_scores[name]
        lines.append("| " + ("Minimum" if CHARGE[1] in fs else "Terminal mean") + " | "
            + ("Maximum individual magnitude" if DIPOLE[1] in fs else "Net magnitude") + " | "
            + ("Yes" if SPIN in fs else "No") + " | "
            + " | ".join(f"{scores[t]['R2']:.4f}" for t in model.TARGETS) + " |")
    lines += ["", "Individual candidate CV scores tune ridge strengths inside folds but hold candidate descriptors fixed. "
        "They are exploratory comparisons and do not include descriptor-selection error. The nested search scores "
        "above include choosing descriptors within each outer fold.", "",
        "## Final training-selected descriptors", ""]
    lines += [f"- {definitions[f]['name']} (`{f}`)" for f in selected_features]
    lines += ["", f"Apply to current models: **{'yes' if accepted else 'no'}**. " + result["acceptance"] + ".", "",
        "## Frozen validation evaluation", "",
        "The final candidate is chosen before evaluating validation. Validation results do not choose the descriptor set.", "",
        "| Target | Reference validation R² | Selected candidate validation R² |",
        "|---|---:|---:|"]
    for t in model.TARGETS:
        lines.append(f"| {t} | {result['reference_validation'][t]['R2']:.4f} | {result['selected_candidate_validation'][t]['R2']:.4f} |")
    lines += ["", "- [Candidate equations, exact descriptor definitions and graphs](selected_candidate_model_summary.md)",
        "- [All candidate CV metrics](candidate_cv_metrics.csv)", "- [Candidate descriptor definitions](candidate_descriptors.csv)",
        "- [Nested fold selections](nested_selections.csv)", "- [Nested predictions](nested_cv_predictions.csv)", "",
        "Reproduce the search from the repository root:", "", "```powershell",
        "python article/KongiCats/calculations/models_20261011_dipole_ridge/optimize_shared_descriptors.py", "```", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    if accepted:
        selection = dict(shared_descriptors=selected_features, model_family="ridge",
            candidate_descriptor_sets=candidates, selection_reference_set=reference,
            acceptance=result["acceptance"], descriptor_selection="nested_shared_subset_search",
            descriptor_selection_cohort=result["current_cohort"], validation_used_for_selection=False,
            selected_input_definitions=[definitions[f] for f in selected_features], similarity_threshold=.95,
            selection_scores_are_conditional=True, experiment_results="shared_descriptor_optimization/results.json")
        (HERE / "current_descriptor_selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
