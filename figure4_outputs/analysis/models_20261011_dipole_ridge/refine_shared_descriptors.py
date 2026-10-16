#!/usr/bin/env python3
"""Shared physical-descriptor replacements, removals and complementary additions."""
import json
from pathlib import Path

import numpy as np

import run_shared_descriptor_search as model
from analyze_descriptor_correlations import extended_catalog
from current_site_descriptors import compute
from try_two_descriptors import family

HERE = Path(__file__).resolve().parent
OUT = HERE / "descriptor_refinement"


def write(name, rows):
    previous = model.OUT
    model.OUT = OUT
    model.write(name, rows)
    model.OUT = previous


def main():
    OUT.mkdir(exist_ok=True)
    sources = {r["name"]: r for r in model.read(HERE.parents[1] / "extracted/structures_by_target.csv")}
    defs = extended_catalog()
    values = [dict(name=r["name"], ads_site=r["ads_site"], **compute(sources[r["name"]], 0 if r["ads_site"] == "metal1" else 1))
              for r in model.read(HERE / "dipole_site_features.csv")]
    previous = model.OUT
    model.OUT = HERE
    model.write("current_site_features.csv", values)
    model.OUT = previous
    pool, _, data, partitions, _, cohort = model.load_data()
    current = json.loads((HERE / "current_descriptor_selection.json").read_text())["shared_descriptors"]
    (OUT / "starting_descriptors.json").write_text(json.dumps(current, indent=2) + "\n")
    (OUT / "starting_cohort.json").write_text(json.dumps(cohort, indent=2) + "\n")
    cache, predictions, trials = {}, [], []

    def evaluate(features):
        identity = tuple(features)
        if identity in cache:
            return cache[identity]
        columns = [pool.index(f) for f in features]
        rows = []
        for repeat in (1, 2, 3):
            for fold in range(1, 6):
                masks = {t: np.asarray([partitions[repeat, n] == fold for n in d["names"]]) for t, d in data.items()}
                training = {t: dict(x=d["x"][~masks[t]], y=d["y"][~masks[t]],
                    names=[n for n, flag in zip(d["names"], masks[t]) if not flag]) for t, d in data.items()}
                choice = model.choose_targets(training, {"trial": columns}, [model.SEED + repeat * 10007 + fold * 101])[0]
                for t, d in data.items():
                    held = masks[t]
                    pp, _ = model.fit_batch(d["x"][~held][:, columns], d["x"][held][:, columns], d["y"][~held])
                    rows += model.prediction_rows(t, "descriptor_refinement", [k for k, flag in zip(d["keys"], held) if flag],
                        d["y"][held], pp[choice["selected"][t]["setting"]], repeat=repeat, fold=fold)
        scores = {}
        for t in model.TARGETS:
            repeats = []
            for repeat in (1, 2, 3):
                rs = [r for r in rows if r["target"] == t and r["repeat"] == repeat]
                repeats.append(model.metric([r["observed_eV"] for r in rs], [r["predicted_eV"] for r in rs]))
            scores[t] = {k: float(np.mean([r[k] for r in repeats])) for k in repeats[0]}
        cache[identity] = scores, rows
        return scores, rows

    def candidates(features):
        for removed in features:
            if removed != "metal_metal_distance_A":
                yield "remove", removed, "", [f for f in features if f != removed]
        for removed in features:
            if "dipole" in removed:
                for prefix in ("site", "partner"):
                    for stat in ("mean", "min", "max", "std"):
                        added = f"{prefix}_heteroatom_dipole_contribution_{stat}_eA"
                        if added != removed:
                            yield "replace", removed, added, [added if f == removed else f for f in features]
            elif family(removed) == "ligand_charge_distribution":
                for prefix in ("site", "partner"):
                    for label in ("terminal", "shared"):
                        added = f"{prefix}_{label}_ligand_charge_mean_e"
                        yield "replace", removed, added, [added if f == removed else f for f in features]
        extras = ["spin_product_muB2"] + [f"{p}_angle_{s}_deg" for p in ("site", "partner") for s in ("mean", "std", "min", "max")]
        extras += ["shared_bridge_angle_mean_deg", "shared_bridge_angle_std_deg"]
        for added in extras:
            if added not in features and family(added) not in {family(f) for f in features}:
                yield "add", "", added, features + [added]

    baseline, rows = evaluate(current)
    trials.append(dict(round=0, operation="starting_set", removed="", added="", decision="starting_set", descriptor_count=len(current),
        **{t + "_CV_R2": baseline[t]["R2"] for t in model.TARGETS}))
    predictions += [dict(trial=0, **r) for r in rows]
    accepted = []
    for step in range(1, 7):
        passing = []
        for operation, removed, added, features in candidates(current):
            if len(features) != len(set(features)):
                continue
            if added:
                j = pool.index(added)
                train_values = data["G_OH"]["x"][:, j]
                held_values = data["G_OH"]["validation_x"][:, j]
                a, b = train_values[np.isfinite(train_values)], held_values[np.isfinite(held_values)]
                if not len(a) or len(b) and (b.min() < a.min() - 1e-10 or b.max() > a.max() + 1e-10):
                    continue
                x = data["G_OH"]["x"][:, pool.index(added)]
                similar = False
                for f in features:
                    if f == added:
                        continue
                    y = data["G_OH"]["x"][:, pool.index(f)]
                    valid = np.isfinite(x) & np.isfinite(y)
                    if valid.sum() > 2 and np.std(x[valid]) > 1e-12 and np.std(y[valid]) > 1e-12 and abs(np.corrcoef(x[valid], y[valid])[0, 1]) >= .95:
                        similar = True
                if similar:
                    continue
            scores, rows = evaluate(features)
            delta = {t: scores[t]["R2"] - baseline[t]["R2"] for t in model.TARGETS}
            passed = all(v > 1e-6 for v in delta.values())
            trial = len(trials)
            trials.append(dict(round=step, operation=operation, removed=removed, added=added,
                decision="eligible_improvement" if passed else "reject", descriptor_count=len(features),
                **{t + "_CV_R2": scores[t]["R2"] for t in model.TARGETS},
                **{t + "_CV_R2_change": delta[t] for t in model.TARGETS}))
            predictions += [dict(trial=trial, **r) for r in rows]
            if passed:
                passing.append((float(np.mean(list(delta.values()))), trial, features, scores))
        if not passing:
            break
        _, trial, current, baseline = max(passing, key=lambda v: (v[0], -len(v[2]), -v[1]))
        trials[trial]["decision"] = "keep"
        accepted.append(trials[trial])
        print("Accepted " + json.dumps(trials[trial]), flush=True)
    write("trial_results.csv", trials)
    write("trial_cv_predictions.csv", predictions)
    selection = dict(shared_descriptors=current, model_family="ridge", acceptance="CV R2 improves for every target; best mean gain per round",
        validation_used_for_selection=False, descriptor_selection_cohort={t: dict(structures=len(set(d["names"])), sites=len(d["keys"])) for t, d in data.items()},
        descriptor_selection_trial_CV_metrics=baseline, current_fit_metrics_path="shared_descriptor_search/model_metrics.csv",
        accepted_operations=accepted, selected_input_definitions=[defs[f] for f in current], similarity_threshold=.95,
        selection_scores_are_conditional=True)
    (HERE / "current_descriptor_selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    lines = ["# Shared descriptor refinement", "", "Each trial uses the same descriptors for all three targets. "
        "Three repeated five-fold structure-grouped evaluations choose ridge strength in four inner folds. "
        "Only changes improving every target's mean CV R2 are retained. Selection uses training CV, with validation labels excluded.", "",
        "| Round | Operation | Removed | Added | Decision | OH CV R2 | O CV R2 | OOH CV R2 |",
        "|---:|---|---|---|---|---:|---:|---:|"]
    for r in trials:
        lines.append(f"| {r['round']} | {r['operation']} | {defs.get(r['removed'], {}).get('name', '')} | {defs.get(r['added'], {}).get('name', '')} | {r['decision']} | " +
                     " | ".join(f"{r[t+'_CV_R2']:.4f}" for t in model.TARGETS) + " |")
    lines += ["", "The scores are conditional on this descriptor search. Current production metrics are in "
        "[model_metrics.csv](../shared_descriptor_search/model_metrics.csv).", "", "[Trial predictions](trial_cv_predictions.csv)", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("Final descriptors: " + json.dumps(current), flush=True)


if __name__ == "__main__":
    main()
