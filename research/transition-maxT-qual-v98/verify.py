from pathlib import Path
import collections,hashlib,json,math
from fractions import Fraction
import numpy as np
from scipy.stats import rankdata,binomtest
from engine import build,draw,invariants,score_batch
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
q=load(R/'QUALIFICATION.json');assert q['manuscript_rescore']=='NOT PERFORMED'
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
for n,h in load(P/'opening-order-audit-v75/FREEZE.json').items():assert hashlib.sha256((P/'opening-order-audit-v75'/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
source=load(P/'transition-control-v96/RESULTS.json');nulls=load(P/'transition-control-v96/NULL-DISTRIBUTIONS.json');v97=load(P/'transition-power-v97/RESULTS.json');old=load(P/'opening-order-audit-v75/RESULTS.json');meta={p['panel_index']:p for p in old['panels']};raw=load(P/'frequency-atlas-v48/rows.json')
import importlib.util
spec=importlib.util.spec_from_file_location('power',P/'transition-power-v97/engine.py');power=importlib.util.module_from_spec(spec);spec.loader.exec_module(power)
checked=0;nullranks=[]
for rec in q['records']:
 bank=rec['bank'];idx=rec['original_panel_index'];view=rec['view'];file=R/f'bank-{bank}-panel-{idx:02d}-{view}.npz';a=np.load(file);pilot=a['pilot_scores'];cal=a['calibration_scores'];mu=a['mean'];sd=a['sd'];mx=a['maxima'];N=len(cal)
 assert pilot.shape==(2048,meta[idx]['class_pairs']) and cal.shape==(4096,meta[idx]['class_pairs']);assert np.allclose(pilot.mean(axis=0),mu,rtol=1e-12,atol=1e-12) and np.allclose(np.sqrt(pilot.var(axis=0)+1),sd,rtol=1e-12,atol=1e-12)
 replay=np.empty(N)
 for lo in range(0,N,128):replay[lo:lo+128]=np.max(np.abs((cal[lo:lo+128]-mu)/sd),axis=1)
 assert np.array_equal(replay,mx)
 original=meta[idx];key=tuple(original[k] for k in ['section','hand','variety','format']);rr=[r for r in raw if tuple(r[2:6])==key];other={r[6] for r in rr if r[0]!=original['reading']};rows=[dict(page=r[1],folio=r[1].split('.')[0],locator=r[6],tokens=r[7]) for r in rr if r[0]==original['reading'] and r[6] in other]
 p,spans=build(rows);assert p['labels']==original['labels'];batch=draw(p,spans,256,np.random.default_rng(98000+1000*(bank-1)+idx));invariants(batch,p,spans);sc=score_batch(batch,p);assert np.array_equal(sc[view],pilot[:256])
 col=original['reported_rules'][0]['column'];sign=original['reported_rules'][0]['sign'];nullrec=next(x for x in nulls if x['original_panel_index']==idx and x['view']==view);null={int(k):int(v,16) for k,v in nullrec['weights_hex'].items()};T=sum(null.values());mean=Fraction(sum(x*n for x,n in null.items()),T);fwd=set();rev=set();pvals={}
 for d in null:
  z=abs((d-mu[col]*sign)/sd[col]);pv=min(1,28*(1+np.count_nonzero(mx>=z-1e-12))/(N+1));pvals[d]=pv
  if pv<=.05:
   if Fraction(d)>mean:fwd.add(d)
   elif Fraction(d)<mean:rev.add(d)
 assert sorted(fwd)==rec['forward_region'] and sorted(rev)==rec['reverse_region'];nullsize=Fraction(sum(n for d,n in null.items() if d in fwd or d in rev),T);assert float(nullsize)==rec['exact_focal_null_size']
 ranks=28*rankdata(-mx,method='max')/N;nullranks.append(ranks)
 assert rec['gates']['rank_bound']==(np.count_nonzero(ranks<=.05)<=math.floor(.05*N/28))
 regions=dict(mean=mean,variance=power.moments(null)[2],forward=fwd,reverse=rev);layout=next(x for x in v97['layouts'] if x['original_panel_index']==idx and x['view']==view);ss=next(v for z in source['panels'] if z['original_panel_index']==idx for v in z['views'] if v['view']==view)['span_records'];cases=[c for c in q['all_power_cases'] if c['bank']==bank and c['original_panel_index']==idx and c['view']==view]
 for coverage in layout['coverage']:
  selected={(s['locator'],s['start_ordinal']) for s in coverage['selected']};chosen={0:1};remaining={0:1}
  for s in ss:
   hist={int(k):int(n,16) for k,n in s['score_support'].items()}
   if (s['locator'],s['start_ordinal']) in selected:chosen=power.convolve(chosen,hist)
   else:remaining=power.convolve(remaining,hist)
  assert power.convolve(chosen,remaining)==null
  for c in [c for c in cases if c['coverage']==coverage['fraction']]:
   r=Fraction(c['weight_ratio']);r=1/r if c['direction']=='reverse' else r;alt=power.convolve(power.tilt_integer(chosen,r),remaining);out=power.evaluate(alt,regions,c['direction']);assert all(c[k]==v for k,v in out.items());checked+=1
 primary=[c for c in cases if c['coverage']=='1' and c['direction']=='forward'];p15=next(c['correct_direction_power'] for c in primary if c['weight_ratio']=='3/2');p2=next(c['correct_direction_power'] for c in primary if c['weight_ratio']=='2');assert rec['gates']['moderate_power']==(p15>=.8) and rec['gates']['strong_power']==(p2>=.9) and rec['passes']==all(rec['gates'].values())
 print('verified',bank,idx,view,flush=True)
assert len(q['records'])==8 and q['status']=='FAIL' and q['robustness_banks_not_run']==[2,3]
verification=dict(frozen_sources_methods_and_effects='pass',computational_sampler_qualification='PASS',full_opening_family_columns_preserved='pass',regenerated_actual_first_batches='all four panels/both views exactly reproduce pilot rows; transitions/words/endpoints/unknowns preserved',all_calibration_maxima_replayed='pass',pilot_independent_from_calibration='disjoint generated row banks',critical_regions_and_focal_null_size='pass',exact_conditional_power_cases_replayed=checked,stageA_power_gates='FAIL, correctly stops StageB',remaining_banks='2 and3 NOT RUN',original_source_arrangement_tested=False,manuscript_rescore='NOT PERFORMED',browser_visual_review='not performed; prior local-file policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(verification,indent=2),encoding='utf-8');print('Qualification failure independently verified; no source rescore.')
