import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from collections import defaultdict, Counter
from functools import lru_cache
import re, math, hashlib, itertools, warnings
import numpy as np
from scipy.stats import hypergeom
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning

ENDINGS=('eey','edy','ey','y')
CELLS=('P1-H','P1-F','P2-H','P2-F')

def tokens(text):
    text=re.sub(r'\{[^}]*\}', '', text.split('#')[0])
    text=re.sub(r'[!\s]', '', text)
    return [w if re.fullmatch('[a-z]+',w) else None for w in re.split(r'[.,=\-]',text) if w]

def family(w): return next((s for s in ENDINGS if w.endswith(s)),'other')

def parse(source, metadata):
    seen=set()
    for raw in source.read_text(encoding='latin1').splitlines():
        m=re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)',raw)
        if not m: continue
        pg,place,num,reading,text=m.groups()
        if reading not in ('H','F') or not place.startswith('P') or pg not in metadata: continue
        info=metadata[pg];hand=info['Scribe'];section=info['Section']
        if hand not in ('2','3'): continue
        panel='P0' if (hand=='2' and section=='Balneological') or (hand=='3' and section=='Starred paragraphs') else 'P1' if hand=='2' else 'P2'
        locator=f'{pg}.{place}.{num}';key=(reading,locator)
        assert key not in seen, ('duplicate locator',key)
        seen.add(key)
        yield dict(panel=panel,reading=reading,folio=pg,line=locator,hand=hand,section=section,tokens=tokens(text))

def extract(lines, outcomes=False):
    events=[];exclusions=defaultdict(Counter);ledger=[]
    for line in lines:
        ws=line['tokens'];cell=line['panel']+'-'+line['reading']
        for i,w in enumerate(ws):
            reason=None
            if w is None: reason='unknown_origin'
            elif not w.startswith(('sh','ch')): continue
            elif i==len(ws)-1: reason='origin_at_end'
            elif ws[i+1] is None: reason='following_unknown'
            prev=ws[i-1] if i else '<EDGE>'
            e=dict(cell=cell,folio=line['folio'],line=line['line'],position=i,length=len(ws),origin=w,
                   prefix=w[:2] if w else None,body=w[2:] if w else None,family=family(w) if w else None,
                   previous=prev or '<UNKNOWN>',hand=line['hand'],section=line['section'])
            if reason:
                exclusions[cell][reason]+=1
            else:
                e['x']=int(w.startswith('sh'))
                if outcomes: e['y']=int(ws[i+1].startswith('qok'))
                events.append(e)
            if outcomes:
                ledger.append({**e,'follower':ws[i+1] if i+1<len(ws) else None,'outcome':int(ws[i+1].startswith('qok')) if reason is None else None,'exclusion_reason':reason or ''})
    return events,dict(exclusions),ledger

def grouping(events):
    groups=defaultdict(list)
    for i,e in enumerate(events): groups[e['folio'],e['family']].append(i)
    return groups

def support(events):
    bypage=defaultdict(float);strata=[]
    for (page,fam),ix in grouping(events).items():
        ns=sum(events[i]['x'] for i in ix);nc=len(ix)-ns;v=ns*nc/len(ix)
        bypage[page]+=v
        strata.append(dict(folio=page,family=fam,sh=ns,ch=nc,V=v))
    V=sum(bypage.values());pages=sum(v>0 for v in bypage.values());share=max(bypage.values(),default=0)/V if V else None
    return dict(eligible_origins=len(events),sh=sum(e['x'] for e in events),ch=sum(1-e['x'] for e in events),
                supported_strata=sum(s['sh']>0 and s['ch']>0 for s in strata),supported_pages=pages,V=V,
                max_page_share=share,page_support=dict(bypage),strata=strata,
                gate=bool(V>=80 and pages>=8 and share<=.25))

@lru_cache(maxsize=16000)
def hg(n,ns,t):
    lo=max(0,t-(n-ns));hi=min(ns,t);p=hypergeom.pmf(np.arange(lo,hi+1),n,t,ns)
    return lo,p/p.sum()

def exact(events, y=None):
    if y is None: y=np.array([e['y'] for e in events],dtype=int)
    dist=np.array([1.]);offset=0;observed=0
    for ix in grouping(events).values():
        ns=sum(events[i]['x'] for i in ix);n=len(ix);t=int(y[ix].sum())
        observed+=sum(int(y[i])*events[i]['x'] for i in ix)
        lo,p=hg(n,ns,t);offset+=lo;dist=np.convolve(dist,p)
    dist=np.maximum(dist,0);dist/=dist.sum()
    degenerate=len(dist)==1
    return dict(p=None if degenerate else float(dist[max(0,observed-offset):].sum()),degenerate=degenerate,
                observed_sh_qok=int(observed),distribution_min=offset,distribution_max=offset+len(dist)-1,
                mass_error=float(abs(dist.sum()-1)))

