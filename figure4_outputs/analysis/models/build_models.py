#!/usr/bin/env python3
"""Fit target-specific ridge models using only descriptors and their split.

Predictors come from the descriptor CSV columns that have finite training
values. Ridge strength is selected by grouped cross-validation on training
catalysts; the validation split is held out for final evaluation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATE_DIR = HERE.parent
DEFAULT_DATA = DATE_DIR / "descriptors" / "model_all_structures_training_data.csv"
DEFAULT_SPLIT_MAP = DATE_DIR / "descriptors" / "model_all_structures_split.csv"
TARGETS = ("G_OH", "G_O", "G_OOH")
SPLITS = ("training", "validation")
ROLE_COLUMN_BY_TARGET = {
    "G_O": "O_model_role",
    "G_OH": "OH_model_role",
    "G_OOH": "OOH_model_role",
}
ALL_ROLES = (*SPLITS, "prediction")
CV_REPEATS = 3
CV_FOLDS = 5
CV_SEED = 20261011
ALPHA_GRID = (0.0,) + tuple(10.0 ** (step / 2) for step in range(-8, 9))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def get_specs(data_rows: list[dict[str, str]]) -> dict[str, dict]:
    """Use descriptor columns with finite values in this target's training rows."""
    if not data_rows:
        raise ValueError("descriptor CSV has no data rows")
    reserved = {"target", "name", "ads_site", "split", "observed_eV"}
    feature_columns = [field for field in data_rows[0] if field not in reserved]
    if not feature_columns:
        raise ValueError("descriptor CSV has no predictor columns")

    specs = {}
    for target in TARGETS:
        training_rows = [row for row in data_rows
                         if row.get("target") == target and row.get("split") == "training"]
        if not training_rows:
            raise ValueError(f"{target} has no training rows for predictor selection")
        features = []
        for feature in feature_columns:
            observed = []
            for row in data_rows:
                raw = (row.get(feature) or "").strip()
                if not raw:
                    continue
                try:
                    value = float(raw)
                except ValueError as exc:
                    raise ValueError(f"non-numeric predictor {feature!r}: {raw!r}") from exc
                if not math.isfinite(value):
                    raise ValueError(f"non-finite predictor {feature!r}: {raw!r}")
                if row.get("target") == target and row.get("split") == "training":
                    observed.append(value)
            if observed:
                features.append(feature)
        if not features:
            raise ValueError(f"{target} has no predictors with finite training values")
        specs[target] = {"features": features}
    return specs


def validate_role_assignments(
    data_rows: list[dict[str, str]], split_rows: list[dict[str, str]]
) -> dict[str, dict[str, int]]:
    """Check labeled rows against the supplied target-specific role map."""
    if not split_rows:
        raise ValueError("role map has no structure rows")
    required = {"name", *ROLE_COLUMN_BY_TARGET.values()}
    missing = required - set(split_rows[0])
    if missing:
        raise ValueError(f"role map is missing columns: {', '.join(sorted(missing))}")

    roles_by_name = {}
    structure_counts = {target: Counter() for target in TARGETS}
    for row in split_rows:
        name = (row.get("name") or "").strip()
        if not name:
            raise ValueError("role map contains a blank structure name")
        if name in roles_by_name:
            raise ValueError(f"duplicate structure name in role map: {name}")
        roles_by_name[name] = {}
        for target, column in ROLE_COLUMN_BY_TARGET.items():
            role = (row.get(column) or "").strip()
            if role not in ALL_ROLES:
                raise ValueError(f"invalid {column} role for {name}: {role!r}")
            roles_by_name[name][target] = role
            structure_counts[target][role] += 1

    seen_rows = set()
    rows_by_target_and_split = {target: Counter() for target in TARGETS}
    for row in data_rows:
        target = (row.get("target") or "").strip()
        name = (row.get("name") or "").strip()
        site = (row.get("ads_site") or "").strip()
        split = (row.get("split") or "").strip()
        if target not in TARGETS or not name or site not in ("metal1", "metal2"):
            raise ValueError(f"invalid model data row: {row}")
        if split not in SPLITS:
            raise ValueError(f"model data must contain only training/validation rows: {row}")
        if name not in roles_by_name:
            raise ValueError(f"model data structure is missing from role map: {name}")
        expected = roles_by_name[name][target]
        if split != expected:
            raise ValueError(
                f"split mismatch for {target}, {name}: data says {split}, role map says {expected}"
            )
        key = (target, name, site)
        if key in seen_rows:
            raise ValueError(f"duplicate target/site model row: {key}")
        seen_rows.add(key)
        try:
            observed = float(row.get("observed_eV", ""))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"missing or non-numeric target value in model row: {key}") from exc
        if not math.isfinite(observed):
            raise ValueError(f"non-finite target value in model row: {key}")
        rows_by_target_and_split[target][split] += 1

    for target in TARGETS:
        for split in SPLITS:
            if not rows_by_target_and_split[target][split]:
                raise ValueError(f"{target} has no {split} rows")
    return {
        target: dict(counts) for target, counts in structure_counts.items()
    }


