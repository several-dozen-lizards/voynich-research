import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,csv,hashlib,math,importlib.util
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.stats import beta,chi2
from scipy.optimize import minimize_scalar,brentq
import engine
R=Path(__file__).resolve().parent;P=R.parent;PREV=P/'bq2-replacement-v1';OLD=P/'sh-qok-context-map-v3';FOLLOW=P/'sh-qok-qualification-followup-v1';GG={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def seal(phase,names):
 with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=phase,utc=datetime.now(timezone.utc).isoformat(),hashes={n:sha(R/n) for n in names}))+'\n')
def verify():
 preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in preserved['hashes'].items())
 for s in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(s)['hashes'].items():assert sha(R/n)==h,('phase hash',n)
def freeze():
 assert not (R/'PROTOCOL.json').exists();preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(Path(p))==h for p,h in preserved['hashes'].items())
 save('PROTOCOL.json',dict(status='FROZEN BEFORE V2 SUPPORT AND FRESH QUALIFICATION; RETROSPECTIVE',utc=datetime.now(timezone.utc).isoformat(),authority='User requested diagnosis followed by separately frozen qualification addressing unequal baselines; score heterogeneity only if qualification passes.',diagnosis='DIAGNOSIS.json uses old R1 section-baseline controls only. R1 working variances underestimate true uncertainty by~16% C2/~11-12% C5, overestimate C1~15%. Oracle-variance chi-square flags122/5000H,108/5000F; old working-variance chi-square189/169 versus old relabel182/166. Thus changing reference alone does not solve variance bias. This diagnosis is exposed exploratory engineering, not qualification.',target='Same aggregate MH sh/ch->qok risk differences C1-C5, heterogeneity centered separately within scribe2 C1-C3 and scribe3 C4-C5. H/F separate. No contexts, folios, transcriptions, endings or pooling added.',design='Reuse R1 supported-folio geometry, dropping only zero-D folios outcome-blind. Keep contexts/folios fixed; never relabel outcomes/baselines across sections. No raw EVT or reserved zodiac. Score support before fresh controls.',variance=dict(coefficients='For each supported folio x ending stratum, raw MH context RD is sum_i a_i*y_i: a_sh=(nc/n)/Dc, a_ch=-(ns/n)/Dc. Unsupported stratum coefficients0. Point estimates remain unshrunk.',pooling='Pool uncertainty only within each original context x prefix. u_i=a_i^2, A=sumu, b_i=u_i/A, N_eff=A^2/sum(u_i^2)>1, r=sum(u_i*y_i)/A. Half-count m=(N_eff*r+.5)/(N_eff+1). Variance-product estimate min(.25,m*(1-m)/(1-1/N_eff)); sum A*product over sh/ch. The finite-weight correction targets the ordinary weighted sampling-variance bias; after regularization/capping this is a working estimator, not an exactly unbiased estimator or an exact Bayesian posterior for weighted data.',rationale='Under independent Bernoulli outcomes, the true squared-coefficient-weighted baseline gives a Jensen upper bound A*pbar*(1-pbar) on that prefix variance. Estimating pbar does not make the plug-in a guaranteed bound. Separate context/prefix pooling avoids R1 tiny-margin shrinkage bias across unequal baselines; qualification must test remaining approximation.',folio_protection='Also compute HC3-style folio variance: sum_p[(Np-Dp*RDc)/(1-Dp/Dc)]^2 / Dc^2 within each context. Use max(pooled_binomial_variance, HC3_folio_variance). This protects against a too-small event model estimate and preserves within-folio dependence at the score level. Max is a candidate safeguard, not a proof of finite-sample coverage.',zero='Pooled half-count product is strictly positive when A>0 and N_eff>1, so empirical HC3 zero never creates a zero denominator. No epsilon floor, observation edits or dropped failures.'),statistic='T=sum_c (RDc-mu_scribe)^2/vc, where mu_scribe is inverse-v weighted mean within each scribe and vc=max(pool,HC3). Fixed-design Gaussian working-model reference chi-square with df=(3-1)+(2-1)=3; p=sf(T,3). Approximate for binary/clustered data, never called exact. No inner permutations or bootstrap MC. A uniform informative outcome configuration is NOT ESTIMABLE rather than negative evidence.',support='Same positive-D folios as R1. Each context>=2 supported folios; leverage Dp/Dc<1; every context-prefix N_eff>1; availability-control target probabilities .20/.28/.32 feasible. Failure blocks reading without adding material.',controls=dict(scenarios=engine.SCENES,null_count=8,positive_count=3,nulls='Original five R1 nulls retained unchanged, plus common+.08 with random folio baseline(.10/.40), common+.08 with random folio×ending baseline(.08/.42), and common population+.08 with independent folio effects .08±.04 at base.20. The last tests within-folio dependence/effect variation under equal context expectations.',positives='Retain abstract+.12 C1 only and availability-preserving+.12 C1 only; add+.12 C1 only with section baselines .10,.40,.20,.15,.45. Power descriptive, no80% gate, retaining B-Q2 rule.',N='Exactly10000 fresh trials per required null per supported reading and2000 per positive:172000 total if both support. No old/new pooling, sample extension, optional stopping, seed replacement, effect enlargement or retuning.',seed='[918260,reading_index H0/F1,scenario_index in engine.SCENES,trial]. No resampling-bank seed exists.',intervals='22 simultaneous two-sided exact Clopper-Pearson intervals; per-interval error.05/22;16 null rates+6 descriptive power rates. Keep full denominators and uniform/invalid cases.',gates='Raw p<=.025 is calibration flag. Every required-null upper bound<=.05, no lower bound>.025 nominal-size alarm, no numeric failure. Upper/lower spanning5% INCONCLUSIVE; lower>5% EVIDENCE ABOVE TOLERANCE. Nominal alarm blocks even if below5% practical tolerance. No alarm is not proof of exact nominal size. All positives and their power intervals retained without altering gates.'),scoring='Only after qualification, trial receipts and independent audit hashes frozen: attach actual original EVENTS.csv y to the exact masked supported events, and score each qualified reading. Failed/inconclusive readings BLOCKED with no new manuscript T,p,tau or I2.',multiplicity='Fixed conservative Holm2 factor per reading [new BQ2-V2, inactive historical BQ1 internalp1]. Prior B-Q1 scores/statuses/families remain unchanged. H/F not pooled or independent replicates. No global research-history correction claim.',decision='Qualified, nonuniform reading: DETECTED HETEROGENEITY if min(1,2*p)<=.05, otherwise NO DETECTION. Both readings must detect for both-reading headline. No detection plus weak power or broad tau CI leaves strength variation unresolved; never interpret as proof of constant strength.',diagnostics='Only qualified readings: unchanged raw context MH effects and carried-forward original descriptive CIs; pooled/HC3/used context variances and effective sample sizes; descriptive within-scribe common-tau REML with separate scribe means, Q-profile95 df3 and I2. No new unqualified scribe2-only sensitivity tests.',engineering='Coefficient reconstruction and direct raw MH check; independent scalar variance/T calculation; Gaussian projection symmetry/idempotence/rank3; all-zero/all-one/perfect-prefix/checkerboard fixtures; shift invariance; variance-enlargement cannot increase minimized quadratic; replay six old undefined synthetic assignments with finite V2 moments. Fixed first3 trial coordinates per reading/scenario verify production vs scalar and remain in fixed qualification run, not extra draws.',postrun_audit='Regenerate every fresh null false flag and trial0 per scenario, verify outcome hash, T and p, independent scalar arithmetic; numerical boundary disagreement blocks qualification. Verify prior hashes and phase hashes before/after. Preserve all trials and failures.',limits='Finite authored-control qualification at actual geometry, not universal asymptotic correctness or a decoding claim. Old context selection C1/C4 and all material exposure remain. Original B-Q2 and R1 remain unqualified and untouched; no real manuscript scoring used to select V2.',sources=['https://www.statsmodels.org/v0.13.5/generated/statsmodels.regression.linear_model.RegressionResults.HC3_se.html','https://stat.ethz.ch/CRAN/doc/manuals/r-patched/packages/stats/refman/stats.html','https://statistics.stanford.edu/technical-reports/exact-and-asymptotically-robust-permutation-tests','https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm']))
 seal('protocol_frozen',['PROTOCOL.json','PRESERVATION.json','DIAGNOSIS.json','DIAGNOSTIC-PLAN.json','diagnose.py','engine.py','run.py']);print('V2 PROTOCOL FROZEN',flush=True)
