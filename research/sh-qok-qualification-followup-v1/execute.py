import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,hashlib,math,itertools,collections,time
from decimal import Decimal,localcontext
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.stats import beta
R=Path(__file__).resolve().parent;OLD=R.parent/'sh-qok-context-map-v3';RUN=R/'run-2026-10-24'
sys.path.insert(0,str(OLD));import analysis as a
sys.path.insert(0,str(R));from diagnose import oracle
CC={};GEOM={};EVENTS=[];HJ={};HBASE={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(RUN/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def verify():
 f=json.loads((R/'FREEZE.json').read_text());assert all(sha(p)==h for p,h in f['hashes'].items())
 old=json.loads((R/'PRESERVED-ATTEMPT.json').read_text());assert all(sha(OLD/p)==h for p,h in old['hashes'].items())
 if (RUN/'EXECUTION-FREEZE.json').exists():
  ex=json.loads((RUN/'EXECUTION-FREEZE.json').read_text());assert all(sha(p)==h for p,h in ex['hashes'].items())
def init():
 global CC,GEOM,EVENTS,HJ,HBASE
 EVENTS=json.loads((OLD/'MASKED-v3.1.json').read_text());CC=a.cells(EVENTS)
 GEOM={}
 for key,vv in CC.items():
  page_last={v['folio']:i for i,v in enumerate(vv)};line_last={v['line']:i for i,v in enumerate(vv)}
  GEOM[key]=dict(page_ix=np.array([page_last[v['folio']] for v in vv]),line_ix=np.array([line_last[v['line']] for v in vv]),x=np.array([v['x'] for v in vv]),pos=np.array([.7*(2*v['position']/max(1,v['length']-1)-1) for v in vv]),is_y=np.array([v['origin'][-1]=='y' for v in vv]))
 HJ={co:[v.copy() for v in EVENTS if v['reading']==co and v['context'] in ['C1','C2','C3','C4','C5']] for co in ['H','F']};HBASE={}
 for ri,co in enumerate(['H','F']):
  vv=HJ[co]
  for v in vv:v['y']=0
  _,lab,hands,_=a.hetero_data(vv,['C1','C2','C3','C4','C5']);HBASE[co]=a.permutation_labels(lab,hands,6100000+ri)
def bulk(key,scenario,seed):
 # Same per-event choice draws and overwrite-last page/line mapping as e.synthetic.
 # Only batching is changed; original generator is replayed in preflight and all post-run flag audits.
 rng=np.random.default_rng(seed);g=GEOM[key];n=len(CC[key]);pages=rng.choice([-.7,.7],size=n);lines=rng.choice([-.7,.7],size=n)
 if scenario in ['null_low','availability_only']:p=.2
 elif scenario=='null_high':p=.6
 elif scenario=='junction_only':p=.1+.5*g['is_y']
 elif scenario=='positive':p=.2+.15*g['x']
 elif scenario=='additive':
  z=-1+pages[g['page_ix']]+lines[g['line_ix']]+g['pos'];p=np.array([1/(1+math.exp(-float(v))) for v in z])
 else:raise ValueError(scenario)
 return (rng.random(n)<p).astype(int)
def preflight():
 verify();RUN.mkdir(exist_ok=True);assert not (RUN/'EXECUTION-FREEZE.json').exists();init()
 assert all('y' not in v and 'follower' not in v and 'outcome' not in v for v in EVENTS)
 support=json.loads((OLD/'SUPPORT-v3.1.json').read_text())
 for k,vv in CC.items():assert a.e.support(vv)==support[k]
 old=[json.loads(s) for s in (OLD/'SYNTHETIC-TRIALS-v3.1.jsonl').read_text().splitlines()];samples=[]
 for k in CC:
  for scene in ['null_low','null_high','additive','junction_only','positive']:
   rr=[v for v in old if v['cell']==k and v['scenario']==scene]
   for rec in [rr[0],rr[-1]]:
    direct=a.e.synthetic(CC[k],scene,rec['seed']);fast=bulk(k,scene,rec['seed']);assert np.array_equal(direct,fast)
    assert hashlib.sha256(direct.astype(np.uint8).tobytes()).hexdigest()==rec['outcome_sha256']
    samples.append(dict(cell=k,scenario=scene,seed=rec['seed']))
 checks=0
 for n in range(2,7):
  for k in range(1,n):
   vv=[dict(folio='toy',family='y',x=int(i<k)) for i in range(n)]
   for bits in itertools.product([0,1],repeat=n):
    y=np.array(bits);p=oracle(vv,y);q=a.e.exact(vv,y)['p'];assert p is None and q is None or abs(p-q)<1e-11;checks+=1
 save('PREFLIGHT.json',dict(status='PASS',support_reproduced=True,masked_outcomes_absent=True,original_seed_replays=samples,bulk_generator_bitwise_outcome_equivalence=True,exact_small_oracles=checks,original39_files_unchanged=True))
 paths=[Path(__file__),RUN/'PREFLIGHT.json',R/'FREEZE.json',OLD/'analysis.py',OLD/'preflight.py',R/'diagnose.py',R.parent/'sh-qok-single-target-attempt-c/engine.py']
 save('EXECUTION-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),authority='User authorized full fixed run including separate BQ2 diagnostic',method='Frozen protocol unchanged. Production exact engine is called directly. Generator random draws are batched with bitwise outcome equivalence checked against80 old coordinate cases and audited against original generation for every false flag and trial0. No new candidate or statistical retuning.',hashes={str(p):sha(p) for p in paths}))
 print('Preflight PASS; execution frozen',flush=True)
def primary_chunk(task):
 ji,start,stop=task;j=json.loads((R/'JOBS.json').read_text())[ji];out=[];vv=CC[j['cell']]
 for t in range(start,stop):
  seed=[913260,j['reading_index'],j['cell_index'],j['scenario_index'],t];y=bulk(j['cell'],j['scenario'],seed);rr=a.e.exact(vv,y);p=rr['p']
  out.append(dict(job_index=ji,cell=j['cell'],scenario=j['scenario'],trial=t,seed=seed,p=p,flag=p is not None and p<=j['nominal_alpha'],degenerate=rr['degenerate'],outcome_sha256=hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest()))
 return out
def primary():
 verify();jobs=json.loads((R/'JOBS.json').read_text());D=RUN/'primary';D.mkdir(exist_ok=True);tasks=[]
 for ji,j in enumerate(jobs):
  for start in range(0,j['N'],200):
   dest=D/f'{ji:02d}-{start:05d}.jsonl';stop=min(start+200,j['N'])
   if dest.exists():
    rr=[json.loads(s) for s in dest.read_text().splitlines()];assert len(rr)==stop-start and all(r['job_index']==ji and r['trial']==start+i for i,r in enumerate(rr));continue
   tasks.append((ji,start,stop))
 with ProcessPoolExecutor(max_workers=3,initializer=init) as pool:
  for task,rows in zip(tasks,pool.map(primary_chunk,tasks,chunksize=1)):
   ji,start,stop=task;dest=D/f'{ji:02d}-{start:05d}.jsonl';temp=dest.with_suffix('.tmp');temp.write_text(''.join(json.dumps(v)+'\n' for v in rows));temp.replace(dest)
   print('Primary',ji,start,stop,'committed',flush=True)
 save('PRIMARY-COMPLETE.json',dict(complete=True,trials=sum(j['N'] for j in jobs),chunks=len(list(D.glob('*.jsonl')))));print('PRIMARY COMPLETE',flush=True)
def bank_details(terms,mat,pages,contexts):
 bad=[];badrows=set()
 for j,c in enumerate(contexts):
  mask=(mat==j).astype(float);m=mask.sum(axis=1);den=mask@terms[:,1];num=mask@terms[:,0]
  with np.errstate(divide='ignore',invalid='ignore'):
   rd=num/den;res=(mask@np.square(terms[:,0]))-2*rd*(mask@(terms[:,0]*terms[:,1]))+rd**2*(mask@np.square(terms[:,1]));var=m/(m-1)*np.maximum(0,res)/den**2
  for ix in np.where(~np.isfinite(rd)|~np.isfinite(var)|(var<=1e-20))[0]:
   selected=np.where(mat[ix]==j)[0];ar=terms[selected];direct=a.cluster(ar);badrows.add(int(ix));high=None
   with localcontext() as dc:
    dc.prec=80;nn=[Decimal.from_float(float(x)) for x in ar[:,0]];dd=[Decimal.from_float(float(x)) for x in ar[:,1]];sd=sum(dd)
    if len(ar)>1 and sd:
     mean=sum(nn)/sd;high=Decimal(len(ar))/Decimal(len(ar)-1)*sum((n-mean*d)**2 for n,d in zip(nn,dd))/sd**2
   classification='NO_SUPPORT' if high is None else 'GENUINE_ZERO_STORED_TERMS' if high==0 else 'BELOW_FROZEN_VARIANCE_FLOOR' if high<=Decimal('1e-20') else 'NUMERICAL_CANCELLATION'
   bad.append(dict(shuffle_index=int(ix),observed=bool(ix==0),context=c,folio_count=len(selected),folios=[pages[i] for i in selected],terms=ar.tolist(),vectorized_variance=float(var[ix]) if np.isfinite(var[ix]) else None,direct_centered_variance=direct[1],decimal80_variance=str(high) if high is not None else None,classification=classification))
 return dict(undefined_shuffles=sum(i>0 for i in badrows),observed_defined=0 not in badrows,undefined_contexts=bad,context_counts={c:int((mat[0]==j).sum()) for j,c in enumerate(contexts)})
def hetero_one(task):
 ri,si,t=task;co=['H','F'][ri];scene=['homogeneous_null','homogeneous_positive'][si];vv=HJ[co];outseed=5100000+ri*100000+si*1000+t;rng=np.random.default_rng(outseed)
 y=(rng.random(len(vv))<np.array([.2+(.08*v['x'] if si==1 else 0) for v in vv])).astype(int)
 for v,yy in zip(vv,y):v['y']=int(yy)
 cs=['C1','C2','C3','C4','C5'];terms,lab,hands,pages=a.hetero_data(vv,cs);banks=[]
 for bi in [0,1,2]:
  seed=6100000+ri if bi==0 else [913261,ri,si,t,bi];mat=HBASE[co] if bi==0 else a.permutation_labels(lab,hands,seed);rr=a.perm_test(terms,mat,5)
  detail=bank_details(terms,mat,pages,cs) if rr['p'] is None else dict(undefined_shuffles=0,observed_defined=True,undefined_contexts=[],context_counts={c:int((lab==j).sum()) for j,c in enumerate(cs)})
  banks.append(dict(bank_index=bi,seed=seed,flag=rr['p'] is not None and rr['p']<=.025,**rr,**detail))
 return dict(reading=co,reading_index=ri,scenario=scene,scenario_index=si,trial=t,outcome_seed=outseed,outcome_sha256=hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest(),banks=banks)
def hetero():
 verify();D=RUN/'bq2';D.mkdir(exist_ok=True);tasks=[]
 old={(r['reading'],r['scenario'],r['trial']):r for r in [json.loads(s) for s in (OLD/'HETEROGENEITY-CONTROLS.jsonl').read_text().splitlines()]}
 for ri in range(2):
  for si in range(2):
   for t in range(200):
    p=D/f'{ri}-{si}-{t:03d}.json'
    if not p.exists():tasks.append((ri,si,t))
 with ProcessPoolExecutor(max_workers=3,initializer=init) as pool:
  for task,rr in zip(tasks,pool.map(hetero_one,tasks,chunksize=1)):
   baseline=rr['banks'][0];prev=old[rr['reading'],rr['scenario'],rr['trial']]
   for key in ['status','p','flag','Q','exceedances','permutation_Q_sha256','undefined_shuffles','observed_defined']:
    if key in prev:assert baseline.get(key)==prev[key],('baseline mismatch',task,key,baseline.get(key),prev[key])
   ri,si,t=task;p=D/f'{ri}-{si}-{t:03d}.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(rr,indent=2));tmp.replace(p);print('BQ2',ri,si,t,'committed',flush=True)
 save('BQ2-COMPLETE.json',dict(complete=True,outer_trials=800,banks_per_trial=3,baseline_shuffles=8000000,fresh_shuffles=16000000,files=len(list(D.glob('*.json')))));print('BQ2 COMPLETE',flush=True)
def audit():
 verify();init();records=[];near=[]
 for path in sorted((RUN/'primary').glob('*.jsonl')):
  for line in path.read_text().splitlines():
   r=json.loads(line);job=json.loads((R/'JOBS.json').read_text())[r['job_index']]
   if not (r['trial']==0 or (job['scenario']!='positive' and r['flag'])):continue
   vv=CC[r['cell']];scene='null_low' if r['scenario']=='availability_only' else r['scenario'];y=a.e.synthetic(vv,scene,r['seed']);assert hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest()==r['outcome_sha256'];p=oracle(vv,y)
   err=abs(p-r['p']) if p is not None and r['p'] is not None else 0;assert err<1e-11
   if p is not None and abs(p-job['nominal_alpha'])<1e-11:near.append(r)
   else:assert (p is not None and p<=job['nominal_alpha'])==r['flag']
   records.append(dict(job_index=r['job_index'],trial=r['trial'],p_error=err))
 # Exact rational oracle for any classification within floating tolerance of the boundary.
 rational=[]
 for r in near:
  from fractions import Fraction
  vv=CC[r['cell']];y=a.e.synthetic(vv,'null_low' if r['scenario']=='availability_only' else r['scenario'],r['seed']);dist={0:1};offset=obs=0
  for ix in a.e.grouping(vv).values():
   ns=sum(vv[i]['x'] for i in ix);nc=len(ix)-ns;t=sum(int(y[i]) for i in ix);lo=max(0,t-nc);hi=min(ns,t);local={j-lo:math.comb(ns,j)*math.comb(nc,t-j) for j in range(lo,hi+1)};offset+=lo;obs+=sum(int(y[i])*vv[i]['x'] for i in ix);new=collections.Counter()
   for s,c in dist.items():
    for z,d in local.items():new[s+z]+=c*d
   dist=dict(new)
  pp=Fraction(sum(c for k,c in dist.items() if k>=obs-offset),sum(dist.values()));alpha=Fraction(1,60 if r['cell'].startswith('A-') else 40);assert (pp<=alpha)==r['flag'];rational.append(dict(job_index=r['job_index'],trial=r['trial'],p_numerator=str(pp.numerator),p_denominator=str(pp.denominator)))
 save('POSTRUN-AUDIT.json',dict(status='PASS',audited_trials=len(records),max_error=max(x['p_error'] for x in records),records=records,rational_boundary_checks=rational,original_attempt_unchanged=True));print('AUDIT PASS',len(records),flush=True)
def summarize():
 verify();assert all((RUN/n).exists() for n in ['PRIMARY-COMPLETE.json','BQ2-COMPLETE.json','POSTRUN-AUDIT.json']);jobs=json.loads((R/'JOBS.json').read_text());counts=collections.defaultdict(lambda:[0,0,0]);ids=set()
 for p in sorted((RUN/'primary').glob('*.jsonl')):
  for line in p.read_text().splitlines():
   r=json.loads(line);key=(r['job_index'],r['trial']);assert key not in ids;ids.add(key);c=counts[r['job_index']];c[0]+=1;c[1]+=r['flag'];c[2]+=r['degenerate']
 results=[];cells=collections.defaultdict(list)
 for ji,j in enumerate(jobs):
  n,k,deg=counts[ji];assert n==j['N'];err=.05/46;lo=0 if k==0 else float(beta.ppf(err/2,k,n-k+1));hi=1 if k==n else float(beta.ppf(1-err/2,k+1,n-k));power=j['scenario']=='positive'
  decision=('POWER QUALIFIED' if lo>=.8 else 'EVIDENCE UNDERPOWERED' if hi<.8 else 'POWER INCONCLUSIVE') if power else ('CERTIFIED BELOW TOLERANCE' if hi<=.05 else 'EVIDENCE ABOVE TOLERANCE' if lo>.05 else 'INCONCLUSIVE')
  nominal=not power and lo>j['nominal_alpha'];row=dict(**j,flags=k,n=n,rate=k/n,degenerate=deg,simultaneous_exact_CI95=[lo,hi],wilson95_descriptive=a.e.wilson(k,n),decision=decision,nominal_size_excess=bool(nominal),exchangeable_nominal_alarm=bool(nominal and j['scenario']!='additive'));results.append(row);cells[j['cell']].append(row)
 cs={}
 for key,rr in cells.items():
  passed=all(r['decision'] in ['POWER QUALIFIED','CERTIFIED BELOW TOLERANCE'] and not r['exchangeable_nominal_alarm'] for r in rr);cs[key]=dict(status='QUALIFIED' if passed else 'NOT QUALIFIED',inconclusive=any('INCONCLUSIVE' in r['decision'] for r in rr),nominal_alarm=any(r['exchangeable_nominal_alarm'] for r in rr))
 save('PRIMARY-SUMMARY.json',dict(total_trials=len(ids),cells=cs,results=results))
 hetero=[json.loads(p.read_text()) for p in sorted((RUN/'bq2').glob('*.json'))];assert len(hetero)==800;hs=[]
 for co in ['H','F']:
  for scene in ['homogeneous_null','homogeneous_positive']:
   rr=[r for r in hetero if r['reading']==co and r['scenario']==scene];banks=[]
   for bi in range(3):
    bb=[r['banks'][bi] for r in rr];n=sum(b['p'] is not None for b in bb);k=sum(b['flag'] for b in bb);classes=collections.Counter(c['classification'] for b in bb for c in b['undefined_contexts'])
    banks.append(dict(bank_index=bi,outer_denominator=200,defined=n,undefined=200-n,flags=k,flag_rate_all200=k/200,flag_rate_defined_only=k/n if n else None,undefined_contexts_by_class=dict(classes),undefined_shuffle_total=sum(b['undefined_shuffles'] for b in bb)))
   pair=[]
   for i,j in [(0,1),(0,2),(1,2)]:pair.append(dict(banks=[i,j],flag_disagreements=sum(r['banks'][i]['flag']!=r['banks'][j]['flag'] for r in rr),both_defined=sum(r['banks'][i]['p'] is not None and r['banks'][j]['p'] is not None for r in rr),flag_disagreements_both_defined=sum(r['banks'][i]['flag']!=r['banks'][j]['flag'] for r in rr if r['banks'][i]['p'] is not None and r['banks'][j]['p'] is not None)))
   hs.append(dict(reading=co,scenario=scene,banks=banks,pairwise=pair))
 save('BQ2-SUMMARY.json',dict(status='DIAGNOSTIC ONLY; NO QUALIFICATION OR MANUSCRIPT PROMOTION',outer_trials=800,results=hs));print(json.dumps(cs,indent=2),flush=True)
if __name__=='__main__':
 {'preflight':preflight,'primary':primary,'bq2':hetero,'audit':audit,'summarize':summarize}[sys.argv[1]]()
