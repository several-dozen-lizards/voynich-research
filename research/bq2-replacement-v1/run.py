import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,csv,math,hashlib,itertools,collections
from datetime import datetime,timezone
from types import SimpleNamespace
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.stats import beta,chi2
from scipy.optimize import minimize_scalar,brentq
import engine as replacement
R=Path(__file__).resolve().parent;P=R.parent;OLD=P/'sh-qok-context-map-v3';FOLLOW=P/'sh-qok-qualification-followup-v1';READJ=P/'sh-qok-retrospective-readjudication-v1';CA=P/'currier-a-available-only-v1'
# Load the existing engine under a distinct module name to avoid the local engine.py name.
import importlib.util
sp=importlib.util.spec_from_file_location('original_exact_engine',P/'sh-qok-single-target-attempt-c/engine.py');original=importlib.util.module_from_spec(sp);sp.loader.exec_module(original)
GG={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def seal(phase,names):
 with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=phase,utc=datetime.now(timezone.utc).isoformat(),hashes={n:sha(R/n) for n in names}))+'\n')
def verify():
 preserved=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(p)==h for p,h in preserved['hashes'].items())
 for line in (R/'PHASES.jsonl').read_text().splitlines():
  for n,h in json.loads(line)['hashes'].items():assert sha(R/n)==h,('changed frozen file',n)
