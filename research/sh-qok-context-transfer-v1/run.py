from pathlib import Path
import collections, hashlib, itertools, json, math, re, sys, warnings
from functools import lru_cache
from datetime import datetime, timezone
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning

R=Path(__file__).resolve().parent
ROOT=R.parent
SOURCE=ROOT/'complete-atlas-v56/ROWS.json'
ENDINGS=('edy','eey','ey','y')
MODELS=('P','J','L','G')
FACTOR=24

def save(name,obj):
    (R/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def log(phase,**extra):
    with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**extra))+'\n')
def verify():
    for p,h in json.loads((R/'FREEZE.json').read_text())['hashes'].items():
        assert sha(p)==h, ('FROZEN_FILE_CHANGED',p)

def ending(w): return next((s for s in ENDINGS if w.endswith(s)),None)
def ctx(words,i,d):
    j=i+d
    for k in range(i+(1 if d>0 else -1),j+(1 if d>0 else -1),1 if d>0 else -1):
        if not 0<=k<len(words): return '<EDGE>'
        if words[k] is None: return '<UNKNOWN>'
    return words[j]

def event(words,i,folio,page,locator):
    w=words[i]
    return dict(folio=folio,page=page,locator=locator,index=i,length=len(words),body=w[2:],ending=ending(w),y=int(w.startswith('sh')),
                context={str(d):ctx(words,i,d) for d in (-4,-3,-2,-1,1,2,3,4)},word=w)

def feature(e,model):
    # Every origin-prefix value is absent from every feature map.
    b=e['body']; en=e['ending']; i=e['index']; n=e['length']; c=e['context']
    f={}
    def add(k,*values): f[k+'='+json.dumps(values,separators=(',',':'))]=1.
    for k,v in [('body',b),('ending',en),('index',i),('reverse',n-1-i),('length',n)]:add(k,v)
    add('body-position',b,i);add('body-reverse',b,n-1-i);add('ending-length-index',en,n,i)
    if model=='P':return f
    nxt=c['1'];prev=c['-1'];q=int(nxt.startswith('qok'))
    for width in (1,2,3):add('right-start',width,nxt[:width])
    for width in (1,2):add('left-end',width,prev[-width:])
    add('qok',q);add('body-right-start',b,nxt[:3]);add('ending-right-start',en,nxt[:3])
    if model=='J':return f
    for d in (-2,-1,1,2):add('local',d,c[str(d)])
    add('left-pair',c['-2'],prev);add('right-pair',nxt,c['2'])
    add('body-left',b,prev);add('body-right',b,nxt);add('flanks',prev,nxt)
    add('frame5',c['-2'],prev,b,nxt,c['2'])
    if model=='L':return f
    for d in (-4,-3,3,4):
        token=c[str(d)];add('far',d,token);add('far-qok',d,token,q);add('far-body',d,token,b)
    return f

def foldmap(events):
    folios=sorted({e['folio'] for e in events},key=lambda x:hashlib.sha256(('sh-qok-context-transfer-v1|'+x).encode()).hexdigest())
    return {f:i%5 for i,f in enumerate(folios)}
def sig(e):return (e['context']['-1'],e['body'],e['context']['1'])

@lru_cache(maxsize=32)
def signs(n):
    if n<=18:
        ix=np.arange(2**n,dtype=np.uint32)[:,None]
        return 2*((ix>>np.arange(n))&1).astype(float)-1
    return np.random.default_rng(1299901).choice([-1.,1.],size=(65535,n))

def p_sign(values):
    a=np.asarray(values,dtype=float);n=len(a);observed=float(a.mean())
    if n<=18:
        return float(np.mean((signs(n)@a/n)>=observed-1e-12))
    return float((1+np.sum(signs(n)@a/n>=observed-1e-12))/65536)

