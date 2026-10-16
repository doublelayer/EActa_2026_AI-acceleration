"""Human-readable definitions of the calculated descriptors considered in the search."""


def catalog():
    rows = {}

    def add(key, name, formula, units, description):
        rows[key] = dict(key=key, name=name, formula=formula, units=units, description=description)

    add("q_site", "Adsorption metal charge", r"q_s=Z_s-N_s^{\mathrm{Bader}}", "e",
        "Signed Bader charge on the adsorption metal; positive means electron deficiency.")
    add("q_partner", "Partner metal charge", r"q_p=Z_p-N_p^{\mathrm{Bader}}", "e",
        "Signed Bader charge on the other metal.")
    add("metal_metal_distance_A", "Metal separation", r"\lVert\mathbf r_s-\mathbf r_p\rVert_2", "Angstrom",
        "Cartesian separation between the two metals.")
    for prefix, symbol, label in (("site", "s", "Adsorption metal"), ("partner", "p", "Partner metal")):
        shell = "H_" + symbol
        for statistic, word, operation in (("mean", "mean", "Mean"), ("std", "spread", "SD"),
                                            ("min", "minimum", "Min"), ("max", "maximum", "Max")):
            add(f"{prefix}_heteroatom_dipole_contribution_{statistic}_eA",
                f"{label}: {word} ligand dipole magnitude",
                rf"\operatorname{{{operation}}}_{{{shell}}}(p_{{i{symbol}}})", "e Angstrom",
                f"{word.capitalize()} of individual point-charge contribution magnitudes "
                "on the selected N/O/S neighbors; spread is population standard deviation.")
        add(f"{prefix}_heteroatom_charge_dipole_proxy_norm_eA", f"{label}: net ligand dipole magnitude",
            rf"\left\lVert\sum_{{i\in {shell}}}q_i(\mathbf r_i-\mathbf r_{symbol})\right\rVert_2", "e Angstrom",
            "Magnitude of the signed vector sum of ligand charge moments around this metal; includes directional cancellation.")
        for statistic, word, operation in (("sum", "total", None), ("mean", "mean", "Mean"),
                                           ("std", "spread", "SD"), ("min", "minimum", "Min"), ("max", "maximum", "Max")):
            formula = rf"\sum_{{i\in {shell}}}q_i" if operation is None else rf"\operatorname{{{operation}}}_{{{shell}}}(q_i)"
            if statistic == "min":
                formula = rf"\min_{{i\in {shell}}}q_i"
            description = ("Smallest signed Bader charge on the selected N/O/S neighbors; the most negative ligand charge."
                           if statistic == "min" else
                           f"{word.capitalize()} of signed Bader charges on the selected N/O/S neighbors; "
                           "minimum is the most negative charge and spread is population standard deviation.")
            add(f"{prefix}_heteroatom_charge_{statistic}_e", f"{label}: {word} ligand charge", formula, "e",
                description)
        for statistic, word in (("mean", "mean"), ("sum", "total")):
            formula = (rf"\operatorname{{Mean}}_{{{shell}}}(\lvert m_i\rvert)" if statistic == "mean"
                       else rf"\sum_{{i\in {shell}}}\lvert m_i\rvert")
            add(f"{prefix}_heteroatom_spin_abs_{statistic}_muB", f"{label}: {word} ligand spin magnitude",
                formula, "Bohr magneton", f"{word.capitalize()} of absolute atomic magnetic moments on the selected N/O/S neighbors.")
    for statistic, word in (("mean", "Mean"), ("std", "SD"), ("min", "Min"), ("max", "Max")):
        label = {"mean": "Mean", "std": "Spread of", "min": "Smallest", "max": "Largest"}[statistic]
        add(f"site_angle_{statistic}_deg", f"{label} ligand angle at adsorption metal",
            rf"\operatorname{{{word}}}_{{P_s}}(\theta_{{ij,s}})", "degree",
            "Summary of all distinct ligand-metal-ligand angles at the adsorption metal; each neighbor pair has equal weight.")
    add("shared_bridge_angle_mean_deg", "Mean metal-bridge-metal angle", r"\operatorname{Mean}_B(\phi_i)", "degree",
        "Mean angle at each shared ligand between vectors pointing to the two metals.")
    add("shared_bridge_angle_std_deg", "Spread of metal-bridge-metal angles", r"\operatorname{SD}_B(\phi_i)", "degree",
        "Population standard deviation of the angles at shared bridging ligands.")
    add("shared_bridge_dipole_contribution_asymmetry_mean_eA", "Mean bridge dipole magnitude asymmetry",
        r"\operatorname{Mean}_B(\lvert q_i\rvert\,\lvert d_{is}-d_{ip}\rvert)", "e Angstrom",
        "Mean absolute difference between a shared ligand's charge-moment magnitudes about the two metals.")
    add("spin_site_abs", "Adsorption metal spin magnitude", r"\lvert m_s\rvert", "Bohr magneton",
        "Absolute calculated atomic magnetic moment of the adsorption metal.")
    add("spin_partner_abs", "Partner metal spin magnitude", r"\lvert m_p\rvert", "Bohr magneton",
        "Absolute calculated atomic magnetic moment of the other metal.")
    add("spin_product_muB2", "Signed metal spin product", r"m_s m_p", "Bohr magneton squared",
        "Product of signed metal magnetic moments; opposite signs give a negative product.")
    add("support_net_spin_muB", "Net support spin", r"\sum_{i\in S}m_i", "Bohr magneton",
        "Signed sum of magnetic moments over every atom except the two metals, including carbon and hydrogen.")
    add("support_abs_spin_sum_muB", "Total support spin magnitude", r"\sum_{i\in S}\lvert m_i\rvert", "Bohr magneton",
        "Sum of absolute magnetic moments over every atom except the two metals.")
    return rows


