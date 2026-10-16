#!/usr/bin/env python3
"""Extract descriptors and prepare role-split model datasets from RPBE-D4 databases.

The five databases are the script's data inputs. Reference corrections and
required predictor names are embedded below.

The original analysis notebook calculates electronic adsorption energies from
clean and adsorbate total energies using H2/H2O references, then adds
thermochemical and solvation corrections to obtain G_X. This script follows
that calculation. The input databases provide raw total energies and do not
store precomputed E_ads_* fields. For OOH, the lower raw total energy is
selected first, as in the notebook; the same correction applies to both
orientations.

Run from this directory with:

    python extract_model_dataset.py

The structure-level assignments come from structure_model_roles.csv. Eligible
target/site labels are limited to the sites retained in the existing
notebook/model_inputs/cohort_membership.csv manifest. This preserves its data
quality exclusions while applying the supplied structure-level roles.

The script writes the eligible labeled training/validation table, separate
target/split CSVs, a structure/site descriptor table for every bare structure,
and a role map beside this script. Prediction-role structures are included in
the descriptor table and excluded from the model training files.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
import struct
from contextlib import closing
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATE_DIR = HERE.parent
DATABASES = {
    "bare": DATE_DIR / "DASC_Bare_Catalysts_RPBE_D4.db",
    "OH": DATE_DIR / "DASC_OH_Adsorption_RPBE_D4.db",
    "O": DATE_DIR / "DASC_O_Adsorption_RPBE_D4.db",
    "OOHx": DATE_DIR / "DASC_OOHx_Adsorption_RPBE_D4.db",
    "OOHz": DATE_DIR / "DASC_OOHz_Adsorption_RPBE_D4.db",
}
DEFAULT_OUTPUT = HERE / "model_all_structures_data.csv"
DEFAULT_DESCRIPTOR_OUTPUT = HERE / "model_structure_descriptors.csv"
DEFAULT_ROLES = HERE / "structure_model_roles.csv"
DEFAULT_ELIGIBLE_SITES = DATE_DIR.parent / "notebook" / "model_inputs" / "cohort_membership.csv"
DEFAULT_TRAINING_OUTPUT = HERE / "model_all_structures_training_data.csv"
DEFAULT_SPLIT_OUTPUT = HERE / "model_all_structures_split.csv"

# Electronic reference energies for H2 and H2O, in eV.
E_H2_EV = -6.73
E_H2O_EV = -13.97

# Electronic adsorption-energy references, calculated from E_H2 and E_H2O.
ADSORPTION_REFERENCE_OFFSETS_EV = {
    "G_OH": -E_H2O_EV + 0.5 * E_H2_EV,
    "G_O": -E_H2O_EV + E_H2_EV,
    "G_OOH": -2 * E_H2O_EV + 1.5 * E_H2_EV,
}
# Literature Delta ZPE - T Delta S corrections at 300 K for OH* (+0.35 eV) and O*
# (+0.05 eV) are from Table 3 of J. K. Norskov et al., "Origin of the
# Overpotential for Oxygen Reduction at a Fuel-Cell Cathode," J. Phys. Chem. B
# 108 (2004), 17886–17892, https://doi.org/10.1021/jp047349j. The OOH* value
# (+0.40 eV) uses the additive O* + OH* approximation documented in the
# analysis notebook; these are fixed corrections, not structure-specific
# vibrational calculations.
THERMOCHEMICAL_CORRECTIONS_EV = {
    "G_OH": 0.35,
    "G_O": 0.05,
    "G_OOH": 0.40,
}
# A literature precedent for these fixed shifts appears in the Supporting
# Information (Computational methods) of X. Guo et al., "Data-driven pursuit
# of electrochemically stable 2D materials with basal plane activity toward
# oxygen electrocatalysis," Energy Environ. Sci. 16 (2023), 5003-5018,
# https://doi.org/10.1039/D3EE01723K. It assigns 0.3, 0.0, and 0.3 eV to
# OOH*, O*, and OH*, respectively, citing prior investigations; the text
# attributes the OH*/OOH* stabilization to hydrogen bonding with water and
# applies no shift to O*. Here stabilization is represented as a negative
# correction to G. This is a literature precedent; the analysis notebook does
# not document whether it was the source of these constants.
SOLVATION_CORRECTIONS_EV = {
    "G_OH": -0.30,
    "G_O": 0.00,
    "G_OOH": -0.30,
}
TARGETS = tuple(ADSORPTION_REFERENCE_OFFSETS_EV)
ROLE_COLUMN_BY_TARGET = {
    "G_O": "O_model_role",
    "G_OH": "OH_model_role",
    "G_OOH": "OOH_model_role",
}
MODEL_ROLES = ("training", "validation", "prediction")

# Export every descriptor for every target. Model predictors are selected from
# the descriptor columns using training data, without importing an older model's
# feature list.
FEATURES = (
    "site_bader_electron_population",
    "spin_site_abs",
    "q_site",
    "site_heteroatom_dipole_contribution_max_eA",
    "metal_pair_charge_dipole_axis_eA",
    "site_heteroatom_charge_min_e",
    "site_terminal_ligand_charge_mean_e",
    "site_metal_ligand_spin_product_muB2",
)

METAL_Z = {"Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29}


def decode_blob(blob, kind: str) -> list:
    if not blob:
        return []
    width, code = (4, "i") if kind == "int" else (8, "d")
    if len(blob) % width:
        raise ValueError(f"malformed {kind} array blob ({len(blob)} bytes)")
    return list(struct.unpack("<" + code * (len(blob) // width), blob))


def decode_data(blob) -> dict:
    if not blob:
        return {}
    try:
        return json.loads(blob[8:].decode("utf-8"))
    except Exception as exc:
        raise ValueError("could not decode ASE system data") from exc


def connect_readonly(path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


def load_structure_roles(path: Path) -> dict[str, dict[str, str]]:
    """Read target-specific roles from the user-provided structure map."""
    required_fields = ["name", *ROLE_COLUMN_BY_TARGET.values()]
    roles = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"role CSV has no header: {path}")
        missing_fields = [field for field in required_fields if field not in reader.fieldnames]
        if missing_fields:
            raise ValueError(f"role CSV is missing columns: {', '.join(missing_fields)}")
        for line_number, row in enumerate(reader, start=2):
            name = (row.get("name") or "").strip()
            if not name:
                raise ValueError(f"role CSV has a blank structure name at line {line_number}")
            if name in roles:
                raise ValueError(f"duplicate structure name in role CSV: {name}")
            target_roles = {}
            for target, column in ROLE_COLUMN_BY_TARGET.items():
                role = (row.get(column) or "").strip()
                if role not in MODEL_ROLES:
                    raise ValueError(
                        f"invalid {column} value at line {line_number} for {name}: {role!r}"
                    )
                target_roles[target] = role
            roles[name] = target_roles
    if not roles:
        raise ValueError(f"role CSV has no structure rows: {path}")
    return roles


def load_eligible_sites(path: Path, structure_roles: dict[str, dict[str, str]]):
    """Load target/site labels retained by the existing data-quality manifest."""
    required_fields = ("target", "name", "ads_site", "role")
    eligible = set()
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"eligible-site CSV has no header: {path}")
        missing_fields = [field for field in required_fields if field not in reader.fieldnames]
        if missing_fields:
            raise ValueError(
                f"eligible-site CSV is missing columns: {', '.join(missing_fields)}"
            )
        for line_number, row in enumerate(reader, start=2):
            target = (row.get("target") or "").strip()
            name = (row.get("name") or "").strip()
            site = (row.get("ads_site") or "").strip()
            membership_role = (row.get("role") or "").strip()
            if target not in TARGETS or site not in ("metal1", "metal2") or not name:
                raise ValueError(f"invalid eligible-site row at line {line_number}: {row}")
            key = (target, name, site)
            if key in seen:
                raise ValueError(f"duplicate target/site membership in {path}: {key}")
            seen.add(key)
            if membership_role in ("training", "validation"):
                if name not in structure_roles:
                    raise ValueError(f"eligible structure is missing from role CSV: {name}")
                role_from_csv = structure_roles[name][target]
                if role_from_csv != membership_role:
                    raise ValueError(
                        f"role mismatch for {target}, {name}, {site}: "
                        f"role CSV says {role_from_csv}, eligible-site manifest says {membership_role}"
                    )
                eligible.add(key)
            elif membership_role != "excluded_by_data_quality":
                raise ValueError(
                    f"unknown eligible-site status at line {line_number}: {membership_role!r}"
                )
    if not eligible:
        raise ValueError(f"eligible-site CSV has no retained target/site rows: {path}")
    return eligible


def load_clean_database(path: Path) -> dict[str, dict]:
    """Read all clean catalyst structures."""
    records = {}
    with closing(connect_readonly(path)) as connection:
        connection.row_factory = sqlite3.Row
        query = """SELECT id, key_value_pairs, data, numbers, positions, pbc,
                          energy, natoms
                   FROM systems ORDER BY id"""
        for system in connection.execute(query):
            props = json.loads(system["key_value_pairs"] or "{}")
            name = props.get("name", "")
            if name in records:
                raise ValueError(f"duplicate clean catalyst name: {name}")
            data = decode_data(system["data"])
            numbers = np.asarray(decode_blob(system["numbers"], "int"), dtype=int)
            positions = np.asarray(decode_blob(system["positions"], "float"), dtype=float)
            charges = np.asarray(data.get("bader_charges", []), dtype=float)
            moments = np.asarray(data.get("post_opt_rpbe_d4_magmoms", []), dtype=float)
            if len(numbers) < 2 or len(numbers) != system["natoms"] or len(positions) != 3 * len(numbers):
                raise ValueError(f"invalid clean atom arrays for {name}")
            if len(charges) != len(numbers) or len(moments) != len(numbers):
                raise ValueError(f"missing or misaligned Bader/spin arrays for {name}")
            if not all(np.isfinite(values).all() for values in (positions, charges, moments)):
                raise ValueError(f"non-finite atom data for {name}")
            if system["pbc"] != 0:
                raise ValueError(f"expected non-periodic clean catalyst: {name}")
            for metal_key, atom_index in (("metal1", 0), ("metal2", 1)):
                metal = props.get(metal_key)
                if metal not in METAL_Z or numbers[atom_index] != METAL_Z[metal]:
                    raise ValueError(f"{metal_key} metadata does not match atom order for {name}")
            energy = system["energy"]
            if energy is None or not math.isfinite(float(energy)):
                raise ValueError(f"non-finite clean total energy for {name}")
            records[name] = {
                "name": name,
                "props": props,
                "energy": float(energy),
                "pbc": system["pbc"],
                "numbers": numbers,
                "positions": positions.reshape(-1, 3),
                "charges": charges,
                "electrons": numbers.astype(float) - charges,
                "moments": moments,
            }
    return records


def load_adsorption_database(path: Path, expected_adsorbate: str) -> dict[tuple[str, str], dict]:
    """Read all raw total energies for an adsorbate."""
    records = {}
    with closing(connect_readonly(path)) as connection:
        query = "SELECT id, key_value_pairs, energy, pbc FROM systems ORDER BY id"
        for record_id, key_values, energy, pbc in connection.execute(query):
            props = json.loads(key_values or "{}")
            catalyst = props.get("catalyst_name", "")
            site = props.get("ads_site", "")
            key = (catalyst, site)
            name = props.get("name", "")
            adsorbate = props.get("adsorbate", "")
            if adsorbate != expected_adsorbate:
                raise ValueError(f"expected {expected_adsorbate} in {path.name}, found {adsorbate!r} at record {record_id}")
            if name != f"{catalyst}_{expected_adsorbate}_{site}":
                raise ValueError(f"record name disagrees with catalyst/site metadata: {name}")
            if site not in ("metal1", "metal2"):
                raise ValueError(f"unknown adsorption site in {path.name}: {site!r} at record {record_id}")
            if energy is None or not math.isfinite(float(energy)):
                raise ValueError(f"non-finite adsorption total energy in {path.name}: {name}")
            if pbc != 0:
                raise ValueError(f"expected non-periodic adsorption structure: {name}")
            if key in records:
                raise ValueError(f"duplicate adsorption site in {path.name}: {key}")
            records[key] = {"energy": float(energy), "metadata": props}
    return records


def assert_metadata_match(adsorbed: dict, clean: dict, key: tuple[str, str]) -> None:
    """Audit the same catalyst/site pairing used by the article notebook."""
    for field in ("metal1", "metal2", "acid", "base", "total_charge"):
        ads_value = adsorbed["metadata"].get(field, "")
        clean_value = clean["props"].get(field, "")
        if field == "total_charge":
            try:
                same = math.isclose(float(ads_value), float(clean_value), rel_tol=0, abs_tol=1e-12)
            except (TypeError, ValueError):
                same = str(ads_value) == str(clean_value)
        else:
            same = str(ads_value) == str(clean_value)
        if not same:
            raise ValueError(f"adsorbate and clean {field} metadata differ for {key}")


def select_ooh_records(x_records, z_records) -> dict[tuple[str, str], tuple[dict, str]]:
    """Mirror notebook selection: lower OOH total energy per site; ties favor x."""
    selected = {}
    for orientation, records in (("x", x_records), ("z", z_records)):
        for key, record in records.items():
            previous = selected.get(key)
            if previous is None or (record["energy"], orientation) < (previous[0]["energy"], previous[1]):
                selected[key] = (record, orientation)
    return selected


def calculate_target_value(target: str, adsorbed: dict, clean: dict) -> float:
    """Calculate G_X using the original notebook's reference and corrections."""
    value = (
        adsorbed["energy"]
        - clean["energy"]
        + ADSORPTION_REFERENCE_OFFSETS_EV[target]
        + THERMOCHEMICAL_CORRECTIONS_EV[target]
        + SOLVATION_CORRECTIONS_EV[target]
    )
    if not math.isfinite(value):
        raise ValueError(f"non-finite calculated {target} value for {clean['name']}")
    return value


