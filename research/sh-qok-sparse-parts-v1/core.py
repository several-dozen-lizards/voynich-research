from pathlib import Path
import importlib.util,collections,hashlib,math,json,warnings
import numpy as np
from scipy import sparse,stats
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning

ROOT=Path(__file__).resolve().parent.parent
def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
prior=module('frozen_nuisance_v2',ROOT/'sh-qok-weak-score-v2/core.py')
a,b=prior.a,prior.b
OFFSETS=(-4,-3,3,4)
FAMILIES=('p1','p2','s1','s2','word')

def parts(w):
    if w.startswith('<'):return {'missing':w}
    return dict(p1=w[:1],p2=w[:2],s1=w[-1:],s2=w[-2:],word=w)

def features(e,model):
    f=prior.null_features(e,model)
    def add(name,*values):f[name+'='+json.dumps(values,separators=(',',':'))]=1.
    def addparts(tag,w):
        for family,value in parts(w).items():add('part',tag,family,value)
        if not w.startswith('<'):f['#loglen:'+str(tag)]=math.log1p(len(w))
    addparts('body',e['body']);x=e['index']/max(1,e['length']-1);f['#position']=x;f['#position2']=x*x
    if model in ('J','L','F'):
        for family,value in parts(e['body']).items():add('bodypart-junction',family,value,e['context']['1'][:3])
    if model in ('L','F'):
        for d in (-2,-1,1,2):addparts(d,e['context'][str(d)])
        for d in (-1,1):
            for family in ('p2','s2'):
                lp=parts(e['context'][str(d)]);bp=parts(e['body'])
                if family in lp:add('localpart-pair',d,family,bp.get(family),lp[family])
    if model=='F':
        for d in OFFSETS:addparts(d,e['context'][str(d)])
    return f

def cache_features(events):return {m:[features(e,m) for e in events] for m in ('P','J','L','F')}

def fitted_matrix(cache,tr,te,model):
    counts=collections.Counter(k for i in tr for k in cache[model][i]);keep={k for k,n in counts.items() if k.startswith('#') or n>=8}
    vec=DictVectorizer();x=vec.fit_transform([{k:v for k,v in cache[model][i].items() if k in keep} for i in tr]);xt=vec.transform([{k:v for k,v in cache[model][i].items() if k in keep} for i in te])
    return x,xt

def raw_fit(events,tr,te,model,cache):
    x,xt=fitted_matrix(cache,tr,te,model);y=[events[i]['y'] for i in tr]
    clf=LogisticRegression(C=.25,solver='liblinear',tol=1e-7,max_iter=2000,random_state=121)
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning);clf.fit(x,y)
    return np.clip(clf.predict_proba(xt)[:,1],1e-9,1-1e-9)

def split(events):
    fs=sorted({e['folio'] for e in events},key=lambda f:hashlib.sha256(('weak-score-honest|'+f).encode()).hexdigest());nt=max(4,math.ceil(len(fs)/4));learn=set(fs[:nt]);test=set(fs[nt:])
    return [i for i,e in enumerate(events) if e['folio'] in learn],[i for i,e in enumerate(events) if e['folio'] in test],learn,test

