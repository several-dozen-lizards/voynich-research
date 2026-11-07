from pathlib import Path
import collections,hashlib,json,random,re
import numpy as np
from engine import TARGETS,buckets,shuffled,score,test
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
inputs=[P/'frequency-atlas-v48/rows.json',P/'middle-contexts-v72/RESULTS.json']
protocol={'scope':'Primary bath/hand2/CurrierB/rawP, original f75 excluded; shared eligible H/F source loci, readings separate. Other v72 strata not pooled or tested. Corpus already inspected; no untouched confirmation.',
 'frame_exclusion':'Exclude a focal ol/qokedy/qol token whenever it is the middle of exact shedy ___ shedy in that arrangement. Recompute in every shuffle; never delete tokens or concatenate gaps. Adjacent pairs of target words cannot have either member at such a frame center, since neither target is shedy. No special word positions locked.',
 'statistics':'Six signed contrasts: three unordered target-pair forward-minus-reverse counts, and each of three targets outgoing-to-the-other-two minus incoming-from-them. Notice qokedy outgoing pooled contrast and its two constituent edges; keep all six contrasts and both signs.',
 'nulls':'Primary exact_slot: shuffle readable words within page/exactordinal/linelength/unknownmask buckets. Sensitivity within_line: shuffle each readable interior span within line; endpoints and unknown barriers fixed. Preserve complete word frequencies within each declared bucket. Within-line sensitivity does not preserve every exact interior ordinal.',
 'calibration':'4999 shuffles plus observed row, seeds H exact7301/within7302, F exact7303/within7304. Pooled-rank single-step minP across six contrasts and both tails, with conservative ties. Further Bonferroni x4 across H/F and both nulls. Frozen positive qokedy-direction and fully corrected p<=.05 screen; do not tune after outcomes.',
 'selection_limit':'Family accounts for all pairwise directions and outward/inward two-edge choices within the fixed triad, not choosing these words, this anchor set, spelling rules, strata or earlier research choices. Retrospective conditional evidence only.',
 'engineering':'Before manuscript scoring: hand-worked pair/excluded-center counts and shuffle bucket/unknown/endpoint invariants. 20 exchangeable and20 planted triad-direction samples per mode with199shuffles; fixed gate <=4/20null flags and>=12/20planted detections on noticed contrast triad-familyp<=.05 with positive excess. Generator-limited engineering check, not historical validation.',
 'preservation':'Retain every target-pair source occurrence including reverse directions and self repetitions, all six contrast outcomes, zeros, excluded-frame centers and folio contributions. Save full permutation matrices for exact numerical replay. Report finite-shuffle uncertainty if any point estimate approaches threshold; no adaptive resampling.',
 'interpretation':'Tests written-word order only. No semantic roles, prefix meanings, validated syntax or independence of H/F inferred. Non-significance is not absence of ordering.'}
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};freeze.update({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['engine.py','run.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)
def invariant(rs,mode):
 bs=buckets(rs,mode);out=shuffled(rs,bs,random.Random(73))
 for r,ws in zip(rs,out):
  assert len(ws)==len(r['tokens']) and [i for i,w in enumerate(ws) if w is None]==[i for i,w in enumerate(r['tokens']) if w is None]
  if mode=='within_line':assert collections.Counter(ws)==collections.Counter(r['tokens']) and ws[0]==r['tokens'][0] and ws[-1]==r['tokens'][-1]
 for b in bs:assert collections.Counter(rs[ri]['tokens'][i] for ri,i in b)==collections.Counter(out[ri][i] for ri,i in b)
v,c,ex=score([['shedy','qokedy','shedy'],['qokedy','ol'],['qol','qokedy']]);assert list(v)==[-1,0,-1,-1,0,1] and ex['qokedy']==1
q=[]
for mi,mode in enumerate(['exact_slot','within_line']):
 flags=hits=0
 for trial in range(20):
  rng=random.Random(73000+trial);null=[];planted=[]
  for i in range(64):
   ws=['s']+[rng.choice(['a','b','c','d','ol','qokedy','qol','shedy']) for _ in range(10)]+['t'];ps=ws[:]
   if i%2==0:
    j=3 if i%4==0 else 7;ps[j]='qokedy';ps[j+1]='ol' if i%8==0 else 'qol'
   null.append(dict(page='toy',tokens=ws));planted.append(dict(page='toy',tokens=ps))
  for isp,rs in [(False,null),(True,planted)]:
   invariant(rs,mode);out,_=test(rs,mode,199,73500+trial+100*mi);r=out['tests'][4];found=r['observed']>r['null_mean'] and r['p_triad_family']<=.05
   if isp:hits+=found
   else:flags+=found
  if (trial+1)%5==0:print('engineering',mode,trial+1,flush=True)
 q.append(dict(mode=mode,null_flags=flags,null_trials=20,planted_detections=hits,planted_trials=20,passes=flags<=4 and hits>=12))
save('QUALIFICATION.json',dict(results=q,scope='Generator-limited engineering controls, not semantic or historical qualification.'))
if not all(x['passes'] for x in q):raise SystemExit('Engineering gate failed; manuscript tests not run; failures retained.')
raw=load(inputs[0]);old=load(inputs[1]);base=[r for r in raw if tuple(r[2:6])==('Balneological','2','B','P') and re.match(r'f\d+',r[1])[0]!='f75'];locs={t:{r[6] for r in base if r[0]==t} for t in ['H','F']};shared=locs['H']&locs['F'];panels=[];observed={}
for ti,tr in enumerate(['H','F']):
 rs=[dict(page=r[1],folio=re.match(r'f\d+',r[1])[0],locator=r[6],tokens=r[7]) for r in base if r[0]==tr and r[6] in shared];events=[];byfolio=collections.defaultdict(list)
 for r in rs:
  byfolio[r['folio']].append(r['tokens'])
  for i in range(len(r['tokens'])-1):
   a,b=r['tokens'][i:i+2]
   if a in TARGETS and b in TARGETS:events.append(dict(r,ordinal=i+1,first=a,second=b))
 observed[tr]=dict(events=events,excluded_centers={w:old['readings'][tr]['profiles'][w]['excluded_frame_centers'] for w in TARGETS},folio_contrasts={f:score(lines)[0].tolist() for f,lines in byfolio.items()})
 for mi,mode in enumerate(['exact_slot','within_line']):
  invariant(rs,mode);out,scores=test(rs,mode,4999,7301+2*ti+mi)
  for x in out['tests']:x['p_four_panels']=min(1,4*x['p_triad_family'])
  out.update(reading=tr,lines=len(rs),folios=len(byfolio));panels.append(out);np.savez_compressed(R/(tr+'-'+mode+'-null.npz'),scores=scores)
  print(tr,mode,out['tests'][4],flush=True)
save('RESULTS.json',dict(protocol=protocol,qualification=q,panels=panels,observed=observed));save('SUMMARY.json',[dict(reading=p['reading'],mode=p['mode'],noticed=p['tests'][4],individual=[p['tests'][0],p['tests'][2]],mobility=p['mobility']) for p in panels]);save('VERIFICATION.json',dict(frozen_inputs_and_methods='pass',shuffle_invariants='pass',hand_worked_direction_count='pass',semantic_inference='none',browser_visual_review='not performed'))
