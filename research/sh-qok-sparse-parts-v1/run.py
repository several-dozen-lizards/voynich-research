from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from functools import lru_cache
import json,hashlib,math,sys
import numpy as np
from scipy import stats
import core

R=Path(__file__).resolve().parent
source=core.module('original_uniform_generator',core.ROOT/'sh-qok-weak-score-v1/run.py')
REGIMES=source.REGIMES
DESIGNS=('uniform16','uniform10','uniform12','matchedH','matchedF')
def save(name,obj):(R/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def log(phase,**kwargs):
    with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**kwargs))+'\n')
def verify():
    for p,h in json.loads((R/'FREEZE.json').read_text())['hashes'].items():assert sha(p)==h,('FROZEN_CHANGED',p)
@lru_cache(maxsize=1)
def inputs():return json.loads((R/'COVARIATES.json').read_text()),json.loads((R/'MATCHED-PROFILES.json').read_text())

def matched_generate(code,regime,seed):
    templates,profiles=inputs();template=templates[code];profile=profiles[code];cue=np.array([core.value(e,profile['cue']) for e in template]);q=np.array([e['context']['1'].startswith('qok') for e in template],dtype=int)
    body=np.array([len(e['body'])>profile['body_length_median'] for e in template],dtype=int);position=np.array([e['index']/max(1,e['length']-1)>profile['position_median'] for e in template],dtype=int)
    z=.5*(2*body-1)+.5*(2*position-1)
    if regime not in ('position','position_proxy'):z=z+1.3*(2*q-1)
    if regime=='position_proxy':z=.5*(2*body-1)+1.3*(2*position-1)
    if regime=='phrase':
        near=np.array([int(hashlib.sha256((str(seed)+'|'+e['context']['-1']+'|'+e['context']['1']).encode()).hexdigest()[:8],16)%2 for e in template]);z=z+1.8*(2*near-1)
    if regime=='proxy_phrase':z=z+1.8*(2*np.array([core.value(e,profile['proxy_local']) for e in template])-1)
    if regime=='additive_far':z=z+.65*(2*cue-1)
    if regime in ('weak','strong','tiny'):z=z+dict(weak=.65,strong=2.5,tiny=.35)[regime]*(2*cue-1)*(2*q-1)
    tr=profile['learning_events'];lo,hi=-30.,30.
    for _ in range(80):
        mid=(lo+hi)/2
        if np.mean(1/(1+np.exp(-(z[tr]+mid))))<.5:lo=mid
        else:hi=mid
    intercept=(lo+hi)/2;prob=1/(1+np.exp(-(z+intercept)));rng=np.random.default_rng(seed);y=(rng.random(len(template))<prob).astype(int)
    events=[dict(e,y=int(y[i]),word=('sh' if y[i] else 'ch')+e['body']) for i,e in enumerate(template)]
    return events,dict(template=code,intercept=intercept,expected_learning_share=float(prob[tr].mean()),expected_testing_share=float(prob[profile['test_events']].mean()),cue=profile['cue'],cue_learning_prevalence=float(cue[tr].mean()),cue_testing_prevalence=float(cue[profile['test_events']].mean()),qok_learning_prevalence=float(q[tr].mean()),original_central_labels_used=False)

def worker(di,regime,trial):
    seed=2110000+di*100000+REGIMES.index(regime)*1000+trial;meta=None
    if di<3:
        F,N=source.DESIGNS[di];events=source.generate(regime,seed,F,N)
    else:events,meta=matched_generate('H' if di==3 else 'F',regime,seed)
    result=core.score(events);old=None
    if di==0 and regime=='weak':
        rr,_,_=core.b.fit_score(events);old=next(s for s in rr if s['view']=='all' and s['contrast']=='G-L')
    return dict(design=DESIGNS[di],design_index=di,regime=regime,trial=trial,seed=seed,result=result,matched_generation=meta,old_v2=old)

def engineering():
    core.a.R=R;core.a.engineering();templates,profiles=inputs()
    for code,tt in templates.items():
        assert all('y' not in e and 'word' not in e for e in tt)
        tr,te,learn,test=core.split(tt);assert len(tr)==(252 if code=='H' else 257) and len(te)==(888 if code=='H' else 884)
        assert len(profiles[code]['learning_events'])==len(tr) and profiles[code]['central_labels_used'] is False
    toy=source.generate('position',1220011,16,48);tr,te,_,_=core.split(toy);cache=core.cache_features(toy);_,p1,c1=core.baseline(toy,tr,te,cache)
    changed=json.loads(json.dumps(toy))
    for i in te:changed[i]['y']=1-changed[i]['y'];changed[i]['word']=('sh' if changed[i]['y'] else 'ch')+changed[i]['body']
    _,p2,c2=core.baseline(changed,tr,te,core.cache_features(changed));assert np.array_equal(p1,p2) and c1==c2
    for e in toy:
        for d in core.OFFSETS:e['context'][str(d)]='<UNKNOWN>'
    z=core.score(toy);assert z['p']==1 and z['mean_score']==0 and all(p['direction']==0 for p in z['heldout'])
    w=np.array([[1.,0.],[1.,1.],[1.,2.]]);zz=np.array([[1.],[0.],[2.]]);lam=np.sqrt(3)
    assert np.allclose(w@w.T@np.linalg.solve(w@w.T+lam*np.eye(3),zz),w@np.linalg.solve(w.T@w+lam*np.eye(2),w.T@zz),atol=1e-12)
    save('ENGINEERING.json',dict(status='PASS',central_labels_removed=True,exact_template_counts=True,outer_label_invariance=True,zero_direction_executed=True,kernel_dual_primal=True))

