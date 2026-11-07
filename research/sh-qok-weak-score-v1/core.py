"""Candidate score estimator. Development uses old synthetic seeds only."""
from pathlib import Path
import importlib.util, hashlib, math, collections, warnings
import numpy as np
from scipy import sparse, stats
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning

ROOT=Path(__file__).resolve().parent.parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('old_a',ROOT/'sh-qok-context-transfer-v1/run.py')
b=module('old_b',ROOT/'sh-qok-context-transfer-v2/run.py')

def null_features(e,model):
    f=a.feature(e,model if model!='F' else 'L')
    if model=='F':
        for d in (-4,-3,3,4):f['additivefar='+str((d,e['context'][str(d)]))]=1.
    return f

def raw_model(events,train,test,model):
    vec=DictVectorizer();x=vec.fit_transform([null_features(events[i],model) for i in train]);xt=vec.transform([null_features(events[i],model) for i in test]);yy=np.array([events[i]['y'] for i in train])
    clf=LogisticRegression(C=.25,solver='liblinear',tol=1e-7,max_iter=2000,random_state=121)
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning);clf.fit(x,yy)
    return np.clip(clf.predict_proba(xt)[:,1],1e-9,1-1e-9)

def baseline(events,tr,te):
    ff=sorted({events[i]['folio'] for i in tr},key=lambda f:hashlib.sha256(('weak-inner|'+f).encode()).hexdigest())
    fit=set(ff[:len(ff)//2]);val=set(ff[len(ff)//2:]);it=[i for i in tr if events[i]['folio'] in fit];iv=[i for i in tr if events[i]['folio'] in val]
    yy=np.array([e['y'] for e in events]);rate=(yy[it].sum()+.5)/(len(it)+1);fallback=np.full(len(iv),rate);weights={}
    for model in ('P','J','L','F'):
        cp=raw_model(events,it,iv,model);w,g=b.mixture_weight(cp,fallback,yy[iv]);weights[model]=w;fallback=(1-w)*fallback+w*cp
    rate=(yy[tr].sum()+.5)/(len(tr)+1);both=tr+te;pred=np.full(len(both),rate)
    for model in ('P','J','L','F'):
        cp=raw_model(events,tr,both,model);w=weights[model];pred=(1-w)*pred+w*cp
    return pred[:len(tr)],pred[len(tr):],dict(weights=weights,inner_fit=sorted(fit),inner_validation=sorted(val))

def score(events):
    fol=sorted({e['folio'] for e in events},key=lambda f:hashlib.sha256(('weak-score-honest|'+f).encode()).hexdigest())
    # Development design: one quarter learns direction; remaining folios test it.
    nt=max(4,math.ceil(len(fol)/4));trainfol=set(fol[:nt]);testfol=set(fol[nt:]);tr=[i for i,e in enumerate(events) if e['folio'] in trainfol];te=[i for i,e in enumerate(events) if e['folio'] in testfol]
    counts=collections.Counter(events[i]['y'] for i in te)
    if len(fol)<10 or len(testfol)<6 or len(tr)<100 or len(te)<200 or min(counts.get(0,0),counts.get(1,0))<30:
        return dict(status='NOT_ESTIMABLE',train_folios=len(trainfol),test_folios=len(testfol),train_n=len(tr),test_n=len(te),test_prefix_counts=dict(counts))
    yy=np.array([e['y'] for e in events]);pt,pe,cal=baseline(events,tr,te)
    vocab={d:[w for w,n in sorted(collections.Counter(events[i]['context'][str(d)] for i in tr).items(),key=lambda z:(-z[1],z[0])) if not w.startswith('<') and n>=8][:12] for d in (-4,-3,3,4)}
    columns=[(d,w) for d in vocab for w in vocab[d]]
    def zmat(ids):
        return np.array([[(int(events[i]['context'][str(d)]==w))*(2*int(events[i]['context']['1'].startswith('qok'))-1) for d,w in columns] for i in ids],dtype=float)
    z=zmat(tr);zt=zmat(te)
    # Project interaction directions onto full local + additive-distant nuisance features.
    v=DictVectorizer();w=v.fit_transform([null_features(events[i],'F') for i in tr]);wt=v.transform([null_features(events[i],'F') for i in te]);w=sparse.hstack([np.ones((len(tr),1)),w],format='csr');wt=sparse.hstack([np.ones((len(te),1)),wt],format='csr')
    lam=math.sqrt(len(tr));kernel=(w@w.T).toarray();alpha=np.linalg.solve(kernel+lam*np.eye(len(tr)),z);rz=z-kernel@alpha;rzt=zt-(wt@w.T)@alpha
    beta=np.linalg.solve(rz.T@rz+lam*np.eye(len(columns)),rz.T@(yy[tr]-pt));direction=rzt@beta;u=(yy[te]-pe)*direction
    by=[]
    for f in sorted(testfol):
        ii=[j for j,i in enumerate(te) if events[i]['folio']==f];by.append(dict(folio=f,n=len(ii),score=float(np.mean(u[ii]))))
    vv=np.array([r['score'] for r in by]);sd=float(vv.std(ddof=1));t=float(vv.mean()/(sd/math.sqrt(len(vv)))) if sd>1e-15 else 0.;p=float(stats.t.sf(t,len(vv)-1)) if sd>1e-15 else 1.
    loss=float(np.mean(-(yy[te]*np.log2(pe)+(1-yy[te])*np.log2(1-pe))));rate=(yy[tr].sum()+.5)/(len(tr)+1);constant=float(np.mean(-(yy[te]*math.log2(rate)+(1-yy[te])*math.log2(1-rate))))
    adequate=loss<=constant+.01
    return dict(status='SCORED',p=p,p4=min(1,p*4),p24=min(1,p*24),flag4=bool(adequate and p*4<=.05),flag24=bool(adequate and p*24<=.05),adequate=adequate,mean_score=float(vv.mean()),t=t,loss=loss,constant=constant,
                train_folios=sorted(trainfol),test_folios=sorted(testfol),train_n=len(tr),test_n=len(te),test_prefix_counts=dict(counts),calibration=cal,vocab=vocab,coefficients=beta.tolist(),per_folio=by,
                heldout=[dict(event=i,folio=events[i]['folio'],y=int(yy[i]),next_qok=events[i]['context']['1'].startswith('qok'),baseline=float(pe[j]),direction=float(direction[j]),score=float(u[j])) for j,i in enumerate(te)])