def compute_site_descriptors(clean: dict, site: str) -> dict[str, float]:
    """Compute only predictor values used by the saved models."""
    site_index = 0 if site == "metal1" else 1 if site == "metal2" else None
    if site_index is None:
        raise ValueError(f"unknown adsorption site {site!r}")
    numbers = clean["numbers"]
    positions = clean["positions"]
    charges = clean["charges"]
    electrons = clean["electrons"]
    moments = clean["moments"]
    partner_index = 1 - site_index

    distances = [np.linalg.norm(positions - positions[index], axis=1) for index in (0, 1)]
    shells = [
        {index for index in range(2, len(numbers))
         if numbers[index] in (7, 8, 16) and distances[metal][index] <= 2.30}
        for metal in (0, 1)
    ]
    shared = shells[0] & shells[1]
    site_ligands = sorted(shells[site_index])
    terminal_ligands = sorted(shells[site_index] - shared)
    ligand_vectors = positions[site_ligands] - positions[site_index]
    dipole_contributions = np.linalg.norm(charges[site_ligands, None] * ligand_vectors, axis=1)
    metal_pair_distance = float(np.linalg.norm(positions[site_index] - positions[partner_index]))

    result = {
        "site_bader_electron_population": float(electrons[site_index]),
        "spin_site_abs": float(abs(moments[site_index])),
        "q_site": float(charges[site_index]),
        "site_heteroatom_dipole_contribution_max_eA": (
            float(dipole_contributions.max()) if len(dipole_contributions) else math.nan
        ),
        "metal_pair_charge_dipole_axis_eA": float(
            (charges[site_index] - charges[partner_index]) * metal_pair_distance / 2
        ),
        "site_heteroatom_charge_min_e": (
            float(charges[site_ligands].min()) if site_ligands else math.nan
        ),
        "site_terminal_ligand_charge_mean_e": (
            float(charges[terminal_ligands].mean()) if terminal_ligands else math.nan
        ),
        "site_metal_ligand_spin_product_muB2": (
            float(moments[site_index] * moments[site_ligands].mean())
            if site_ligands else math.nan
        ),
    }
    return result


