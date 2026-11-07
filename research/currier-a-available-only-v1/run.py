import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,csv,hashlib,math,itertools,collections
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.stats import beta
R=Path(__file__).resolve().parent;P=R.parent;OLD=P/'sh-qok-context-map-v3';FOLLOW=P/'sh-qok-qualification-followup-v1';READJ=P/'sh-qok-retrospective-readjudication-v1'
sys.path.insert(0,str(OLD));import analysis as a
sys.path.insert(0,str(FOLLOW));from diagnose import oracle
SCENES=['null_low','null_high','additive','junction_only','availability_only','positive'];CC={};GG={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def seal(phase,names):
 with (R/'PHASES.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(phase=phase,utc=datetime.now(timezone.utc).isoformat(),hashes={n:sha(R/n) for n in names}))+'\n')
def preserved():
 return {str(p):sha(p) for root in [OLD,FOLLOW,READJ] for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
def verify():
 original=json.loads((R/'PRESERVATION.json').read_text());assert all(sha(p)==h for p,h in original['hashes'].items())
 for line in (R/'PHASES.jsonl').read_text().splitlines():
  for name,h in json.loads(line)['hashes'].items():assert sha(R/name)==h,('phase file changed',name)
def freeze():
 assert not (R/'PROTOCOL.json').exists()
 oldmanifest=json.loads((FOLLOW/'PRESERVED-ATTEMPT.json').read_text());assert all(sha(OLD/n)==h for n,h in oldmanifest['hashes'].items())
 save('PRESERVATION.json',dict(hash_exclusions='__pycache__ only',hashes=preserved()))
 save('PROTOCOL.json',dict(status='FROZEN BEFORE AVAILABLE-ONLY SUPPORT AND QUALIFICATION',authority='User explicitly requested freeze and run a separate available-only Currier A test',utc=datetime.now(timezone.utc).isoformat(),exposure='RETROSPECTIVE; all manuscript material exposed/uncertified and earlier aggregate/descriptive outcomes known. Not prospective confirmation or an independent replication.',question='Among available followers in Davis scribe1 Botanical+Recipes C6+C7, is next-qok more frequent after sh than ch? C6+C7 are the only pooling; H/F separate.',data='Only frozen v3.1 MASKED-v3.1.json and, after qualification, EVENTS.csv. Scribe1 C6+C7, same P-unit eligibility/tokenizer/exclusions/ending families. Drop blocked events before folio x ending strata. Availability excludes ch/sh/cth/ckh/cph/cfh follower openings. No new folios, reserved zodiac, raw EVT, glyph merges or separate section tests.',support='Compute without y: V>=80, >=8 supported pages, no page>25% of V. Failed reading NOT ESTIMABLE; do not expand material. Hash masked subset and support before controls.',engine='Unchanged attempt C exact one-sided sh>ch convolution; stratum folio x ending. MH risk difference with4999 folio-bootstrap percentile95 CI; seeds915260+reading_index. Degenerate exact distribution NOT ESTIMABLE. No new engine or nuisance fitting.',multiplicity='Conservative continuation of Part B correction: fixed Holm2 family per reading [CA-available, B-Q2-unqualified]. B-Q2 internal p=1, displayed inferential p=null; never remove its slot. Thus available-only p is doubled. This new candidate does not replace or alter the previous aggregate question/family. H/F are alternate readings and cannot be pooled; headline requires both PASS. No claim of global correction across research history.',qualification=dict(nulls=SCENES[:-1],positive='.20 after ch vs .35 after sh, among available followers',N='Exactly10000 per required null and2000 per positive per supported reading. If both support, total104000 unique trial coordinates. No extension, seed replacement, optional stopping, effect enlargement or retuning.',generators='Existing e.synthetic unchanged on actual available-only geometry: low.20, high.60, additive page/line/position, final-y junction .10/.60, positive .20/.35. availability_only maps to independently seeded null_low after filtering, a duplicate marginal law, not a distinct mechanism. All synthetic events are available; structural blockers are absent.',randomness='Coordinate seed [914260,reading_index(H0,F1),scenario_index in SCENES,trial]. Execution independent of scheduling. Batched draws replay the original generator bitwise, checked on first5 coordinates of each cell/scenario; those same coordinates remain part of the fixed run, not additional trials.',intervals='12 simultaneous two-sided exact Clopper-Pearson intervals, per-interval error .05/12, even if a reading lacks support. Keep original pointwise Wilson95 as descriptive bridge.',gates='Required-null U<=.05 CERTIFIED; L>.05 EVIDENCE ABOVE TOLERANCE; otherwise INCONCLUSIVE. Separately alarm if L>.025; exchangeable-null alarm blocks qualification even below practical tolerance. Additive is a nonexchangeable robustness stress. Positive L>=.80 POWER QUALIFIED; U<.80 EVIDENCE UNDERPOWERED; otherwise POWER INCONCLUSIVE. A reading qualifies only if every practical null and power gate passes and no exchangeable nominal alarm. No detected nominal alarm is not proof of exact size.'),verification='Preservation and phase hashes, no outcomes in masked subset, one-to-one original-event coverage, independent small exact oracle; original generator replay of first5 fixed coordinates before full run; all null false flags and trial0 per scenario independently regenerated/oracle-audited after run. Near nominal boundary use integer/rational oracle; unresolved arithmetic blocks qualification.',scoring='Only after controls, audit and qualification hashes freeze: attach original ledger y to subset, reconcile fields, compute manuscript exact p only if reading qualifies/support passes. Independently verify p and MH effect. Otherwise report effect/CI descriptively with no inferential p. Holm2 unchanged per reading.',comparison='Carry original aggregate Currier-A estimate and CI unchanged for reference only. Descriptive surviving-share ratio available RD/aggregate RD uses paired4999 folio bootstrap draws, seed916260+reading_index. Invalid zero-denominator draws counted. Ratio is not a mediation fraction. No aggregate p rescoring or new context/section tests.',BQ2='UNQUALIFIED throughout. No new heterogeneity, REML, permutation banks or scribe2 sensitivities.',interpretation='A both-reading PASS supports this retrospective available-only association in these samples. It excludes the specified binary blocking explanation alone, not all spelling/junction/register confounding; no scribe-independent mechanism, grammar, sounds or meanings.',preservation='Write only this new directory. Preserve all non-cache files in v3.1, fixed qualification follow-up and separate aggregate re-adjudication. Prior results/statuses remain unchanged.'))
 seal('protocol_frozen',['run.py','PROTOCOL.json','PRESERVATION.json']);print('PROTOCOL FROZEN',flush=True)
def prepare():
 verify();assert not (R/'SUPPORT.json').exists();masked=json.loads((OLD/'MASKED-v3.1.json').read_text());assert all('y' not in v and 'follower' not in v for v in masked)
 subset=[v for v in masked if v['context'] in ['C6','C7'] and v['hand']=='1' and v['available']];support={co:a.e.support([v for v in subset if v['reading']==co]) for co in ['H','F']}
 save('MASKED.json',subset);save('SUPPORT.json',support);seal('outcome_blind_support_frozen',['MASKED.json','SUPPORT.json']);print(json.dumps({co:{k:s[k] for k in ['eligible_origins','V','supported_pages','max_page_share','gate']} for co,s in support.items()},indent=2),flush=True)
def init():
 global CC,GG
 events=json.loads((R/'MASKED.json').read_text());CC={co:[v for v in events if v['reading']==co] for co in ['H','F']};GG={}
 for co,vv in CC.items():
  pl={v['folio']:i for i,v in enumerate(vv)};ll={v['line']:i for i,v in enumerate(vv)};GG[co]=dict(pg=np.array([pl[v['folio']] for v in vv]),ln=np.array([ll[v['line']] for v in vv]),pos=np.array([.7*(2*v['position']/max(1,v['length']-1)-1) for v in vv]),x=np.array([v['x'] for v in vv]),endy=np.array([v['origin'][-1]=='y' for v in vv]))
def generate(co,scene,seed):
 rng=np.random.default_rng(seed);n=len(CC[co]);g=GG[co];pg=rng.choice([-.7,.7],size=n);ln=rng.choice([-.7,.7],size=n)
 if scene in ['null_low','availability_only']:p=.2
 elif scene=='null_high':p=.6
 elif scene=='positive':p=.2+.15*g['x']
 elif scene=='junction_only':p=.1+.5*g['endy']
 elif scene=='additive':p=np.array([1/(1+math.exp(-float(z))) for z in -1+pg[g['pg']]+ln[g['ln']]+g['pos']])
 else:raise ValueError(scene)
 return (rng.random(n)<p).astype(int)
def preflight():
 verify();init();checks=0;replay=[]
 for n in range(2,7):
  for k in range(1,n):
   vv=[dict(folio='toy',family='y',x=int(i<k)) for i in range(n)]
   for bits in itertools.product([0,1],repeat=n):
    y=np.array(bits);p=oracle(vv,y);q=a.e.exact(vv,y)['p'];assert p is None and q is None or abs(p-q)<1e-11;checks+=1
 for ri,co in enumerate(['H','F']):
  for si,scene in enumerate(SCENES):
   for t in range(5):
    seed=[914260,ri,si,t];y=generate(co,scene,seed);direct=a.e.synthetic(CC[co],'null_low' if scene=='availability_only' else scene,seed);assert np.array_equal(y,direct);replay.append(dict(reading=co,scenario=scene,trial=t,outcome_sha256=hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest()))
 save('PREFLIGHT.json',dict(status='PASS',exact_oracles=checks,fixed_coordinate_replays=replay,extra_qualification_coordinates=0));seal('engineering_verified',['PREFLIGHT.json']);print('ENGINEERING PASS',checks,flush=True)
def chunk(task):
 ri,si,start,stop=task;co=['H','F'][ri];scene=SCENES[si];vv=CC[co];out=[]
 for t in range(start,stop):
  seed=[914260,ri,si,t];y=generate(co,scene,seed);rr=a.e.exact(vv,y);p=rr['p'];out.append(dict(reading=co,scenario=scene,scenario_index=si,trial=t,seed=seed,p=p,flag=p is not None and p<=.025,degenerate=rr['degenerate'],outcome_sha256=hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest()))
 return out
def qualify():
 verify();support=json.loads((R/'SUPPORT.json').read_text());D=R/'trials';D.mkdir(exist_ok=True);tasks=[]
 for ri,co in enumerate(['H','F']):
  if not support[co]['gate']:continue
  for si,scene in enumerate(SCENES):
   n=2000 if scene=='positive' else 10000
   for start in range(0,n,200):
    path=D/f'{ri}-{si}-{start:05d}.jsonl'
    if path.exists():
     rows=[json.loads(s) for s in path.read_text().splitlines()];assert len(rows)==200 and all(r['trial']==start+i and r['reading']==co and r['scenario']==scene for i,r in enumerate(rows));continue
    tasks.append((ri,si,start,start+200))
 with ProcessPoolExecutor(max_workers=3,initializer=init) as pool:
  for task,rr in zip(tasks,pool.map(chunk,tasks,chunksize=1)):
   ri,si,start,stop=task;dest=D/f'{ri}-{si}-{start:05d}.jsonl';tmp=dest.with_suffix('.tmp');tmp.write_text(''.join(json.dumps(v)+'\n' for v in rr));tmp.replace(dest);print('Controls',ri,si,stop,'committed',flush=True)
 save('CONTROLS-COMPLETE.json',dict(unique_trials=sum(52000 for co in ['H','F'] if support[co]['gate']),fixed_coordinates_complete=True));print('CONTROLS COMPLETE',flush=True)
def rational(vv,y):
 from fractions import Fraction
 dist={0:1};offset=obs=0
 for ix in a.e.grouping(vv).values():
  ns=sum(vv[i]['x'] for i in ix);nc=len(ix)-ns;t=sum(int(y[i]) for i in ix);lo=max(0,t-nc);hi=min(ns,t);local={j-lo:math.comb(ns,j)*math.comb(nc,t-j) for j in range(lo,hi+1)};offset+=lo;obs+=sum(int(y[i])*vv[i]['x'] for i in ix);new=collections.Counter()
  for s,c in dist.items():
   for z,d in local.items():new[s+z]+=c*d
  dist=dict(new)
 return Fraction(sum(c for k,c in dist.items() if k>=obs-offset),sum(dist.values()))
def audit():
 verify();init();assert (R/'CONTROLS-COMPLETE.json').exists();checks=[];boundaries=[]
 for path in sorted((R/'trials').glob('*.jsonl')):
  for line in path.read_text().splitlines():
   r=json.loads(line)
   if r['trial']!=0 and (r['scenario']=='positive' or not r['flag']):continue
   vv=CC[r['reading']];y=a.e.synthetic(vv,'null_low' if r['scenario']=='availability_only' else r['scenario'],r['seed']);assert hashlib.sha256(y.astype(np.uint8).tobytes()).hexdigest()==r['outcome_sha256'];p=oracle(vv,y);error=abs(p-r['p']) if p is not None and r['p'] is not None else 0.;assert error<1e-11
   if p is not None and abs(p-.025)<1e-11:
    from fractions import Fraction
    pp=rational(vv,y);assert (pp<=Fraction(1,40))==r['flag'];boundaries.append(dict(reading=r['reading'],scenario=r['scenario'],trial=r['trial'],p=str(pp)))
   else:assert (p is not None and p<=.025)==r['flag']
   checks.append(dict(reading=r['reading'],scenario=r['scenario'],trial=r['trial'],absolute_error=error))
 save('POSTRUN-AUDIT.json',dict(status='PASS',checks=checks,max_error=max([v['absolute_error'] for v in checks],default=0),rational_boundary_checks=boundaries));print('AUDIT PASS',len(checks),flush=True)
def summarize():
 verify();support=json.loads((R/'SUPPORT.json').read_text());counts=collections.defaultdict(lambda:[0,0,0]);seen=set()
 for p in (R/'trials').glob('*.jsonl'):
  for line in p.read_text().splitlines():
   r=json.loads(line);key=(r['reading'],r['scenario'],r['trial']);assert key not in seen;seen.add(key);v=counts[r['reading'],r['scenario']];v[0]+=1;v[1]+=r['flag'];v[2]+=r['degenerate']
 result={}
 for co in ['H','F']:
  rows=[]
  if not support[co]['gate']:result[co]=dict(status='NOT ESTIMABLE',controls=[]);continue
  for scene in SCENES:
   n,k,deg=counts[co,scene];assert n==(2000 if scene=='positive' else 10000);err=.05/12;lo=0 if not k else float(beta.ppf(err/2,k,n-k+1));hi=1 if k==n else float(beta.ppf(1-err/2,k+1,n-k));power=scene=='positive';status=('POWER QUALIFIED' if lo>=.8 else 'EVIDENCE UNDERPOWERED' if hi<.8 else 'POWER INCONCLUSIVE') if power else ('CERTIFIED BELOW TOLERANCE' if hi<=.05 else 'EVIDENCE ABOVE TOLERANCE' if lo>.05 else 'INCONCLUSIVE');alarm=not power and lo>.025;rows.append(dict(scenario=scene,n=n,flags=k,rate=k/n,degenerate=deg,simultaneous_exact_CI95=[lo,hi],wilson95_descriptive=a.e.wilson(k,n),status=status,nominal_excess=alarm,exchangeable_nominal_alarm=alarm and scene!='additive'))
  good=all(v['status'] in ['POWER QUALIFIED','CERTIFIED BELOW TOLERANCE'] and not v['exchangeable_nominal_alarm'] for v in rows);result[co]=dict(status='QUALIFIED' if good else 'NOT QUALIFIED',controls=rows)
 assert len(seen)==json.loads((R/'CONTROLS-COMPLETE.json').read_text())['unique_trials'];assert json.loads((R/'POSTRUN-AUDIT.json').read_text())['status']=='PASS';save('QUALIFICATION.json',dict(unique_trials=len(seen),results=result));seal('qualification_and_audit_frozen',['CONTROLS-COMPLETE.json','QUALIFICATION.json','POSTRUN-AUDIT.json']);save('TRIAL-HASHES.json',{str(p.relative_to(R)):sha(p) for p in (R/'trials').glob('*.jsonl')});seal('trial_receipts_frozen',['TRIAL-HASHES.json']);print(json.dumps({co:v['status'] for co,v in result.items()}),flush=True)
def outcomes():
 verify();assert not (R/'RESULTS.json').exists();masked=json.loads((R/'MASKED.json').read_text());qual=json.loads((R/'QUALIFICATION.json').read_text());support=json.loads((R/'SUPPORT.json').read_text())
 with (OLD/'EVENTS.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
 ledger={}
 for r in rows:
  if r['context'] not in ['C6','C7'] or r['exclusion_reason'] or r['available']!='True':continue
  key=(r['reading'],r['line'],int(r['position']));assert key not in ledger;ledger[key]=r
 assert len(ledger)==len(masked);events=[]
 for v in masked:
  r=ledger[v['reading'],v['line'],v['position']];assert r['origin']==v['origin'] and r['family']==v['family'];y=int(r['outcome']);assert y==int(r['follower'].startswith('qok'));events.append(v|dict(y=y))
 result={};audits=[];aggregate=json.loads((READJ/'PART-B-TESTS.json').read_text());allmasked=json.loads((OLD/'MASKED-v3.1.json').read_text());oldledger={(r['reading'],r['line'],int(r['position'])):r for r in rows if r['context'] in ['C6','C7'] and not r['exclusion_reason']}
 for ri,co in enumerate(['H','F']):
  vv=[v for v in events if v['reading']==co];assert a.e.support(vv)==support[co];estimate=a.estimate(vv,915260+ri);scorable=qual['results'][co]['status']=='QUALIFIED' and support[co]['gate'];raw=a.e.exact(vv) if scorable else dict(p=None,degenerate=None);adjusted=a.e.holm([raw['p'],None]);assert adjusted[0] is None or adjusted[0]==min(1,2*raw['p'])
  num=den=0.
  for ix in a.e.grouping(vv).values():
   ns=sum(vv[i]['x'] for i in ix);nc=len(ix)-ns
   if ns and nc:w=ns*nc/len(ix);ys=sum(vv[i]['x']*vv[i]['y'] for i in ix);yc=sum((1-vv[i]['x'])*vv[i]['y'] for i in ix);num+=w*(ys/ns-yc/nc);den+=w
  assert abs(100*num/den-estimate['effect_points'])<1e-11
  if raw['p'] is not None:
   independent=oracle(vv,np.array([v['y'] for v in vv]));assert abs(raw['p']-independent)<1e-11;audits.append(dict(reading=co,p_error=abs(raw['p']-independent)))
  status='NOT ESTIMABLE' if not support[co]['gate'] or raw['degenerate'] else 'BLOCKED: QUALIFICATION' if not scorable else 'PASS' if adjusted[0]<=.05 and estimate['effect_points']>0 else 'NO PASS'
  agg=[]
  for v in allmasked:
   if v['reading']==co and v['context'] in ['C6','C7']:agg.append(v|dict(y=int(oldledger[co,v['line'],v['position']]['outcome'])))
  result[co]=dict(status=status,estimate=estimate,exact=raw,holm_p=adjusted[0],family=dict(members=['CA-available-'+co,'B-Q2-'+co],internal_p=[raw['p'] if raw['p'] is not None else 1,1],BQ2_status='UNQUALIFIED',BQ2_display_p=None),qualification=qual['results'][co]['status'],original_aggregate_reference=aggregate['B-Q1-'+co]['estimate'],surviving_share_descriptive=a.share(agg,vv,916260+ri))
 save('RESULTS.json',dict(retrospective=True,readings=result,both_readings_pass=all(v['status']=='PASS' for v in result.values()),BQ2='UNQUALIFIED'));seal('manuscript_scored',['RESULTS.json'])
 with (R/'EVENTS.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,list(events[0]));w.writeheader();w.writerows(events)
 lines=['RETROSPECTIVE — all material exposed or uncertified (v100/v102).','','Separate available-only Currier A test, frozen before support and qualified at actual support before manuscript scoring. H/F remain alternate readings, never pooled. All earlier attempts remain unchanged.','','| Reading | Available events | V | Supported pages | Largest page share | Effect, points [95% CI] | Raw p | Holm2 p | Result |','|---|---|---|---|---|---|---|---|']
 for co in ['H','F']:
  rr=result[co];s=support[co];es=rr['estimate'];ci=es['CI95_points'];lines.append(f"| {co} | {len([v for v in events if v['reading']==co])} | {s['V']:.3f} | {s['supported_pages']} | {s['max_page_share']:.3%} | {es['effect_points']:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}] | {rr['exact']['p']} | {rr['holm_p']} | {rr['status']} |")
 lines+=['','Both-reading headline: '+('PASS.' if all(v['status']=='PASS' for v in result.values()) else 'NO BOTH-READING PASS.'),'','The conservative fixed Holm2 family in each reading is [this new available-only candidate, unqualified B-Q2]. B-Q2 occupies internal p=1 and displays no inferential p. Prior aggregate Currier A tests and their families are preserved as historical separate questions. This is not correction for the entire research history.','','| Reading | Scenario | Flags/N | Simultaneous exact interval | Decision | Exchangeable nominal alarm |','|---|---|---|---|---|---|']
 for co in ['H','F']:
  for cr in qual['results'][co]['controls']:ci=cr['simultaneous_exact_CI95'];lines.append(f"| {co} | {cr['scenario']} | {cr['flags']}/{cr['n']} | [{ci[0]:.3%}, {ci[1]:.3%}] | {cr['status']} | {cr['exchangeable_nominal_alarm']} |")
 lines+=['','Qualification used exactly10,000 per required null and2,000 per positive per supported reading, with12 simultaneous two-sided exact Clopper–Pearson intervals. Practical null target U≤5%, positive target L≥80%; exchangeable-null lower bound >2.5% triggers a nominal alarm. No alarm is not proof of exact nominal size. Inconclusive and failed cells were retained; no run extension or retuning occurred. The availability-only control is an independently seeded repetition of the low-null law after filtering. Additive variation is a robustness stress, not an exchangeability guarantee.','','Descriptive comparison with the original aggregate question:','','| Reading | Aggregate effect [CI], points | Available effect [CI], points | Available/aggregate share [paired CI] |','|---|---|---|---|']
 for co in ['H','F']:
  rr=result[co];ag=rr['original_aggregate_reference'];av=rr['estimate'];sh=rr['surviving_share_descriptive'];lines.append(f"| {co} | {ag['effect_points']:+.3f} [{ag['CI95_points'][0]:+.3f}, {ag['CI95_points'][1]:+.3f}] | {av['effect_points']:+.3f} [{av['CI95_points'][0]:+.3f}, {av['CI95_points'][1]:+.3f}] | {sh['share']:.3f} [{sh['CI95'][0]:.3f}, {sh['CI95'][1]:.3f}] |")
 lines+=['','The share is descriptive, not a causal mediation fraction; the available and aggregate contrasts use different denominators/stratum weights. Invalid bootstrap draws are recorded in RESULTS.json. The aggregate inferential p-value was not rescored.','','A pass supports this retrospective association among available followers of scribe1 in C6+C7. It rules out the specified binary follower-blocking explanation alone for that association, not spelling/junction/register alternatives. It does not prove a scribe-independent mechanism, grammar, semantics or a decipherment. A no-pass or blocked result does not establish absence. The contexts were not separately tested or expanded.','','B-Q2 remains UNQUALIFIED; no new heterogeneity calculation, smoothing, REML, permutations or scribe2 sensitivity was run. Reserved zodiac material and raw EVT were not opened.','','Verification: source/phase preservation, outcome-blind support freeze, independent exact fixtures, original-generator replay of fixed coordinates, post-run audit of every null false flag and trial0, one-to-one ledger reconciliation, independent manuscript exact p and direct MH effect, and fixed Holm2 arithmetic. Prior non-cache file hashes were checked before and after.']
 (R/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');verify();assert all(sha(R/p)==h for p,h in json.loads((R/'TRIAL-HASHES.json').read_text()).items());save('VERIFICATION.json',dict(status='PASS',prior_noncache_files_preserved=len(json.loads((R/'PRESERVATION.json').read_text())['hashes']),support_frozen_before_controls=True,qualification_frozen_before_scoring=True,unique_qualification_trials=qual['unique_trials'],manuscript_oracle_checks=audits,eligible_events=len(events),BQ2_unqualified=True,artifact_hashes={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='VERIFICATION.json'}));print(json.dumps({co:dict(status=rr['status'],effect=rr['estimate']['effect_points'],holm_p=rr['holm_p']) for co,rr in result.items()},indent=2),flush=True)
if __name__=='__main__':{'freeze':freeze,'prepare':prepare,'preflight':preflight,'qualify':qualify,'audit':audit,'summarize':summarize,'outcomes':outcomes}[sys.argv[1]]()
