from pathlib import Path
import collections,hashlib,json,math
from fractions import Fraction
from engine import convolve,tilt_integer,moments
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');source=load(P/'transition-control-v96/RESULTS.json');nulls=load(P/'transition-control-v96/NULL-DISTRIBUTIONS.json')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
assert len(d['power_cases'])==312 and d['manuscript_rescore']=='NOT PERFORMED'
checked=0
for layout in d['layouts']:
 idx=layout['original_panel_index'];view=layout['view'];rec=next(n for n in nulls if n['original_panel_index']==idx and n['view']==view);null={int(k):int(v,16) for k,v in rec['weights_hex'].items()};T=sum(null.values());moment=sum(k*n for k,n in null.items());mu=Fraction(moment,T);budget=layout['correction']
 # Independently form rejection regions with direct rational distance tails.
 fwd=set();rev=set()
 for x in null:
  tail=sum(n for z,n in null.items() if abs(Fraction(z)-mu)>=abs(Fraction(x)-mu))
  if tail*budget*20<=T:
   if Fraction(x)>mu:fwd.add(x)
   elif Fraction(x)<mu:rev.add(x)
 assert sorted(fwd)==layout['forward_region'] and sorted(rev)==layout['reverse_region']
 p=next(p for p in source['panels'] if p['original_panel_index']==idx);v=next(v for v in p['views'] if v['view']==view);spans=v['span_records'];cases=[c for c in d['power_cases'] if c['original_panel_index']==idx and c['view']==view]
 for coverage in layout['coverage']:
  selected={(s['locator'],s['start_ordinal']) for s in coverage['selected']};var=[]
  for s in spans:
   if len(s['score_support'])>1:
    rank=hashlib.sha256(f"v97|{idx}|{view}|{s['locator']}|{s['start_ordinal']}".encode()).hexdigest();var.append((rank,s['locator'],s['start_ordinal']))
  var.sort();expected={(loc,start) for rank,loc,start in var[:math.ceil(Fraction(coverage['fraction'])*len(var))]};assert selected==expected
  chosen={0:1};remaining={0:1}
  for s in spans:
   hist={int(k):int(w,16) for k,w in s['score_support'].items()}
   if (s['locator'],s['start_ordinal']) in selected:chosen=convolve(chosen,hist)
   else:remaining=convolve(remaining,hist)
  assert convolve(chosen,remaining)==null
  for c in [c for c in cases if c['coverage']==coverage['fraction']]:
   r=Fraction(c['applied_ratio']);alt=convolve(tilt_integer(chosen,r),remaining);total=sum(alt.values());positive=sum(w for x,w in alt.items() if x in fwd);negative=sum(w for x,w in alt.items() if x in rev);right=positive if c['direction']=='forward' else negative if c['direction']=='reverse' else positive+negative
   assert hex(right)==c['power_numerator_hex'] and hex(total)==c['alternative_total_hex'];assert float(Fraction(right,total))==c['correct_direction_power']
   mean=Fraction(sum(x*w for x,w in alt.items()),total);assert float(mean)==c['alternative_mean'] and float(mean-mu)==c['mean_shift_D']
   if c['direction']=='null':assert alt==null and Fraction(positive+negative,total)<=Fraction(1,20*budget)
   if coverage['fraction']=='1':
    direct=tilt_integer(null,r);den=sum(direct.values());assert all(Fraction(w,total)==Fraction(direct[x],den) for x,w in alt.items())
   checked+=1
 primary=[c for c in cases if c['coverage']=='1' and c['direction']=='forward'];p15=next(c['correct_direction_power'] for c in primary if c['weight_ratio']=='3/2');p2=next(c['correct_direction_power'] for c in primary if c['weight_ratio']=='2');assert layout['moderate_gate']==(p15>=.8) and layout['strong_gate']==(p2>=.9)
 print('verified',idx,view,flush=True)
verification=dict(frozen_effects_sources_and_scripts='pass',arithmetic_qualification='PASS before actual-layout power',power_cases_exactly_replayed=checked,independent_rational_rejection_regions='pass',hash_selected_span_membership='pass',selected_remaining_null_recomposition='pass',full_coverage_pooled_tilt_equivalence='pass',null_exact_size_bound='pass',observed_manuscript_scores_retested=False,manuscript_rescore='NOT PERFORMED',browser_visual_review='not performed; prior local-file policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(verification,indent=2),encoding='utf-8');print('All312 power cases and benchmark failures verified; no observed-score rescore.')