def baseline(events,tr,te,cache):
    y=np.array([e['y'] for e in events]);fs=sorted({events[i]['folio'] for i in tr});pos={i:j for j,i in enumerate(tr)};oof={m:np.zeros(len(tr)) for m in ('constant','P','J','L','F')};assign=[]
    for f in fs:
        it=[i for i in tr if events[i]['folio']!=f];iv=[i for i in tr if events[i]['folio']==f];jj=[pos[i] for i in iv];rate=(y[it].sum()+.5)/(len(it)+1);oof['constant'][jj]=rate
        for m in ('P','J','L','F'):oof[m][jj]=raw_fit(events,it,iv,m,cache)
        assign.append(dict(validation_folio=f,fit_folios=[g for g in fs if g!=f],validation_events=len(iv)))
    penalty=(.5*math.log(len(tr))+math.log(4))/len(tr);choices=[]
    for m in ('P','J','L','F'):
        w,gain=b.mixture_weight(oof[m],oof['constant'],y[tr]);mix=(1-w)*oof['constant']+w*oof[m]
        event_gain=np.where(y[tr],np.log(mix/oof['constant']),np.log((1-mix)/(1-oof['constant'])))
        fg=[float(np.mean([event_gain[pos[i]] for i in tr if events[i]['folio']==f])) for f in fs]
        se=float(np.std(fg,ddof=1)/math.sqrt(len(fs)));lower=float(np.mean(fg)-stats.t.ppf(.95,len(fs)-1)*se)
        choices.append(dict(model=m,weight=float(w),pooled_gain_nats=float(gain),folio_gains=fg,lower95_gain_nats=lower,penalized_lower=lower-penalty))
    best=max(choices,key=lambda c:c['penalized_lower']);selected=best['model'] if best['penalized_lower']>0 else 'constant';weight=best['weight'] if selected!='constant' else 0.;rate=(y[tr].sum()+.5)/(len(tr)+1)
    raw=raw_fit(events,tr,tr+te,selected,cache) if selected!='constant' else np.full(len(tr)+len(te),rate);pred=(1-weight)*rate+weight*raw
    cal=dict(method='shared parts and folio-uncertainty OOF backoff',learning_events=tr,learning_y=y[tr].astype(int).tolist(),learning_folios=fs,assignments=assign,oof={m:v.tolist() for m,v in oof.items()},candidates=choices,penalty_nats=penalty,selected=selected,weight=float(weight),full_learning_constant=float(rate),selected_raw_probabilities=raw.tolist())
    return pred[:len(tr)],pred[len(tr):],cal

def value(e,desc):
    w=e['context'][str(desc['offset'])]
    if w.startswith('<'):return 0.
    if desc['family']=='loglen':return (math.log1p(len(w))-desc['mean'])/desc['sd']
    return float(parts(w).get(desc['family'])==desc['value'])

def design(events,tr,te,cache):
    descriptors=[]
    for d in OFFSETS:
        ws=[events[i]['context'][str(d)] for i in tr if not events[i]['context'][str(d)].startswith('<')]
        for fam in FAMILIES:
            counts=collections.Counter(parts(w)[fam] for w in ws)
            for v,n in sorted(counts.items(),key=lambda z:(-z[1],z[0])):
                if n>=8 and sum(x['offset']==d and x['family']==fam for x in descriptors)<12:descriptors.append(dict(offset=d,family=fam,value=v,count=n))
        lens=np.array([math.log1p(len(w)) for w in ws])
        if len(lens) and lens.std()>1e-12:descriptors.append(dict(offset=d,family='loglen',mean=float(lens.mean()),sd=float(lens.std())))
    def zm(ids):return np.array([[value(events[i],desc)*(2*int(events[i]['context']['1'].startswith('qok'))-1) for desc in descriptors] for i in ids],dtype=float).reshape(len(ids),len(descriptors))
    z,zt=zm(tr),zm(te);w,wt=fitted_matrix(cache,tr,te,'F');w=sparse.hstack([np.ones((len(tr),1)),w],format='csr');wt=sparse.hstack([np.ones((len(te),1)),wt],format='csr');lam=math.sqrt(len(tr));kernel=(w@w.T).toarray();alpha=np.linalg.solve(kernel+lam*np.eye(len(tr)),z);rz=z-kernel@alpha;rzt=zt-(wt@w.T)@alpha
    return descriptors,rz,rzt,lam