def summarize(events,preds):
    out=[]
    for view in ('all','novel'):
        ids=[i for i,p in enumerate(preds) if view=='all' or p['novel']]
        ec=collections.Counter(events[i]['y'] for i in ids);folios=sorted({events[i]['folio'] for i in ids})
        supported=len(ids)>=200 and len(folios)>=8 and min(ec.get(0,0),ec.get(1,0))>=30
        losses={m:float(np.mean([preds[i]['loss'][m] for i in ids])) if ids else None for m in (*MODELS,'constant')}
        for low,high in zip(MODELS[:-1],MODELS[1:]):
            by=[]
            for folio in folios:
                ii=[i for i in ids if events[i]['folio']==folio]
                by.append(dict(folio=folio,n=len(ii),gain=float(np.mean([preds[i]['loss'][low]-preds[i]['loss'][high] for i in ii]))))
            gain=float(np.mean([z['gain'] for z in by])) if by else None
            p=p_sign([z['gain'] for z in by]) if supported else None
            adequate=losses[low] is not None and losses[low]<=losses['constant']+.01
            out.append(dict(view=view,contrast=high+'-'+low,n=len(ids),folios=len(folios),prefix_counts=dict(ec),supported=supported,losses=losses,
                            gain_bits=gain,p=p,p_adjusted=min(1,p*FACTOR) if p is not None else None,baseline_adequate=adequate,
                            flag=bool(supported and adequate and gain>0 and p*FACTOR<=.05),per_folio=by))
    return out

def fit_score(events):
    fm=foldmap(events);preds=[None]*len(events);yy=np.array([e['y'] for e in events])
    for fold in range(5):
        tr=[i for i,e in enumerate(events) if fm[e['folio']]!=fold];te=[i for i,e in enumerate(events) if fm[e['folio']]==fold]
        assert tr and te and set(events[i]['folio'] for i in tr).isdisjoint(events[i]['folio'] for i in te)
        assert len(set(yy[tr]))==2
        known={sig(events[i]) for i in tr};rate=(yy[tr].sum()+.5)/(len(tr)+1)
        probs={'constant':np.full(len(te),rate)}
        for model in MODELS:
            vec=DictVectorizer();x=vec.fit_transform([feature(events[i],model) for i in tr]);xt=vec.transform([feature(events[i],model) for i in te])
            clf=LogisticRegression(C=.25,solver='liblinear',tol=1e-7,max_iter=2000,random_state=121)
            with warnings.catch_warnings():
                warnings.simplefilter('error',ConvergenceWarning);clf.fit(x,yy[tr])
            probs[model]=np.clip(clf.predict_proba(xt)[:,1],1e-9,1-1e-9)
        for j,i in enumerate(te):
            y=yy[i];pr={m:float(v[j]) for m,v in probs.items()}
            preds[i]=dict(fold=fold,novel=sig(events[i]) not in known,probability=pr,
                          loss={m:float(-math.log2(p if y else 1-p)) for m,p in pr.items()})
    return summarize(events,preds),preds,fm

def generate(regime,seed):
    rng=np.random.default_rng(seed);events=[]
    for fol in range(16):
        for line in range(48):
            i=4 if line%2==0 else 3;b=int(rng.integers(4));q=int(rng.integers(2));near=int(rng.integers(8));far=int(rng.integers(2))
            words=['w'+str(int(rng.integers(8))) for _ in range(9)]
            words[i-1]='p'+str(near);words[i+1]=('qok' if q else 'dar')+str(int(rng.integers(8)))
            words[i-3]='cue'+str(far)
            z=(-.5 if b<2 else .5)+(.5 if i==4 else -.5)
            if regime!='position':z+=1.3*(2*q-1)
            if regime=='phrase':z+=1.8*(2*(near<4)-1)
            if regime in ('distant_strong','distant_small','template_equivalent'):
                z+=(2.5 if regime!='distant_small' else .65)*(2*far-1)*(2*q-1)
            y=int(rng.random()<1/(1+math.exp(-z)));words[i]=('sh' if y else 'ch')+['edy','eey','ey','y'][b]
            events.append(event(words,i,'synthetic'+str(fol),'synthetic'+str(fol),str(fol)+'.'+str(line)))
    return events

def ci(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-r),min(1,c+r)]