def freeze():
 assert not (R/'PROTOCOL.json').exists()
 hashes={str(p):sha(p) for root in [OLD,FOLLOW,READJ,CA] for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts};save('PRESERVATION.json',dict(excluded='__pycache__ only',hashes=hashes))
 save('PROTOCOL.json',dict(status='FROZEN BEFORE REPLACEMENT SUPPORT/QUALIFICATION; RETROSPECTIVE',utc=datetime.now(timezone.utc).isoformat(),authority='User requested freeze and qualify B-Q2 replacement at real support, score heterogeneity only if qualified, retain inconclusive results',exposure='Prior manuscript effects, old control failures and zero-variance cases known. No prospective or independent confirmation claim.',target='Same aggregate sh/ch->qok MH risk differences, contexts C1-C5. H/F separate. Heterogeneity only within scribe2 C1-C3 and within scribe3 C4-C5; combine those two dispersion statistics. Same physical folio permutation unit.',data='Original masked v3.1 events; no new folios, raw EVT, reserved zodiac, glyph handling, context additions or section pooling. Folios with zero MH assignment-support D are excluded from permutation pool before outcomes because they contribute no MH information. Remaining folios retain all their eligible events. All informative exact folio x ending strata remain unchanged.',support='Each context >=2 folios of positive D. Every permuted context thus has positive total D. Record pages, D, concentration and availability by context. Availability-preserving controls must be feasible at frozen target rates .20/.28 or .20/.32; infeasibility blocks qualification without lowering targets.',method=dict(raw_effect='For each folio x ending stratum: ns,nc,ys,yc, w=ns*nc/(ns+nc); Ng=w*(ys/ns-yc/nc); Dg=w. Raw effects unshrunk. Only discordant strata contribute.',working_variance='Jeffreys-smoothed probabilities ps=(ys+.5)/(ns+1), pc=(yc+.5)/(nc+1). Vg=(nc/(ns+nc))^2*ns*ps*(1-ps)+(ns/(ns+nc))^2*nc*pc*(1-pc). Sum Ng,Dg,Vg by folio. Vg>0 whenever ns,nc>0 even all-zero/all-one counts. This is a binomial working variance for studentization, not a posterior confidence interval or measured physiology.',statistic='For each reassignment: context RDc=sumNp/sumDp; working sampling variance vc=sumVp/(sumDp)^2; Wc=1/vc. Center each scribe separately at its W-weighted context mean. T=sum over scribes and contexts Wc*(RDc-mu_scribe)^2. No division by empirical between-folio residual variance, epsilon floor, failed-permutation deletion, clipping of observations or outcome edits.',permutation='Exactly10000 fresh independent whole-folio reassignments within each scribe per trial and per manuscript reading, with original supported-folio context counts fixed. NumPy Generator.permuted(...,axis=1) independently shuffles each row. Include observed assignment as row0. All folio N,D,V quantities travel together; recompute context working variances and centers every shuffle.',tail='p=(1+#Tperm>=Tobs-tol)/(10001). tol=128*float64_eps*max(1,maxT), numerical tie handling only, frozen. No negative-score truncation is needed because T is a sum of weighted squared deviations. All-identical score distributions have computational p1 and degenerate=True; not negative evidence.',limits='Studentization does not make weak equal-effect nulls finite-sample permutation-exact when folio distributions differ. Real-support synthetic qualification is necessary and limited to its authored generators; this implementation is not claimed to inherit a theorem automatically.'),controls=dict(null_scenarios=replacement.SCENES[:5],null_details=['homogeneous_null: p=.20, delta0','homogeneous_positive: p=.20+.08sh in every context','scribe_baseline_homogeneous: base .12 for scribe2, .40 for scribe3; delta.08 everywhere','section_baseline_homogeneous: bases C1..C5=.10,.40,.20,.15,.45; delta.08 everywhere, equal effects with different sampling variances','available_homogeneous: blocked outcomes0; among available followers pch=.20/fch,c and psh=.28/fsh,c. f is the masked MH-weighted available fraction by prefix/context. Analytic context aggregate risk differences exactly.08; may vary within context/folio. Infeasible targets block.'],positive_scenarios=replacement.SCENES[5:],positive_details=['heterogeneous_positive: base.20; +.12 aftersh only C1, zero elsewhere','available_heterogeneous_positive: blocked0; availablepch=.20/fch,c; availablesh probability [.32,.20,.20,.20,.20]/fsh,c, making aggregate effects+.12 C1/0 elsewhere'],N='Exactly5000 fresh trials per null scenario per supported reading and1000 per positive per reading; if both support54000 total. Every trial gets a fresh independent10000-shuffle bank. No reused banks, sample extension, optional stopping, seed replacement, enlarged effects or retuning.',seeds='Outcome coordinate [917260,reading_index(H0,F1),scenario_index0..6,trial,0]; permutation coordinate same but last1. Manuscript bank [917261,reading_index]. Engineering deterministic fixtures and old failed synthetic cases only, no new random qualification coordinates.',intervals='14 simultaneous exact two-sided Clopper-Pearson intervals with error.05/14, covering10 null and4 descriptive-power proportions. Keep full denominators, degeneracy and numeric failures. Any numeric undefined blocks the candidate; never discard failed permutations/trials.',gates='Each null U<=.05 CERTIFIED BELOW TOLERANCE, L>.05 EVIDENCE ABOVE TOLERANCE, else INCONCLUSIVE. Separately L>.025 is NOMINAL SIZE EXCESS and blocks qualification for any required equal-effect null. Reading qualifies only if every null certified, no nominal alarm, no undefined numeric cases. No detected alarm is not proof of exact nominal calibration.',power='Report power and simultaneous intervals descriptively for both+.12 controls, no80% gate, retaining original B-Q2 rule. Report both point-p flags and conservative inner-MC-certified flags. Low power prevents interpreting no detection as absence of heterogeneity.'),qualification_flag='Point Monte Carlo p<=.025, conservative calibration target for the guarded manuscript rejection rule. Independent of old control series; old and new counts never pooled.',score_gate='Attach actual manuscript y only after qualification and audit hashes frozen, and only for each qualified reading. Failed/inconclusive readings: BLOCKED, no new manuscript statistic, REML or p. Prior B-Q2 remains unqualified regardless.',manuscript_decision='Conservative Holm2 per reading [newBQ2-R1, inactive historicalBQ1 internal p1], leaving prior B-Q1 tests/statuses untouched. No global research-history correction claimed. For finite-inner-MC uncertainty, exact binomial tail intervals at simultaneous95% across H/F (per-reading error.025), transformed through add-one and factor2. DETECTED only if adjusted pointp<=.05 and interval upper<=.05; NO DETECTION only if interval lower>.05. Otherwise INCONCLUSIVE INNER MONTE CARLO, never extend bank. Degenerate distribution NOT ESTIMABLE. Both readings must DETECT for both-reading headline.',context_and_tau='Only for qualified readings, report unchanged raw context MH effects, original descriptive percentile CIs as carry-forward, new working variances, within-scribe REML common tau2 with separate scribe means and Q-profile95 interval(df3), and descriptive I2=max(0,(T-df)/T). Broad tau intervals mean unresolved. No new inferential scribe2-only sensitivities: those lack separate support qualification and remain prior unqualified diagnostics.',verification='Exhaustive finite small permutation orbit and rank super-uniformity, vectorized vs independent scalar scoring, all-zero/all-one/binary-perfect fixtures, direct MH effect replay, replay all six prior zero-variance synthetic assignments with finite new scores. Every fresh null false flag and trial0 per scenario: regenerate outcome and bank, verify hashes/counts, scalar-check observed/first32/extreme/near-observed assignments. Verify original prior-file hashes before and after.',interpretation='Even qualified inference remains retrospective and affected by selection of C1/C4 for large prior effects. No detection, especially with weak positive-control power or broad tau bounds, does not establish a uniform rule. Detection concerns strength across sections within these scribes, not why, meaning or mechanism.',preservation='Write only this new directory. All prior attempts, failures, controls, statuses and unqualified old B-Q2 remain byte-identical except ignored Python caches.',sources=['https://statistics.stanford.edu/technical-reports/exact-and-asymptotically-robust-permutation-tests','https://docs.astropy.org/en/stable/api/astropy.stats.binom_conf_interval.html','https://numpy.org/doc/2.0/reference/random/generated/numpy.random.Generator.permuted.html','https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm']))
 seal('protocol_frozen',['PROTOCOL.json','PRESERVATION.json','run.py','engine.py']);print('PROTOCOL FROZEN',flush=True)
