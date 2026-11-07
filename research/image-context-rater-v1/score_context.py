"""Validate real annotations and summarize coverage; no association or semantic scoring."""
import json,sys,collections
from pathlib import Path
R=Path(__file__).resolve().parent
FEATURES={'plant_parts','human_figures','water_or_vessels','stars_or_circles','architecture','other'}
def score(data):
 tasks={t['task_id']:t for t in json.loads((R/'rater-only/TASKS.json').read_text())}
 if data.get('schema')!='image-context-v1' or not str(data.get('rater_id','')).strip() or data.get('prior_exposure') not in ('yes','no'):raise ValueError('Schema, rater ID and prior-exposure declaration required')
 rows=data.get('responses',[])
 if not isinstance(rows,list) or not rows:raise ValueError('Actual nonempty responses required')
 seen=set();counts=collections.Counter();eligible=0
 for row in rows:
  if row.get('task_id') not in tasks:raise ValueError('Unknown task')
  t=tasks[row['task_id']]
  def box(v):
   if not isinstance(v,list) or len(v)!=4 or any(type(x) not in (int,float) for x in v):raise ValueError('Four numeric native coordinates required')
   x,y,w,h=v
   if not (x>=0 and y>=0 and w>0 and h>0 and x+w<=t['native_width']+1 and y+h<=t['native_height']+1):raise ValueError('Region outside canvas')
  box(row.get('line_region'));ident=(row['task_id'],tuple(row['line_region']))
  if ident in seen:raise ValueError('Duplicate exact line rectangle; resolve before scoring')
  seen.add(ident)
  if row.get('context') not in ('pictured','none','unclear'):raise ValueError('Invalid context')
  if row['context']=='pictured':box(row.get('image_region'))
  elif row.get('image_region') is not None:raise ValueError('Non-pictured context must not have an image region')
  if type(row.get('confidence')) is not int or row['confidence'] not in range(4):raise ValueError('Confidence 0..3 required')
  if row.get('recognized') not in ('yes','no'):raise ValueError('Recognition declaration required')
  if set(row.get('features',{}))!=FEATURES or any(v not in ('yes','no','uncertain') for v in row['features'].values()):raise ValueError('Every feature requires yes/no/uncertain')
  if not row.get('description','').strip() or not row.get('ambiguity','').strip():raise ValueError('Description and uncertainty required')
  eligible+=data['prior_exposure']=='no' and row['recognized']=='no';counts[row['context']]+=1
 return dict(status='VALIDATED ANNOTATIONS ONLY; REGISTRATION AND SCIENTIFIC ANALYSIS PENDING',rater_id=data['rater_id'],annotations=len(rows),source_pages=len({r['task_id'] for r in rows}),released_pages=len(tasks),context_counts=dict(counts),exposure_eligible_annotations=eligible,blindness_limit='Self-declaration only; recognition and visible section cannot be erased.',line_registration='Requires independent checked crosswalk. Overlapping boxes may duplicate a physical line; exact-box check alone cannot establish unique loci.',inferential_results=None)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python score_context.py actual-responses.json')
 print(json.dumps(score(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))),indent=2))
