from pathlib import Path
import collections,hashlib,json,random,re
import numpy as np
from engine import buckets,shuffle,directional,run
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
inputs=[P/'frequency-atlas-v48/rows.json',P/'category-extension-v61/RESULTS.json',P/'neighbor-patterns-v66/FORM-PAIR-SUPPLEMENT.json']
protocol={
 'scope':'qol only; bath section, hand2, Currier B, raw P. Unchanged v61 original numbered-folio exclusions and H/F shared source loci. H/F separate, not independent replications.',
 'primary':'exact_slot: lock all qol and unknown positions; shuffle other words across same page, exact line length, exact ordinal, identical unknown-slot mask. Preserves word counts within these buckets; thus page, position and layout-conditioned word frequencies. May be highly immobile.',
 'sensitivity':'within_line: lock first/last, all qol and unknowns as barriers; shuffle remaining readable contiguous interior segments within each source line. Preserves per-line word multiset and broad positions, not exact non-anchor interior ordinals.',
 'statistic':'D=(prefixed-before - prefixed-after)+(base-after - base-before), summed over chosen literal qo-removal pairs. Anchor positions fixed. No inferred morphology or meaning.',
 'selection_family':'Every literal qoX/X pair with both exact words anywhere in each fixed reading stratum. Test every single pair, every two-pair subset, and the whole available pair inventory. Both signs included. Primary noticed set is qokedy/kedy + qokeedy/keedy; it is not granted special unadjusted status.',
 'calibration':'1999 conditional permutations plus observed row, seeds H exact6701/within6702, F exact6703/within6704. Single-step minP: symmetric pooled tail ranks per subset in observed+permuted rows; minimum across both tails/all subsets each row; family p is fraction of row minima <= observed subset minimum. Then Bonferroni x4 across H/F and both nulls. Ties conservative. Raw two-sided p also shown; not a separate winning criterion.',
 'retrospective_limit':'Corrects the declared pair/subset/sign/null/reading family, not every spelling rule, anchor or research choice previously examined. No untouched confirmation or semantic qualification.',
 'engineering':'Before manuscript test, invariant checks for both shuffle schemes; 20 exchangeable and 20 planted synthetic samples per scheme using 199 shuffles and full available-pair family. Gate <=4/20 false flags and >=12/20 planted detections, limited to this generator. Preserve failures and do not tune after outcomes.',
 'acceptance':'Report corrected p, effect/null interval, mobility, each constituent cells, negative-direction or sparse pairs, folio contributions and all noticed-pair source lines. Require noticed signed D>0 and four-panel adjusted p<=.05 for a supported direction under each null. Failure or immobility is not absence of structure.'}
freeze={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
freeze.update({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'run.py',R/'engine.py']})
if (R/'FREEZE.json').exists():assert load(R/'FREEZE.json')==freeze and load(R/'PROTOCOL.json')==protocol
else:save('PROTOCOL.json',protocol);save('FREEZE.json',freeze)

def invariant(rows,mode):
 bs=buckets(rows,mode);out=shuffle(rows,bs,random.Random(67))
 for ri,(r,ws) in enumerate(zip(rows,out)):
  assert len(r['tokens'])==len(ws)
  for i,w in enumerate(r['tokens']):
   if w in (None,'qol'):assert ws[i]==w
  if mode=='within_line':assert collections.Counter(r['tokens'])==collections.Counter(ws) and r['tokens'][0]==ws[0] and r['tokens'][-1]==ws[-1]
 for bucket in bs:assert collections.Counter(rows[ri]['tokens'][i] for ri,i in bucket)==collections.Counter(out[ri][i] for ri,i in bucket)

