# Current model descriptor formulas

## Descriptors used by all three models

### Symbols and atomic selection

Let $s$ denote the adsorption metal and $p$ the partner metal. Their Cartesian positions $\mathbf r_s$ and $\mathbf r_p$ are in Angstrom. Inputs are the optimized clean-structure coordinates, Bader charges and post-optimization RPBE-D4 atomic magnetic moments.

The signed Bader charge of atom $i$ is $q_i=Z_i-N_i^{\mathrm{Bader}}$, where $Z_i$ is its atomic number and $N_i^{\mathrm{Bader}}$ its Bader electron population. Positive charge means electron deficiency. The signed atomic magnetic moment $m_i$ is in Bohr magnetons.

### Exact meaning of the spin values

The spin values are calculated local atomic magnetic moments, stored as one signed value per atom in `data.post_opt_rpbe_d4_magmoms`. They are the post-optimization RPBE-D4 values of the clean catalyst. Their unit is the Bohr magneton, $\mu_B$. A local magnetic moment measures spin polarization, and can be fractional. The sign gives its orientation along the calculation's spin axis.

Conceptually, the local moment reflects the imbalance between spin-up and spin-down electron populations assigned to that atom:

$$
m_i\approx(N_{i,\uparrow}-N_{i,\downarrow})\mu_B.
$$

Atomic moment assignment depends on the electronic-structure method's partitioning; this population expression explains the physical meaning. The model reads the stored atomic moments directly and does not recompute them from Bader charges. The available array does not establish that the moment assignment uses Bader basins. See the [local magnetic moment definition](https://gpaw.readthedocs.io/tutorialsexercises/magnetic/sites/sites.html).

The current spin inputs are defined exactly as:

$$
x_{3}=|m_s|,\qquad
x_{4}=\frac{1}{n_s}\sum_{i\in H_s}|m_i|,\qquad
x_{5}=\frac{1}{n_p}\sum_{i\in H_p}|m_i|.
$$

Absolute values discard orientation; each ligand's absolute moment is taken before averaging. Individual moments and mean magnitudes are in $\mu_B$.

### Ligand selection and geometry

For each metal $M\in\{s,p\}$:

$$
H_M=\{i:Z_i\in\{7,8,16\},\ i\notin\{s,p\},\ \lVert\mathbf r_i-\mathbf r_M\rVert_2\leq2.30\ \mathrm{Angstrom}\},\qquad n_M=\#H_M.
$$

N/O/S neighbors are pooled and an atom may belong to both neighborhoods. Distances are Cartesian for nonperiodic structures. Metal separation is:

$$
d_{sp}=\sqrt{(r_{s,x}-r_{p,x})^2+(r_{s,y}-r_{p,y})^2+(r_{s,z}-r_{p,z})^2}.
$$

### Shared and terminal ligand charge

$$
B=H_s\cap H_p,\qquad T_M=H_M\setminus B,\qquad
\operatorname{Mean}_A(q)=\frac{1}{\#A}\sum_{i\in A}q_i.
$$

Shared ligands neighbor both metals; terminal ligands neighbor only the specified metal. Charge means retain the sign of each Bader charge and have units of $e$.

### Local ligand dipole definition

$$
\boldsymbol\mu_M=\sum_{i\in H_M}q_i(\mathbf r_i-\mathbf r_M),\qquad p_M=\lVert\boldsymbol\mu_M\rVert_2.
$$

The net magnitude sums signed vectors first and includes directional cancellation. It has units of $e\,\mathrm{Angstrom}$. The metal defines the origin of this local Bader point-charge approximation.

### Summary operations in use

$$
\operatorname{Mean}_A(v)=\frac{1}{\#A}\sum_{i\in A}v_i.
$$

An empty ligand or pair set produces a missing summary, replaced by the target's training median. Genuine zero charges, moments and net dipole cancellation are retained as zero.


Each row is one input to every model, in the equation order shown.

| Symbol | Descriptor name | Description | Formula | Units | Data column |
|---|---|---|---|---|---|
| $x_{1}$ | Adsorption metal charge | Signed Bader charge on the adsorption metal; positive means electron deficiency. | $q_s=Z_s-N_s^{\mathrm{Bader}}$ | e | `q_site` |
| $x_{2}$ | Partner metal charge | Signed Bader charge on the other metal. | $q_p=Z_p-N_p^{\mathrm{Bader}}$ | e | `q_partner` |
| $x_{3}$ | Adsorption metal spin magnitude | Absolute calculated atomic magnetic moment of the adsorption metal. | $\lvert m_s\rvert$ | Bohr magneton | `spin_site_abs` |
| $x_{4}$ | Adsorption metal: mean ligand spin magnitude | Mean of absolute atomic magnetic moments on the selected N/O/S neighbors. | $\operatorname{Mean}_{H_s}(\lvert m_i\rvert)$ | Bohr magneton | `site_heteroatom_spin_abs_mean_muB` |
| $x_{5}$ | Partner metal: mean ligand spin magnitude | Mean of absolute atomic magnetic moments on the selected N/O/S neighbors. | $\operatorname{Mean}_{H_p}(\lvert m_i\rvert)$ | Bohr magneton | `partner_heteroatom_spin_abs_mean_muB` |
| $x_{6}$ | Metal separation | Cartesian separation between the two metals. | $\lVert\mathbf r_s-\mathbf r_p\rVert_2$ | Angstrom | `metal_metal_distance_A` |
| $x_{7}$ | Adsorption metal: mean terminal ligand charge | Mean signed Bader charge of terminal ligands in this metal's shell. | $\operatorname{Mean}_{H_s\setminus B}(q_i)$ | e | `site_terminal_ligand_charge_mean_e` |
| $x_{8}$ | Adsorption metal: net ligand dipole magnitude | Magnitude of the signed vector sum of ligand charge moments around this metal; includes directional cancellation. | $\left\lVert\sum_{i\in H_s}q_i(\mathbf r_i-\mathbf r_s)\right\rVert_2$ | e Angstrom | `site_heteroatom_charge_dipole_proxy_norm_eA` |