def build_all_structure_rows(
    clean_records, adsorption_records, descriptor_values, structure_roles, eligible_sites
):
    """Build role-tagged descriptor rows, labeling only retained target/site pairs."""
    rows = []
    eligible_counts = {}
    unmatched_clean = {}
    for target in TARGETS:
        target_records = adsorption_records[target]
        unmatched_clean[target] = sum(key[0] not in clean_records for key in target_records)
        eligible_counts[target] = 0
        target_sites = sorted(
            (name, site) for eligible_target, name, site in eligible_sites
            if eligible_target == target
        )
        for name, site in target_sites:
            key = (name, site)
            clean = clean_records[name]
            adsorbed = target_records.get(key)
            if adsorbed is None:
                raise ValueError(
                    f"eligible target/site has no adsorption record for {target}, {name}, {site}"
                )
            assert_metadata_match(adsorbed, clean, key)
            row = {
                "target": target,
                "name": name,
                "ads_site": site,
                "split": structure_roles[name][target],
                "observed_eV": calculate_target_value(target, adsorbed, clean),
            }
            features = descriptor_values[key]
            for feature in FEATURES:
                value = float(features[feature])
                row[feature] = value if math.isfinite(value) else ""
            rows.append(row)
            eligible_counts[target] += 1
    return rows, eligible_counts, unmatched_clean


