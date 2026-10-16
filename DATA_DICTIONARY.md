# Data dictionary

For the DFT data accompanying *“Accelerating Catalyst Discovery with Artificial Intelligence Using Molecular Dual-Atom Site Catalysts as a Case Study.”*

These datasets use the Atomic Simulation Environment (ASE) format. Structure and calculator properties are stored in standard ASE fields; searchable scalar metadata are key–value pairs (KVPs); and custom per-atom arrays are stored in `row.data`.

## Dataset organization

| Collection | Structures represented |
| --- | --- |
| `DASC_Bare_Catalysts_RPBE_D4` | **1,348** optimized bare molecular dual-atom site catalysts |
| `DASC_O_Adsorption_RPBE_D4` | Optimized O-adsorption states |
| `DASC_OH_Adsorption_RPBE_D4` | Optimized OH-adsorption states |
| `DASC_OOHx_Adsorption_RPBE_D4` | Optimized OOH adsorption states from initial orientations parallel to the catalyst *xy* plane |
| `DASC_OOHz_Adsorption_RPBE_D4` | Optimized OOH adsorption states from initial orientations perpendicular to the catalyst *xy* plane |

Adsorption calculations were attempted for selected subsets of the bare catalysts to generate training and validation data for the O, OH, and OOH adsorption-energy models. The adsorption databases only contain the successfully optimized configurations. So the numbers of available records vary among intermediates and adsorption sites. The model-role fields described below record actual use in the final machine learning (ML) workflow.

These **five separate databases** are each published in ASE SQLite (`.db`) and ASE JSON (`.json`) representations of the same records.

## Key–value pairs

| Key | Collection | Definition |
| --- | --- | --- |
| `name` | All | Identifier of the stored structure; includes the adsorption configuration for adsorbate records |
| `catalyst_name` | Adsorption | Identifier of the corresponding bare catalyst; links to `name` in the bare collection |
| `metal1`, `metal2` | All | Ordered metal sites, each Cr, Mn, Fe, Co, Ni, or Cu |
| `acid` | All | Dialdehyde/acid-fragment code (e.g., `A2`); molecular components are described in the related parent dataset |
| `base` | All | Diamine/base-fragment code; `B1` = 1,2-phenylenediamine and `B2` = 1,8-naphthalenediamine |
| `bridge` | All | Code for N/O/S bridge composition (e.g., `NN`, `OO`, or `SS`) |
| `total_charge` | All | Net molecular charge, in units of elementary charge; `2` corresponds to +2 |
| `adsorbate` | Adsorption | Adsorption intermediate: O, OH, or OOH |
| `ads_site` | Adsorption | Metal adsorption center, `metal1` or `metal2` |
| `O_model_role` | Bare | Actual usage in the O adsorption energy ML model |
| `OH_model_role` | Bare | Actual usage in the OH adsorption energy ML model |
| `OOH_model_role` | Bare | Actual usage in the OOH adsorption energy ML model |

### Model-role values

Each of `O_model_role`, `OH_model_role`, and `OOH_model_role` takes one of these lowercase values:

| Value | Meaning |
| --- | --- |
| `training` | Actually used to fit the corresponding ML model |
| `validation` | Actually used to validate the corresponding ML model |
| `prediction` | Actually used as a prediction/screening input for the corresponding ML model |

The values reflect **actual model usage**, rather than an intended or predefined split. They are independent across the three models: for example, a catalyst can have `training` for O, `validation` for OH, and `prediction` for OOH.

### Adsorption configurations and orientations

O, OH, and OOH may be adsorbed at either of the two metal sites. Two orientations were used when constructing initial OOH adsorption geometries:

| Label | Initial O–O bond orientation |
| --- | --- |
| **OOHx** | **Parallel** to the catalyst *xy* plane |
| **OOHz** | **Perpendicular** to the catalyst *xy* plane |

OOHx and OOHz describe different initial placements of the same OOH intermediate; the final O–O bond orientation is determined by geometry optimization.

### Identifier example

```text
Bare catalyst:
  name          = KMC_Co_Co_A2_B1_NNNNOO_q2

O-adsorption structure:
  name          = KMC_Co_Co_A2_B1_NNNNOO_q2_O_metal1
  catalyst_name = KMC_Co_Co_A2_B1_NNNNOO_q2
  adsorbate     = O
  ads_site      = metal1
```

Join an adsorption record's `catalyst_name` to a bare record's `name`. `name` is the structure identifier; ASE's numeric `id` is specific to a database file.

## Standard ASE properties

| Field | Meaning and unit |
| --- | --- |
| Atomic symbols and positions | Chemical elements and Cartesian coordinates, Å |
| Cell and periodic-boundary flags | Simulation-cell vectors in Å and PBC settings |
| Constraints | Atomic constraints stored with each structure |
| `energy` | Final electronic total energy of the optimized structure, eV |
| `fmax` | Maximum residual atomic force at the end of optimization, eV Å⁻¹ |
| `mass` | Total atomic mass, u |
| `id` | Database-local row number |
| `ctime` | Database record creation time |

The `energy` field supplies the total-energy input from which adsorption energetics can be calculated using the corresponding clean and adsorbed catalyst energies and the reference conventions described in the associated work. The `fmax` KVP records the final optimization force criterion.

## Custom atom-resolved data

| Entry in `row.data` | Meaning | Unit |
| --- | --- | --- |
| `bader_charges` | Per-atom net Bader charges; a positive value indicates electron depletion | e |
| `post_opt_rpbe_d4_magmoms` | Per-atom signed magnetic moments from the optimized RPBE-D4 structure | μB |

Arrays follow the stored atomic order. This ordering permits site-resolved descriptors of the two metal atoms and the ligand/adsorbate atoms.

## Computational methods

Spin-polarized RPBE calculations were performed with **GPAW v24.6** in plane-wave mode and the D4 dispersion correction (`dftd4` **v3.6.0**) applied through the ASE `SumCalculator`.

| Parameter | Setting |
| --- | --- |
| Plane-wave cutoff | 550 eV |
| Grid spacing | 0.15 Å |
| Vacuum | 6.00 Å on every side |
| Optimization criterion | Maximum force below 0.05 eV Å⁻¹ |