def init():
 global GG
 events=json.loads((R/'MASKED.json').read_text());GG={co:replacement.Geometry([e for e in events if e['reading']==co]) for co in ['H','F']}
def prepare():
 verify();assert not (R/'SUPPORT.json').exists();events=json.loads((OLD/'MASKED-v3.1.json').read_text());subset=[e for e in events if e['context'] in replacement.CONTEXTS];assert all('y' not in e and 'follower' not in e for e in subset);save('MASKED.json',subset);init();support={co:g.support() for co,g in GG.items()};save('SUPPORT.json',support);seal('support_frozen',['MASKED.json','SUPPORT.json']);print(json.dumps(support,indent=2),flush=True)
def preflight():
 verify();init();labels=np.array([0,0,1,1,2,2,3,3,4,4]);D=np.array([1.,2.,3.,1.,2.,4.,2.,1.,3.,2.]);N=np.array([.1,-.2,.3,.15,.1,-.12,.04,.4,-.3,.2]);V=np.array([.1,.2,.15,.12,.2,.3,.13,.14,.3,.2]);toy=SimpleNamespace(D=D)
 left=sorted(set(itertools.permutations(labels[:6])));right=sorted(set(itertools.permutations(labels[6:])));mat=np.array([l+r for l in left for r in right]);scores,_,_=replacement.statistic(toy,N,V,mat);scalar=np.array([replacement.scalar(toy,N,V,row) for row in mat]);assert np.max(np.abs(scores-scalar))<1e-11;tol=128*np.finfo(float).eps*max(1,float(scores.max()));ps=np.array([np.mean(scores>=v-tol) for v in scores]);assert np.mean(ps<=.025)<=.025
 zeros=replacement.statistic(toy,np.zeros(10),V,mat)[0];assert not zeros.any();fixtures=[]
 for ri,co in enumerate(['H','F']):
  g=GG[co];bank=replacement.labels_bank(g,[917262,ri]);assert all(np.array_equal(np.sort(row[g.hands==h]),np.sort(g.labels[g.hands==h])) for row in bank for h in [2,3])
  for name,y in [('all_zero',np.zeros(len(g.events),dtype=np.int8)),('all_one',np.ones(len(g.events),dtype=np.int8)),('perfect_prefix',g.x.astype(np.int8)),('checkerboard',(np.arange(len(g.events))%2).astype(np.int8))]:
   nn,vv=g.terms(y);qq,_,_=replacement.statistic(g,nn,vv,bank);assert np.isfinite(qq).all() and np.all(vv>0)
   if name in ['all_zero','all_one','perfect_prefix']:assert qq.max()-qq.min()<=128*np.finfo(float).eps*max(1,float(qq.max()))
   ev=[e|dict(y=int(v)) for e,v in zip(g.events,y)];manual=original.page_effects(ev)
   assert max(abs(nn[g.pi[pg]]-terms[0])+abs(g.D[g.pi[pg]]-terms[1]) for pg,terms in manual.items())<1e-10;fixtures.append(dict(reading=co,fixture=name,minimum_working_variance=float(vv.min()),finite_everywhere=True))
 # Replay the already-saved failed synthetic assignments; no manuscript outcomes are consulted.
 sys.path.insert(0,str(OLD));spec=importlib.util.spec_from_file_location('prior_bq2_analysis',OLD/'analysis.py');aa=importlib.util.module_from_spec(spec)
 # Its 'import engine as e' would otherwise bind this replacement; bind the old exact engine during import.
 cached=sys.modules.get('engine');sys.modules['engine']=original
 try:spec.loader.exec_module(aa)
 finally:sys.modules['engine']=cached
 cases=json.loads((FOLLOW/'run-2026-10-24/BQ2-UNDEFINED-CONTEXTS.json').read_text());allmasked=json.loads((OLD/'MASKED-v3.1.json').read_text());receipts=[]
 for case in cases:
  co=case['reading'];ri=['H','F'].index(co);si=['homogeneous_null','homogeneous_positive'].index(case['scenario']);t=case['trial'];full=[e.copy() for e in allmasked if e['reading']==co and e['context'] in replacement.CONTEXTS];rng=np.random.default_rng(5100000+ri*100000+si*1000+t);yy=(rng.random(len(full))<np.array([.2+(.08*e['x'] if si else 0) for e in full])).astype(np.int8)
  lookup={(e['line'],e['position']):int(y) for e,y in zip(full,yy)}
  for e,y in zip(full,yy):e['y']=int(y)
  _,lab,hands,pages=aa.hetero_data(full,replacement.CONTEXTS);bi=case['bank'];seed=6100000+ri if bi==0 else [913261,ri,si,t,bi];oldmat=aa.permutation_labels(lab,hands,seed);g=GG[co];newlabels=oldmat[case['shuffle_index'],[pages.index(pg) for pg in g.pages]];y=np.array([lookup[e['line'],e['position']] for e in g.events],dtype=np.int8);nn,vv=g.terms(y);value=replacement.scalar(g,nn,vv,newlabels);assert math.isfinite(value);receipts.append(dict(reading=co,trial=t,bank=bi,old_zero_context=case['context'],new_statistic=value,new_minimum_working_variance=float(vv.min())))
 save('ENGINEERING.json',dict(status='PASS',small_orbit_size=len(mat),scalar_max_error=float(np.abs(scores-scalar).max()),exact_orbit_flag_rate=float(np.mean(ps<=.025)),all_tie_fixture_p=1,fixtures=fixtures,old_zero_assignments_replayed=receipts));seal('engineering_verified',['ENGINEERING.json']);print('ENGINEERING PASS',len(mat),'orbit assignments;',len(receipts),'old zero cases',flush=True)
