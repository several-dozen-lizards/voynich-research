"""Join visually reviewed shared geometry to header-only EVT locators. No outcomes."""
from pathlib import Path
import json,csv,math,hashlib,collections,shutil
R=Path(__file__).resolve().parent;W=R/'registrar-only'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def validate_review(review,pages):
 for k in ('fresh_context','outcome_blind','picture_boxes_unseen'):
  if review.get(k) is not True:raise ValueError('Independent blind declaration required: '+k)
 if not isinstance(review.get('registrar_id'),str) or not review['registrar_id'].strip():raise ValueError('Registrar ID required')
 seen_pages=set()
 for page in review.get('pages',[]):
  tid=page.get('task_id')
  if tid not in pages or tid in seen_pages:raise ValueError('Unknown or duplicate reviewed page')
  seen_pages.add(tid);dims=pages[tid];seen_blocks=set()
  def box(b):
   if not isinstance(b,list) or len(b)!=4 or any(type(x) not in (int,float) or not math.isfinite(x) for x in b):raise ValueError('Finite native rectangle required')
   x,y,w,h=b
   if not (x>=0 and y>=0 and w>0 and h>0 and x+w<=dims['native_width']+1 and y+h<=dims['native_height']+1):raise ValueError('Box outside native canvas')
  for block in page.get('blocks',[]):
   bid=block.get('block_id')
   if not isinstance(bid,str) or not bid or bid in seen_blocks:raise ValueError('Unique block IDs required')
   seen_blocks.add(bid)
   if block.get('decision') not in ('VERIFIED','UNREGISTERED'):raise ValueError('Explicit block decision required')
   if not block.get('reason','').strip():raise ValueError('Visual decision reason required')
   if block['decision']=='VERIFIED':
    if page.get('reviewed') is not True:raise ValueError('Cannot accept geometry on unreviewed page')
    box(block.get('box'));lines=block.get('lines',[])
    if not lines:raise ValueError('Verified block must have writing lines')
    if [x.get('line_number') for x in lines]!=list(range(1,len(lines)+1)):raise ValueError('Consecutive physical line order required')
    bx,by,bw,bh=block['box'];last=-1
    for line in lines:
     box(line.get('box'));x,y,w,h=line['box']
     if not (x>=bx-1 and y>=by-1 and x+w<=bx+bw+1 and y+h<=by+bh+1):raise ValueError('Line outside block')
     if y<last:raise ValueError('Lines not top-to-bottom')
     last=y
 return True
def build(pages,units,candidates,review=None):
 pmap={p['task_id']:p for p in pages};byfolio={p['folio']:p for p in pages}
 if review:validate_review(review,pmap)
 reviews={p['task_id']:p for p in review.get('pages',[])} if review else {}
 cmap={c['task_id']:c for c in candidates};accepted=[];dropped=[];shared={};used=set();block_audit=[]
 index={(u['folio'],u['unit'],u['reading']):u for u in units}
 for p in pages:
  rp=reviews.get(p['task_id']);blocks=rp.get('blocks',[]) if rp else []
  mapped=collections.Counter(b.get('unit') for b in blocks if b.get('decision')=='VERIFIED' and b.get('unit'))
  for b in blocks:
   bid=b['block_id'];unit=b.get('unit');state=b['decision'];reason=b['reason']
   if state!='VERIFIED' or not unit:
    block_audit.append(dict(task_id=p['task_id'],folio=p['folio'],block_id=bid,unit=unit,status='UNREGISTERED',reason=reason));continue
   if mapped[unit]>1:
    block_audit.append(dict(task_id=p['task_id'],folio=p['folio'],block_id=bid,unit=unit,status='AMBIGUOUS_DUPLICATE_UNIT',reason='Multiple reviewed blocks assigned the same P unit; no automatic concatenation.'));continue
   for co in ('H','F'):
    key=(p['folio'],unit,co);u=index.get(key)
    if not u:
     dropped.append(dict(folio=p['folio'],unit=unit,reading=co,block_id=bid,status='DROPPED',reason='READING_UNIT_ABSENT',expected_lines=None,visible_lines=len(b['lines'])));continue
    used.add(key)
    if u['line_count']!=len(b['lines']):
     dropped.append(dict(folio=p['folio'],unit=unit,reading=co,block_id=bid,status='DROPPED',reason='LINE_COUNT_MISMATCH',expected_lines=u['line_count'],visible_lines=len(b['lines'])));continue
    pairs=[]
    for line,locus in zip(b['lines'],u['lines']):
     lid=p['task_id']+'/'+bid+'/'+str(line['line_number']);shared[lid]=dict(shared_line_id=lid,task_id=p['task_id'],folio=p['folio'],block_id=bid,line_number=line['line_number'],box=line['box'],block_box=b['box'],line_height=line['box'][3],line_width=line['box'][2])
     pairs.append(dict(shared_line_id=lid,locus=locus['locus']))
    accepted.append(dict(folio=p['folio'],unit=unit,reading=co,task_id=p['task_id'],block_id=bid,status='REGISTERED',line_count=len(pairs),line_map=pairs,registrar=review['registrar_id'],basis='Independent visual geometry and within-block order; exact reading-specific count.'))
   block_audit.append(dict(task_id=p['task_id'],folio=p['folio'],block_id=bid,unit=unit,status='REVIEWED',reason=reason))
  for c in cmap.get(p['task_id'],{}).get('blocks',[]):
   # Every candidate is accounted for, even if reviewer replaced segmentation entirely.
   block_audit.append(dict(task_id=p['task_id'],folio=p['folio'],block_id='candidate/'+c['block_id'],unit=None,status='SUPERSEDED_BY_VISUAL_REVIEW' if rp else 'PENDING_VISUAL_REVIEW',reason='Automated candidate is not an independent accepted registration.'))
 for u in units:
  key=(u['folio'],u['unit'],u['reading'])
  if key in used:continue
  page=byfolio.get(u['folio']);rp=reviews.get(page['task_id']) if page else None
  relevant=[b for b in rp.get('blocks',[]) if b.get('unit')==u['unit']] if rp else []
  reason='IMAGE_PANEL_UNREGISTERED' if not page else 'PENDING_VISUAL_REVIEW' if not rp or not rp.get('reviewed') else 'AMBIGUOUS_DUPLICATE_UNIT' if sum(b.get('decision')=='VERIFIED' for b in relevant)>1 else 'VISUAL_ABSTENTION' if relevant else 'NO_VERIFIED_BLOCK_MAPPING'
  all_visual=rp.get('blocks',[]) if rp else []
  detail=' | '.join(b['block_id']+': '+b['reason'] for b in (relevant or all_visual))
  dropped.append(dict(folio=u['folio'],unit=u['unit'],reading=u['reading'],block_id=';'.join(b['block_id'] for b in (relevant or all_visual)),status='PENDING' if reason=='PENDING_VISUAL_REVIEW' else 'DROPPED',reason=reason,expected_lines=u['line_count'],visible_lines=sum(len(b.get('lines',[])) for b in (relevant or all_visual)) if all_visual else None,detail=detail))
 return dict(accepted=accepted,dropped=dropped,shared_lines=list(shared.values()),block_audit=block_audit,reviewed_pages=len(reviews),ready_pages=len(pages))
