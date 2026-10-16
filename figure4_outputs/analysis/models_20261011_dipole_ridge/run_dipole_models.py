#!/usr/bin/env python3
"""Compare distance and local charge-moment descriptors on frozen v2 cohorts."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / "models_20261008_linear_ridge_v2"
ALPHAS = (0.001, 0.01, 0.1, 1.0, 10.0, 100.0)
EMPIRICAL_FEATURES = frozenset({
    "site_electronegativity_Pauling", "partner_electronegativity_Pauling",
})


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(name, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def key(row):
    return row["name"], row["ads_site"]


def dipole_descriptors(lm, desc):
    structures = {row["name"]: row for row in lm.read(lm.INPUT)}
    contributions = []
    for row in desc:
        source = structures[row["name"]]
        z = lm.arr(source["array.numbers"]).astype(int)
        xyz = lm.arr(source["array.positions"]).reshape((-1, 3))
        charge = lm.arr(source["data.bader_charges"])
        site = 0 if row["ads_site"] == "metal1" else 1
        shells = {}
        for prefix, center in (("site", site), ("partner", 1 - site)):
            ids = [i for i, number in enumerate(z)
                   if number in lm.HETEROATOM_Z and i not in (0, 1)
                   and np.linalg.norm(xyz[i] - xyz[center]) <= lm.CUTOFF]
            vectors = charge[ids, None] * (xyz[ids] - xyz[center])
            magnitudes = np.linalg.norm(vectors, axis=1)
            for statistic, operation in (("mean", np.mean), ("std", np.std),
                                         ("min", np.min), ("max", np.max)):
                row[f"{prefix}_heteroatom_dipole_contribution_{statistic}_eA"] = (
                    float(operation(magnitudes)) if ids else "")
            # Same metal-centered net moment as the existing v2 descriptor.
            row[f"{prefix}_heteroatom_charge_dipole_proxy_norm_eA"] = (
                float(np.linalg.norm(vectors.sum(axis=0))) if ids else "")
            shells[center] = set(ids)
            for i, magnitude, vector in zip(ids, magnitudes, vectors):
                contributions.append({"name": row["name"], "ads_site": row["ads_site"],
                    "environment": prefix, "atom_index_zero_based": i,
                    "element_audit_only": lm.ELEMENTS[int(z[i])],
                    "bader_charge_e": float(charge[i]),
                    "distance_A_audit_only": float(np.linalg.norm(xyz[i] - xyz[center])),
                    "dipole_contribution_magnitude_eA": float(magnitude),
                    **{f"dipole_contribution_{axis}_eA": float(value)
                       for axis, value in zip("xyz", vector)}})
        shared = shells[0] & shells[1]
        row["shared_bridge_dipole_contribution_asymmetry_mean_eA"] = (
            float(np.mean([abs(charge[i]) * abs(np.linalg.norm(xyz[i] - xyz[0])
                - np.linalg.norm(xyz[i] - xyz[1])) for i in shared])) if shared else "")
    return contributions


def replace_features(features):
    replacements = []
    mapping = []
    for feature in features:
        if "heteroatom_distance_" in feature:
            replacement = feature.replace("heteroatom_distance_", "heteroatom_dipole_contribution_")
            replacement = replacement.removesuffix("_A") + "_eA"
        elif feature == "shared_bridge_distance_asymmetry_mean_A":
            replacement = "shared_bridge_dipole_contribution_asymmetry_mean_eA"
        elif "charge_weighted_sum_e_per_A" in feature:
            mapping.append({"original_feature": feature, "dipole_feature": "",
                            "action": "removed inverse-distance charge descriptor"})
            continue
        else:
            replacement = feature
        duplicate = replacement in replacements
        if not duplicate:
            replacements.append(replacement)
        mapping.append({"original_feature": feature, "dipole_feature": replacement,
                        "action": "deduplicated" if duplicate else
                        ("retained" if feature == replacement else "replaced")})
    return replacements, mapping


def fit(lm, desc, train_keys, held_keys, features, labels, target, alpha):
    if EMPIRICAL_FEATURES.intersection(features):
        raise ValueError("empirical descriptors must not enter either model variant")
    ids = {key(row): i for i, row in enumerate(desc)}
    train, held = lm.encode(desc, [ids[k] for k in train_keys],
                           [ids[k] for k in held_keys], features)
    truth = np.asarray([float(labels[k][target]) for k in train_keys])
    penalty = np.diag([0.0] + [alpha] * (train.shape[1] - 1))
    coefficients = np.linalg.solve(train.T @ train + penalty, train.T @ truth)
    return held @ coefficients, coefficients


def select_alpha(lm, desc, train_keys, features, labels, target, seed):
    partitions = lm.folds([k[0] for k in train_keys], seed, 4)
    scores = []
    for alpha in ALPHAS:
        errors = []
        for held_names in partitions:
            train = [k for k in train_keys if k[0] not in held_names]
            held = [k for k in train_keys if k[0] in held_names]
            predictions, _ = fit(lm, desc, train, held, features, labels, target, alpha)
            errors.extend(predictions - np.asarray([float(labels[k][target]) for k in held]))
        scores.append((float(np.sqrt(np.mean(np.square(errors)))), alpha))
    return min(scores)


def metrics(rows):
    truth = np.asarray([r["observed_eV"] for r in rows])
    predictions = np.asarray([r["predicted_eV"] for r in rows])
    errors = predictions - truth
    return {"R2": float(1 - np.sum(errors ** 2) / np.sum((truth - truth.mean()) ** 2)),
            "RMSE_eV": float(np.sqrt(np.mean(errors ** 2))),
            "MAE_eV": float(np.mean(np.abs(errors))),
            "pearson_r": float(np.corrcoef(truth, predictions)[0, 1])}


def prediction_rows(target, variant, keys, labels, predictions, **extra):
    return [{"target": target, "variant": variant, "name": k[0], "ads_site": k[1],
             "observed_eV": float(labels[k][target]), "predicted_eV": float(p),
             "error_eV": float(p - float(labels[k][target])), **extra}
            for k, p in zip(keys, predictions)]


def preprocessing(desc, train_keys, features, target, variant):
    by_key = {key(row): row for row in desc}
    rows = []
    for index, feature in enumerate(features, 1):
        values = np.asarray([float(by_key[k].get(feature, "") or "nan") for k in train_keys])
        finite = np.isfinite(values)
        median = float(np.median(values[finite])) if finite.any() else 0.0
        values[~finite] = median
        sd = float(values.std())
        rows.append({"target": target, "variant": variant, "predictor_index": index,
                     "feature": feature, "training_median_for_imputation": median,
                     "training_mean_after_imputation": float(values.mean()),
                     "training_sd_after_imputation": sd if sd > 1e-12 else 1.0})
    return rows


def main():
    spec = importlib.util.spec_from_file_location("dipole_source", SOURCE / "run_models_linear.py")
    lm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lm)
    desc, _, _ = lm.descriptors()
    # The v2 reader supplies historical lookup columns; discard them before modelling.
    for row in desc:
        for feature in EMPIRICAL_FEATURES:
            row.pop(feature, None)
    labels = {key(row): row for row in lm.read(lm.LABELS)}
    contributions = dipole_descriptors(lm, desc)
    write("dipole_contributions_audit.csv", contributions)
    stats, cv_predictions, validation_predictions = [], [], []
    fold_selections, coefficients, prep, feature_mapping, membership = [], [], [], [], []
    feature_sets = {}
    for target in ("G_OH", "G_O", "G_OOH"):
        focused = target == "G_OOH"
        cv_source = SOURCE / ("selected_ooh_cv_predictions.csv" if focused else "selected_cv_predictions.csv")
        val_source = SOURCE / ("selected_ooh_validation_predictions.csv" if focused else "selected_validation_predictions.csv")
        saved_cv = [r for r in read(cv_source) if r["target"] == target]
        saved_val = [r for r in read(val_source) if r["target"] == target]
        train_keys = sorted({key(r) for r in saved_cv})
        validation_keys = sorted({key(r) for r in saved_val})
        expected = (70, 49) if focused else (81, 56)
        if (len(train_keys), len({k[0] for k in train_keys})) != expected:
            raise ValueError(f"unexpected frozen training cohort for {target}")
        if (len(validation_keys), len({k[0] for k in validation_keys})) != (23, 15):
            raise ValueError(f"unexpected frozen validation cohort for {target}")
        if {k[0] for k in train_keys} & {k[0] for k in validation_keys}:
            raise ValueError("structure overlap between training and validation")
        block = "geometry_plus_heteroatom_electronics" if focused else "geometry_angles_heteroatom_charge_spin"
        original = [feature for feature in lm.FEATURES[block] if feature not in EMPIRICAL_FEATURES]
        dipole, mapping = replace_features(original)
        feature_sets[target] = {"distance_baseline": original, "dipole": dipole}
        mapping.extend({"original_feature": feature, "dipole_feature": "",
                        "action": "removed empirical lookup descriptor from both variants"}
                       for feature in sorted(EMPIRICAL_FEATURES))
        feature_mapping.extend({"target": target, **row} for row in mapping)
        train_set, val_set = set(train_keys), set(validation_keys)
        membership.extend({"target": target, "name": row["name"], "ads_site": row["ads_site"],
                           "role": "training" if key(row) in train_set else
                           "validation" if key(row) in val_set else "excluded_in_source_cohort"}
                          for row in desc)
        for variant, features in feature_sets[target].items():
            current_cv, repeat_stats = [], []
            for repeat in (1, 2, 3):
                fold_by = {key(r): int(r["fold"]) for r in saved_cv if int(r["repeat"]) == repeat}
                if set(fold_by) != train_set:
                    raise ValueError("incomplete saved CV assignments")
                for name in {k[0] for k in train_keys}:
                    if len({fold_by[k] for k in train_keys if k[0] == name}) != 1:
                        raise ValueError("saved fold splits a structure")
                current_repeat = []
                for fold in range(1, 6):
                    train = [k for k in train_keys if fold_by[k] != fold]
                    held = [k for k in train_keys if fold_by[k] == fold]
                    seed = lm.SEED + repeat * 10007 + fold * 101
                    inner_rmse, alpha = select_alpha(lm, desc, train, features, labels, target, seed)
                    predictions, _ = fit(lm, desc, train, held, features, labels, target, alpha)
                    current_repeat.extend(prediction_rows(target, variant, held, labels, predictions,
                                                          repeat=repeat, fold=fold))
                    fold_selections.append({"target": target, "variant": variant, "repeat": repeat,
                        "fold": fold, "ridge_alpha": alpha, "inner_grouped_rmse_eV": inner_rmse})
                repeat_stats.append(metrics(current_repeat))
                current_cv.extend(current_repeat)
            cv_predictions.extend(current_cv)
            inner_rmse, alpha = select_alpha(lm, desc, train_keys, features, labels, target, lm.SEED + 811)
            predictions, coef = fit(lm, desc, train_keys, validation_keys, features, labels, target, alpha)
            current_val = prediction_rows(target, variant, validation_keys, labels, predictions)
            validation_predictions.extend(current_val)
            vm = metrics(current_val)
            stats.append({"target": target, "variant": variant, "predictor_entries": len(features),
                "training_structures": expected[1], "training_site_rows": expected[0],
                "validation_structures": 15, "validation_site_rows": 23,
                "ridge_alpha": alpha, "inner_grouped_rmse_eV": inner_rmse,
                **{f"cv_mean_{metric}": float(np.mean([r[metric] for r in repeat_stats])) for metric in vm},
                **{f"cv_min_{metric}": float(min(r[metric] for r in repeat_stats)) for metric in vm},
                **{f"validation_{metric}": value for metric, value in vm.items()}})
            coefficients.extend({"target": target, "variant": variant, "predictor_index": i,
                "term": term, "standardized_coefficient": float(value), "ridge_alpha": alpha}
                for i, (term, value) in enumerate(zip(["intercept"] + features, coef)))
            prep.extend(preprocessing(desc, train_keys, features, target, variant))
            print(f"{target} {variant}: {len(features)} predictors; CV R2 "
                  f"{stats[-1]['cv_mean_R2']:.3f}; validation R2 {vm['R2']:.3f}", flush=True)
    for filename, rows in (("model_metrics.csv", stats), ("cv_predictions.csv", cv_predictions),
                           ("validation_predictions.csv", validation_predictions),
                           ("cv_selections.csv", fold_selections), ("model_coefficients.csv", coefficients),
                           ("model_preprocessing.csv", prep), ("descriptor_replacements.csv", feature_mapping),
                           ("cohort_membership.csv", membership)):
        write(filename, rows)
    dipole_features = list(dict.fromkeys(f for variants in feature_sets.values() for f in variants["dipole"]))
    write("dipole_site_features.csv", [{"name": row["name"], "ads_site": row["ads_site"],
          **{feature: row[feature] for feature in dipole_features}} for row in desc])
    inputs = [lm.INPUT, lm.LABELS, SOURCE / "run_models_linear.py", Path(__file__), OUT / "descriptor_formulas.md",
              OUT / "dipole_with_empirical_model_metrics.csv",
              *[SOURCE / name for name in ("selected_cv_predictions.csv", "selected_validation_predictions.csv",
                                          "selected_ooh_cv_predictions.csv", "selected_ooh_validation_predictions.csv")]]
    config = {"run_date": "2026-10-11", "feature_sets": feature_sets,
              "excluded_empirical_descriptors": sorted(EMPIRICAL_FEATURES),
              "descriptor_policy": "calculated clean-structure charges, magnetic moments and geometry; no empirical element-property lookup predictors",
              "ridge_alphas": ALPHAS, "outer_repeats": 3, "outer_folds": 5, "inner_folds": 4,
              "neighbor_rule": "combined N/O/S within 2.30 Angstrom of each metal; Cartesian",
              "dipole_contribution": "p_i = |q_i| * norm(r_i - r_metal), e Angstrom",
              "net_dipole_proxy": "norm(sum_i q_i * (r_i-r_metal)), e Angstrom; metal origin",
              "bridge_asymmetry": "mean_i |q_i| * |d_i_metal1 - d_i_metal2| over shared neighbors",
              "retained_distance_predictor": "metal_metal_distance_A",
              "cohort_policy": "exact saved selected-model site cohorts and outer fold assignments; no new pruning",
              "selection_policy": "feature sets fixed; ridge alpha selected in training-only grouped folds",
              "baseline_policy": "paired refit of original final feature set with both Pauling columns removed, retaining duplicate columns; ridge alpha retuned",
              "preprocessing": "training-only median imputation and population-SD standardization in every fold",
              "numpy_version": np.__version__,
              "sha256": {str(path.relative_to(OUT.parent.parent.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in inputs}}
    (OUT / "run_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    report = ["# Local dipole descriptors: selected-cohort ridge comparison", "",
        "Both fitted variants exclude all empirical element-property lookup descriptors. "
        "`site_electronegativity_Pauling` and `partner_electronegativity_Pauling` are removed from "
        "the model inputs, preprocessing and coefficients. The dipole models use 39 predictors "
        "for G_OH/G_O and 23 for G_OOH, derived from calculated clean-structure charges, "
        "magnetic moments and atomic coordinates. Element atomic numbers select N/O/S neighbors "
        "and identify the two metals; they are not predictor columns.", "",
        "This experiment replaces pooled metal-heteroatom distance mean, population standard deviation, minimum "
        "and maximum with the same summaries of local Bader point-charge contribution magnitudes. "
        "The two inverse-distance charge sums are removed. Bridge distance asymmetry is replaced with "
        "charge-moment contribution asymmetry. Metal-metal distance remains a predictor. "
        "Repeated descriptor names are deduplicated in the dipole model.", "",
        "For each N/O/S neighbor within 2.30 Angstrom, define `mu_i = q_i * (r_i-r_metal)` "
        "and `p_i = norm(mu_i) = abs(q_i) * d_i`. Compute mean/std/min/max over `p_i`. "
        "The existing net local dipole `norm(sum_i mu_i)` remains included. Units are e Angstrom. "
        "The mean of contribution magnitudes differs from the magnitude of their vector sum: "
        "the latter includes cancellation between directions.", "",
        "These are point-charge dipole proxies with the metal as the specified origin. They are "
        "translation and rotation invariant under rigid motion of the structure, but remain sensitive "
        "to charge partitioning, the local origin and neighbor selection. They are not atom-resolved "
        "DFT dipoles or the total molecular dipole. Charge-only representations omit local atomic "
        "polarization; see [Veit et al., J. Chem. Phys. 153, 024113 (2020)](https://arxiv.org/abs/2003.12437). "
        "There is no assumption that multiplying charge by distance removes all N/O/S differences. "
        "The original 2.30 Angstrom shell cutoff remains species sensitive.", "",
        "## Paired model results", "",
        "Both variants use the same saved selected-model training sites, fixed validation sites and "
        "three repeated five-fold structure-grouped outer partitions. Ridge alpha is selected by "
        "four-fold grouped CV within each training partition. Feature sets are fixed to the original "
        "final block and its dipole replacement after removing empirical lookup columns from both. "
        "The distance baseline is a fresh paired refit, "
        "not the historical nested search across descriptor blocks and OLS/ridge families. "
        "No additional structures are removed and validation is not used to choose alpha.", "",
        "| Target | Variant | Predictors | Training structures/sites | Alpha | Mean CV R2 | Validation R2 | CV RMSE (eV) | Validation RMSE (eV) |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|"]
    for r in stats:
        report.append(f"| {r['target']} | {r['variant']} | {r['predictor_entries']} | "
                      f"{r['training_structures']}/{r['training_site_rows']} | {r['ridge_alpha']:g} | "
                      f"{r['cv_mean_R2']:.3f} | {r['validation_R2']:.3f} | "
                      f"{r['cv_mean_RMSE_eV']:.3f} | {r['validation_RMSE_eV']:.3f} |")
    report += ["", "### Effect of the dipole replacement without empirical descriptors", ""]
    for target in ("G_OH", "G_O", "G_OOH"):
        baseline = next(r for r in stats if r["target"] == target and r["variant"] == "distance_baseline")
        dipole = next(r for r in stats if r["target"] == target and r["variant"] == "dipole")
        report.append(f"- {target}: mean CV R2 changes from {baseline['cv_mean_R2']:.3f} to "
                      f"{dipole['cv_mean_R2']:.3f}; validation R2 changes from "
                      f"{baseline['validation_R2']:.3f} to {dipole['validation_R2']:.3f}.")
    empirical_reference = {r["target"]: r for r in read(OUT / "dipole_with_empirical_model_metrics.csv")
                           if r["variant"] == "dipole"}
    report += ["", "### Effect of removing empirical descriptors from the dipole models", "",
               "The prior dipole fits included both Pauling lookup descriptors. The table compares "
               "their saved metrics with the current fits using the same cohorts, outer folds and "
               "ridge-alpha selection procedure. Ridge alpha is retuned after removing the two columns. "
               "The prior metrics are retained as a historical comparison; current fitted variants "
               "both exclude empirical descriptors.", "",
               "| Target | Prior predictors | Current predictors | Prior CV R2 | Current CV R2 | Prior validation R2 | Current validation R2 |",
               "|---|---:|---:|---:|---:|---:|---:|"]
    for current in stats:
        if current["variant"] != "dipole":
            continue
        prior = empirical_reference[current["target"]]
        report.append(f"| {current['target']} | {prior['predictor_entries']} | {current['predictor_entries']} | "
                      f"{float(prior['cv_mean_R2']):.3f} | {current['cv_mean_R2']:.3f} | "
                      f"{float(prior['validation_R2']):.3f} | {current['validation_R2']:.3f} |")
    report += ["", "The distance-versus-dipole comparison includes the dipole replacements, removal of inverse-distance "
               "charge sums, deduplication and retuning of ridge alpha. They do not isolate the "
               "contribution of any single descriptor. This comparison measures prediction "
               "within the inherited cohorts; it does not establish transferability across N/O/S environments.",
               "", "All three targets use 15 validation structures / 23 validation sites. "
               "The inherited cohorts were selected using historical model residuals, and OOH cohort "
               "selection inspected this validation set. These results remain exploratory; the CV scores "
               "are conditional on the previously selected population.", ""]
    report.extend((OUT / "descriptor_formulas.md").read_text(encoding="utf-8").splitlines())
    report += ["", "## Prediction formulas", "",
               "`G_hat = intercept + sum_j coefficient_j * ((x_j_imputed-training_mean_j)/training_sd_j)`. "
               "Missing values use the training median. Empty neighbor environments have missing "
               "summaries rather than zero dipole contributions.", ""]
    for target in ("G_OH", "G_O", "G_OOH"):
        report += [f"### {target}: dipole model", "", "| Term | Standardized coefficient |", "|---|---:|"]
        report += [f"| `{r['term']}` | {r['standardized_coefficient']:+.8f} |"
                   for r in coefficients if r["target"] == target and r["variant"] == "dipole"]
        report.append("")
    report += ["## Reproduction and files", "",
        "Run `python article/KongiCats/calculations/models_20261011_dipole_ridge/run_dipole_models.py` "
        "from the repository root; NumPy is required. The original v2 source files and saved fold "
        "assignments are required. `descriptor_formulas.md` supplies the descriptor definitions embedded "
        "in this report. Input hashes and definitions are recorded in `run_config.json`.", "",
        "`model_metrics.csv`, `cv_predictions.csv`, `validation_predictions.csv` and `cv_selections.csv` "
        "contain paired results. `model_coefficients.csv` and `model_preprocessing.csv` define both "
        "fits. `descriptor_replacements.csv` records every replacement and removed duplicate. "
        "`dipole_site_features.csv` contains dipole model inputs; `dipole_contributions_audit.csv` "
        "records individual atomic contributions and diagnostic element identities/distances. "
        "`cohort_membership.csv` records the role of every source site for every target. "
        "`dipole_with_empirical_model_metrics.csv` preserves the prior fit metrics for the empirical-descriptor removal comparison.", ""]
    (OUT / "target_specific_models_summary.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
