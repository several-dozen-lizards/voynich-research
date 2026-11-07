from pathlib import Path
import collections,hashlib,json
import numpy as np
from engine import belongs,calibrate,QUESTIONS,prepare
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');raw=load(P/'frequency-atlas-v48/rows.json');source={(r[0],r[6]):r for r in raw}
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
precision=[]
for p in d['panels']:
 idx=p['panel_index'];tr=p['reading'];scores=np.load(R/(f'panel-{idx:02d}-null.npz'))['scores'];assert scores.shape==(5000,p['class_pairs'])
 minimum,tails=calibrate(scores);floor=float(np.mean(minimum<=1/5000+1e-14));q=p['reported_rules'][0]
 precision.append(dict(panel_index=idx,section=p['section'],hand=p['hand'],variety=p['variety'],reading=tr,comparisons=p['class_pairs'],calibration_rows=5000,min_rank_tail=1/5000,minimum_achievable_family_p_in_this_calibration=floor,minimum_achievable_all_panel_p=min(1,floor*d['panel_count']),principal_forward_null_exceedances=round(q['p_upper']*5000)-1,principal_at_best_possible_tail=min(tails[q['column']][:2])==1/5000,note='Observed finite-rank calibration resolution; a floor above .05 makes this full screen incapable of accepting even the smallest observed tail. Do not interpret nonpassing as absence of order.'))
 for x in p['reported_rules']:
  col=x['column'];sign=x['sign'];v=scores[:,col].astype(np.int32)*sign;up,lo,t=tails[col]
  if sign<0:up,lo=lo,up
  assert x['observed_D']==int(v[0]) and x['p_upper']==up
  assert x['p_raw_two_sided']==min(1,2*t) and x['p_search_family']==float(np.mean(minimum<=t+1e-14))
  assert x['p_all_panels']==min(1,x['p_search_family']*d['panel_count'])
  assert x['null_mean']==float(v[1:].mean())
 ev=next(s for s in d['source_events'] if s['panel_index']==idx);forward=sum(e['orientation']=='forward' for e in ev['events']);reverse=sum(e['orientation']=='reverse' for e in ev['events']);assert (forward,reverse)==(q['forward'],q['reverse'])
 assert sum(z['forward'] for z in ev['folios'].values())==forward and sum(z['reverse'] for z in ev['folios'].values())==reverse
 for e in ev['events']:
  assert source[(tr,e['locator'])][7]==e['tokens'];i=e['ordinal']-1;assert e['tokens'][i:i+2]==[e['first'],e['second']]
 # Independent direct count for every reported opening relation on shared loci.
 rs=[r for r in raw if r[0]==tr and tuple(r[2:6])==(p['section'],p['hand'],p['variety'],p['format'])]
 other={r[6] for r in raw if r[0]!=tr and tuple(r[2:6])==(p['section'],p['hand'],p['variety'],p['format'])}
 rs=[r for r in rs if r[6] in other]
 # Independent shuffle-invariant check on the encoded representation.
 enc=prepare([dict(page=r[1],folio=r[1].split('.')[0],locator=r[6],tokens=r[7]) for r in rs]);a=enc['original'].copy();rng=np.random.default_rng(75999+idx)
 for b in enc['buckets']:
  a[b]=rng.permutation(a[b]);assert collections.Counter(a[b])==collections.Counter(enc['original'][b])
 assert np.array_equal(a<0,enc['original']<0)
 offset=0
 for r in rs:
  n=len(r[7]);assert a[offset]==enc['original'][offset] and a[offset+n-1]==enc['original'][offset+n-1]
  assert collections.Counter(a[offset:offset+n])==collections.Counter(enc['original'][offset:offset+n]);offset+=n
 for x in p['reported_rules']:
  f=b=0
  for r in rs:
   for a,z in zip(r[7],r[7][1:]):
    if a is None or z is None:continue
    f+=belongs(a,x['A']) and belongs(z,x['B']);b+=belongs(a,x['B']) and belongs(z,x['A'])
  assert (f,b)==(x['forward'],x['reverse'])
 print('verified',idx+1,'floor',floor,flush=True)
(R/'FAMILY-PRECISION.json').write_text(json.dumps(precision,indent=2),encoding='utf-8')
v=load(R/'VERIFICATION.json');v.update(saved_matrix_tail_and_family_replay='all reported rules in all panels',source_and_folio_counts='pass',independent_class_relation_counts='pass',precision_audit='FAMILY-PRECISION.json; finite-rank acceptance floor explicit',browser_visual_review='not performed; existing local-file URL policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print('Source, numerical replay and family-resolution audit complete.')