def definitions_for(features):
    text = CURRENT_DEFINITIONS.split("### Exact meaning of the spin values")[0]
    spin_features = [f for f in features if "spin" in f]
    if spin_features:
        text += "### Exact meaning of the spin values" + CURRENT_DEFINITIONS.split("### Exact meaning of the spin values")[1].split("The four spin inputs")[0]
        expressions = {"spin_site_abs": r"|m_s|", "spin_partner_abs": r"|m_p|",
            "site_heteroatom_spin_abs_mean_muB": r"\frac{1}{n_s}\sum_{i\in H_s}|m_i|",
            "partner_heteroatom_spin_abs_mean_muB": r"\frac{1}{n_p}\sum_{i\in H_p}|m_i|",
            "spin_product_muB2": r"m_s m_p"}
        text += "The current spin inputs are defined exactly as:\n\n$$\n" + ",\\qquad\n".join(
            rf"x_{{{features.index(f)+1}}}={expressions[f]}" for f in spin_features) + ".\n$$\n\n"
        text += "Absolute values discard orientation; each ligand's absolute moment is taken before averaging. "
        if "spin_product_muB2" in features:
            text += "The signed metal spin product is positive for moments with the same sign and negative for opposite signs. "
            text += "It measures their relative collinear orientation weighted by their magnitudes, in $\\mu_B^2$; it is not an exchange-energy calculation. "
        text += "Individual moments and mean magnitudes are in $\\mu_B$.\n\n"
    text += r"""### Ligand selection and geometry

For each metal $M\in\{s,p\}$:

$$
H_M=\{i:Z_i\in\{7,8,16\},\ i\notin\{s,p\},\ \lVert\mathbf r_i-\mathbf r_M\rVert_2\leq2.30\ \mathrm{Angstrom}\},\qquad n_M=\#H_M.
$$

N/O/S neighbors are pooled and an atom may belong to both neighborhoods. Distances are Cartesian for nonperiodic structures. Metal separation is:

$$
d_{sp}=\sqrt{(r_{s,x}-r_{p,x})^2+(r_{s,y}-r_{p,y})^2+(r_{s,z}-r_{p,z})^2}.
$$

"""
    if any("terminal_ligand" in f or "shared_ligand" in f for f in features):
        text += r"""### Shared and terminal ligand charge

$$
B=H_s\cap H_p,\qquad T_M=H_M\setminus B,\qquad
\operatorname{Mean}_A(q)=\frac{1}{\#A}\sum_{i\in A}q_i.
$$

Shared ligands neighbor both metals; terminal ligands neighbor only the specified metal. Charge means retain the sign of each Bader charge and have units of $e$.

"""
    if any("dipole" in f for f in features):
        text += "### Local ligand dipole definition\n\n"
        if any("dipole_contribution" in f for f in features):
            text += r"""$$
p_{iM}=\lVert q_i(\mathbf r_i-\mathbf r_M)\rVert_2=|q_i|\lVert\mathbf r_i-\mathbf r_M\rVert_2.
$$

An individual contribution is its signed point-charge moment's magnitude, in $e\,\mathrm{Angstrom}$. Summary statistics operate on these individual magnitudes.

"""
        if any("dipole_proxy_norm" in f for f in features):
            text += r"""$$
\boldsymbol\mu_M=\sum_{i\in H_M}q_i(\mathbf r_i-\mathbf r_M),\qquad p_M=\lVert\boldsymbol\mu_M\rVert_2.
$$

The net magnitude sums signed vectors first and includes directional cancellation. It has units of $e\,\mathrm{Angstrom}$. The metal defines the origin of this local Bader point-charge approximation.

"""
    if any("angle" in f for f in features):
        text += r"""### Ligand angles

Let $\mathbf u_{iM}=\mathbf r_i-\mathbf r_M$. The pair set $P_M=\{(i,j):i,j\in H_M,\ i<j\}$ contains every distinct ligand pair once.

$$
\theta_{ij,M}=\frac{180}{\pi}\arccos\left(\frac{\mathbf u_{iM}\cdot\mathbf u_{jM}}{\lVert\mathbf u_{iM}\rVert_2\lVert\mathbf u_{jM}\rVert_2}\right).
$$

Angles are in degrees and the numerical cosine is clipped to $[-1,1]$ before arccos. Each pair has equal weight.

"""
        if any("shared_bridge_angle" in f for f in features):
            text += r"""Shared bridge angles use $B=H_s\cap H_p$ and the shared ligand as vertex:

$$
\phi_i=\frac{180}{\pi}\arccos\left(\frac{(\mathbf r_s-\mathbf r_i)\cdot(\mathbf r_p-\mathbf r_i)}{\lVert\mathbf r_s-\mathbf r_i\rVert_2\lVert\mathbf r_p-\mathbf r_i\rVert_2}\right),\quad i\in B.
$$

"""
    operations = []
    if any("_mean_" in f for f in features):
        operations.append(r"\operatorname{Mean}_A(v)=\frac{1}{\#A}\sum_{i\in A}v_i")
    if any("_min_" in f for f in features):
        operations.append(r"\operatorname{Min}_A(v)=\min_{i\in A}v_i")
    if any("_max_" in f for f in features):
        operations.append(r"\operatorname{Max}_A(v)=\max_{i\in A}v_i")
    if any("_std_" in f for f in features):
        operations.append(r"\operatorname{SD}_A(v)=\sqrt{\frac{1}{\#A}\sum_{i\in A}(v_i-\overline v_A)^2},\quad \overline v_A=\frac{1}{\#A}\sum_{i\in A}v_i")
    if operations:
        text += "### Summary operations in use\n\n$$\n" + ",\\qquad\n".join(operations) + ".\n$$\n\n"
    text += "An empty ligand or pair set produces a missing summary, replaced by the target's training median. "
    text += "Genuine zero charges, moments and net dipole cancellation are retained as zero.\n"
    return text


