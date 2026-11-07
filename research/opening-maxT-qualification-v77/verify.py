from pathlib import Path
import hashlib,json
import numpy as np
from scipy.stats import beta
from method import maximums,target_result,rotation_p
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
q=load(R/'QUALIFICATION.json')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['method.py','qualify.py','rescore.py'] else P/n).read_bytes()).hexdigest()==h
for bank in q['banks']:
 a=np.load(R/(f'bank-{bank["bank"]:02d}-diagnostics.npz'));mx=a['panel_maxima'];assert mx.shape==(14,4096)
 ps=np.array([rotation_p(x,14) for x in mx]);assert np.count_nonzero(np.any(ps<=.05,axis=0))==bank['global_null_flags']
 assert bank['passes']==all(bank[k] for k in ['null_gate','precision_gate','strong_power_gate','paired_gate'])
 assert bank['strong_power_gate']==all(v['detections']['8']/v['trials']>=.9 for v in bank['dose_results'])
 assert bank['precision_gate']==all(v<=.01 for v in bank['minimum_achievable_panel_adjusted_p'])
v=dict(frozen_inputs_and_method='pass',qualification_bank_replay='pass',qualification_status=q['status'],manuscript_rescore='not performed if qualification failed',semantic_qualification='not claimed',visual_review='not performed')
if q['status']=='PASS' and (R/'RESULTS.json').exists():
 d=load(R/'RESULTS.json');old=load(P/'opening-order-audit-v75/RESULTS.json');unc=[]
 assert len(d['panels'])==len(old['panels'])==14
 for p,original in zip(d['panels'],old['panels']):
  idx=p['panel_index'];file=P/'opening-order-audit-v75'/f'panel-{idx:02d}-null.npz';assert hashlib.sha256(file.read_bytes()).hexdigest()==p['source_matrix_sha256'];scores=np.load(file)['scores']
  mean,sd,mx=maximums(scores);saved=np.load(R/(f'panel-{idx:02d}-maxT.npz'))
  assert np.array_equal(mean,saved['mean']) and np.array_equal(sd,saved['sd']) and np.array_equal(mx,saved['maxima'])
  for x,prev in zip(p['rules'],original['reported_rules']):
   r=target_result(scores,prev['column'],prev['sign'],mx,mean,sd,14);assert all(x[k]==z for k,z in r.items());assert x['forward']==prev['forward'] and x['reverse']==prev['reverse'] and x['observed_D']==prev['observed_D']
   assert x['observed_D']==x['forward']-x['reverse']
  # Independent direct transform on selected columns and rows (not the chunk helper).
  col=original['reported_rules'][0]['column'];x=scores[:,col].astype(float);assert np.isclose(mean[col],x.mean(),rtol=1e-12,atol=1e-12) and np.isclose(sd[col],np.sqrt(x.var()+1),rtol=1e-12,atol=1e-12)
  z=abs((x[0]-x.mean())/np.sqrt(x.var()+1));tail=int(np.sum(mx[1:]>=z-1e-12));assert tail==p['rules'][0]['max_tail_exceedances']
  # Approximate MC interval: symmetric estimated centering/scaling couples rows.
  # Binomial bounds are explicitly descriptive, not exact for this plug-in maxT.
  n=4999;lo=0. if tail==0 else float(beta.ppf(.025,tail,n-tail+1));hi=1. if tail==n else float(beta.ppf(.975,tail+1,n-tail))
  unc.append(dict(panel_index=idx,reading=p['reading'],hand=p['hand'],section=p['section'],max_tail_exceedances=tail,shuffles=n,approximate_adjusted_tail_interval95=[min(1,14*lo),min(1,14*hi)],limitation='Descriptive binomial MC approximation only: pooled mean/scale couple rows. Not an exact interval or independent replication. No adaptive extra shuffles.'))
  print('verified rescore',idx+1,flush=True)
 (R/'MC-PRECISION.json').write_text(json.dumps(unc,indent=2),encoding='utf-8');v.update(manuscript_rescore='all 14 original panels; no change to scores or candidate family',saved_maxT_and_target_tail_replay='pass',original_counts_and_directions='unchanged',MC_precision='MC-PRECISION.json with dependency caveat')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print('Qualification and available rescore verification complete.')
