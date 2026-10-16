# Shared descriptor refinement

Each trial uses the same descriptors for all three targets. Three repeated five-fold structure-grouped evaluations choose ridge strength in four inner folds. Only changes improving every target's mean CV R2 are retained. Selection uses training CV, with validation labels excluded.

| Round | Operation | Removed | Added | Decision | OH CV R2 | O CV R2 | OOH CV R2 |
|---:|---|---|---|---|---:|---:|---:|
| 0 | starting_set |  |  | starting_set | 0.7744 | 0.8666 | 0.6784 |
| 1 | remove | Adsorption metal charge |  | reject | 0.7770 | 0.8625 | 0.6809 |
| 1 | remove | Partner metal charge |  | reject | 0.7807 | 0.8723 | 0.6777 |
| 1 | remove | Adsorption metal spin magnitude |  | reject | 0.7132 | 0.8267 | 0.6417 |
| 1 | remove | Partner metal spin magnitude |  | eligible_improvement | 0.7819 | 0.8734 | 0.6786 |
| 1 | remove | Adsorption metal: mean ligand spin magnitude |  | reject | 0.7737 | 0.8522 | 0.6712 |
| 1 | remove | Partner metal: mean ligand spin magnitude |  | reject | 0.7735 | 0.8574 | 0.6703 |
| 1 | remove | Adsorption metal: minimum ligand charge |  | reject | 0.7625 | 0.8587 | 0.6905 |
| 1 | remove | Adsorption metal: net ligand dipole magnitude |  | reject | 0.7696 | 0.8554 | 0.6696 |
| 1 | replace | Adsorption metal: minimum ligand charge | Adsorption metal: mean terminal ligand charge | keep | 0.7828 | 0.8699 | 0.6832 |
| 1 | replace | Adsorption metal: minimum ligand charge | Partner metal: mean terminal ligand charge | reject | 0.7625 | 0.8526 | 0.6899 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: mean ligand dipole magnitude | reject | 0.7679 | 0.8564 | 0.6718 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: minimum ligand dipole magnitude | reject | 0.7680 | 0.8571 | 0.6724 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: maximum ligand dipole magnitude | reject | 0.7642 | 0.8539 | 0.6653 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: spread ligand dipole magnitude | reject | 0.7679 | 0.8574 | 0.6727 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: mean ligand dipole magnitude | reject | 0.7660 | 0.8529 | 0.6718 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: minimum ligand dipole magnitude | reject | 0.7663 | 0.8541 | 0.6722 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: maximum ligand dipole magnitude | reject | 0.7646 | 0.8509 | 0.6618 |
| 1 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: spread ligand dipole magnitude | reject | 0.7666 | 0.8552 | 0.6726 |
| 1 | add |  | Signed metal spin product | reject | 0.7708 | 0.8563 | 0.6788 |
| 1 | add |  | Mean ligand angle at adsorption metal | reject | 0.7620 | 0.8570 | 0.6774 |
| 1 | add |  | Spread of ligand angle at adsorption metal | reject | 0.7616 | 0.8569 | 0.6725 |
| 1 | add |  | Smallest ligand angle at adsorption metal | reject | 0.7738 | 0.8650 | 0.6813 |
| 1 | add |  | Largest ligand angle at adsorption metal | reject | 0.7621 | 0.8570 | 0.6776 |
| 1 | add |  | Mean ligand angle at partner metal | reject | 0.7676 | 0.8575 | 0.6746 |
| 1 | add |  | Spread of ligand angle at partner metal | reject | 0.7674 | 0.8579 | 0.6742 |
| 1 | add |  | Smallest ligand angle at partner metal | reject | 0.7787 | 0.8614 | 0.6670 |
| 1 | add |  | Largest ligand angle at partner metal | reject | 0.7677 | 0.8575 | 0.6746 |
| 1 | add |  | Spread of metal-bridge-metal angles | reject | 0.5989 | 0.6998 | 0.5404 |
| 2 | remove | Adsorption metal charge |  | reject | 0.7846 | 0.8680 | 0.6838 |
| 2 | remove | Partner metal charge |  | eligible_improvement | 0.7848 | 0.8712 | 0.6835 |
| 2 | remove | Adsorption metal spin magnitude |  | reject | 0.7148 | 0.8269 | 0.6553 |
| 2 | remove | Partner metal spin magnitude |  | keep | 0.7861 | 0.8720 | 0.6877 |
| 2 | remove | Adsorption metal: mean ligand spin magnitude |  | reject | 0.7843 | 0.8564 | 0.6793 |
| 2 | remove | Partner metal: mean ligand spin magnitude |  | reject | 0.7904 | 0.8625 | 0.6820 |
| 2 | remove | Adsorption metal: mean terminal ligand charge |  | reject | 0.7625 | 0.8587 | 0.6905 |
| 2 | remove | Adsorption metal: net ligand dipole magnitude |  | reject | 0.7791 | 0.8598 | 0.6789 |
| 2 | replace | Adsorption metal: mean terminal ligand charge | Adsorption metal: mean terminal ligand charge | reject | 0.7828 | 0.8699 | 0.6832 |
| 2 | replace | Adsorption metal: mean terminal ligand charge | Partner metal: mean terminal ligand charge | reject | 0.7625 | 0.8526 | 0.6899 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: mean ligand dipole magnitude | reject | 0.7792 | 0.8624 | 0.6798 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: minimum ligand dipole magnitude | reject | 0.7796 | 0.8633 | 0.6801 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: maximum ligand dipole magnitude | reject | 0.7778 | 0.8567 | 0.6753 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: spread ligand dipole magnitude | reject | 0.7798 | 0.8639 | 0.6805 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: mean ligand dipole magnitude | reject | 0.7775 | 0.8593 | 0.6771 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: minimum ligand dipole magnitude | reject | 0.7779 | 0.8602 | 0.6778 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: maximum ligand dipole magnitude | reject | 0.7740 | 0.8539 | 0.6689 |
| 2 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: spread ligand dipole magnitude | reject | 0.7781 | 0.8610 | 0.6796 |
| 2 | add |  | Signed metal spin product | reject | 0.7788 | 0.8581 | 0.6827 |
| 2 | add |  | Mean ligand angle at adsorption metal | reject | 0.7685 | 0.8600 | 0.6806 |
| 2 | add |  | Spread of ligand angle at adsorption metal | reject | 0.7672 | 0.8603 | 0.6791 |
| 2 | add |  | Smallest ligand angle at adsorption metal | reject | 0.7798 | 0.8650 | 0.6852 |
| 2 | add |  | Largest ligand angle at adsorption metal | reject | 0.7686 | 0.8600 | 0.6808 |
| 2 | add |  | Mean ligand angle at partner metal | reject | 0.7749 | 0.8629 | 0.6823 |
| 2 | add |  | Spread of ligand angle at partner metal | reject | 0.7747 | 0.8628 | 0.6792 |
| 2 | add |  | Smallest ligand angle at partner metal | reject | 0.7813 | 0.8676 | 0.6809 |
| 2 | add |  | Largest ligand angle at partner metal | reject | 0.7749 | 0.8630 | 0.6787 |
| 2 | add |  | Spread of metal-bridge-metal angles | reject | 0.6132 | 0.7031 | 0.5478 |
| 3 | remove | Adsorption metal charge |  | reject | 0.7941 | 0.8707 | 0.6894 |
| 3 | remove | Partner metal charge |  | reject | 0.7901 | 0.8720 | 0.6848 |
| 3 | remove | Adsorption metal spin magnitude |  | reject | 0.7212 | 0.8315 | 0.6601 |
| 3 | remove | Adsorption metal: mean ligand spin magnitude |  | reject | 0.7908 | 0.8592 | 0.6818 |
| 3 | remove | Partner metal: mean ligand spin magnitude |  | reject | 0.7925 | 0.8666 | 0.6837 |
| 3 | remove | Adsorption metal: mean terminal ligand charge |  | reject | 0.7661 | 0.8648 | 0.6933 |
| 3 | remove | Adsorption metal: net ligand dipole magnitude |  | reject | 0.7844 | 0.8502 | 0.6780 |
| 3 | replace | Adsorption metal: mean terminal ligand charge | Adsorption metal: mean terminal ligand charge | reject | 0.7861 | 0.8720 | 0.6877 |
| 3 | replace | Adsorption metal: mean terminal ligand charge | Partner metal: mean terminal ligand charge | reject | 0.7662 | 0.8546 | 0.6911 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: mean ligand dipole magnitude | reject | 0.7815 | 0.8642 | 0.6784 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: minimum ligand dipole magnitude | reject | 0.7824 | 0.8656 | 0.6795 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: maximum ligand dipole magnitude | reject | 0.7808 | 0.8490 | 0.6716 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Adsorption metal: spread ligand dipole magnitude | reject | 0.7828 | 0.8662 | 0.6796 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: mean ligand dipole magnitude | reject | 0.7809 | 0.8613 | 0.6751 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: minimum ligand dipole magnitude | reject | 0.7811 | 0.8607 | 0.6754 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: maximum ligand dipole magnitude | reject | 0.7797 | 0.8457 | 0.6627 |
| 3 | replace | Adsorption metal: net ligand dipole magnitude | Partner metal: spread ligand dipole magnitude | reject | 0.7811 | 0.8613 | 0.6756 |
| 3 | add |  | Signed metal spin product | reject | 0.7820 | 0.8610 | 0.6840 |
| 3 | add |  | Mean ligand angle at adsorption metal | reject | 0.7714 | 0.8672 | 0.6823 |
| 3 | add |  | Spread of ligand angle at adsorption metal | reject | 0.7700 | 0.8640 | 0.6797 |
| 3 | add |  | Smallest ligand angle at adsorption metal | reject | 0.7826 | 0.8722 | 0.6890 |
| 3 | add |  | Largest ligand angle at adsorption metal | reject | 0.7715 | 0.8672 | 0.6825 |
| 3 | add |  | Mean ligand angle at partner metal | reject | 0.7777 | 0.8684 | 0.6803 |
| 3 | add |  | Spread of ligand angle at partner metal | reject | 0.7776 | 0.8682 | 0.6808 |
| 3 | add |  | Smallest ligand angle at partner metal | reject | 0.7846 | 0.8699 | 0.6830 |
| 3 | add |  | Largest ligand angle at partner metal | reject | 0.7778 | 0.8684 | 0.6803 |
| 3 | add |  | Spread of metal-bridge-metal angles | reject | 0.6172 | 0.7050 | 0.5481 |

The scores are conditional on this descriptor search. Current production metrics are in [model_metrics.csv](../shared_descriptor_search/model_metrics.csv).

[Trial predictions](trial_cv_predictions.csv)
