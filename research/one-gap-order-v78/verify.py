from pathlib import Path
import collections,hashlib,importlib.util,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
d=load(R/'RESULTS.json');q=load(R/'QUALIFICATION.json');assert q['status']=='PASS'
for n,h in load(R/'FREEZE.json').items():assert hashlib.sha256((R/n if n in ['engine.py','qualify.py','run.py'] else P/n).read_bytes()).hexdigest()==h
for n,h in load(P/'opening-order-audit-v75/FREEZE.json').items():assert hashlib.sha256((P/'opening-order-audit-v75'/n if n in ['engine.py','run.py'] else P/n).read_bytes()).hexdigest()==h
spec=importlib.util.spec_from_file_location('maxT',P/'opening-maxT-qualification-v77/method.py');method=importlib.util.module_from_spec(spec);spec.loader.exec_module(method)
raw=load(P/'frequency-atlas-v48/rows.json');source={(r[0],r[6]):r for r in raw};old=load(P/'opening-order-audit-v75/RESULTS.json');checked=0
for panel in d['panels']:
 idx=panel['original_panel_index'];tr=panel['reading'];mode=panel['view'];a=np.load(R/(f'panel-{idx:02d}-{mode}-null.npz'));scores=a['scores'];assert scores.shape==(5000,panel['class_pairs'])
 mean,sd,mx=method.maximums(scores);assert np.array_equal(mean,a['mean']) and np.array_equal(sd,a['sd']) and np.array_equal(mx,a['maxima'])
 prev=next(p for p in old['panels'] if p['panel_index']==idx)['reported_rules'][0];calc=method.target_result(scores,prev['column'],prev['sign'],mx,mean,sd,28);assert calc==panel['result'];assert calc['observed_D']==panel['cells']['forward']-panel['cells']['reverse']
 obs=next(o for o in d['observed'] if o['original_panel_index']==idx);ev=[e for e in obs['events'] if mode=='any_middle' or e['neutral_middle']]
 assert sum(e['orientation']=='forward' for e in ev)==panel['cells']['forward'] and sum(e['orientation']=='reverse' for e in ev)==panel['cells']['reverse']
 for e in ev:
  ws=source[(tr,e['locator'])][7];i=e['ordinal']-1;assert ws==e['tokens'] and ws[i:i+3]==[e['first'],e['middle'],e['last']] and None not in ws[i:i+3];checked+=1
 prefix='' if mode=='any_middle' else 'neutral_';assert sum(v[prefix+'forward'] for v in obs['folios'].values())==panel['cells']['forward'];assert sum(v[prefix+'reverse'] for v in obs['folios'].values())==panel['cells']['reverse']
 # Independent literal source-token count with fixed hand/section/variety/format.
 rr=[r for r in raw if tuple(r[2:6])==(panel['section'],panel['hand'],panel['variety'],panel['format'])];other={r[6] for r in rr if r[0]!=tr};f=b=0
 for r in rr:
  if r[0]!=tr or r[6] not in other:continue
  for x,m,y in zip(r[7],r[7][1:],r[7][2:]):
   if x is None or m is None or y is None or (mode=='non_target_middle' and m.startswith(('sh','qok'))):continue
   f+=x.startswith('sh') and y.startswith('qok');b+=x.startswith('qok') and y.startswith('sh')
 assert (f,b)==(panel['cells']['forward'],panel['cells']['reverse']);print('verified',idx,mode,flush=True)
v=dict(frozen_sources_and_methods='pass',new_gap_counter_qualification='PASS before manuscript scoring',saved_score_maximum_and_tail_replay='all eight view/panel matrices',independent_literal_gap_counts='pass',source_event_views_checked=checked,folio_and_middle_exclusions='pass',browser_visual_review='not performed; existing file URL policy block respected',interpretation='Gap result cannot alone separate grammar from chained local transitions.')
(R/'VERIFICATION.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print('All gap source events, exclusions, and eight null results verified.')
