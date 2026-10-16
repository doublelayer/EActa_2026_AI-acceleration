# 20261015 models

Run from the parent folder containing `models` and `descriptors`:

```powershell
python models\build_models.py
```

By default, the builder reads `descriptors/model_all_structures_training_data.csv` and `descriptors/model_all_structures_split.csv`. Its target-specific predictor lists come from the non-intercept terms in `../../notebook/model_inputs/final_model_parameters.csv` (relative to this `models` folder). It refits all coefficients and selects new ridge strengths using the 20261015 training data. To use a different feature reference, pass `--feature-reference <csv>`.

For each target, ridge alpha is selected from `0` and `10^-4` through `10^4` in half-decade steps. Selection minimizes mean RMSE over three repeats of five-fold cross-validation grouped by catalyst name. The fixed validation split is excluded from predictor and alpha selection and is used for final evaluation. Missing predictor values are imputed with training-row medians; scaling and coefficients are fitted on training rows only.

The reference contains 8 predictors for G_OH, 8 for G_O, and 6 for G_OOH. The builder checks that every referenced predictor exists in the descriptor input. It writes `alpha_selection.csv`, `final_model_parameters.csv`, `model_metrics.csv`, `predictions.csv`, `validation_predictions.csv`, `cv_predictions.csv`, `model_bundle.json`, and `run_config.json` beside this README. Input paths in the run configuration are relative to this `models` folder; it also records the feature reference, selected predictors, alpha grid, and CV settings.

Generate training-versus-validation observed/predicted plots with:

```powershell
python models\plot_training_validation_regressions.py
```

The script writes one combined plot and one two-panel plot per target into `models/regression_plots/`.

## Current results

| Target | Training sites | Validation sites | Predictors | Alpha | Training CV RMSE (eV) | Validation R2 | Validation RMSE (eV) | Validation MAE (eV) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| G_OH | 112 | 24 | 8 | 0 | 0.246 | 0.875 | 0.195 | 0.156 |
| G_O | 111 | 23 | 8 | 10 | 0.798 | 0.815 | 0.424 | 0.332 |
| G_OOH | 121 | 25 | 6 | 10 | 0.315 | 0.575 | 0.256 | 0.213 |

Training CV RMSE is the alpha-selection score; validation rows are excluded from that selection. Alpha `0` is the unregularized least-squares endpoint of the search grid.

