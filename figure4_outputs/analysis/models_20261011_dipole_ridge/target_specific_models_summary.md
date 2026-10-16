# Local dipole descriptors: selected-cohort ridge comparison

Both fitted variants exclude all empirical element-property lookup descriptors. `site_electronegativity_Pauling` and `partner_electronegativity_Pauling` are removed from the model inputs, preprocessing and coefficients. The dipole models use 39 predictors for G_OH/G_O and 23 for G_OOH, derived from calculated clean-structure charges, magnetic moments and atomic coordinates. Element atomic numbers select N/O/S neighbors and identify the two metals; they are not predictor columns.

This experiment replaces pooled metal-heteroatom distance mean, population standard deviation, minimum and maximum with the same summaries of local Bader point-charge contribution magnitudes. The two inverse-distance charge sums are removed. Bridge distance asymmetry is replaced with charge-moment contribution asymmetry. Metal-metal distance remains a predictor. Repeated descriptor names are deduplicated in the dipole model.

For each N/O/S neighbor within 2.30 Angstrom, define `mu_i = q_i * (r_i-r_metal)` and `p_i = norm(mu_i) = abs(q_i) * d_i`. Compute mean/std/min/max over `p_i`. The existing net local dipole `norm(sum_i mu_i)` remains included. Units are e Angstrom. The mean of contribution magnitudes differs from the magnitude of their vector sum: the latter includes cancellation between directions.

