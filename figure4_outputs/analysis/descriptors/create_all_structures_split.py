#!/usr/bin/env python3
"""Create a catalyst-level split from the all-structures dataset.

Catalysts are assigned from scratch by a fixed seed. Only catalysts having all
three targets are eligible for validation. Every site and target row for a
catalyst receives the same split.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ALL_DATA = HERE / "model_all_structures_data.csv"
DEFAULT_OUTPUT = HERE / "model_all_structures_training_data.csv"
DEFAULT_SPLIT_OUTPUT = HERE / "model_all_structures_split.csv"
TARGET_OUTPUTS = {
    "G_O": HERE / "model_G_O_training_data.csv",
    "G_OH": HERE / "model_G_OH_training_data.csv",
    "G_OOH": HERE / "model_G_OOH_training_data.csv",
}
TARGETS = ("G_O", "G_OH", "G_OOH")
SPLITS = {"training", "validation"}
SEED = 20261015
VALIDATION_FRACTION = 1 / 6


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader.fieldnames), list(reader)


def build_assignments(rows: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, set[str]]]:
    targets_by_name: dict[str, set[str]] = defaultdict(set)
    seen_rows = set()
    for row in rows:
        name = (row.get("name") or "").strip()
        site = (row.get("ads_site") or "").strip()
        target = (row.get("target") or "").strip()
        if not name or site not in ("metal1", "metal2") or target not in TARGETS:
            raise ValueError(f"invalid all-structures data row: {row}")
        key = (name, site, target)
        if key in seen_rows:
            raise ValueError(f"duplicate target/site row: {key}")
        seen_rows.add(key)
        targets_by_name[name].add(target)

    names = set(targets_by_name)
    fully_labeled = sorted(
        name for name in names if targets_by_name[name] == set(TARGETS)
    )
    validation_count = round(len(names) * VALIDATION_FRACTION)
    if not 0 < validation_count <= len(fully_labeled):
        raise ValueError(
            "cannot create a non-empty validation split from fully labeled catalysts: "
            f"need {validation_count}, have {len(fully_labeled)} eligible catalysts"
        )
    validation_names = set(random.Random(SEED).sample(fully_labeled, validation_count))
    assignments = {
        name: "validation" if name in validation_names else "training"
        for name in names
    }

    if set(assignments) != names:
        raise ValueError("not every all-structures catalyst received a split")
    if set(assignments.values()) != SPLITS:
        raise ValueError(f"both splits must be non-empty: {Counter(assignments.values())}")
    return assignments, targets_by_name


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ALL_DATA,
                        help=f"unsplit all-structures CSV (default: {ALL_DATA})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"combined train/validation CSV (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--split-output", type=Path, default=DEFAULT_SPLIT_OUTPUT,
                        help=f"one row per catalyst split map (default: {DEFAULT_SPLIT_OUTPUT})")
    args = parser.parse_args()

    fields, rows = read_csv(args.data)
    assignments, targets_by_name = build_assignments(rows)

    output_fields = [field for field in fields if field != "split"]
    insert_index = output_fields.index("ads_site") + 1
    output_fields.insert(insert_index, "split")
    split_rows = []
    for row in rows:
        split_row = dict(row)
        name = (row.get("name") or "").strip()
        split_row["name"] = name
        split_row["ads_site"] = (row.get("ads_site") or "").strip()
        split_row["target"] = (row.get("target") or "").strip()
        split_row["split"] = assignments[name]
        split_rows.append(split_row)

    split_map_rows = [
        {
            "name": name,
            "split": assignments[name],
            "targets_available": ";".join(target for target in TARGETS
                                           if target in targets_by_name[name]),
        }
        for name in sorted(assignments)
    ]
    write_rows(args.output.resolve(), output_fields, split_rows)
    write_rows(args.split_output.resolve(),
               ["name", "split", "targets_available"], split_map_rows)
    target_output_paths = {}
    for target, target_path in TARGET_OUTPUTS.items():
        target_rows = [row for row in split_rows if row["target"] == target]
        write_rows(target_path, output_fields, target_rows)
        target_output_paths[target] = str(target_path.resolve())

    rows_by_target_and_split = {
        target: {
            split: sum(row["target"] == target and row["split"] == split
                       for row in split_rows)
            for split in ("training", "validation")
        }
        for target in TARGETS
    }
    catalysts_by_split = dict(Counter(assignments.values()))
    print(json.dumps({
        "data": str(args.data.resolve()),
        "output": str(args.output.resolve()),
        "split_map": str(args.split_output.resolve()),
        "target_outputs": target_output_paths,
        "catalysts_by_split": catalysts_by_split,
        "rows_by_target_and_split": rows_by_target_and_split,
        "validation_fraction": VALIDATION_FRACTION,
        "seed_for_validation_catalysts": SEED,
        "validation_catalysts": sum(split == "validation" for split in assignments.values()),
    }, indent=2))


if __name__ == "__main__":
    main()