def engineering():
    assert [ending(x) for x in ('shedy','sheey','shey','shy','sham')]==list(ENDINGS)+[None]
    words=['a','shedy',None,'qokam','z'];assert ctx(words,1,2)=='<UNKNOWN>' and ctx(words,1,-2)=='<EDGE>'
    e=event(['a','b','c','d','shedy','qokam','e','f','g'],4,'f1','f1r','toy')
    alt=dict(e);alt['y']=0;alt['word']='chedy'
    assert all(feature(e,m)==feature(alt,m) for m in MODELS)
    far=json.loads(json.dumps(e));far['context']['-3']='different'
    assert all(feature(e,m)==feature(far,m) for m in ('P','J','L')) and feature(e,'G')!=feature(far,'G')
    for m in MODELS[:-1]:assert set(feature(e,m))<=set(feature(e,MODELS[MODELS.index(m)+1]))
    for v in itertools.product([-1.,1.],repeat=4):
        p=p_sign(v);assert 0<=p<=1
    orbit=[p_sign(np.array(v)*np.array([1.,2.,4.,8.])) for v in itertools.product([-1.,1.],repeat=4)]
    assert sum(p<=.125 for p in orbit)/16<=.125
    fixture=[]
    for co in ('H','F'):
        fixture.append([co,'f1r','Balneological','2','B','P',None,None,'f1r.P.1',['shedy','qokam',None,'chedy','dar'], 'toy'])
    fixture.append(['H','f2r','Balneological','2','B','P',None,None,'f2r.P.1',['shedy','qokam'],'unshared'])
    ev,ex,lines=extract(fixture,'Balneological','2','H')
    assert len(ev)==2 and len(lines)==1 and ev[0]['context']['2']=='<UNKNOWN>' and ev[1]['context']['-1']=='<UNKNOWN>'
    assert ev[0]['ending']=='edy' and ev[0]['y']==1 and ev[1]['y']==0
    aa=generate('distant_strong',12991);bb=generate('template_equivalent',12991)
    assert aa==bb
    save('IDENTIFIABILITY.json',dict(equal_output=True,events=len(aa),data_sha256=hashlib.sha256(json.dumps(aa,sort_keys=True).encode()).hexdigest(),
        explanation='The same far-cue x next-qok dependency can be described as agreement-like rule or reusable variable-slot phrase template. Identical events and outcomes mean no statistic of these data distinguishes those descriptions.'))
    save('ENGINEERING.json',dict(status='PASS',ending_disjoint=True,barriers=True,no_target_leak=True,nesting=True,far_invariance=True,sign_orbits_checked=16,equal_output=True,shared_locus_parser_fixture=True))

def qualify():
    verify();log('qualification_start');engineering();records=[];summary=[]
    regimes=('position','junction','phrase','distant_strong','distant_small')
    for ri,regime in enumerate(regimes):
        for trial in range(60):
            seed=1210000+ri*1000+trial;ev=generate(regime,seed);scores,preds,fm=fit_score(ev)
            save(f'synthetic/{regime}-{trial:02d}.json',dict(regime=regime,seed=seed,scores=scores,predictions=preds,folds=fm))
            records.append(dict(regime=regime,trial=trial,seed=seed,scores=scores))
            if (trial+1)%10==0: print(regime,trial+1,'/60',flush=True)
        rr=[r for r in records if r['regime']==regime]
        for view in ('all','novel'):
            ss=[next(s for s in r['scores'] if s['view']==view and s['contrast']=='G-L') for r in rr]
            k=sum(s['flag'] for s in ss);bounds=ci(k,len(ss));gate=None
            if view=='all' and regime in regimes[:3]:gate=bounds[1]<=.10
            if view=='all' and regime=='distant_strong':gate=bounds[0]>=.80
            summary.append(dict(regime=regime,view=view,trials=len(ss),supported=sum(s['supported'] for s in ss),flags=k,wilson95=bounds,
                                mean_gain=float(np.mean([s['gain_bits'] for s in ss])),required_gate=gate))
        save('QUALIFICATION-PROGRESS.json',summary)
    passed=all(s['required_gate'] is not False for s in summary)
    save('QUALIFICATION.json',dict(status='PASS_LIMITED' if passed else 'FAIL',results=summary,limits='Synthetic local logistic mechanisms and strong dense distant signals only; not grammar specificity or manuscript-sized power.'))
    verify();log('qualification_complete',status='PASS_LIMITED' if passed else 'FAIL');print('QUALIFICATION', 'PASS_LIMITED' if passed else 'FAIL',flush=True)