These are point-charge dipole proxies with the metal as the specified origin. They are translation and rotation invariant under rigid motion of the structure, but remain sensitive to charge partitioning, the local origin and neighbor selection. They are not atom-resolved DFT dipoles or the total molecular dipole. Charge-only representations omit local atomic polarization; see [Veit et al., J. Chem. Phys. 153, 024113 (2020)](https://arxiv.org/abs/2003.12437). There is no assumption that multiplying charge by distance removes all N/O/S differences. The original 2.30 Angstrom shell cutoff remains species sensitive.

## Paired model results

Both variants use the same saved selected-model training sites, fixed validation sites and three repeated five-fold structure-grouped outer partitions. Ridge alpha is selected by four-fold grouped CV within each training partition. Feature sets are fixed to the original final block and its dipole replacement after removing empirical lookup columns from both. The distance baseline is a fresh paired refit, not the historical nested search across descriptor blocks and OLS/ridge families. No additional structures are removed and validation is not used to choose alpha.

| Target | Variant | Predictors | Training structures/sites | Alpha | Mean CV R2 | Validation R2 | CV RMSE (eV) | Validation RMSE (eV) |
|---|---|---:|---|---:|---:|---:|---:|---:|
| G_OH | distance_baseline | 47 | 56/81 | 1 | 0.729 | 0.872 | 0.313 | 0.225 |
| G_OH | dipole | 39 | 56/81 | 1 | 0.625 | 0.893 | 0.368 | 0.205 |
| G_O | distance_baseline | 47 | 56/81 | 0.001 | 0.850 | 0.918 | 0.405 | 0.300 |
| G_O | dipole | 39 | 56/81 | 0.1 | 0.823 | 0.949 | 0.441 | 0.238 |
| G_OOH | distance_baseline | 25 | 49/70 | 1 | 0.796 | 0.845 | 0.192 | 0.161 |
| G_OOH | dipole | 23 | 49/70 | 0.1 | 0.800 | 0.777 | 0.190 | 0.193 |

### Effect of the dipole replacement without empirical descriptors

- G_OH: mean CV R2 changes from 0.729 to 0.625; validation R2 changes from 0.872 to 0.893.
- G_O: mean CV R2 changes from 0.850 to 0.823; validation R2 changes from 0.918 to 0.949.
- G_OOH: mean CV R2 changes from 0.796 to 0.800; validation R2 changes from 0.845 to 0.777.

### Effect of removing empirical descriptors from the dipole models

The prior dipole fits included both Pauling lookup descriptors. The table compares their saved metrics with the current fits using the same cohorts, outer folds and ridge-alpha selection procedure. Ridge alpha is retuned after removing the two columns. The prior metrics are retained as a historical comparison; current fitted variants both exclude empirical descriptors.

| Target | Prior predictors | Current predictors | Prior CV R2 | Current CV R2 | Prior validation R2 | Current validation R2 |
|---|---:|---:|---:|---:|---:|---:|
| G_OH | 41 | 39 | 0.695 | 0.625 | 0.871 | 0.893 |
| G_O | 41 | 39 | 0.808 | 0.823 | 0.861 | 0.949 |
| G_OOH | 25 | 23 | 0.795 | 0.800 | 0.663 | 0.777 |

The distance-versus-dipole comparison includes the dipole replacements, removal of inverse-distance charge sums, deduplication and retuning of ridge alpha. They do not isolate the contribution of any single descriptor. This comparison measures prediction within the inherited cohorts; it does not establish transferability across N/O/S environments.

All three targets use 15 validation structures / 23 validation sites. The inherited cohorts were selected using historical model residuals, and OOH cohort selection inspected this validation set. These results remain exploratory; the CV scores are conditional on the previously selected population.

## Descriptor formulas

The tables below define every raw descriptor used by the dipole models and the additional descriptors used by the distance baseline. G_OH and G_O each use 39 unique dipole descriptors; G_OOH uses the 23 descriptors in the first three tables. The remaining 16 descriptors are used by G_OH and G_O. Both current model variants use calculated structural and electronic quantities; empirical element-property lookup descriptors are excluded.

### Atomic inputs and neighborhood definitions

All atomic inputs come from the optimized clean structure in `../models_20261008_linear_ridge_v2/run_models_linear.py`: positions from `array.positions`, element atomic numbers from `array.numbers`, charges from `data.bader_charges`, and signed atomic magnetic moments from `data.post_opt_rpbe_d4_magmoms`.

For one prediction row, let $s$ denote the adsorption metal (`site`) and $p$ the other metal (`partner`). Their assignment is taken from the saved `ads_site` field. Atom positions are $\mathbf r_i$ in Angstrom; signed charges are $q_i$ in elementary-charge units, and signed magnetic moments are $m_i$ in Bohr magnetons. The charge convention enforced by the source code is $q_i=Z_i-N_i^{\mathrm{Bader}}$, where $Z_i$ is the atomic number and $N_i^{\mathrm{Bader}}$ is the stored Bader electron count. Positive charge denotes electron deficiency; negative charge denotes electron excess.

For either metal $M\in\{s,p\}$, define the displacement and distance:

$$
\mathbf u_{iM}=\mathbf r_i-\mathbf r_M,\qquad
d_{iM}=\lVert\mathbf u_{iM}\rVert_2
=\sqrt{(x_i-x_M)^2+(y_i-y_M)^2+(z_i-z_M)^2}.
$$

The selected heteroatom shell is:

$$
H_M=\{i:\ Z_i\in\{7,8,16\},\ i\notin\{s,p\},\ d_{iM}\leq2.30\ {\rm Angstrom}\},
\qquad n_M=\#H_M.
$$

N, O and S are pooled in this set. An atom can belong to both metal neighborhoods. Distances are Cartesian, with no periodic wrapping; the source requires nonperiodic structures. The shared bridge set and support set are:

$$
B=H_s\cap H_p,\qquad n_B=\#B,\qquad
S=\{i:\ i\notin\{s,p\}\}.
$$

The support spin sums include every atom in $S$ except the two metals, including carbon and hydrogen, regardless of distance. Neighborhood sizes are used as denominators and for atom selection; they are not separate model predictors.

For any scalar quantity $v_i$ on a nonempty atom set $A$, define:

$$
\operatorname{Mean}_A(v)=\frac{1}{\#A}\sum_{i\in A}v_i,\qquad
\operatorname{SD}_A(v)=
\sqrt{\frac{1}{\#A}\sum_{i\in A}\left(v_i-\operatorname{Mean}_A(v)\right)^2}.
$$

$$
\operatorname{Min}_A(v)=\min_{i\in A}v_i,\qquad
\operatorname{Max}_A(v)=\max_{i\in A}v_i.
$$

All standard deviations use the population denominator $\#A$ (`numpy.std`, `ddof=0`). A single selected value therefore has standard deviation zero.

### Metal descriptors: all three dipole models

The metal descriptors use calculated Bader charges and the Cartesian separation of the two metals.

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `q_site` | $q_s$ | e |
| `q_partner` | $q_p$ | e |
| `metal_metal_distance_A` | $\lVert\mathbf r_s-\mathbf r_p\rVert_2$ | Angstrom |

### Local dipole descriptors: all three dipole models

For each selected neighbor, define the signed vector contribution and its nonnegative magnitude:

$$
\boldsymbol\mu_{iM}=q_i\mathbf u_{iM},\qquad
p_{iM}=\lVert\boldsymbol\mu_{iM}\rVert_2=\lvert q_i\rvert d_{iM}.
$$

These use the metal position as the local origin. The following eight summary descriptors operate on the individual magnitudes $p_{iM}$; the two net descriptors sum the signed vectors first and then take the norm.

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `site_heteroatom_dipole_contribution_mean_eA` | $\operatorname{Mean}_{H_s}(p_{is})$ | e Angstrom |
| `partner_heteroatom_dipole_contribution_mean_eA` | $\operatorname{Mean}_{H_p}(p_{ip})$ | e Angstrom |
| `site_heteroatom_dipole_contribution_std_eA` | $\operatorname{SD}_{H_s}(p_{is})$ | e Angstrom |
| `site_heteroatom_dipole_contribution_min_eA` | $\operatorname{Min}_{H_s}(p_{is})$ | e Angstrom |
| `site_heteroatom_dipole_contribution_max_eA` | $\operatorname{Max}_{H_s}(p_{is})$ | e Angstrom |
| `partner_heteroatom_dipole_contribution_std_eA` | $\operatorname{SD}_{H_p}(p_{ip})$ | e Angstrom |
| `partner_heteroatom_dipole_contribution_min_eA` | $\operatorname{Min}_{H_p}(p_{ip})$ | e Angstrom |
| `partner_heteroatom_dipole_contribution_max_eA` | $\operatorname{Max}_{H_p}(p_{ip})$ | e Angstrom |
| `site_heteroatom_charge_dipole_proxy_norm_eA` | $\left\lVert\sum_{i\in H_s}q_i(\mathbf r_i-\mathbf r_s)\right\rVert_2$ | e Angstrom |
| `partner_heteroatom_charge_dipole_proxy_norm_eA` | $\left\lVert\sum_{i\in H_p}q_i(\mathbf r_i-\mathbf r_p)\right\rVert_2$ | e Angstrom |

The net norm includes cancellation between contributions pointing in different directions. It can be zero even when individual magnitudes are positive. The summary magnitudes use absolute charges; the vector sums retain charge signs. These descriptors are local point-charge moments. The implemented metal-centered convention fixes their origin for a neighborhood with nonzero net charge.

### Heteroatom charge descriptors: all three dipole models

These summarize the signed Bader charges on the same selected shells. In particular, a minimum charge is the most negative value.

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `site_heteroatom_charge_sum_e` | $\sum_{i\in H_s}q_i$ | e |
| `site_heteroatom_charge_mean_e` | $\operatorname{Mean}_{H_s}(q_i)$ | e |
| `site_heteroatom_charge_std_e` | $\operatorname{SD}_{H_s}(q_i)$ | e |
| `site_heteroatom_charge_min_e` | $\operatorname{Min}_{H_s}(q_i)$ | e |
| `site_heteroatom_charge_max_e` | $\operatorname{Max}_{H_s}(q_i)$ | e |
| `partner_heteroatom_charge_sum_e` | $\sum_{i\in H_p}q_i$ | e |
| `partner_heteroatom_charge_mean_e` | $\operatorname{Mean}_{H_p}(q_i)$ | e |
| `partner_heteroatom_charge_std_e` | $\operatorname{SD}_{H_p}(q_i)$ | e |
| `partner_heteroatom_charge_min_e` | $\operatorname{Min}_{H_p}(q_i)$ | e |
| `partner_heteroatom_charge_max_e` | $\operatorname{Max}_{H_p}(q_i)$ | e |

### Heteroatom spin descriptors: G_OH and G_O

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `site_heteroatom_spin_abs_mean_muB` | $\operatorname{Mean}_{H_s}(\lvert m_i\rvert)$ | Bohr magneton |
| `site_heteroatom_spin_abs_sum_muB` | $\sum_{i\in H_s}\lvert m_i\rvert$ | Bohr magneton |
| `partner_heteroatom_spin_abs_mean_muB` | $\operatorname{Mean}_{H_p}(\lvert m_i\rvert)$ | Bohr magneton |
| `partner_heteroatom_spin_abs_sum_muB` | $\sum_{i\in H_p}\lvert m_i\rvert$ | Bohr magneton |

### Site angle descriptors: G_OH and G_O

Every unique pair of selected neighbors contributes a heteroatom-site-heteroatom angle. Let $P_s=\{(i,j):i,j\in H_s,\ i<j\}$, with $K_s=\#P_s=n_s(n_s-1)/2$. Define:

$$
\theta_{ij,s}=\frac{180}{\pi}
\arccos\!\left[
\operatorname{clip}\!\left(
\frac{\mathbf u_{is}\cdot\mathbf u_{js}}{d_{is}d_{js}},
-1,1\right)\right],\qquad
\overline\theta_s=\frac{1}{K_s}\sum_{(i,j)\in P_s}\theta_{ij,s}.
$$

The clip operation limits roundoff error before applying arccos. Four neighbors give six angles. Every pair has equal weight, independent of element identity or distance.

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `site_angle_mean_deg` | $\overline\theta_s$ | degree |
| `site_angle_std_deg` | $\sqrt{\frac{1}{K_s}\sum_{(i,j)\in P_s}(\theta_{ij,s}-\overline\theta_s)^2}$ | degree |
| `site_angle_min_deg` | $\min_{(i,j)\in P_s}\theta_{ij,s}$ | degree |
| `site_angle_max_deg` | $\max_{(i,j)\in P_s}\theta_{ij,s}$ | degree |

### Shared bridge descriptors: G_OH and G_O

For each shared heteroatom $i\in B$, calculate the metal-heteroatom-metal angle with the angle vertex at the heteroatom:

$$
\phi_i=\frac{180}{\pi}
\arccos\!\left[
\operatorname{clip}\!\left(
\frac{(\mathbf r_s-\mathbf r_i)\cdot(\mathbf r_p-\mathbf r_i)}
{d_{is}d_{ip}},-1,1\right)\right].
$$

Define the magnitude asymmetry of its two local contributions:

$$
a_i=\lvert p_{is}-p_{ip}\rvert
=\lvert q_i\rvert\,\lvert d_{is}-d_{ip}\rvert.
$$

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `shared_bridge_angle_mean_deg` | $\operatorname{Mean}_B(\phi_i)$ | degree |
| `shared_bridge_angle_std_deg` | $\operatorname{SD}_B(\phi_i)$ | degree |
| `shared_bridge_dipole_contribution_asymmetry_mean_eA` | $\operatorname{Mean}_B(a_i)=\frac{1}{n_B}\sum_{i\in B}\lvert q_i\rvert\,\lvert d_{is}-d_{ip}\rvert$ | e Angstrom |

A shared bridge at equal distances from the two metals has zero magnitude asymmetry. This descriptor averages the absolute difference of the individual contribution magnitudes.

### Metal and support spin descriptors: G_OH and G_O

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `spin_site_abs` | $\lvert m_s\rvert$ | Bohr magneton |
| `spin_partner_abs` | $\lvert m_p\rvert$ | Bohr magneton |
| `spin_product_muB2` | $m_s m_p$ | Bohr magneton squared |
| `support_net_spin_muB` | $\sum_{i\in S}m_i$ | Bohr magneton |
| `support_abs_spin_sum_muB` | $\sum_{i\in S}\lvert m_i\rvert$ | Bohr magneton |

The spin product uses signed moments: parallel signs yield a positive product and opposite signs yield a negative product. The support net spin also retains signs; its absolute-spin sum measures the sum of magnitudes.

### Additional distance baseline descriptors

The baseline uses the definitions above for its retained electronic, angle and spin descriptors, and the following raw distance descriptors instead of the corresponding dipole contribution summaries and bridge asymmetry. It also includes two inverse-distance charge sums.

| Descriptor name | Raw-value formula | Units |
|---|---|---|
| `site_heteroatom_distance_mean_A` | $\operatorname{Mean}_{H_s}(d_{is})$ | Angstrom |
| `partner_heteroatom_distance_mean_A` | $\operatorname{Mean}_{H_p}(d_{ip})$ | Angstrom |
| `site_heteroatom_distance_std_A` | $\operatorname{SD}_{H_s}(d_{is})$ | Angstrom |
| `site_heteroatom_distance_min_A` | $\operatorname{Min}_{H_s}(d_{is})$ | Angstrom |
| `site_heteroatom_distance_max_A` | $\operatorname{Max}_{H_s}(d_{is})$ | Angstrom |
| `partner_heteroatom_distance_std_A` | $\operatorname{SD}_{H_p}(d_{ip})$ | Angstrom |
| `partner_heteroatom_distance_min_A` | $\operatorname{Min}_{H_p}(d_{ip})$ | Angstrom |
| `partner_heteroatom_distance_max_A` | $\operatorname{Max}_{H_p}(d_{ip})$ | Angstrom |
| `site_heteroatom_charge_weighted_sum_e_per_A` | $\sum_{i\in H_s}q_i/d_{is}$ | e / Angstrom |
| `partner_heteroatom_charge_weighted_sum_e_per_A` | $\sum_{i\in H_p}q_i/d_{ip}$ | e / Angstrom |
| `shared_bridge_distance_asymmetry_mean_A` | $\operatorname{Mean}_B(\lvert d_{is}-d_{ip}\rvert)$ | Angstrom |

G_OOH's baseline uses the first ten descriptors in this table. G_OH and G_O also use bridge distance asymmetry, and repeat the distance standard deviation, minimum and maximum columns for both metals. Those repeated entries have the same raw-value formulas but separate coefficient entries. The dipole models have one column for each descriptor name.

### Missing values and the transformation used in the model

If $H_M$ is empty, its charge, spin, distance and dipole summaries are stored as missing, including the sum and net dipole norm. Site angles are missing if fewer than two neighbors are selected. Shared bridge summaries are missing if $B$ is empty. Valid zero values remain zero, including a net vector dipole whose contributions cancel.

For each descriptor $j$ and the current training set $T$ of site rows, the imputation value is the median over finite training values:

$$
c_j=\operatorname{median}\{x_{tj}:t\in T,\ x_{tj}\ {\rm finite}\},\qquad
\widetilde x_{tj}=
\begin{cases}
x_{tj}, & x_{tj}\ {\rm finite},\\
c_j, & \text{otherwise}.
\end{cases}
$$

The implementation uses $c_j=0$ if no training value is finite. After imputation, define the training mean and population standard deviation:

$$
\overline x_j=\frac{1}{\#T}\sum_{t\in T}\widetilde x_{tj},\qquad
\sigma_j=\sqrt{\frac{1}{\#T}\sum_{t\in T}(\widetilde x_{tj}-\overline x_j)^2}.
$$

For a new row, impute with the same $c_j$, then standardize using those training values:

$$
z_j=\frac{\widetilde x_j-\overline x_j}{s_j},\qquad
s_j=
\begin{cases}
\sigma_j,&\sigma_j>10^{-12},\\
1,&\text{otherwise}.
\end{cases}
$$

These statistics weight site rows equally. Both sites of a structure stay together when folds are assigned, but each retained site supplies one row when imputation and scaling are calculated. Every inner fold, outer fold and final fit computes its own training statistics. `model_preprocessing.csv` provides the final-fit values for each target and model variant.

The coefficients in the following tables multiply these dimensionless $z_j$ values. Prediction energies are in eV; the intercept is unpenalized in ridge regression.



## Prediction formulas

`G_hat = intercept + sum_j coefficient_j * ((x_j_imputed-training_mean_j)/training_sd_j)`. Missing values use the training median. Empty neighbor environments have missing summaries rather than zero dipole contributions.

### G_OH: dipole model

| Term | Standardized coefficient |
|---|---:|
| `intercept` | +1.06458342 |
| `q_site` | +0.00575598 |
| `q_partner` | -0.08095293 |
| `metal_metal_distance_A` | +0.08344196 |
| `site_heteroatom_dipole_contribution_mean_eA` | +0.08960008 |
| `partner_heteroatom_dipole_contribution_mean_eA` | -0.09899549 |
| `site_heteroatom_dipole_contribution_std_eA` | -0.11905344 |
| `site_heteroatom_dipole_contribution_min_eA` | +0.11982402 |
| `site_heteroatom_dipole_contribution_max_eA` | +0.00223186 |
| `site_heteroatom_charge_sum_e` | +0.01184735 |
| `site_heteroatom_charge_mean_e` | +0.01184735 |
| `site_heteroatom_charge_std_e` | +0.03587042 |
| `site_heteroatom_charge_min_e` | -0.14586761 |
| `site_heteroatom_charge_max_e` | +0.01175698 |
| `site_heteroatom_charge_dipole_proxy_norm_eA` | -0.33386599 |
| `partner_heteroatom_dipole_contribution_std_eA` | +0.09331386 |
| `partner_heteroatom_dipole_contribution_min_eA` | -0.09471200 |
| `partner_heteroatom_dipole_contribution_max_eA` | -0.05891540 |
| `partner_heteroatom_charge_sum_e` | +0.05173941 |
| `partner_heteroatom_charge_mean_e` | +0.05173941 |
| `partner_heteroatom_charge_std_e` | +0.07974085 |
| `partner_heteroatom_charge_min_e` | -0.13910318 |
| `partner_heteroatom_charge_max_e` | +0.06534967 |
| `partner_heteroatom_charge_dipole_proxy_norm_eA` | +0.01463453 |
| `site_heteroatom_spin_abs_mean_muB` | +0.06737056 |
| `site_heteroatom_spin_abs_sum_muB` | +0.06737056 |
| `partner_heteroatom_spin_abs_mean_muB` | -0.04291180 |
| `partner_heteroatom_spin_abs_sum_muB` | -0.04291180 |
| `site_angle_mean_deg` | -0.09542206 |
| `site_angle_std_deg` | +0.12825624 |
| `site_angle_min_deg` | +0.02346908 |
| `site_angle_max_deg` | -0.10178894 |
| `shared_bridge_angle_mean_deg` | +0.13688143 |
| `shared_bridge_angle_std_deg` | +0.00473617 |
| `shared_bridge_dipole_contribution_asymmetry_mean_eA` | +0.01897861 |
| `spin_site_abs` | -0.62987706 |
| `spin_partner_abs` | +0.00976013 |
| `spin_product_muB2` | +0.03420605 |
| `support_net_spin_muB` | +0.04036810 |
| `support_abs_spin_sum_muB` | -0.03514532 |

### G_O: dipole model

| Term | Standardized coefficient |
|---|---:|
| `intercept` | +2.98014825 |
| `q_site` | +0.12967069 |
| `q_partner` | -0.10685536 |
| `metal_metal_distance_A` | -0.30422361 |
| `site_heteroatom_dipole_contribution_mean_eA` | +0.50965663 |
| `partner_heteroatom_dipole_contribution_mean_eA` | -0.71963313 |
| `site_heteroatom_dipole_contribution_std_eA` | -0.50007979 |
| `site_heteroatom_dipole_contribution_min_eA` | +0.66305899 |
| `site_heteroatom_dipole_contribution_max_eA` | +0.35938994 |
| `site_heteroatom_charge_sum_e` | +0.04073866 |
| `site_heteroatom_charge_mean_e` | +0.04073866 |
| `site_heteroatom_charge_std_e` | +0.08899207 |
| `site_heteroatom_charge_min_e` | -0.04793962 |
| `site_heteroatom_charge_max_e` | -0.05824831 |
| `site_heteroatom_charge_dipole_proxy_norm_eA` | -0.66550983 |
| `partner_heteroatom_dipole_contribution_std_eA` | +0.62918806 |
| `partner_heteroatom_dipole_contribution_min_eA` | -0.66120504 |
| `partner_heteroatom_dipole_contribution_max_eA` | -0.12555561 |
| `partner_heteroatom_charge_sum_e` | +0.04623744 |
| `partner_heteroatom_charge_mean_e` | +0.04623744 |
| `partner_heteroatom_charge_std_e` | -0.08067310 |
| `partner_heteroatom_charge_min_e` | -0.08682704 |
| `partner_heteroatom_charge_max_e` | -0.02325368 |
| `partner_heteroatom_charge_dipole_proxy_norm_eA` | +0.35255267 |
| `site_heteroatom_spin_abs_mean_muB` | +0.07412252 |
| `site_heteroatom_spin_abs_sum_muB` | +0.07412252 |
| `partner_heteroatom_spin_abs_mean_muB` | -0.06881211 |
| `partner_heteroatom_spin_abs_sum_muB` | -0.06881211 |
| `site_angle_mean_deg` | -0.40060805 |
| `site_angle_std_deg` | +0.56023675 |
| `site_angle_min_deg` | +0.60904064 |
| `site_angle_max_deg` | -0.45598922 |
| `shared_bridge_angle_mean_deg` | +0.83728126 |
| `shared_bridge_angle_std_deg` | -0.03554232 |
| `shared_bridge_dipole_contribution_asymmetry_mean_eA` | +0.05217181 |
| `spin_site_abs` | -1.43493931 |
| `spin_partner_abs` | +0.09654985 |
| `spin_product_muB2` | +0.07333605 |
| `support_net_spin_muB` | +0.02502178 |
| `support_abs_spin_sum_muB` | +0.08764422 |

### G_OOH: dipole model

| Term | Standardized coefficient |
|---|---:|
| `intercept` | +3.71314453 |
| `q_site` | -0.60593259 |
| `q_partner` | -0.08636396 |
| `metal_metal_distance_A` | -0.01917475 |
| `site_heteroatom_dipole_contribution_mean_eA` | +0.15577395 |
| `partner_heteroatom_dipole_contribution_mean_eA` | -0.13871112 |
| `site_heteroatom_dipole_contribution_std_eA` | -0.15224358 |
| `site_heteroatom_dipole_contribution_min_eA` | +0.21444403 |
| `site_heteroatom_dipole_contribution_max_eA` | +0.14080851 |
| `site_heteroatom_charge_sum_e` | +0.15824677 |
| `site_heteroatom_charge_mean_e` | +0.15824677 |
| `site_heteroatom_charge_std_e` | +0.19582569 |
| `site_heteroatom_charge_min_e` | -0.11816496 |
| `site_heteroatom_charge_max_e` | +0.08664552 |
| `site_heteroatom_charge_dipole_proxy_norm_eA` | -0.41739286 |
| `partner_heteroatom_dipole_contribution_std_eA` | +0.07408806 |
| `partner_heteroatom_dipole_contribution_min_eA` | -0.06876911 |
| `partner_heteroatom_dipole_contribution_max_eA` | +0.00688237 |
| `partner_heteroatom_charge_sum_e` | +0.09430681 |
| `partner_heteroatom_charge_mean_e` | +0.09430681 |
| `partner_heteroatom_charge_std_e` | -0.00328673 |
| `partner_heteroatom_charge_min_e` | +0.02250926 |
| `partner_heteroatom_charge_max_e` | -0.02028771 |
| `partner_heteroatom_charge_dipole_proxy_norm_eA` | -0.25041369 |

## Reproduction and files

Run `python article/KongiCats/calculations/models_20261011_dipole_ridge/run_dipole_models.py` from the repository root; NumPy is required. The original v2 source files and saved fold assignments are required. `descriptor_formulas.md` supplies the descriptor definitions embedded in this report. Input hashes and definitions are recorded in `run_config.json`.

`model_metrics.csv`, `cv_predictions.csv`, `validation_predictions.csv` and `cv_selections.csv` contain paired results. `model_coefficients.csv` and `model_preprocessing.csv` define both fits. `descriptor_replacements.csv` records every replacement and removed duplicate. `dipole_site_features.csv` contains dipole model inputs; `dipole_contributions_audit.csv` records individual atomic contributions and diagnostic element identities/distances. `cohort_membership.csv` records the role of every source site for every target. `dipole_with_empirical_model_metrics.csv` preserves the prior fit metrics for the empirical-descriptor removal comparison.
