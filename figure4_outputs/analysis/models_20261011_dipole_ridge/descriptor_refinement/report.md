# Shared descriptor refinement

Each trial uses the same descriptors for all three targets. Three repeated five-fold structure-grouped evaluations choose ridge strength in four inner folds. Only changes improving every target's mean CV R2 are retained. Selection uses training CV, with validation labels excluded.

| Round | Operation | Removed | Added | Decision | OH CV R2 | O CV R2 | OOH CV R2 |
|---:|---|---|---|---|---:|---:|---:|
| 0 | starting_set |  |  | starting_set | 0.7754 | 0.8655 | 0.6711 |
| 1 | remove | Adsorption metal charge |  | reject | 0.7837 | 0.8648 | 0.6758 |
| 1 | remove | Partner metal charge |  | reject | 0.7799 | 0.8655 | 0.6718 |
| 1 | remove | Adsorption metal spin magnitude |  | reject | 0.7074 | 0.8229 | 0.6448 |
| 1 | remove | Adsorption metal: mean ligand spin magnitude |  | reject | 0.7807 | 0.8527 | 0.6668 |
| 1 | remove | Partner metal: mean ligand spin magnitude |  | reject | 0.7824 | 0.8590 | 0.6696 |
| 1 | remove | Adsorption metal: mean terminal ligand charge |  | reject | 0.7541 | 0.8579 | 0.6765 |
| 1 | remove | Adsorption metal: net ligand dipole magnitude |  | reject | 0.7748 | 0.8437 | 0.6638 |
| 1 | replace | Adsorption metal: mean terminal ligand charge | Adsorption metal: mean terminal ligand charge | reject | 0.7754 | 0.8655 | 0.6711 |
| 1 | replace | Adsorption metal: mean terminal ligand charge | Partner metal: mean terminal ligand charge | reject | 0.7550 | 0.8474 | 0.6773 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: mean ligand dipole magnitude | reject | 0.7694 | 0.8558 | 0.6632 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: minimum ligand dipole magnitude | reject | 0.7703 | 0.8570 | 0.6642 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: maximum ligand dipole magnitude | reject | 0.7715 | 0.8424 | 0.6538 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: spread ligand dipole magnitude | reject | 0.7705 | 0.8575 | 0.6647 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: mean ligand dipole magnitude | reject | 0.7685 | 0.8513 | 0.6601 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: minimum ligand dipole magnitude | reject | 0.7686 | 0.8522 | 0.6604 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: maximum ligand dipole magnitude | reject | 0.7679 | 0.8362 | 0.6422 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: spread ligand dipole magnitude | reject | 0.7689 | 0.8528 | 0.6606 |
| 1 | add |  | Signed metal spin product | reject | 0.7719 | 0.8541 | 0.6704 |
| 1 | add |  | Mean ligand angle at adsorption metal | reject | 0.7593 | 0.8605 | 0.6687 |
| 1 | add |  | Spread of ligand angle at adsorption metal | reject | 0.7577 | 0.8610 | 0.6658 |
| 1 | add |  | Smallest ligand angle at adsorption metal | reject | 0.7727 | 0.8653 | 0.6733 |
| 1 | add |  | Largest ligand angle at adsorption metal | reject | 0.7594 | 0.8605 | 0.6689 |
| 1 | add |  | Mean ligand angle at partner metal | reject | 0.7670 | 0.8618 | 0.6652 |
| 1 | add |  | Spread of ligand angle at partner metal | reject | 0.7667 | 0.8617 | 0.6669 |
| 1 | add |  | Largest ligand angle at partner metal | reject | 0.7670 | 0.8618 | 0.6652 |
| 1 | add |  | Spread of metal-bridge-metal angles | reject | 0.6196 | 0.7061 | 0.5453 |

The scores are conditional on this descriptor search. Current production metrics are in [model_metrics.csv](../shared_descriptor_search/model_metrics.csv).

[Trial predictions](trial_cv_predictions.csv)
