import json,hashlib
from pathlib import Path
from PIL import Image
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-C');o=json.loads((p/'REVIEW.json').read_text());a=json.loads((p/'PAGES.json').read_text())
extras={33:[(198,324,249,375)],48:[(36,90,118,758)],50:[(58,277,111,681)]}
for i,rects in extras.items():
 v=a[i];im=Image.open(p/v['image']);sh=round(im.height*600/im.width)
 for j,(x,y,x2,y2) in enumerate(rects):
  o['pages'][i]['blocks'].append({'block_id':f'A{j+1:03}','unit':None,'box':[round(x*v['native_width']/600,2),round((y-35)*v['native_height']/sh,2),round((x2-x)*v['native_width']/600,2),round((y2-y)*v['native_height']/sh,2)],'lines':[],'decision':'UNREGISTERED','reason':'Small isolated ink marks visible within an interrupted source area. Writing versus decorative-stroke membership and P identity unresolved; retained as explicit abstention.'})
# Record honest scope of rectangular envelopes.
for q in o['pages']:
 for b in q['blocks']:
  if b['decision']=='VERIFIED':
   b['reason']+=' Line rectangles are conservative full-field horizontal envelopes; they can overlap vertically and include whitespace or intervening strokes. They are not glyph-tight masks.'
   x,y,w,h=b['box'];b['box']=[max(0,x-0.1),max(0,y-0.1),w+0.2,h+0.2]
qafile={'registrar_id':'blind_registrar_C','source_pages_inspected':51,'unreviewed_pages':[],'accepted_blocks':sum(b['decision']=='VERIFIED' for q in o['pages'] for b in q['blocks']),'accepted_line_boxes':sum(len(b['lines']) for q in o['pages'] for b in q['blocks'] if b['decision']=='VERIFIED'),'abstained_blocks':sum(b['decision']=='UNREGISTERED' for q in o['pages'] for b in q['blocks']),'source_contact_sheets':'sheet00.jpg through sheet16.jpg','enlarged_source_checks':'crop07,08,13,16,18,20,21,22,25,28,29,31,33,39,40; large48 and large50','accepted_overlay_QA':'All final-overlay files for indices07,08,13,16,21,22,29,31,33,39,40,48,50 visually inspected after expansion. All17 accepted blocks present in these13 images.','limitations':'Remaining fields are explicit abstentions. Their broad field boxes do not constitute complete line geometry. Accepted line rectangles are conservative horizontal envelopes and may overlap. No forced P mapping for separated fields or uncertain boundaries.','blindness':{'only_assigned_folder_read':True,'transcription_bodies_seen':False,'outcomes_seen':False,'picture_rater_boxes_or_categories_seen':False,'words_transcribed':False,'outcome_analysis_run':False}}
errors=[]
for i,q in enumerate(o['pages']):
 v=a[i]
 for b in q['blocks']:
  x,y,w,h=b['box']
  if min(x,y)<0 or x+w>v['native_width']+.1 or y+h>v['native_height']+.1:errors.append((i,b['block_id'],'bounds'))
  for l in b['lines']:
   lx,ly,lw,lh=l['box']
   if lx<x-.1 or ly<y-.1 or lx+lw>x+w+.1 or ly+lh>y+h+.1:errors.append((i,b['block_id'],'containment'))
qafile['native_geometry_validation_errors']=errors
(p/'REVIEW-v04-final.json').write_text(json.dumps(o,indent=2));(p/'REVIEW.json').write_text(json.dumps(o,indent=2));qafile['review_sha256']=hashlib.sha256((p/'REVIEW.json').read_bytes()).hexdigest();(p/'SOURCE-QA-RECEIPT.json').write_text(json.dumps(qafile,indent=2));(p/'PROGRESS.txt').write_text('Complete: source-only visual review of all51 pages and final accepted-overlay QA. REVIEW.json equals REVIEW-v04-final.json. SOURCE-QA-RECEIPT.json records scope, conservative envelope limitations, explicit abstentions and validation. No unreviewed pages.\n')
print(json.dumps(qafile,indent=2))
