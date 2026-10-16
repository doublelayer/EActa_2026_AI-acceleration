#!/usr/bin/env python3
"""Deterministic chemistry coverage holdout with descriptor-range constraints."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "representative_split"
MAX_VALIDATION = 10
TOLERANCE = 1e-10
MAX_ADSORBATE_METAL_DISTANCE = 3.0
MAX_OO_DISTANCE = 2.0
TARGETS = ("G_OH", "G_O", "G_OOH")


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(exist_ok=True)
    source_path = ROOT / "calculations/models_20261008_linear_ridge_v2/common_cohort_exclusion_ledger.csv"
    ledger = read(source_path)
    eligible = sorted({(r["name"], r["ads_site"]) for r in ledger if r["included_common_cohort"] == "True"})
    labels_path = ROOT / "extracted/orr_analysis_energies.csv"
    geometry_path = ROOT / "calculations/review_20261008/endpoint_geometry_audit.csv"
    labels = {(r["name"], r["ads_site"]): r for r in read(labels_path)}
    endpoints = {(r["state"], r["name"], r["ads_site"]): r for r in read(geometry_path)}
    relative_path = OUT / "relative_distance_exclusions.json"
    relative = json.loads(relative_path.read_text(encoding="utf-8")) if relative_path.exists() else None
    excluded_structures = set(relative["excluded_structures"]) if relative else set()
    reference_means = {(r["adsorption_metal"], r["adsorbate"]): r["mean_A"]
                       for r in relative["reference_means"]} if relative else {}
    flagged_endpoints = relative["flagged_endpoints"] if relative else []
    if relative:
        write(OUT / "relative_distance_flagged_endpoints.csv", flagged_endpoints)
        write(OUT / "relative_distance_reference_means.csv", relative["reference_means"])
    geometry_rows, rejected = [], set()
    for name, site in eligible:
        orientation = labels[name, site]["OOH_orientation"].split()[0]
        for state in ("OH", "O", "OOH" + orientation):
            row = endpoints.get((state, name, site), {})
            reasons = []
            if not row or row.get("mapping_valid") != "True" or row.get("db_arrays_verified") != "True":
                reasons.append("missing or unverified endpoint geometry")
            distance = float(row.get("nearest_adsorbate_O_to_intended_metal_A") or "nan")
            support_distance = float(row.get("nearest_adsorbate_O_to_support_atom_A") or "nan")
            oo = float(row.get("adsorbate_OO_distance_A") or "nan")
            if not np.isfinite(distance) or distance > MAX_ADSORBATE_METAL_DISTANCE:
                reasons.append("adsorbate O to intended metal exceeds 3.0 Angstrom or is missing")
            if not np.isfinite(support_distance) or support_distance > MAX_ADSORBATE_METAL_DISTANCE:
                reasons.append("adsorbate O to support exceeds 3.0 Angstrom or is missing")
            if state.startswith("OOH") and (not np.isfinite(oo) or oo > MAX_OO_DISTANCE):
                reasons.append("OOH O-O exceeds 2.0 Angstrom or is missing")
            metal = name.split("_")[1 if site == "metal1" else 2]
            adsorbate = "OOH" if state.startswith("OOH") else state
            mean = reference_means.get((metal, adsorbate))
            threshold = (1 + relative["relative_threshold"]) * mean if mean is not None else None
            relative_failed = threshold is not None and distance >= threshold
            if relative_failed:
                reasons.append("adsorbate O to intended metal is at least 5% above the fixed mean for this metal and adsorbate")
            if reasons:
                rejected.add((name, site))
            geometry_rows.append(dict(name=name, ads_site=site, selected_endpoint_state=state,
                endpoint_id=row.get("id", ""), intended_metal_distance_A=distance,
                nearest_support_distance_A=support_distance, O_O_distance_A=oo if np.isfinite(oo) else "",
                geometry_valid=not reasons, exclusion_reason="; ".join(reasons),
                adsorption_metal=metal, adsorbate=adsorbate, reference_mean_A=mean if mean is not None else "",
                relative_threshold_A=threshold if threshold is not None else "",
                above_reference_mean_percent=100 * (distance / mean - 1) if mean is not None else "",
                relative_distance_exceeded=bool(relative_failed),
                excluded_whole_structure=name in excluded_structures))
    rejected.update(k for k in eligible if k[0] in excluded_structures)
    eligible = [k for k in eligible if k not in rejected]
    target_values = np.asarray([[float(labels[k][target]) for target in TARGETS] for k in eligible])
    if not np.isfinite(target_values).all():
        raise ValueError("target-range split requires finite common-cohort target values")
    target_min = target_values.min(axis=0)
    target_span = target_values.max(axis=0) - target_min
    if np.any(target_span <= 0):
        raise ValueError("target-range split requires a nonzero range for every target")
    target_scaled = (target_values - target_min) / target_span
    for row in geometry_rows:
        row["retained_for_all_targets"] = (row["name"], row["ads_site"]) not in rejected
    write(OUT / "selected_endpoint_geometry_checks.csv", geometry_rows)
    write(OUT / "data_quality_exclusion_ledger.csv", [dict(name=r["name"], ads_site=r["ads_site"],
        included_after_geometry_checks=(r["name"], r["ads_site"]) in set(eligible),
        source_eligibility=r["included_common_cohort"], source_exclusion_reason=r["exclusion_reason_applied_to_all_targets"],
        additional_geometry_exclusion=(r["name"], r["ads_site"]) in rejected,
        excluded_whole_structure=r["name"] in excluded_structures,
        current_exclusion_reason=("whole structure excluded: selected adsorbate distance at least 5% above the fixed same-metal/same-adsorbate mean"
            if r["name"] in excluded_structures else r["exclusion_reason_applied_to_all_targets"])) for r in ledger])
    names = sorted({k[0] for k in eligible})
    source = {r["name"]: r for r in read(ROOT / "extracted/structures_by_target.csv")}
    feature_file = HERE / ("current_site_features.csv" if (HERE / "current_site_features.csv").exists() else "dipole_site_features.csv")
    raw_rows = read(feature_file)
    raw = {(r["name"], r["ads_site"]): r for r in raw_rows}
    features = json.loads((HERE / "current_descriptor_selection.json").read_text())["shared_descriptors"]
    x = np.asarray([[float(raw[k].get(f) or "nan") for f in features] for k in eligible])
    if not np.isfinite(x).all():
        raise ValueError("range-constrained split requires finite current descriptor values")
    positions = {n: [i for i, k in enumerate(eligible) if k[0] == n] for n in names}
    pair = {n: tuple(sorted((source[n]["metal1"], source[n]["metal2"]))) for n in names}
    # Environment labels refer to the six coordinating N/O/S atoms in the clean source.
    environment = {n: "".join({7: "N", 8: "O", 16: "S"}[z] for z in sorted(
        z for z in json.loads(source[n]["array.numbers"])[2:] if z in (7, 8, 16))) for n in names}
    adsorption_metal = [source[n][s] for n, s in eligible]
    partner_metal = [source[n]["metal2" if s == "metal1" else "metal1"] for n, s in eligible]
    metals = set(adsorption_metal)
    environments = set(environment.values())
    scale = np.where(x.std(axis=0) > 1e-12, x.std(axis=0), 1.0)
    normalized = (x - x.mean(axis=0)) / scale

    def range_checks(selected):
        held = np.asarray([n in selected for n, _ in eligible])
        checks = []
        selections = [("all_sites", j, np.ones(len(eligible), dtype=bool)) for j in range(len(features))]
        for role, labels, columns in (("adsorption", adsorption_metal, ("q_site", "spin_site_abs")),
                                     ("partner", partner_metal, ("q_partner", "spin_partner_abs"))):
            for metal in sorted(metals):
                for f in columns:
                    if f not in features:
                        continue
                    selections.append((f"{role}_metal_{metal}", features.index(f), np.asarray([m == metal for m in labels])))
        for scope, j, chosen in selections:
            train, val = x[chosen & ~held, j], x[chosen & held, j]
            if not len(train):
                return [], False
            okay = not len(val) or val.min() >= train.min() - TOLERANCE and val.max() <= train.max() + TOLERANCE
            checks.append(dict(scope=scope, descriptor_key=features[j], training_min=float(train.min()),
                training_max=float(train.max()), validation_min=float(val.min()) if len(val) else "",
                validation_max=float(val.max()) if len(val) else "", within_training_bounds=bool(okay)))
            if not okay:
                return checks, False
        return checks, True

    def feasible(selected):
        train = set(names) - selected
        return ({pair[n] for n in selected} <= {pair[n] for n in train}
                and {environment[n] for n in selected} <= {environment[n] for n in train}
                and range_checks(selected)[1])

    def coverage(selected):
        ix = [i for n in selected for i in positions[n]]
        return set(adsorption_metal[i] for i in ix), {environment[n] for n in selected}, {pair[n] for n in selected}

    def distance_score(name, selected):
        held = set(selected) | {name}
        distances = []
        for i in positions[name]:
            # Prefer a nearby training site with the same adsorption metal and ligand environment.
            train = [j for j, (n, _) in enumerate(eligible) if n not in held
                     and adsorption_metal[j] == adsorption_metal[i] and environment[n] == environment[name]]
            if not train:
                train = [j for j, (n, _) in enumerate(eligible) if n not in held]
            distances.append(float(np.min(np.linalg.norm(normalized[train] - normalized[i], axis=1))))
        return float(np.mean(distances))

    def target_spread_score(chosen):
        """Squared gap error from an even grid across each full eligible target range."""
        ix = [i for n in chosen for i in positions[n]]
        errors = []
        for j in range(len(TARGETS)):
            values = np.sort(target_scaled[ix, j])
            gaps = np.diff(np.concatenate(([0.0], values, [1.0])))
            errors.append(float(np.mean((gaps * (len(values) + 1) - 1.0) ** 2)))
        return float(np.mean(errors))

    selected, sequence = set(), []
    for step in range(MAX_VALIDATION):
        covered_metals, covered_env, covered_pairs = coverage(selected)
        env_counts = Counter(environment[n] for n in selected)
        scored = []
        for n in names:
            if n in selected or pair[n] in covered_pairs or not feasible(selected | {n}):
                continue
            new_metals = len({adsorption_metal[i] for i in positions[n]} - covered_metals)
            new_env = int(environment[n] not in covered_env)
            nearest = distance_score(n, selected)
            # Lexicographic objective: chemistry coverage, pair diversity, balanced environments, proximity.
            scored.append(((-new_metals, -new_env, env_counts[environment[n]], nearest, n), n, nearest))
        if not scored:
            break
        _, n, nearest = min(scored)
        selected.add(n)
        sequence.append(dict(order=step + 1, name=n, metal_pair="-".join(pair[n]), ligand_environment=environment[n],
                             mean_nearest_matching_training_distance_SD=nearest))

    # Improve target-range spacing with deterministic swaps that preserve split constraints.
    while True:
        current_score = target_spread_score(selected)
        best = None
        for removed in sorted(selected):
            for added in names:
                if added in selected:
                    continue
                candidate = (selected - {removed}) | {added}
                if len({pair[n] for n in candidate}) != len(candidate):
                    continue
                if not feasible(candidate):
                    continue
                candidate_metals, candidate_env, _ = coverage(candidate)
                if candidate_metals != metals or candidate_env != environments:
                    continue
                score = target_spread_score(candidate)
                proposal = (score, removed, added)
                if score < current_score - 1e-12 and (best is None or proposal < best):
                    best = proposal
        if best is None:
            break
        _, removed, added = best
        selected.remove(removed)
        selected.add(added)
        sequence = [row for row in sequence if row["name"] != removed]
        sequence.append(dict(order=0, name=added, metal_pair="-".join(pair[added]),
                             ligand_environment=environment[added],
                             mean_nearest_matching_training_distance_SD=distance_score(added, selected - {added})))
    covered_metals, covered_env, covered_pairs = coverage(selected)
    checks, okay = range_checks(selected)
    if covered_metals != metals or covered_env != environments or not okay or not feasible(selected):
        raise ValueError("cannot satisfy metal/environment coverage and interpolation bounds")
    sequence = [dict(order=i + 1, name=n, metal_pair="-".join(pair[n]),
                     ligand_environment=environment[n],
                     mean_nearest_matching_training_distance_SD=distance_score(n, selected - {n}))
                for i, n in enumerate(sorted(selected))]
    train = set(names) - selected
    write(OUT / "descriptor_range_checks.csv", checks)
    selection_rows = []
    for row in sequence:
        n = row["name"]
        selection_rows.append({**row, "eligible_sites": ";".join(eligible[i][1] for i in positions[n]),
            "training_structures_same_pair": sum(pair[t] == pair[n] for t in train),
            "training_structures_same_environment": sum(environment[t] == environment[n] for t in train),
            "mean_nearest_matching_training_distance_SD": distance_score(n, selected - {n})})
    write(OUT / "validation_structures.csv", selection_rows)
    target_spread_rows = []
    validation_ix = [i for n in sorted(selected) for i in positions[n]]
    for j, target in enumerate(TARGETS):
        ordered = sorted((float(target_values[i, j]), eligible[i][0], eligible[i][1]) for i in validation_ix)
        normalized = [(value - target_min[j]) / target_span[j] for value, _, _ in ordered]
        gaps = np.diff(np.concatenate(([0.0], normalized, [1.0])))
        target_spread_rows.append(dict(target=target, eligible_min=float(target_min[j]),
            eligible_max=float(target_min[j] + target_span[j]), validation_rows=len(ordered),
            validation_min=ordered[0][0], validation_max=ordered[-1][0],
            normalized_validation_values=";".join(f"{value:.6f}" for value in normalized),
            validation_observations=";".join(f"{name}:{site}:{value:.6f}" for value, name, site in ordered),
            maximum_normalized_gap=float(gaps.max()),
            normalized_gap_error=float(np.mean((gaps * (len(ordered) + 1) - 1.0) ** 2))))
    write(OUT / "validation_target_value_spread.csv", target_spread_rows)
    category_rows = []
    for category, values in (("metal", {n: set(pair[n]) for n in names}),
                             ("metal_pair", {n: {"-".join(pair[n])} for n in names}),
                             ("ligand_environment", {n: {environment[n]} for n in names})):
        for value in sorted(set.union(*values.values())):
            category_rows.append(dict(category=category, value=value,
                training_structures=sum(value in values[n] for n in train),
                validation_structures=sum(value in values[n] for n in selected)))
    write(OUT / "chemistry_coverage.csv", category_rows)
    valid_keys = set(eligible)
    membership = [dict(target=t, name=r["name"], ads_site=r["ads_site"],
        role=("validation" if r["name"] in selected else "training") if (r["name"], r["ads_site"]) in valid_keys
             else "excluded_by_data_quality") for t in ("G_OH", "G_O", "G_OOH") for r in raw_rows]
    write(HERE / "cohort_membership.csv", membership)
    paths = [Path(__file__), source_path, labels_path, geometry_path, ROOT / "extracted/structures_by_target.csv", feature_file,
             HERE / "current_descriptor_selection.json"]
    config = dict(policy="deterministic chemistry-coverage and target-range-spread holdout within training descriptor ranges",
        validation_max_structures=MAX_VALIDATION, eligible_structures=len(names), eligible_site_rows=len(eligible),
        training_structures=len(train), training_site_rows=sum(len(positions[n]) for n in train),
        validation_structures=sorted(selected), validation_site_rows=sum(len(positions[n]) for n in selected),
        validation_metals=sorted(covered_metals), validation_metal_pairs=[list(p) for p in sorted(covered_pairs)],
        validation_environments=sorted(covered_env), shared_target_cohort=True, prediction_error_pruning=False,
        target_energies_used_for_split=True,
        target_value_spread_objective="minimize mean squared normalized gap error across G_OH, G_O, and G_OOH",
        target_value_spread_score=target_spread_score(selected),
        coverage_source="optimized clean structures and retained eligible site labels",
        geometry_policy="preserve every source data-quality exclusion; verify selected OH/O/OOH endpoints before split",
        maximum_adsorbate_O_to_intended_metal_A=MAX_ADSORBATE_METAL_DISTANCE,
        maximum_adsorbate_O_to_support_A=MAX_ADSORBATE_METAL_DISTANCE, maximum_OOH_OO_A=MAX_OO_DISTANCE,
        newly_rejected_geometry_site_rows=len(rejected),
        bounds_features=features, bounds_tolerance=TOLERANCE,
        bounds_scope="current descriptors globally; metal charge/spin also conditioned on metal identity and site role",
        geometric_domain_note="coordinatewise descriptor ranges, not a guarantee of multivariate convex-hull inclusion",
        selection_order="new adsorption metals; new ligand environments; one structure per pair; environment balance; nearest matching training sites; deterministic target-value spread improving swaps; name tie break",
        outer_folds="three repeats of five grouped folds generated from the shared training names",
        validation_status="target-value-spread and chemistry-focused holdout; target labels informed membership, so validation metrics are not an unbiased population estimate or untouched external test",
        sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    config["available_metal_pairs"] = [list(p) for p in sorted(set(pair.values()))]
    if relative:
        config.update(relative_distance_exclusion_file="representative_split/relative_distance_exclusions.json",
            relative_distance_threshold=relative["relative_threshold"],
            relative_distance_reference_policy=relative["reference_policy"],
            excluded_whole_structures=sorted(excluded_structures),
            excluded_whole_structure_count=len(excluded_structures))
        config["sha256"][str(relative_path.relative_to(ROOT))] = hashlib.sha256(relative_path.read_bytes()).hexdigest()
    (OUT / "split_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    lines = ["# Current training and validation split", "",
        f"All three targets use the same **{len(train)} training structures / {config['training_site_rows']} sites** "
        f"and **{len(selected)} validation structures / {config['validation_site_rows']} sites**.", "",
        "Eligible sites require finite, raw-DFT-matched OH, O and OOH labels and pass the recorded endpoint/data-quality filters. "
        "The split uses optimized clean-structure chemistry, calculated descriptors, and the three target values. After "
        "chemistry coverage is selected, deterministic structure swaps improve even spacing of validation observations "
        "across the eligible minimum-to-maximum range for G_OH, G_O, and G_OOH. Model residuals and validation prediction scores "
        "do not determine membership. Both sites of a structure remain in one partition.", "",
        "All recorded invalid-geometry exclusions remain excluded from both training and validation. For every eligible site, "
        "the selected OH, O and OOH endpoints must have verified mappings and arrays, their nearest adsorbate O must be "
        "within 3.0 Angstrom of the intended metal and support, and selected OOH must have O-O separation at most "
        "2.0 Angstrom. If any endpoint fails, that site is excluded from all three targets. OOH checks use the orientation "
        "selected for the energy label. See the [selected endpoint geometry checks](selected_endpoint_geometry_checks.csv) "
        "and [data-quality exclusion ledger](data_quality_exclusion_ledger.csv).", "",
        *([f"The {len(excluded_structures)} structures listed in the "
            "[distance exclusion record](relative_distance_exclusions.json) are excluded in full: both sites and all targets. "
            "The criterion is selected metal-to-adsorbate-oxygen distance at least 5% above the fixed mean for the same "
            "metal and adsorbate (O, OH or OOH). Means and the approved list remain fixed when the split is rebuilt. "
            "[Reference means](relative_distance_reference_means.csv) and "
            "[flagged endpoints](relative_distance_flagged_endpoints.csv) give the numerical evidence.", ""] if relative else []),
        "## Selection rule", "",
        "A deterministic greedy selection covers adsorption metals and N/O/S ligand environments first, chooses one structure "
        "per metal pair, balances ligand environments, and prefers nearby training examples with the same adsorption metal "
        "and ligand environment. It then makes deterministic one-structure swaps that improve normalized target-range "
        "spacing while preserving chemistry coverage, unique validation pairs, and descriptor interpolation bounds. "
        "Structure names resolve exact ties. The validation budget is ten structures. Every validation pair and "
        "environment also occurs in training; singleton pairs remain in training. See [target-value spread diagnostics]"
        "(validation_target_value_spread.csv).", "",
        f"All validation values of the {len(features)} inputs lie within the training minima and maxima. Metal charges and spin "
        "magnitudes additionally lie within training ranges for that same metal and adsorption/partner role. These are "
        "coordinatewise range checks; multivariate convex-hull inclusion is not asserted.", "",
        f"Validation covers **{len(covered_metals)} / {len(metals)} metals**, **{len(covered_pairs)} / {len(set(pair.values()))} metal pairs**, "
        f"and **{len(covered_env)} / {len(environments)} ligand environments**. "
        "Metal pairs represented by only one eligible structure remain in training.", "",
        "## Validation structures", "", "| Structure | Metal pair | Ligand environment | Eligible sites | Training structures with same pair |",
        "|---|---|---|---|---:|"]
    for row in selection_rows:
        lines.append(f"| `{row['name']}` | {row['metal_pair']} | {row['ligand_environment']} | {row['eligible_sites']} | {row['training_structures_same_pair']} |")
    lines += ["", "This validation set measures interpolation among represented chemistries, with target ranges deliberately represented in the holdout. Target labels informed membership, so validation metrics are descriptive and are not an unbiased performance estimate. Its deliberate coverage and "
        "descriptor-range constraints do not estimate performance on unseen metal pairs or extrapolation, and it is not an untouched external test.", "",
        "- [Chemistry coverage](chemistry_coverage.csv)", "- [Descriptor range checks](descriptor_range_checks.csv)",
        "- [Validation structure details](validation_structures.csv)", "- [Selection settings and source hashes](split_config.json)",
        "- [All site memberships](../cohort_membership.csv)", "", "Reproduce the split:", "", "```powershell",
        "python article/KongiCats/calculations/models_20261011_dipole_ridge/select_representative_split.py", "```", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: config[k] for k in ("training_structures", "training_site_rows", "validation_structures", "validation_site_rows", "validation_metals", "validation_metal_pairs", "validation_environments")}), flush=True)


if __name__ == "__main__":
    main()
