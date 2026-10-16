#!/usr/bin/env python3
"""Sequential training-only addition of up to two distinct descriptor families."""
import hashlib
import json
from pathlib import Path

import numpy as np

import run_shared_descriptor_search as model
from analyze_descriptor_correlations import extended_catalog
from current_site_descriptors import compute

HERE = Path(__file__).resolve().parent
OUT = HERE / "forward_descriptor_selection"
BASE = ["q_site", "q_partner", "spin_site_abs", "spin_partner_abs",
        "site_heteroatom_spin_abs_mean_muB", "partner_heteroatom_spin_abs_mean_muB", "metal_metal_distance_A"]
SIMILARITY = 0.95


def family(feature):
    if feature in ("q_site", "q_partner"):
        return "metal_charge"
    if feature in ("spin_site_abs", "spin_partner_abs"):
        return "metal_spin_magnitude"
    if "heteroatom_spin_abs" in feature:
        return "ligand_spin_magnitude"
    if "dipole" in feature:
        return "local_ligand_dipole"
    if "ligand_charge" in feature or "heteroatom_charge" in feature:
        return "ligand_charge_distribution"
    if feature.startswith(("site_angle", "partner_angle")):
        return "ligand_angles"
    if feature.startswith("shared_bridge_angle"):
        return "bridge_angles"
    if feature.startswith("support_"):
        return "support_spin"
    if feature.startswith("second_shell_"):
        return "second_shell_density"
    return feature


