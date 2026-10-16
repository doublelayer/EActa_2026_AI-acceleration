# Sequential descriptor-addition trials

These descriptor-selection trials used 81 OH/O sites (56 structures) and 70 OOH sites (49 structures). Current model evaluation uses the separately documented representative split; current metrics are in [model_metrics.csv](../shared_descriptor_search/model_metrics.csv). The correlation ranking used for these trials is preserved in [source_correlations.csv](source_correlations.csv).

Candidates are ranked by their mean absolute Pearson correlation with OH, O and OOH on the common training cohort. Each trial adds one descriptor to all three linear ridge models. A descriptor is kept only if the mean repeated grouped CV R2 increases for every target. Alpha is selected within each outer training fold. Validation energies do not determine candidate ranking, trial acceptance or stopping.

A candidate is skipped if its summary family is represented or its absolute correlation with an existing input is at least 0.95. Existing adsorption/partner metal pairs are retained. Signed metal spin product is a pair alignment quantity distinct from the individual spin magnitudes.

These trial scores are used for descriptor selection and are selection conditional; they are not an independent estimate of the entire selection procedure.

| Stage | Candidate | Decision | OH CV R2 | O CV R2 | OOH CV R2 |
|---:|---|---|---:|---:|---:|
| 0 | Starting seven descriptors | starting_set | 0.7311 | 0.8429 | 0.7741 |
| 1 | Adsorption metal: minimum ligand charge | keep | 0.7616 | 0.8524 | 0.7943 |
| 2 | Adsorption metal: maximum ligand dipole magnitude | reject_not_improved_for_every_target | 0.7562 | 0.8493 | 0.7882 |
| 2 | Signed metal spin product | reject_not_improved_for_every_target | 0.7591 | 0.8509 | 0.7904 |
| 2 | Net support spin | reject_not_improved_for_every_target | 0.7564 | 0.8464 | 0.7900 |
| 2 | Partner metal: maximum ligand dipole magnitude | reject_not_improved_for_every_target | 0.7527 | 0.8497 | 0.7892 |
| 2 | Adsorption metal: mean ligand dipole magnitude | reject_not_improved_for_every_target | 0.7576 | 0.8540 | 0.7869 |
| 2 | Second-shell N/O/S density near 3.6 Angstrom | reject_not_improved_for_every_target | 0.7510 | 0.8497 | 0.7845 |
| 2 | Smallest ligand angle at partner metal | reject_not_improved_for_every_target | 0.7766 | 0.8558 | 0.7942 |
| 2 | Total support spin magnitude | reject_not_improved_for_every_target | 0.7614 | 0.8502 | 0.8043 |
| 2 | Spread of metal-bridge-metal angles | reject_not_improved_for_every_target | 0.5425 | 0.7685 | 0.5202 |
| 2 | Partner metal: mean ligand dipole magnitude | reject_not_improved_for_every_target | 0.7578 | 0.8523 | 0.7876 |
| 2 | Adsorption metal: minimum ligand dipole magnitude | reject_not_improved_for_every_target | 0.7578 | 0.8544 | 0.7876 |
| 2 | Second-shell N/O/S density near 2.8 Angstrom | reject_not_improved_for_every_target | 0.6553 | 0.7434 | 0.6726 |
| 2 | Partner metal: minimum ligand dipole magnitude | reject_not_improved_for_every_target | 0.7583 | 0.8522 | 0.7877 |
| 2 | Smallest ligand angle at adsorption metal | reject_not_improved_for_every_target | 0.7578 | 0.8491 | 0.7863 |
| 2 | Metal displacement from ligand plane | reject_not_improved_for_every_target | -7.1778 | -3.5491 | -6.4350 |
| 2 | Mean ligand angle at partner metal | reject_not_improved_for_every_target | 0.7666 | 0.8555 | 0.7941 |
| 2 | Largest ligand angle at partner metal | reject_not_improved_for_every_target | 0.7683 | 0.8554 | 0.7940 |
| 2 | Adsorption metal: net ligand dipole magnitude | keep | 0.7624 | 0.8650 | 0.8083 |

Accepted additions: 2.

- [Candidate-family and similarity checks](candidate_eligibility.csv)
- [Trial scores and per-target changes](trial_results.csv)
- [Per-site held-out predictions for every evaluated trial](trial_cv_predictions.csv)
