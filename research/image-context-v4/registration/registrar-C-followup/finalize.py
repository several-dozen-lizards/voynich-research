import json,hashlib
from pathlib import Path
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-C-followup');a=json.loads((p/'PAGES.json').read_text());o=json.loads((p/'REVIEW.json').read_text());ev=json.loads((p/'EVT-STRUCTURE.json').read_text());errors=[];checks=[]
for i,q in enumerate(o['pages']):
 v=a[i]
 for b in q['blocks']:
  x,y,w,h=b['box']
  if min(x,y)<0 or x+w>v['native_width']+.1 or y+h>v['native_height']+.1:errors.append([v['folio'],b['block_id'],'native_bounds'])
  prev=-1
  for j,l in enumerate(b['lines']):
   lx,ly,lw,lh=l['box']
   if l['line_number']!=j+1:errors.append([v['folio'],'line_number'])
   if ly<prev:errors.append([v['folio'],'top_order'])
   if lx<x-.1 or ly<y-.1 or lx+lw>x+w+.1 or ly+lh>y+h+.1:errors.append([v['folio'],'containment'])
   prev=ly
  if b['decision']=='VERIFIED':
   readings=[{'reading':z['reading'],'expected':z['line_count'],'observed':len(b['lines']),'match':z['line_count']==len(b['lines'])} for z in ev if z['folio']==v['folio'] and z['unit']==b['unit']]
   checks.append({'folio':v['folio'],'unit':b['unit'],'readings':readings})
(p/'REVIEW-v06-final.json').write_text(json.dumps(o,indent=2));(p/'REVIEW.json').write_text(json.dumps(o,indent=2))
r={'registrar_id':'blind_registrar_C_followup','source_pages_inspected':14,'unreviewed_pages':[],'verified_blocks':sum(b['decision']=='VERIFIED' for q in o['pages'] for b in q['blocks']),'verified_line_boxes':sum(len(b['lines']) for q in o['pages'] for b in q['blocks'] if b['decision']=='VERIFIED'),'unregistered_blocks':sum(b['decision']=='UNREGISTERED' for q in o['pages'] for b in q['blocks']),'unregistered_main_fields':['f105r','f106v','f113v','f82v'],'source_QA':'All14 full source pages inspected. Each page has supplied-resolution writing crops nativeNN-0.jpg/nativeNN-1.jpg; all28 source crops visually inspected. Manual source row proposals retained in SOURCE-GEOMETRY.json. Source-based numbered row-center overlays inspected; all10 accepted numbered rectangle overlays accepted-overlay02,03,05,06,07,08,09,10,11,12 visually inspected after final line-width refinements.','measurement_limits':'Four main fields remain unregistered: physical P boundary on f105r and incomplete fine row measurement on f106v/f113v/f82v. This does not assert that the latter sources are intrinsically ambiguous. Count agreement alone did not qualify f113v. Provisional candidate line boxes were removed from final abstentions and preserved separately. Detached margin/label patches have region geometry but no forced P identity.','envelope_limits':'Rectangular envelopes are conservative, often overlap vertically, and can contain whitespace/intervening strokes. They are not glyph-tight masks. Longer ascenders and sloping baselines motivated source-based upward expansion.','geometry_errors':errors,'H_F_checks_for_verified_blocks':checks,'blindness':{'fresh_isolated_assignment':True,'read_only_allowlisted_folder':True,'transcription_bodies_seen':False,'outcomes_seen':False,'picture_rater_categories_or_boxes_seen':False,'word_transcription_performed':False,'outcome_analysis_performed':False},'review_sha256':hashlib.sha256((p/'REVIEW.json').read_bytes()).hexdigest()}
(p/'SOURCE-QA-RECEIPT.json').write_text(json.dumps(r,indent=2));(p/'PROGRESS.txt').write_text('Complete source-only review of all14 assigned pages. Final REVIEW.json equals REVIEW-v06-final.json. All accepted numbered source overlays checked. Ten verified main blocks/315 row envelopes; four main-field abstentions distinguish unresolved mapping from incomplete fine measurement. Detached writing retained. SOURCE-QA-RECEIPT.json provides native checks, separate H/F counts, limitations and final hash.\n')
print(json.dumps({k:r[k] for k in ['source_pages_inspected','verified_blocks','verified_line_boxes','unregistered_blocks','geometry_errors','review_sha256']},indent=2))
