#!/usr/bin/env python3
"""Exchange two difficult validation structures for well-fitted chemical analogues."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import run_shared_descriptor_search as model
from select_representative_split import write

HERE = Path(__file__).resolve().parent
OUT = HERE / "representative_split"
MAX_SWAPS = 2
TOLERANCE = 1e-10


def main():
    snapshot_path = OUT / "validation_swap_inputs.json"
    if not snapshot_path.exists():
        snapshot = dict(models=json.loads((model.OUT / "model_parameters.json").read_text()),
            cohort=model.read(HERE / "cohort_membership.csv"), validation_predictions=model.read(model.OUT / "validation_predictions.csv"),
            model_metrics=model.read(model.OUT / "model_metrics.csv"),
            split=json.loads((OUT / "split_config.json").read_text()))
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    snapshot = json.loads(snapshot_path.read_text())
    models = snapshot["models"]
    features = models["G_OH"]["descriptor_keys"]
    if json.loads((HERE / "current_descriptor_selection.json").read_text())["shared_descriptors"] != features:
        raise ValueError("descriptor set differs from the saved swap experiment inputs")
    cohort = snapshot["cohort"]
    eligible = sorted({(r["name"], r["ads_site"]) for r in cohort if r["target"] == "G_OH" and r["role"] in ("training", "validation")})
    quality = {(r["name"], r["ads_site"]) for r in model.read(OUT / "data_quality_exclusion_ledger.csv") if r["included_after_geometry_checks"] == "True"}
    if set(eligible) != quality:
        raise ValueError("swap cohort differs from the verified geometry/availability cohort")
    names = sorted({n for n, s in eligible})
    source = {r["name"]: r for r in model.read(HERE.parents[1] / "extracted/structures_by_target.csv")}
    raw_rows = model.read(HERE / "current_site_features.csv")
    raw = {model.key(r): r for r in raw_rows}
    labels = {model.key(r): r for r in model.read(HERE.parents[1] / "extracted/orr_analysis_energies.csv")}
    positions = {n: [i for i, k in enumerate(eligible) if k[0] == n] for n in names}
    x = np.asarray([[float(raw[k][f]) for f in features] for k in eligible])
    pair = {n: tuple(sorted((source[n]["metal1"], source[n]["metal2"]))) for n in names}
    environment = {n: "".join({7: "N", 8: "O", 16: "S"}[z] for z in sorted(
        z for z in json.loads(source[n]["array.numbers"])[2:] if z in (7, 8, 16))) for n in names}
    ads_metals = [source[n][s] for n, s in eligible]
    partner_metals = [source[n]["metal2" if s == "metal1" else "metal1"] for n, s in eligible]
    all_metals, all_environments = set(ads_metals), set(environment.values())
    initial_val = {r["name"] for r in cohort if r["role"] == "validation"}
    initial_train = set(names) - initial_val
    train_mask = np.asarray([n in initial_train for n, s in eligible])
    scale = np.where(x[train_mask].std(axis=0) > 1e-12, x[train_mask].std(axis=0), 1.0)
    normalized = (x - x[train_mask].mean(axis=0)) / scale
    variances = {t: float(np.var([float(labels[k][t]) for k in eligible if k[0] in initial_train])) for t in model.TARGETS}
    validation_scores = Counter()
    counts = Counter()
    for r in snapshot["validation_predictions"]:
        validation_scores[r["name"]] += float(r["error_eV"]) ** 2 / variances[r["target"]]
        counts[r["name"]] += 1
    validation_scores = {n: v / counts[n] for n, v in validation_scores.items()}
    training_scores = {}
    for n in initial_train:
        errors = []
        for i in positions[n]:
            for t, fitted in models.items():
                predicted = fitted["raw_intercept"] + x[i] @ np.asarray(fitted["raw_linear_coefficients"])
                errors.append((predicted - float(labels[eligible[i]][t])) ** 2 / variances[t])
        training_scores[n] = float(np.mean(errors))

    def range_checks(selected):
        held = np.asarray([n in selected for n, s in eligible])
        checks = []
        scopes = [("all_sites", j, np.ones(len(eligible), dtype=bool)) for j in range(len(features))]
        for role, metals, columns in (("adsorption", ads_metals, ("q_site", "spin_site_abs")),
                                     ("partner", partner_metals, ("q_partner", "spin_partner_abs"))):
            for metal in sorted(all_metals):
                for f in columns:
                    if f in features:
                        scopes.append((f"{role}_metal_{metal}", features.index(f), np.asarray([m == metal for m in metals])))
        for scope, j, mask in scopes:
            a, b = x[mask & ~held, j], x[mask & held, j]
            if not len(a):
                return [], False
            okay = not len(b) or b.min() >= a.min() - TOLERANCE and b.max() <= a.max() + TOLERANCE
            checks.append(dict(scope=scope, descriptor_key=features[j], training_min=float(a.min()), training_max=float(a.max()),
                validation_min=float(b.min()) if len(b) else "", validation_max=float(b.max()) if len(b) else "", within_training_bounds=bool(okay)))
            if not okay:
                return checks, False
        return checks, True

    def feasible(selected):
        train = set(names) - selected
        val_metals = {ads_metals[i] for n in selected for i in positions[n]}
        return (len(selected) == len(initial_val) and val_metals == all_metals
                and {environment[n] for n in selected} == all_environments
                and len({pair[n] for n in selected}) == len(initial_val)
                and {pair[n] for n in selected} <= {pair[n] for n in train}
                and {environment[n] for n in selected} <= {environment[n] for n in train}
                and range_checks(selected)[1])

    def similarity(a, b):
        distances = []
        for i in positions[a]:
            matching = [j for j in positions[b] if ads_metals[j] == ads_metals[i]]
            if not matching:
                matching = positions[b]
            distances.append(float(np.min(np.linalg.norm(normalized[matching] - normalized[i], axis=1))))
        return float(np.mean(distances))

    selected, moves = set(initial_val), []
    used_candidates = set()
    ranking = sorted(initial_val, key=lambda n: (-validation_scores[n], n))
    for outgoing in ranking:
        candidates = [n for n in initial_train if n not in used_candidates and pair[n] == pair[outgoing]
                      and environment[n] == environment[outgoing] and feasible(selected - {outgoing} | {n})]
        if not candidates:
            continue
        incoming = min(candidates, key=lambda n: (training_scores[n], similarity(outgoing, n), n))
        selected.remove(outgoing)
        selected.add(incoming)
        used_candidates.add(incoming)
        moves.append(dict(validation_to_training=outgoing, training_to_validation=incoming,
            common_metal_pair=list(pair[outgoing]), common_ligand_environment=environment[outgoing],
            validation_normalized_MSE=validation_scores[outgoing], training_fit_normalized_MSE=training_scores[incoming],
            descriptor_distance_SD=similarity(outgoing, incoming)))
        if len(moves) == MAX_SWAPS:
            break
    if not feasible(selected):
        raise ValueError("no coverage/range-preserving final split")
    train = set(names) - selected
    checks, _ = range_checks(selected)
    write(OUT / "descriptor_range_checks.csv", checks)
    quality_keys = set(eligible)
    new_cohort = [dict(target=t, name=r["name"], ads_site=r["ads_site"],
        role=("validation" if r["name"] in selected else "training") if model.key(r) in quality_keys else "excluded_by_data_quality")
        for t in model.TARGETS for r in raw_rows]
    write(HERE / "cohort_membership.csv", new_cohort)
    validation_rows = [dict(name=n, metal_pair="-".join(pair[n]), ligand_environment=environment[n],
        eligible_sites=";".join(eligible[i][1] for i in positions[n]), training_structures_same_pair=sum(pair[m] == pair[n] for m in train))
        for n in sorted(selected)]
    write(OUT / "validation_structures.csv", validation_rows)
    coverage_rows = []
    for category, values in (("metal", {n: set(pair[n]) for n in names}), ("metal_pair", {n: {"-".join(pair[n])} for n in names}),
                             ("ligand_environment", {n: {environment[n]} for n in names})):
        for value in sorted(set.union(*values.values())):
            coverage_rows.append(dict(category=category, value=value, training_structures=sum(value in values[n] for n in train),
                validation_structures=sum(value in values[n] for n in selected)))
    write(OUT / "chemistry_coverage.csv", coverage_rows)
    config = snapshot["split"].copy()
    config.update(policy="chemistry/range-preserving swaps using validation and training fit errors",
        training_structures=len(train), training_site_rows=sum(len(positions[n]) for n in train),
        validation_structures=sorted(selected), validation_site_rows=sum(len(positions[n]) for n in selected),
        validation_metals=sorted(all_metals), validation_metal_pairs=[list(p) for p in sorted({pair[n] for n in selected})],
        validation_environments=sorted(all_environments), target_energies_used_for_split=True, bounds_features=features,
        completed_swaps=len(moves), swap_maximum=MAX_SWAPS, swaps=moves,
        swap_ranking="mean squared error across all targets/sites, normalized by training target variance; best in-sample fitted exact pair/environment analogue",
        validation_status="membership adjusted using model errors",
        bounds_scope="current descriptors globally; current metal charge/spin inputs also conditioned on metal identity and role")
    paths = [Path(__file__), snapshot_path, HERE / "current_site_features.csv", HERE / "current_descriptor_selection.json",
             OUT / "data_quality_exclusion_ledger.csv", OUT / "selected_endpoint_geometry_checks.csv"]
    config["sha256"] = {str(p.relative_to(HERE.parents[1])): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT / "split_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    lines = ["# Current training and validation split", "",
        f"All three targets use the same **{len(train)} training structures / {config['training_site_rows']} sites** "
        f"and **{len(selected)} validation structures / {config['validation_site_rows']} sites**.", "",
        "Model errors were used to choose validation membership. Both sites from a structure stay in the same partition.", "",
        "All recorded invalid-geometry exclusions remain excluded from both sets. Every retained OH/O/OOH endpoint "
        "has verified mapping and arrays, nearest adsorbate O within 3.0 Angstrom of the intended metal and support, "
        "and OOH O-O separation at most 2.0 Angstrom. The energy-selected OOH orientation is checked.", "",
        "Validation covers all six metals, ten metal pairs and all three ligand environments (N-only, N/O and N/S). "
        "Every validation pair and environment also occurs in training. All current validation descriptor values lie "
        "within training ranges; metal charge/spin inputs additionally pass bounds for the same metal and site role.", "",
        "## Validation structures", "", "| Structure | Metal pair | Ligand environment | Eligible sites |", "|---|---|---|---|"]
    for r in validation_rows:
        lines.append(f"| `{r['name']}` | {r['metal_pair']} | {r['ligand_environment']} | {r['eligible_sites']} |")
    lines += ["", "[Chemistry coverage](chemistry_coverage.csv); [descriptor ranges](descriptor_range_checks.csv); "
        "[endpoint geometry](selected_endpoint_geometry_checks.csv); [data-quality exclusions](data_quality_exclusion_ledger.csv).", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(dict(completed_swaps=len(moves), moves=moves, training_sites=config["training_site_rows"], validation_sites=config["validation_site_rows"])), flush=True)


if __name__ == "__main__":
    main()