CURRENT_DEFINITIONS = r"""### Symbols and atomic selection

Let $s$ denote the adsorption metal and $p$ the partner metal. Their Cartesian positions $\mathbf r_s$ and $\mathbf r_p$ are in Angstrom. Inputs are the optimized clean-structure coordinates, Bader charges and post-optimization RPBE-D4 atomic magnetic moments.

The signed Bader charge of atom $i$ is $q_i=Z_i-N_i^{\mathrm{Bader}}$, where $Z_i$ is its atomic number and $N_i^{\mathrm{Bader}}$ its Bader electron population. Positive charge means electron deficiency. The signed atomic magnetic moment $m_i$ is in Bohr magnetons.

### Exact meaning of the spin values

The spin values are calculated local atomic magnetic moments, stored as one signed value per atom in `data.post_opt_rpbe_d4_magmoms`. They are the post-optimization RPBE-D4 values of the clean catalyst. Their unit is the Bohr magneton, $\mu_B$. A local magnetic moment measures spin polarization, and can be fractional. The sign gives its orientation along the calculation's spin axis.

Conceptually, the local moment reflects the imbalance between spin-up and spin-down electron populations assigned to that atom:

$$
m_i\approx(N_{i,\uparrow}-N_{i,\downarrow})\mu_B.
$$

Atomic moment assignment depends on the electronic-structure method's partitioning; this population expression explains the physical meaning. The model reads the stored atomic moments directly and does not recompute them from Bader charges. The available array does not establish that the moment assignment uses Bader basins. See the [local magnetic moment definition](https://gpaw.readthedocs.io/tutorialsexercises/magnetic/sites/sites.html).

The four spin inputs are defined exactly as:

$$
x_3=|m_s|,\qquad x_4=|m_p|,\qquad
x_5=\frac{1}{n_s}\sum_{i\in H_s}|m_i|,\qquad
x_6=\frac{1}{n_p}\sum_{i\in H_p}|m_i|.
$$

Here $s$ is the adsorption metal, $p$ is the partner metal, and the selected ligand neighborhoods $H_s,H_p$ and their sizes $n_s,n_p$ are specified below. All four inputs have units of $\mu_B$. The absolute value is taken for each atom before the ligand average. For example, ligand moments $+0.04,-0.02,+0.01,-0.01\ \mu_B$ give $(0.04+0.02+0.01+0.01)/4=0.020\ \mu_B$.

These inputs discard spin orientation: metal moments $+3$ and $-3\ \mu_B$ both produce a magnitude of $3\ \mu_B$. Thus the current spin inputs cannot directly distinguish parallel from antiparallel metal moments.

### Ligand selection and metal separation

For each metal $M\in\{s,p\}$, select its N/O/S neighbors:

$$
H_M=\{i:Z_i\in\{7,8,16\},\ i\notin\{s,p\},\ \lVert\mathbf r_i-\mathbf r_M\rVert_2\leq2.30\ \mathrm{Angstrom}\},\qquad n_M=\#H_M.
$$

N/O/S neighbors are pooled, and an atom may belong to both metal neighborhoods. Distances use Cartesian coordinates for nonperiodic structures. For a nonempty neighborhood, the mean ligand spin magnitude is:

$$
\operatorname{Mean}_{H_M}(\lvert m_i\rvert)=\frac{1}{n_M}\sum_{i\in H_M}\lvert m_i\rvert.
$$

An empty neighborhood has a missing mean, replaced by the target's training median during prediction. A zero magnetic moment is retained as zero.

Metal separation is the Euclidean distance between the two metal positions:

$$
d_{sp}=\sqrt{(r_{s,x}-r_{p,x})^2+(r_{s,y}-r_{p,y})^2+(r_{s,z}-r_{p,z})^2}.
$$
"""