def qualify():
    verify();log('qualification_start');engineering();summary=[]
    for di in range(5):
        for regime in REGIMES:
            rows=[]
            with ProcessPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(worker,di,regime,t) for t in range(100)]
                for future in as_completed(futures):
                    row=future.result();save(f'trials/d{di}-{regime}-{row["trial"]:03d}.json',row);rows.append(row)
                    if len(rows)%25==0:print(DESIGNS[di],regime,len(rows),'/100',flush=True)
            k=sum(r['result'].get('flag4',False) for r in rows);k24=sum(r['result'].get('flag24',False) for r in rows);bounds=core.a.ci(k,100)
            gate=bounds[1]<=.10 if regime in REGIMES[:6] else bounds[0]>=.80 if regime in ('weak','strong') else None
            s=dict(design=DESIGNS[di],design_index=di,regime=regime,n=100,flags4=k,flags24=k24,wilson95=bounds,required_gate=gate,adequate=sum(r['result'].get('adequate',False) for r in rows),supported=sum(r['result']['status']=='SCORED' for r in rows),zero_directions=sum(r['result'].get('status')=='SCORED' and all(v['direction']==0 for v in r['result']['heldout']) for r in rows))
            if di==0 and regime=='weak':
                win=sum(r['result'].get('flag24',False) and not r['old_v2']['flag'] for r in rows);lose=sum(r['old_v2']['flag'] and not r['result'].get('flag24',False) for r in rows);pv=float(stats.binomtest(win,win+lose,.5,alternative='greater').pvalue) if win+lose else 1.
                s['paired_factor24']=dict(new_only=win,old_only=lose,p=pv,old_detections=sum(r['old_v2']['flag'] for r in rows),required_gate=pv<=.01)
            summary.append(s);save('QUALIFICATION-PROGRESS.json',summary)
    passed=all(s['required_gate'] is not False and s.get('paired_factor24',{}).get('required_gate',True) for s in summary)
    save('QUALIFICATION.json',dict(status='PASS_LIMITED' if passed else 'FAIL',cells=summary,manuscript_allowed=passed));verify();log('qualification_complete',status='PASS_LIMITED' if passed else 'FAIL');print('QUALIFICATION','PASS_LIMITED' if passed else 'FAIL',flush=True)

def manuscript():
    verify();assert json.loads((R/'QUALIFICATION.json').read_text())['manuscript_allowed'];log('manuscript_read_start');raw=json.loads(core.a.SOURCE.read_text());out=[]
    for code in ('H','F'):
        events,ex,lines=core.a.extract(raw,'Starred paragraphs','3',code);result=core.score(events);panel='starred-'+code
        save(panel+'-events.json',events);save(panel+'-source-lines.json',lines);save(panel+'-score.json',result);out.append(dict(panel=panel,result=result,events=len(events),excluded=ex));save('RESULTS.json',out)
    verify();log('manuscript_complete')

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='freeze':
        assert not (R/'FREEZE.json').exists();templates=json.loads((R/'COVARIATES.json').read_text());profiles={code:core.prepare_profile(e) for code,e in templates.items()};save('MATCHED-PROFILES.json',profiles)
        old=core.ROOT/'sh-qok-weak-score-v2';paths=[R/'core.py',R/'run.py',R/'PROTOCOL.md',R/'COVARIATES.json',R/'COVARIATE-SUMMARY.json',R/'MATCHED-PROFILES.json']+[Path(p) for p in json.loads((old/'FREEZE.json').read_text())['hashes']]+[old/n for n in ('core.py','run.py','PROTOCOL.md','FREEZE.json','QUALIFICATION.json','OUTCOME.json','starred-H-events.json','starred-F-events.json','starred-H-score.json','starred-F-score.json')]
        save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):sha(p) for p in paths}));(R/'trials').mkdir();log('freeze_complete');print('FROZEN SPARSE REPAIR')
    elif mode=='qualify':qualify()
    elif mode=='manuscript':manuscript()
    else:raise ValueError(mode)