def main():
 if (R/'REGISTRATION-SNAPSHOT.json').exists():
  old=json.loads((R/'REGISTRATION-SNAPSHOT.json').read_text());archive=R/'snapshots'/sha(R/'REGISTRATION-SNAPSHOT.json')[:16];archive.mkdir(parents=True,exist_ok=True)
  for name in list(old['files'])+['REGISTRATION-SNAPSHOT.json']:
   if (R/name).exists():shutil.copy2(R/name,archive/name)
 pages=json.loads((W/'PAGES.json').read_text());units=json.loads((W/'EVT-STRUCTURE.json').read_text());candidates=json.loads((W/'GEOMETRY-CANDIDATES.json').read_text()) if (W/'GEOMETRY-CANDIDATES.json').exists() else []
 review=json.loads((W/'REVIEW.json').read_text()) if (W/'REVIEW.json').exists() else None
 result=build(pages,units,candidates,review)
 save(R/'REGISTRATION.json',dict(status='PARTIAL_REGISTRATION' if result['accepted'] else 'AWAITING_BLIND_VISUAL_REGISTRATION',accepted=result['accepted'],dropped=result['dropped'],reviewed_pages=result['reviewed_pages'],ready_pages=result['ready_pages'],outcomes_joined=False,picture_boxes_used=False))
 save(R/'SHARED-LINE-GEOMETRY.json',dict(status='REVIEWED_REGISTERED_LINES_ONLY',lines=result['shared_lines'],readings_share_geometry=True))
 save(R/'BLOCK-AUDIT.json',result['block_audit'])
 with (R/'DROPPED-BLOCKS.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=['folio','unit','reading','block_id','status','reason','expected_lines','visible_lines','detail']);writer.writeheader();writer.writerows(result['dropped'])
 summary=dict(status='PARTIAL; UNREVIEWED PAGES RETAINED' if result['reviewed_pages']<len(pages) else 'REVIEW COMPLETE; DROPS RETAINED',reviewed_pages=result['reviewed_pages'],ready_pages=len(pages),registered_reading_blocks=len(result['accepted']),shared_physical_lines=len(result['shared_lines']),excluded_reading_units=len(result['dropped']),exclusions_by_reason=dict(collections.Counter(x['reason'] for x in result['dropped'])),outcomes_joined=False,picture_boxes_used=False,v103='PARKED',statistical_analysis='NOT RUN')
 save(R/'STATUS.json',summary)
 save(R/'REGISTRATION-SNAPSHOT.json',dict(status='SEALED CURRENT COVERAGE; NOT FULL-COHORT COMPLETION',files={n:sha(R/n) for n in ['REGISTRATION.json','SHARED-LINE-GEOMETRY.json','BLOCK-AUDIT.json','DROPPED-BLOCKS.csv','STATUS.json']},review_sha256=sha(W/'REVIEW.json') if review else None,structure_sha256=sha(W/'EVT-STRUCTURE.json')))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
