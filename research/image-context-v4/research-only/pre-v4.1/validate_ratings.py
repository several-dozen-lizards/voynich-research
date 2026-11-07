"""Validate exported blind box annotations; no fabricated ratings or premature agreement."""
from pathlib import Path
import json,sys,math,collections,csv
R=Path(__file__).resolve().parent
def validate(data):
 tasks={t['task_id']:t for t in json.loads((R/'rater-only/TASKS.json').read_text())}
 if data.get('schema')!='v4-blind-boxes' or not isinstance(data.get('rater_id'),str) or not data['rater_id'].strip():raise ValueError('Schema and rater ID required')
 rows=data.get('rows')
 if not isinstance(rows,list) or not rows:raise ValueError('Nonempty actual annotation rows required')
 blocks={};lines=collections.defaultdict(list);types=collections.Counter();seen=set()
 for row in rows:
  if row.get('page') not in tasks:raise ValueError('Unknown or withheld page')
  if row.get('kind') not in ('picture','block','line'):raise ValueError('Invalid row type')
  t=tasks[row['page']];b=row.get('box')
  if not isinstance(b,list) or len(b)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in b):raise ValueError('Four finite coordinates required')
  x,y,w,h=b
  if not (x>=0 and y>=0 and w>0 and h>0 and x+w<=t['native_width']+1 and y+h<=t['native_height']+1):raise ValueError('Box outside native canvas')
  ident=(row['page'],row['kind'],tuple(b))
  if ident in seen:raise ValueError('Duplicate rectangle of same type')
  seen.add(ident);types[row['kind']]+=1
  if not isinstance(row.get('note'),str):raise ValueError('Note field must be text')
  if row['kind']=='picture':
   if row.get('category') not in ('PL','VE','FG','CE','OT'):raise ValueError('Invalid picture category')
  else:
   if not isinstance(row.get('block'),str) or not row['block'].strip():raise ValueError('Writing block ID required')
   if row.get('category') is not None:raise ValueError('Writing has no picture category')
   key=row['page'],row['block']
   if row['kind']=='block':
    if key in blocks:raise ValueError('Duplicate block ID on page')
    blocks[key]=row
   else:
    if type(row.get('line_number')) is not int or row['line_number']<1:raise ValueError('Positive integer line number required')
    lines[key].append(row)
 for key,rr in lines.items():
  if key not in blocks:raise ValueError('Line has no recorded parent block')
  nums=[r['line_number'] for r in rr]
  if sorted(nums)!=list(range(1,len(rr)+1)):raise ValueError('Line numbers must be unique and consecutive from one')
  parent=blocks[key]['box'];px,py,pw,ph=parent
  ordered=sorted(rr,key=lambda r:r['line_number'])
  if any(a['box'][1]>b['box'][1] for a,b in zip(ordered,ordered[1:])):raise ValueError('Line numbering is not top to bottom')
  for row in rr:
   x,y,w,h=row['box']
   if not(x>=px-1 and y>=py-1 and x+w<=px+pw+1 and y+h<=py+ph+1):raise ValueError('Line outside parent block')
 empty=[list(k) for k in blocks if k not in lines]
 return dict(status='ANNOTATION_SCHEMA_VALID; COMPLETENESS REQUIRES INDEPENDENT PAGE CHECK',rater_id=data['rater_id'],model_version=data.get('model_version'),rows=len(rows),row_types=dict(types),annotated_pages=len({r['page'] for r in rows}),released_pages=len(tasks),empty_blocks=empty,agreement='NOT COMPUTED: independent line matching and kappa population must be frozen first',EVT_registration='NOT RUN',outcomes_joined=False)
def export_csv(data,path):
 with Path(path).open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['rater_id','page','kind','block','line_number','x','y','width','height','category','note'])
  for r in data['rows']:w.writerow([data['rater_id'],r['page'],r['kind'],r.get('block'),r.get('line_number'),*r['box'],r.get('category'),r['note']])
if __name__=='__main__':
 if len(sys.argv) not in (2,3):raise SystemExit('Usage: python validate_ratings.py actual-responses.json [validated-output.csv]')
 data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));result=validate(data)
 if len(sys.argv)==3:export_csv(data,sys.argv[2])
 print(json.dumps(result,indent=2))