def prepare_profile(template):
    tr,te,learn,test=split(template);cache=cache_features(template);desc,rz,_,_=design(template,tr,te,cache)
    candidates=[]
    for j,d in enumerate(desc):
        if d['family']=='loglen':continue
        vv=np.array([value(template[i],d) for i in tr])
        if sum(vv)>=8 and sum(1-vv)>=8:candidates.append((float(np.mean(rz[:,j]**2)),j))
    if not candidates:raise RuntimeError('No support for a matched positive cue; no synthetic labels generated.')
    variance,j=max(candidates,key=lambda x:x[0]);cue=desc[j];cv=np.array([value(template[i],cue) for i in tr]);near=[]
    for d in (-1,1):
        for fam in ('p1','p2','s1','s2'):
            vals=collections.Counter(parts(template[i]['context'][str(d)]).get(fam) for i in tr)
            for v,n in sorted(vals.items(),key=lambda x:str(x[0])):
                if v is None or n<8 or len(tr)-n<8:continue
                de=dict(offset=d,family=fam,value=v);bits=np.array([value(template[i],de) for i in tr]);corr=float(np.corrcoef(cv,bits)[0,1]) if cv.std()>0 and bits.std()>0 else 0.
                near.append((abs(corr),de,corr))
    _,near_desc,corr=max(near,key=lambda x:x[0])
    return dict(learning_events=tr,test_events=te,learning_folios=sorted(learn),testing_folios=sorted(test),cue=cue,cue_residual_variance=variance,proxy_local=near_desc,proxy_learning_correlation=corr,body_length_median=float(np.median([len(template[i]['body']) for i in tr])),position_median=float(np.median([template[i]['index']/max(1,template[i]['length']-1) for i in tr])),remote_feature_count=len(desc),central_labels_used=False)

def score(events):
    tr,te,learn,test=split(events);counts=collections.Counter(events[i]['y'] for i in te)
    if len(learn|test)<10 or len(test)<6 or len(tr)<100 or len(te)<200 or min(counts.get(0,0),counts.get(1,0))<30:return dict(status='NOT_ESTIMABLE',train_n=len(tr),test_n=len(te),reason='unchanged count support gate')
    cache=cache_features(events);pt,pe,cal=baseline(events,tr,te,cache);desc,rz,rzt,lam=design(events,tr,te,cache);y=np.array([e['y'] for e in events]);beta=np.linalg.solve(rz.T@rz+lam*np.eye(len(desc)),rz.T@(y[tr]-pt));direction=rzt@beta;u=(y[te]-pe)*direction;by=[]
    for f in sorted(test):
        ii=[j for j,i in enumerate(te) if events[i]['folio']==f];by.append(dict(folio=f,n=len(ii),score=float(np.mean(u[ii]))))
    vv=np.array([r['score'] for r in by]);sd=float(vv.std(ddof=1));t=float(vv.mean()/(sd/math.sqrt(len(vv)))) if sd>1e-15 else 0.;p=float(stats.t.sf(t,len(vv)-1)) if sd>1e-15 else 1.
    loss=float(np.mean(-(y[te]*np.log2(pe)+(1-y[te])*np.log2(1-pe))));rate=(y[tr].sum()+.5)/(len(tr)+1);constant=float(np.mean(-(y[te]*math.log2(rate)+(1-y[te])*math.log2(1-rate))));adequate=loss<=constant+.01
    return dict(status='SCORED',p=p,p4=min(1,p*4),p24=min(1,p*24),flag4=bool(adequate and p*4<=.05),flag24=bool(adequate and p*24<=.05),adequate=adequate,mean_score=float(vv.mean()),t=t,loss=loss,constant=constant,train_folios=sorted(learn),test_folios=sorted(test),train_n=len(tr),test_n=len(te),test_prefix_counts=dict(counts),calibration=cal,descriptors=desc,coefficients=beta.tolist(),per_folio=by,heldout=[dict(event=i,folio=events[i]['folio'],y=int(y[i]),next_qok=events[i]['context']['1'].startswith('qok'),baseline=float(pe[j]),direction=float(direction[j]),score=float(u[j])) for j,i in enumerate(te)])