def page_effects(events):
    out=defaultdict(lambda: [0.,0.])
    for (pg,f),ix in grouping(events).items():
        ns=sum(events[i]['x'] for i in ix);nc=len(ix)-ns
        if not ns or not nc: continue
        a=sum(events[i]['x']*events[i]['y'] for i in ix);b=sum((1-events[i]['x'])*events[i]['y'] for i in ix)
        v=ns*nc/len(ix);out[pg][0]+=v*(a/ns-b/nc);out[pg][1]+=v
    return dict(out)

def effect(events,seed):
    pages=sorted({e['folio'] for e in events});terms=page_effects(events)
    a=np.array([terms.get(p,[0,0]) for p in pages]);den=a[:,1].sum() if len(a) else 0
    if not den:return dict(effect_points=None,CI95_points=None,bootstrap_valid=0)
    rng=np.random.default_rng(seed);ix=rng.integers(len(a),size=(4999,len(a)));s=a[ix].sum(axis=1);good=s[:,1]>0
    boot=100*s[good,0]/s[good,1]
    return dict(effect_points=float(100*a[:,0].sum()/den),CI95_points=np.quantile(boot,[.025,.975]).tolist(),bootstrap_valid=int(good.sum()),page_terms=terms)

def holm(ps):
    order=sorted(range(len(ps)),key=lambda i:1 if ps[i] is None else ps[i]);out=[None]*len(ps);last=0.
    for rank,i in enumerate(order):
        p=ps[i] if ps[i] is not None else 1.
        last=max(last,min(1.,(len(ps)-rank)*p))
        out[i]=last if ps[i] is not None else None
    return out

def wilson(k,n):
    z=1.959963984540054;d=1+z*z/n;c=(k/n+z*z/(2*n))/d;r=z*math.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/d
    return [max(0,c-r),min(1,c+r)]

def feature(e,model):
    b=e['body'];f=e['family'];i=e['position'];n=e['length'];x=e['prefix'];out={}
    def add(k,*v):out[k+'='+repr(v)]=1.
    for k,v in [('body',b),('ending',f),('prefix',x),('index',i),('reverse',n-1-i),('length',n)]:add(k,v)
    add('body-position',b,i);add('body-reverse',b,n-1-i);add('ending-length-index',f,n,i)
    if model=='J':
        for w in (1,2):
            end=e['origin'][-w:];prev=e['previous'][-w:] if not e['previous'].startswith('<') else e['previous']
            add('origin-end',w,end);add('left-end',w,prev);add('prefix-origin-end',x,w,end);add('prefix-left-end',x,w,prev)
    return out

def mix_weight(candidate,fallback,y):
    d=candidate-fallback
    def derivative(w):
        p=np.clip(fallback+w*d,1e-9,1-1e-9);return float(np.mean(d*(p-y)/(p*(1-p))))
    if derivative(0)>=0:w=0.
    elif derivative(1)<=0:w=1.
    else:
        lo,hi=0.,1.
        for _ in range(60):
            m=(lo+hi)/2
            if derivative(m)<0:lo=m
            else:hi=m
        w=(lo+hi)/2
    def loss(p):return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))
    gain=loss(fallback)-loss(np.clip(fallback+w*d,1e-9,1-1e-9))
    return float(w if gain>1/len(y) else 0.),gain

def raw_predict(events,tr,te,model,y):
    rate=(y[tr].sum()+.5)/(len(tr)+1)
    if len(set(y[tr]))<2:return np.full(len(te),rate)
    vec=DictVectorizer();x=vec.fit_transform([feature(events[i],model) for i in tr]);xt=vec.transform([feature(events[i],model) for i in te])
    clf=LogisticRegression(C=.25,solver='liblinear',tol=1e-7,max_iter=2000,random_state=121)
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning);clf.fit(x,y[tr])
    return np.clip(clf.predict_proba(xt)[:,1],1e-9,1-1e-9)

