from pathlib import Path
import ast,types,json,hashlib,collections,itertools,functools,math,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent;SRC=P/'sh-qok-all-interior/run.py';SUB=P/'sh-qok-expanded-null/run.py'
def save(n,x):(R/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='freeze':
 save('PROTOCOL.json',dict(scope='Fresh synthetic matched-effect diagnostic only; no manuscript reads, H/F separate.',design='100fresh layouts for each density.35/.70 x variablelength6..14/fixed12 x bodypool1/12;12pages24lines,2%unknownslots. Seeds1090000+cell*1000+trial. Actual token arrays, no overwritten origins.',matching='Unchanged allinterior body-only maximumweight pairing, exactpage/length/body groups. Identify discordant groups with0<k<n before outcomes. Vg=k(n-k)/n. Matched contrast defined as Vg-weighted mean of group sh-following-qok rate minus ch-following-qok rate, across those groups only. This effect summary is explicit; exacttest statistic remains total sh*qok.',calibration='Compute Vg-weighted available-follower fractions f_ch,f_sh within movablegroups, including structural-zero followers. Target weighted rates .10 and .25; assign available matched followers probabilities .10/f_ch and .25/f_sh. Require totalV>0 and fractions>=targets; otherwise record no_support or infeasible without positive scoring. Uniform draws only after matching/calibration. This calibrates weighted aggregate, not eachgroup. Save analytic expectation and realized weighted contrast.',controls='For every layout run independent null: qokprob.2 on all available nonorigins, no prefix-conditioned calibration. For feasible positive place target probabilities on matched followers; unmatched available followers prob.2. Matched corner followers cannot overlap between origins. Qok never replaces origins/unknowns. Verify matching/support unchanged by generated outcomes.',gates='Per cell100attempts: positive practical-power denominator includes no_support/infeasible failures; require Wilson95 lower>=.80. Report feasible-only power separately. Null upper<=.10; constant-score cases not negativeevidence. Anygatefailure retained; no qualification or scoring of manuscript. No reruns/repair after outcomes.'))
 save('FREEZE.json',{str(p):sha(p) for p in [Path(__file__),R/'PROTOCOL.json',SRC,SUB]});print('Frozen');sys.exit()
for p,h in json.loads((R/'FREEZE.json').read_text()).items():assert sha(Path(p))==h
def load(p,names,e):exec(compile(ast.Module(body=[n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),e)
m=types.ModuleType('subset');m.__dict__.update(collections=collections);load(SUB,['subset'],m.__dict__)
env=dict(np=np,math=math,collections=collections,functools=functools,m=m);load(SRC,['matching','events','score','ci'],env)
def extract(rows):
 strata=collections.defaultdict(list)
 for ri,(pg,ws) in enumerate(rows):strata[pg,len(ws)].append((ri,env['events'](ws)))
 groups=[]
 for (pg,L),lines in strata.items():
  weights={}
  for j in range(1,L-1):
   for k in range(j+1,L-1):
    c=collections.Counter(e[j][0] for ri,e in lines if j in e and k in e and e[j][0]==e[k][0]);weights[j,k]=sum(n*(n-1)//2 for n in c.values())
  _,pairs=env['matching'](range(1,L-1),weights)
  for j,k in pairs:
   dd=collections.defaultdict(list)
   for ri,e in lines:
    if j in e and k in e and e[j][0]==e[k][0] and e[j][1]!=e[k][1]:dd[e[j][0]].append((ri,j,k,e[j][1]))
   for entries in dd.values():
    n=len(entries);ns=sum(z[3] for z in entries)
    if 0<ns<n:groups.append((ns*(n-ns)/n,entries))
 return groups
def rates(rows,groups,availability=False):
 out=[0.,0.];total=sum(v for v,e in groups)
 for v,entries in groups:
  c=[0.,0.]
  for ri,j,k,left in entries:
   for pos,variant in [(j,left),(k,1-left)]:
    w=rows[ri][1][pos+1];c[variant]+=not w.startswith(('sh','ch')) if availability else w.startswith('qok')
  for a in range(2):out[a]+=v*c[a]/len(entries)
 return [x/total for x in out] if total else [0.,0.]
records=[];cells=list(itertools.product([.35,.70],['variable','fixed'],[1,12]))
for ix,(density,lengths,pool) in enumerate(cells):
 for trial in range(100):
  seed=1090000+ix*1000+trial;rng=np.random.default_rng(seed);rows=[]
  for pg in range(12):
   for line in range(24):
    L=int(rng.integers(6,15)) if lengths=='variable' else 12;ws=[]
    for j in range(L):
     if rng.random()<density:ws.append(('sh' if rng.random()<.5 else 'ch')+'abcdefghijkl'[int(rng.integers(pool))]+'edy')
     else:ws.append('dar')
    ws=[None if rng.random()<.02 else w for w in ws];rows.append((pg,ws))
  groups=extract(rows);V=sum(v for v,e in groups);f=rates(rows,groups,True);status='no_support' if not V else 'infeasible' if f[0]<.1 or f[1]<.25 else 'feasible'
  common=dict(density=density,lengths=lengths,pool=pool,trial=trial,seed=seed,V=V,availability=f,positive_status=status)
  for scenario in ['null','positive']:
   if scenario=='positive' and status!='feasible':records.append(common|dict(scenario=scenario,flag=False,p_adjusted=None,expected_gap=None,observed_gap=None));continue
   probs={}
   if scenario=='positive':
    for v,entries in groups:
     for ri,j,k,left in entries:
      for pos,a in [(j,left),(k,1-left)]:
       if not rows[ri][1][pos+1].startswith(('sh','ch')):
        key=(ri,pos+1);assert key not in probs;probs[key]=(.1 if a==0 else .25)/f[a]
   new=[]
   for ri,(pg,ws) in enumerate(rows):new.append((pg,[w if w is None or w.startswith(('sh','ch')) else 'qokam' if rng.random()<probs.get((ri,j),.2) else 'dar' for j,w in enumerate(ws)]))
   assert extract(new)==groups
   expected=.15 if scenario=='positive' else .2*(f[1]-f[0])
   if scenario=='positive':assert abs(f[1]*(.25/f[1])-f[0]*(.1/f[0])-.15)<1e-12
   rr=rates(new,groups);result=env['score'](new);assert abs(result['V']-V)<1e-9
   records.append(common|result|dict(scenario=scenario,expected_gap=expected if V else None,observed_gap=rr[1]-rr[0] if V else None))
 save('TRIALS.json',records);print(density,lengths,pool,'complete',flush=True)
summary=[]
for density,lengths,pool in cells:
 for scenario in ['null','positive']:
  rr=[r for r in records if (r['density'],r['lengths'],r['pool'],r['scenario'])==(density,lengths,pool,scenario)];k=sum(r['flag'] for r in rr);ci=env['ci'](k,100);valid=[r for r in rr if r['positive_status']=='feasible'];obs=[r['observed_gap'] for r in rr if r['observed_gap'] is not None]
  summary.append(dict(density=density,lengths=lengths,pool=pool,scenario=scenario,flags=k,n=100,status_counts=dict(collections.Counter(r['positive_status'] for r in rr)),feasible_positive_flags=sum(r['flag'] for r in valid) if scenario=='positive' else None,mean_observed_gap=float(np.mean(obs)) if obs else None,medianV=float(np.median([r['V'] for r in rr])),wilson95=ci,pass_gate=ci[1]<=.10 if scenario=='null' else ci[0]>=.80))
save('SUMMARY.json',summary);save('VERIFICATION.json',dict(hashes_unchanged=all(sha(Path(p))==h for p,h in json.loads((R/'FREEZE.json').read_text()).items()),matched_expectation_verified=True,matching_unchanged_after_outcomes=True,records=len(records),manuscript_read=False))
