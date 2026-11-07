from pathlib import Path
import collections,hashlib,json
import numpy as np
from engine import calibration
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');old=load(P/'middle-contexts-v72/RESULTS.json')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
for n,h in load(R/'SENSITIVITY-FREEZE.json').items():assert hashlib.sha256((R/'FREEZE.json' if n=='original_FREEZE.json' else R/n).read_bytes()).hexdigest()==h
assert len(d['panels'])==2 and all(p['mode']=='within_line' for p in d['panels'])
toy=np.array([[2,-1,1,1,3,-4],[1,1,0,2,-1,-1],[0,-2,1,-2,1,1],[2,0,-1,2,-3,1],[-1,2,1,1,2,-3]],dtype=np.int32)
tail=[]
for j in range(6):
 v=toy[:,j];tail.append(np.array([min(np.mean(v>=x),np.mean(v<=x)) for x in v]))
minimum=np.min(tail,axis=0)
for j,x in enumerate(calibration(toy)):
 assert x['p_upper']==np.mean(toy[:,j]>=toy[0,j]) and x['p_lower']==np.mean(toy[:,j]<=toy[0,j])
 assert x['p_triad_family']==np.mean(minimum<=tail[j][0]+1e-14)
caution=[]
for p in d['panels']:
 tr=p['reading'];a=np.load(R/(tr+'-within_line-null.npz'))['scores'];assert a.shape==(5000,6)
 for x,y in zip(p['tests'],calibration(a)):
  assert all(x[k]==v for k,v in y.items());assert x['p_four_panels']==min(1,4*x['p_triad_family'])
 for key,c in p['directed_cells'].items():assert c==old['readings'][tr]['directed_target_pairs'][key]['count']
 count=collections.Counter(e['first']+' '+e['second'] for e in d['observed'][tr]['events']);assert all(count[k]==v for k,v in p['directed_cells'].items())
 assert [sum(v[j] for v in d['observed'][tr]['folio_contrasts'].values()) for j in range(6)]==a[0].tolist()
 q=d['observed'][tr]['qokedy_profile'];assert all(not(e['left']==e['right']=='shedy') for e in q['events'])
 x=p['tests'][4];caution.append(dict(reading=tr,calibration_rows=5000,pooled_minP_rows_at_least_as_extreme=round(5000*x['p_triad_family']),p_triad_family=x['p_triad_family'],p_four_panels=x['p_four_panels'],note='Monte Carlo point estimate. Pooled rank indicators are dependent; do not attach a naive independent-binomial confidence interval to this minP result. F=.044 is close to .05; no adaptive resampling or stable-pass claim.'))
(R/'MC-CAUTION.json').write_text(json.dumps(caution,indent=2),encoding='utf-8')
v=load(R/'VERIFICATION.json');v.update(original_and_sensitivity_freeze='pass',independent_small_matrix_tail_rank_minP='pass',saved_sensitivity_matrix_replay='all 12 contrasts match',original_v72_directed_cells='pass',folio_and_source_pair_conservation='pass',primary_status='not run; original engineering failure not waived',monte_carlo_caution='MC-CAUTION.json',browser_visual_review='not performed; prior file URL policy block respected')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print('Both sensitivity matrices, all original cells and independent minP checks verified. Primary remains unrun.')
