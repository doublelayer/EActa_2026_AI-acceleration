# Current training and validation split

All three targets use the same **50 training structures / 70 sites** and **10 validation structures / 13 sites**.

Eligible sites require finite, raw-DFT-matched OH, O and OOH labels and pass the recorded endpoint/data-quality filters. The split uses optimized clean-structure chemistry, calculated descriptors, and the three target values. After chemistry coverage is selected, deterministic structure swaps improve even spacing of validation observations across the eligible minimum-to-maximum range for G_OH, G_O, and G_OOH. Model residuals and validation prediction scores do not determine membership. Both sites of a structure remain in one partition.

All recorded invalid-geometry exclusions remain excluded from both training and validation. For every eligible site, the selected OH, O and OOH endpoints must have verified mappings and arrays, their nearest adsorbate O must be within 3.0 Angstrom of the intended metal and support, and selected OOH must have O-O separation at most 2.0 Angstrom. If any endpoint fails, that site is excluded from all three targets. OOH checks use the orientation selected for the energy label. See the [selected endpoint geometry checks](selected_endpoint_geometry_checks.csv) and [data-quality exclusion ledger](data_quality_exclusion_ledger.csv).

The 14 structures listed in the [distance exclusion record](relative_distance_exclusions.json) are excluded in full: both sites and all targets. The criterion is selected metal-to-adsorbate-oxygen distance at least 5% above the fixed mean for the same metal and adsorbate (O, OH or OOH). Means and the approved list remain fixed when the split is rebuilt. [Reference means](relative_distance_reference_means.csv) and [flagged endpoints](relative_distance_flagged_endpoints.csv) give the numerical evidence.

## Selection rule

A deterministic greedy selection covers adsorption metals and N/O/S ligand environments first, chooses one structure per metal pair, balances ligand environments, and prefers nearby training examples with the same adsorption metal and ligand environment. It then makes deterministic one-structure swaps that improve normalized target-range spacing while preserving chemistry coverage, unique validation pairs, and descriptor interpolation bounds. Structure names resolve exact ties. The validation budget is ten structures. Every validation pair and environment also occurs in training; singleton pairs remain in training. See [target-value spread diagnostics](validation_target_value_spread.csv).

All validation values of the 8 inputs lie within the training minima and maxima. Metal charges and spin magnitudes additionally lie within training ranges for that same metal and adsorption/partner role. These are coordinatewise range checks; multivariate convex-hull inclusion is not asserted.

Validation covers **6 / 6 metals**, **10 / 19 metal pairs**, and **3 / 3 ligand environments**. Metal pairs represented by only one eligible structure remain in training.

## Validation structures

| Structure | Metal pair | Ligand environment | Eligible sites | Training structures with same pair |
|---|---|---|---|---:|
| `KMC_Co_Co_A2_B1_NNNNOO_q2` | Co-Co | NNNNOO | metal1 | 4 |
| `KMC_Co_Cu_A2_B2_NNNNOO_q2` | Co-Cu | NNNNOO | metal1;metal2 | 2 |
| `KMC_Co_Ni_A2_B2_NNNNNN_q2` | Co-Ni | NNNNNN | metal1;metal2 | 3 |
| `KMC_Cr_Co_A2_B2_NNNNOO_q2` | Co-Cr | NNNNOO | metal1 | 5 |
| `KMC_Cr_Cr_A2_B1_NNNNNN_q2` | Cr-Cr | NNNNNN | metal1 | 4 |
| `KMC_Fe_Ni_A2_B1_NNNNSS_q2` | Fe-Ni | NNNNSS | metal1 | 1 |
| `KMC_Mn_Co_A2_B1_NNNNNN_q2` | Co-Mn | NNNNNN | metal1;metal2 | 4 |
| `KMC_Mn_Mn_A2_B1_NNNNSS_q2` | Mn-Mn | NNNNSS | metal1 | 3 |
| `KMC_Mn_Ni_A2_B1_NNNNOO_q2` | Mn-Ni | NNNNOO | metal1 | 2 |
| `KMC_Ni_Ni_A2_B2_NNNNOO_q2` | Ni-Ni | NNNNOO | metal1 | 1 |

This validation set measures interpolation among represented chemistries, with target ranges deliberately represented in the holdout. Target labels informed membership, so validation metrics are descriptive and are not an unbiased performance estimate. Its deliberate coverage and descriptor-range constraints do not estimate performance on unseen metal pairs or extrapolation, and it is not an untouched external test.

- [Chemistry coverage](chemistry_coverage.csv)
- [Descriptor range checks](descriptor_range_checks.csv)
- [Validation structure details](validation_structures.csv)
- [Selection settings and source hashes](split_config.json)
- [All site memberships](../cohort_membership.csv)

Reproduce the split:

```powershell
python article/KongiCats/calculations/models_20261011_dipole_ridge/select_representative_split.py
```
