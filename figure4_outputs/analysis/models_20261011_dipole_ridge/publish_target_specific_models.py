#!/usr/bin/env python3
"""Publish complete definitions, executable models and current-only reports."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import search_target_specific_models as search
import numpy as np
import joblib
from sklearn.gaussian_process.kernels import Matern
from predict_target_specific_models import load_models, predict, site_features
import build_overpotential_report as overpotential

HERE=Path(__file__).resolve().parent
OUT=HERE/"target_specific_best_models"
LABELS=dict(ridge="Ridge regression",rbf_ridge="Gaussian kernel ridge regression",
    linear_rbf_ridge="Linear + Gaussian kernel ridge regression",gaussian_process="Gaussian-process regression",
    svr="Support-vector regression",pls="Partial least squares regression",extra_trees="Extremely randomized trees",
    random_forest="Random forest",catboost="CatBoost regression",hist_gradient_boosting="Histogram gradient boosting")


def write(name,rows):
    rows=list(rows)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def jsonable(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [jsonable(v) for v in value]
    return value


def save_json(name,value):
    (OUT/name).write_text(json.dumps(jsonable(value),indent=2)+"\n",encoding="utf-8")


def tree_nodes(tree):
    return [dict(node=i,feature=int(tree.feature[i])+1,threshold_standardized=float(tree.threshold[i]),
        left=int(tree.children_left[i]),right=int(tree.children_right[i]),
        normalized_value=float(tree.value[i].reshape(-1)[0]),leaf=bool(tree.children_left[i]<0))
        for i in range(tree.node_count)]


def export(target,result,state):
    prep,estimator,spec=state["preprocessing"],state["estimator"],state["specification"]
    model=dict(target=target,target_index=search.TARGETS.index(target),family=spec["family"],
        descriptor_keys=result["descriptors"],state_file=f"model_{target}.joblib",
        descriptor_means=prep["mean"],descriptor_scales=prep["scale"],imputation_medians=prep["median"],
        target_mean_eV=prep["y_mean"],target_scale_eV=prep["y_scale"],hyperparameters=spec["parameters"])
    lines=[]
    method=spec["family"]
    if method in ("gaussian_process","shared_kernel_gaussian_process"):
        kernel=estimator.kernel_
        component=kernel.k1.k2
        model.update(kernel_amplitude=float(kernel.k1.k1.constant_value),length_scales=component.length_scale,
            noise_variance=float(kernel.k2.noise_level),kernel_type="matern_1.5" if isinstance(component,Matern) else "rbf",
            training_diagonal_jitter=estimator.alpha)
        alpha=np.asarray(estimator.alpha_)
        if alpha.ndim>1:alpha=alpha[:,search.TARGETS.index(target)]
        support=estimator.X_train_
        model["dual_coefficients"]=alpha
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}(\mathbf x)={prep['y_mean']:.12g}+{prep['y_scale']:.12g}\sum_{{i=1}}^{{{len(alpha)}}}a_i k(\mathbf z,\mathbf z_i)\quad[\mathrm{{eV}}].",r"$$","",r"$$",r"r_i^2=\sum_{j=1}^{p}\left(\frac{z_j-z_{ij}}{\ell_j}\right)^2.",r"$$",""]
        if isinstance(component,Matern):
            lines += [r"$$",rf"k(\mathbf z,\mathbf z_i)={model['kernel_amplitude']:.12g}(1+\sqrt{{3}}r_i)\exp(-\sqrt{{3}}r_i).",r"$$",""]
        else:
            lines += [r"$$",rf"k(\mathbf z,\mathbf z_i)={model['kernel_amplitude']:.12g}\exp(-r_i^2/2).",r"$$",""]
        lines += [f"The fitted training noise variance is {model['noise_variance']:.12g} and diagonal numerical jitter is {estimator.alpha:.12g}, in standardized target units. "
            "Noise enters the training covariance; it contributes zero to the cross-covariance used for the prediction mean.","",
            r"$$",r"\mathbf a=(K+(\sigma_n^2+\epsilon)I)^{-1}\widetilde{\mathbf y},\quad \widetilde y_i=(y_i-\overline y)/s_y.",r"$$",""]
    elif method in ("rbf_ridge","linear_rbf_ridge"):
        support,alpha=estimator["support"],estimator["dual_coefficient"]
        model["dual_coefficients"]=alpha
        params=spec["parameters"]
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}(\mathbf x)={prep['y_mean']:.12g}+{prep['y_scale']:.12g}\sum_{{i=1}}^{{{len(alpha)}}}a_i k(\mathbf z,\mathbf z_i)\quad[\mathrm{{eV}}].",r"$$","",r"$$",rf"k(\mathbf z,\mathbf z_i)=\exp\!\left(-\frac{{\|\mathbf z-\mathbf z_i\|_2^2}}{{2({params['length']:.12g})^2}}\right)+{params['linear_weight']:.12g}\frac{{\mathbf z\cdot\mathbf z_i}}{{{support.shape[1]}}}.",r"$$","",r"$$",rf"\mathbf a=(K+{params['alpha']:.12g}I)^{{-1}}\widetilde{{\mathbf y}},\quad\widetilde y_i=(y_i-\overline y)/s_y.",r"$$",""]
    elif method=="svr":
        support,alpha=estimator.support_vectors_,estimator.dual_coef_[0]
        model.update(dual_coefficients=alpha,normalized_intercept=float(estimator.intercept_[0]))
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}(\mathbf x)={prep['y_mean']:.12g}+{prep['y_scale']:.12g}\left[{estimator.intercept_[0]:.12g}+\sum_{{i=1}}^{{{len(alpha)}}}a_i\exp\!\left(-{estimator._gamma:.12g}\|\mathbf z-\mathbf z_i\|_2^2\right)\right]\quad[\mathrm{{eV}}].",r"$$",""]
    elif method in ("ridge","pls"):
        beta=estimator["coefficient"] if method=="ridge" else estimator.coef_.reshape(-1)
        b=0. if method=="ridge" else float(estimator.intercept_[0])
        raw=prep["y_scale"]*beta/prep["scale"]
        intercept=prep["y_mean"]+prep["y_scale"]*b-float(raw@prep["mean"])
        model.update(raw_linear_coefficients=raw,raw_intercept=intercept)
        terms="".join(f" {'+' if c>=0 else '-'} {abs(c):.12g}x_{{{j}}}" for j,c in enumerate(raw,1))
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}={intercept:.12g}{terms}\quad[\mathrm{{eV}}].",r"$$",""]
        support=alpha=None
    elif method in ("extra_trees","random_forest"):
        save_json(f"trees_{target}.json",[tree_nodes(tree.tree_) for tree in estimator.estimators_])
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}(\mathbf x)={prep['y_mean']:.12g}+\frac{{{prep['y_scale']:.12g}}}{{{len(estimator.estimators_)}}}\sum_{{t=1}}^{{{len(estimator.estimators_)}}}T_t(\mathbf z)\quad[\mathrm{{eV}}].",r"$$","",
            "$T_t$ follows the saved split nodes: choose the left child when $z_j\leq c$, otherwise choose the right child; a leaf returns its stored normalized value. "
            f"Every split, child index and leaf value is specified in [the fitted trees](target_specific_best_models/trees_{target}.json).",""
        ]
        support=alpha=None
    elif method=="catboost":
        estimator.save_model(str(OUT/f"trees_{target}.json"),format="json")
        scale,bias=estimator.get_scale_and_bias()
        model.update(tree_scale=scale,tree_bias=bias)
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}={prep['y_mean']:.12g}+{prep['y_scale']:.12g}\left[{bias:.12g}+{scale:.12g}\sum_{{t=1}}^{{{estimator.tree_count_}}}T_t(\mathbf z)\right]\quad[\mathrm{{eV}}].",r"$$","",
            f"All split conditions and leaf values, including the fitted learning rate, are specified in [the fitted trees](target_specific_best_models/trees_{target}.json).",""]
        support=alpha=None
    else:
        baseline=float(estimator._baseline_prediction.reshape(-1)[0])
        trees=[[{name:jsonable(value) for name,value in zip(t.nodes.dtype.names,node)} for node in t.nodes] for iteration in estimator._predictors for t in iteration]
        save_json(f"trees_{target}.json",trees)
        lines += [r"$$",rf"\widehat{{G}}_{{\mathrm{{{target[2:]}}}}}={prep['y_mean']:.12g}+{prep['y_scale']:.12g}\left[{baseline:.12g}+\sum_{{t=1}}^{{{len(trees)}}}T_t(\mathbf z)\right]\quad[\mathrm{{eV}}].",r"$$","",
            f"The fitted split conditions and leaf values are in [the fitted trees](target_specific_best_models/trees_{target}.json). Leaf values already include the learning rate.",""]
        support=alpha=None
    if support is not None:
        write(f"kernel_expansion_{target}.csv",[dict(i=i+1,weight=float(a),**{f"z_{j+1}":float(v) for j,v in enumerate(row)}) for i,(a,row) in enumerate(zip(alpha,support))])
        lines += [f"Every $a_i$ and $z_{{ij}}$ is stored at full precision in [the kernel expansion](target_specific_best_models/kernel_expansion_{target}.csv).",""]
    return model,lines


DEFINITIONS=r"""## Descriptor definitions