def chunk(task):
 ri,si,start,stop=task;co=['H','F'][ri];scene=replacement.SCENES[si];g=GG[co];rows=[]
 for t in range(start,stop):
  seed=[917260,ri,si,t,0];bankseed=[917260,ri,si,t,1];y=g.generate(scene,seed);rr=replacement.test(g,y,bankseed);k=rr['exceedances'];hi=1 if k==replacement.B else float(beta.ppf(1-.025/2,k+1,replacement.B-k));guarded=min(1,2*(1+replacement.B*hi)/(replacement.B+1))<=.05
  rows.append(dict(reading=co,scenario=scene,scenario_index=si,trial=t,outcome_seed=seed,permutation_seed=bankseed,guarded_flag=guarded,**rr))
 return rows
def qualify():
 verify();support=json.loads((R/'SUPPORT.json').read_text());D=R/'trials';D.mkdir(exist_ok=True);tasks=[]
 for ri,co in enumerate(['H','F']):
  if not support[co]['gate']:continue
  for si,scene in enumerate(replacement.SCENES):
   n=5000 if si<5 else 1000
   for start in range(0,n,50):
    dest=D/f'{ri}-{si}-{start:05d}.jsonl'
    if dest.exists():
     rr=[json.loads(s) for s in dest.read_text().splitlines()];assert len(rr)==50 and all(r['reading']==co and r['scenario_index']==si and r['trial']==start+i for i,r in enumerate(rr));continue
    tasks.append((ri,si,start,start+50))
 with ProcessPoolExecutor(max_workers=3,initializer=init) as pool:
  for task,rr in zip(tasks,pool.map(chunk,tasks,chunksize=1)):
   ri,si,start,stop=task;dest=D/f'{ri}-{si}-{start:05d}.jsonl';tmp=dest.with_suffix('.tmp');tmp.write_text(''.join(json.dumps(v)+'\n' for v in rr));tmp.replace(dest);print('Controls',ri,si,stop,'committed',flush=True)
 save('CONTROLS-COMPLETE.json',dict(unique_trials=sum(27000 for co in ['H','F'] if support[co]['gate']),fresh_shuffles=sum(270000000 for co in ['H','F'] if support[co]['gate'])));print('CONTROLS COMPLETE',flush=True)
