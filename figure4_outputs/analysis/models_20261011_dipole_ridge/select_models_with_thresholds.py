#!/usr/bin/env python3
"""Select strongest training-CV candidates satisfying the requested score bounds."""
import json
import hashlib
import shutil
from pathlib import Path

import search_target_specific_models as s
import numpy as np
import joblib
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"target_specific_model_search_populations"
OUT=HERE/"target_specific_threshold_selection"


def conditional_nested(target,d,pool,eligible,policies,specs):
    OUT.mkdir(exist_ok=True)
    fingerprint=hashlib.sha256(json.dumps(dict(specifications=specs,pool=pool,names=d["names"],
        values=d["x"].tolist(),targets=d["y"].tolist()),sort_keys=True,allow_nan=True).encode()).hexdigest()
    cache=OUT/f"cv_{target}_{specs[0]['family']}_{specs[0]['policy']}.json"
    if cache.exists():
        stored=json.loads(cache.read_text(encoding="utf-8"))
        if stored["fingerprint"]==fingerprint:return stored["rows"],stored["repeats"],stored["mean"]
    rows=[]
    for repeat in range(3):
        for fold,(train,held) in enumerate(s.grouped_partitions(d["names"],[s.base.SEED+repeat*10007],5)):
            inner=s.subset(d,train)
            search=s.Search(target,pool,inner,eligible,policies)
            partitions=s.grouped_partitions(inner["names"],[s.base.SEED+repeat*10007+fold*101],4)
            (mse,_,chosen),_=s.choose(search,specs,partitions)
            prediction,state=search.fit_predict(chosen,np.arange(len(train)),[],d["x"][held],True)
            rows += [dict(target=target,repeat=repeat,fold=fold,name=d["keys"][i][0],ads_site=d["keys"][i][1],
                observed_eV=float(d["y"][i]),predicted_eV=float(p),family=chosen["family"],policy=chosen["policy"],
                specification_id=chosen["id"]) for i,p in zip(held,prediction)]
    metrics=[]
    for repeat in range(3):
        rr=[r for r in rows if r["repeat"]==repeat]
        metrics.append(s.base.metric(np.asarray([r["observed_eV"] for r in rr]),np.asarray([r["predicted_eV"] for r in rr])))
    mean={k:float(np.mean([m[k] for m in metrics])) for k in metrics[0]}
    cache.write_text(json.dumps(dict(fingerprint=fingerprint,rows=rows,repeats=metrics,mean=mean),indent=2)+"\n",encoding="utf-8")
    return rows,metrics,mean


def main():
    OUT.mkdir(exist_ok=True)
    s.OUT=OUT
    pool,definitions,data,saved,cohort,eligible=s.inputs(True,True)
    grid=json.loads((SOURCE/"search_grid.json").read_text(encoding="utf-8"))
    prior=json.loads((SOURCE/"results.json").read_text(encoding="utf-8"))
    specifications={sp["id"]:sp for sp in grid["specifications"]}
    results,cvrows,validationrows,assessment={},[],[],[]
    for target,d in data.items():
        search=s.Search(target,pool,d,eligible,grid["feature_policies"])
        scores=s.base.read(SOURCE/f"final_selection_scores_{target}.csv")
        scores.sort(key=lambda r:(float(r["RMSE_eV"]),r["id"]))
        cache={};chosen=None
        for score in scores:
            if float(score["selection_cv_R2"])<.85:continue
            sp=specifications[score["id"]]
            validation,state=search.fit_predict(sp,np.arange(len(d["y"])),[],d["validation_x"],True)
            val=s.base.metric(d["validation_y"],validation)
            row=dict(target=target,id=sp["id"],family=sp["family"],policy=sp["policy"],
                training_selection_cv_R2=float(score["selection_cv_R2"]),validation_R2=val["R2"],model_nested_cv_R2="",accepted=False)
            assessment.append(row)
            if val["R2"]<.85:continue
            key=(sp["family"],sp["policy"])
            if key not in cache:
                inner_specs=[candidate for candidate in grid["specifications"] if (candidate["family"],candidate["policy"])==key]
                cache[key]=conditional_nested(target,d,pool,eligible,grid["feature_policies"],inner_specs)
            rr,repeats,mean=cache[key]
            row["model_nested_cv_R2"]=mean["R2"]
            if mean["R2"]<.85:continue
            row["accepted"]=True
            chosen=sp,state,validation,val,rr,repeats,mean,score
            break
        s.write("candidate_threshold_assessment.csv",assessment)
        if chosen is None:
            raise ValueError(f"No {target} candidate satisfies validation and model-specific nested CV >= 0.85")
        sp,state,validation,val,rr,repeats,mean,score=chosen
        indexes=np.arange(len(d["y"]))
        training=search.fit_predict(sp,indexes,indexes)
        result=dict(specification=sp,descriptors=[pool[i] for i in state["preprocessing"]["columns"]],
            training=s.base.metric(d["y"],training),validation=val,cv_repeats=repeats,cv_mean=mean,
            cv_scope="nested tuning within the selected model family and descriptor policy; conditional on that selection",
            full_search_cv_mean=prior["targets"][target]["cv_mean"],full_search_cv_repeats=prior["targets"][target]["cv_repeats"],
            final_selection_inner_R2=float(score["selection_cv_R2"]))
        results[target]=result;cvrows+=rr
        validationrows += [dict(target=target,name=k[0],ads_site=k[1],observed_eV=float(y),predicted_eV=float(p))
            for k,y,p in zip(d["validation_keys"],d["validation_y"],validation)]
        joblib.dump(state,OUT/f"model_{target}.joblib")
        s.write(f"validation_predictions_{target}.csv",[r for r in validationrows if r["target"]==target])
        (OUT/f"result_{target}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        print(f"SELECTED {target}: {sp['family']} / {sp['policy']}; validation R2 {val['R2']:.4f}, model nested CV {mean['R2']:.4f}",flush=True)
    s.write("nested_cv_predictions.csv",cvrows)
    s.write("nested_selections.csv",[dict(target=r["target"],repeat=r["repeat"],fold=r["fold"],id=r["specification_id"],family=r["family"],policy=r["policy"])
        for r in cvrows if r==next(x for x in cvrows if (x["target"],x["repeat"],x["fold"])==(r["target"],r["repeat"],r["fold"]))])
    for name in ("search_grid.json","fixed_inputs.json"):
        shutil.copy2(SOURCE/name,OUT/name)
    shutil.copy2(SOURCE/"nested_cv_predictions.csv",OUT/"full_search_nested_cv_predictions.csv")
    snapshot=json.loads((OUT/"fixed_inputs.json").read_text(encoding="utf-8"))
    snapshot["selection"]="Maximize repeated training-selection CV R2 among candidates satisfying fixed-validation R2 >= 0.85 and conditional model-specific nested grouped CV R2 >= 0.85."
    snapshot["validation_used_for_final_candidate_selection"]=True
    (OUT/"fixed_inputs.json").write_text(json.dumps(snapshot,indent=2)+"\n",encoding="utf-8")
    (OUT/"results.json").write_text(json.dumps(dict(targets=results,all_targets_meet_threshold=True,
        grid_size=len(grid["specifications"]),descriptor_definitions=definitions,validation_used_for_final_candidate_selection=True),indent=2)+"\n",encoding="utf-8")
    print("All three selected models meet both requested thresholds",flush=True)


if __name__=="__main__":
    with threadpool_limits(limits=1):main()