All inputs are calculated from the optimized **clean catalyst**. Let $s$ be the adsorption metal, $p$ the partner metal, $\mathbf r_i$ the Cartesian position of atom $i$ in Å, $q_i$ its signed Bader charge in $e$, and $m_i$ its signed post-optimization RPBE-D4 atomic magnetic moment in $\mu_B$.

$$
q_i=Z_i-N_i^{\mathrm{Bader}},\qquad N_i^{\mathrm{Bader}}=\int_{\Omega_i}n(\mathbf r)\,d^3r.
$$

$\Omega_i$ is the atom's Bader basin, defined by zero-flux boundaries of the electron density. The code reads `data.bader_electrons` directly. The stored population includes the source calculation's core-electron convention; it is a total assigned electron population, not a valence-only electron count. Positive $q_i$ means electron deficiency. Because $N_i^{\mathrm{Bader}}=Z_i-q_i$, electron population also distinguishes metals through their nuclear charge, whereas net charge alone removes that distinction.

The population integral and basin definition follow [Bader charge-density analysis](https://theory.cm.utexas.edu/bader/).

### Exact meaning of spin

The values in `data.post_opt_rpbe_d4_magmoms` are calculated local atomic magnetic moments of the optimized clean structure. They measure spin polarization, can be fractional, and carry a sign indicating orientation along the calculation's spin axis:

$$
m_i\approx(N_{i,\uparrow}-N_{i,\downarrow})\mu_B.
$$

This expression explains the physical meaning; the code uses the stored moments. The atom-assignment convention depends on the electronic-structure calculation and is not established to use Bader basins by this array. See the [local magnetic moment definition](https://gpaw.readthedocs.io/tutorialsexercises/magnetic/sites/sites.html).

### Neighborhoods and exact summary operations

$$
H_M=\{i\notin\{s,p\}:Z_i\in\{7,8,16\},\ \|\mathbf r_i-\mathbf r_M\|_2\leq2.30\ \mathrm{Å}\},\quad n_M=\#H_M,\quad M\in\{s,p\}.
$$

N/O/S neighbors are pooled. A ligand may belong to both neighborhoods. $B=H_s\cap H_p$ denotes shared ligands, $T_M=H_M\setminus B$ terminal ligands, and $S$ all atoms except the two metals. Distances use the nonperiodic Cartesian coordinates.

$$
\overline v_A=\operatorname{Mean}_A(v)=\frac{1}{\#A}\sum_{i\in A}v_i,\qquad
\operatorname{SD}_A(v)=\sqrt{\frac{1}{\#A}\sum_{i\in A}(v_i-\overline v_A)^2}.
$$

$$
\operatorname{Min}_A(v)=\min_{i\in A}v_i,\qquad \operatorname{Max}_A(v)=\max_{i\in A}v_i.
$$

The standard deviation uses the population denominator. For a ligand spin magnitude mean, absolute values are taken **before** averaging. A net spin magnitude takes the absolute value **after** summing signed moments. Spin-product descriptors measure relative collinear alignment weighted by moment magnitudes; their unit is $\mu_B^2$, and they are not exchange energies.

### Charge moments and geometry

$$
\mathbf u_{iM}=\mathbf r_i-\mathbf r_M,\quad d_{iM}=\|\mathbf u_{iM}\|_2,\quad
d_{sp}=\|\mathbf r_s-\mathbf r_p\|_2,\quad \mathbf e_M=\frac{\mathbf r_M-\mathbf r_{\mathrm{other}}}{d_{sp}}.
$$

$$
p_{iM}=|q_i|d_{iM},\qquad \boldsymbol\mu_M=\sum_{i\in H_M}q_i\mathbf u_{iM}.
$$

$p_{iM}$ is an individual ligand charge-moment magnitude. $\|\boldsymbol\mu_M\|_2$ sums signed vectors first and retains cancellation. Axial projections use $\boldsymbol\mu_M\cdot\mathbf e_M$. These are local Bader point-charge moment approximations about the metal origin, not full electronic-density dipoles.

$$
Q_M=\sum_{i\in H_M}q_i[3\mathbf u_{iM}\mathbf u_{iM}^{\mathsf T}-d_{iM}^2 I].
$$

This is the traceless Cartesian point-charge quadrupole tensor. Its Frobenius norm and axial projection have units of $e\,\mathrm{Å}^2$. See the [Cartesian multipole definition](https://galileoandeinstein.phys.virginia.edu/Elec_Mag/2022_Lectures/EM_26_Multipoles.html).

For $P_M=\{(i,j):i,j\in H_M,i<j\}$, ligand angles are

$$
\theta_{ij,M}=\frac{180}{\pi}\arccos\!\left[\operatorname{clip}\left(\frac{\mathbf u_{iM}\cdot\mathbf u_{jM}}{d_{iM}d_{jM}},-1,1\right)\right].
$$

The shared-bridge angle $\phi_i$ uses vectors $\mathbf r_s-\mathbf r_i$ and $\mathbf r_p-\mathbf r_i$ with the same clipped arccos expression. Angles are in degrees with equal weight per distinct pair or bridge atom.

Second-shell density for element group $A$ and radius $R$ is $\sum_{i\in A,d_{is}>2.30}\exp[-((d_{is}-R)/0.45)^2]$, with distances in Å. The group is carbon or N/O/S as named in the descriptor.

An empty scalar neighborhood summary is missing and uses the training median. Valid zero moments and exact cancellation remain zero.
"""


def definitions_for(features):
    text=DEFINITIONS
    if not any("quadrupole" in f for f in features):
        start=text.index("$$\nQ_M=")
        end=text.index("For $P_M=",start)
        text=text[:start]+text[end:]
    if not any("angle" in f for f in features):
        start=text.index("For $P_M=")
        end=text.index("Second-shell density",start)
        text=text[:start]+text[end:]
    elif not any("shared_bridge_angle" in f for f in features):
        start=text.index("The shared-bridge angle")
        end=text.index("Second-shell density",start)
        text=text[:start]+"Angles use degrees with equal weight per distinct pair.\n\n"+text[end:]
    if not any(f.startswith("second_shell_") for f in features):
        start=text.index("Second-shell density")
        end=text.index("An empty scalar",start)
        text=text[:start]+text[end:]
    if any("ligand_plane" in f for f in features):
        text+=r"""

### Least squares ligand plane

Let $\mathbf c=n_s^{-1}\sum_{i\in H_s}\mathbf r_i$. Form a matrix $A$ with rows $(\mathbf r_i-\mathbf c)^\mathsf T$. Its unit right singular vector $\mathbf n$ for the smallest singular value is the fitted plane normal. The plane RMS displacement is $\sigma_{\min}(A)/\sqrt{n_s}$, and metal height is $|(\mathbf r_s-\mathbf c)\cdot\mathbf n|$. Fewer than three ligands gives a missing value.
"""
    return text


def graphs(results,source):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    (OUT/"graphs").mkdir(exist_ok=True)
    cv=search.base.read(source/"nested_cv_predictions.csv")
    for target in search.TARGETS:
        for kind,rows in (("validation",search.base.read(source/f"validation_predictions_{target}.csv")),
                          ("grouped_cv",[r for r in cv if r["target"]==target])):
            y=np.asarray([float(r["observed_eV"]) for r in rows]);p=np.asarray([float(r["predicted_eV"]) for r in rows])
            score=results[target]["validation"] if kind=="validation" else results[target]["cv_mean"]
            low,high=min(y.min(),p.min()),max(y.max(),p.max());pad=max(.05,(high-low)*.07)
            fig,ax=plt.subplots(figsize=(6.5,5.5),constrained_layout=True)
            ax.scatter(y,p,s=25,alpha=.65,color="#296ca5",edgecolors="white",linewidths=.3)
            ax.plot([low-pad,high+pad],[low-pad,high+pad],"--",color="#343434")
            ax.set(xlabel="DFT energy (eV)",ylabel="Predicted energy (eV)",title=f"{target[2:]}: {kind.replace('_',' ')}",xlim=(low-pad,high+pad),ylim=(low-pad,high+pad))
            ax.set_aspect("equal");ax.grid(alpha=.15)
            note=f"R² = {score['R2']:.3f}\nRMSE = {score['RMSE_eV']:.3f} eV"
            if kind=="grouped_cv":note+="\nScores: mean of three repeats"
            ax.text(.03,.97,note,transform=ax.transAxes,va="top",bbox=dict(facecolor="white",edgecolor="#ddd",alpha=.9))
            for ext in ("png","svg","pdf"):fig.savefig(OUT/"graphs"/f"{target}_{kind}.{ext}",dpi=220)
            plt.close(fig)


def publish(source_name="target_specific_model_search_populations"):
    source=HERE/source_name
    summary=json.loads((source/"results.json").read_text(encoding="utf-8"))
    results,definitions=summary["targets"],summary["descriptor_definitions"]
    OUT.mkdir(exist_ok=True)
    models,sections={},{}
    for target,result in results.items():
        shutil.copy2(source/f"model_{target}.joblib",OUT/f"model_{target}.joblib")
        state=joblib.load(OUT/f"model_{target}.joblib")
        models[target],sections[target]=export(target,result,state)
    save_json("model_parameters.json",models)
    save_json("model_metrics.json",results)
    shutil.copy2(HERE/"cohort_membership.csv",OUT/"cohort_membership.csv")
    for name in ("nested_cv_predictions.csv","nested_selections.csv","fixed_inputs.json","search_grid.json"):
        shutil.copy2(source/name,OUT/name)
    for target in results:
        shutil.copy2(source/f"validation_predictions_{target}.csv",OUT/f"validation_predictions_{target}.csv")
    write("descriptors.csv",[dict(target=t,position=i+1,**definitions[f]) for t,r in results.items() for i,f in enumerate(r["descriptors"])])
    graphs(results,source)
    lines=["# Current adsorption-energy models","","Separate calculated-input models predict OH, O and OOH adsorption energies in eV. "
        "The three targets use the same training and validation membership.","","## Model performance","",
        "| Target | Model | Inputs | Training R² | Validation R² | R²cv | Validation RMSE (eV) | CV RMSE (eV) |",
        "|---|---|---:|---:|---:|---:|---:|---:|"]
    for t,r in results.items():
        lines.append(f"| {t[2:]} | {LABELS[r['specification']['family']]} | {len(r['descriptors'])} | {r['training']['R2']:.4f} | {r['validation']['R2']:.4f} | {r['cv_mean']['R2']:.4f} | {r['validation']['RMSE_eV']:.4f} | {r['cv_mean']['RMSE_eV']:.4f} |")
    lines += ["",f"**All three targets meet validation R² ≥ 0.85 and R²cv ≥ 0.85: {'yes' if summary['all_targets_meet_threshold'] else 'no'}.**","",
        "Training comprises **50 structures / 70 sites**. Validation comprises **10 structures / 13 sites**. "
        "Both sites of a structure stay together. The validation set retains the frozen chemistry coverage and descriptor-range requirements. "
        "The original geometry quality checks and approved whole-structure exclusions apply to every target.","",
        "R²cv is the mean R² from three repetitions of five outer folds grouped by structure. In each outer fold, "
        f"the {summary['grid_size']:,} configured model/descriptor candidates are compared by four inner folds using only outer-training data. "
        "Feature ranking, imputation, scaling and fitting use the applicable training subset. "
        "The outer-held structures do not enter those operations. The final candidate is selected by three repetitions "
        "of four grouped folds on the full training set, then fitted to all 70 training sites. Validation errors do not select that final candidate.","",
        "These results describe performance within this curated structure dataset. The fixed validation cohort has been inspected during model development, so it is not a fresh external test set.","",
        "| Target | CV repeat 1 R² | CV repeat 2 R² | CV repeat 3 R² |","|---|---:|---:|---:|"]
    for t,r in results.items():lines.append(f"| {t[2:]} | "+" | ".join(f"{m['R2']:.4f}" for m in r['cv_repeats'])+" |")
    if summary.get("validation_used_for_final_candidate_selection"):
        start=next(i for i,line in enumerate(lines) if line.startswith("R²cv is the mean"))
        lines[start]="R²cv is the mean R² from three repetitions of five outer folds grouped by structure, conditional on the selected model family and descriptor policy. " \
            "Four inner folds tune the selected family's hyperparameters within each outer training fold. " \
            "For ranked policies, descriptors are ranked anew inside each fitting subset; fixed descriptor policies keep their specified inputs. " \
            "Imputation, scaling and fitting use the applicable training subset. The descriptor tables show the final full-training fit. " \
            "Final candidates maximize the repeated training-selection CV score subject to the requested validation and model-CV bounds. " \
            "The frozen validation set therefore participates in final candidate acceptance. Its R² is a development-validation score."
        lines += ["", "### Complete search procedure", "",
            f"The full {summary['grid_size']:,}-candidate search was also repeated inside every outer training fold, with four inner folds selecting the family, descriptor policy and hyperparameters. "
            "These scores assess that complete training-only search procedure rather than the chosen family's tuning alone.","",
            "| Target | Complete-search nested R²cv | CV RMSE (eV) |","|---|---:|---:|"]
        for t,r in results.items():
            m=r['full_search_cv_mean'];lines.append(f"| {t[2:]} | {m['R2']:.4f} | {m['RMSE_eV']:.4f} |")
        shutil.copy2(source/'full_search_nested_cv_predictions.csv',OUT/'full_search_nested_cv_predictions.csv')
    features=list(dict.fromkeys(f for r in results.values() for f in r['descriptors']))
    lines += ["",definitions_for(features),"","## Inputs and fitted prediction formulas","",
        "The descriptor order is defined separately for each target. Missing values use the training median $h_j$. "
        "Inputs then use $z_j=(x_j^*-\mu_j)/s_j$, where $x_j^*=x_j$ for a finite value and $h_j$ otherwise. "
        "$\mu_j$ and $s_j$ are the training mean and population standard deviation after imputation. "
        "A zero or negligible standard deviation is replaced by one. Numerical formulas below use energies in eV.",""]
    for t,r in results.items():
        m=models[t]
        lines += [f"### {t[2:]} model","",f"**{LABELS[m['family']]}**, fitted parameters: `{json.dumps(m['hyperparameters'])}`.","",
            "| Input | Human-readable descriptor | Formula | Units | Description |","|---|---|---|---|---|"]
        for j,f in enumerate(r["descriptors"],1):
            d=definitions[f];formula=d['formula'].replace('|',r'\vert ')
            lines.append(f"| $x_{{{j}}}$ | {d['name']} | ${formula}$ | {d['units']} | {d['description']} |")
        lines += ["","| Input | Median $h_j$ | Mean $\mu_j$ | Scale $s_j$"+(" | Kernel length $\ell_j$" if 'length_scales' in m else '')+" |",
            "|---|---:|---:|---:"+("|---:" if 'length_scales' in m else '')+"|"]
        for j,(median,mean,scale) in enumerate(zip(m['imputation_medians'],m['descriptor_means'],m['descriptor_scales']),1):
            text=f"| $x_{{{j}}}$ | {median:.12g} | {mean:.12g} | {scale:.12g}"
            if 'length_scales' in m:text+=f" | {m['length_scales'][j-1]:.12g}"
            lines.append(text+" |")
        lines += ["",*sections[t],
            "| Validation | Structure-grouped nested CV |","|---|---|",
            f"| ![{t} validation](target_specific_best_models/graphs/{t}_validation.png) | ![{t} grouped CV](target_specific_best_models/graphs/{t}_grouped_cv.png) |",""]
    live=load_models(OUT)
    # Check exported inference against the final selected prediction artifacts.
    structures={r['name']:r for r in search.base.read(HERE.parents[1]/'extracted/structures_by_target.csv')}
    for t in results:
        for r in search.base.read(OUT/f"validation_predictions_{t}.csv"):
            actual=predict(site_features(structures[r['name']],int(r['ads_site'].replace('metal',''))-1),live[t])
            if abs(actual-float(r['predicted_eV']))>1e-8:raise ValueError(f"export mismatch {t} {r['name']} {r['ads_site']}")
    lines += overpotential.build_overpotential_section(models_override=live,output_directory=OUT,
        feature_function=site_features,prediction_function=predict,report_prefix="target_specific_best_models")
    lines += ["## Reproducible model artifacts","",
        "- [Fitted model parameters](target_specific_best_models/model_parameters.json)",
        "- [Human-readable descriptor catalog](target_specific_best_models/descriptors.csv)",
        "- [Nested CV predictions](target_specific_best_models/nested_cv_predictions.csv)",
        "- [Cohort membership](target_specific_best_models/cohort_membership.csv)",
        "- [Prediction implementation](predict_target_specific_models.py)","",
        "All numeric model parameters are saved at full precision. Plots are supplied as PNG, SVG and PDF.",""]
    report="\n".join(lines)
    (HERE/"selected_models_full_summary.md").write_text(report,encoding="utf-8")
    local=report.replace('](target_specific_best_models/','](').replace('](predict_target_specific_models.py)','](../predict_target_specific_models.py)')
    local=local.replace('](../../archive/','](../../../archive/')
    (OUT/"selected_models_full_summary.md").write_text(local,encoding="utf-8")
    manifest=dict(status="current",model_directory=OUT.name,report="selected_models_full_summary.md",targets=search.TARGETS,
        descriptor_keys={t:r['descriptors'] for t,r in results.items()},
        thresholds=dict(validation_R2=.85,nested_grouped_CV_R2=.85),all_thresholds_met=summary['all_targets_meet_threshold'],
        sha256={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'cohort_membership.csv',OUT/'model_parameters.json',OUT/'nested_cv_predictions.csv']})
    manifest["search_directory"]=source.name
    (HERE/"current_model_selection.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("Published current target-specific models and full report",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--source",default="target_specific_model_search_populations")
    publish(parser.parse_args().source)
