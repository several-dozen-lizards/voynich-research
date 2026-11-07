import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,csv,hashlib,math,importlib.util,time
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.stats import beta,chi2
R=Path(__file__).resolve().parent;P=R.parent;V2=P/'bq2-baseline-fixed-v2'
sp=importlib.util.spec_from_file_location('unchanged_v2',V2/'engine.py');v2=importlib.util.module_from_spec(sp);sp.loader.exec_module(v2)
ARCH=['uniform','unequal','available'];COMMON=[0.,.08];DELTAS=[.04,.08,.12,.16,.20,.24,.28,.32,.40,.48];M=612;GG={};JOBS=[]
def sha(p):
 path=Path(p)
 for attempt in range(3):
  try:
   h=hashlib.sha256()
   with path.open('rb') as f:
    while True:
     block=f.read(1024*1024)
     if not block:break
     h.update(block)
   return h.hexdigest()
  except OSError as error:
   with (R/'IO-RETRIES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(path=str(path),attempt=attempt,error=str(error)))+'\n')
   if attempt==2:raise OSError(f'Cannot hash preserved file: {path}') from error
   time.sleep(.2*(attempt+1))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def seal(phase,names):
 with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=phase,utc=datetime.now(timezone.utc).isoformat(),hashes={n:sha(R/n) for n in names}))+'\n')
def verify():
 preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in preserved['hashes'].items())
 for s in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(s)['hashes'].items():assert sha(R/n)==h,('changed frozen file',n)
