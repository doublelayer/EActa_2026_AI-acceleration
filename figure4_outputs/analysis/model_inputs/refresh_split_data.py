#!/usr/bin/env python3
"""Refit the bundled fixed ridge models on the current representative split."""
import csv
import json
import shutil
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE.parent
KONGICATS = NOTEBOOK.parent
MODEL_DIR = KONGICATS / "calculations" / "models_20261011_dipole_ridge"
SPLIT_DIR = MODEL_DIR / "representative_split"
TARGETS = ("G_OH", "G_O", "G_OOH")


def read(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    rows = list(rows)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def key(row):
    return row["name"], row["ads_site"]


def fit(train_x, predict_x, train_y, alpha):
    train_x = np.asarray(train_x, dtype=float).copy()
    predict_x = np.asarray(predict_x, dtype=float).copy()
    train_y = np.asarray(train_y, dtype=float)
    medians = np.asarray([
        np.median(train_x[np.isfinite(train_x[:, j]), j]) if np.isfinite(train_x[:, j]).any() else 0.0
        for j in range(train_x.shape[1])
    ])
    train_x = np.where(np.isfinite(train_x), train_x, medians)
    predict_x = np.where(np.isfinite(predict_x), predict_x, medians)
    means = train_x.mean(axis=0)
    scales = train_x.std(axis=0)
    scales[scales <= 1e-12] = 1.0
    train_z = (train_x - means) / scales
    predict_z = (predict_x - means) / scales
    y_mean = float(train_y.mean())
    centered_y = train_y - y_mean
    if alpha == 0:
        coefficients = np.linalg.lstsq(train_z, centered_y, rcond=None)[0]
    else:
        coefficients = np.linalg.solve(
            train_z.T @ train_z + alpha * np.eye(train_z.shape[1]),
            train_z.T @ centered_y,
        )
    return y_mean + predict_z @ coefficients, dict(
        medians=medians, means=means, scales=scales, coefficients=coefficients, intercept=y_mean
    )


def r2(observed, predicted):
    observed = np.asarray(observed, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    denominator = float(np.sum((observed - observed.mean()) ** 2))
    return float(1 - np.sum((predicted - observed) ** 2) / denominator) if denominator else float("nan")


def rmse(observed, predicted):
    return float(np.sqrt(np.mean((np.asarray(predicted) - np.asarray(observed)) ** 2)))


def grouped_folds(names, seed, count=5):
    names = sorted(set(names))
    np.random.default_rng(seed).shuffle(names)
    bins = [set() for _ in range(count)]
    for index, name in enumerate(names):
        bins[index % count].add(name)
    return bins


def main():
    import importlib.util

    spec = importlib.util.spec_from_file_location("bundled_extended_descriptors", HERE / "extended_physical_descriptors.py")
    extended = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extended)

    structures = {row["name"]: row for row in read(HERE / "structures_by_target.csv")}
    features = {}
    for filename in ("current_site_features.csv", "descriptor_values.csv"):
        for row in read(HERE / filename):
            features.setdefault(key(row), {}).update(row)
    for (name, site), row in features.items():
        row.update(extended.compute(structures[name], int(site.removeprefix("metal")) - 1))

    labels_path = KONGICATS / "extracted" / "orr_analysis_energies.csv"
    labels = {key(row): row for row in read(labels_path)}
    membership = read(MODEL_DIR / "cohort_membership.csv")
    membership_by_key = {}
    for row in membership:
        if row["target"] == TARGETS[0]:
            membership_by_key[key(row)] = row["role"]
    training_keys = sorted(k for k, role in membership_by_key.items() if role == "training")
    validation_keys = sorted(k for k, role in membership_by_key.items() if role == "validation")
    if len(training_keys) != 70 or len(validation_keys) != 13:
        raise ValueError(f"unexpected revised shared split: {len(training_keys)} training / {len(validation_keys)} validation sites")
    if {k[0] for k in training_keys} & {k[0] for k in validation_keys}:
        raise ValueError("structure overlap between training and validation")
    if any(k not in features or k not in labels for k in training_keys + validation_keys):
        raise ValueError("missing feature or target row in revised split")

    # Preserve the published model's target-specific descriptors and ridge alpha;
    # refit coefficients and preprocessing on the revised training cohort.
    old_parameters = read(HERE / "final_model_parameters.csv")
    parameter_rows, validation_rows, cv_rows, metric_rows = [], [], [], []
    for target in TARGETS:
        old = [row for row in old_parameters if row["target"] == target]
        terms = [row["term"] for row in old if row["term"] != "intercept"]
        alpha = float(next(row["ridge_alpha"] for row in old if row["term"] == "intercept"))
        train_y = np.asarray([float(labels[k][target]) for k in training_keys])
        val_y = np.asarray([float(labels[k][target]) for k in validation_keys])
        train_x = np.asarray([[float(features[k].get(term) or "nan") for term in terms] for k in training_keys])
        val_x = np.asarray([[float(features[k].get(term) or "nan") for term in terms] for k in validation_keys])

        val_pred, model = fit(train_x, val_x, train_y, alpha)
        train_pred, _ = fit(train_x, train_x, train_y, alpha)
        parameter_rows.append(dict(target=target, term="intercept", standardized_coefficient=model["intercept"],
            training_median="", training_mean="", training_sd="", ridge_alpha=alpha))
        for j, term in enumerate(terms):
            parameter_rows.append(dict(target=target, term=term,
                standardized_coefficient=float(model["coefficients"][j]),
                training_median=float(model["medians"][j]), training_mean=float(model["means"][j]),
                training_sd=float(model["scales"][j]), ridge_alpha=alpha))
        for k, observed, predicted in zip(validation_keys, val_y, val_pred):
            validation_rows.append(dict(target=target, name=k[0], ads_site=k[1], observed_eV=float(observed),
                predicted_eV=float(predicted), error_eV=float(predicted - observed)))

        repeat_scores, repeat_rmses = [], []
        for repeat in range(3):
            held_names_by_fold = grouped_folds((k[0] for k in training_keys), 20261011 + repeat)
            repeated_observed, repeated_predicted = [], []
            for fold, held_names in enumerate(held_names_by_fold, 1):
                train_ix = [i for i, k in enumerate(training_keys) if k[0] not in held_names]
                held_ix = [i for i, k in enumerate(training_keys) if k[0] in held_names]
                pred, _ = fit(train_x[train_ix], train_x[held_ix], train_y[train_ix], alpha)
                repeated_observed.extend(train_y[held_ix])
                repeated_predicted.extend(pred)
                for i, value in zip(held_ix, pred):
                    k = training_keys[i]
                    cv_rows.append(dict(target=target, repeat=repeat + 1, fold=fold, name=k[0], ads_site=k[1],
                        observed_eV=float(train_y[i]), predicted_eV=float(value), error_eV=float(value - train_y[i])))
            repeat_scores.append(r2(repeated_observed, repeated_predicted))
            repeat_rmses.append(rmse(repeated_observed, repeated_predicted))

        metric_rows.append(dict(target=target, training_sites=len(training_keys),
            training_structures=len({k[0] for k in training_keys}), validation_sites=len(validation_keys),
            validation_structures=len({k[0] for k in validation_keys}), selected_predictors=len(terms),
            ridge_alpha=alpha, training_R2=r2(train_y, train_pred), mean_repeat_R2cv=float(np.mean(repeat_scores)),
            pooled_repeated_OOF_R2=r2([row["observed_eV"] for row in cv_rows if row["target"] == target],
                                      [row["predicted_eV"] for row in cv_rows if row["target"] == target]),
            validation_R2=r2(val_y, val_pred), mean_repeat_RMSEcv_eV=float(np.mean(repeat_rmses)),
            validation_RMSE_eV=rmse(val_y, val_pred), inner_grouped_RMSE_eV="",
            final_features=";".join(terms), validation_interpretation="descriptive; target labels informed split selection"))

    write(HERE / "final_model_parameters.csv", parameter_rows)
    write(HERE / "metrics.csv", metric_rows)
    write(HERE / "validation_predictions.csv", validation_rows)
    write(HERE / "cv_predictions.csv", cv_rows)
    for name in ("cohort_membership.csv", "split_config.json", "validation_structures.csv", "validation_target_value_spread.csv"):
        source = (MODEL_DIR / name) if name in ("cohort_membership.csv",) else (SPLIT_DIR / name)
        shutil.copy2(source, HERE / name)
    print(json.dumps(dict(training_sites=len(training_keys), validation_sites=len(validation_keys),
        training_structures=len({k[0] for k in training_keys}),
        validation_structures=len({k[0] for k in validation_keys}), metrics=metric_rows), indent=2))


if __name__ == "__main__":
    main()
