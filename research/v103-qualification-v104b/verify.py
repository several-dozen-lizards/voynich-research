from pathlib import Path
from fractions import Fraction
import hashlib,json,math,zipfile
import numpy as np
from core import build,spans,scores,minima,dp,target,rational
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
freeze=load(R/'FREEZE.json')
for n,h in freeze['local_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
for n,h in freeze['historical_sha256'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
if not (R/'QUALIFICATION.json').exists():
 assert (R/'EXECUTION-FAILURE.json').exists()
 print('Frozen execution failure retained; incomplete controls; scoring closed.')
 raise SystemExit(0)
q=load(R/'QUALIFICATION.json');panels=load(R/'FAMILY.json');rows=next(x['rows'] for x in load(R/'FIXTURES.json') if x['name']=='positive32');total_columns=0;replayed=0
for panel in panels:
 for neutral in (False,True):
  p=build(rows,panel['labels'],neutral)
  with zipfile.ZipFile(R/f'panel-{panel["panel_index"]:02d}-{int(neutral)}-calibration.npz') as z:
   with z.open('column_group.npy') as fh:mapping=np.lib.format.read_array(fh,allow_pickle=False)
   assert np.array_equal(mapping,p['column_group']);representative=[int(np.flatnonzero(mapping==j)[0]) for j in range(len(p['groups']))];blocks=[]
   with z.open('scores.npy') as fh:
    version=np.lib.format.read_magic(fh);shape,fortran,dtype=np.lib.format.read_array_header_1_0(fh);assert shape==(4096,panel['class_pairs']) and not fortran
    for lo in range(0,4096,32):
     size=min(32,4096-lo);block=np.frombuffer(fh.read(size*shape[1]*dtype.itemsize),dtype=dtype).reshape(size,shape[1]);g=block[:,representative];assert np.array_equal(block,g[:,mapping]);blocks.append(g.copy())
   gs=np.concatenate(blocks)
  mm=minima(gs,p);assert [rational(x) for x in mm]==load(R/f'panel-{panel["panel_index"]:02d}-{int(neutral)}-minima.json')
  ps=scores((spans(rows),),p);_,j,sign=target(p);pv=dp.calibrated(p['groups'][j]['tails'][int(ps[0,j])],mm)
  r=next(x for x in q['records'] if x.get('panel_index')==panel['panel_index'] and x.get('fixture')=='positive32' and x.get('view')==('non_target_middle' if neutral else 'any_middle'))
  assert r['positive_adjusted_p']==rational(pv);assert r['positive_pass']==(r['positive_forward'] and pv<=Fraction(1,20));total_columns+=panel['class_pairs'];replayed+=1
assert len([x for x in q['records'] if 'panel_index' in x])==4*7*2
assert q['status']==('PASS_STAGE1_CONTROLS_ONLY' if all(x['pass_gate'] for x in q['records']) else 'FAIL_STAGE1')
old=load(P/'transition-maxT-qual-v98/QUALIFICATION.json');assert old['status']=='FAIL' and old['robustness_banks_not_run']==[2,3]
result=dict(frozen_files='PASS',all_family_columns_in_each_saved_bank='PASS',column_views_verified=total_columns,calibration_banks_replayed=replayed,all_minima_and_positive_adjustments='PASS',control_records=56,gate_status_replay='PASS',actual_layout_power='NOT RUN',manuscript_score='NOT COMPUTED',v98='FAIL unchanged; banks2/3 unrun')
(R/'VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
