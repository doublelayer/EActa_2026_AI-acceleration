#!/usr/bin/env python3
"""Publish the fitted models, their inputs and their prediction equations."""
import csv
import json
from pathlib import Path

import numpy as np

from build_shared_report import equation, plain_equation, scatter_svg
from descriptor_catalog import definitions_for

HERE = Path(__file__).resolve().parent
OUT = HERE / "shared_descriptor_search"
TARGETS = ("G_OH", "G_O", "G_OOH")


def read(name):
    with (OUT / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def build_report():
    current_manifest = HERE / "current_model_selection.json"
    if current_manifest.exists():
        manifest = json.loads(current_manifest.read_text(encoding="utf-8"))
        if manifest.get("status") == "current" and manifest.get("model_directory") == "target_specific_best_models":
            from publish_target_specific_models import publish
            publish(manifest["search_directory"])
            return
    config = json.loads((OUT / "run_config.json").read_text(encoding="utf-8"))
    models = json.loads((OUT / "model_parameters.json").read_text(encoding="utf-8"))
    descriptors = read("selected_descriptors.csv")
    metrics = read("model_metrics.csv")
    cv = {r["target"]: r for r in metrics if r["method"] == "nested_shared_search"}
    validation = {r["target"]: r for r in metrics if r["method"] == "selected_shared_validation"}
    features = config["shared_descriptors"]
    split = json.loads((HERE / "representative_split/split_config.json").read_text(encoding="utf-8"))
    with (HERE / "representative_split/chemistry_coverage.csv").open(encoding="utf-8-sig", newline="") as stream:
        coverage = list(csv.DictReader(stream))
    pair_count = sum(r["category"] == "metal_pair" for r in coverage)
    count = len(features)
    if any(models[t]["descriptor_keys"] != features for t in TARGETS):
        raise ValueError("all targets must have identical descriptor order")
    if any(models[t]["family"] != "ridge" or len(models[t]["raw_linear_coefficients"]) != count for t in TARGETS):
        raise ValueError("current models must be linear ridge with one coefficient per descriptor")
    if "metal_metal_distance_A" not in features:
        raise ValueError("metal separation must be included")
    feature_file = HERE / ("current_site_features.csv" if (HERE / "current_site_features.csv").exists() else "dipole_site_features.csv")
    with feature_file.open(encoding="utf-8-sig", newline="") as stream:
        source_features = {(r["name"], r["ads_site"]): r for r in csv.DictReader(stream)}
    validation_rows = read("validation_predictions.csv")
    errors = {}
    for target, model in models.items():
        full_errors, rounded_errors = [], []
        for row in validation_rows:
            if row["target"] != target:
                continue
            source = source_features[row["name"], row["ads_site"]]
            raw = np.asarray([float(source.get(f) or "nan") for f in features])
            raw = np.where(np.isfinite(raw), raw, model["imputation_medians"])
            linear = np.asarray(model["raw_linear_coefficients"])
            prediction = model["raw_intercept"] + raw @ linear
            rounded = float(f"{model['raw_intercept']:.10g}")
            rounded += raw @ np.asarray([float(f"{v:.10g}") for v in linear])
            full_errors.append(abs(prediction - float(row["predicted_eV"])))
            rounded_errors.append(abs(rounded - float(row["predicted_eV"])))
        if max(full_errors) > 1e-8 or max(rounded_errors) > 1e-6:
            raise ValueError(f"equation precision exceeds tolerance for {target}")
        errors[target] = dict(full_precision_max_error_eV=max(full_errors),
                              displayed_max_error_eV=max(rounded_errors))
    (OUT / "equation_consistency.json").write_text(json.dumps(errors, indent=2) + "\n", encoding="utf-8")

    descriptor_lines = ["## Descriptors used by all three models", "", definitions_for(features), "",
        "Each row is one input to every model, in the equation order shown.", "",
        "| Symbol | Descriptor name | Description | Formula | Units | Data column |",
        "|---|---|---|---|---|---|"]
    for r in descriptors:
        descriptor_lines.append(f"| $x_{{{r['index']}}}$ | {r['name']} | {r['description']} | "
                                f"${r['formula']}$ | {r['units']} | `{r['key']}` |")
    (HERE / "descriptor_formulas.md").write_text(
        "# Current model descriptor formulas\n\n" + "\n".join(descriptor_lines) + "\n", encoding="utf-8")

    lines = ["# Current adsorption-energy models", "",
        f"OH, O and OOH use the same **{count} descriptors** and **linear ridge regression**. "
        "Inputs are calculated from optimized clean structures. Coefficients and ridge strengths are fitted separately for each target.", "",
        "**Inputs:** " + "; ".join(r["name"] for r in descriptors) + ".", "",
        f"Each equation contains {count} linear terms and an intercept.", "", *descriptor_lines, "",
        "## Prediction equations", "",
        "The equations below use **raw input units** from the descriptor table. Replace missing inputs "
        "with the target's training medians listed below. The coefficients already incorporate fitted scaling; "
        "evaluate these equations directly without standardizing the inputs. Energies are in eV. "
        "Displayed coefficients have ten significant digits; CSV and JSON files retain full precision.", ""]
    for target in TARGETS:
        lines += [f"### {target}", "", f"Ridge strength $\\alpha$: **{models[target]['parameter']:g}**.", "",
                  equation(target, models[target]), "", plain_equation(target, models[target]), ""]
    lines += ["The displayed equations reproduce the saved validation predictions with a maximum "
              f"difference of {max(r['displayed_max_error_eV'] for r in errors.values()):.3g} eV.", "",
        "## Model performance", "",
        "| Target | Training structures / sites | Grouped CV R² | Grouped CV RMSE (eV) | Validation R² | Validation RMSE (eV) |",
        "|---|---:|---:|---:|---:|---:|"]
    for target in TARGETS:
        model, c, v = models[target], cv[target], validation[target]
        lines.append(f"| {target} | {model['training_structures']} / {model['training_site_rows']} | "
            f"{float(c['CV_mean_R2']):.3f} | {float(c['CV_mean_RMSE_eV']):.3f} | "
            f"{float(v['R2']):.3f} | {float(v['RMSE_eV']):.3f} |")
    selecting = config.get("descriptor_selection_in_outer_folds", False)
    lines += ["", "CV scores are the mean of three repeated five-fold structure-grouped evaluations. "
        "Both sites from a structure stay together in each split. " +
        (f"Inside each outer training partition, four-fold grouped CV selects one shared input set from "
         f"{config['descriptor_set_count']} candidates and a ridge strength for each target. The selected descriptor set "
         "is identical across targets within a fold and may differ between folds. Linear ridge is used throughout."
         if selecting else f"The {count} descriptors and linear form are fixed in every fold; ridge strength is chosen "
         "using four-fold grouped CV within each outer training partition."), "",
        ("The reported CV includes descriptor selection inside the outer folds. Metal separation is mandatory. "
         "A candidate must have no higher inner-CV MSE than the reference input set for any target; eligible candidates "
         "minimize the mean target-variance-normalized inner MSE. Only one adsorption-metal ligand-charge summary "
         "and one adsorption-metal ligand-dipole summary may be selected."
         if selecting else f"The {count} inputs are fixed for the current split. CV evaluates fitting and ridge-strength "
         "selection conditional on these inputs. It does not independently evaluate the exploratory process used to choose the descriptors."), "",
        ("The final common descriptor set and ridge strengths are chosen " if selecting else "Final ridge strengths are chosen ")
        + "using three repeated four-fold grouped CV runs on training data, "
        "then each model is fitted to all its training sites. The ridge grid is "
        "0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000 and 10000. "
        "Validation energies are not used to choose the current ridge strengths.", "",
        "## Training and validation selection", "",
        f"All three targets use the same {split['training_structures']} training structures / {split['training_site_rows']} sites "
        f"and {len(split['validation_structures'])} validation structures / {split['validation_site_rows']} sites. "
        "Eligible sites require all three finite, raw-DFT-matched energy labels and pass the recorded endpoint/data-quality filters. "
        "Training sites are retained regardless of their model prediction errors.", "",
        "Invalid endpoint geometries remain excluded from training and validation. Each selected OH/O/OOH endpoint "
        "must have a verified mapping and atomic arrays, nearest adsorbate O within 3.0 Angstrom of the intended metal "
        "and support, and OOH O-O separation at most 2.0 Angstrom. Any failed endpoint excludes that site from all "
        "three targets. The checks use the OOH orientation selected for the energy label. "
        "[Endpoint geometry checks](representative_split/selected_endpoint_geometry_checks.csv) and "
        "[data-quality exclusion ledger](representative_split/data_quality_exclusion_ledger.csv) record the evidence.", "",
        *([f"The {split['excluded_whole_structure_count']} structures in the "
            "[distance exclusion record](representative_split/relative_distance_exclusions.json) are excluded in full "
            "from all three targets, including both adsorption sites. Their selected O, OH or OOH distance is at least "
            "5% above the fixed mean for the same adsorption metal and adsorbate. The reference means and structure "
            "list are fixed; rebuilding the split does not repeatedly recalculate exclusions. "
            "[Reference means](representative_split/relative_distance_reference_means.csv) and "
            "[flagged endpoints](representative_split/relative_distance_flagged_endpoints.csv) give the numerical evidence.", ""]
          if split.get("relative_distance_exclusion_file") else []),
        ("Target values were used to improve even spacing across their eligible ranges; model errors and prediction scores did not choose membership. "
         if split.get("target_value_spread_objective") else
         "Validation membership is selected using clean-structure chemistry and descriptor ranges. ")
        + "Both sites of each structure stay together.", "",
        f"The validation set covers {len(split['validation_metals'])} metals ({', '.join(split['validation_metals'])}), "
        f"{len(split['validation_environments'])} ligand environments (N-only, N/O and N/S), "
        f"and {len(split['validation_metal_pairs'])} of the {pair_count} available metal pairs. "
        "Each validation pair and ligand environment is also represented in training; singleton pairs stay in training.", "",
        f"All {count} validation inputs lie within the training minima and maxima. Metal charge and spin magnitudes also "
        "lie within training ranges for that same metal and adsorption/partner role. These are coordinatewise bounds, "
        "not a guarantee of inclusion in the multivariate training convex hull. See the "
        "[split report and structure list](representative_split/report.md), "
        "[chemistry coverage](representative_split/chemistry_coverage.csv) and "
        "[descriptor range checks](representative_split/descriptor_range_checks.csv).", "",
        "These results measure interpolation among represented chemistries. They are conditional on the chosen inputs "
        "and eligibility filters. Validation labels have already been examined during model development; this is not "
        "an untouched external test or an estimate of extrapolation to unseen chemistries.", "",
        "## Missing values and fitting", "",
        "| Symbol | Descriptor | OH median | O median | OOH median |", "|---|---|---:|---:|---:|"]
    prep = read("model_preprocessing.csv")
    medians = {(r["target"], r["descriptor_key"]): float(r["median"]) for r in prep}
    for r in descriptors:
        lines.append(f"| $x_{{{r['index']}}}$ | {r['name']} | " +
                     " | ".join(f"{medians[t, r['key']]:.10g}" for t in TARGETS) + " |")
    lines += ["", r"For fitting, median-imputed inputs $\widetilde x_j$ are standardized as "
        r"$z_j=(\widetilde x_j-\overline x_j)/s_j$. "
        "All medians, means and population standard deviations come from the applicable training partition. "
        "An entirely missing training column has median zero; standard deviations at most $10^{-12}$ are replaced by one.", "",
        "The fitting objective is:", "", r"$$",
        r"\min_{b,\boldsymbol\beta}\left[\sum_{i\in T}"
        rf"\left(G_i-b-\sum_{{j=1}}^{{{count}}}\beta_j z_{{ij}}\right)^2"
        rf"+\alpha\sum_{{j=1}}^{{{count}}}\beta_j^2\right].", r"$$", "",
        "The ridge penalty acts on fitted coefficients and controls their magnitude. "
        "The intercept is unpenalized. The fitted scaling is incorporated into the raw-input equations above.", ""]
    graphs = OUT / "graphs"
    graphs.mkdir(exist_ok=True)
    cv_rows = read("nested_cv_predictions.csv")
    for target in TARGETS:
        for kind, rows in (("nested_cv", cv_rows), ("validation", validation_rows)):
            (graphs / f"{target}_{kind}.svg").write_text(scatter_svg(
                [r for r in rows if r["target"] == target], target,
                "grouped CV" if kind == "nested_cv" else "validation"), encoding="utf-8")
    lines += ["## Prediction graphs", "",
        "CV graphs pool predictions across the three repeats; their pooled R² differs from the mean repeat R² in the table.", "",
        "| Target | Grouped CV | Validation |", "|---|---|---|"]
    for target in TARGETS:
        lines.append(f"| {target} | ![{target} grouped CV](shared_descriptor_search/graphs/{target}_nested_cv.svg) | "
                     f"![{target} validation](shared_descriptor_search/graphs/{target}_validation.svg) |")
    from build_overpotential_report import build_overpotential_section
    lines += ["", *build_overpotential_section()]
    lines += ["", "## Model files and reproduction", "",
        "The current model files are in `shared_descriptor_search/`:", "",
        "- [Descriptor names, formulas and units](shared_descriptor_search/selected_descriptors.csv)",
        "- [Full-precision equations and model parameters](shared_descriptor_search/model_parameters.json)",
        "- [Model coefficients](shared_descriptor_search/model_coefficients.csv)",
        "- [Training medians and scaling](shared_descriptor_search/model_preprocessing.csv)",
        "- [Model metrics](shared_descriptor_search/model_metrics.csv)",
        "- [Grouped CV predictions](shared_descriptor_search/nested_cv_predictions.csv)",
        "- [Validation predictions](shared_descriptor_search/validation_predictions.csv)",
        "- [Training and validation membership](shared_descriptor_search/cohort_membership.csv)", "",
        "Reproduce the fit and reports from the repository root:", "", "```powershell",
        "python article/KongiCats/calculations/models_20261011_dipole_ridge/run_shared_descriptor_search.py",
        "```", "", "Fitting uses NumPy; overpotential graphs use Matplotlib. "
        "Matplotlib can be installed locally with "
        "`python -m pip install --target article/KongiCats/calculations/models_20261011_dipole_ridge/.plot_dependencies matplotlib`. "
        "To rebuild reports from the fitted model files, run "
        "`python article/KongiCats/calculations/models_20261011_dipole_ridge/build_current_report.py`.", ""]
    (HERE / "selected_models_full_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("Published current model report and descriptor formulas", flush=True)


if __name__ == "__main__":
    build_report()
