"""Additional rotation-invariant descriptors from clean DFT arrays only."""
import csv
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def catalog(populations=False):
    out = {}
    def add(key, name, units, formula, description):
        out[key] = dict(feature=key, name=name, units=units, formula=formula, description=description)
    add("metal_pair_net_spin_abs_muB", "Net metal-pair magnetic moment magnitude", "µB", r"|m_s+m_p|", "Magnitude of the sum of the two signed local metal moments.")
    add("metal_pair_spin_imbalance_muB", "Metal magnetic moment imbalance", "µB", r"||m_s|-|m_p||", "Difference between the magnitudes of the two local metal moments.")
    add("total_clean_magnetic_moment_abs_muB", "Total clean-structure magnetic moment magnitude", "µB", r"|M_{\mathrm{DFT}}|", "Absolute stored post_opt_rpbe_d4_total_magmom; a whole-system DFT quantity, not a sum asserted equal to partitioned atomic moments.")
    add("site_support_spin_product_muB2", "Adsorption metal–support spin product", "µB²", r"m_s\sum_{i\ge2}m_i", "Signed alignment proxy for the metal and the remaining clean support; not an exchange energy.")
    add("metal_pair_charge_dipole_axis_eA", "Metal-pair axial charge dipole", "e Å", r"(q_s-q_p)d_{sp}/2", "Metal-only Bader-charge moment about the metal midpoint, projected toward the adsorption metal.")
    for prefix, index in (("site", "s"), ("partner", "p")):
        label = "Adsorption-site" if prefix == "site" else "Partner-site"
        add(f"{prefix}_heteroatom_net_spin_abs_mean_muB", f"{label} net ligand magnetic moment per atom", "µB", rf"|\sum_{{i\in H_{index}}}m_i|/n_{index}", "Cancellation-aware magnitude of the signed mean ligand moment.")
        add(f"{prefix}_metal_ligand_spin_product_muB2", f"{label} metal–ligand spin product", "µB²", rf"m_{index}\sum_{{i\in H_{index}}}m_i/n_{index}", "Signed collinear metal–ligand alignment proxy; not an exchange energy.")
        add(f"{prefix}_heteroatom_dipole_axis_eA", f"{label} axial ligand charge dipole", "e Å", rf"\boldsymbol\mu_{index}\cdot\mathbf e_{index}", "Signed ligand Bader-charge moment projected along the metal-pair axis away from the other metal.")
        add(f"{prefix}_heteroatom_dipole_transverse_eA", f"{label} transverse ligand charge dipole", "e Å", rf"\|\boldsymbol\mu_{index}-(\boldsymbol\mu_{index}\cdot\mathbf e_{index})\mathbf e_{index}\|", "Magnitude of the ligand charge moment perpendicular to the metal-pair axis.")
        add(f"{prefix}_ligand_quadrupole_norm_eA2", f"{label} ligand charge quadrupole magnitude", "e Å²", rf"\sqrt{{\sum_{{a,b}}(Q_{{{index},ab}})^2}}", "Frobenius norm of the traceless Bader-charge quadrupole tensor about this metal.")
        add(f"{prefix}_ligand_quadrupole_axis_eA2", f"{label} axial ligand charge quadrupole", "e Å²", rf"\mathbf e_{index}^\mathsf T Q_{index}\mathbf e_{index}", "Quadrupole tensor projected along the metal-pair axis.")
    if populations:
        for prefix,index in (("site","s"),("partner","p")):
            label="Adsorption metal" if prefix=="site" else "Partner metal"
            add(f"{prefix}_bader_electron_population", f"{label} Bader electron population", "electrons", rf"N_{index}^{{\mathrm{{Bader}}}}", "Stored DFT Bader electron population from data.bader_electrons, including the core convention of the source calculation.")
            add(f"{prefix}_ligand_bader_electron_mean", f"{label} mean ligand Bader electron population", "electrons", rf"\sum_{{i\in H_{index}}}N_i^{{\mathrm{{Bader}}}}/n_{index}", "Mean stored Bader electron population of selected N/O/S ligands.")
    return out


