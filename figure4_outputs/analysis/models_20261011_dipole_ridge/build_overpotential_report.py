#!/usr/bin/env python3
"""Calculate same-site ORR overpotentials and publish structure-level comparisons."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from current_site_descriptors import compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "shared_descriptor_search"
TARGETS = ("G_OH", "G_O", "G_OOH")
U_EQ, TOTAL = 1.23, 4.92
STEPS = ("O2 -> OOH*", "OOH* -> O*", "O* -> OH*", "OH* -> H2O")


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def finite(value):
    if value in (None, ""):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def pathway(values, prefix):
    oh, oxygen, ooh = values
    steps = [TOTAL - ooh, ooh - oxygen, oxygen - oh, oh]
    index = int(np.argmin(steps))
    return {**{f"{prefix}_U_step_{i + 1}_V": v for i, v in enumerate(steps)},
            f"{prefix}_U_L_V": steps[index], f"{prefix}_overpotential_V": U_EQ - steps[index],
            f"{prefix}_determining_step": STEPS[index]}


def raw_source():
    helper_path = ROOT / "extracted" / "build_orr_analysis_energies.py"
    spec = importlib.util.spec_from_file_location("orr_energy_source", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    metadata = {r["name"]: r for r in helper.read_ase_rows(helper.ENERGY_METADATA_DB)}
    raw = {state: helper.index_unique(helper.read_ase_rows(path),
        lambda r: (r["parent_name"], r["ads_site"]), str(path))
        for state, path in helper.RAW_DATABASES.items()}
    return helper, metadata, raw


def dft_inputs(name, site, helper, metadata, raw):
    meta = metadata.get(name, {})
    values = [finite(meta.get(f"E_ads_{state}_{site}")) for state in ("OH", "O", "OOH")]
    totals = {state: finite(rows.get((name, site), {}).get("post_opt_rpbe_d4_E"))
              for state, rows in raw.items()}
    options = [(orientation, totals[f"OOH_{orientation}"]) for orientation in ("x", "z")
               if totals[f"OOH_{orientation}"] is not None]
    orientation, selected = min(options, key=lambda item: item[1]) if options else ("", None)
    matches = [helper.is_match(finite(meta.get(f"E_tot_{state}_{site}")),
        selected if state == "OOH" else totals[state]) for state in ("OH", "O", "OOH")]
    complete = all(v is not None for v in values) and all(matches)
    missing = [state for state, v, matched in zip(("OH", "O", "OOH"), values, matches)
               if v is None or not matched]
    return values, complete, orientation, missing


def site_features(source, index):
    return compute(source, index)


def predict(features, model):
    values = np.asarray([features[f] for f in model["descriptor_keys"]])
    values = np.where(np.isfinite(values), values, model["imputation_medians"])
    if model["family"] != "ridge" or len(model["raw_linear_coefficients"]) != len(values):
        raise ValueError("overpotential predictions require one linear coefficient per current descriptor")
    return float(model["raw_intercept"] + values @ np.asarray(model["raw_linear_coefficients"]))


def scores(rows):
    if not rows:
        return dict(count=0)
    x = np.asarray([r["dft_overpotential_V"] for r in rows])
    y = np.asarray([r["predicted_overpotential_V"] for r in rows])
    delta = y - x
    denominator = np.sum((x - x.mean()) ** 2)
    return dict(count=len(rows), structures=len({r["name"] for r in rows}),
        R2=float(1 - np.sum(delta ** 2) / denominator) if denominator > 0 else None,
        pearson_r=float(np.corrcoef(x, y)[0, 1]) if len(rows) > 1 and np.std(x) > 0 and np.std(y) > 0 else None,
        RMSE_V=float(np.sqrt(np.mean(delta ** 2))), MAE_V=float(np.mean(abs(delta))))


def draw(rows, stem, title):
    import matplotlib.pyplot as plt

    stats = scores(rows)
    x = np.asarray([r["dft_overpotential_V"] for r in rows])
    y = np.asarray([r["predicted_overpotential_V"] for r in rows])
    low, high = min(x.min(), y.min()), max(x.max(), y.max())
    padding = max((high - low) * 0.07, 0.04)
    limits = (low - padding, high + padding)
    colors = {"training": "#2673a5", "validation": "#dd7833", "other": "#858585", "grouped_cv": "#2673a5"}
    labels = {"training": "Training: fitted predictions", "validation": "Validation", "other": "Outside common training/validation", "grouped_cv": "Grouped CV predictions"}
    fig, ax = plt.subplots(figsize=(7.3, 6.1), constrained_layout=True)
    categories = sorted({r.get("prediction_group", "other") for r in rows})
    for group in categories:
        indices = [i for i, r in enumerate(rows) if r.get("prediction_group", "other") == group]
        ax.scatter(x[indices], y[indices], s=32, color=colors[group], alpha=0.75, edgecolor="white", linewidth=0.4, label=labels[group])
    ax.plot(limits, limits, color="#303030", linewidth=1.2, linestyle="--", label="Perfect agreement")
    ax.set(xlim=limits, ylim=limits, xlabel="DFT-based overpotential (V)", ylabel="Predicted overpotential (V)", title=title)
    ax.set_aspect("equal", adjustable="box")
    ax.text(0.03, 0.97, f"n = {stats['count']}\n$R^2$ = {stats['R2']:.3f}\nr = {stats['pearson_r']:.3f}\nRMSE = {stats['RMSE_V']:.3f} V",
            transform=ax.transAxes, va="top", bbox=dict(facecolor="white", alpha=0.9, edgecolor="#dddddd"))
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.16)
    for extension in ("png", "svg", "pdf"):
        fig.savefig(OUT / "graphs" / f"{stem}.{extension}", dpi=220)
    plt.close(fig)


def build_overpotential_section(models_override=None, output_directory=None, feature_function=None,
                                prediction_function=None, report_prefix="shared_descriptor_search"):
    global OUT
    if output_directory is not None:
        OUT = Path(output_directory)
    # Keep the fitting NumPy environment unchanged while loading plotting dependencies.
    dependencies = HERE / ".plot_dependencies"
    if dependencies.exists():
        sys.path.insert(0, str(dependencies))
    os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".matplotlib_cache"))
    import matplotlib
    matplotlib.use("Agg")

    notebook_path = ROOT / "archive" / "ML-article_2026_DAC_ORR_analysis.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    cell_sources = ["".join(cell.get("source", [])) for cell in notebook["cells"]]
    calculation = next(s for s in cell_sources if "def add_che_results" in s)
    if not all(expr in calculation for expr in ("ORR_FREE_ENERGY - result['G_OOH']",
        "result['G_OOH'] - result['G_O']", "result['G_O'] - result['G_OH']", "U_EQ - result['U_L']")):
        raise ValueError("notebook overpotential expression changed")
    models = models_override if models_override is not None else json.loads((OUT / "model_parameters.json").read_text(encoding="utf-8"))
    feature_keys = list(dict.fromkeys(f for t in TARGETS for f in models[t]["descriptor_keys"]))
    structures = {r["name"]: r for r in read(ROOT / "extracted" / "structures_by_target.csv")}
    feature_file = HERE / ("current_site_features.csv" if (HERE / "current_site_features.csv").exists() else "dipole_site_features.csv")
    existing_features = {(r["name"], r["ads_site"]): r for r in read(feature_file)}
    existing_labels = {(r["name"], r["ads_site"]): r for r in read(ROOT / "extracted" / "orr_analysis_energies.csv")}
    roles = {(r["target"], r["name"], r["ads_site"]): r["role"] for r in read(OUT / "cohort_membership.csv")}
    helper, metadata, raw = raw_source()
    site_rows = []
    for name, source in sorted(structures.items()):
        for index, site in enumerate(("metal1", "metal2")):
            calculated = (feature_function or site_features)(source, index)
            features = {f: calculated[f] for f in feature_keys}
            if (name, site) in existing_features:
                for f in feature_keys:
                    if f not in existing_features[name, site]:
                        continue
                    stored = finite(existing_features[name, site][f])
                    actual = finite(features[f])
                    if (stored is None) != (actual is None) or stored is not None and abs(stored - actual) > 1e-10:
                        raise ValueError(f"descriptor mismatch: {name} {site} {f}")
            predicted = [(prediction_function or predict)(features, models[t]) for t in TARGETS]
            dft, complete, orientation, missing = dft_inputs(name, site, helper, metadata, raw)
            target_roles = [roles.get((t, name, site), "outside_model_cohort") for t in TARGETS]
            group = "training" if all(r == "training" for r in target_roles) else "validation" if all(r == "validation" for r in target_roles) else "other"
            row = dict(id=source["id"], name=name, ads_site=site, ads_metal=source[site],
                other_metal=source["metal2" if index == 0 else "metal1"], prediction_group=group,
                **{f"{t}_cohort_role": role for t, role in zip(TARGETS, target_roles)},
                **features, **{f"predicted_{t}_eV": value for t, value in zip(TARGETS, predicted)},
                **{f"dft_{t}_eV": value for t, value in zip(TARGETS, dft)},
                dft_complete_verified=complete, dft_missing_or_unverified_targets=";".join(missing), OOH_orientation=orientation,
                dft_notebook_energy_filter_pass=complete and dft[0] >= 0 and dft[1] <= TOTAL,
                **pathway(predicted, "predicted"))
            if complete:
                row.update(pathway(dft, "dft"))
                row["overpotential_error_V"] = row["predicted_overpotential_V"] - row["dft_overpotential_V"]
            stored_label = existing_labels.get((name, site))
            if stored_label and complete:
                if stored_label["raw_complete_match"] != "True" or abs(float(stored_label["overpotential"]) - row["dft_overpotential_V"]) > 1e-10:
                    raise ValueError(f"DFT pathway mismatch: {name} {site}")
            site_rows.append(row)
    write("overpotential_site_calculations.csv", site_rows)
    paired = [r for r in site_rows if r["dft_complete_verified"]]
    filtered = [r for r in paired if r["dft_notebook_energy_filter_pass"]]
    validation = [r for r in paired if r["prediction_group"] == "validation"]
    structure_rows = []
    for name in sorted(structures):
        sites = [r for r in site_rows if r["name"] == name]
        available = [r for r in sites if r["dft_complete_verified"]]
        predicted_all = min(sites, key=lambda r: r["predicted_overpotential_V"])
        row = dict(id=structures[name]["id"], name=name, available_dft_sites=len(available),
            predicted_best_site_all=predicted_all["ads_site"], predicted_best_overpotential_all_V=predicted_all["predicted_overpotential_V"])
        if available:
            observed_best = min(available, key=lambda r: r["dft_overpotential_V"])
            predicted_best = min(available, key=lambda r: r["predicted_overpotential_V"])
            group = "validation" if all(r["prediction_group"] == "validation" for r in available) else "training" if all(r["prediction_group"] == "training" for r in available) else "other"
            row.update(dft_best_site=observed_best["ads_site"], dft_overpotential_V=observed_best["dft_overpotential_V"],
                predicted_best_site_matched=predicted_best["ads_site"], predicted_overpotential_V=predicted_best["predicted_overpotential_V"],
                prediction_group=group, overpotential_error_V=predicted_best["predicted_overpotential_V"] - observed_best["dft_overpotential_V"])
        structure_rows.append(row)
    write("overpotential_structure_calculations.csv", structure_rows)
    structure_paired = [r for r in structure_rows if r["available_dft_sites"]]
    cv_groups = {}
    for r in read(OUT / "nested_cv_predictions.csv"):
        bucket = cv_groups.setdefault((int(r["repeat"]), r["name"], r["ads_site"]), {})
        bucket[r["target"]] = r
    paired_by_key = {(r["name"], r["ads_site"]): r for r in paired}
    cv_rows = []
    for (repeat, name, site), bucket in sorted(cv_groups.items()):
        if set(bucket) != set(TARGETS) or (name, site) not in paired_by_key:
            continue
        if len({r["fold"] for r in bucket.values()}) != 1:
            raise ValueError("OOF target predictions have inconsistent held-out structures")
        dft = [float(bucket[t]["observed_eV"]) for t in TARGETS]
        predicted = [float(bucket[t]["predicted_eV"]) for t in TARGETS]
        row = dict(name=name, ads_site=site, repeat=repeat, fold=int(bucket["G_OH"]["fold"]), prediction_group="grouped_cv",
            **{f"dft_{t}_eV": v for t, v in zip(TARGETS, dft)},
            **{f"predicted_{t}_eV": v for t, v in zip(TARGETS, predicted)},
            **pathway(dft, "dft"), **pathway(predicted, "predicted"))
        row["overpotential_error_V"] = row["predicted_overpotential_V"] - row["dft_overpotential_V"]
        cv_rows.append(row)
    write("overpotential_grouped_cv_predictions.csv", cv_rows)
    metrics = [dict(dataset=label, **scores(rows)) for label, rows in (
        ("all_complete_sites_final_fit", paired), ("notebook_filtered_sites_final_fit", filtered),
        ("complete_structures_matched_site_sets_final_fit", structure_paired),
        ("validation_sites", validation), ("grouped_cv_sites_pooled_repeats", cv_rows))]
    for index, repeat in enumerate(sorted({r["repeat"] for r in cv_rows}), 1):
        metrics.append(dict(dataset=f"grouped_cv_repeat_{index}", **scores([r for r in cv_rows if r["repeat"] == repeat])))
    write("overpotential_metrics.csv", metrics)
    (OUT / "graphs").mkdir(exist_ok=True)
    for rows, stem, title in (
        (structure_paired, "overpotential_structures", "Structure overpotential: best available site"),
        (paired, "overpotential_all_sites", "Same-site ORR overpotential: all complete DFT pathways"),
        (filtered, "overpotential_notebook_filtered", "Same-site ORR overpotential: notebook energy filter"),
        (validation, "overpotential_validation", "ORR overpotential: validation sites"),
        (cv_rows, "overpotential_grouped_cv", "ORR overpotential: grouped cross-validation")):
        draw(rows, stem, title)
    paths = [notebook_path, Path(__file__), HERE / "current_site_descriptors.py", helper.ENERGY_METADATA_DB,
        ROOT / "extracted" / "structures_by_target.csv", OUT / "model_parameters.json", *helper.RAW_DATABASES.values()]
    (OUT / "overpotential_config.json").write_text(json.dumps(dict(equilibrium_potential_V=U_EQ,
        total_ORR_free_energy_eV=TOTAL, same_site_only=True, complete_raw_energy_tolerance_eV=1e-8,
        structure_comparison="minimum overpotential over the same DFT-complete site set for each method",
        energy_filter="record G_OH >= 0 and G_O <= 4.92; retain all complete pathways in main table",
        spin_source="data.post_opt_rpbe_d4_magmoms", matplotlib_version=matplotlib.__version__,
        sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}), indent=2) + "\n", encoding="utf-8")

    lines = ["## ORR limiting potential and overpotential", "",
        "The calculation follows `add_che_results()` in "
        "[ML-article_2026_DAC_ORR_analysis.ipynb](../../archive/ML-article_2026_DAC_ORR_analysis.ipynb). "
        "For each adsorption site, all three intermediate energies belong to that same site. "
        "The four one-electron step potentials are:", "", r"$$",
        r"U_1=(4.92-G_{\mathrm{OOH}})/e,\quad U_2=(G_{\mathrm{OOH}}-G_{\mathrm O})/e,\quad",
        r"U_3=(G_{\mathrm O}-G_{\mathrm{OH}})/e,\quad U_4=G_{\mathrm{OH}}/e.", r"$$", "", r"$$",
        r"U_L=\min(U_1,U_2,U_3,U_4),\qquad \eta_{\mathrm{ORR}}=1.23\ \mathrm V-U_L.", r"$$", "",
        "Here $e$ is the elementary charge. With energies in eV and one electron transferred per step, the numerical step values are in V. "
        "The potential-determining step is the step with the smallest potential; ties use the first step. "
        "DFT-based overpotential uses the stored DFT-derived adsorption energies. Predicted overpotential "
        "uses the three current regression predictions. No extra energy corrections are introduced; "
        "the thermodynamic interpretation follows the supplied energy convention.", "",
        f"The calculation covers **{len(structures)} structures / {len(site_rows)} possible metal sites**. "
        f"Complete, raw-verified DFT pathways exist for **{len(paired)} sites in {len(structure_paired)} structures**. "
        "Predictions are supplied for both metal sites, including structures whose DFT pathway is incomplete. "
        "Incomplete DFT overpotentials remain blank; available predicted energies never fill missing DFT energies.", "",
        "DFT verification requires source total energies for OH, O and the lowest-energy available OOH x/z "
        "orientation to match the corresponding raw same-site calculations within $10^{-8}$ eV. "
        rf"The notebook's energy filter ($G_{{OH}}\geq0$, $G_O\leq4.92$ eV) retains {len(filtered)} sites. "
        "Its pass/fail flag is included in the site CSV; the complete-pathway table includes every verified site.", "",
        "### Predicted versus DFT-based overpotential", "",
        "For a structure, the reported overpotential is the minimum site overpotential. "
        "The correlation graph compares minima over the **same DFT-complete site set** for each structure. "
        "The table also lists the best predicted value over both metal sites, which can include a site without a complete DFT pathway.", "",
        "![Predicted versus DFT-based structure overpotential](shared_descriptor_search/graphs/overpotential_structures.png)", "",
        "| Evaluation | Points | R² | Pearson r | RMSE (V) | MAE (V) |", "|---|---:|---:|---:|---:|---:|"]
    labels = {"all_complete_sites_final_fit": "All complete sites: final fitted models",
        "notebook_filtered_sites_final_fit": "Notebook energy-filtered sites: final fitted models",
        "complete_structures_matched_site_sets_final_fit": "Structures: same available site sets",
        "validation_sites": "Validation sites", "grouped_cv_sites_pooled_repeats": "Grouped CV sites: pooled repeats"}
    for m in metrics[:5]:
        lines.append(f"| {labels[m['dataset']]} | {m['count']} | {m['R2']:.3f} | {m['pearson_r']:.3f} | {m['RMSE_V']:.3f} | {m['MAE_V']:.3f} |")
    lines += ["", "All-site and structure correlations include training predictions and are descriptive fit summaries. "
        "The validation graph uses sites held out from all three fits. The grouped CV graph combines three "
        "same-fold held-out energy predictions before calculating each site's overpotential, and pools the three repeats. "
        f"Its {len(cv_rows)} plotted predictions represent {len({(r['name'], r['ads_site']) for r in cv_rows})} distinct sites "
        f"in {len({r['name'] for r in cv_rows})} structures. "
        "These scores remain exploratory and conditional on the curated cohorts and chosen descriptor set.", "",
        "Overpotential is evaluated directly because it depends on differences between intermediate energies "
        "and selection of the smallest step potential. Accurate intermediate-energy regressions can still "
        "produce a less accurate overpotential or change the predicted determining step.", "",
        "| Validation sites | Grouped CV sites |", "|---|---|",
        "| ![Validation overpotential](shared_descriptor_search/graphs/overpotential_validation.png) | "
        "![Grouped CV overpotential](shared_descriptor_search/graphs/overpotential_grouped_cv.png) |", "",
        "[All-site correlation graph](shared_descriptor_search/graphs/overpotential_all_sites.png); "
        "[notebook energy-filtered correlation graph](shared_descriptor_search/graphs/overpotential_notebook_filtered.png). "
        "Every overpotential graph is also saved as SVG and PDF in `shared_descriptor_search/graphs/`.", "",
        "### Overpotential for every structure", "",
        "`DFT η` and `Predicted η (matched sites)` use the same available DFT-complete site set. "
        "`Predicted η (both sites)` uses both metal sites. All values are in V; a dash indicates an incomplete DFT pathway.", "",
        "| ID | Structure | DFT sites | DFT best site | DFT η | Predicted best matched site | Predicted η (matched sites) | Predicted best site | Predicted η (both sites) |",
        "|---:|---|---:|---|---:|---|---:|---|---:|"]
    for row in sorted(structure_rows, key=lambda r: int(r["id"])):
        dft_text = f"{row['dft_overpotential_V']:.4f}" if row["available_dft_sites"] else "—"
        predicted_text = f"{row['predicted_overpotential_V']:.4f}" if row["available_dft_sites"] else "—"
        lines.append(f"| {row['id']} | {row['name']} | {row['available_dft_sites']} | {row.get('dft_best_site', '—')} | "
            f"{dft_text} | {row.get('predicted_best_site_matched', '—')} | {predicted_text} | "
            f"{row['predicted_best_site_all']} | {row['predicted_best_overpotential_all_V']:.4f} |")
    lines += ["", "### Detailed calculations", "",
        "- [All site calculations](shared_descriptor_search/overpotential_site_calculations.csv): raw descriptors, "
        "DFT and predicted intermediate energies, four step potentials, limiting potential, overpotential, "
        "determining step, source verification, notebook energy-filter flag and training/validation membership.",
        "- [All structure calculations](shared_descriptor_search/overpotential_structure_calculations.csv)",
        "- [Grouped CV overpotential calculations](shared_descriptor_search/overpotential_grouped_cv_predictions.csv)",
        "- [Overpotential metrics](shared_descriptor_search/overpotential_metrics.csv)", ""]
    print(f"Calculated ORR overpotential: {len(site_rows)} sites, {len(paired)} DFT pairs, {len(structure_paired)} paired structures", flush=True)
    return [line.replace("shared_descriptor_search/", report_prefix + "/") for line in lines]