def numeric_matrix(rows: list[dict[str, str]], features: list[str]) -> np.ndarray:
    values = []
    for row in rows:
        values.append([
            float(row[feature]) if row.get(feature, "").strip() else np.nan
            for feature in features
        ])
    return np.asarray(values, dtype=float)


def fit_predict(train_rows: list[dict[str, str]], predict_rows: list[dict[str, str]],
                features: list[str], alpha: float) -> tuple[np.ndarray, dict]:
    train_x = numeric_matrix(train_rows, features)
    predict_x = numeric_matrix(predict_rows, features)
    train_y = np.asarray([float(row["observed_eV"]) for row in train_rows], dtype=float)
    finite = np.isfinite(train_x)
    medians = np.asarray([
        float(np.median(train_x[finite[:, j], j])) if finite[:, j].any() else 0.0
        for j in range(train_x.shape[1])
    ])
    train_x = np.where(finite, train_x, medians)
    predict_x = np.where(np.isfinite(predict_x), predict_x, medians)
    means = train_x.mean(axis=0)
    scales = train_x.std(axis=0)
    scales[scales <= 1e-12] = 1.0
    train_z = (train_x - means) / scales
    predict_z = (predict_x - means) / scales
    intercept = float(train_y.mean())
    centered_y = train_y - intercept
    if alpha == 0:
        coefficients = np.linalg.lstsq(train_z, centered_y, rcond=None)[0]
    else:
        coefficients = np.linalg.solve(
            train_z.T @ train_z + alpha * np.eye(train_z.shape[1]),
            train_z.T @ centered_y,
        )
    predictions = intercept + predict_z @ coefficients
    model = {
        "intercept": intercept,
        "coefficients": coefficients,
        "medians": medians,
        "means": means,
        "scales": scales,
    }
    return predictions, model


