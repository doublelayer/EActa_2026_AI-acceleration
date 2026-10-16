# 20261015 model data extractor

Run these commands from this (`descriptors`) folder to extract the unsplit all-structures dataset:

```powershell
python .\extract_model_dataset.py
```

This reads the bare, O, OH, OOHx, and OOHz databases from the parent folder and writes `model_all_structures_data.csv` here. The output has no `split` column. It includes one row per available target and catalyst/site pair and exports all eight descriptors for every target. A descriptor cell is blank only if it is undefined for that structure; the target row is retained. Target-energy references and descriptor formulas are defined in the extractor. Use `--output .\filename.csv` to write the extracted CSV to another file in this folder, or `--output ..\filename.csv` to write it in the parent folder.

The target calculation follows cell 10 of `Leite_2026_DACS_ORR_ML_scaling_relation_figure_3_markers_v11.ipynb`. The notebook uses `E_H2 = -6.73 eV` and `E_H2O = -13.97 eV` to calculate electronic adsorption energies, then adds the listed thermochemical and solvation corrections to obtain `G_X`. The 20261015 databases contain raw total energies rather than precomputed `E_ads_*` fields, so the extractor calculates both stages directly. It selects the lower-energy OOH orientation before calculating `G_OOH`. `U_EQ = 1.23 V` and `ORR_FREE_ENERGY = 4.92 eV` are used later for CHE pathway analysis.

The all-structures output currently has 416 target rows across 148 distinct catalyst/site pairs: 136 `G_OH`, 134 `G_O`, and 146 `G_OOH` rows. Target availability differs by database, so not every pair has all three targets.

To assign train/validation splits from `model_all_structures_data.csv`, run this from the same folder:

```powershell
python .\create_all_structures_split.py
```

The script creates assignments from scratch using only `model_all_structures_data.csv`. It samples about one sixth of catalysts with all three targets into validation using the fixed seed `20261015`; all other catalysts go to training. Every target and site row for a catalyst shares its assignment. For the current 88 catalysts this gives 73 training and 15 validation catalysts. It writes `model_all_structures_training_data.csv` (all target rows with a `split` column), `model_all_structures_split.csv` (one row per catalyst, including target availability), and separate target files: `model_G_O_training_data.csv`, `model_G_OH_training_data.csv`, and `model_G_OOH_training_data.csv`. Each target file retains its `split` column. Rebuilding the split can change assignments, so rerun the model-building step afterward to refresh model results.

The electronic adsorption-energy reference offsets are:

- `E_ads_OH = E_total(OH*) - E_total(clean) + 10.605 eV`
- `E_ads_O = E_total(O*) - E_total(clean) + 7.24 eV`
- `E_ads_OOH = E_total(OOH*) - E_total(clean) + 17.845 eV`

Then the notebook adds net corrections of `+0.05 eV` for OH, `+0.05 eV` for O, and `+0.10 eV` for OOH, giving the model targets:

- `G_OH = E_ads_OH + 0.05 eV`
- `G_O = E_ads_O + 0.05 eV`
- `G_OOH = E_ads_OOH + 0.10 eV`

For each OOH site, the lower total energy from the available x and z records is used; exact ties select x.
