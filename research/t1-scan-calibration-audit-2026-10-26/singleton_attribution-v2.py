import sys,os
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json,collections
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
s=importlib.util.spec_from_file_location('c',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
rows=read(OLD/'SUPPORT-ROWS.json');trials=read(OLD/'CONTROL-TRIALS.json');ml=collections.defaultdict(int)
for r in read(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines']:ml[(r['task_id'],r['block_id'])]=max(ml[(r['task_id'],r['block_id'])],r['line_number'])
result={}
for reading,rr in rows.items():
 ix=[i for i,r in enumerate(rr) if r['folio']=='f80v' and r['length_bin']=='short' and r['label']=='FG'];assert sum(rr[i]['n'] for i in ix)==1
 counts=collections.Counter();details=[]
 for t in trials:
  if t['reading']!=reading or t['scenario']!='independent-null':continue
  Y=c.simulate(rr,t['scenario'],reading,t['trial'],ml);singleton=Y[ix].sum(axis=0);flagged=[j for j,p in enumerate(t['scan_holm']) if p is not None and p<.05]
  counts['datasets']+=1;counts['flagged_families']+=bool(flagged);counts['flagged_classes']+=len(flagged);counts['flagged_classes_matching_singleton']+=sum(singleton[j]==1 for j in flagged);counts['families_with_singleton_matching_flag']+=any(singleton[j]==1 for j in flagged)
  details.append(dict(trial=t['trial'],flagged=[c.m.CLASSES[j] for j in flagged],singleton_classes=[c.m.CLASSES[j] for j in range(17) if singleton[j]]))
 result[reading]=dict(counts={k:int(v) for k,v in counts.items()},details=details)
(P/'SINGLETON-ATTRIBUTION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v['counts'] for k,v in result.items()},indent=2))
