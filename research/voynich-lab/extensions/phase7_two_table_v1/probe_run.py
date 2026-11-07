from common import *
import os
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('MKL_NUM_THREADS','2')
from src.train import prepare,fit,load_model
from src.probes import representations,fit_probe
from threadpoolctl import threadpool_limits
import numpy as np,torch
torch.set_num_threads(2)
def scores(name,seed,rows,features):
    sp=split();parts=[sp[r['folio']] for r in rows];result=[]
    for target in ['currier_lang','section']:
        labels=[r.get(target) if target!='currier_lang' or r.get(target) in ['A','B'] else None for r in rows]
        value=fit_probe(features,labels,parts,[.01,.1,1,10]);result.append(dict(corpus=name,seed=seed,target=target,scope='all',**value))
    for label in ['A','B']:
        indices=[i for i,r in enumerate(rows) if r.get('currier_lang')==label]
        value=fit_probe(features[indices],[rows[i].get('section') for i in indices],[parts[i] for i in indices],[.01,.1,1,10]);result.append(dict(corpus=name,seed=seed,target='section',scope=label,**value))
    train=[r for r in rows if sp[r['folio']]=='train' and r.get('section')];majority=Counter(r['section'] for r in train).most_common(1)[0][0];conditional={}
    for label in ['A','B']:
        counts=Counter(r['section'] for r in train if r.get('currier_lang')==label);conditional[label]=counts.most_common(1)[0][0] if counts else majority
    test=[r for r in rows if sp[r['folio']]=='test' and r.get('section')];acc=sum(r['section']==conditional.get(r.get('currier_lang'),majority) for r in test)/len(test)
    result.append(dict(corpus=name,seed=seed,target='section',scope='AB_only_baseline',status='PASS',accuracy=acc,test=len(test),conditional_modal_sections=json.dumps(conditional)))
    return result
def main():
    verify_registration();assert json.loads((R/'HELD_OUT_EVALUATED.json').read_text())['status']=='COMPLETE'
    cfg=json.loads((I/'configs/phase4.json').read_text());sp=split();target=typed(read(LAB/'data/voynich/ZL_running.csv'));output=[];models=[]
    # Qualify the exact historical instrument before interpreting controls.
    with threadpool_limits(limits=2):
        for seed in [1729]:
            path=LAB/'runs/phase4-de886963575d'/f'ZL_running-T1-transformer-p0-s{seed}'
            model,spec=load_model(path/'model.pt',cfg);features=representations(model,target,spec,cfg);del model;torch.cuda.empty_cache()
            rs=scores('ZL',seed,target,features);output.extend(rs);np.savez_compressed(R/f'ZL_features_s{seed}.npz',features=features)
            if seed==1729:
                old=read(LAB/'report/probes.csv');checks=[]
                for target_name in ['currier_lang','section']:
                    a=next(r for r in rs if r['target']==target_name and r['scope']=='all');b=next(r for r in old if r['corpus']=='ZL_running' and r['target']==target_name)
                    fields=['accuracy','balanced_accuracy','majority_baseline','selected_C'];assert all(a[k]==float(b[k]) for k in fields),(a,b);checks.append(dict(target=target_name,exact=True,accuracy=a['accuracy']))
                dump(R/'PROBE_REPLAY_QUALIFICATION.json',dict(status='PASS',checks=checks,original_instrument='Transformer/T1 baseline96, mean line representations, unchanged scaler/logistic/validation selector'))
            print('ZL cached-model probe',seed,flush=True)
        for family in ['C1','C2','C9']:
            for arm in ['two','single']:
                name=family+'_'+arm
                for seed in SEEDS:
                    rows=typed(read(R/'data'/name/f's{seed}.csv'));p=prepare('P7_'+name,'T1',cfg,rows=rows,split=sp);path=I/'runs'/f'{name}-s{seed}'
                    if not (path/'model.pt').exists():
                        model,metric=fit(p,'transformer',False,seed,cfg,path,save_weights=True);del model
                    else:metric=json.loads((path/'metrics.json').read_text())
                    del p;model,spec=load_model(path/'model.pt',cfg);features=representations(model,rows,spec,cfg);del model;torch.cuda.empty_cache()
                    output.extend(scores(name,seed,rows,features));np.savez_compressed(path/'line_features.npz',features=features)
                    models.append({k:v for k,v in metric.items() if k!='curve'});table(R/'probes.csv',output);table(R/'models.csv',models)
                    dump(R/'PROBE_PROGRESS.json',dict(status='RUNNING',completed=len(models),scheduled=30));print('control probes',len(models),'/30',name,seed,flush=True)
    dump(R/'PROBE_PROGRESS.json',dict(status='COMPLETE',completed=30,scheduled=30,new_ZL_models=0,original_ZL_models_reused=1))
if __name__=='__main__':main()