MINIMUM_CHARGE_DEFINITION = r"""
### Minimum ligand charge at the adsorption metal

$$
x_8=q_{\min,s}=\min_{i\in H_s}q_i.
$$

This is the smallest signed Bader charge among the adsorption metal's selected N/O/S neighbors, in elementary-charge units ($e$). It identifies the most electron-rich ligand by its atomic charge; for charges $-1.10,-0.85,-0.72,-0.90\ e$, the descriptor is $-1.10\ e$. An empty neighborhood gives a missing value, replaced by the target's training median.
"""

NET_DIPOLE_DEFINITION = r"""
### Net ligand dipole magnitude at the adsorption metal

$$
\boldsymbol\mu_s=\sum_{i\in H_s}q_i(\mathbf r_i-\mathbf r_s),\qquad
x_9=p_s=\lVert\boldsymbol\mu_s\rVert_2
=\sqrt{\mu_{s,x}^2+\mu_{s,y}^2+\mu_{s,z}^2}.
$$

Each selected ligand contributes its signed Bader charge multiplied by its displacement from the adsorption metal. The vectors are summed first, then the Euclidean magnitude is taken, in $e\,\mathrm{Angstrom}$. Contributions in opposing directions can cancel. This is a metal-centered point-charge approximation to the local ligand charge moment, with the adsorption metal defining the origin; it is not a full electronic-density dipole. It combines charge with the spatial arrangement of the selected ligands. An empty neighborhood gives a missing value, replaced by the target's training median; exact vector cancellation gives zero and is retained.
"""