def sign_p(values):
    v=np.array(values);n=len(v)
    if not n or np.all(abs(v)<1e-14):return None
    if n<=18:
        signs=2*((np.arange(2**n,dtype=np.uint32)[:,None]>>np.arange(n))&1).astype(float)-1
        return float(np.mean(signs@v>=v.sum()-1e-12))
    rng=np.random.default_rng(240999);k=0
    for start in range(0,65535,4096):
        s=rng.choice([-1.,1.],size=(min(4096,65535-start),n));k+=int((s@v>=v.sum()-1e-12).sum())
    return float((1+k)/65536)

def h2(events,y=None,receipts=False):
    if y is None:y=np.array([e['y'] for e in events])
    fs=sorted({e['folio'] for e in events},key=lambda f:hashlib.sha256(('sh-qok-context-transfer-v1|'+f).encode()).hexdigest());fm={f:i%5 for i,f in enumerate(fs)}
    if len(fs)<8 or len(events)<200:return dict(status='NOT_ESTIMABLE',p=None)
    probs={m:np.zeros(len(events)) for m in ['constant','P','J']};cal=[]
    for fold in range(5):
        tr=[i for i,e in enumerate(events) if fm[e['folio']]!=fold];te=[i for i,e in enumerate(events) if fm[e['folio']]==fold]
        tf=sorted({events[i]['folio'] for i in tr},key=lambda f:hashlib.sha256(('inner|'+f).encode()).hexdigest());fit=set(tf[:len(tf)//2]);val=set(tf[len(tf)//2:])
        it=[i for i in tr if events[i]['folio'] in fit];iv=[i for i in tr if events[i]['folio'] in val]
        assert fit.isdisjoint(val) and (fit|val).isdisjoint(events[i]['folio'] for i in te)
        fallback=np.full(len(iv),(y[it].sum()+.5)/(len(it)+1));weights={};gains={}
        for m in ['P','J']:
            p=raw_predict(events,it,iv,m,y);w,g=mix_weight(p,fallback,y[iv]);weights[m]=w;gains[m]=g;fallback=(1-w)*fallback+w*p
        rate=(y[tr].sum()+.5)/(len(tr)+1);probs['constant'][te]=rate;fallback=np.full(len(te),rate)
        for m in ['P','J']:
            raw=raw_predict(events,tr,te,m,y);fallback=(1-weights[m])*fallback+weights[m]*raw;probs[m][te]=fallback
        cal.append(dict(fold=fold,train_folios=sorted(fit|val),test_folios=sorted({events[i]['folio'] for i in te}),inner_fit=sorted(fit),inner_validation=sorted(val),weights=weights,gains=gains))
    losses={m:-(y*np.log2(p)+(1-y)*np.log2(1-p)) for m,p in probs.items()}
    by=[dict(folio=f,gain_bits=float(np.mean([losses['P'][i]-losses['J'][i] for i,e in enumerate(events) if e['folio']==f]))) for f in fs]
    adequate=float(losses['P'].mean())<=float(losses['constant'].mean())+.01
    enough=min(int(y.sum()),len(y)-int(y.sum()))>=30
    p=sign_p([b['gain_bits'] for b in by]) if adequate and enough else None
    out=dict(status='SCORED' if adequate and enough else 'INADEQUATE_BASELINE' if not adequate else 'INSUFFICIENT_OUTCOME_SUPPORT',p=p,gain_bits=float(np.mean([b['gain_bits'] for b in by])),adequate=adequate,outcome_counts=[int(len(y)-y.sum()),int(y.sum())],losses_bits={m:float(v.mean()) for m,v in losses.items()},per_folio=by)
    if receipts:out.update(calibration=cal,probabilities={m:p.tolist() for m,p in probs.items()},foldmap=fm)
    return out

def synthetic(events,scenario,seed,h2_mode=False):
    rng=np.random.default_rng(seed);pages={e['folio']:float(rng.choice([-.7,.7])) for e in events};lines={e['line']:float(rng.choice([-.7,.7])) for e in events};p=[]
    for e in events:
        if scenario=='null_low':q=.2
        elif scenario=='null_high':q=.6
        elif scenario=='additive':q=1/(1+math.exp(-(-1+pages[e['folio']]+lines[e['line']]+.7*(2*e['position']/max(1,e['length']-1)-1))))
        elif scenario=='junction_only':q=.1+.5*(e['origin'][-1]=='y')
        elif scenario=='positive' and not h2_mode:q=.2+.15*e['x']
        elif scenario=='positive':q=1/(1+math.exp(-(-1+2.5*(2*e['x']-1)*(2*int(e['origin'][-1]=='y')-1))))
        else:raise ValueError(scenario)
        p.append(q)
    return (rng.random(len(events))<np.array(p)).astype(int)
