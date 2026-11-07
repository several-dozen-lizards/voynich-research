from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;FILES=[P/'sh-qok-matched-effect/run.py',P/'sh-qok-all-interior/run.py',P/'sh-qok-expanded-null/run.py']
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Synthetic joint-rule qualification only. No manuscript reads; H/F separate.',rule='Allinterior exactbody matched support V>=80, >=8pageswithV, maxpage share<=.25 AND matched availability f_ch>=.10,f_sh>=.25. Outcomes not used. Boundarychallenge80<=V<84. Feasibility may vary across conditional orientations: empirically test selected nulls, do not assume selection innocuous.',design='Two independent synthetic layouts:1body,22..30lines/page;4bodies,60..110lines/page.12pages,length12,originprob.70,2%unknown. Prefixp=.5. First100accepted nearthreshold layouts perdesign,max1500attempts; preserve every rejected support/feasibility record. Seeds1110000+design*100000+attempt. All matched positive rates target.10/.25 using previous frozen weighted calibration.',outcomes='After acceptance, draw independent null outcomes with available-nonoriginqokprob.2 and.6; positive assigns matched availablefollowers .10/f_ch or.25/f_sh, unmatchedprob.2. Exact unchanged nullBonferroni8. No outcome-driven rejection. Nulls are NOT prefixcalibrated.',gates='Eachdesign needs100accepted layouts. PositiveWilson95 lowerpower>=.80; eachnullupperfalseflag<=.10. Missingquota or anyfailedgate=FAIL. Keep realized matched effects, failures and all attempts. No repair afteroutcomes. No manuscript application evenifpass.',limits='Only this80..84band and these architectures; no evidence of universal minimum or actual manuscript availability. Feasibilityscreen conditions on prefixarrangement and can bias nulls. Constant-score nulls retained. Fourbodycontrol is more diverse, not historical realism.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json']+FILES});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(path,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),e)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(FILES[2],['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(FILES[1],['matching','events','score','ci'],env)
matched=dict(collections=collections,env=env);load(FILES[0],['extract','rates'],matched)
attempts=[];records=[]
for di,pool in enumerate([1,4]):
 accepted=0
 for attempt in range(1500):
  seed=1110000+di*100000+attempt;rng=np.random.default_rng(seed);N=int(rng.integers(22,31) if pool==1 else rng.integers(60,111));rows=[]
  for pg in range(12):
   for line in range(N):
    ws=[('sh' if rng.random()<.5 else 'ch')+'abcd'[int(rng.integers(pool))]+'edy' if rng.random()<.7 else 'dar' for j in range(12)];ws=[None if rng.random()<.02 else w for w in ws];rows.append((pg,ws))
  groups=matched['extract'](rows);V=sum(v for v,e in groups);f=matched['rates'](rows,groups,True);pagev=[0.]*12
  for v,entries in groups:pagev[rows[entries[0][0]][0]]+=v
  npages=sum(v>0 for v in pagev);share=max(pagev)/V if V else 1.;support=V>=80 and npages>=8 and share<=.25;feasible=f[0]>=.1 and f[1]>=.25;ok=support and feasible and V<84
  attempts.append(dict(pool=pool,seed=seed,lines_per_page=N,V=V,availability=f,pages=npages,max_share=share,support=support,feasible=feasible,accepted=ok))
  if not ok:continue
  qrng=np.random.default_rng(seed+5000000)
  for scenario in ['null_low','null_high','positive']:
   probs={}
   if scenario=='positive':
    for v,entries in groups:
     for ri,j,k,left in entries:
      for pos,a in [(j,left),(k,1-left)]:
       if not rows[ri][1][pos+1].startswith(('sh','ch')):
        key=(ri,pos+1);assert key not in probs;probs[key]=(.1 if a==0 else .25)/f[a]
   baseline=.6 if scenario=='null_high' else .2
   new=[(pg,[w if w is None or w.startswith(('sh','ch')) else 'qokam' if qrng.random()<probs.get((ri,j),baseline) else 'dar' for j,w in enumerate(ws)]) for ri,(pg,ws) in enumerate(rows)]
   assert matched['extract'](new)==groups
   result=env['score'](new);rr=matched['rates'](new,groups);assert abs(result['V']-V)<1e-9
   records.append(dict(pool=pool,seed=seed,scenario=scenario,availability=f,expected_gap=.15 if scenario=='positive' else baseline*(f[1]-f[0]),observed_gap=rr[1]-rr[0],**result))
  accepted+=1
  if accepted%25==0:print(pool,'accepted',accepted,'attempt',attempt+1,flush=True)
  if accepted==100:break
 save('ATTEMPTS.json',attempts);save('TRIALS.json',records);print(pool,'finished',accepted,flush=True)
summary=[]
for pool,scenario in itertools.product([1,4],['null_low','null_high','positive']):
 rr=[r for r in records if r['pool']==pool and r['scenario']==scenario];n=len(rr);k=sum(r['flag'] for r in rr);ci=env['ci'](k,n) if n else [0,1]
 summary.append(dict(pool=pool,scenario=scenario,n=n,flags=k,wilson95=ci,pass_gate=n==100 and (ci[0]>=.8 if scenario=='positive' else ci[1]<=.1),mean_observed_gap=float(np.mean([r['observed_gap'] for r in rr])) if rr else None,V_range=[min(r['V'] for r in rr),max(r['V'] for r in rr)] if rr else [],not_estimable=sum(r['p_adjusted'] is None for r in rr)))
save('SUMMARY.json',dict(status='PASS_LIMITED_SCOPE' if all(r['pass_gate'] for r in summary) else 'FAIL',results=summary));save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),matching_fixed_before_outcomes=True,records=len(records),attempts=len(attempts),manuscript_read=False))