def freeze():
 assert not (R/'PROTOCOL.json').exists()
 v=json.loads((V2/'VERIFICATION.json').read_text());assert all(sha(V2/n)==h for n,h in v['artifact_hashes'].items());old=json.loads((V2/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in old['hashes'].items())
 roots=['sh-qok-context-map-v3','sh-qok-qualification-followup-v1','sh-qok-retrospective-readjudication-v1','currier-a-available-only-v1','bq2-replacement-v1','bq2-baseline-fixed-v2'];preserved={str(p):sha(p) for root in roots for p in (P/root).rglob('*') if p.is_file() and '__pycache__' not in p.parts};save('PRESERVATION.json',dict(hashes=preserved))
 prior=json.loads((V2/'QUALIFICATION.json').read_text());assert all(prior['results'][co]['status']=='QUALIFIED CALIBRATION' for co in ['H','F'])
 save('PROTOCOL.json',dict(status='FROZEN BEFORE POWER-STUDY SUPPORT AND NEW OUTCOMES',utc=datetime.now(timezone.utc).isoformat(),authority='User explicitly requested freeze and run real-support V2 power curve; preserve prior attempts, H/F separate, retain inconclusive results.',scope='Simulation power study only. Unchanged V2 engine/statistic/working variances/chi-square3 reference and conservative Holm2 detection threshold rawp<=.025. No new manuscript scores, model fitting, altered correction or old/new pooling.',geometry='Same original V2 supported folios and masked events for H/F. Verify support exactly, including context pages76H/72F total and sparse contexts; no added folios or raw EVT/zodiac access.',effect='Common aggregate sh-ch risk difference b in every context, plus additional positive difference delta in one target context at a time C1-C5. Delta is a percentage-point difference of section effects, not a relative percentage or an event rate shared by all sections. Other contexts have effect b. Primary statistic still tests within-scribe heterogeneity.',grid=dict(targets=v2.CONTEXTS,common_effects_points=[0,8],positive_differences_points=[4,8,12,16,20,24,28,32,40,48],architecture=['uniform: ch probability.20, sh=.20+b+delta_in_target','unequal: ch probabilities C1..C5=.10,.40,.20,.15,.45, sh=ch+b+delta_in_target','available: blocked followers0, availablepch=.20/fch,c, availablepsh=(.20+b+delta_in_target)/fsh,c. f from unchanged masked MH-weighted available fractions. Aggregate effects exactly b+delta_target.'],zero='One shared zero-difference guard cell per reading/architecture/common b, not five duplicate controls. Twelve zero cells;600 positive cells before feasibility. Zero estimates appear in all matching target plots as the same guard, never independent replications.',feasibility='Before outcomes, compute every event probability and expected MH effects for every cell. Out-of-[0,1] probabilities mark INFEASIBLE, retain cell with no trials/CI. Never clip probabilities, replace baseline, reduce target or add effect points. Infeasible cells still occupy simultaneous-interval family slots.'),simulation=dict(N_positive=2000,N_zero_guard=10000,potential_total=1320000,planned='Run every feasible frozen coordinate once; actual total fixed by outcome-blind feasibility. No extension, optional stopping, seed replacement, adaptive grid or model retuning.',seed='[919260,reading_index H0/F1,architecture_index uniform0/unequal1/available2,common_index0/1,target_index0..4 or5 for zero guard,grid_index1..10 or0 for zero,trial]. Independent fresh streams by coordinate, not pooled across H/F or cells.',records='Every hit and miss retains job/trial/seed,T,p,flag,uniform status and outcome SHA256. Compact sufficient receipts; all details reproducible from masked geometry and frozen engine. Fixed500-trial checkpoint chunks, missing coordinates only on resume.'),uncertainty=dict(family=612,interval='612 simultaneous two-sided exact Clopper-Pearson intervals, per-interval error.05/612. Includes12 guards+600 positive slots, even infeasible slots, so confidence remains conservative. No pointwise-CI threshold picking.',reliability='Power>=80% is the fixed target: LOWER>=.80 RELIABLY DETECTABLE; UPPER<.80 BELOW80% TARGET; otherwise INCONCLUSIVE. Retain the interval and label; do not add trials.',guards='For each reading/architecture/common level, zero-difference guard must have U<=.05 and L<=.025; L>.025 NOMINAL ALARM, L>.05 ABOVE PRACTICAL TOLERANCE, otherwise failed bound INCONCLUSIVE. Failed/inconclusive guard blocks reliability certification of its curves, but measured power and every trial remain. This does not retroactively alter V2 qualification or manuscript results.'),summaries='Report all cells and60 individual curves(reading xarchitecture xcommon xtarget). First reliable tested point and first sustained reliable tested point through all larger feasible tested grid points, with no monotonic fit, smoothing or interpolation. Keep infeasible boundaries and gaps. A ten-row cross-reading/architecture summary requires reliability in each of six H/Fxarchitecture cells at a grid point, separately for each target/common. This means80% marginal power in each reading, not80% joint detection probability; do not pool or multiply H/F power.',verification='Freeze before support and outcomes; reproduce V2 support exactly; analytic expected context effects for every feasible generator. Production generator bitwise-equals V2 original positive generators for targetC1,b0,delta.12 and matching zero guards. First/middle/last planned trial of every feasible cell and every zero-guard false flag independently regenerated and scalar-audited. Trial counts/coordinate uniqueness and simultaneous bounds recalculated; preserve all previous non-cache file hashes.',plots='Static scientific PNG and SVG per reading, six panels(common level xbaseline architecture), five target-context curves. Display simultaneous intervals,80% line and infeasible cells/gaps. Lines are visual guides, not interpolated detection thresholds.',interpretation='Conditional simulation operating characteristics at actual support and specified generators. No continuous minimum detectable effect, general mechanism claim or bound on actual manuscript heterogeneity. Limited support, baseline assumptions, and original selected/exposed contexts remain. No detection in the prior manuscript test is not proof of equal strength.',preservation='Write only this new directory. Prior non-cache source, data, controls, failed attempts, qualified V2 and manuscript scores stay unchanged; no new manuscript data are opened or scored.'))
 seal('protocol_frozen',['PROTOCOL.json','PRESERVATION.json','run.py','plot.py']);print('POWER PROTOCOL FROZEN',flush=True)
def init():
 global GG,JOBS
 events=json.loads((R/'MASKED.json').read_text());GG={co:v2.Geometry([e for e in events if e['reading']==co]) for co in ['H','F']};JOBS=json.loads((R/'JOBS.json').read_text()) if (R/'JOBS.json').exists() else []
def probabilities(g,arch,b,target,delta):
 effect=np.full(5,b)
 if target is not None:effect[target]+=delta
 if arch=='uniform':prob=.20+effect[g.ec]*g.x
 elif arch=='unequal':prob=np.array([.10,.40,.20,.15,.45])[g.ec]+effect[g.ec]*g.x
 elif arch=='available':prob=np.where(g.x==1,((.20+effect)/g.fsh)[g.ec],(.20/g.fch)[g.ec])*g.av
 else:raise ValueError(arch)
 return prob,effect
def prepare():
 verify();assert not (R/'JOBS.json').exists();events=json.loads((V2/'MASKED.json').read_text());assert all('y' not in e and 'follower' not in e for e in events);save('MASKED.json',events);init();support={co:g.support() for co,g in GG.items()};assert support==json.loads((V2/'SUPPORT.json').read_text());jobs=[]
 for ri,co in enumerate(['H','F']):
  g=GG[co]
  for ai,arch in enumerate(ARCH):
   for bi,b in enumerate(COMMON):
    zeroid=len(jobs)
    for target,di,delta in [(None,0,0.)]+[(target,di+1,delta) for target in range(5) for di,delta in enumerate(DELTAS)]:
     prob,expected=probabilities(g,arch,b,target,delta);feasible=bool(np.all((prob>=0)&(prob<=1)));actual=np.bincount(g.ec,weights=g.coeff*prob,minlength=5);assert np.max(abs(actual-expected))<1e-12
     jobs.append(dict(job=len(jobs),reading=co,reading_index=ri,architecture=arch,architecture_index=ai,common_effect=b,common_index=bi,target=None if target is None else v2.CONTEXTS[target],target_index=5 if target is None else target,grid_index=di,difference=delta,N=10000 if target is None else 2000,zero_guard_job=zeroid,feasible=feasible,probability_range=[float(prob.min()),float(prob.max())],expected_context_effects=actual.tolist()))
 assert len(jobs)==M;save('JOBS.json',jobs);save('SUPPORT.json',support);save('FEASIBILITY.json',dict(family_slots=M,feasible_cells=sum(j['feasible'] for j in jobs),infeasible=[j for j in jobs if not j['feasible']],planned_trials=sum(j['N'] for j in jobs if j['feasible'])));seal('support_generators_jobs_frozen',['MASKED.json','SUPPORT.json','JOBS.json','FEASIBILITY.json']);print(json.dumps(json.loads((R/'FEASIBILITY.json').read_text()),indent=2),flush=True)
def seed_for(j,t):return [919260,j['reading_index'],j['architecture_index'],j['common_index'],j['target_index'],j['grid_index'],t]
def generate(g,j,t):
 prob,_=probabilities(g,j['architecture'],j['common_effect'],None if j['target'] is None else j['target_index'],j['difference']);assert j['feasible'];y=(np.random.default_rng(seed_for(j,t)).random(len(prob))<prob).astype(np.int8)
 if j['architecture']=='available':assert not y[~g.av].any()
 return y
def preflight():
 verify();init();checks=[]
 for j in JOBS:
  if not j['feasible']:continue
  g=GG[j['reading']];y=generate(g,j,0);rr=v2.test(g,y,probe=True);checks.append(dict(job=j['job'],trial=0,scalar_error=rr['scalar_error'],fixed_coordinate=True))
  if j['common_effect']==0 and j['target']=='C1' and j['difference']==.12:
   scene={'uniform':'heterogeneous_positive','unequal':'section_baseline_heterogeneous_positive','available':'available_heterogeneous_positive'}[j['architecture']];assert np.array_equal(y,g.generate(scene,seed_for(j,0)))
  if j['target'] is None and (j['architecture']=='uniform' or j['common_effect']==.08):
   scene='homogeneous_null' if j['architecture']=='uniform' and j['common_effect']==0 else 'homogeneous_positive' if j['architecture']=='uniform' else 'section_baseline_homogeneous' if j['architecture']=='unequal' else 'available_homogeneous';assert np.array_equal(y,g.generate(scene,seed_for(j,0)))
 save('ENGINEERING.json',dict(status='PASS',checks=checks,original_positive_generator_equivalence=True,extra_unique_power_coordinates=0));seal('engineering_verified',['ENGINEERING.json']);print('POWER ENGINEERING PASS',len(checks),flush=True)
def chunk(task):
 ji,start,stop=task;j=JOBS[ji];g=GG[j['reading']];rows=[]
 for t in range(start,stop):
  seed=seed_for(j,t);y=generate(g,j,t);r=v2.test(g,y);rows.append(dict(job=ji,trial=t,seed=seed,T=r['T'],p=r['p'],flag=r['flag'],uniform=r['informative_outcomes_uniform'],outcome_sha256=r['outcome_sha256']))
 return rows
def simulate():
 verify();init();D=R/'trials';D.mkdir(exist_ok=True);tasks=[]
 for j in JOBS:
  if not j['feasible']:continue
  for start in range(0,j['N'],500):
   dest=D/f"{j['job']:03d}-{start:05d}.jsonl";stop=min(start+500,j['N'])
   if dest.exists():
    rr=[json.loads(s) for s in dest.read_text().splitlines()];assert len(rr)==stop-start and all(r['job']==j['job'] and r['trial']==start+i for i,r in enumerate(rr));continue
   tasks.append((j['job'],start,stop))
 with ProcessPoolExecutor(max_workers=3,initializer=init) as pool:
  for task,rr in zip(tasks,pool.map(chunk,tasks,chunksize=1)):
   ji,start,stop=task;dest=D/f'{ji:03d}-{start:05d}.jsonl';tmp=dest.with_suffix('.tmp');tmp.write_text(''.join(json.dumps(r)+'\n' for r in rr));tmp.replace(dest)
   if start==0:print('Power job',ji,'committed',flush=True)
 save('SIMULATION-COMPLETE.json',dict(complete=True,planned_unique_trials=sum(j['N'] for j in JOBS if j['feasible'])));print('POWER SIMULATION COMPLETE',flush=True)
def audit():
 verify();init();assert (R/'SIMULATION-COMPLETE.json').exists();checks=[]
 for path in sorted((R/'trials').glob('*.jsonl')):
  for line in path.read_text().splitlines():
   r=json.loads(line);j=JOBS[r['job']];t=r['trial'];fixed=t in [0,j['N']//2,j['N']-1];guard_false_flag=j['target'] is None and r['flag'];boundary=abs(r['p']-.025)<1e-8
   if not (fixed or guard_false_flag or boundary):continue
   g=GG[j['reading']];y=generate(g,j,t);assert seed_for(j,t)==r['seed'];rr=v2.test(g,y,probe=True);assert rr['outcome_sha256']==r['outcome_sha256'] and rr['T']==r['T'] and rr['p']==r['p'];ts,_,_=v2.scalar(g,y);pp=float(chi2.sf(ts,3));assert abs(pp-r['p'])<1e-10 and (pp<=.025)==r['flag'];checks.append(dict(job=j['job'],trial=t,scalar_error=rr['scalar_error']))
 save('POSTRUN-AUDIT.json',dict(status='PASS',checks=checks,max_scalar_error=max([c['scalar_error'] for c in checks],default=0)));print('POWER AUDIT PASS',len(checks),flush=True)
def interval(k,n):
 err=.05/M;return [0 if k==0 else float(beta.ppf(err/2,k,n-k+1)),1 if k==n else float(beta.ppf(1-err/2,k+1,n-k))]
def summarize():
 verify();init();counts={};seen=set();hashes={}
 for path in (R/'trials').glob('*.jsonl'):
  hashes[str(path.relative_to(R))]=sha(path)
  for line in path.read_text().splitlines():
   r=json.loads(line);key=(r['job'],r['trial']);assert key not in seen;seen.add(key);c=counts.setdefault(r['job'],[0,0,0]);c[0]+=1;c[1]+=r['flag'];c[2]+=r['uniform']
 rows=[]
 for j in JOBS:
  if not j['feasible']:assert j['job'] not in counts;rows.append(j|dict(status='INFEASIBLE',n=0,flags=None,power=None,CI=None));continue
  n,k,unif=counts[j['job']];assert n==j['N'];lo,hi=interval(k,n)
  if j['target'] is None:status='GUARD PASS' if hi<=.05 and lo<=.025 else 'NOMINAL ALARM' if lo>.025 else 'INCONCLUSIVE GUARD'
  else:status='RELIABLY DETECTABLE' if lo>=.80 else 'BELOW 80% TARGET' if hi<.80 else 'INCONCLUSIVE'
  rows.append(j|dict(status=status,n=n,flags=k,power=k/n,CI=[lo,hi],uniform_trials=unif))
 for r in rows:
  if r['target'] is not None and r['feasible'] and rows[r['zero_guard_job']]['status']!='GUARD PASS':r['power_classification_before_guard']=r['status'];r['status']='CALIBRATION BLOCKED'
 assert len(seen)==json.loads((R/'FEASIBILITY.json').read_text())['planned_trials'];curves=[]
 for ri,co in enumerate(['H','F']):
  for arch in ARCH:
   for b in COMMON:
    for target in v2.CONTEXTS:
     rr=[r for r in rows if r['reading']==co and r['architecture']==arch and r['common_effect']==b and r['target']==target];cert=[r['difference'] for r in rr if r['status']=='RELIABLY DETECTABLE'];sustained=[r['difference'] for i,r in enumerate(rr) if r['status']=='RELIABLY DETECTABLE' and all(x['status']=='RELIABLY DETECTABLE' for x in rr[i:] if x['feasible'])];curves.append(dict(reading=co,architecture=arch,common_effect=b,target=target,first_certified_tested_difference=min(cert) if cert else None,first_sustained_certified_tested_difference=min(sustained) if sustained else None,certified_tested_differences=cert,inconclusive_tested_differences=[r['difference'] for r in rr if r['status']=='INCONCLUSIVE'],infeasible_tested_differences=[r['difference'] for r in rr if not r['feasible']],largest_feasible_tested_difference=max(r['difference'] for r in rr if r['feasible'])))
 robust=[]
 for b in COMMON:
  for target in v2.CONTEXTS:
   points=[]
   for delta in DELTAS:
    rr=[r for r in rows if r['common_effect']==b and r['target']==target and r['difference']==delta];assert len(rr)==6;points.append(dict(difference=delta,jointly_feasible=all(r['feasible'] for r in rr),each_reading_architecture_certified=all(r['status']=='RELIABLY DETECTABLE' for r in rr),per_cell_statuses={r['reading']+'-'+r['architecture']:r['status'] for r in rr}))
   cert=[p['difference'] for p in points if p['each_reading_architecture_certified']];sustained=[p['difference'] for i,p in enumerate(points) if p['each_reading_architecture_certified'] and all(x['each_reading_architecture_certified'] for x in points[i:] if x['jointly_feasible'])];robust.append(dict(common_effect=b,target=target,first_certified_tested_difference=min(cert) if cert else None,first_sustained_certified_tested_difference=min(sustained) if sustained else None,largest_jointly_feasible_tested_difference=max(p['difference'] for p in points if p['jointly_feasible']),points=points,note='Certification of marginal power>=80% separately in each reading/architecture, not joint detection probability.'))
 save('RESULTS.json',dict(family_slots=M,unique_trials=len(seen),rows=rows));save('CURVE-THRESHOLDS.json',curves);save('ROBUST-THRESHOLDS.json',robust);save('TRIAL-HASHES.json',hashes);assert json.loads((R/'POSTRUN-AUDIT.json').read_text())['status']=='PASS';seal('curve_results_frozen',['RESULTS.json','CURVE-THRESHOLDS.json','ROBUST-THRESHOLDS.json','TRIAL-HASHES.json','POSTRUN-AUDIT.json','SIMULATION-COMPLETE.json']);print(json.dumps(robust,indent=2),flush=True)
if __name__=='__main__':{'freeze':freeze,'prepare':prepare,'preflight':preflight,'simulate':simulate,'audit':audit,'summarize':summarize}[sys.argv[1]]()
