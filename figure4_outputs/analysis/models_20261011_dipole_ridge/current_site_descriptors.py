"""Calculate available clean-site descriptors for either metal site."""
import json
import math

import numpy as np


def compute(source, site):
    z = np.asarray(json.loads(source["array.numbers"]), dtype=int)
    xyz = np.asarray(json.loads(source["array.positions"]), dtype=float).reshape(-1, 3)
    q = np.asarray(json.loads(source["data.bader_charges"]), dtype=float)
    m = np.asarray(json.loads(source["data.post_opt_rpbe_d4_magmoms"]), dtype=float)
    if int(source["pbc"]) != 0 or any(len(a) != len(z) for a in (xyz, q, m)):
        raise ValueError(f"invalid clean arrays for {source['name']}")
    distance = [np.linalg.norm(xyz - xyz[metal], axis=1) for metal in (0, 1)]
    shells = [set(i for i in range(2, len(z)) if z[i] in (7, 8, 16) and distance[metal][i] <= 2.30) for metal in (0, 1)]
    shared = shells[0] & shells[1]
    result = dict(q_site=float(q[site]), q_partner=float(q[1 - site]),
        spin_site_abs=float(abs(m[site])), spin_partner_abs=float(abs(m[1 - site])),
        metal_metal_distance_A=float(np.linalg.norm(xyz[0] - xyz[1])),
        spin_product_muB2=float(m[0] * m[1]), support_net_spin_muB=float(m[2:].sum()),
        support_abs_spin_sum_muB=float(abs(m[2:]).sum()), shared_ligand_count=len(shared),
        terminal_ligand_count=len(shells[site] - shared))

    def summaries(prefix, values, operations):
        for statistic, operation in operations:
            result[prefix.format(statistic)] = float(operation(values)) if len(values) else math.nan

    stats = (("mean", np.mean), ("std", np.std), ("min", np.min), ("max", np.max))
    for prefix, metal in (("site", site), ("partner", 1 - site)):
        ids = sorted(shells[metal])
        vectors = xyz[ids] - xyz[metal]
        moments = q[ids, None] * vectors
        summaries(f"{prefix}_heteroatom_dipole_contribution_{{}}_eA", np.linalg.norm(moments, axis=1), stats)
        summaries(f"{prefix}_heteroatom_charge_{{}}_e", q[ids], (("sum", np.sum), *stats))
        summaries(f"{prefix}_heteroatom_spin_abs_{{}}_muB", abs(m[ids]), (("mean", np.mean), ("sum", np.sum)))
        result[f"{prefix}_heteroatom_charge_dipole_proxy_norm_eA"] = float(np.linalg.norm(moments.sum(axis=0))) if ids else math.nan
        angles = []
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                cosine = np.dot(vectors[i], vectors[j]) / (np.linalg.norm(vectors[i]) * np.linalg.norm(vectors[j]))
                angles.append(float(np.degrees(np.arccos(np.clip(cosine, -1, 1)))))
        summaries(f"{prefix}_angle_{{}}_deg", angles, stats)
        for label, chosen in (("shared", sorted(shared)), ("terminal", sorted(shells[metal] - shared))):
            result[f"{prefix}_{label}_ligand_charge_mean_e"] = float(q[chosen].mean()) if chosen else math.nan
    bridge_angles = []
    for atom in sorted(shared):
        v0, v1 = xyz[0] - xyz[atom], xyz[1] - xyz[atom]
        bridge_angles.append(float(np.degrees(np.arccos(np.clip(np.dot(v0, v1) / (np.linalg.norm(v0) * np.linalg.norm(v1)), -1, 1)))))
    summaries("shared_bridge_angle_{}_deg", bridge_angles, stats[:2])
    result["shared_bridge_dipole_contribution_asymmetry_mean_eA"] = float(np.mean([
        abs(q[i]) * abs(distance[0][i] - distance[1][i]) for i in sorted(shared)])) if shared else math.nan
    ids = sorted(shells[site])
    result["ligand_plane_rms_A"] = result["metal_height_above_ligand_plane_A"] = math.nan
    if len(ids) >= 3:
        centroid = xyz[ids].mean(axis=0)
        _, singular, vt = np.linalg.svd(xyz[ids] - centroid, full_matrices=False)
        result["ligand_plane_rms_A"] = float(singular[-1] / np.sqrt(len(ids)))
        result["metal_height_above_ligand_plane_A"] = float(abs((xyz[site] - centroid) @ vt[-1]))
    for label, numbers in (("C", (6,)), ("heteroatom", (7, 8, 16))):
        selected = [i for i in range(2, len(z)) if z[i] in numbers and distance[site][i] > 2.30]
        for radius in (2.8, 3.6):
            result[f"second_shell_{label}_{radius:.1f}A"] = float(sum(np.exp(-((distance[site][i] - radius) / 0.45) ** 2) for i in selected))
    return result
