"""Frozen-geometry picture-context labels and pre-adjudication G6/G2 only."""
from pathlib import Path
from fractions import Fraction
import json,csv,math,collections,hashlib
R=Path(__file__).resolve().parent;V=R.parent
CATS=['PL','VE','FG','CE','OT','NO']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate_response(data):
 if not isinstance(data,dict) or set(data)!={'completed','pictures'} or data['completed'] is not True or not isinstance(data['pictures'],list):raise ValueError('Complete page/picture schema required')
 seen={}
 for p in data['pictures']:
  if set(p)!={'box','category','note'} or p['category'] not in CATS[:-1] or not isinstance(p['note'],str):raise ValueError('Picture fields/category/note invalid')
  b=p['box']
  if not isinstance(b,list) or len(b)!=4 or any(type(x) not in (float,int) or not math.isfinite(x) for x in b):raise ValueError('Four finite normalized box coordinates required')
  x,y,w,h=b
  if not(0<=x<=1 and 0<=y<=1 and w>0 and h>0 and x+w<=1+1e-9 and y+h<=1+1e-9):raise ValueError('Normalized box outside image or degenerate')
  key=tuple(b)
  if key in seen and seen[key]!=p['category']:raise ValueError('Coincident boxes have conflicting categories')
  seen[key]=p['category']
 return data
def assign(line,pictures,width,height):
 lx,ly,lw,lh=line['box'];assert lh>0
 ranked=[]
 for i,p in enumerate(pictures):
  x,y,w,h=p['box'];x*=width;y*=height;w*=width;h*=height
  dx=max(x-(lx+lw),lx-(x+w),0);dy=max(y-(ly+lh),ly-(y+h),0)
  distance=math.hypot(dx,dy)
  centers=math.hypot((x+w/2)-(lx+lw/2),(y+h/2)-(ly+lh/2))
  # Ties resolved geometrically, never by picture category or rater order.
  ranked.append((distance,centers,w*h,x,y,w,h,p['category'],i))
 if not ranked:return dict(label='NO',distance_line_heights=None,picture_index=None,tie=False)
 ranked.sort(key=lambda t:t[:7]);best=ranked[0];ratio=best[0]/lh
 return dict(label=best[7] if ratio<=2 else 'NO',distance_line_heights=ratio,picture_index=best[8],tie=sum(t[0]==best[0] for t in ranked)>1)
def kappa(a,b,cats):
 assert len(a)==len(b);matrix=[[0 for _ in cats] for _ in cats];ix={c:i for i,c in enumerate(cats)}
 for x,y in zip(a,b):matrix[ix[x]][ix[y]]+=1
 n=len(a)
 if not n:return dict(n=0,kappa=None,status='UNDEFINED_EMPTY',categories=cats,confusion_matrix=matrix,pass_gate=False)
 ra=[sum(row) for row in matrix];cb=[sum(row[j] for row in matrix) for j in range(len(cats))]
 po=Fraction(sum(matrix[i][i] for i in range(len(cats))),n);pe=Fraction(sum(x*y for x,y in zip(ra,cb)),n*n)
 value=(po-pe)/(1-pe) if pe!=1 else None
 return dict(n=n,kappa=float(value) if value is not None else None,exact_kappa=str(value) if value is not None else None,observed_agreement=float(po),expected_agreement=float(pe),categories=cats,confusion_matrix=matrix,status='DEFINED' if value is not None else 'UNDEFINED_SINGLE_CLASS_EXPECTATION',pass_gate=value is not None and value>=Fraction(3,5))
def main():
 freeze=json.loads((R/'RATING-FREEZE.json').read_text());geometry=V/'registration/SHARED-LINE-GEOMETRY.json';assert sha(geometry)==freeze['geometry_sha256'];lines=json.loads(geometry.read_text())['lines'];tasks={t['task_id']:t for t in json.loads((V/'rater-only/TASKS.json').read_text())}
 ratings={};failed={};labels={}
 for role in ['A','B']:
  ratings[role]={};failed[role]={}
  for tid in tasks:
   path=R/'responses'/role/(tid+'.json')
   if not path.exists():failed[role][tid]='NO_ACCEPTED_RESPONSE';continue
   record=json.loads(path.read_text())
   try:
    assert record['model']==freeze['models'][role]
    ratings[role][tid]=validate_response(record['annotation'])
   except (AssertionError,ValueError,KeyError) as e:failed[role][tid]=str(e)
  rows=[];labels[role]={}
  for line in lines:
   tid=line['task_id']
   if tid not in ratings[role]:continue
   task=tasks[tid];context=assign(line,ratings[role][tid]['pictures'],task['native_width'],task['native_height']);row=dict(shared_line_id=line['shared_line_id'],task_id=tid,**context);rows.append(row);labels[role][line['shared_line_id']]=context['label']
  with (R/f'LINE-CONTEXT-{role}.csv').open('w',newline='',encoding='utf-8') as f:
   w=csv.DictWriter(f,fieldnames=['shared_line_id','task_id','label','distance_line_heights','picture_index','tie']);w.writeheader();w.writerows(rows)
 paired=[l['shared_line_id'] for l in lines if l['shared_line_id'] in labels['A'] and l['shared_line_id'] in labels['B']];a=[labels['A'][lid] for lid in paired];b=[labels['B'][lid] for lid in paired]
 g6=kappa(a,b,CATS);g2=kappa(['PL' if x=='PL' else 'not-PL' for x in a],['PL' if x=='PL' else 'not-PL' for x in b],['PL','not-PL'])
 complete=len(paired)==len(lines)
 for g in (g6,g2):
  g['gate_status']='PASS' if complete and g['pass_gate'] else 'NOT ESTIMABLE: MISSING REGISTERED-LINE RATINGS' if not complete else 'NOT RELIABLE'
  g['pass_gate']=complete and g['pass_gate']
 result=dict(status='PRE_ADJUDICATION_AGREEMENT; NO OT MERGE',registered_physical_lines=len(lines),paired_physical_lines=len(paired),G6=dict(governs='H-IMG',**g6),G2=dict(governs='H-PLANT',**g2),valid_page_responses={r:len(x) for r,x in ratings.items()},failed_or_missing_pages=failed,models=freeze['models'],geometry_sha256=sha(geometry),manual_sha256=freeze['manual_sha256'],adjudication='NOT RUN',OT_merge='NOT RUN',H_F_pooling='No duplicated H/F observations; physical line IDs only.',timing_exception=freeze['timing_exception'],coordinate_control_limit=freeze['coordinate_control_limit'],outcome_join='NOT RUN',support_and_scientific_tests='NOT RUN',v103='PARKED')
 (R/'AGREEMENT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['registered_physical_lines','paired_physical_lines','G6','G2','valid_page_responses']},indent=2))
if __name__=='__main__':main()
