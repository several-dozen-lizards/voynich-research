"""Nested physical-folio CV. Manuscript execution requires a completed freeze and gates."""
from common import *
import argparse
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss, balanced_accuracy_score

GRID=(.01,.1,1.,10.)

def folds(groups,n):
    unique=sorted(set(groups),key=lambda g:digest('v6-fold:'+g))
    n=min(n,len(unique))
    if n<2: raise ValueError('Insufficient physical folios')
    for k in range(n):
        held=set(unique[k::n]); test=np.array([i for i,g in enumerate(groups) if g in held])
        train=np.array([i for i,g in enumerate(groups) if g not in held])
        assert not set(groups[train])&set(groups[test])
        yield train,test

def fit_predict(X,y,train,test,C,classes):
    if set(y[train])!=set(classes): raise ValueError('Training fold lacks an eligible class')
    model=make_pipeline(DictVectorizer(),StandardScaler(with_mean=False),
                        LogisticRegression(C=C,penalty='l2',solver='lbfgs',max_iter=1500,tol=1e-6))
    model.fit([X[i] for i in train],y[train])
    if np.max(model[-1].n_iter_)>=1500: raise ValueError('Convergence failure; no silent scored fit')
    probs=model.predict_proba([X[i] for i in test])
    assert list(model[-1].classes_)==list(classes)
    return probs

def page_prior(y,pages,classes):
    ci={c:i for i,c in enumerate(classes)}; result=[]
    for i,page in enumerate(pages):
        peers=[j for j,p in enumerate(pages) if p==page and j!=i]
        counts=Counter(y[j] for j in peers)
        result.append([(counts[c]+.5)/(len(peers)+.5*len(classes)) for c in classes])
    return np.array(result)

def evaluate(X,y,groups,pages):
    y=np.asarray(y);groups=np.asarray(groups);classes=np.unique(y);pred=np.zeros((len(y),len(classes)))
    if len(classes)<2: raise ValueError('At least two classes required')
    tuning=[]
    for train,test in folds(groups,5):
        best=None
        for C in GRID:
            losses=[];weights=[]
            for itrain,itest in folds(groups[train],4):
                tr,te=train[itrain],train[itest]
                probabilities=fit_predict(X,y,tr,te,C,classes)
                losses.append(log_loss(y[te],probabilities,labels=classes));weights.append(len(te))
            loss=float(np.average(losses,weights=weights))
            if best is None or loss<best[0]-1e-12: best=(loss,C)
        pred[test]=fit_predict(X,y,train,test,best[1],classes)
        tuning.append(dict(test_folios=sorted(set(groups[test])),C=best[1],inner_log_loss=best[0]))
    prior=page_prior(y,pages,classes)
    ll=float(log_loss(y,pred,labels=classes));base=float(log_loss(y,prior,labels=classes))
    return dict(gain=base-ll,log_loss=ll,page_prior_log_loss=base,
                balanced_accuracy=float(balanced_accuracy_score(y,classes[np.argmax(pred,axis=1)])),
                page_prior_balanced_accuracy=float(balanced_accuracy_score(y,classes[np.argmax(prior,axis=1)])),
                tuning=tuning)

def permute(y,pages,rng):
    out=np.array(y).copy()
    for p in sorted(set(pages)):
        ix=np.flatnonzero(np.array(pages)==p);out[ix]=rng.permutation(out[ix])
        assert Counter(out[ix])==Counter(np.array(y)[ix])
    return out

def test(X,y,groups,pages,nperm=5000,seed=60624):
    observed=evaluate(X,y,groups,pages);rng=np.random.default_rng(seed);null=[]
    for i in range(nperm):
        null.append(evaluate(X,permute(y,pages,rng),groups,pages)['gain'])
    observed.update(permutations=nperm,seed=seed,null_gains=null,
                    p_raw=(1+sum(v>=observed['gain']-1e-12 for v in null))/(nperm+1))
    return observed

def holm(ps):
    order=sorted(range(len(ps)),key=lambda i:ps[i]);adjusted=[0.]*len(ps);prior=0
    for rank,i in enumerate(order):
        prior=max(prior,min(1.,(len(ps)-rank)*ps[i]));adjusted[i]=prior
    return adjusted

def run():
    protocol=load(ROOT/'PROTOCOL.json')
    if protocol['claim_freeze_status']!='FROZEN': raise ValueError('Incomplete claim freeze')
    freeze=load(ROOT/'FREEZE.json')
    if any(sha(ROOT/p)!=h for p,h in freeze['hashes'].items()): raise ValueError('Changed frozen files')
    if not load(ROOT/'QUALIFICATION.json').get('scientific_gate_passed'): raise ValueError('Controls not qualified')
    if not (ROOT/'OUTCOME-JOIN.json').exists(): raise ValueError('No gated object join')
    objects={r['task_id']:r['class'] for r in read_csv(ROOT/'LABEL-OBJECTS.csv')}
    inventory={r['task_id']:r for r in read_csv(ROOT/'LABEL-INVENTORY.csv')}
    feats=read_csv(ROOT/'FEATURES.csv');panels=defaultdict(list)
    for r in feats:
        c=objects.get(r['task_id']);meta=inventory[r['task_id']]
        if c and c not in ['NONE','UNCLEAR','OTHER','EXCLUDED_COLLAPSE'] and r['eligible']=='True':
            panels[(r['reading'],meta['section'])].append((r,meta,c))
    results=[]
    for (reading,section),rr in sorted(panels.items()):
        classes=sorted({c for _,_,c in rr if sum(v==c for _,_,v in rr)>=30 and
                        len({m['folio'] for _,m,v in rr if v==c})>=6})
        rr=[r for r in rr if r[2] in classes]
        item=dict(reading=reading,section=section,eligible_classes=classes,n=len(rr))
        if len(classes)<2: item.update(status='NOT_ESTIMABLE_CLASS_SUPPORT')
        else:
            try:
                result=test([json.loads(r['features']) for r,_,_ in rr],[c for _,_,c in rr],
                            [m['folio'] for _,m,_ in rr],[m['page'] for _,m,_ in rr])
                item.update(status='ESTIMATED',**result)
            except ValueError as e: item.update(status='NOT_ESTIMABLE',reason=str(e))
        results.append(item)
    for reading in ['H','F']:
        rr=[r for r in results if r['reading']==reading and r['status']=='ESTIMATED']
        for r,p in zip(rr,holm([r['p_raw'] for r in rr])):
            r.update(p_holm=p,passed=bool(p<=.05 and r['gain']>0))
    headline=[s for s in {r['section'] for r in results} if all(any(r['section']==s and r['reading']==t and r.get('passed') for r in results) for t in ['H','F'])]
    save(ROOT/'T1.json',dict(status='COMPLETED',panels=results,headline_sections=headline,
                            interpretation='Conditional predictive association; no word meaning or unique naming mechanism.'))

if __name__=='__main__': run()