def main():
    OUT.mkdir(exist_ok=True)
    _, _, data, partitions, _, _ = model.load_data()
    definitions = extended_catalog()
    pool = list(definitions)
    sources = {r["name"]: r for r in model.read(HERE.parents[1] / "extracted" / "structures_by_target.csv")}
    raw = {model.key(r): compute(sources[r["name"]], 0 if r["ads_site"] == "metal1" else 1)
           for r in model.read(HERE / "dipole_site_features.csv")}
    for target, d in data.items():
        d["x"] = np.asarray([[raw[k][f] for f in pool] for k in d["keys"]])
    common = sorted(set.intersection(*(set(d["keys"]) for d in data.values())))
    indices = {t: {k: i for i, k in enumerate(d["keys"])} for t, d in data.items()}
    correlations = model.read(HERE / "descriptor_correlation_analysis" / "descriptor_target_correlations.csv")
    scores = {}
    for row in correlations:
        if row["scope"] == "common_training" and row["target"] in model.TARGETS and row["pearson_r"]:
            scores.setdefault(row["descriptor_key"], []).append(abs(float(row["pearson_r"])))
    ranking = sorted((f for f in pool if f not in BASE and len(scores.get(f, [])) == 3),
                     key=lambda f: (-np.mean(scores[f]), f))
    records, predictions = [], []
    candidate_audit = []
    current = BASE.copy()
    accepted = []

    def evaluate(features):
        columns = [pool.index(f) for f in features]
        rows = []
        for repeat in (1, 2, 3):
            for fold in range(1, 6):
                masks = {t: np.asarray([partitions[repeat, name] == fold for name in d["names"]]) for t, d in data.items()}
                training = {t: dict(x=d["x"][~masks[t]], y=d["y"][~masks[t]],
                    names=[name for name, held in zip(d["names"], masks[t]) if not held]) for t, d in data.items()}
                choice = model.choose_targets(training, {"trial": columns}, [model.SEED + repeat * 10007 + fold * 101])[0]
                for target, d in data.items():
                    held = masks[target]
                    setting = choice["selected"][target]["setting"]
                    pp, _ = model.fit_batch(d["x"][~held][:, columns], d["x"][held][:, columns], d["y"][~held])
                    rows.extend(model.prediction_rows(target, "forward_selection_trial", [k for k, flag in zip(d["keys"], held) if flag],
                        d["y"][held], pp[setting], repeat=repeat, fold=fold))
        metrics = {}
        for target in model.TARGETS:
            rs = []
            for repeat in (1, 2, 3):
                subset = [r for r in rows if r["target"] == target and r["repeat"] == repeat]
                rs.append(model.metric([r["observed_eV"] for r in subset], [r["predicted_eV"] for r in subset]))
            metrics[target] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
        return metrics, rows

    baseline, base_predictions = evaluate(current)
    records.append(dict(stage=0, candidate="initial_seven", decision="starting_set", descriptor_count=7,
        **{f"{t}_CV_R2": baseline[t]["R2"] for t in model.TARGETS},
        **{f"{t}_CV_RMSE_eV": baseline[t]["RMSE_eV"] for t in model.TARGETS}))
    predictions.extend(dict(stage=0, candidate="initial_seven", **r) for r in base_predictions)
    while len(accepted) < 2:
        kept = False
        for candidate in ranking:
            if candidate in current:
                continue
            reason = ""
            related = ""
            if family(candidate) in {family(f) for f in current}:
                reason = "family_already_represented"
            x = np.asarray([raw[k][candidate] for k in common])
            maximum_similarity = 0.0
            for existing in current:
                y = np.asarray([raw[k][existing] for k in common])
                valid = np.isfinite(x) & np.isfinite(y)
                if valid.sum() >= 3 and np.std(x[valid]) > 1e-12 and np.std(y[valid]) > 1e-12:
                    similarity = abs(float(np.corrcoef(x[valid], y[valid])[0, 1]))
                    if similarity > maximum_similarity:
                        maximum_similarity, related = similarity, existing
            if maximum_similarity >= SIMILARITY:
                reason = "near_duplicate_of_existing_input"
            candidate_audit.append(dict(stage=len(accepted) + 1, candidate=candidate, readable_name=definitions[candidate]["name"],
                family=family(candidate), mean_abs_target_r=float(np.mean(scores[candidate])),
                maximum_abs_input_correlation=maximum_similarity, most_similar_input=related, eligibility=reason or "eligible"))
            if reason:
                continue
            trial, rows = evaluate(current + [candidate])
            improvements = {t: trial[t]["R2"] - baseline[t]["R2"] for t in model.TARGETS}
            passed = all(delta > 1e-6 for delta in improvements.values())
            decision = "keep" if passed else "reject_not_improved_for_every_target"
            print(f"Addition {len(accepted) + 1}: {definitions[candidate]['name']} -> {decision}; " +
                  "; ".join(f"{t} CV R2 {trial[t]['R2']:.4f} ({improvements[t]:+.4f})" for t in model.TARGETS), flush=True)
            records.append(dict(stage=len(accepted) + 1, candidate=candidate, readable_name=definitions[candidate]["name"],
                decision=decision, descriptor_count=len(current) + 1,
                **{f"{t}_CV_R2": trial[t]["R2"] for t in model.TARGETS},
                **{f"{t}_CV_RMSE_eV": trial[t]["RMSE_eV"] for t in model.TARGETS},
                **{f"{t}_CV_R2_change": improvements[t] for t in model.TARGETS}))
            predictions.extend(dict(stage=len(accepted) + 1, candidate=candidate, **r) for r in rows)
            if passed:
                accepted.append(candidate)
                current.append(candidate)
                baseline = trial
                kept = True
                break
        if not kept:
            break
    previous_out = model.OUT
    model.OUT = OUT
    for name, rows in (("trial_results.csv", records), ("candidate_eligibility.csv", candidate_audit), ("trial_cv_predictions.csv", predictions)):
        model.write(name, rows)
    model.OUT = previous_out
    selection = dict(base_descriptors=BASE, added_descriptors=accepted, shared_descriptors=current,
        model_family="ridge", ranking="decreasing mean absolute Pearson r across three targets on common training sites",
        acceptance="increase mean repeated nested-alpha grouped CV R2 by more than 1e-6 for every target",
        evaluation="three repeats of five structure-grouped folds; ridge alpha chosen in four inner grouped folds",
        similarity_absolute_Pearson_threshold=SIMILARITY, family_rule="one family of added ligand-charge, dipole, angle, support-spin, or radial summaries; base metal/site pairs retained",
        validation_used_for_selection=False, selection_scores_are_conditional=True,
        selected_CV_metrics=baseline,
        source_correlations_sha256=hashlib.sha256((HERE / "descriptor_correlation_analysis" / "descriptor_target_correlations.csv").read_bytes()).hexdigest())
    (HERE / "current_descriptor_selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    lines = ["# Sequential descriptor-addition trials", "",
        "Candidates are ranked by their mean absolute Pearson correlation with OH, O and OOH on the common training cohort. "
        "Each trial adds one descriptor to all three linear ridge models. A descriptor is kept only if the mean repeated "
        "grouped CV R2 increases for every target. Alpha is selected within each outer training fold. Validation energies "
        "do not determine candidate ranking, trial acceptance or stopping.", "",
        "A candidate is skipped if its summary family is represented or its absolute correlation with an existing input "
        "is at least 0.95. Existing adsorption/partner metal pairs are retained. Signed metal spin product is a pair "
        "alignment quantity distinct from the individual spin magnitudes.", "",
        "These trial scores are used for descriptor selection and are selection conditional; they are not an independent "
        "estimate of the entire selection procedure.", "",
        "| Stage | Candidate | Decision | OH CV R2 | O CV R2 | OOH CV R2 |", "|---:|---|---|---:|---:|---:|"]
    for row in records:
        lines.append(f"| {row['stage']} | {row.get('readable_name', 'Starting seven descriptors')} | {row['decision']} | " +
                     " | ".join(f"{row[t+'_CV_R2']:.4f}" for t in model.TARGETS) + " |")
    lines += ["", f"Accepted additions: {len(accepted)}.", "",
        "- [Candidate-family and similarity checks](candidate_eligibility.csv)",
        "- [Trial scores and per-target changes](trial_results.csv)",
        "- [Per-site held-out predictions for every evaluated trial](trial_cv_predictions.csv)", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("Selected added descriptors: " + json.dumps(accepted), flush=True)


if __name__ == "__main__":
    main()