qualification=[]
for mi,mode in enumerate(['exact_slot','within_line']):
 false=hit=0
 for trial in range(20):
  rng=random.Random(67000+trial);null=[];planted=[]
  for i in range(64):
   ws=['s']+[rng.choice(['a','b','c','d','e','f','qokedy','kedy']) for _ in range(10)]+['t']
   if i%2==0:ws[5]='qol'
   null.append({'page':'toy','tokens':ws[:]});ps=ws[:]
   if i%2==0:ps[4]='qokedy';ps[6]='kedy'
   planted.append({'page':'toy','tokens':ps})
  for flag,rs in [(False,null),(True,planted)]:
   invariant(rs,mode);out,_,_=run(rs,mode,199,67500+trial+100*mi)
   found=any(x['observed']>0 and x['p_search_family']<=.05 for x in out['records'])
   if flag:hit+=found
   else:false+=found
  print('qualification',mode,trial+1,flush=True)
 qualification.append({'mode':mode,'null_flags':false,'null_trials':20,'planted_detections':hit,'planted_trials':20,'pass':false<=4 and hit>=12})
save('QUALIFICATION.json',{'results':qualification,'scope':'Synthetic engineering diagnostics under one generator, not historical or semantic validation.'})
if not all(q['pass'] for q in qualification):raise SystemExit('Engineering gate failed. Manuscript tests not run; no tuning.')

rows=load(inputs[0]);old=load(inputs[1]);prior=next(g for g in old['groups'] if g['id']=='bath')
eligible=[r for r in rows if tuple(r[2:6])==('Balneological','2','B','P') and re.match(r'f\d+',r[1])[0] not in prior['excluded_folios']]
locs={tr:{r[6] for r in eligible if r[0]==tr} for tr in ('H','F')};shared=locs['H']&locs['F']
noticed={('qokedy','kedy'),('qokeedy','keedy')};panels=[]
for ti,tr in enumerate(['H','F']):
 rs=[dict(page=r[1],folio=re.match(r'f\d+',r[1])[0],locator=r[6],tokens=r[7]) for r in eligible if r[0]==tr and r[6] in shared]
 events=[];byfolio=collections.defaultdict(list)
 for r in rs:byfolio[r['folio']].append(r['tokens'])
 for ri,r in enumerate(rs):
  ws=r['tokens']
  for i,w in enumerate(ws):
   if w!='qol':continue
   l=ws[i-1] if i else '#EDGE';rr=ws[i+1] if i+1<len(ws) else '#EDGE'
   if l in {p for p,b in noticed}|{b for p,b in noticed} or rr in {p for p,b in noticed}|{b for p,b in noticed}:events.append(dict(r,ordinal=i+1,left=l,right=rr))
 for mi,mode in enumerate(['exact_slot','within_line']):
  invariant(rs,mode);out,scores,bs=run(rs,mode,1999,6701+2*ti+mi)
  for rec in out['records']:rec['p_four_panels']=min(1,rec['p_search_family']*4)
  out.update(reading=tr,lines=len(rs),folios=len(byfolio),noticed_events=events)
  chosen=[rec for rec in out['records'] if {tuple(p) for p in rec['pairs']}==noticed];assert len(chosen)==1
  out['noticed_result']=chosen[0];idx=[i for i,p in enumerate(out['pairs']) if tuple(p) in noticed]
  folios={f:int(directional(ls,[tuple(out['pairs'][i]) for i in idx])[0].sum()) for f,ls in byfolio.items()}
  out['noticed_folio_D']=folios
  np.savez_compressed(R/(tr+'-'+mode+'-null.npz'),pair_scores=scores)
  panels.append(out);print(tr,mode,chosen[0],out['mobility'],flush=True)
save('RESULTS.json',{'protocol':protocol,'qualification':qualification,'panels':panels})
save('SUMMARY.json',[dict(reading=p['reading'],mode=p['mode'],pairs=len(p['pairs']),family_size=p['family_size'],noticed=p['noticed_result'],mobility=p['mobility'],folio_D=p['noticed_folio_D']) for p in panels])
save('VERIFICATION.json',{'freeze_integrity':'pass','shuffle_invariants':'pass','semantic_inference':'none','visual_review':'not performed'})