def init():
 global GG
 events=json.loads((R/'MASKED.json').read_text());GG={co:engine.Geometry([e for e in events if e['reading']==co]) for co in ['H','F']}
def prepare():
 verify();assert not (R/'SUPPORT.json').exists();events=json.loads((PREV/'MASKED.json').read_text());assert all('y' not in e and 'follower' not in e for e in events);save('MASKED.json',events);init();support={co:g.support() for co,g in GG.items()};save('SUPPORT.json',support);seal('outcome_blind_support_frozen',['MASKED.json','SUPPORT.json']);print(json.dumps({co:{k:s[k] for k in ['supported_folios','context_pages','context_prefix_effective_N_ch_sh','gate']} for co,s in support.items()},indent=2),flush=True)
def preflight():
 verify();init();checks=[]
 # GLS projection under the Gaussian working model has residual rank3.
 v=np.array([.1,.2,.3,.25,.4]);X=np.array([[1,0],[1,0],[1,0],[0,1],[0,1]],float);Z=X/np.sqrt(v[:,None]);Proj=np.eye(5)-Z@np.linalg.inv(Z.T@Z)@Z.T;assert np.max(abs(Proj-Proj.T))<1e-12 and np.max(abs(Proj@Proj-Proj))<1e-12 and abs(np.trace(Proj)-3)<1e-12
 z=np.array([.1,-.7,.3,.5,-.1]);assert abs(engine.statistic(np.sqrt(v)*z,v)-float(z@Proj@z))<1e-12;assert abs(chi2.sf(chi2.ppf(.975,3),3)-.025)<1e-13
 for ri,co in enumerate(['H','F']):
  g=GG[co]
  for name,y in [('all_zero',np.zeros(len(g.events),np.int8)),('all_one',np.ones(len(g.events),np.int8)),('perfect_prefix',g.x.astype(np.int8)),('checkerboard',(np.arange(len(g.events))%2).astype(np.int8))]:
   rr=engine.test(g,y,probe=True);assert min(rr['context_variances'])>0;ef=np.array(rr['context_effects']);vv=np.array(rr['context_variances']);shift=ef+np.array([.07,.07,.07,-.03,-.03]);assert abs(engine.statistic(ef,vv)-engine.statistic(shift,vv))<1e-10;assert engine.statistic(ef,2*vv)<=rr['T']+1e-10;checks.append(dict(reading=co,fixture=name,scalar_error=rr['scalar_error'],minimum_variance=min(rr['context_variances'])))
  for si,scene in enumerate(engine.SCENES):
   for t in range(3):
    y=g.generate(scene,[918260,ri,si,t]);rr=engine.test(g,y,probe=True);checks.append(dict(reading=co,scenario=scene,trial=t,scalar_error=rr['scalar_error'],part_of_fixed_run=True))
 # Recreate old failed synthetic assignments using their saved fixed seeds and folio rows.
 cases=json.loads((FOLLOW/'run-2026-10-24/BQ2-UNDEFINED-CONTEXTS.json').read_text());allmasked=json.loads((PREV/'MASKED.json').read_text());replayed=[]
 for case in cases:
  co=case['reading'];ri=['H','F'].index(co);si=['homogeneous_null','homogeneous_positive'].index(case['scenario']);t=case['trial'];full=[e for e in allmasked if e['reading']==co];rng=np.random.default_rng(5100000+ri*100000+si*1000+t);yy=(rng.random(len(full))<np.array([.2+(.08*e['x'] if si else 0) for e in full])).astype(np.int8);lookup={(e['line'],e['position']):int(y) for e,y in zip(full,yy)};pages=sorted({e['folio'] for e in full});lab=np.array([engine.CONTEXTS.index(next(e['context'] for e in full if e['folio']==pg)) for pg in pages]);hands=np.array([2 if j<3 else 3 for j in lab]);bi=case['bank'];seed=6100000+ri if bi==0 else [913261,ri,si,t,bi];rng=np.random.default_rng(seed);mat=np.tile(lab,(10000,1))
  for hand in sorted(set(hands)):
   ix=np.where(hands==hand)[0]
   for row in mat:row[ix]=rng.permutation(lab[ix])
  labels=lab if case['shuffle_index']==0 else mat[case['shuffle_index']-1];g=GG[co];labels=labels[[pages.index(pg) for pg in g.pages]];y=np.array([lookup[e['line'],e['position']] for e in g.events],dtype=np.int8);effects,vars,pooled,hc3,pp=g.moments(y,labels);value=engine.statistic(effects,vars);assert math.isfinite(value) and np.all(vars>0);replayed.append(dict(reading=co,trial=t,bank=bi,minimum_variance=float(vars.min()),T=value))
 save('ENGINEERING.json',dict(status='PASS',projection_rank3=True,checks=checks,old_zero_assignments_replayed=replayed));seal('engineering_verified',['ENGINEERING.json']);print('V2 ENGINEERING PASS',len(checks),'checks;6 old zeros',flush=True)