def compute(source, site):
    z = np.asarray(json.loads(source["array.numbers"]), dtype=int)
    xyz = np.asarray(json.loads(source["array.positions"]), dtype=float).reshape(-1, 3)
    q = np.asarray(json.loads(source["data.bader_charges"]), dtype=float)
    electrons = np.asarray(json.loads(source["data.bader_electrons"]), dtype=float)
    m = np.asarray(json.loads(source["data.post_opt_rpbe_d4_magmoms"]), dtype=float)
    if int(source["pbc"]) != 0 or any(len(a) != len(z) for a in (xyz, q, m)):
        raise ValueError(f"invalid clean arrays for {source['name']}")
    partner = 1-site
    distance = float(np.linalg.norm(xyz[site]-xyz[partner]))
    total = source.get("post_opt_rpbe_d4_total_magmom", "")
    result = dict(metal_pair_net_spin_abs_muB=float(abs(m[0]+m[1])),
        metal_pair_spin_imbalance_muB=float(abs(abs(m[0])-abs(m[1]))),
        total_clean_magnetic_moment_abs_muB=abs(float(total)) if total else math.nan,
        site_support_spin_product_muB2=float(m[site]*m[2:].sum()),
        metal_pair_charge_dipole_axis_eA=float((q[site]-q[partner])*distance/2))
    for prefix, metal in (("site", site), ("partner", partner)):
        d = np.linalg.norm(xyz-xyz[metal],axis=1)
        ids = [i for i in range(2,len(z)) if z[i] in (7,8,16) and d[i] <= 2.30]
        u = xyz[ids]-xyz[metal]
        axis = (xyz[metal]-xyz[1-metal])/distance
        mu = (q[ids,None]*u).sum(axis=0)
        tensor = sum((q[i]*(3*np.outer(v,v)-np.dot(v,v)*np.eye(3)) for i,v in zip(ids,u)),start=np.zeros((3,3)))
        moment = float(np.mean(m[ids])) if ids else math.nan
        result[f"{prefix}_heteroatom_net_spin_abs_mean_muB"] = abs(moment)
        result[f"{prefix}_metal_ligand_spin_product_muB2"] = float(m[metal]*moment)
        result[f"{prefix}_heteroatom_dipole_axis_eA"] = float(mu@axis)
        result[f"{prefix}_heteroatom_dipole_transverse_eA"] = float(np.linalg.norm(mu-(mu@axis)*axis))
        result[f"{prefix}_ligand_quadrupole_norm_eA2"] = float(np.linalg.norm(tensor))
        result[f"{prefix}_ligand_quadrupole_axis_eA2"] = float(axis@tensor@axis)
        result[f"{prefix}_bader_electron_population"] = float(electrons[metal])
        result[f"{prefix}_ligand_bader_electron_mean"] = float(electrons[ids].mean()) if ids else math.nan
    return result


def augment(pool, definitions, data, populations=False):
    source = HERE.parents[1] / "extracted" / "structures_by_target.csv"
    with source.open(encoding="utf-8-sig", newline="") as stream:
        structures = {row["name"]: row for row in csv.DictReader(stream)}
    extra = catalog(populations)
    cache = {}
    def values(keys):
        rows = []
        for key in keys:
            if key not in cache:
                name, ads_site = key
                cache[key] = compute(structures[name], int(ads_site.replace("metal", ""))-1)
            rows.append([cache[key][f] for f in extra])
        return np.asarray(rows)
    for d in data.values():
        d["x"] = np.column_stack((d["x"], values(d["keys"])))
        d["validation_x"] = np.column_stack((d["validation_x"], values(d["validation_keys"])))
    return [*pool, *extra], {**definitions, **extra}, data