def score(observed, predicted) -> dict[str, float]:
    observed = np.asarray(observed, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    errors = predicted - observed
    denominator = float(np.sum((observed - observed.mean()) ** 2))
    r2 = float(1.0 - np.sum(errors ** 2) / denominator) if denominator else float("nan")
    return {
        "R2": r2,
        "RMSE_eV": float(np.sqrt(np.mean(errors ** 2))),
        "MAE_eV": float(np.mean(np.abs(errors))),
    }


def grouped_folds(names, seed: int, count: int = CV_FOLDS) -> list[set[str]]:
    shuffled = sorted(set(names))
    if len(shuffled) < count:
        raise ValueError(f"need at least {count} training catalysts for grouped CV, have {len(shuffled)}")
    np.random.default_rng(seed).shuffle(shuffled)
    folds = [set() for _ in range(count)]
    for index, name in enumerate(shuffled):
        folds[index % count].add(name)
    return folds


def cross_validate(target: str, train_rows: list[dict[str, str]],
                   features: list[str], alpha: float) -> tuple[dict, list[dict]]:
    """Evaluate one ridge alpha with repeated folds grouped by catalyst."""
    train_names = {row["name"] for row in train_rows}
    repeat_scores = []
    pooled_observed = []
    pooled_predicted = []
    prediction_rows = []
    for repeat in range(CV_REPEATS):
        folds = grouped_folds(train_names, CV_SEED + repeat)
        repeat_observed = []
        repeat_predicted = []
        for fold_number, held_names in enumerate(folds, start=1):
            fold_train = [row for row in train_rows if row["name"] not in held_names]
            fold_held = [row for row in train_rows if row["name"] in held_names]
            if not fold_train or not fold_held:
                raise ValueError(f"empty grouped CV fold for {target}, repeat {repeat + 1}, fold {fold_number}")
            fold_pred, _ = fit_predict(fold_train, fold_held, features, alpha)
            fold_truth = [float(row["observed_eV"]) for row in fold_held]
            repeat_observed.extend(fold_truth)
            repeat_predicted.extend(float(value) for value in fold_pred)
            pooled_observed.extend(fold_truth)
            pooled_predicted.extend(float(value) for value in fold_pred)
            for row, prediction in zip(fold_held, fold_pred):
                observed = float(row["observed_eV"])
                prediction = float(prediction)
                prediction_rows.append({
                    "target": target,
                    "alpha": alpha,
                    "repeat": repeat + 1,
                    "fold": fold_number,
                    "name": row["name"],
                    "ads_site": row["ads_site"],
                    "observed_eV": observed,
                    "predicted_eV": prediction,
                    "error_eV": prediction - observed,
                })
        repeat_scores.append(score(repeat_observed, repeat_predicted))
    pooled_scores = score(pooled_observed, pooled_predicted)
    return {
        "mean_repeat_R2cv": float(np.mean([item["R2"] for item in repeat_scores])),
        "pooled_repeated_OOF_R2": pooled_scores["R2"],
        "mean_repeat_RMSEcv_eV": float(np.mean([item["RMSE_eV"] for item in repeat_scores])),
        "pooled_repeated_OOF_RMSE_eV": pooled_scores["RMSE_eV"],
    }, prediction_rows


def select_alpha(target: str, train_rows: list[dict[str, str]],
                 features: list[str]) -> tuple[float, list[dict], dict, list[dict]]:
    """Select ridge strength from training-only grouped CV."""
    scores = []
    for alpha in ALPHA_GRID:
        cv_metrics, _ = cross_validate(target, train_rows, features, alpha)
        scores.append({
            "target": target,
            "alpha": alpha,
            **cv_metrics,
            "selected": False,
        })
    selected = min(scores, key=lambda row: (row["mean_repeat_RMSEcv_eV"], row["alpha"]))
    selected["selected"] = True
    alpha = float(selected["alpha"])
    cv_metrics, predictions = cross_validate(target, train_rows, features, alpha)
    return alpha, scores, cv_metrics, predictions


def make_prediction_rows(target: str, rows: list[dict[str, str]], predictions: np.ndarray) -> list[dict]:
    results = []
    for row, prediction in zip(rows, predictions):
        observed = float(row["observed_eV"])
        prediction = float(prediction)
        results.append({
            "target": target,
            "name": row["name"],
            "ads_site": row["ads_site"],
            "split": row["split"],
            "observed_eV": observed,
            "predicted_eV": prediction,
            "error_eV": prediction - observed,
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA,
                        help=f"combined split data CSV (default: {DEFAULT_DATA})")
    parser.add_argument("--split-map", type=Path, default=DEFAULT_SPLIT_MAP,
                        help=f"catalyst split map (default: {DEFAULT_SPLIT_MAP})")
    parser.add_argument("--output-dir", type=Path, default=HERE,
                        help=f"model artifact directory (default: {HERE})")
    args = parser.parse_args()

    data_rows = read_csv(args.data)
    split_rows = read_csv(args.split_map)
    structures_by_target_role = validate_role_assignments(data_rows, split_rows)
    specs = get_specs(data_rows)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    parameter_rows = []
    metric_rows = []
    alpha_selection_rows = []
    validation_predictions = []
    all_predictions = []
    cv_predictions = []
    bundle = {
        "model_type": "standardized_ridge",
        "feature_selection": "descriptor columns with finite values in target training rows",
        "alpha_selection": "minimum mean repeated grouped-CV RMSE on target training rows",
        "targets": {},
    }

    for target in TARGETS:
        target_rows = [row for row in data_rows if row["target"] == target]
        train_rows = [row for row in target_rows if row["split"] == "training"]
        val_rows = [row for row in target_rows if row["split"] == "validation"]
        if not train_rows or not val_rows:
            raise ValueError(f"{target} requires both training and validation rows")
        features = specs[target]["features"]
        alpha, alpha_rows, cv_metrics, target_cv_predictions = select_alpha(
            target, train_rows, features
        )
        alpha_selection_rows.extend(alpha_rows)
        cv_predictions.extend(target_cv_predictions)

        val_pred, model = fit_predict(train_rows, val_rows, features, alpha)
        train_pred, _ = fit_predict(train_rows, train_rows, features, alpha)
        validation_predictions.extend(make_prediction_rows(target, val_rows, val_pred))
        all_predictions.extend(make_prediction_rows(target, train_rows, train_pred))
        all_predictions.extend(make_prediction_rows(target, val_rows, val_pred))

        parameter_rows.append({
            "target": target, "term": "intercept",
            "standardized_coefficient": model["intercept"],
            "training_median": "", "training_mean": "", "training_sd": "",
            "ridge_alpha": alpha,
        })
        feature_parameters = []
        for index, feature in enumerate(features):
            parameter_rows.append({
                "target": target,
                "term": feature,
                "standardized_coefficient": float(model["coefficients"][index]),
                "training_median": float(model["medians"][index]),
                "training_mean": float(model["means"][index]),
                "training_sd": float(model["scales"][index]),
                "ridge_alpha": alpha,
            })
            feature_parameters.append({
                "name": feature,
                "standardized_coefficient": float(model["coefficients"][index]),
                "training_median": float(model["medians"][index]),
                "training_mean": float(model["means"][index]),
                "training_sd": float(model["scales"][index]),
            })

        train_y = [float(row["observed_eV"]) for row in train_rows]
        val_y = [float(row["observed_eV"]) for row in val_rows]
        train_scores = score(train_y, train_pred)
        val_scores = score(val_y, val_pred)

        target_train_names = {row["name"] for row in train_rows}
        metric_rows.append({
            "target": target,
            "training_sites": len(train_rows),
            "training_catalysts": len(target_train_names),
            "validation_sites": len(val_rows),
            "validation_catalysts": len({row["name"] for row in val_rows}),
            "selected_predictors": len(features),
            "ridge_alpha": alpha,
            "training_R2": train_scores["R2"],
            "training_RMSE_eV": train_scores["RMSE_eV"],
            "training_MAE_eV": train_scores["MAE_eV"],
            "mean_repeat_R2cv": cv_metrics["mean_repeat_R2cv"],
            "pooled_repeated_OOF_R2": cv_metrics["pooled_repeated_OOF_R2"],
            "mean_repeat_RMSEcv_eV": cv_metrics["mean_repeat_RMSEcv_eV"],
            "pooled_repeated_OOF_RMSE_eV": cv_metrics["pooled_repeated_OOF_RMSE_eV"],
            "validation_R2": val_scores["R2"],
            "validation_RMSE_eV": val_scores["RMSE_eV"],
            "validation_MAE_eV": val_scores["MAE_eV"],
            "features": ";".join(features),
        })
        bundle["targets"][target] = {
            "alpha": alpha,
            "intercept_eV": model["intercept"],
            "features": feature_parameters,
        }

    model_rows_fields = [
        "target", "term", "standardized_coefficient", "training_median",
        "training_mean", "training_sd", "ridge_alpha",
    ]
    metric_fields = list(metric_rows[0])
    prediction_fields = [
        "target", "name", "ads_site", "split", "observed_eV",
        "predicted_eV", "error_eV",
    ]
    alpha_fields = [
        "target", "alpha", "mean_repeat_R2cv", "pooled_repeated_OOF_R2",
        "mean_repeat_RMSEcv_eV", "pooled_repeated_OOF_RMSE_eV", "selected",
    ]
    write_csv(output_dir / "final_model_parameters.csv", model_rows_fields, parameter_rows)
    write_csv(output_dir / "model_metrics.csv", metric_fields, metric_rows)
    write_csv(output_dir / "alpha_selection.csv", alpha_fields, alpha_selection_rows)
    write_csv(output_dir / "predictions.csv", prediction_fields, all_predictions)
    write_csv(output_dir / "validation_predictions.csv", prediction_fields, validation_predictions)
    write_csv(output_dir / "cv_predictions.csv", [
        "target", "alpha", "repeat", "fold", "name", "ads_site", "observed_eV",
        "predicted_eV", "error_eV",
    ], cv_predictions)

    bundle["description"] = (
        "Per-target standardized ridge regressions. Missing predictors are imputed with the "
        "median of finite values in that model's training rows. Standardization and coefficients "
        "are fitted on training rows only."
    )
    (output_dir / "model_bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    manifest = {
        "data_csv": Path(os.path.relpath(args.data.resolve(), start=output_dir)).as_posix(),
        "split_map_csv": Path(os.path.relpath(args.split_map.resolve(), start=output_dir)).as_posix(),
        "feature_selection": "descriptor columns with finite values in target training rows",
        "alpha_selection": {
            "method": "minimum mean repeated grouped-CV RMSE on target training rows",
            "grid": list(ALPHA_GRID),
        },
        "targets": {
            target: {"features": specs[target]["features"],
                     "ridge_alpha": next(row["alpha"] for row in alpha_selection_rows
                                          if row["target"] == target and row["selected"])}
            for target in TARGETS
        },
        "role_columns": ROLE_COLUMN_BY_TARGET,
        "cv": {"grouped_by": "catalyst name", "folds": CV_FOLDS, "repeats": CV_REPEATS,
               "seed_start": CV_SEED},
    }
    (output_dir / "run_config.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps({
        "output_dir": str(output_dir),
        "structures_by_target_role": structures_by_target_role,
        "metrics": metric_rows,
        "artifacts": [
            "final_model_parameters.csv", "model_metrics.csv", "alpha_selection.csv", "predictions.csv",
            "validation_predictions.csv", "cv_predictions.csv", "model_bundle.json", "run_config.json",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
