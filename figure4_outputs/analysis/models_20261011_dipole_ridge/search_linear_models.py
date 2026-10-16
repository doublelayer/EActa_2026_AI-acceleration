from __future__ import annotations
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE.parent / 'models_20261008_linear_ridge_v2'
OUT = HERE / 'linear_model_search'
SEED = 20261008
TARGETS = ('G_OH', 'G_O', 'G_OOH')
ALPHAS = (0.0, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0)
MAX_FEATURES = 12

sys.path.insert(0, str(HERE))
import extended_physical_descriptors as epd


def rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def key(row): return row['name'], row['ads_site']

def number(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else np.nan
    except (TypeError, ValueError):
        return np.nan

def grouped_folds(keys, seed, count):
    names = sorted({name for name, _ in keys})
    np.random.default_rng(seed).shuffle(names)
    bins = [set() for _ in range(count)]
    for i, name in enumerate(names): bins[i % count].add(name)
    return bins

def fill_and_scale(train, held):
    train = np.asarray(train, float).copy(); held = np.asarray(held, float).copy()
    medians = np.asarray([np.median(train[np.isfinite(train[:,j]),j]) if np.isfinite(train[:,j]).any() else 0.0
                          for j in range(train.shape[1])])
    train = np.where(np.isfinite(train), train, medians)
    held = np.where(np.isfinite(held), held, medians)
    mean, scale = train.mean(axis=0), train.std(axis=0)
    scale[scale <= 1e-12] = 1.0
    return (train-mean)/scale, (held-mean)/scale

def ranked_features(x, y, names, limit):
    # All ranking uses only the current training partition.
    raw=np.asarray(x,float).copy()
    medians=np.asarray([np.median(raw[np.isfinite(raw[:,j]),j]) if np.isfinite(raw[:,j]).any() else 0.0
                        for j in range(raw.shape[1])])
    raw=np.where(np.isfinite(raw),raw,medians)
    centered=raw-raw.mean(axis=0)
    centered_y=y-y.mean()
    denom=np.sqrt(np.sum(centered**2,axis=0)*np.sum(centered_y**2))
    corr=np.divide(centered.T@centered_y,denom,out=np.zeros_like(denom),where=denom>1e-12)
    ranked=sorted(range(len(names)),key=lambda j:(-abs(float(corr[j])),names[j]))
    return [j for j in ranked[:limit] if denom[j]>1e-12]

def fit_predict(x_train, x_test, y_train, alpha):
    a,b=fill_and_scale(x_train,x_test)
    ym=float(np.mean(y_train)); yc=y_train-ym
    if alpha == 0:
        coef=np.linalg.lstsq(a,yc,rcond=None)[0]
    else:
        coef=np.linalg.solve(a.T@a+alpha*np.eye(a.shape[1]), a.T@yc)
    return b@coef+ym, coef, ym

def r2(y,p):
    den=float(np.sum((y-y.mean())**2))
    return float(1-np.sum((y-p)**2)/den) if den else float('nan')
def rmse(y,p): return float(np.sqrt(np.mean((y-p)**2)))

def selected_cv(train_keys, x_by_key, y_by_key, features, target, seeds, max_features=MAX_FEATURES):
    # Candidate count and ridge penalty are selected in grouped CV only.
    score_rows=[]
    folds_data=[]
    for seed in seeds:
        for held_names in grouped_folds(train_keys, seed, 4):
            tr=[key for key in train_keys if key[0] not in held_names]
            te=[key for key in train_keys if key[0] in held_names]
            ix=np.asarray([x_by_key[key] for key in tr]); iy=np.asarray([y_by_key[key] for key in tr])
            jx=np.asarray([x_by_key[key] for key in te]); jy=np.asarray([y_by_key[key] for key in te])
            folds_data.append((iy,jy,ix,jx,ranked_features(ix,iy,features,max_features)))
    for k in range(1, min(max_features,len(features))+1):
        for alpha in ALPHAS:
            errors=[]
            for iy,jy,ix,jx,ranking in folds_data:
                cols=ranking[:k]
                pred,_,_=fit_predict(ix[:,cols],jx[:,cols],iy,alpha)
                errors.extend(pred-jy)
            score_rows.append({'target':target,'n_features':k,'alpha':alpha,
                               'grouped_inner_rmse_eV':rmse(np.zeros(len(errors)),np.asarray(errors))})
    best=min(score_rows,key=lambda r:(r['grouped_inner_rmse_eV'],r['n_features'],r['alpha']))
    return best,score_rows


def main():
    try:
        from threadpoolctl import threadpool_limits
        threadpool_limits(limits=1)
    except ImportError:
        pass
    OUT.mkdir(exist_ok=True)
    # Merge independently audited calculated clean-structure feature tables.
    merged={}
    for filename in ('current_site_features.csv','descriptor_correlation_analysis/descriptor_values.csv'):
        for row in rows(HERE/filename):
            k=key(row); merged.setdefault(k,{}).update(row)
    structure_rows={r['name']:r for r in rows(ROOT/'extracted/structures_by_target.csv')}
    for k in list(merged):
        name,site=k; ix=int(site[-1])-1
        merged[k].update(epd.compute(structure_rows[name],ix))
    excluded={'name','ads_site','source_db','source_db_id','neighbor_rule'}
    excluded.update(f for f in (merged[next(iter(merged))]) if 'electronegativity' in f.lower())
    excluded.update({'shared_ligand_count','terminal_ligand_count'})
    # Keep the full numeric candidate catalogue. A feature becomes eligible in
    # each fold only if it varies and has enough finite training values.
    features=[field for field in merged[next(iter(merged))] if field not in excluded]
    labels={key(r):r for r in rows(ROOT/'extracted/orr_analysis_energies.csv')}
    cv_all=rows(HERE/'cv_predictions.csv'); val_all=rows(HERE/'validation_predictions.csv')
    out_metrics=[]; cv_predictions=[]; val_predictions=[]; choices=[]; all_inner=[]; train_fit_rows=[]; final_parameters=[]
    for target in TARGETS:
        cv=[r for r in cv_all if r['target']==target]
        val=[r for r in val_all if r['target']==target]
        train_keys=sorted({key(r) for r in cv}); val_keys=sorted({key(r) for r in val})
        if {k[0] for k in train_keys}&{k[0] for k in val_keys}: raise ValueError(f'train/validation overlap for {target}')
        x_by_key={k:np.asarray([number(merged[k].get(f)) for f in features]) for k in train_keys+val_keys}
        y_by_key={k:number(labels[k][target]) for k in train_keys+val_keys}
        if any(not np.isfinite(y_by_key[k]) for k in train_keys+val_keys): raise ValueError(f'non-finite label in saved cohort {target}')
        current_repeat_predictions=[]
        for repeat in sorted({int(r['repeat']) for r in cv}):
            fold_map={key(r):int(r['fold']) for r in cv if int(r['repeat'])==repeat}
            if set(fold_map)!=set(train_keys): raise ValueError(f'incomplete saved folds {target} repeat {repeat}')
            for name in {k[0] for k in train_keys}:
                if len({fold_map[k] for k in train_keys if k[0]==name})!=1: raise ValueError(f'fold split structure {name}')
            for fold in sorted(set(fold_map.values())):
                outer_train=[k for k in train_keys if fold_map[k]!=fold]
                outer_test=[k for k in train_keys if fold_map[k]==fold]
                best,inner=selected_cv(outer_train,x_by_key,y_by_key,features,target,
                    [SEED+repeat*10007+fold*101],max_features=MAX_FEATURES)
                all_inner.extend([{**r,'outer_repeat':repeat,'outer_fold':fold} for r in inner])
                tr_x=np.asarray([x_by_key[k] for k in outer_train]); tr_y=np.asarray([y_by_key[k] for k in outer_train])
                te_x=np.asarray([x_by_key[k] for k in outer_test]); te_y=np.asarray([y_by_key[k] for k in outer_test])
                cols=ranked_features(tr_x,tr_y,features,int(best['n_features']))
                pred,_,_=fit_predict(tr_x[:,cols],te_x[:,cols],tr_y,float(best['alpha']))
                choices.append({'target':target,'repeat':repeat,'fold':fold,'n_features':best['n_features'],
                    'alpha':best['alpha'],'inner_grouped_rmse_eV':best['grouped_inner_rmse_eV'],
                    'features':';'.join(features[j] for j in cols)})
                for k,p in zip(outer_test,pred):
                    row={'target':target,'repeat':repeat,'fold':fold,'name':k[0],'ads_site':k[1],
                         'observed_eV':y_by_key[k],'predicted_eV':float(p),'error_eV':float(p-y_by_key[k])}
                    cv_predictions.append(row); current_repeat_predictions.append(row)
        # Select final model on three repeated four-fold grouped CV runs over training only.
        final,selections=selected_cv(train_keys,x_by_key,y_by_key,features,target,
                                     [SEED+811+i*10007 for i in range(3)])
        all_inner.extend([{**r,'outer_repeat':'final_training_selection','outer_fold':''} for r in selections])
        train_x=np.asarray([x_by_key[k] for k in train_keys]); train_y=np.asarray([y_by_key[k] for k in train_keys])
        validation_x=np.asarray([x_by_key[k] for k in val_keys]); validation_y=np.asarray([y_by_key[k] for k in val_keys])
        final_cols=ranked_features(train_x,train_y,features,int(final['n_features']))
        val_pred,coef,ym=fit_predict(train_x[:,final_cols],validation_x[:,final_cols],train_y,float(final['alpha']))
        train_pred,_,_=fit_predict(train_x[:,final_cols],train_x[:,final_cols],train_y,float(final['alpha']))
        selected_train=train_x[:,final_cols].copy()
        medians=np.asarray([np.median(selected_train[np.isfinite(selected_train[:,j]),j]) if np.isfinite(selected_train[:,j]).any() else 0.0
                            for j in range(selected_train.shape[1])])
        selected_train=np.where(np.isfinite(selected_train),selected_train,medians)
        means,scales=selected_train.mean(axis=0),selected_train.std(axis=0)
        scales[scales<=1e-12]=1.0
        final_parameters.append({'target':target,'term':'intercept','standardized_coefficient':ym,
                                 'training_median':'','training_mean':'','training_sd':'','ridge_alpha':float(final['alpha'])})
        for feature_index, descriptor_index in enumerate(final_cols):
            final_parameters.append({'target':target,'term':features[descriptor_index],
                'standardized_coefficient':float(coef[feature_index]),'training_median':float(medians[feature_index]),
                'training_mean':float(means[feature_index]),'training_sd':float(scales[feature_index]),
                'ridge_alpha':float(final['alpha'])})
        fold_repeats=[]
        for repeat in sorted({r['repeat'] for r in current_repeat_predictions}):
            part=[r for r in current_repeat_predictions if r['repeat']==repeat]
            yy=np.asarray([r['observed_eV'] for r in part]); pp=np.asarray([r['predicted_eV'] for r in part])
            fold_repeats.append(r2(yy,pp))
        pooled_y=np.asarray([r['observed_eV'] for r in current_repeat_predictions])
        pooled_p=np.asarray([r['predicted_eV'] for r in current_repeat_predictions])
        out_metrics.append({'target':target,'training_sites':len(train_keys),'training_structures':len({k[0] for k in train_keys}),
            'validation_sites':len(val_keys),'validation_structures':len({k[0] for k in val_keys}),
            'selected_predictors':int(final['n_features']),'ridge_alpha':float(final['alpha']),
            'training_R2':r2(train_y,train_pred),'mean_repeat_R2cv':float(np.mean(fold_repeats)),
            'pooled_repeated_OOF_R2':r2(pooled_y,pooled_p),'validation_R2':r2(validation_y,val_pred),
            'mean_repeat_RMSEcv_eV':float(np.mean([rmse(np.asarray([r['observed_eV'] for r in current_repeat_predictions if r['repeat']==rep]),np.asarray([r['predicted_eV'] for r in current_repeat_predictions if r['repeat']==rep])) for rep in sorted({r['repeat'] for r in current_repeat_predictions})])),
            'validation_RMSE_eV':rmse(validation_y,val_pred),'inner_grouped_RMSE_eV':float(final['grouped_inner_rmse_eV']),
            'final_features':';'.join(features[j] for j in final_cols)})
        for k,p in zip(val_keys,val_pred):
            val_predictions.append({'target':target,'name':k[0],'ads_site':k[1],'observed_eV':y_by_key[k],
                                    'predicted_eV':float(p),'error_eV':float(p-y_by_key[k])})
        for k,p in zip(train_keys,train_pred):
            train_fit_rows.append({'target':target,'name':k[0],'ads_site':k[1],'observed_eV':y_by_key[k],
                                   'predicted_eV':float(p),'error_eV':float(p-y_by_key[k])})
        print(target, 'features',int(final['n_features']),'alpha',final['alpha'],
              'train R2',round(out_metrics[-1]['training_R2'],3),'CV R2',round(out_metrics[-1]['mean_repeat_R2cv'],3),
              'validation R2',round(out_metrics[-1]['validation_R2'],3),flush=True)
    pd.DataFrame(out_metrics).to_csv(OUT/'metrics.csv',index=False)
    pd.DataFrame(cv_predictions).to_csv(OUT/'nested_cv_predictions.csv',index=False)
    pd.DataFrame(val_predictions).to_csv(OUT/'validation_predictions.csv',index=False)
    pd.DataFrame(train_fit_rows).to_csv(OUT/'training_fit_predictions.csv',index=False)
    pd.DataFrame(choices).to_csv(OUT/'outer_fold_selections.csv',index=False)
    pd.DataFrame(all_inner).to_csv(OUT/'inner_search_scores.csv',index=False)
    pd.DataFrame(final_parameters).to_csv(OUT/'final_model_parameters.csv',index=False)
    report=['# Target specific linear model search','',
      'Searches OLS and ridge regressions on calculated clean-structure descriptors. Candidate feature count (1–12), feature ranking, and ridge strength are selected using structure-grouped CV within each training partition. The feature ranking uses absolute training-only Pearson correlation. The intercept is unpenalized; missing predictors use training medians and predictors are standardized from training rows only. No kernel or tree model is included.','',
      'Training and validation membership come from the saved `cv_predictions.csv` and `validation_predictions.csv` for the three dipole models. Their inherited outlier and geometry exclusions are left unchanged; validation labels do not select descriptors or hyperparameters in this search. The OH/O models inherit training-only OOF pruning of `KMC_Mn_Mn_A2_B1_NNNNNN_q2`, `KMC_Mn_Co_A2_B1_NNNNNN_q2`, and `KMC_Cr_Cr_A2_B2_NNNNOO_q2`. OOH inherits a separate ten-structure pruning path recorded in `../models_20261008_linear_ridge_v2/ooh_focused_best_model_set.json`; its selected pruning count was chosen after examining validation. OOH validation performance is therefore selection-influenced. The independent search results for other cohort files in this directory are not used here.','',
      '## Results','',
      '| Target | Training R² | Mean repeated grouped R²cv | Pooled OOF R² | Validation R² | Predictors | Alpha | Training rows / structures |','|---|---:|---:|---:|---:|---:|---:|---|']
    for r in out_metrics:
        report.append(f"| {r['target']} | {r['training_R2']:.3f} | {r['mean_repeat_R2cv']:.3f} | {r['pooled_repeated_OOF_R2']:.3f} | {r['validation_R2']:.3f} | {r['selected_predictors']} | {r['ridge_alpha']:g} | {r['training_sites']} / {r['training_structures']} |")
    report += ['', 'A target meets the stated training and CV goal only when both `training_R2` and `mean_repeat_R2cv` exceed 0.90. Validation R² is reported as a final check, not used for model selection. `nested_cv_predictions.csv` contains outer held-out predictions from the feature/alpha selection process; `outer_fold_selections.csv` records each outer-fold equation. `inner_search_scores.csv` contains selection scores. The final descriptor list and performance are in `metrics.csv`.','',
      'Feature candidates are numeric descriptors calculated from clean catalyst coordinates, Bader charges, and magnetic moments. Element-property lookup fields, categorical metal labels, ligand counts, and adsorption-state descriptors are excluded. N/O/S neighbor summaries remain pooled. Existing target cohorts differ where the saved model cohorts differ. `final_model_parameters.csv` stores the standardized coefficients and training-only imputation/scaling values for each final equation.','']
    (OUT/'report.md').write_text('\n'.join(report),encoding='utf-8')
    (OUT/'search_config.json').write_text(json.dumps({'cohort_source':'saved current-model cv_predictions.csv and validation_predictions.csv',
       'feature_source':['current_site_features.csv','descriptor_correlation_analysis/descriptor_values.csv','extended_physical_descriptors.compute'],
       'feature_filter':'numeric clean-structure descriptors; exclude empirical lookup, categorical, counts',
       'feature_selection':'training-only absolute Pearson ranking; k=1..12', 'models':['OLS','Ridge'],
       'ridge_alphas':ALPHAS,'outer_repeats':3,'outer_folds':5,'inner_repeats_final':3,'inner_folds':4,
       'group':'catalyst name','seed':SEED,'validation_used_for_selection':False},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