def chunk(task):
 ri,si,start,stop=task;co=['H','F'][ri];scene=engine.SCENES[si];g=GG[co];rows=[]
 for t in range(start,stop):
  seed=[918260,ri,si,t];y=g.generate(scene,seed);rr=engine.test(g,y);rr.pop('pooled_probability_details');rows.append(dict(reading=co,scenario=scene,scenario_index=si,trial=t,seed=seed,**rr))
 return rows
def qualify():
 verify();support=json.loads((R/'SUPPORT.json').read_text());D=R/'trials';D.mkdir(exist_ok=True);tasks=[]
 for ri,co in enumerate(['H','F']):
  if not support[co]['gate']:continue
  for si,scene in enumerate(engine.SCENES):
   n=10000 if si<8 else 2000
   for start in range(0,n,250):
    dest=D/f'{ri}-{si}-{start:05d}.jsonl'
    if dest.exists():
     rr=[json.loads(s) for s in dest.read_text().splitlines()];assert len(rr)==250 and all(r['reading']==co and r['scenario_index']==si and r['trial']==start+i for i,r in enumerate(rr));continue
    tasks.append((ri,si,start,start+250))
 with ProcessPoolExecutor(max_workers=3,initializer=init) as pool:
  for task,rr in zip(tasks,pool.map(chunk,tasks,chunksize=1)):
   ri,si,start,stop=task;dest=D/f'{ri}-{si}-{start:05d}.jsonl';tmp=dest.with_suffix('.tmp');tmp.write_text(''.join(json.dumps(v)+'\n' for v in rr));tmp.replace(dest);print('V2 controls',ri,si,stop,'committed',flush=True)
 save('CONTROLS-COMPLETE.json',dict(unique_trials=sum(86000 for co in ['H','F'] if support[co]['gate']),no_inner_MC=True));print('V2 CONTROLS COMPLETE',flush=True)
