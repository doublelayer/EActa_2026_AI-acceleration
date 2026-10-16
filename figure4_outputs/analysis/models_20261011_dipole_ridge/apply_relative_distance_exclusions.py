#!/usr/bin/env python3
"""Freeze the approved distance exclusions and rebuild the common split."""
import hashlib
import json
from collections import defaultdict

from select_representative_split import HERE, OUT, main as select_split, read

AUTHORIZED_STRUCTURES = {
    "KMC_Co_Cu_A2_B1_NNNNOO_q2", "KMC_Co_Ni_A2_B1_NNNNOO_q2",
    "KMC_Cr_Fe_A2_B1_NNNNSS_q2", "KMC_Cr_Ni_A2_B1_NNNNOO_q2",
    "KMC_Cu_Cu_A2_B1_NNNNSS_q2", "KMC_Cu_Cu_A2_B2_NNNNSS_q2",
    "KMC_Fe_Cu_A2_B1_NNNNSS_q2", "KMC_Fe_Cu_A2_B2_NNNNSS_q2",
    "KMC_Mn_Co_A2_B2_NNNNNN_q2", "KMC_Mn_Cu_A2_B1_NNNNSS_q2",
    "KMC_Mn_Ni_A2_B1_NNNNNN_q2", "KMC_Mn_Ni_A2_B1_NNNNSS_q2",
    "KMC_Mn_Ni_A2_B2_NNNNNN_q2", "KMC_Ni_Ni_A2_B1_NNNNOO_q2",
}


def main():
    snapshot_path = OUT / "relative_distance_exclusions.json"
    if not snapshot_path.exists():
        geometry_path = OUT / "selected_endpoint_geometry_checks.csv"
        rows = [r for r in read(geometry_path) if r["retained_for_all_targets"] == "True"]
        groups = defaultdict(list)
        for row in rows:
            metal = row["name"].split("_")[1 if row["ads_site"] == "metal1" else 2]
            adsorbate = "OOH" if row["selected_endpoint_state"].startswith("OOH") else row["selected_endpoint_state"]
            groups[metal, adsorbate].append(float(row["intended_metal_distance_A"]))
        means = {k: sum(values) / len(values) for k, values in groups.items()}
        flagged = []
        for row in rows:
            metal = row["name"].split("_")[1 if row["ads_site"] == "metal1" else 2]
            adsorbate = "OOH" if row["selected_endpoint_state"].startswith("OOH") else row["selected_endpoint_state"]
            distance, mean = float(row["intended_metal_distance_A"]), means[metal, adsorbate]
            if distance >= 1.05 * mean:
                flagged.append(dict(name=row["name"], ads_site=row["ads_site"], adsorption_metal=metal,
                    adsorbate=adsorbate, selected_endpoint_state=row["selected_endpoint_state"],
                    endpoint_id=row["endpoint_id"], distance_A=distance, reference_mean_A=mean,
                    threshold_A=1.05 * mean, above_mean_percent=100 * (distance / mean - 1)))
        if {r["name"] for r in flagged} != AUTHORIZED_STRUCTURES:
            raise ValueError("distance flags do not match the 14 structures approved for exclusion")
        snapshot = dict(relative_threshold=0.05, comparison="distance >= 1.05 * mean for the same metal and adsorbate",
            exclusion_scope="whole structure: both sites and all three targets",
            reference_policy="fixed means from the retained cohort used to identify the approved structures; no iterative reclassification",
            reference_site_rows=len({(r["name"], r["ads_site"]) for r in rows}),
            reference_structures=len({r["name"] for r in rows}),
            reference_sites=[dict(name=n, ads_site=s) for n, s in sorted({(r["name"], r["ads_site"]) for r in rows})],
            reference_means=[dict(adsorption_metal=m, adsorbate=a, sites=len(groups[m, a]),
                mean_A=mean, threshold_A=1.05 * mean) for (m, a), mean in sorted(means.items())],
            excluded_structures=sorted(AUTHORIZED_STRUCTURES),
            flagged_endpoints=sorted(flagged, key=lambda r: (r["name"], r["ads_site"], r["adsorbate"])),
            reference_geometry_sha256=hashlib.sha256(geometry_path.read_bytes()).hexdigest())
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if set(snapshot["excluded_structures"]) != AUTHORIZED_STRUCTURES or snapshot["relative_threshold"] != 0.05:
        raise ValueError("saved exclusions differ from the approved structure list or threshold")
    select_split()


if __name__ == "__main__":
    main()
