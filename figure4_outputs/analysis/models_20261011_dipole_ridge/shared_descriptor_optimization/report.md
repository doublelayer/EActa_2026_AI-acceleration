# Shared descriptor replacement and subset search

The fixed cohort contains 50 training structures / 70 sites. The validation membership and geometry exclusions remain fixed. Validation energies are excluded from selection.

The search evaluates 576 common descriptor sets. Metal separation is mandatory. Ligand-charge choices are terminal mean, minimum, or absent; ligand-dipole choices are net magnitude, maximum individual magnitude, or absent. The signed metal spin product is optional. Every combination of the remaining inputs is considered. A pair with absolute training Pearson correlation at least 0.95 is disallowed. Every retained validation input remains within its training range.

In each of three repeats of five outer structure-grouped folds, four inner grouped folds choose the common descriptor set and each target's ridge strength. Candidates must have no higher inner MSE than the reference set for any target; eligible candidates minimize mean target-variance-normalized inner MSE. The final set uses three repeats of four grouped folds on the full training cohort.

## Descriptor-selection procedure scores

| Procedure | OH CV R² | O CV R² | OOH CV R² |
|---|---:|---:|---:|
| Reference fixed inputs | 0.7470 | 0.8467 | 0.6358 |
| Full replacements and optional spin: nested selection | 0.7269 | 0.8379 | 0.6213 |
| Replacements and exhaustive subsets: nested selection | 0.7154 | 0.8105 | 0.6193 |

## Full replacement trials

These scores hold candidate inputs fixed; ridge strengths are selected inside each outer training fold.

| Ligand charge summary | Ligand dipole summary | Signed metal spin product | OH CV R² | O CV R² | OOH CV R² |
|---|---|---|---:|---:|---:|
| Terminal mean | Net magnitude | No | 0.7470 | 0.8467 | 0.6358 |
| Terminal mean | Net magnitude | Yes | 0.7348 | 0.8203 | 0.6337 |
| Terminal mean | Maximum individual magnitude | No | 0.7269 | 0.8228 | 0.6227 |
| Terminal mean | Maximum individual magnitude | Yes | 0.7193 | 0.8129 | 0.6299 |
| Minimum | Net magnitude | No | 0.7379 | 0.8549 | 0.6325 |
| Minimum | Net magnitude | Yes | 0.7143 | 0.8393 | 0.6250 |
| Minimum | Maximum individual magnitude | No | 0.7087 | 0.8193 | 0.6196 |
| Minimum | Maximum individual magnitude | Yes | 0.6914 | 0.8141 | 0.6222 |

Individual candidate CV scores tune ridge strengths inside folds but hold candidate descriptors fixed. They are exploratory comparisons and do not include descriptor-selection error. The nested search scores above include choosing descriptors within each outer fold.

## Final training-selected descriptors

- Partner metal charge (`q_partner`)
- Adsorption metal spin magnitude (`spin_site_abs`)
- Metal separation (`metal_metal_distance_A`)
- Adsorption metal: net ligand dipole magnitude (`site_heteroatom_charge_dipole_proxy_norm_eA`)

Apply to current models: **no**. descriptor-search nested CV R2 improves for every target versus the fixed starting inputs.

## Frozen validation evaluation

The final candidate is chosen before evaluating validation. Validation results do not choose the descriptor set.

| Target | Reference validation R² | Selected candidate validation R² |
|---|---:|---:|
| G_OH | 0.5966 | 0.4298 |
| G_O | 0.8933 | 0.7831 |
| G_OOH | 0.6136 | 0.5681 |

- [Candidate equations, exact descriptor definitions and graphs](selected_candidate_model_summary.md)
- [All candidate CV metrics](candidate_cv_metrics.csv)
- [Candidate descriptor definitions](candidate_descriptors.csv)
- [Nested fold selections](nested_selections.csv)
- [Nested predictions](nested_cv_predictions.csv)

Reproduce the search from the repository root:

```powershell
python article/KongiCats/calculations/models_20261011_dipole_ridge/optimize_shared_descriptors.py
```
