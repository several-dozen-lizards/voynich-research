"""T1 pre-join methods. No manuscript/ratings loader; arrays are explicit inputs.
No continuity correction, wrap-restricted shuffle, or failed-draw deletion.
"""
import copy, hashlib, itertools, math, re
from collections import defaultdict
import numpy as np
LABELS=('PL','VE','FG','CE','OT','NO')
OPENERS=('qok','qo','ot','ok','d','ch','sh','other-gallows','y','o','a','s','other')
ENDINGS={'a':('aiin','ain','air','ar','al'),'y':('edy','eey','ey','y'),'ol/or':('ol','or')}
CLASSES=tuple('open:'+x for x in OPENERS)+('end:a','end:y','end:ol/or','end:other')
RESERVED={'f72v1','f72v2','f73r','f73v'}
class NotEstimable(ValueError): pass

def derived_seed(base,reading,feature):
    if reading not in ('H','F') or feature not in CLASSES:raise ValueError('reading/class seed domain')
    return int.from_bytes(hashlib.sha256(f'{base}:{reading}:{feature}'.encode()).digest()[:8],'big')

def classify(w):
    if not isinstance(w,str) or not re.fullmatch('[a-z]+',w): return None
    op=next((x for x in OPENERS[:7] if w.startswith(x)),None)
    if op is None:
        op='other-gallows' if w[0] in 'ktpf' else next((x for x in ('y','o','a','s') if w.startswith(x)),'other')
    ends=sorted(((e,g) for g,es in ENDINGS.items() for e in es),key=lambda x:(-len(x[0]),x[0]))
    en=next((g for e,g in ends if w.endswith(e)),'other')
    return 'open:'+op,'end:'+en

def count_line(row):
    # Exclude the physical first slot, including when it is unknown.
    if row['folio'] in RESERVED or row.get('vault'): raise NotEstimable('reserved line')
    if row['reading'] not in ('H','F') or row['length_bin'] not in ('short','normal'): raise NotEstimable('reading/wrap metadata')
    if row['label'] not in LABELS: raise NotEstimable('label')
    c=dict.fromkeys(CLASSES,0); n=bad=0
    for w in row['words'][1:]:
        z=classify(w)
        if z is None: bad+=1; continue
        n+=1
        for k in z:c[k]+=1
    return dict(id=row['id'],folio=row['folio'],reading=row['reading'],length_bin=row['length_bin'],label=row['label'],n=n,counts=c,unknown=bad)

def validate(rows):
    if not rows or len({r['reading'] for r in rows})!=1: raise NotEstimable('empty or pooled readings')
    if len({r['id'] for r in rows})!=len(rows): raise NotEstimable('duplicate line')
    for r in rows:
        if r['folio'] in RESERVED or r.get('vault'): raise NotEstimable('reserved line')
        if r['reading'] not in ('H','F') or r['label'] not in LABELS or r['length_bin'] not in ('short','normal'): raise NotEstimable('metadata')
        if not isinstance(r['n'],int) or r['n']<0: raise NotEstimable('slots')
        if set(r['counts'])!=set(CLASSES) or any(not isinstance(v,int) or not 0<=v<=r['n'] for v in r['counts'].values()): raise NotEstimable('class counts')
        if sum(r['counts'][k] for k in CLASSES[:13])!=r['n'] or sum(r['counts'][k] for k in CLASSES[13:])!=r['n']:raise NotEstimable('class partitions do not equal slot denominator')

def rate_ratio(rows,feature='open:qok',left=('FG','VE'),right=('PL','NO'),gated=True):
    validate(rows)
    strata=defaultdict(lambda:[0,0,0,0]); totals=defaultdict(lambda:[0,0])
    for r in rows:
        group=0 if r['label'] in left else 1 if r['label'] in right else None
        if group is None: continue
        s=strata[(r['folio'],r['length_bin'])];s[group]+=r['n'];s[group+2]+=r['counts'][feature]
        totals[r['folio']][group]+=r['n']
    eligible={f for f,(na,nb) in totals.items() if na>=30 and nb>=30}
    num=den=0.;weights=defaultdict(float)
    for (f,b),(na,nb,a,bv) in strata.items():
        if f not in eligible or not na or not nb: continue
        num+=a*nb/(na+nb);den+=bv*na/(na+nb);weights[f]+=na*nb/(na+nb)
    weights={f:w for f,w in weights.items() if w>0}; total=sum(weights.values())
    if not total: raise NotEstimable('no comparable strata')
    weightmax=max(weights.values())/total
    if gated and (len(weights)<8 or weightmax>.25): raise NotEstimable('folio support or dominant weight')
    if num<=0 or den<=0: raise NotEstimable('zero event rate; no pseudocount')
    return dict(logRR=math.log(num/den),folios=len(weights),maximum_weight=weightmax,weights={f:w/total for f,w in weights.items()},numerator=num,denominator=den)