def extract(raw,section,hand,reading):
    loci={co:{x[8] for x in raw if x[0]==co and x[2]==section and x[3]==hand and x[4]=='B' and x[5]=='P'} for co in ('H','F')}
    shared=loci['H']&loci['F'];events=[];ex=collections.Counter();lines=[]
    for x in raw:
        if x[0]!=reading or x[8] not in shared:continue
        words=x[9];folio=re.match(r'f\d+',x[1]).group();lines.append(dict(page=x[1],locator=x[8],tokens=words,raw=x[10]))
        for i,w in enumerate(words):
            if w is None:ex['unknown_origin']+=1;continue
            if not w.startswith(('sh','ch')) or ending(w) is None:continue
            if i+1==len(words):ex['origin_at_end']+=1;continue
            if words[i+1] is None:ex['following_unknown']+=1;continue
            events.append(event(words,i,folio,x[1],x[8]))
    assert len({(e['locator'],e['index']) for e in events})==len(events),'duplicate physical origin'
    return events,dict(ex),lines

def manuscript():
    verify();assert json.loads((R/'QUALIFICATION.json').read_text())['status']=='PASS_LIMITED'
    log('manuscript_read_start');raw=json.loads(SOURCE.read_text());results=[]
    for sec,hand in [('Balneological','2'),('Starred paragraphs','3')]:
        for reading in ('H','F'):
            label=('bath' if hand=='2' else 'starred')+'-'+reading;events,excluded,lines=extract(raw,sec,hand,reading)
            counts=collections.Counter(e['y'] for e in events)
            if len(events)<200 or len({e['folio'] for e in events})<8 or min(counts.get(0,0),counts.get(1,0))<30:
                result=dict(panel=label,status='NOT_ESTIMABLE',events=len(events),folios=len({e['folio'] for e in events}),prefix_counts=dict(counts),excluded=excluded,scores=[])
                save(label+'-events.json',events)
            else:
                scores,preds,fm=fit_score(events)
                result=dict(panel=label,status='SCORED',events=len(events),folios=len(fm),prefix_counts=dict(counts),excluded=excluded,scores=scores)
                save(label+'-events.json',events);save(label+'-predictions.json',preds);save(label+'-folds.json',fm)
                for view in ('all','novel'):
                    desc=[]
                    for q in (False,True):
                        ids=[i for i,e in enumerate(events) if e['context']['1'].startswith('qok')==q and (view=='all' or preds[i]['novel'])]
                        desc.append(dict(next_qok=q,n=len(ids),gain_G_L=float(np.mean([preds[i]['loss']['L']-preds[i]['loss']['G'] for i in ids])) if ids else None))
                    result.setdefault('qok_diagnostics',{})[view]=desc
            save(label+'-source-lines.json',lines);results.append(result);save('RESULTS.json',results);print(label,result['status'],result['events'],flush=True)
    verify();save('FINAL-INTEGRITY.json',dict(status='PASS',frozen_inputs_unchanged=True));log('manuscript_complete')

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='freeze':
        assert not (R/'FREEZE.json').exists(),'Never overwrite a freeze'
        paths=[R/'run.py',R/'PROTOCOL.md',SOURCE,ROOT/'complete-atlas-v56/SOURCE-MANIFEST.json',ROOT/'sh-qok-ending-qualification-reed-v94/PROTOCOL.json',ROOT/'sh-qok-ending-qualification-reed-v94/run.py']
        save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):sha(p) for p in paths}));log('freeze_complete');(R/'synthetic').mkdir();print('FROZEN')
    elif mode=='qualify':qualify()
    elif mode=='manuscript':manuscript()
    else:raise ValueError(mode)