def audit():
 verify();init();assert (R/'CONTROLS-COMPLETE.json').exists();checks=[]
 for path in sorted((R/'trials').glob('*.jsonl')):
  for line in path.read_text().splitlines():
   r=json.loads(line)
   if r['trial']!=0 and (r['scenario_index']>=8 or not r['flag']):continue
   g=GG[r['reading']];y=g.generate(r['scenario'],r['seed']);rr=engine.test(g,y,probe=True)
   for key in ['T','p','flag','outcome_sha256','context_variances','context_effects']:assert rr[key]==r[key]
   ts,_,_=engine.scalar(g,y);independent_p=float(chi2.sf(ts,3));assert abs(independent_p-rr['p'])<1e-10
   if abs(independent_p-.025)<1e-10:raise RuntimeError('Unresolved numeric decision boundary; qualification blocked')
   assert (independent_p<=.025)==r['flag'];checks.append(dict(reading=r['reading'],scenario=r['scenario'],trial=r['trial'],scalar_error=rr['scalar_error']))
 save('POSTRUN-AUDIT.json',dict(status='PASS',checks=checks,max_error=max([x['scalar_error'] for x in checks],default=0)));print('V2 AUDIT PASS',len(checks),flush=True)
def interval(k,n,error=.05/22):return [0 if not k else float(beta.ppf(error/2,k,n-k+1)),1 if k==n else float(beta.ppf(1-error/2,k+1,n-k))]
def summarize():
 verify();support=json.loads((R/'SUPPORT.json').read_text());counts={};seen=set();hashes={}
 for path in (R/'trials').glob('*.jsonl'):
  hashes[str(path.relative_to(R))]=sha(path)
  for line in path.read_text().splitlines():
   r=json.loads(line);key=(r['reading'],r['scenario_index'],r['trial']);assert key not in seen;seen.add(key);c=counts.setdefault((r['reading'],r['scenario_index']),[0,0,0]);c[0]+=1;c[1]+=r['flag'];c[2]+=r['informative_outcomes_uniform']
 result={}
 for co in ['H','F']:
  if not support[co]['gate']:result[co]=dict(status='NOT ESTIMABLE',controls=[]);continue
  rr=[]
  for si,scene in enumerate(engine.SCENES):
   n,k,uniform=counts[co,si];assert n==(10000 if si<8 else 2000);lo,hi=interval(k,n);status='DESCRIPTIVE POWER' if si>=8 else 'CERTIFIED BELOW TOLERANCE' if hi<=.05 else 'EVIDENCE ABOVE TOLERANCE' if lo>.05 else 'INCONCLUSIVE';alarm=si<8 and lo>.025;rr.append(dict(scenario=scene,n=n,flags=k,rate=k/n,simultaneous_exact_CI95=[lo,hi],status=status,nominal_alarm=alarm,uniform=uniform))
  good=all(r['status']=='CERTIFIED BELOW TOLERANCE' and not r['nominal_alarm'] for r in rr[:8]);result[co]=dict(status='QUALIFIED CALIBRATION' if good else 'NOT QUALIFIED',inconclusive=any(r['status']=='INCONCLUSIVE' for r in rr[:8]),controls=rr)
 assert len(seen)==json.loads((R/'CONTROLS-COMPLETE.json').read_text())['unique_trials'];assert json.loads((R/'POSTRUN-AUDIT.json').read_text())['status']=='PASS';save('QUALIFICATION.json',dict(unique_trials=len(seen),results=result));save('TRIAL-HASHES.json',hashes);seal('qualification_and_audit_frozen',['QUALIFICATION.json','TRIAL-HASHES.json','POSTRUN-AUDIT.json','CONTROLS-COMPLETE.json']);print(json.dumps({co:r['status'] for co,r in result.items()}),flush=True)
