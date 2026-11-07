"""Picture-only export validation; no writing segmentation or scientific scores."""
from pathlib import Path
import json,sys,math,collections,csv
R=Path(__file__).resolve().parent
def validate(data):
 tasks={t['task_id']:t for t in json.loads((R/'rater-only/TASKS.json').read_text())}
 if data.get('schema')!='v4.1-picture-boxes' or not isinstance(data.get('rater_id'),str) or not data['rater_id'].strip():raise ValueError('Schema and rater ID required')
 pages=data.get('completed_pages');rows=data.get('rows')
 if not isinstance(pages,list) or not pages or any(not isinstance(p,str) or p not in tasks for p in pages) or len(set(pages))!=len(pages):raise ValueError('Unique reviewed pages required')
 if not isinstance(rows,list):raise ValueError('Rows required; an empty list is valid for completed pages without pictures')
 seen=set();counts=collections.Counter()
 for row in rows:
  if set(row)!={'page','box','category','note'}:raise ValueError('Picture fields only; no rater writing geometry')
  if row['page'] not in tasks:raise ValueError('Unknown page')
  t=tasks[row['page']];b=row['box']
  if not isinstance(b,list) or len(b)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in b):raise ValueError('Four finite coordinates required')
  x,y,w,h=b
  if not (x>=0 and y>=0 and w>0 and h>0 and x+w<=t['native_width']+1 and y+h<=t['native_height']+1):raise ValueError('Invalid native box')
  ident=(row['page'],tuple(b))
  if ident in seen:raise ValueError('Duplicate picture rectangle')
  seen.add(ident)
  if row['category'] not in ('PL','VE','FG','CE','OT') or not isinstance(row['note'],str):raise ValueError('Category and text note required')
  if row['page'] in pages:counts[row['category']]+=1
 return dict(status='VALID PICTURE EXPORT; COMPLETENESS REQUIRES INDEPENDENT CHECK',rater_id=data['rater_id'],completed_pages=len(pages),complete_page_picture_counts=dict(counts),draft_rows=sum(r['page'] not in pages for r in rows),reviewed_without_pictures=[p for p in pages if not any(r['page']==p for r in rows)],agreement='NOT COMPUTED',outcomes_joined=False)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python validate_picture_ratings.py actual-picture-boxes.json')
 print(json.dumps(validate(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))),indent=2))
