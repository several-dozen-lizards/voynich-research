from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json,hashlib,math,sys,collections
import numpy as np
from scipy import stats
import core

R=Path(__file__).resolve().parent
DESIGNS=((16,48),(10,100),(12,96))
REGIMES=('position','junction','phrase','proxy_phrase','position_proxy','additive_far','weak','strong','tiny')
NULLS=REGIMES[:6]
def save(name,obj):(R/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def log(phase,**data):
    with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),phase=phase,**data))+'\n')
def verify():
    for p,h in json.loads((R/'FREEZE.json').read_text())['hashes'].items():assert sha(p)==h,('FROZEN_CHANGED',p)

def generate(regime,seed,F,N):
    rng=np.random.default_rng(seed);ev=[]
    for fol in range(F):
        for line in range(N):
            i=4 if line%2==0 else 3;b=int(rng.integers(4));q=int(rng.integers(2));near=int(rng.integers(8));far=int(rng.integers(2))
            words=['w'+str(int(rng.integers(8))) for _ in range(9)]
            words[i-1]='p'+str(near);words[i+1]=('qok' if q else 'dar')+str(int(rng.integers(8)))
            if regime=='proxy_phrase':far=int(near<4) if rng.random()<.8 else int(near>=4)
            if regime=='position_proxy':far=int(i==4) if rng.random()<.8 else int(i!=4)
            words[i-3]='cue'+str(far)
            z=(-.5 if b<2 else .5)+(.5 if i==4 else -.5)
            if regime not in ('position','position_proxy'):z+=1.3*(2*q-1)
            if regime in ('phrase','proxy_phrase'):z+=1.8*(2*(near<4)-1)
            if regime=='additive_far':z+=.65*(2*far-1)
            if regime in ('weak','strong','tiny'):z+=dict(weak=.65,strong=2.5,tiny=.35)[regime]*(2*far-1)*(2*q-1)
            y=int(rng.random()<1/(1+math.exp(-z)));words[i]=('sh' if y else 'ch')+['edy','eey','ey','y'][b]
            ev.append(core.a.event(words,i,'synthetic'+str(fol),'synthetic'+str(fol),str(fol)+'.'+str(line)))
    return ev

def worker(di,regime,trial):
    F,N=DESIGNS[di];seed=1310000+di*100000+REGIMES.index(regime)*1000+trial;ev=generate(regime,seed,F,N);result=core.score(ev)
    old=None
    if di==0 and regime=='weak':
        ss,_,_=core.b.fit_score(ev);old=next(s for s in ss if s['view']=='all' and s['contrast']=='G-L')
    return dict(design=di,folios=F,events_per_folio=N,regime=regime,trial=trial,seed=seed,result=result,old_v2=old)

def engineering():
    # Old fixtures write only into this new folder; they do not read manuscript rows.
    core.a.R=R;core.a.engineering()
    for regime,old in [('position','position'),('junction','junction'),('phrase','phrase'),('weak','distant_small'),('strong','distant_strong')]:
        assert generate(regime,1220011,16,48)==core.a.generate(old,1220011)
    w=np.array([[1.,0.],[1.,1.],[1.,2.]]);z=np.array([[1.],[0.],[2.]]);lam=math.sqrt(3)
    dual=np.linalg.solve(w@w.T+lam*np.eye(3),z);primal=np.linalg.solve(w.T@w+lam*np.eye(2),w.T@z)
    assert np.allclose(w@w.T@dual,w@primal,atol=1e-12)
    yy=np.array([0.,1.,1.]);pp=np.array([.3,.6,.7]);d=np.array([.4,-.1,.2]);u=(yy-pp)*d
    assert np.allclose(u,np.array([(float(y)-float(p))*float(v) for y,p,v in zip(yy,pp,d)]))
    beta=stats.t.sf(0,5);assert beta==.5
    # t survival at zero and conditional score zero are defined before any seed.
    save('SCORE-ENGINEERING.json',dict(status='PASS',old_generator_exact_replay=True,dual_primal_projection=True,scalar_scores=True,t_zero=.5,zero_score_p=1,imports_do_not_open_atlas=True))

def qualify():
    verify();log('qualification_start');engineering();summary=[]
    for di in range(len(DESIGNS)):
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
                paired=float(stats.binomtest(wins,wins+losses,.5,alternative='greater').pvalue) if wins+losses else 1.
                row['paired_factor24']=dict(new_only=wins,old_only=losses,p=paired,required_gate=paired<=.01,old_detections=sum(r['old_v2']['flag'] for r in records))
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
        paths=[R/'run.py',R/'core.py',R/'PROTOCOL.md',R/'DEVELOPMENT.json',R/'development-core.py',core.ROOT/'sh-qok-context-transfer-v1/run.py',core.ROOT/'sh-qok-context-transfer-v1/PROTOCOL.md',core.ROOT/'sh-qok-context-transfer-v2/run.py',core.ROOT/'sh-qok-context-transfer-v2/PROTOCOL.md',core.ROOT/'sh-qok-context-transfer-v2/QUALIFICATION.json',core.a.SOURCE,core.ROOT/'complete-atlas-v56/SOURCE-MANIFEST.json',core.ROOT/'sh-qok-ending-qualification-reed-v94/run.py']
        save('FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p):sha(p) for p in paths}));(R/'trials').mkdir();log('freeze_complete');print('FROZEN')
    elif mode=='qualify':qualify()
    elif mode=='manuscript':manuscript()
    else:raise ValueError(mode)
