from pathlib import Path
import importlib.util, json, hashlib, math, sys, warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning

R=Path(__file__).resolve().parent
APATH=R.parent/'sh-qok-context-transfer-v1/run.py'
spec=importlib.util.spec_from_file_location('frozen_context_v1',APATH)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
a.R=R

def mixture_weight(candidate,fallback,y):
    d=candidate-fallback
    def derivative(w):
        p=np.clip(fallback+w*d,1e-9,1-1e-9)
        return float(np.mean(d*(p-y)/(p*(1-p))))
    if derivative(0)>=0:w=0.
    elif derivative(1)<=0:w=1.
    else:
        lo,hi=0.,1.
        for _ in range(60):
            mid=(lo+hi)/2
            if derivative(mid)<0:lo=mid
            else:hi=mid
        w=(lo+hi)/2
    def loss(p):return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))
    gain=loss(fallback)-loss(np.clip(fallback+w*d,1e-9,1-1e-9))
    return (w if gain>1/len(y) else 0.),gain

def raw_fit(events,tr,te,model,yy):
    vec=DictVectorizer();x=vec.fit_transform([a.feature(events[i],model) for i in tr]);xt=vec.transform([a.feature(events[i],model) for i in te])
    clf=LogisticRegression(C=.25,solver='liblinear',tol=1e-7,max_iter=2000,random_state=121)
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning);clf.fit(x,yy[tr])
    return np.clip(clf.predict_proba(xt)[:,1],1e-9,1-1e-9)

def fit_score(events):
    fm=a.foldmap(events);yy=np.array([e['y'] for e in events]);preds=[None]*len(events)
    for fold in range(5):
        tr=[i for i,e in enumerate(events) if fm[e['folio']]!=fold];te=[i for i,e in enumerate(events) if fm[e['folio']]==fold]
        tf=sorted({events[i]['folio'] for i in tr},key=lambda x:hashlib.sha256(('inner|'+x).encode()).hexdigest())
        fitfolios=set(tf[:len(tf)//2]);valfolios=set(tf[len(tf)//2:]);it=[i for i in tr if events[i]['folio'] in fitfolios];iv=[i for i in tr if events[i]['folio'] in valfolios]
        assert fitfolios.isdisjoint(valfolios) and (fitfolios|valfolios).isdisjoint({events[i]['folio'] for i in te})
        assert len(set(yy[it]))==2 and len(set(yy[tr]))==2
        base=(yy[it].sum()+.5)/(len(it)+1);fallback=np.full(len(iv),base);weights={};vgains={}
        for model in a.MODELS:
            candidate=raw_fit(events,it,iv,model,yy);w,gain=mixture_weight(candidate,fallback,yy[iv]);weights[model]=w;vgains[model]=gain
            fallback=(1-w)*fallback+w*candidate
        rate=(yy[tr].sum()+.5)/(len(tr)+1);probs={'constant':np.full(len(te),rate)};raw={};fallback=probs['constant']
        for model in a.MODELS:
            raw[model]=raw_fit(events,tr,te,model,yy);w=weights[model];probs[model]=(1-w)*fallback+w*raw[model];fallback=probs[model]
        known={a.sig(events[i]) for i in tr}
        calibration=dict(inner_fit_folios=sorted(fitfolios),inner_validation_folios=sorted(valfolios),weights=weights,validation_gain_nats=vgains,validation_n=len(iv))
        for j,i in enumerate(te):
            pr={m:float(v[j]) for m,v in probs.items()};y=yy[i]
            preds[i]=dict(fold=fold,novel=a.sig(events[i]) not in known,probability=pr,raw_probability={m:float(v[j]) for m,v in raw.items()},
                          calibration=calibration,loss={m:float(-math.log2(p if y else 1-p)) for m,p in pr.items()})
    return a.summarize(events,preds),preds,fm

def worker(regime,trial):
    seed=1220000+('position','junction','phrase','distant_strong','distant_small').index(regime)*1000+trial
    ev=a.generate(regime,seed);scores,preds,fm=fit_score(ev)
    return dict(regime=regime,trial=trial,seed=seed,scores=scores,predictions=preds,folds=fm)

def qualify():
    a.verify();a.log('qualification_start');a.engineering()
    # Boundary and optimum checks for the new convex combination procedure.
    w,_=mixture_weight(np.array([.9,.1]),np.array([.5,.5]),np.array([1,0]));assert w==1
    w,_=mixture_weight(np.array([.1,.9]),np.array([.5,.5]),np.array([1,0]));assert w==0
    a.save('BACKOFF-CHECKS.json',dict(status='PASS',good_endpoint=1,bad_endpoint=0,selection_has_no_outer_test_argument=True))
    records=[];summary=[];regimes=('position','junction','phrase','distant_strong','distant_small')
    for regime in regimes:
        with ProcessPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(worker,regime,t) for t in range(60)]
            for future in as_completed(futures):
                record=future.result();a.save(f'synthetic/{regime}-{record["trial"]:02d}.json',record)
                records.append({k:v for k,v in record.items() if k not in ('predictions','folds')})
                n=sum(x['regime']==regime for x in records)
                if n%10==0:print(regime,n,'/60',flush=True)
        rr=[r for r in records if r['regime']==regime]
        for view in ('all','novel'):
            ss=[next(s for s in r['scores'] if s['view']==view and s['contrast']=='G-L') for r in rr];k=sum(s['flag'] for s in ss);bounds=a.ci(k,len(ss));gate=None
            if view=='all' and regime in regimes[:3]:gate=bounds[1]<=.10
            if view=='all' and regime=='distant_strong':gate=bounds[0]>=.80
            summary.append(dict(regime=regime,view=view,trials=len(ss),supported=sum(s['supported'] for s in ss),flags=k,wilson95=bounds,mean_gain=float(np.mean([s['gain_bits'] for s in ss])),required_gate=gate))
        a.save('QUALIFICATION-PROGRESS.json',summary)
    passed=all(s['required_gate'] is not False for s in summary)
    a.save('QUALIFICATION.json',dict(status='PASS_LIMITED' if passed else 'FAIL',results=summary,limits='Training-selected backoff; authored synthetic mechanisms, not general grammar or manuscript-sized power.'))
    a.verify();a.log('qualification_complete',status='PASS_LIMITED' if passed else 'FAIL');print('QUALIFICATION', 'PASS_LIMITED' if passed else 'FAIL',flush=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='freeze':
        assert not (R/'FREEZE.json').exists()
        paths=[R/'run.py',R/'PROTOCOL.md',APATH,APATH.parent/'PROTOCOL.md',APATH.parent/'FREEZE.json',APATH.parent/'QUALIFICATION.json',a.SOURCE,a.ROOT/'complete-atlas-v56/SOURCE-MANIFEST.json',a.ROOT/'sh-qok-ending-qualification-reed-v94/PROTOCOL.json',a.ROOT/'sh-qok-ending-qualification-reed-v94/run.py']
        a.save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):a.sha(p) for p in paths}));a.log('freeze_complete');(R/'synthetic').mkdir();print('FROZEN B')
    elif mode=='qualify':qualify()
    elif mode=='manuscript':
        a.fit_score=fit_score;a.manuscript()
    else:raise ValueError(mode)
