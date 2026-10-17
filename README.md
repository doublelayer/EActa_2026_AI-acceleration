# DFT Data for “Accelerating Catalyst Discovery with Artificial Intelligence Using Molecular Dual-Atom Site Catalysts as a Case Study”

## Authors and contact

Bruno Inácio da Silva Roux Leite¹; Denis Savchenko¹; Timmo-Henrik Pukk¹; Ba Long Nguyen¹; Vladislav Ivanistsev²; Nadezda Kongi¹.

1. Institute of Chemistry, University of Tartu, Ravila 14a, 50411 Tartu, Estonia.
2. Department of Chemistry, University of Latvia, Jelgavas iela 1, Riga, LV-1004, Latvia.

Correspondence: vladislav.ivanistsev@lu.lv; nadezda.kongi@ut.ee.

## Overview

This release provides density functional theory (DFT) data underlying the study of oxygen reduction reaction (ORR) intermediates on molecular dual-atom site catalysts (DASCs). It contains **1,348 optimized bare catalyst structures** and optimized adsorption configurations for O, OH, and OOH. Adsorption calculations were attempted for a subset of catalysts initially selected to generate data for training and validating the corresponding machine learning (ML) models, rather than for the entire bare catalyst collection. The release includes atomic coordinates, electronic total energies, structural metadata, and atom-resolved Bader charges and magnetic moments where available.

The adsorption databases only contain successfully optimized configurations from these attempts. So record counts can differ among intermediates and adsorption sites.

The catalysts contain two metal centers chosen from Cr, Mn, Fe, Co, Ni, and Cu, N/O/S bridge atoms, and molecular ligand fragments identified by `acid` and `base` codes. The molecular-component definitions are provided in the related parent dataset: https://doi.org/10.5281/zenodo.18601379.

## Dataset contents

The dataset contains **five distinct structure databases**, each supplied in Atomic Simulation Environment (ASE) SQLite (`.db`) and corresponding ASE JSON (`.json`) format:

| Collection | Contents |
| --- | --- |
| `DASC_Bare_Catalysts_RPBE_D4` | 1,348 optimized bare catalysts, total energies, composition metadata, available atomic charge/moment data, and model-specific roles |
| `DASC_O_Adsorption_RPBE_D4` | Optimized O-adsorption configurations and associated data |
| `DASC_OH_Adsorption_RPBE_D4` | Optimized OH-adsorption configurations and associated data |
| `DASC_OOHx_Adsorption_RPBE_D4` | Optimized OOH configurations originating from O–O bonds placed parallel to the catalyst *xy* plane and associated data |
| `DASC_OOHz_Adsorption_RPBE_D4` | Optimized OOH configurations originating from O–O bonds placed perpendicular to the catalyst *xy* plane and associated data |

The OOHx and OOHz labels refer to the initial O–O bond orientations; the final orientations are determined by geometry optimization.

For each of the five databases, the `.db` and `.json` files are **equivalent representations** of the same structure records. The exact number of adsorption records is available from the published databases. See `DATA_DICTIONARY.md` for metadata definitions, units, and naming conventions.

## Structure identifiers

The `name` field identifies an individual structure. For bare catalysts, it is the catalyst identifier; in adsorption records, it identifies a specific adsorbed configuration. The `catalyst_name` field in adsorption records links to `name` in the bare catalyst collection. `ads_site` identifies the occupied metal site (`metal1` or `metal2`), and `adsorbate` identifies the O, OH, or OOH intermediate.

Example:

```text
Bare catalyst:
  name          = KMC_Co_Co_A2_B1_NNNNOO_q2

O-adsorption configuration:
  name          = KMC_Co_Co_A2_B1_NNNNOO_q2_O_metal1
  catalyst_name = KMC_Co_Co_A2_B1_NNNNOO_q2
  adsorbate     = O
  ads_site      = metal1
```

Use the structure names to associate adsorption records with their bare catalysts; numeric ASE row IDs are local to each file.

## Model assignments

Each bare catalyst record has three independent model-role fields:

| Key | Adsorption-energy model | Values |
| --- | --- | --- |
| `O_model_role` | O | `training`, `validation`, `prediction` |
| `OH_model_role` | OH | `training`, `validation`, `prediction` |
| `OOH_model_role` | OOH | `training`, `validation`, `prediction` |

These fields record **actual usage in the completed ML workflow**, not the original selection of catalysts for adsorption calculations. `training` identifies catalysts used to fit the corresponding model, `validation` identifies those used to validate it, and `prediction` identifies those used as inputs for ML-based screening. The three roles are assigned independently for O, OH, and OOH, so a catalyst can have **different roles in different models**.

## DFT calculation settings

Spin-polarized RPBE calculations were performed with **GPAW v24.6** in plane-wave mode. The D4 dispersion correction was applied using **`dftd4` v3.6.0** through the ASE **`SumCalculator`**. The plane-wave cutoff was **550 eV**, the grid spacing was **0.15 Å**, and **6.00 Å of vacuum was added on every side**. Geometry optimization proceeded until the maximum force was below **0.05 eV Å⁻¹**.

Electronic total energies are recorded in the standard ASE `energy` field in eV. `total_charge` gives the net system charge, and the available per-atom Bader charges and magnetic moments are stored in `row.data`. The associated study uses the clean and adsorbed total energies to derive adsorption energetics and ORR thermodynamic quantities.

## Reading and reusing the data

The corresponding ASE JSON exports provide the same structures and metadata. The files can be read using ASE:

```python
from ase.db import connect

bare = connect("DASC_Bare_Catalysts_RPBE_D4.db")
print("Bare catalyst records:", bare.count())

for row in bare.select(O_model_role="training"):
    atoms = row.toatoms()
    print(row.name, row.energy, row.O_model_role)
    break
```

## Citation and related data

Associated manuscript: *Accelerating Catalyst Discovery with Artificial Intelligence Using Molecular Dual-Atom Site Catalysts as a Case Study* (publication DOI to be added when available).

Parent molecular structure dataset: B. L. Nguyen, T. K. Madsen, V. Ivanistsev, and N. Kongi, *Dataset of Molecular Dual-Atom Site Complexes for Catalysis*, *Data in Brief* **66** (2026) 112806. Article: https://doi.org/10.1016/j.dib.2026.112806; dataset: https://doi.org/10.5281/zenodo.18601379.

Please cite the Zenodo release DOI when using these data and the related research article when available. The license is specified in the Zenodo record.

## Article generation and review

The manuscript's versioning, DOCX review, comment extraction, and archive-update workflow is documented in [ARTICLE_GENERATION_PIPELINE.md](ARTICLE_GENERATION_PIPELINE.md). The operative package instructions remain in `one_prompt_article_v1/PROMPT.txt` and `one_prompt_article_v1/AGENTS.md`.
