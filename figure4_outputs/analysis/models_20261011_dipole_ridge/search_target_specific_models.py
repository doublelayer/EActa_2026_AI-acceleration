#!/usr/bin/env python3
"""Independent physical-input searches on the unchanged common cohort."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".model_dependencies"))
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".matplotlib_cache"))
import numpy as np
from threadpoolctl import threadpool_limits
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, Matern, WhiteKernel
from sklearn.svm import SVR
from catboost import CatBoostRegressor
import joblib

import run_shared_descriptor_search as base

OUT = HERE / "target_specific_model_search"
MANDATORY = "metal_metal_distance_A"
TARGETS = base.TARGETS
SEED = 20261011


def write(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader(); writer.writerows(rows)


def family(f):
    if f.endswith("_ligand_bader_electron_mean"):
        return ("site" if f.startswith("site") else "partner") + "_ligand_charge"
    if "heteroatom_charge_" in f and "dipole" not in f or "ligand_charge" in f:
        return ("site" if f.startswith("site") else "partner") + "_ligand_charge"
    if "dipole" in f and ("heteroatom" in f):
        return ("site" if f.startswith("site") else "partner") + "_ligand_dipole"
    if "heteroatom_spin" in f:
        return ("site" if f.startswith("site") else "partner") + "_ligand_spin"
    if f.startswith("site_angle_"): return "site_angle"
    if f.startswith("partner_angle_"): return "partner_angle"
    if f.startswith("shared_bridge_angle_"): return "bridge_angle"
    if f.startswith("second_shell_C_"): return "carbon_density"
    if f.startswith("second_shell_heteroatom_"): return "heteroatom_density"
    if f.startswith("support_"): return "support_spin"
    return f


def inputs(extended=False,populations=False):
    pool, definitions, data, partitions, aligned, cohort = base.load_data()
    if extended:
        from extended_physical_descriptors import augment
        pool, definitions, data = augment(pool, definitions, data, populations)
    joint_y = np.column_stack([data[t]["y"] for t in TARGETS])
    for d in data.values(): d["joint_y"] = joint_y
    shared = data[TARGETS[0]]
    eligible = []
    for j, f in enumerate(pool):
        a, b = shared["x"][:, j], shared["validation_x"][:, j]
        a, b = a[np.isfinite(a)], b[np.isfinite(b)]
        if len(a) < 30 or np.ptp(a) <= 1e-10:
            continue
        if len(b) and (b.min() < a.min() - 1e-10 or b.max() > a.max() + 1e-10):
            continue
        if "_sum_" in f and "heteroatom" in f:
            continue  # Same information as mean for the fixed four-ligand shells.
        eligible.append(f)
    return pool, definitions, data, partitions, cohort, eligible


def policies(eligible):
    current = json.loads((HERE / "current_descriptor_selection.json").read_text(encoding="utf-8"))["shared_descriptors"]
    sets = {"physical_8": current,
        "compact_4": ["q_partner", "spin_site_abs", MANDATORY, "site_heteroatom_charge_dipole_proxy_norm_eA"],
        "metals": [f for f in ["q_site", "q_partner", "spin_site_abs", "spin_partner_abs", "spin_product_muB2", MANDATORY] if f in eligible]}
    for k in (3, 5, 7, 10, 12): sets[f"ranked_{k}"] = dict(kind="ranked", count=k)
    for k in (4, 6, 8): sets[f"residual_{k}"] = dict(kind="residual", count=k)
    groups = {}
    for f in eligible:
        if f != MANDATORY: groups.setdefault(family(f), []).append(f)
    rng = np.random.default_rng(SEED)
    known = {tuple(sorted(fs)) for fs in sets.values() if isinstance(fs, list)}
    for _ in range(32):
        for attempt in range(100):
            selected = [MANDATORY]
            for group, fs in groups.items():
                probability = .8 if group in ("q_site", "q_partner", "spin_site_abs") else .35
                if rng.random() < probability: selected.append(str(rng.choice(fs)))
            if 3 <= len(selected) <= 11 and tuple(sorted(selected)) not in known:
                known.add(tuple(sorted(selected))); sets[f"physical_mix_{len(known):02d}"] = selected; break
    return sets


def specifications(feature_policies):
    specs = []
    def add(policy, method, **parameters):
        specs.append(dict(id=f"candidate_{len(specs):04d}", policy=policy, family=method, parameters=parameters))
    for policy in feature_policies:
        for alpha in (.01, .1, 1., 10., 100.): add(policy, "ridge", alpha=alpha)
        for length, alpha in itertools.product((.7, 1.5, 3., 6.), (.001, .01, .1, 1.)):
            add(policy, "rbf_ridge", length=length, alpha=alpha, linear_weight=0.)
    focused = [p for p in feature_policies if not p.startswith("physical_mix")]
    for policy in focused:
        for length, alpha, weight in itertools.product((1.5, 3.), (.01, .1), (.3, 1.)):
            add(policy, "linear_rbf_ridge", length=length, alpha=alpha, linear_weight=weight)
        for components in (1, 2, 3, 5): add(policy, "pls", components=components)
        for c, length, epsilon in itertools.product((1., 10., 100.), (1.5, 3.), (.01, .1)):
            add(policy, "svr", C=c, length=length, epsilon=epsilon)
    tree_policies = ["physical_8", "compact_4", "ranked_5", "ranked_7", "ranked_10", "residual_6"]
    for policy in tree_policies:
        for depth, leaf in ((3, 1), (5, 1), (None, 1), (None, 3)):
            add(policy, "extra_trees", depth=depth, leaf=leaf)
        for depth, leaf in ((4, 1), (None, 1), (None, 3)):
            add(policy, "random_forest", depth=depth, leaf=leaf)
        for depth, regularization in itertools.product((2, 3, 4), (3., 10.)):
            add(policy, "catboost", depth=depth, regularization=regularization, iterations=300)
        for leaf, regularization in ((3, 1.), (6, 1.), (6, 10.)):
            add(policy, "hist_gradient_boosting", leaf=leaf, regularization=regularization)
    gpr_policies = list(feature_policies)
    for policy in gpr_policies:
        for kernel in ("rbf", "matern"):
            add(policy, "gaussian_process", kernel=kernel)
    return specs


class Search:
    def __init__(self, target, pool, d, eligible, feature_policies):
        self.target, self.pool, self.d = target, pool, d
        self.x, self.y = d["x"], d["y"]
        self.eligible, self.policies = eligible, feature_policies
        self.selection_cache, self.preprocessing_cache, self.kernel_cache = {}, {}, {}

    def selected(self, policy, train):
        key = (policy, tuple(train))
        if key in self.selection_cache: return self.selection_cache[key]
        definition = self.policies[policy]
        if isinstance(definition, list):
            fs = definition
        else:
            values = self.x[train]
            y = self.y[train]
            fs = [MANDATORY]
            available = list(self.eligible)
            for step in range(definition["count"] - 1):
                residual = y - y.mean()
                if definition["kind"] == "residual" and len(fs) > 1:
                    columns = [self.pool.index(f) for f in fs]
                    pp, _ = base.fit_batch(values[:, columns], values[:, columns], y)
                    residual = y - pp["ridge", 10.]
                candidates = []
                for f in available:
                    if family(f) in {family(chosen) for chosen in fs}: continue
                    v = values[:, self.pool.index(f)]
                    valid = np.isfinite(v) & np.isfinite(residual)
                    if valid.sum() < 3 or np.std(v[valid]) <= 1e-12: continue
                    similar = False
                    for chosen in fs:
                        w = values[:, self.pool.index(chosen)]
                        good = np.isfinite(v) & np.isfinite(w)
                        if good.sum() > 2 and np.std(w[good]) > 1e-12 and abs(np.corrcoef(v[good], w[good])[0, 1]) >= .95:
                            similar = True; break
                    if not similar:
                        corr = abs(float(np.corrcoef(v[valid], residual[valid])[0, 1]))
                        candidates.append((-corr, f))
                if not candidates: break
                fs.append(min(candidates)[1])
        columns = [self.pool.index(f) for f in fs]
        self.selection_cache[key] = columns
        return columns

    def prepared(self, policy, train, held, external=None):
        columns = self.selected(policy, train)
        key = (policy, tuple(train), tuple(held))
        if external is None and key in self.preprocessing_cache: return self.preprocessing_cache[key]
        xh = self.x[held][:, columns] if external is None else external[:, columns]
        z, zh, median, mean, scale = base.preprocess(self.x[train][:, columns], xh)
        ym, ys = float(self.y[train].mean()), float(self.y[train].std())
        ys = max(ys, 1e-12)
        value = dict(z=z, zh=zh, median=median, mean=mean, scale=scale, y=(self.y[train]-ym)/ys,
            y_mean=ym, y_scale=ys, columns=columns)
        if external is None: self.preprocessing_cache[key] = value
        return value

    def fit_predict(self, spec, train, held, external=None, retain=False):
        p = self.prepared(spec["policy"], train, held, external)
        z, zh, y, params, method = p["z"], p["zh"], p["y"], spec["parameters"], spec["family"]
        fitted = None
        if method == "ridge":
            beta = np.linalg.solve(z.T @ z + params["alpha"]*np.eye(z.shape[1]), z.T @ y)
            prediction = zh @ beta
            fitted = dict(coefficient=beta)
        elif method in ("rbf_ridge", "linear_rbf_ridge"):
            cache_key = (spec["policy"], tuple(train), tuple(held), params["length"], params["linear_weight"])
            if external is None and cache_key in self.kernel_cache:
                eigenvalues, vectors, cross = self.kernel_cache[cache_key]
            else:
                dd = np.maximum(np.sum(z*z,axis=1)[:,None]+np.sum(z*z,axis=1)[None,:]-2*z@z.T,0.)
                dh = np.maximum(np.sum(zh*zh,axis=1)[:,None]+np.sum(z*z,axis=1)[None,:]-2*zh@z.T,0.)
                kernel = np.exp(-dd/(2*params["length"]**2)) + params["linear_weight"]*(z@z.T)/z.shape[1]
                cross = np.exp(-dh/(2*params["length"]**2)) + params["linear_weight"]*(zh@z.T)/z.shape[1]
                eigenvalues, vectors = np.linalg.eigh(kernel)
                if external is None: self.kernel_cache[cache_key] = eigenvalues, vectors, cross
            beta = vectors @ ((vectors.T@y)/(np.maximum(eigenvalues,0.)+params["alpha"]))
            prediction = cross @ beta
            fitted = dict(dual_coefficient=beta, support=z)
        else:
            if method == "pls":
                fitted = PLSRegression(n_components=min(params["components"],z.shape[1]),scale=False,max_iter=500)
            elif method == "svr":
                fitted = SVR(C=params["C"],gamma=1/(2*params["length"]**2),epsilon=params["epsilon"],cache_size=64)
            elif method in ("extra_trees", "random_forest"):
                cls = ExtraTreesRegressor if method == "extra_trees" else RandomForestRegressor
                fitted = cls(n_estimators=96,max_depth=params["depth"],min_samples_leaf=params["leaf"],
                    random_state=SEED,n_jobs=1,max_features=1.)
            elif method == "catboost":
                fitted = CatBoostRegressor(iterations=params["iterations"],depth=params["depth"],
                    l2_leaf_reg=params["regularization"],learning_rate=.05,loss_function="RMSE",verbose=False,
                    random_seed=SEED,thread_count=1,allow_writing_files=False)
            elif method == "hist_gradient_boosting":
                fitted = HistGradientBoostingRegressor(max_iter=200,max_leaf_nodes=7,
                    min_samples_leaf=params["leaf"],l2_regularization=params["regularization"],
                    learning_rate=.05,early_stopping=False,random_state=SEED)
            elif method in ("gaussian_process", "shared_kernel_gaussian_process"):
                component = RBF(np.full(z.shape[1],2.),(.2,20.)) if params["kernel"]=="rbf" else Matern(np.full(z.shape[1],2.),(.2,20.),nu=1.5)
                kernel = ConstantKernel(1.,(.01,100.))*component+WhiteKernel(.05,(.001,1.))
                fitted = GaussianProcessRegressor(kernel=kernel,normalize_y=False,n_restarts_optimizer=0,
                    random_state=SEED,alpha=1e-8)
            else: raise ValueError(method)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if method == "shared_kernel_gaussian_process":
                    yy = self.d["joint_y"][train]
                    fitted.fit(z,(yy-yy.mean(axis=0))/np.maximum(yy.std(axis=0),1e-12))
                else:
                    fitted.fit(z,y)
            prediction = np.asarray(fitted.predict(zh)).reshape(-1)
            if method == "shared_kernel_gaussian_process":
                prediction = np.asarray(fitted.predict(zh))[:,TARGETS.index(self.target)]
        result = p["y_mean"] + p["y_scale"]*prediction
        return (result, dict(specification=spec,preprocessing=p,estimator=fitted)) if retain else result

    def evaluate(self, spec, partitions):
        sse, count = 0., 0
        for train, held in partitions:
            pp = self.fit_predict(spec,train,held)
            sse += float(np.sum((pp-self.y[held])**2)); count += len(held)
        return sse/count


def grouped_partitions(names, seeds, count):
    result=[]
    for seed in seeds:
        for held_names in base.folds(names, seed, count):
            held=np.asarray([i for i,n in enumerate(names) if n in held_names],dtype=int)
            train=np.asarray([i for i,n in enumerate(names) if n not in held_names],dtype=int)
            result.append((train,held))
    return result


def subset(d, indexes):
    return dict(x=d["x"][indexes], y=d["y"][indexes], joint_y=d["joint_y"][indexes],
        names=[d["names"][i] for i in indexes], keys=[d["keys"][i] for i in indexes])


def choose(search, specs, partitions):
    scores=[]
    for spec in specs:
        try:
            mse=search.evaluate(spec,partitions)
            if np.isfinite(mse): scores.append((float(mse),spec["id"],spec))
        except (ValueError, np.linalg.LinAlgError):
            continue
    if not scores: raise ValueError("no candidate fitted successfully")
    return min(scores,key=lambda x:(x[0],x[1])), scores


def nested_job(target, repeat, fold, pool, d, eligible, feature_policies, specs, train, held):
    checkpoint=OUT/f"nested_{target}_{repeat}_{fold}.json"
    if checkpoint.exists(): return json.loads(checkpoint.read_text(encoding="utf-8"))
    inner=subset(d,train)
    search=Search(target,pool,inner,eligible,feature_policies)
    partitions=grouped_partitions(inner["names"],[base.SEED+repeat*10007+fold*101],4)
    (mse,_,spec),scores=choose(search,specs,partitions)
    prediction,state=search.fit_predict(spec,np.arange(len(train)),[],external=d["x"][held],retain=True)
    result=dict(target=target,repeat=repeat,fold=fold,specification=spec,inner_R2=1-mse/float(np.var(inner["y"])),
        descriptors=[pool[j] for j in state["preprocessing"]["columns"]],
        rows=[dict(target=target,repeat=repeat,fold=fold,name=d["keys"][i][0],ads_site=d["keys"][i][1],
            observed_eV=float(d["y"][i]),predicted_eV=float(p)) for i,p in zip(held,prediction)])
    checkpoint.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(f"Nested {target} repeat {repeat+1} fold {fold+1}: {spec['family']} / {spec['policy']} completed",flush=True)
    return result


def initialize_worker(directory):
    global OUT
    OUT=Path(directory)
    threadpool_limits(limits=1)


def final_job(target,d,pool,eligible,feature_policies,specs,completed):
    search=Search(target,pool,d,eligible,feature_policies)
    partitions=grouped_partitions(d["names"],[base.SEED+811+i*10007 for i in range(3)],4)
    preview=OUT/"OOH_final_selection_preview.json"
    if target=="G_OOH" and preview.exists():
        saved=json.loads(preview.read_text(encoding="utf-8"))
        ids={candidate["id"]:candidate for candidate in specs}
        if {r["id"] for r in saved} != set(ids): raise ValueError("incomplete saved OOH selection scores")
        scores=[(float(r["MSE"]),r["id"],ids[r["id"]]) for r in saved]
        mse,_,spec=min(scores,key=lambda x:(x[0],x[1]))
    else:
        (mse,_,spec),scores=choose(search,specs,partitions)
    indexes=np.arange(len(d["y"]))
    validation,state=search.fit_predict(spec,indexes,[],d["validation_x"],True)
    training=search.fit_predict(spec,indexes,indexes)
    joblib.dump(state,OUT/f"model_{target}.joblib")
    metrics=[]
    for repeat in range(3):
        rows=sorted((r for result in completed if result["target"]==target and result["repeat"]==repeat for r in result["rows"]),key=lambda r:(r["name"],r["ads_site"]))
        metrics.append(base.metric(np.asarray([r["observed_eV"] for r in rows]),np.asarray([r["predicted_eV"] for r in rows])))
    final=dict(specification=spec,descriptors=[pool[i] for i in state["preprocessing"]["columns"]],
        training=base.metric(d["y"],training),validation=base.metric(d["validation_y"],validation),
        cv_repeats=metrics,cv_mean={k:float(np.mean([m[k] for m in metrics])) for k in metrics[0]},
        final_selection_inner_R2=1-mse/float(np.var(d["y"])))
    predrows=[dict(target=target,name=k[0],ads_site=k[1],observed_eV=float(y),predicted_eV=float(p))
        for k,y,p in zip(d["validation_keys"],d["validation_y"],validation)]
    scorerows=[dict(target=target,id=ident,family=c["family"],policy=c["policy"],
        selection_cv_R2=1-error/float(np.var(d["y"])),RMSE_eV=float(np.sqrt(error))) for error,ident,c in scores]
    write(f"final_selection_scores_{target}.csv",scorerows)
    (OUT/f"result_{target}.json").write_text(json.dumps(final,indent=2)+"\n",encoding="utf-8")
    write(f"validation_predictions_{target}.csv",predrows)
    print(f"FINAL {target}: {spec['family']} / {spec['policy']}, validation R2 {final['validation']['R2']:.4f}, nested CV R2 {final['cv_mean']['R2']:.4f}",flush=True)
    return target,final

def assess(args):
    OUT.mkdir(exist_ok=True)
    pool,definitions,data,saved,cohort,eligible=inputs(args.extended,args.populations)
    grid=json.loads((OUT/"search_grid.json").read_text(encoding="utf-8"))
    feature_policies,specs=grid["feature_policies"],grid["specifications"]
    # The recorded, unchanged grid is repeated inside every outer training fold.
    jobs=[]
    for target,d in data.items():
        for repeat in range(3):
            partitions=grouped_partitions(d["names"],[base.SEED+repeat*10007],5)
            for fold,(train,held) in enumerate(partitions):
                jobs.append((target,repeat,fold,pool,d,eligible,feature_policies,specs,train,held))
    completed=[]
    with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize_worker,initargs=(str(OUT),)) as executor:
        pending=[executor.submit(nested_job,*job) for job in jobs]
        for future in as_completed(pending):
            completed.append(future.result())
            rows=[r for result in completed for r in result["rows"]]
            write("nested_cv_predictions.csv",rows)
            write("nested_selections.csv",[dict(target=r["target"],repeat=r["repeat"],fold=r["fold"],
                family=r["specification"]["family"],policy=r["specification"]["policy"],
                id=r["specification"]["id"],inner_R2=r["inner_R2"],descriptors=";".join(r["descriptors"])) for r in completed])
    results={}
    with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize_worker,initargs=(str(OUT),)) as executor:
        pending=[executor.submit(final_job,target,d,pool,eligible,feature_policies,specs,completed) for target,d in data.items()]
        for future in as_completed(pending):
            target,result=future.result();results[target]=result
    all_pass=all(r["validation"]["R2"]>=.85 and r["cv_mean"]["R2"]>=.85 for r in results.values())
    (OUT/"results.json").write_text(json.dumps(dict(targets=results,all_targets_meet_threshold=all_pass,
        grid_size=len(specs),descriptor_definitions=definitions),indent=2)+"\n",encoding="utf-8")
    print(f"ASSESSMENT COMPLETE: threshold met for all targets = {all_pass}",flush=True)


def screen(args):
    OUT.mkdir(exist_ok=True)
    pool, definitions, data, saved, cohort, eligible = inputs(args.extended,args.populations)
    feature_policies = policies(eligible)
    specs = specifications(feature_policies)
    (OUT / "search_grid.json").write_text(json.dumps(dict(feature_policies=feature_policies,specifications=specs,
        eligible_descriptors=eligible,excluded_descriptors=[f for f in pool if f not in eligible]),indent=2)+"\n",encoding="utf-8")
    source_files=[HERE/"cohort_membership.csv",HERE/"current_site_features.csv",HERE/"representative_split/relative_distance_exclusions.json"]
    snapshot=dict(cohort=cohort,training_structures=50,training_sites=70,validation_structures=10,validation_sites=13,
        sha256={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
        criterion="validation R2 >= 0.85 and repeated grouped CV R2 >= 0.85 for every target",
        selection="training grouped CV only; validation evaluated after final selection")
    (OUT/"fixed_inputs.json").write_text(json.dumps(snapshot,indent=2)+"\n",encoding="utf-8")
    print(f"Screening {len(specs)} specifications / {len(feature_policies)} feature policies per target",flush=True)
    screening=[]
    for target,d in data.items():
        if target not in args.targets: continue
        search=Search(target,pool,d,eligible,feature_policies)
        partitions=grouped_partitions(d["names"],[base.SEED+10007],5)
        started=time.monotonic()
        for i,spec in enumerate(specs,1):
            try:
                mse=search.evaluate(spec,partitions)
                row=dict(target=target,id=spec["id"],family=spec["family"],policy=spec["policy"],
                    screening_R2=1-mse/float(np.var(d["y"])),RMSE_eV=float(np.sqrt(mse)),error="")
            except Exception as exc:
                row=dict(target=target,id=spec["id"],family=spec["family"],policy=spec["policy"],screening_R2=-999.,RMSE_eV="",error=str(exc))
            screening.append(row)
            if i%100==0 or i==len(specs):
                best=max((r for r in screening if r["target"]==target),key=lambda r:r["screening_R2"])
                print(f"{target}: {i}/{len(specs)}, best screening R2 {best['screening_R2']:.4f} ({best['family']}, {best['policy']}), {time.monotonic()-started:.0f}s",flush=True)
                write("screening_metrics.csv",screening)
    print("SCREENING COMPLETE",flush=True)


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=["screen","assess"],default="screen")
    parser.add_argument("--extended",action="store_true")
    parser.add_argument("--populations",action="store_true")
    parser.add_argument("--targets",nargs="+",choices=TARGETS,default=list(TARGETS))
    parser.add_argument("--workers",type=int,default=3)
    args=parser.parse_args()
    if args.extended: OUT = HERE / "target_specific_model_search_extended"
    if args.populations:
        args.extended=True
        OUT = HERE / "target_specific_model_search_populations"
    with threadpool_limits(limits=1):
        (screen if args.phase=="screen" else assess)(args)


if __name__=="__main__": main()