def reml(effects,variances):
 y=np.array(effects);v=np.array(variances)
 def Q(t):return engine.statistic(y,v+t)
 def obj(t):return float(np.log(v+t).sum()+sum(np.log((1/(v[ix]+t)).sum()) for ix in [[0,1,2],[3,4]])+Q(t))
 opt=minimize_scalar(obj,bounds=(0,1),method='bounded',options={'xatol':1e-13});tau=float(opt.x) if opt.fun<obj(0) else 0.
 def root(target):
  if Q(0)<=target:return 0.
  hi=1.
  while Q(hi)>target:hi*=2
  return float(brentq(lambda t:Q(t)-target,0,hi))
 q=Q(0);return dict(tau2=tau,Q_profile95=[root(chi2.ppf(.975,3)),root(chi2.ppf(.025,3))],I2=max(0,(q-3)/q) if q else 0,df=3,working_model_descriptive=True)
def outcomes():
 verify();assert not (R/'RESULTS.json').exists();init();qual=json.loads((R/'QUALIFICATION.json').read_text());old=json.loads((OLD/'PART-B-ESTIMATES.json').read_text());ledger=None;result={}
 for co in ['H','F']:
  if qual['results'][co]['status']!='QUALIFIED CALIBRATION':result[co]=dict(status='BLOCKED: QUALIFICATION',manuscript_scored=False,p=None,holm_p=None);continue
  if ledger is None:
   with (OLD/'EVENTS.csv').open(encoding='utf-8') as f:ledger={(r['reading'],r['line'],int(r['position'])):r for r in csv.DictReader(f) if not r['exclusion_reason']}
  g=GG[co];yy=[]
  for e in g.events:
   r=ledger[co,e['line'],e['position']];assert r['origin']==e['origin'] and r['family']==e['family'];y=int(r['outcome']);assert y==int(r['follower'].startswith('qok'));yy.append(y)
  rr=engine.test(g,np.array(yy,dtype=np.int8),probe=True);assert all(abs(100*rr['context_effects'][j]-old[c+'-'+co]['aggregate']['effect_points'])<1e-10 for j,c in enumerate(engine.CONTEXTS));adj=min(1,2*rr['p']);status='NOT ESTIMABLE: UNIFORM OUTCOMES' if rr['informative_outcomes_uniform'] else 'DETECTED HETEROGENEITY' if adj<=.05 else 'NO DETECTION';result[co]=dict(status=status,manuscript_scored=True,p=rr['p'],holm_p=adj,test=rr,random_effects_descriptive=reml(rr['context_effects'],rr['context_variances']),inactive_BQ1_internal_p=1)
 save('RESULTS.json',dict(retrospective=True,readings=result,prior_BQ2_and_R1='UNQUALIFIED; UNCHANGED',both_readings_detected=all(r['status']=='DETECTED HETEROGENEITY' for r in result.values())));seal('conditional_manuscript_scoring_complete',['RESULTS.json'])
 lines=['RETROSPECTIVE — all material exposed or uncertified (v100/v102).','','V2 fixed-baseline replacement. All prior attempts and their statuses remain unchanged. Qualification was frozen and completed before any V2 manuscript statistic; failed/inconclusive readings remain unscored.','','The R1 diagnosis identified variance bias: the old tiny-margin working variance was~16% too small in C2 and~11–12% too small in C5 under the failed unequal-baseline null. Its fixed chi-square flags were189H/169F per5000, versus122H/108F with known generating variances. Simply switching reference was insufficient. DIAGNOSIS.json retains all context ratios and observed/reference quantiles. This was exploratory diagnosis of old controls, not fresh qualification.','','V2 keeps raw MH effects. It estimates baseline uncertainty within each fixed context and prefix, using squared event-coefficient weights and effective sample size. It takes the larger of that pooled binomial variance and leverage-adjusted folio HC3 variance. Context membership is fixed; no baseline relabeling occurs. Chi-square3 is an approximate Gaussian working-model reference, not an exact finite-sample binary/clustered theorem. Fresh real-support qualification tests the approximation.','','| Reading | Qualification | Manuscript status | Adjusted p |','|---|---|---|---|']
 for co in ['H','F']:lines.append(f"| {co} | {qual['results'][co]['status']} | {result[co]['status']} | {result[co]['holm_p']} |")
 lines+=['','| Reading | Scenario | Flags/N | Simultaneous exact interval | Decision | Nominal alarm |','|---|---|---|---|---|---|']
 for co in ['H','F']:
  for c in qual['results'][co]['controls']:lo,hi=c['simultaneous_exact_CI95'];lines.append(f"| {co} | {c['scenario']} | {c['flags']}/{c['n']} | [{lo:.3%}, {hi:.3%}] | {c['status']} | {c['nominal_alarm']} |")
 lines+=['','Fixed qualification:8 nulls×10,000 and3 positives×2,000 per supported reading,172,000 total if both supported. Twenty-two simultaneous exact Clopper–Pearson intervals, full denominators retained. Required-null U≤5% and no L>2.5% nominal alarm; failures and intervals spanning5% remain blocked/inconclusive. No alarm is not proof of exact nominal size. Power is descriptive under the original B-Q2 rule. No extension, retuning, seed replacement or old/new pooling occurred.']
 for co in ['H','F']:
  r=result[co]
  if not r['manuscript_scored']:continue
  rr=r['test'];lines+=['',f"{co}: T={rr['T']:.6g}, df3, rawp={rr['p']:.6g}, conservative Holm2p={r['holm_p']:.6g}, {r['status']}.",f"{co} working-model descriptive random effects, separate scribe means: {r['random_effects_descriptive']}.",f"{co} context raw effects (points): {[100*x for x in rr['context_effects']]}; pooled variances={rr['pooled_variances']}; HC3={rr['HC3_variances']}; used={rr['context_variances']}."]
 lines+=['','Holm2 per reading retains a conservative inactive historical B-Q1 slotp1; historical B-Q1 tests and families remain unchanged. H/F are alternate readings and were never pooled. Uniform outcome configurations are non-estimable, not negative evidence. There is no inner permutation/Monte Carlo uncertainty in V2 p-values.','','NO DETECTION does not establish a uniform-strength rule. Read power and τ² intervals: weak sensitivity or broad intervals leave heterogeneity unresolved. C1/C4 were selected for large earlier effects, and all material is exposed. No new scribe2-only sensitivity tests were transported into qualified status.','','The pooled estimate uses squared-coefficient-weighted rates; the half-count/effective-N correction is a regularized working estimate, not an exact Bayesian posterior for weighted observations. The Jensen statement concerns the true baseline, not guaranteed coverage of the plug-in. HC3 protection and a maximum of variances are safeguards, not a universal theorem. See [statsmodels HC3 documentation](https://www.statsmodels.org/v0.13.5/generated/statsmodels.regression.linear_model.RegressionResults.HC3_se.html), [R weighted covariance correction](https://stat.ethz.ch/CRAN/doc/manuals/r-patched/packages/stats/refman/stats.html), and [primary permutation research](https://statistics.stanford.edu/technical-reports/exact-and-asymptotically-robust-permutation-tests).','','Controls retain the five R1 nulls including physically availability-preserving equal aggregate effects. Added nulls vary folio/stratum baselines and include correlated folio-level effect fluctuations with equal context expectations. Positives include unequal-baseline heterogeneity. These authored controls cover specific relationships at the actual support; arbitrary text dependence or nuisance structures are not proven calibrated. No semantics, sounds, glyph merges, causal explanation or prospective confirmation follows.','','Prior non-cache files and phase hashes were checked before and after. Original manuscript raw context effects replayed where scoring was permitted. ENGINEERING.json and POSTRUN-AUDIT.json retain independent scalar checks, boundary fixtures and old zero-case replays. No raw EVT or reserved zodiac material was opened.']
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');verify();assert all(sha(R/n)==h for n,h in json.loads((R/'TRIAL-HASHES.json').read_text()).items());save('VERIFICATION.json',dict(status='PASS',prior_files_preserved=len(json.loads((R/'PRESERVATION.json').read_text())['hashes']),unique_qualification_trials=qual['unique_trials'],qualification_frozen_before_scoring=True,manuscript_readings_scored=[co for co,r in result.items() if r['manuscript_scored']],prior_BQ2_and_R1_unqualified_unchanged=True,artifact_hashes={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='VERIFICATION.json'}));print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':{'freeze':freeze,'prepare':prepare,'preflight':preflight,'qualify':qualify,'audit':audit,'summarize':summarize,'outcomes':outcomes}[sys.argv[1]]()