def build_structure_descriptor_rows(clean_records, descriptor_values, structure_roles):
    """Build one target-independent descriptor row per structure and metal site."""
    rows = []
    for name in sorted(clean_records):
        for site in ("metal1", "metal2"):
            row = {
                "name": name,
                "ads_site": site,
                **{
                    column: structure_roles[name][target]
                    for target, column in ROLE_COLUMN_BY_TARGET.items()
                },
            }
            for feature, value in descriptor_values[(name, site)].items():
                row[feature] = value if math.isfinite(value) else ""
            rows.append(row)
    return rows


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = ["target", "name", "ads_site", "split", "observed_eV", *FEATURES]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"labeled training/validation CSV path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--descriptor-output", type=Path, default=DEFAULT_DESCRIPTOR_OUTPUT,
                        help=f"all-structure descriptor CSV path (default: {DEFAULT_DESCRIPTOR_OUTPUT})")
    parser.add_argument("--roles", type=Path, default=DEFAULT_ROLES,
                        help=f"structure role CSV path (default: {DEFAULT_ROLES})")
    parser.add_argument("--eligible-sites", type=Path, default=DEFAULT_ELIGIBLE_SITES,
                        help=f"retained target/site manifest (default: {DEFAULT_ELIGIBLE_SITES})")
    parser.add_argument("--training-output", type=Path, default=DEFAULT_TRAINING_OUTPUT,
                        help=f"labeled training/validation CSV for model fitting (default: {DEFAULT_TRAINING_OUTPUT})")
    parser.add_argument("--split-output", type=Path, default=DEFAULT_SPLIT_OUTPUT,
                        help=f"structure role map output path (default: {DEFAULT_SPLIT_OUTPUT})")
    args = parser.parse_args()

    structure_roles = load_structure_roles(args.roles)
    eligible_sites = load_eligible_sites(args.eligible_sites, structure_roles)
    clean_records = load_clean_database(DATABASES["bare"])
    missing_roles = set(clean_records) - set(structure_roles)
    extra_roles = set(structure_roles) - set(clean_records)
    if missing_roles or extra_roles:
        raise ValueError(
            "role CSV and bare catalyst database names differ: "
            f"missing roles for {len(missing_roles)} clean structures "
            f"({sorted(missing_roles)[:5]}), "
            f"unknown role structures {len(extra_roles)} ({sorted(extra_roles)[:5]})"
        )

    adsorption_records = {
        "G_OH": load_adsorption_database(DATABASES["OH"], "OH"),
        "G_O": load_adsorption_database(DATABASES["O"], "O"),
    }
    ooh_x = load_adsorption_database(DATABASES["OOHx"], "OOH")
    ooh_z = load_adsorption_database(DATABASES["OOHz"], "OOH")
    adsorption_records["G_OOH"] = {
        key: value[0] for key, value in select_ooh_records(ooh_x, ooh_z).items()
    }
    all_keys = {
        (name, site)
        for name in clean_records
        for site in ("metal1", "metal2")
    }
    descriptor_values = {
        key: compute_site_descriptors(clean_records[key[0]], key[1])
        for key in sorted(all_keys)
    }
    rows, eligible_counts, unmatched_clean = build_all_structure_rows(
        clean_records, adsorption_records, descriptor_values,
        structure_roles, eligible_sites,
    )
    output_path = args.output.resolve()
    write_csv(output_path, rows)

    descriptor_rows = build_structure_descriptor_rows(
        clean_records, descriptor_values, structure_roles
    )
    descriptor_output_path = args.descriptor_output.resolve()
    write_csv(
        descriptor_output_path,
        descriptor_rows,
        ["name", "ads_site", *ROLE_COLUMN_BY_TARGET.values(), *FEATURES],
    )

    labeled_training_validation_rows = rows
    training_output_path = args.training_output.resolve()
    write_csv(training_output_path, labeled_training_validation_rows)

    split_rows = [
        {
            "name": name,
            **{
                column: structure_roles[name][target]
                for target, column in ROLE_COLUMN_BY_TARGET.items()
            },
        }
        for name in sorted(structure_roles)
    ]
    split_output_path = args.split_output.resolve()
    write_csv(
        split_output_path,
        split_rows,
        ["name", *ROLE_COLUMN_BY_TARGET.values()],
    )

    target_outputs = {}
    rows_by_target_and_role = {}
    labeled_rows_by_target_and_role = {}
    for target in TARGETS:
        target_outputs[target] = {}
        rows_by_target_and_role[target] = {}
        labeled_rows_by_target_and_role[target] = {}
        target_rows = [row for row in rows if row["target"] == target]
        for role in ("training", "validation"):
            role_rows = [row for row in target_rows if row["split"] == role]
            rows_by_target_and_role[target][role] = len(role_rows)
            labeled_rows_by_target_and_role[target][role] = len(role_rows)
            role_output_path = HERE / f"model_{target}_{role}_data.csv"
            write_csv(role_output_path, role_rows)
            target_outputs[target][role] = str(role_output_path.resolve())

    print(json.dumps({
        "output": str(output_path),
        "structure_descriptors": str(descriptor_output_path),
        "training_validation_data": str(training_output_path),
        "role_map": str(split_output_path),
        "roles_input": str(args.roles.resolve()),
        "eligible_site_manifest": str(args.eligible_sites.resolve()),
        "rows": len(rows),
        "descriptor_site_pairs": len(all_keys),
        "structure_descriptor_rows": len(descriptor_rows),
        "eligible_labeled_rows_by_target": eligible_counts,
        "rows_by_target_and_role": rows_by_target_and_role,
        "labeled_rows_by_target_and_role": labeled_rows_by_target_and_role,
        "target_role_outputs": target_outputs,
        "adsorption_keys_without_bare_structure": unmatched_clean,
        "descriptors": list(FEATURES),
        "gas_reference_energies_eV": {"H2": E_H2_EV, "H2O": E_H2O_EV},
        "adsorption_reference_offsets_eV": {
            target: ADSORPTION_REFERENCE_OFFSETS_EV[target] for target in TARGETS
        },
        "thermochemical_corrections_eV": {
            target: THERMOCHEMICAL_CORRECTIONS_EV[target] for target in TARGETS
        },
        "solvation_corrections_eV": {
            target: SOLVATION_CORRECTIONS_EV[target] for target in TARGETS
        },
        "net_G_additions_eV": {
            target: (
                ADSORPTION_REFERENCE_OFFSETS_EV[target]
                + THERMOCHEMICAL_CORRECTIONS_EV[target]
                + SOLVATION_CORRECTIONS_EV[target]
            )
            for target in TARGETS
        },
    }, indent=2))


if __name__ == "__main__":
    main()
