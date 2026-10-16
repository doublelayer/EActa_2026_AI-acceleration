#!/usr/bin/env python3
"""Plot observed-versus-predicted model results for training and validation."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
TARGETS = ("G_OH", "G_O", "G_OOH")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def plot_split(ax, rows: list[dict[str, str]], split: str, color: str) -> None:
    observed = np.asarray([float(row["observed_eV"]) for row in rows])
    predicted = np.asarray([float(row["predicted_eV"]) for row in rows])
    ax.scatter(observed, predicted, s=34, alpha=0.78, color=color,
               edgecolors="white", linewidths=0.45, label=split)


def format_metrics(metrics: dict[str, str], split: str) -> str:
    prefix = "training" if split == "Training" else "validation"
    r2 = float(metrics[f"{prefix}_R2"])
    rmse = float(metrics[f"{prefix}_RMSE_eV"])
    mae = float(metrics[f"{prefix}_MAE_eV"])
    return f"$R^2$ = {r2:.3f}\nRMSE = {rmse:.3f} eV\nMAE = {mae:.3f} eV"


def configure_axes(ax, rows: list[dict[str, str]]) -> None:
    observed = [float(row["observed_eV"]) for row in rows]
    predicted = [float(row["predicted_eV"]) for row in rows]
    low = min(observed + predicted)
    high = max(observed + predicted)
    padding = max((high - low) * 0.06, 0.02)
    low -= padding
    high += padding
    ax.plot([low, high], [low, high], color="#333333", linestyle="--",
            linewidth=1.25, label="Ideal: predicted = observed")
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Observed target (eV)")
    ax.set_ylabel("Predicted target (eV)")
    ax.grid(True, color="#d9d9d9", linewidth=0.65, alpha=0.75)
    ax.set_axisbelow(True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=HERE,
                        help=f"directory with model output CSVs (default: {HERE})")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="plot output directory (default: <model-dir>/regression_plots)")
    args = parser.parse_args()
    model_dir = args.model_dir.resolve()
    output_dir = (args.output_dir or model_dir / "regression_plots").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    predictions = read_csv(model_dir / "predictions.csv")
    metrics_rows = read_csv(model_dir / "model_metrics.csv")
    metrics_by_target = {row["target"]: row for row in metrics_rows}
    colors = {"training": "#2878B5", "validation": "#E07A24"}

    overview, axes = plt.subplots(1, len(TARGETS), figsize=(15.2, 5.4),
                                  constrained_layout=True)
    overview.suptitle("Observed vs predicted: training and validation", fontsize=15)

    for target, ax in zip(TARGETS, axes):
        target_rows = [row for row in predictions if row["target"] == target]
        train_rows = [row for row in target_rows if row["split"] == "training"]
        validation_rows = [row for row in target_rows if row["split"] == "validation"]
        if not train_rows or not validation_rows:
            raise ValueError(f"{target} must have training and validation predictions")
        combined = train_rows + validation_rows
        plot_split(ax, train_rows, "Training", colors["training"])
        plot_split(ax, validation_rows, "Validation", colors["validation"])
        configure_axes(ax, combined)
        ax.set_title(target)
        metrics = metrics_by_target[target]
        ax.text(0.04, 0.96,
                "Training\n" + format_metrics(metrics, "Training") +
                "\n\nValidation\n" + format_metrics(metrics, "Validation"),
                transform=ax.transAxes, va="top", ha="left", fontsize=8.5,
                bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "alpha": 0.9,
                      "edgecolor": "#cccccc"})
        ax.legend(loc="lower right", fontsize=8, frameon=True)

        split_figure, split_axes = plt.subplots(1, 2, figsize=(10.8, 5.0),
                                                constrained_layout=True)
        for split_ax, rows, split, color in zip(
                split_axes,
                (train_rows, validation_rows),
                ("Training", "Validation"),
                (colors["training"], colors["validation"])):
            plot_split(split_ax, rows, split, color)
            configure_axes(split_ax, combined)
            split_ax.set_title(f"{split} (n={len(rows)})")
            split_ax.text(0.04, 0.96, format_metrics(metrics, split),
                          transform=split_ax.transAxes, va="top", ha="left", fontsize=9,
                          bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "alpha": 0.9,
                                "edgecolor": "#cccccc"})
        split_figure.suptitle(f"{target}: training and validation", fontsize=14)
        split_figure.savefig(output_dir / f"regression_{target}_training_validation.png",
                             dpi=300, bbox_inches="tight")
        plt.close(split_figure)

    overview.savefig(output_dir / "regression_train_validation_all_targets.png",
                     dpi=300, bbox_inches="tight")
    plt.close(overview)
    print(f"Saved regression plots to {output_dir}")


if __name__ == "__main__":
    main()
