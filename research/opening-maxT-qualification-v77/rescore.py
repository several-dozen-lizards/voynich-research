from pathlib import Path
import hashlib,json
import numpy as np
from method import maximums,target_result
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
q=load(R/'QUALIFICATION.json')
if q['status']!='PASS':raise SystemExit('Qualification failed: no manuscript score matrices opened.')
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['method.py','qualify.py','rescore.py'] else P/n).read_bytes()).hexdigest()==h
old=load(P/'opening-order-audit-v75/RESULTS.json');panels=[]
for p in old['panels']:
 idx=p['panel_index'];file=P/'opening-order-audit-v75'/f'panel-{idx:02d}-null.npz';scores=np.load(file)['scores'];assert scores.shape==(5000,p['class_pairs']);mean,sd,mx=maximums(scores);rules=[]
 for original in p['reported_rules']:
  rules.append(dict(A=original['A'],B=original['B'],forward=original['forward'],reverse=original['reverse'],**target_result(scores,original['column'],original['sign'],mx,mean,sd,14)))
 panels.append(dict(panel_index=idx,reading=p['reading'],section=p['section'],hand=p['hand'],variety=p['variety'],format=p['format'],hand_ambiguous=p['hand_ambiguous'],lines=p['lines'],folios=p['folios'],class_pairs=p['class_pairs'],rules=rules,source_matrix_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),maxT_minimum_possible_panel_p=float(np.min([min(1,14*np.mean(mx>=v-1e-12)) for v in [mx.max()]]))))
 np.savez_compressed(R/(f'panel-{idx:02d}-maxT.npz'),mean=mean,sd=sd,maxima=mx);print(idx+1,rules[0],flush=True)
save('RESULTS.json',dict(qualification_status='PASS before manuscript matrix access',method=load(R/'PROTOCOL.json'),panels=panels,source_events_reference='../opening-order-audit-v75/RESULTS.json',original_failures_reference='../opening-order-audit-v75/FAMILY-PRECISION.json'))
save('SUMMARY.json',[dict(section=p['section'],hand=p['hand'],variety=p['variety'],reading=p['reading'],principal=p['rules'][0]) for p in panels])