def cmh(rows,feature,gated=True):
    validate(rows)
    groups=defaultdict(list)
    for r in rows:groups[(r['folio'],r['length_bin'])].append(r)
    d=np.zeros(6);V=np.zeros((6,6));fw=defaultdict(float)
    for (f,b),rs in groups.items():
        n=np.array([sum(r['n'] for r in rs if r['label']==lab) for lab in LABELS],dtype=float)
        a=np.array([sum(r['counts'][feature] for r in rs if r['label']==lab) for lab in LABELS],dtype=float)
        N=n.sum(); n1=a.sum();n0=N-n1
        if N<=1 or n1==0 or n0==0 or np.count_nonzero(n)<2:continue
        cov=n1*n0/(N*(N-1))*(np.diag(n)-np.outer(n,n)/N)
        d+=a-n*n1/N;V+=cov;fw[f]+=float(np.trace(cov))
    total=sum(fw.values())
    if not total: raise NotEstimable('no information for class scan')
    if gated and (len(fw)<8 or max(fw.values())/total>.25): raise NotEstimable('scan folio information support')
    rank=int(np.linalg.matrix_rank(V,tol=1e-10))
    return dict(statistic=float(d@np.linalg.pinv(V,rcond=1e-10)@d),rank=rank,folios=len(fw),maximum_weight=max(fw.values())/total)

def permute(rows,rng):
    out=copy.deepcopy(rows);groups=defaultdict(list)
    for i,r in enumerate(out): groups[r['folio']].append(i)
    for ids in groups.values():
        labels=[out[i]['label'] for i in ids];rng.shuffle(labels)
        for i,label in zip(ids,labels):out[i]['label']=label
    return out

def permutation_test(rows,feature='open:qok',scan=False,draws=10000,seed=810251):
    if draws<10000: raise ValueError('at least 10000 permutations')
    fn=(lambda r:cmh(r,feature)['statistic']) if scan else (lambda r:rate_ratio(r,feature)['logRR'])
    observed=fn(rows);rng=np.random.default_rng(seed);above=0
    for i in range(draws):
        try: value=fn(permute(rows,rng))
        except NotEstimable as exc:
            return dict(status='NOT_ESTIMABLE',reason='permuted support: '+str(exc),failed_draw=i,requested=draws,p=None)
        above+=value>=observed-1e-12
    return dict(status='ESTIMABLE',observed=observed,p=(1+above)/(draws+1),draws=draws,seed=seed)

def holm(ps):
    if len(ps)!=17: raise ValueError('all 17 classes required')
    # Missing p-values stay in the declared family and cannot pass.
    order=sorted(range(17),key=lambda i:1. if ps[i] is None else ps[i]);out=[None]*17;prev=0.
    for j,i in enumerate(order):
        p=1. if ps[i] is None else ps[i]
        prev=max(prev,min(1.,(17-j)*p));out[i]=prev if ps[i] is not None else None
    return out

def equivalence(rows,feature,draws=10000,seed=810252):
    if draws<10000: raise ValueError('at least 10000 bootstrap draws')
    pairs=list(itertools.combinations(LABELS,2))
    def theta(rs):return np.array([rate_ratio(rs,feature,(a,),(b,))['logRR'] for a,b in pairs])
    try: observed=theta(rows)
    except NotEstimable as exc:return dict(status='UNRESOLVED',reason=str(exc),equivalent=False)
    fs=sorted({r['folio'] for r in rows});by={f:[r for r in rows if r['folio']==f] for f in fs};rng=np.random.default_rng(seed);dev=[]
    for i in range(draws):
        sampled=[]
        for j,f in enumerate(rng.choice(fs,len(fs),replace=True)):
            for r in by[f]:
                z=copy.deepcopy(r);z['folio']='bootstrap-'+str(j);z['id']=str(j)+':'+r['id'];sampled.append(z)
        try: dev.append(float(np.max(np.abs(theta(sampled)-observed))))
        except NotEstimable as exc:return dict(status='UNRESOLVED',reason='undefined bootstrap draw: '+str(exc),failed_draw=i,equivalent=False)
    # Conservative empirical quantile: choose an observed order statistic, never interpolate downward.
    c=float(np.quantile(dev,.95,method='higher'));bound=float(np.max(np.abs(observed))+c)
    return dict(status='ESTIMABLE',simultaneous_radius=c,maximum_absolute_bound=bound,equivalent=bound<=.25,draws=draws,seed=seed,pairs=[dict(a=a,b=b,logRR=float(t),low=float(t-c),high=float(t+c)) for (a,b),t in zip(pairs,observed)])

def classify_both(h_p,f_p,h_eq,f_eq):
    if h_p is not None and f_p is not None and h_p<.05 and f_p<.05:return 'context-sensitive'
    if h_p is not None and f_p is not None and h_p>=.05 and f_p>=.05 and h_eq.get('equivalent') is True and f_eq.get('equivalent') is True:return 'context-invariant'
    return 'unresolved'
