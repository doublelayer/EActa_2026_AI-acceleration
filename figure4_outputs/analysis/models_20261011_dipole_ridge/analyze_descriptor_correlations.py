#!/usr/bin/env python3
"""Describe raw descriptor/DFT-target correlations without changing fitted models."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

from descriptor_catalog import catalog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "descriptor_correlation_analysis"
TARGETS = ("G_OH", "G_O", "G_OOH", "overpotential")
SEED, BOOTSTRAPS = 20261011, 2000


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def key(row):
    return row["name"], row["ads_site"]


def write(name, rows):
    fields = list(dict.fromkeys(f for row in rows for f in row))
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def numeric(value):
    return float(value) if value not in (None, "") else math.nan


def extended_catalog():
    definitions = catalog()

    def add(name, label, formula, unit, description):
        definitions[name] = dict(key=name, name=label, formula=formula, units=unit, description=description)

    add("ligand_plane_rms_A", "Ligand nonplanarity", r"\sqrt{\operatorname{Mean}_{H_s}[((\mathbf r_i-\mathbf c)\cdot\mathbf n)^2]}",
        "Angstrom", "RMS perpendicular ligand displacement from the best-fit plane; requires at least three selected ligands.")
    add("metal_height_above_ligand_plane_A", "Metal displacement from ligand plane", r"|(\mathbf r_s-\mathbf c)\cdot\mathbf n|",
        "Angstrom", "Absolute distance of adsorption metal from the best-fit ligand plane.")
    add("shared_ligand_count", "Shared ligand count", r"\#(H_s\cap H_p)", "count", "Number of N/O/S ligands within 2.30 Angstrom of both metals.")
    add("terminal_ligand_count", "Terminal ligand count", r"\#(H_s\setminus H_p)", "count", "Number of selected adsorption-metal ligands that do not neighbor the partner metal.")
    for prefix, symbol, metal in (("site", "s", "Adsorption metal"), ("partner", "p", "Partner metal")):
        for ligand_type, shell in (("shared", "B"), ("terminal", rf"H_{symbol}\setminus B")):
            add(f"{prefix}_{ligand_type}_ligand_charge_mean_e", f"{metal}: mean {ligand_type} ligand charge",
                rf"\operatorname{{Mean}}_{{{shell}}}(q_i)", "e", f"Mean signed Bader charge of {ligand_type} ligands in this metal's shell.")
    for element, label in (("C", "carbon"), ("heteroatom", "N/O/S")):
        for center in (2.8, 3.6):
            add(f"second_shell_{element}_{center:.1f}A", f"Second-shell {label} density near {center:.1f} Angstrom",
                rf"\sum_i\exp[-((d_{{is}}-{center})/0.45)^2]", "dimensionless",
                "Sum over the specified support atoms farther than 2.30 Angstrom from the adsorption metal; both metals excluded.")
    for statistic, label, operator in (("mean", "Mean", "Mean"), ("std", "Spread of", "SD"), ("min", "Smallest", "Min"), ("max", "Largest", "Max")):
        add(f"partner_angle_{statistic}_deg", f"{label} ligand angle at partner metal",
            rf"\operatorname{{{operator}}}_{{P_p}}(\theta_{{ij,p}})", "degree",
            "Summary over all unique selected ligand pairs, with the partner metal as the angle vertex.")
    return definitions


def partner_angles(source, site):
    z = np.asarray(json.loads(source["array.numbers"]), dtype=int)
    xyz = np.asarray(json.loads(source["array.positions"]), dtype=float).reshape(-1, 3)
    partner = 1 if site == "metal1" else 0
    distance = np.linalg.norm(xyz - xyz[partner], axis=1)
    selected = np.isin(z, (7, 8, 16)) & (distance <= 2.30)
    selected[:2] = False
    vector = xyz[selected] - xyz[partner]
    angles = []
    for i in range(len(vector)):
        for j in range(i + 1, len(vector)):
            cosine = np.dot(vector[i], vector[j]) / (np.linalg.norm(vector[i]) * np.linalg.norm(vector[j]))
            angles.append(float(np.degrees(np.arccos(np.clip(cosine, -1, 1)))))
    return {f"partner_angle_{stat}_deg": float(op(angles)) if angles else math.nan
            for stat, op in (("mean", np.mean), ("std", np.std), ("min", np.min), ("max", np.max))}


def tied_ranks(values):
    order = np.argsort(values, kind="stable")
    sorted_values = values[order]
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2 + 1
        start = end
    return ranks


def constant(values):
    return np.ptp(values) <= 1e-12 * max(1.0, float(np.max(abs(values))))


def correlation(x, y):
    if len(x) < 3:
        return None, None, "fewer_than_three_pairs"
    if constant(x) or constant(y):
        return None, None, "constant_or_numerically_constant"
    return float(np.corrcoef(x, y)[0, 1]), float(np.corrcoef(tied_ranks(x), tied_ranks(y))[0, 1]), "ok"


def cluster_interval(x, y, names, rng):
    # Resample structures with both site rows together; weighted sufficient statistics
    # give the exact Pearson coefficient for each resampled collection of site rows.
    if len(x) < 3 or constant(x) or constant(y):
        return None, None
    unique = sorted(set(names))
    groups = np.asarray([unique.index(n) for n in names])
    x, y = x - x.mean(), y - y.mean()
    sums = np.column_stack([np.bincount(groups, weights=v, minlength=len(unique))
                            for v in (np.ones(len(x)), x, y, x * x, y * y, x * y)])
    weights = rng.multinomial(len(unique), np.full(len(unique), 1 / len(unique)), size=BOOTSTRAPS)
    n, sx, sy, sxx, syy, sxy = (weights @ sums).T
    covariance = sxy - sx * sy / n
    vx, vy = sxx - sx ** 2 / n, syy - sy ** 2 / n
    valid = (vx > 1e-20) & (vy > 1e-20)
    coefficients = covariance[valid] / np.sqrt(vx[valid] * vy[valid])
    return tuple(float(v) for v in np.percentile(coefficients, (2.5, 97.5))) if len(coefficients) else (None, None)


def load():
    definitions = extended_catalog()
    available = {key(r): r for r in read(HERE / "dipole_site_features.csv")}
    expanded = {key(r): r for r in read(HERE.parent / "models_20261008_linear_ridge_v2" / "clean_site_features.csv")}
    diagnostics = {key(r): r for r in read(HERE.parent / "review_20261008" / "candidate_geometry_diagnostics.csv")}
    sources = {r["name"]: r for r in read(ROOT / "extracted" / "structures_by_target.csv")}
    extra_keys = set(definitions) - set(catalog()) - {f"partner_angle_{s}_deg" for s in ("mean", "std", "min", "max")}
    for k, row in available.items():
        row.update({f: expanded[k].get(f, diagnostics[k].get(f, "")) for f in extra_keys})
        row.update(partner_angles(sources[k[0]], k[1]))
    labels = {key(r): r for r in read(ROOT / "extracted" / "orr_analysis_energies.csv")}
    cohort = read(HERE / "shared_descriptor_search" / "cohort_membership.csv")
    train = {t: {key(r) for r in cohort if r["target"] == t and r["role"] == "training"} for t in TARGETS[:3]}
    common = set.intersection(*train.values())
    used = set(json.loads((HERE / "shared_descriptor_search" / "run_config.json").read_text(encoding="utf-8"))["shared_descriptors"])
    return definitions, available, labels, train, common, used


def heatmap(results, unused, definitions, kind):
    dependencies = HERE / ".plot_dependencies"
    if dependencies.exists():
        sys.path.insert(0, str(dependencies))
    os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".matplotlib_cache"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    matrix = np.asarray([[results[f, t][kind] if results[f, t][kind] is not None else np.nan for t in TARGETS] for f in unused])
    fig, ax = plt.subplots(figsize=(14, 0.34 * len(unused) + 2.0), constrained_layout=True)
    color_map = plt.get_cmap("RdBu_r").copy()
    color_map.set_bad("#eeeeee")
    image = ax.imshow(matrix, cmap=color_map, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(4), ("OH energy", "O energy", "OOH energy", "DFT overpotential"))
    ax.set_yticks(range(len(unused)), [definitions[f]["name"] for f in unused], fontsize=9)
    ax.tick_params(axis="x", top=True, labeltop=True, bottom=False, labelbottom=False)
    for i in range(len(unused)):
        for j in range(4):
            value = matrix[i, j]
            ax.text(j, i, f"{value:+.2f}" if np.isfinite(value) else "NA", ha="center", va="center",
                    color="white" if np.isfinite(value) and abs(value) > 0.65 else "black", fontsize=8)
    label = "Pearson r" if kind == "pearson_r" else "Spearman rho"
    ax.set_title(f"Unused descriptors versus DFT targets: {label}\nCommon training cohort; pairwise complete observations", pad=48)
    fig.colorbar(image, ax=ax, fraction=0.025, pad=0.03, label=label)
    paths = []
    for extension in ("png", "svg", "pdf"):
        path = OUT / f"unused_descriptors_{kind}.{extension}"
        try:
            fig.savefig(path, dpi=180)
        except PermissionError:
            # An open viewer may lock an existing Windows export. Preserve it and publish a fresh named export.
            from uuid import uuid4
            path = OUT / f"unused_descriptors_{kind}_{uuid4().hex[:8]}.{extension}"
            fig.savefig(path, dpi=180)
        paths.append(str(path.relative_to(OUT)))
    plt.close(fig)
    return paths


def display(value):
    return f"{value:+.3f}" if value is not None else "NA"


def main():
    OUT.mkdir(exist_ok=True)
    definitions, available, labels, train, common, used = load()
    rng = np.random.default_rng(SEED)
    rows, cohort_summary = [], []
    for scope in ("common_training", "target_training", "all_verified_available"):
        for target in TARGETS:
            candidate_keys = common if scope == "common_training" else train[target] if scope == "target_training" and target != "overpotential" else common if scope == "target_training" else set(available)
            valid_target_keys = []
            for k in sorted(candidate_keys):
                label = labels[k]
                flag = "raw_complete_match" if target == "overpotential" else "raw_match_" + target.removeprefix("G_")
                if str(label.get(flag)).lower() == "true" and math.isfinite(numeric(label.get(target))):
                    valid_target_keys.append(k)
            cohort_summary.append(dict(scope=scope, target=target, target_available_sites=len(valid_target_keys),
                                       target_available_structures=len({k[0] for k in valid_target_keys})))
            for feature, definition in definitions.items():
                keys = [k for k in valid_target_keys if math.isfinite(numeric(available[k].get(feature)))]
                x = np.asarray([numeric(available[k][feature]) for k in keys])
                y = np.asarray([numeric(labels[k][target]) for k in keys])
                pearson, spearman, status = correlation(x, y)
                lo, hi = cluster_interval(x, y, [k[0] for k in keys], rng)
                rows.append(dict(scope=scope, target=target, descriptor_key=feature, readable_name=definition["name"],
                    used_in_current_models=feature in used, pair_count=len(keys), structure_count=len({k[0] for k in keys}),
                    target_available_count=len(valid_target_keys), missing_descriptor_count=len(valid_target_keys) - len(keys),
                    pearson_r=pearson, spearman_rho=spearman, pearson_cluster_CI95_low=lo, pearson_cluster_CI95_high=hi, status=status))
    write("descriptor_target_correlations.csv", rows)
    write("correlation_cohorts.csv", cohort_summary)
    write("descriptor_definitions.csv", [dict(**v, used_in_current_models=k in used) for k, v in definitions.items()])
    write("descriptor_values.csv", [dict(name=k[0], ads_site=k[1], **{f: available[k].get(f, "") for f in definitions}) for k in sorted(available)])
    results = {(r["descriptor_key"], r["target"]): r for r in rows if r["scope"] == "common_training"}
    unused = [f for f in definitions if f not in used]
    graph_exports = {kind: heatmap(results, unused, definitions, kind) for kind in ("pearson_r", "spearman_rho")}
    lines = ["# Available descriptor correlations with DFT targets", "",
        f"This analysis covers **{len(unused)} unused candidate descriptors** and the **{len(used)} current inputs**. "
        "It reports associations with OH, O and OOH energies and same-site DFT-based ORR overpotential. "
        "The model fits and descriptor selection are unchanged.", "",
        f"The main tables use the same **{len(common)} training sites in {len({k[0] for k in common})} structures** "
        "for every target. Validation sites are excluded from the main tables. "
        "Only finite, raw-verified target values and finite raw descriptor values enter each correlation. "
        "There is no median imputation; counts may vary by descriptor.", "",
        "Pearson r measures linear association. Spearman rho measures monotonic association using average ranks for ties. "
        "Values range from -1 to +1; the sign indicates direction. A correlation does not measure the independent "
        "contribution of a descriptor in a multiple-input model, and does not establish a physical mechanism.", "",
        r"$$",
        r"r_{xy}=\frac{\sum_i(x_i-\overline x)(y_i-\overline y)}{\sqrt{\sum_i(x_i-\overline x)^2\sum_i(y_i-\overline y)^2}},"
        r"\qquad \rho_{xy}=r_{\operatorname{rank}(x),\operatorname{rank}(y)}.", r"$$", "",
        "`NA` means fewer than three pairs or a constant/numerically constant descriptor or target. "
        r"Numerical constancy is a range no larger than $10^{-12}\max(1,\max|x|)$. "
        "The CSV includes a 95% structure-bootstrap interval for Pearson r, using 2,000 resamples "
        "with both sites from a structure resampled together. These intervals describe exploratory sampling variation; "
        "they do not correct for inspecting many descriptor-target pairs.", "",
        "## Pearson correlations: unused descriptors", "",
        f"![Pearson correlations]({graph_exports['pearson_r'][0]})", "",
        "| Descriptor | OH r | O r | OOH r | Overpotential r | Pairs | Structures |", "|---|---:|---:|---:|---:|---:|---:|"]
    for feature in unused:
        rs = [results[feature, target] for target in TARGETS]
        lines.append(f"| {definitions[feature]['name']} | " + " | ".join(display(r["pearson_r"]) for r in rs) +
                     f" | {rs[0]['pair_count']} | {rs[0]['structure_count']} |")
    lines += ["", "## Spearman correlations: unused descriptors", "",
        f"![Spearman correlations]({graph_exports['spearman_rho'][0]})", "",
        "| Descriptor | OH rho | O rho | OOH rho | Overpotential rho |", "|---|---:|---:|---:|---:|"]
    for feature in unused:
        lines.append(f"| {definitions[feature]['name']} | " + " | ".join(display(results[feature, target]["spearman_rho"]) for target in TARGETS) + " |")
    lines += ["", "## Current model inputs: Pearson correlations", "",
        "| Descriptor | OH r | O r | OOH r | Overpotential r |", "|---|---:|---:|---:|---:|"]
    for feature in definitions:
        if feature in used:
            lines.append(f"| {definitions[feature]['name']} | " + " | ".join(display(results[feature, target]["pearson_r"]) for target in TARGETS) + " |")
    lines += ["", "## Constant and redundant descriptors", ""]
    constant_features = [f for f in unused if results[f, "G_OH"]["status"] == "constant_or_numerically_constant"]
    if constant_features:
        lines.append("Correlation is undefined in the common training cohort for: " +
                     "; ".join(definitions[f]["name"] for f in constant_features) + ".")
        lines.append("")
    common_rows = [available[k] for k in sorted(common)]
    if all(numeric(r["shared_ligand_count"]) == 2 and numeric(r["terminal_ligand_count"]) == 2 for r in common_rows):
        lines += ["Every adsorption site in this cohort has two shared and two terminal ligands. "
                  "The ligand-count descriptors therefore provide no variation within this cohort.", ""]
    if all(numeric(r["ligand_plane_rms_A"]) == 0 for r in common_rows):
        lines += ["The stored ligand nonplanarity is zero at every common-training site.", ""]
    for prefix, label in (("site", "Adsorption metal"), ("partner", "Partner metal")):
        for quantity, suffix, description in (("charge", "e", "ligand charge"), ("spin_abs", "muB", "absolute ligand magnetic moment")):
            total = f"{prefix}_heteroatom_{quantity}_sum_{suffix}"
            mean = f"{prefix}_heteroatom_{quantity}_mean_{suffix}"
            if all(abs(numeric(r[total]) - 4 * numeric(r[mean])) < 1e-12 for r in common_rows):
                lines += [f"- {label}: total {description} equals four times its mean in this cohort. "
                          "The total and mean have identical correlations and do not supply independent linear inputs."]
    if all(abs(numeric(r["site_shared_ligand_charge_mean_e"]) - numeric(r["partner_shared_ligand_charge_mean_e"])) < 1e-12 for r in common_rows):
        lines += ["", "Mean shared-ligand charge is identical for the two metals, because both summaries use the same bridging atoms."]
    lines += ["", "## Additional cohorts and reproducibility", "",
        "The CSV also includes `target_training` correlations on each target's complete training cohort "
        f"({len(train['G_OH'])} OH sites, {len(train['G_O'])} O sites, {len(train['G_OOH'])} OOH sites; overpotential uses the common training cohort), "
        "and `all_verified_available` correlations on all available verified data, which include validation and "
        "other sites. The latter are descriptive summaries and should not guide selection using validation data.", "",
        "All ligand summaries use pooled N/O/S neighbors within 2.30 Angstrom of the corresponding metal. "
        "The dipole entries are metal-centered Bader point-charge moments. Plane descriptors use the smallest-singular-value "
        "normal of the centered ligand coordinates. The partner-metal angle summaries were calculated from the clean coordinates "
        "for this analysis. All descriptors use clean-structure information.", "",
        "- [All correlations, counts, missing-value coverage and Pearson intervals](descriptor_target_correlations.csv)",
        "- [Descriptor names, definitions and units](descriptor_definitions.csv)",
        "- [Raw descriptor values](descriptor_values.csv)",
        "- [Cohort sizes](correlation_cohorts.csv)", "",
        "Current heatmap exports: " + "; ".join(
            f"[{kind} {Path(path).suffix[1:].upper()}]({path})" for kind, paths in graph_exports.items() for path in paths) + ".", "",
        "Reproduce from the repository root:", "", "```powershell",
        "python article/KongiCats/calculations/models_20261011_dipole_ridge/analyze_descriptor_correlations.py", "```", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    paths = [Path(__file__), HERE / "descriptor_catalog.py", HERE / "dipole_site_features.csv",
        HERE.parent / "models_20261008_linear_ridge_v2" / "clean_site_features.csv",
        HERE.parent / "review_20261008" / "candidate_geometry_diagnostics.csv",
        ROOT / "extracted" / "structures_by_target.csv", ROOT / "extracted" / "orr_analysis_energies.csv",
        HERE / "shared_descriptor_search" / "cohort_membership.csv", HERE / "shared_descriptor_search" / "run_config.json"]
    (OUT / "run_config.json").write_text(json.dumps(dict(seed=SEED, bootstrap_resamples=BOOTSTRAPS,
        bootstrap_unit="structure", pairwise_complete=True, imputation=False, current_models_changed=False,
        main_scope="common_training", numpy_version=np.__version__, graph_exports=graph_exports,
        sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}), indent=2) + "\n", encoding="utf-8")
    print(f"Calculated {len(definitions)} descriptors, {len(unused)} unused, on {len(common)} common training sites", flush=True)
    for target in TARGETS:
        ranking = sorted([results[f, target] for f in unused if results[f, target]["pearson_r"] is not None],
                         key=lambda r: abs(r["pearson_r"]), reverse=True)
        print(target, json.dumps([{k: r[k] for k in ("readable_name", "pearson_r", "spearman_rho", "pair_count")} for r in ranking[:8]]), flush=True)


if __name__ == "__main__":
    main()