def audit():
 verify();init();assert (R/'CONTROLS-COMPLETE.json').exists();checks=[]
 for path in sorted((R/'trials').glob('*.jsonl')):
  for line in path.read_text().splitlines():
   r=json.loads(line)
   if r['trial']!=0 and (r['scenario_index']>=5 or not r['flag']):continue
   g=GG[r['reading']];y=g.generate(r['scenario'],r['outcome_seed']);rr=replacement.test(g,y,r['permutation_seed'],probe=True)
   for key in ['p','Q','exceedances','flag','degenerate','permutation_Q_sha256','outcome_sha256']:assert rr[key]==r[key],(key,r['reading'],r['scenario'],r['trial'])
   checks.append(dict(reading=r['reading'],scenario=r['scenario'],trial=r['trial'],scalar_probe_error=rr['scalar_probe_error']))
 save('POSTRUN-AUDIT.json',dict(status='PASS',checks=checks,max_scalar_error=max([x['scalar_probe_error'] for x in checks],default=0)));print('AUDIT PASS',len(checks),flush=True)
def interval(k,n,error):return [0 if not k else float(beta.ppf(error/2,k,n-k+1)),1 if k==n else float(beta.ppf(1-error/2,k+1,n-k))]
def summarize():
 verify();support=json.loads((R/'SUPPORT.json').read_text());seen=set();counts=collections.defaultdict(lambda:[0,0,0,0]);hashes={}
 for p in (R/'trials').glob('*.jsonl'):
  hashes[str(p.relative_to(R))]=sha(p)
  for line in p.read_text().splitlines():
   r=json.loads(line);key=(r['reading'],r['scenario_index'],r['trial']);assert key not in seen;seen.add(key);c=counts[r['reading'],r['scenario_index']];c[0]+=1;c[1]+=r['flag'];c[2]+=r['degenerate'];c[3]+=r['guarded_flag']
 results={}
 for co in ['H','F']:
  if not support[co]['gate']:results[co]=dict(status='NOT ESTIMABLE',controls=[]);continue
  rr=[]
  for si,scene in enumerate(replacement.SCENES):
   n,k,deg,guard=counts[co,si];assert n==(5000 if si<5 else 1000);lo,hi=interval(k,n,.05/14);status='DESCRIPTIVE POWER' if si>=5 else 'CERTIFIED BELOW TOLERANCE' if hi<=.05 else 'EVIDENCE ABOVE TOLERANCE' if lo>.05 else 'INCONCLUSIVE';alarm=si<5 and lo>.025;rr.append(dict(scenario=scene,n=n,flags=k,rate=k/n,simultaneous_exact_CI95=[lo,hi],guarded_flags=guard,guarded_power_CI95=interval(guard,n,.05/14) if si>=5 else None,degenerate=deg,status=status,nominal_size_alarm=alarm))
  passed=all(r['status']=='CERTIFIED BELOW TOLERANCE' and not r['nominal_size_alarm'] for r in rr[:5]);results[co]=dict(status='QUALIFIED CALIBRATION' if passed else 'NOT QUALIFIED',inconclusive=any(r['status']=='INCONCLUSIVE' for r in rr[:5]),controls=rr)
 assert len(seen)==json.loads((R/'CONTROLS-COMPLETE.json').read_text())['unique_trials'];assert json.loads((R/'POSTRUN-AUDIT.json').read_text())['status']=='PASS';save('QUALIFICATION.json',dict(unique_trials=len(seen),results=results));save('TRIAL-HASHES.json',hashes);seal('qualification_and_audit_frozen',['QUALIFICATION.json','POSTRUN-AUDIT.json','CONTROLS-COMPLETE.json','TRIAL-HASHES.json']);print(json.dumps({co:r['status'] for co,r in results.items()}),flush=True)
