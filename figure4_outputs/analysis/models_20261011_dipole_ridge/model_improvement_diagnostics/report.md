# Current model error diagnostics

Repeated structure-grouped CV predictions are pooled across three repeats. Cohort counts refer to unique site rows; RMSE and subgroup R? use all three repeated predictions.

| Target | Ligand environment | Sites | RMSE (eV) | Fraction of target squared error |
|---|---|---:|---:|---:|
| G_O | NNNNNN | 14 | 0.627 | 46.9% |
| G_O | NNNNOO | 22 | 0.346 | 22.4% |
| G_O | NNNNSS | 34 | 0.325 | 30.6% |
| G_OH | NNNNNN | 14 | 0.426 | 41.0% |
| G_OH | NNNNOO | 22 | 0.294 | 30.6% |
| G_OH | NNNNSS | 34 | 0.228 | 28.4% |
| G_OOH | NNNNNN | 14 | 0.397 | 46.3% |
| G_OOH | NNNNOO | 22 | 0.224 | 23.1% |
| G_OOH | NNNNSS | 34 | 0.208 | 30.7% |

[Grouped CV predictions](../shared_descriptor_search/nested_cv_predictions.csv); [full environment errors](environment_cv_errors.csv).