DEFINITIONS = r"""### Symbols and atomic selection

Let $s$ be the adsorption metal and $p$ the partner metal. Positions $\mathbf r_i$ are in Angstrom, signed Bader charges $q_i$ are in elementary-charge units, and signed calculated atomic magnetic moments $m_i$ are in Bohr magnetons. Inputs are the optimized clean-structure positions, Bader charges and post-optimization RPBE-D4 atomic magnetic moments. No adsorption-state descriptor or empirical element-property lookup enters the model.

$$
q_i=Z_i-N_i^{\mathrm{Bader}},\quad
\mathbf u_{iM}=\mathbf r_i-\mathbf r_M,\quad
d_{iM}=\lVert\mathbf u_{iM}\rVert_2,\quad M\in\{s,p\}.
$$

The code verifies the stored charge convention against atomic numbers and stored Bader electron counts. Atomic numbers identify atoms for neighborhood selection; they are not predictors.

$$
H_M=\{i:Z_i\in\{7,8,16\},\ i\notin\{s,p\},\ d_{iM}\leq2.30\ \mathrm{Angstrom}\},\quad
B=H_s\cap H_p,\quad S=\{i:i\notin\{s,p\}\}.
$$

N/O/S neighbors are pooled. Distances use Cartesian coordinates for nonperiodic structures. A bridging ligand belongs to both shells. The 2.30 Angstrom cutoff is retained from the earlier workflow and can affect N/O/S environments differently.

For a nonempty index set $A$ and scalar values $v_i$, all table formulas use these exact operators:

$$
\operatorname{Mean}_A(v)=\frac{1}{\#A}\sum_{i\in A}v_i,\qquad
\operatorname{SD}_A(v)=\sqrt{\frac{1}{\#A}\sum_{i\in A}\left(v_i-\operatorname{Mean}_A(v)\right)^2}.
$$

$$
\operatorname{Min}_A(v)=\min_{i\in A}v_i,\qquad
\operatorname{Max}_A(v)=\max_{i\in A}v_i.
$$

The standard deviation uses the population denominator, with no sample correction. A one-value set has zero spread. Empty shells have missing charge, spin and dipole summaries, including sums; empty bridges have missing bridge summaries. Valid cancellation to zero is retained as zero.

Individual local dipole contributions are:

$$
\boldsymbol\mu_{iM}=q_i(\mathbf r_i-\mathbf r_M),\qquad
p_{iM}=\lVert\boldsymbol\mu_{iM}\rVert_2=\lvert q_i\rvert d_{iM}.
$$

The table distinguishes a summary of individual magnitudes from the magnitude of the signed vector sum. These are Bader point-charge proxies using the metal as the local origin; the full DFT dipole also depends on local atomic polarization ([Veit et al., 2020](https://arxiv.org/abs/2003.12437)).

Site-angle pairs are $P_s=\{(i,j):i,j\in H_s,\ i<j\}$, with one angle for each pair:

$$
\theta_{ij,s}=\frac{180}{\pi}\arccos\!\left[\operatorname{clip}\!\left(
\frac{\mathbf u_{is}\cdot\mathbf u_{js}}{d_{is}d_{js}},-1,1\right)\right].
$$

Fewer than two selected neighbors give missing site-angle summaries. Bridge angles have their vertex at the shared ligand:

$$
\phi_i=\frac{180}{\pi}\arccos\!\left[\operatorname{clip}\!\left(
\frac{(\mathbf r_s-\mathbf r_i)\cdot(\mathbf r_p-\mathbf r_i)}{d_{is}d_{ip}},-1,1\right)\right].
$$

The clip operation limits floating-point roundoff before arccos. All angular summaries weight the selected angles equally.
"""