def random_effects(effects,variances):
 y=np.array(effects);v=np.array(variances)
 def q(t):
  value=0.
  for ix in [[0,1,2],[3,4]]:
   w=1/(v[ix]+t);mu=(w*y[ix]).sum()/w.sum();value+=float((w*(y[ix]-mu)**2).sum())
  return value
 def objective(t):return float(np.log(v+t).sum()+sum(np.log((1/(v[ix]+t)).sum()) for ix in [[0,1,2],[3,4]])+q(t))
 opt=minimize_scalar(objective,bounds=(0,1),method='bounded',options={'xatol':1e-13});tau=float(opt.x) if opt.fun<objective(0) else 0.
 def root(target):
  if q(0)<=target:return 0.
  hi=1.
  while q(hi)>target:hi*=2
  return float(brentq(lambda t:q(t)-target,0,hi))
 Q=q(0);return dict(tau2=tau,Q_profile95=[root(chi2.ppf(.975,3)),root(chi2.ppf(.025,3))],I2=max(0,(Q-3)/Q) if Q else 0,df=3,separate_scribe_means=True,working_model_descriptive=True)
def outcomes():
 verify();assert not (R/'RESULTS.json').exists();init();qual=json.loads((R/'QUALIFICATION.json').read_text());result={};oldest=json.loads((OLD/'PART-B-ESTIMATES.json').read_text());ledger=None
 for ri,co in enumerate(['H','F']):
  if qual['results'][co]['status']!='QUALIFIED CALIBRATION':result[co]=dict(status='BLOCKED: QUALIFICATION',p=None,holm_p=None,manuscript_scored=False);continue
  if ledger is None:
   with (OLD/'EVENTS.csv').open(encoding='utf-8') as f:ledger={(r['reading'],r['line'],int(r['position'])):r for r in csv.DictReader(f) if not r['exclusion_reason']}
  g=GG[co];yy=[]
  for e in g.events:
   r=ledger[co,e['line'],e['position']];assert r['origin']==e['origin'] and r['family']==e['family'];y=int(r['outcome']);assert y==int(r['follower'].startswith('qok'));yy.append(y)
  y=np.array(yy,dtype=np.int8);rr=replacement.test(g,y,[917261,ri],probe=True);lo,hi=interval(rr['exceedances'],replacement.B,.025);adjusted_ci=[min(1,2*(1+replacement.B*x)/(replacement.B+1)) for x in [lo,hi]];adjusted=min(1,2*rr['p'])
  status='NOT ESTIMABLE: DEGENERATE' if rr['degenerate'] else 'DETECTED HETEROGENEITY' if adjusted<=.05 and adjusted_ci[1]<=.05 else 'NO DETECTION' if adjusted_ci[0]>.05 else 'INCONCLUSIVE INNER MONTE CARLO'
  effects=rr['context_effects'];assert all(abs(100*effects[j]-oldest[c+'-'+co]['aggregate']['effect_points'])<1e-10 for j,c in enumerate(replacement.CONTEXTS));re=random_effects(effects,rr['context_working_variances']);assert abs(replacement.scalar(g,*g.terms(y),g.labels)-rr['Q'])<1e-10
  result[co]=dict(status=status,manuscript_scored=True,test=rr,p=rr['p'],holm_p=adjusted,holm_internal_other_p=1,adjusted_inner_MC_CI95_family2=adjusted_ci,full_permutation_tail_CI95_family2=[lo,hi],context_effects_points={c:100*effects[j] for j,c in enumerate(replacement.CONTEXTS)},random_effects_descriptive=re)
 save('RESULTS.json',dict(retrospective=True,readings=result,old_BQ2='UNQUALIFIED; UNCHANGED',both_readings_detected=all(r['status']=='DETECTED HETEROGENEITY' for r in result.values())));seal('conditional_manuscript_scoring_complete',['RESULTS.json'])
 lines=['RETROSPECTIVE — all material exposed or uncertified (v100/v102).','','Separate B-Q2 replacement R1. Original attempts and the original unqualified B-Q2 remain unchanged. The replacement retains raw folio×ending MH effects, uses positive Jeffreys-stabilized binomial working variances, and centers heterogeneity within each scribe. Qualification, not merely mathematical finiteness, gates scoring.','','| Reading | Supported folios | Context folios C1–C5 | Qualification | Manuscript result | Adjusted p |','|---|---|---|---|---|---|']
 support=json.loads((R/'SUPPORT.json').read_text())
 for co in ['H','F']:lines.append(f"| {co} | {support[co]['supported_folios']} | {list(support[co]['context_pages'].values())} | {qual['results'][co]['status']} | {result[co]['status']} | {result[co].get('holm_p')} |")
 lines+=['','A blocked reading has no new manuscript statistic, p, REML or I². H/F were never pooled. No failed permutation or synthetic trial was dropped; scoreable zero empirical variance uses the frozen positive working variance, and all-tie scores remain degenerate rather than negative evidence.','','| Reading | Scenario | Flags/N | Simultaneous exact interval | Decision | Nominal alarm | Guarded flags |','|---|---|---|---|---|---|---|']
 for co in ['H','F']:
  for cr in qual['results'][co]['controls']:ci=cr['simultaneous_exact_CI95'];lines.append(f"| {co} | {cr['scenario']} | {cr['flags']}/{cr['n']} | [{ci[0]:.3%}, {ci[1]:.3%}] | {cr['status']} | {cr['nominal_size_alarm']} | {cr['guarded_flags']} |")
 lines+=['','Fixed run:5,000 trials per five required nulls and1,000 per two positives per supported reading (54,000 if both support), each with its own fresh independent10,000-shuffle bank. Point-p flags use p≤.025. Fourteen simultaneous exact Clopper–Pearson intervals quantify outer simulation uncertainty; qualification requires all practical-null upper bounds≤5%, no lower bound>.025 nominal alarm, and no numeric failures. Power has no qualification gate and is descriptive; guarded flags additionally require the inner-MC interval to clear the manuscript cutoff. No extension or retuning occurred.']
 for co in ['H','F']:
  rr=result[co]
  if not rr['manuscript_scored']:continue
  lines+=['',f"{co}: statistic {rr['test']['Q']:.6g}; raw permutation p {rr['p']:.6g}; conservative Holm2 p {rr['holm_p']:.6g}; adjusted inner-MC interval {rr['adjusted_inner_MC_CI95_family2']}. Result: {rr['status']}.",f"{co} descriptive within-scribe random effects: τ²={rr['random_effects_descriptive']['tau2']:.6g}, Q-profile interval={rr['random_effects_descriptive']['Q_profile95']}, I²={rr['random_effects_descriptive']['I2']:.3%}; squared-probability units for τ². Broad intervals remain inconclusive. Context raw effects were verified unchanged."]
 lines+=['','A no-detection result does not establish a constant-strength rule, especially if planted-positive power is weak or τ² intervals are broad. Monte Carlo boundary results remain inconclusive without adding permutations. If qualification fails, the manuscript stays unscored for that reading. Selection of C1/C4 for large earlier effects remains a retrospective bias. No new scribe2-only sensitivities were inferentially scored: their smaller geometries were not independently qualified.','','The five calibration nulls distinguish identical baseline, common+.08 effect, between-scribe baseline changes, between-section baseline changes at equal effect, and a physically availability-preserving common aggregate+.08 effect. The latter uses precomputed MH-weighted available fractions; its probabilities were frozen at support time. The two positives plant+.12 only in C1 with either abstract Bernoulli outcomes or availability-preserving outcomes. The abstract controls do not reproduce every token dependency; this is qualification for authored controls on actual geometry, not universal calibration.','','The working-variance half-count is a fixed Jeffreys construction, not an outcome-tuned numerical floor. Raw observations/effects are unchanged. Studentized permutation tests need care under equal-parameter but nonidentical-distribution nulls; this candidate is not asserted to inherit finite-sample exactness. [Chung and Romano’s primary research](https://statistics.stanford.edu/technical-reports/exact-and-asymptotically-robust-permutation-tests) motivates that distinction. [Astropy’s documentation](https://docs.astropy.org/en/stable/api/astropy.stats.binom_conf_interval.html) describes the Beta(1/2,1/2) construction; [NumPy](https://numpy.org/doc/2.0/reference/random/generated/numpy.random.Generator.permuted.html) documents independent row permutations, and [NIST](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm) documents exact binomial bounds.','','All prior non-cache files were hash-preserved. Engineering includes a complete small permutation orbit, independent scalar scoring, deterministic all-zero/all-one/perfect-prefix fixtures and finite replacement scores on all six prior zero-variance synthetic assignments. POSTRUN-AUDIT.json records independent scalar probes for every fresh null false flag and trial0 per scenario. All outcomes/banks are reproducible from recorded coordinates and hashes. No reserved zodiac material or raw EVT was opened; no meanings, grammar or mechanisms are claimed.']
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');verify();assert all(sha(R/n)==h for n,h in json.loads((R/'TRIAL-HASHES.json').read_text()).items());save('VERIFICATION.json',dict(status='PASS',qualification_frozen_before_scoring=True,prior_files_preserved=len(json.loads((R/'PRESERVATION.json').read_text())['hashes']),unique_qualification_trials=qual['unique_trials'],old_BQ2_unchanged_unqualified=True,manuscript_readings_scored=[co for co,r in result.items() if r['manuscript_scored']],artifact_hashes={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='VERIFICATION.json'}));print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':{'freeze':freeze,'prepare':prepare,'preflight':preflight,'qualify':qualify,'audit':audit,'summarize':summarize,'outcomes':outcomes}[sys.argv[1]]()
