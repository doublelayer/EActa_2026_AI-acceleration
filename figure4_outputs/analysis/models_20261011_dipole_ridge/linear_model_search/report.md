# Target specific linear model search

Searches OLS and ridge regressions on calculated clean-structure descriptors. Candidate feature count (1–12), feature ranking, and ridge strength are selected using structure-grouped CV within each training partition. The feature ranking uses absolute training-only Pearson correlation. The intercept is unpenalized; missing predictors use training medians and predictors are standardized from training rows only. No kernel or tree model is included.

Training and validation membership come from the saved `cv_predictions.csv` and `validation_predictions.csv` for the three dipole models. Their inherited outlier and geometry exclusions are left unchanged; validation labels do not select descriptors or hyperparameters in this search. The OH/O models inherit training-only OOF pruning of `KMC_Mn_Mn_A2_B1_NNNNNN_q2`, `KMC_Mn_Co_A2_B1_NNNNNN_q2`, and `KMC_Cr_Cr_A2_B2_NNNNOO_q2`. OOH inherits a separate ten-structure pruning path recorded in `../models_20261008_linear_ridge_v2/ooh_focused_best_model_set.json`; its selected pruning count was chosen after examining validation. OOH validation performance is therefore selection-influenced. The independent search results for other cohort files in this directory are not used here.

## Results

| Target | Training R² | Mean repeated grouped R²cv | Pooled OOF R² | Validation R² | Predictors | Alpha | Training rows / structures |
|---|---:|---:|---:|---:|---:|---:|---|
| G_OH | 0.922 | 0.898 | 0.898 | 0.938 | 8 | 0.1 | 81 / 56 |
| G_O | 0.937 | 0.904 | 0.904 | 0.958 | 8 | 1 | 81 / 56 |
| G_OOH | 0.873 | 0.833 | 0.833 | 0.878 | 6 | 1 | 70 / 49 |

A target meets the stated training and CV goal only when both `training_R2` and `mean_repeat_R2cv` exceed 0.90. Validation R² is reported as a final check, not used for model selection. `nested_cv_predictions.csv` contains outer held-out predictions from the feature/alpha selection process; `outer_fold_selections.csv` records each outer-fold equation. `inner_search_scores.csv` contains selection scores. The final descriptor list and performance are in `metrics.csv`.

Feature candidates are numeric descriptors calculated from clean catalyst coordinates, Bader charges, and magnetic moments. Element-property lookup fields, categorical metal labels, ligand counts, and adsorption-state descriptors are excluded. N/O/S neighbor summaries remain pooled. Existing target cohorts differ where the saved model cohorts differ. `final_model_parameters.csv` stores the standardized coefficients and training-only imputation/scaling values for each final equation.
