from pathlib import Path
import collections,hashlib,importlib.util,json,math
from fractions import Fraction
import numpy as np
from engine import loose_distribution
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('power',P/'transition-power-v97/engine.py');power=importlib.util.module_from_spec(spec);spec.loader.exec_module(power)
d=load(R/'RESULTS.json');v98=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');source=load(P/'transition-control-v96/RESULTS.json');nulls=load(P/'transition-control-v96/NULL-DISTRIBUTIONS.json');v97=load(P/'transition-power-v97/RESULTS.json');loosenulls=load(R/'LOOSE-NULLS.json');old=load(P/'opening-order-audit-v75/RESULTS.json')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
assert v98['status']=='FAIL' and v98['robustness_banks_not_run']==[2,3] and d['manuscript_rescore']=='NOT PERFORMED';assert len(d['correction_cases'])==1248 and len(d['constraint_model_cases'])==312
checked=0
for layout in d['layouts']:
 idx=layout['original_panel_index'];view=layout['view'];meta=next(p for p in old['panels'] if p['panel_index']==idx)['reported_rules'][0];bank=np.load(P/'transition-maxT-qual-v98'/f'bank-1-panel-{idx:02d}-{view}.npz');mu=bank['mean'][meta['column']]*meta['sign'];sd=bank['sd'][meta['column']];mx=bank['maxima'];tz=np.abs((bank['calibration_scores'][:,meta['column']]*meta['sign']-mu)/sd);N=len(mx)
 nrec=next(n for n in nulls if n['original_panel_index']==idx and n['view']==view);strict={int(k):int(n,16) for k,n in nrec['weights_hex'].items()};T,mean,var=power.moments(strict);regimes={name:dict(mean=mean,variance=var,forward=set(),reverse=set()) for name in ['target_only','target_x28','search_only','search_x28']}
 for x in strict:
  z=abs((x-mu)/sd);single=(1+np.count_nonzero(tz>=z-1e-12))/(N+1);search=(1+np.count_nonzero(mx>=z-1e-12))/(N+1)
  for name,pval in [('target_only',single),('target_x28',min(1,single*28)),('search_only',search),('search_x28',min(1,search*28))]:
   if pval<=.05 and Fraction(x)!=mean:regimes[name]['forward' if Fraction(x)>mean else 'reverse'].add(x)
 for side in ['forward','reverse']:
  assert regimes['search_x28'][side]<=regimes['search_only'][side]<=regimes['target_only'][side];assert regimes['search_x28'][side]<=regimes['target_x28'][side]<=regimes['target_only'][side]
 srec=next(v for p in source['panels'] if p['original_panel_index']==idx for v in p['views'] if v['view']==view)['span_records'];prior_layout=next(l for l in v97['layouts'] if l['original_panel_index']==idx and l['view']==view);cases=[c for c in d['correction_cases'] if c['original_panel_index']==idx and c['view']==view]
 for coverage in prior_layout['coverage']:
  chosen={(s['locator'],s['start_ordinal']) for s in coverage['selected']};a={0:1};b={0:1}
  for s in srec:
   hist={int(k):int(n,16) for k,n in s['score_support'].items()}
   if (s['locator'],s['start_ordinal']) in chosen:a=power.convolve(a,hist)
   else:b=power.convolve(b,hist)
  assert power.convolve(a,b)==strict
  basecases=[c for c in v98['all_power_cases'] if c['original_panel_index']==idx and c['view']==view and c['coverage']==coverage['fraction']]
  for c in [c for c in cases if c['coverage']==coverage['fraction']]:
   ratio=Fraction(c['weight_ratio']);ratio=1/ratio if c['direction']=='reverse' else ratio;alt=power.convolve(power.tilt_integer(a,ratio),b);ev=power.evaluate(alt,regimes[c['threshold']],c['direction']);assert all(c[k]==v for k,v in ev.items());checked+=1
   if c['threshold']=='search_x28':
    original=next(x for x in basecases if x['direction']==c['direction'] and x['weight_ratio']==c['weight_ratio']);assert all(original[k]==v for k,v in ev.items())
 loose={0:1};bits=0.;varspans=0
 for s in srec:
  seq=s['classes'];counts=tuple(seq[1:-1].count(i) for i in range(3));hist,calls=loose_distribution(seq[0],seq[-1],counts,view=='non_target_middle',len(seq)==1);expected=1 if len(seq)==1 else math.factorial(len(seq)-2)//math.prod(math.factorial(n) for n in counts);assert sum(hist.values())==expected
  strict_hist={int(k):int(v,16) for k,v in s['score_support'].items()};assert all(v<=hist.get(k,0) for k,v in strict_hist.items());loose=power.convolve(loose,hist);bits+=math.log2(sum(hist.values()))-math.log2(sum(strict_hist.values()));varspans+=len(hist)>1
 saved=next(n for n in loosenulls if n['original_panel_index']==idx and n['view']==view);assert loose=={int(k):int(v,16) for k,v in saved['loose_null_hex'].items()};_,lm,lv=power.moments(loose);assert float(var/lv)==layout['constraints']['retained_variance_fraction'];assert math.isclose(bits,layout['constraints']['removed_log2_class_orders'],rel_tol=1e-12);assert varspans==layout['constraints']['loose_variable_spans']
 sr=power.rejection_regions(strict,1);lr=power.rejection_regions(loose,1)
 for c in [x for x in d['constraint_model_cases'] if x['original_panel_index']==idx and x['view']==view]:
  r=Fraction(c['weight_ratio']);r=1/r if c['direction']=='reverse' else r;alt=power.tilt_integer(loose if c['comparison']=='loose_own_base' else strict,r);reg=sr if c['comparison']=='strict_own_base' else lr;ev=power.evaluate(alt,reg,c['direction']);assert all(c[k]==v for k,v in ev.items());checked+=1
 print('verified',idx,view,flush=True)
verification=dict(frozen_diagnostic_inputs_and_methods='pass',loose_DP_authored_oracle='PASS before diagnostics',power_cases_replayed=checked,correction_region_nesting='pass',unchanged_full_v98_power_cases='all312 exact matches',strict_fiber_subset_of_loose_fiber='pass',span_multinomial_counts_and_loose_null_convolutions='pass',model_mismatch_baselines='preserved, not called calibration error',v98_gates_and_unrun_banks='unchanged FAIL; banks2/3 remain notrun',manuscript_rescore='NOT PERFORMED',browser_visual_review='not performed; prior local-file policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(verification,indent=2),encoding='utf-8');print('All1560 diagnostic power cases verified; gates and manuscript scores untouched.')
