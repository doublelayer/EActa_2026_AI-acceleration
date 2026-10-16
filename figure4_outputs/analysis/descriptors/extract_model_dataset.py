#!/usr/bin/env python3
"""Extract unsplit model labels and descriptors from the RPBE-D4 databases.

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

This writes model_all_structures_data.csv beside this script, using every
matching target/site record found in the databases. The output has no split
column; train/validation assignments are added by create_all_structures_split.py.
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


def build_all_structure_rows(clean_records, adsorption_records, descriptor_values):
    """Build unsplit rows for every target/site pair with a matching clean structure."""
    rows = []
    counts = {}
    unmatched_clean = {}
    for target in TARGETS:
        target_records = adsorption_records[target]
        keys = sorted(key for key in target_records if key[0] in clean_records)
        unmatched_clean[target] = sum(key[0] not in clean_records for key in target_records)
        counts[target] = len(keys)
        for key in keys:
            name, site = key
            clean = clean_records[name]
            adsorbed = target_records[key]
            assert_metadata_match(adsorbed, clean, key)
            row = {
                "target": target,
                "name": name,
                "ads_site": site,
                "observed_eV": calculate_target_value(target, adsorbed, clean),
            }
            features = descriptor_values[key]
            for feature in FEATURES:
                value = float(features[feature])
                # Keep every target-labeled site; an undefined descriptor is blank.
                row[feature] = value if math.isfinite(value) else ""
            rows.append(row)
    return rows, counts, unmatched_clean


def write_csv(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["target", "name", "ads_site", "observed_eV", *FEATURES]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"CSV output path (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    clean_records = load_clean_database(DATABASES["bare"])
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
        key for target_records in adsorption_records.values()
        for key in target_records if key[0] in clean_records
    }
    descriptor_values = {
        key: compute_site_descriptors(clean_records[key[0]], key[1])
        for key in sorted(all_keys)
    }
    rows, counts, unmatched_clean = build_all_structure_rows(
        clean_records, adsorption_records, descriptor_values
    )
    output_path = args.output.resolve()
    write_csv(output_path, rows)
    site_pairs = len(all_keys)

    print(json.dumps({
        "output": str(output_path),
        "rows": len(rows),
        "site_pairs": site_pairs,
        "rows_by_target": counts,
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
