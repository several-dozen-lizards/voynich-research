from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from scipy import stats
import core

R=Path(__file__).resolve().parent
previous=core.module('frozen_weak_v1_runner',core.ROOT/'sh-qok-weak-score-v1/run.py')
original=core.module('independent_weak_v1_core',core.ROOT/'sh-qok-weak-score-v1/core.py')
DESIGNS,REGIMES,NULLS=previous.DESIGNS,previous.REGIMES,previous.NULLS
generate=previous.generate
def save(name,obj):(R/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def log(phase,**data):
    with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**data))+'\n')
def verify():
    for p,h in json.loads((R/'FREEZE.json').read_text())['hashes'].items():assert sha(p)==h,('FROZEN_CHANGED',p)

def worker(di,regime,trial):
    F,N=DESIGNS[di];seed=1710000+di*100000+REGIMES.index(regime)*1000+trial;ev=generate(regime,seed,F,N);result=core.score(ev)
    old=None;prior=None
    if di==0 and regime=='weak':
        ss,_,_=core.b.fit_score(ev);old=next(s for s in ss if s['view']=='all' and s['contrast']=='G-L')
    if di==0 and regime=='strong':prior=original.score(ev)
    return dict(design=di,folios=F,events_per_folio=N,regime=regime,trial=trial,seed=seed,result=result,old_v2=old,prior_weak_v1=prior)

def engineering():
    core.a.R=R;core.a.engineering()
    # Prior numerical fixtures require only a small explicit matrix; no atlas read.
    w=np.array([[1.,0.],[1.,1.],[1.,2.]]);z=np.array([[1.],[0.],[2.]]);lam=np.sqrt(3)
    assert np.allclose(w@w.T@np.linalg.solve(w@w.T+lam*np.eye(3),z),w@np.linalg.solve(w.T@w+lam*np.eye(2),w.T@z),atol=1e-12)
    ev=generate('position',1220011,16,48)
    for e in ev:
        for d in (-4,-3,3,4):e['context'][str(d)]='<UNKNOWN>'
    zero=core.score(ev);assert zero['p']==1 and zero['mean_score']==0 and all(p['direction']==0 for p in zero['heldout'])
    tr=zero['calibration']['learning_events'];te=[i for i in range(len(ev)) if i not in set(tr)];_,p1,c1=core.baseline(ev,tr,te)
    altered=json.loads(json.dumps(ev))
    for i in te:altered[i]['y']=1-altered[i]['y'];altered[i]['word']=('sh' if altered[i]['y'] else 'ch')+altered[i]['body']
    _,p2,c2=core.baseline(altered,tr,te);assert np.array_equal(p1,p2) and c1==c2
    for assignment in c1['assignments']:
        assert assignment['validation_folio'] not in assignment['fit_folios']
        assert set(assignment['fit_folios']).isdisjoint(zero['test_folios'])
    save('SCORE-ENGINEERING.json',dict(status='PASS',old_parser_fixtures=True,kernel_dual_primal=True,zero_direction_executed=True,outer_label_invariance=True,OOF_separation=True))

def qualify():
    verify();log('qualification_start');engineering();summary=[]
    for di in range(3):
        for regime in REGIMES:
            records=[]
            with ProcessPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(worker,di,regime,t) for t in range(100)]
                for future in as_completed(futures):
                    record=future.result();save(f'trials/d{di}-{regime}-{record["trial"]:03d}.json',record);records.append(record)
                    if len(records)%25==0:print(di,regime,len(records),'/100',flush=True)
            k=sum(r['result'].get('flag4',False) for r in records);k24=sum(r['result'].get('flag24',False) for r in records);bounds=core.a.ci(k,100)
            gate=bounds[1]<=.10 if regime in NULLS else bounds[0]>=.80 if regime in ('weak','strong') else None
            row=dict(design=di,folios=DESIGNS[di][0],events_per_folio=DESIGNS[di][1],regime=regime,n=100,flags4=k,flags24=k24,wilson95=bounds,required_gate=gate,adequate=sum(r['result'].get('adequate',False) for r in records),supported=sum(r['result']['status']=='SCORED' for r in records))
            if di==0 and regime=='weak':
                wins=sum(r['result'].get('flag24',False) and not r['old_v2']['flag'] for r in records);losses=sum(r['old_v2']['flag'] and not r['result'].get('flag24',False) for r in records)
                p=float(stats.binomtest(wins,wins+losses,.5,alternative='greater').pvalue) if wins+losses else 1.
                row['paired_factor24']=dict(new_only=wins,old_only=losses,p=p,required_gate=p<=.01,old_detections=sum(r['old_v2']['flag'] for r in records))
            if di==0 and regime=='strong':row['prior_weak_v1_diagnostic']=dict(adequate=sum(r['prior_weak_v1'].get('adequate',False) for r in records),flags4=sum(r['prior_weak_v1'].get('flag4',False) for r in records),n=100)
            summary.append(row);save('QUALIFICATION-PROGRESS.json',summary)
    passed=all(s['required_gate'] is not False and s.get('paired_factor24',{}).get('required_gate',True) for s in summary)
    save('QUALIFICATION.json',dict(status='PASS_LIMITED' if passed else 'FAIL',cells=summary,manuscript_allowed=passed))
    verify();log('qualification_complete',status='PASS_LIMITED' if passed else 'FAIL');print('QUALIFICATION','PASS_LIMITED' if passed else 'FAIL',flush=True)

def manuscript():
    verify();assert json.loads((R/'QUALIFICATION.json').read_text())['manuscript_allowed'];log('manuscript_read_start');raw=json.loads(core.a.SOURCE.read_text());out=[]
    for section,hand in [('Balneological','2'),('Starred paragraphs','3')]:
        for reading in ('H','F'):
            panel=('bath' if hand=='2' else 'starred')+'-'+reading;ev,ex,lines=core.a.extract(raw,section,hand,reading);result=core.score(ev)
            save(panel+'-events.json',ev);save(panel+'-lines.json',lines);save(panel+'-score.json',result);out.append(dict(panel=panel,events=len(ev),exclusions=ex,result=result));save('RESULTS.json',out)
    verify();log('manuscript_complete')

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='freeze':
        assert not (R/'FREEZE.json').exists()
        paths=[R/'core.py',R/'run.py',R/'PROTOCOL.md']
        prior=core.ROOT/'sh-qok-weak-score-v1'
        inherited=json.loads((prior/'FREEZE.json').read_text())['hashes']
        paths.extend(Path(p) for p in inherited)
        paths.extend(prior/x for x in ('core.py','run.py','PROTOCOL.md','FREEZE.json','QUALIFICATION.json','STRONG-FAILURE-DIAGNOSIS.json','INDEPENDENT-AUDIT.json'))
        save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):sha(p) for p in paths}));(R/'trials').mkdir();log('freeze_complete');print('FROZEN REPAIR')
    elif mode=='qualify':qualify()
    elif mode=='manuscript':manuscript()
    else:raise ValueError(mode)
