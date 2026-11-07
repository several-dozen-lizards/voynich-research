import json,hashlib
from pathlib import Path
from PIL import Image
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());res=json.loads((p/'REVIEW.v04.json').read_text())
unfinished={0,1,2,4,5,6,13,34,41,42,44,45,46}
for i,page in enumerate(res['pages']):
 v=a[i];im=Image.open(p/v['image']);im.thumbnail((600,850));sw,sh=im.size
 page['source_visual_inspection_complete']=True
 page['geometry_complete']=i not in unfinished
 for j,b in enumerate(page['blocks']):
  if b['decision']=='UNREGISTERED':
   if b['lines']:b['candidate_lines']=b.pop('lines');b['lines']=[]
   x,y,w,h=r[str(i)][j];b['box']=[round(x/sw*v['native_width'],2),round((y-30)/sh*v['native_height'],2),round(w/sw*v['native_width'],2),round(h/sh*v['native_height'],2)]
   if i in unfinished and j==0:
    b['registration_status']='UNFINISHED_FINE_SEGMENTATION'
    b['missing_work']='Correct and visually verify every physical row enclosure, including short rows and slanted endpoints, before any P mapping. Retained candidate rectangles are not certified source lines.'
    b['reason']='Source field is visible, but complete corrected row enclosures were not established in this pass. This is unfinished fine segmentation, not an intrinsic manuscript ambiguity. Previous provisional/count-matching completions were withheld after visual QA; source field remains preserved.'
   else:
    b['registration_status']='SOURCE_MAPPING_ABSTENTION'
    b['reason']='Visually observed writing field is separated from other writing by drawing or blank space, or is an isolated marginal/short run. The supplied P locator does not independently identify this physical field. Retain the region without merging independent fields to obtain a count match. No complete line registration is claimed.'
  else:b['registration_status']='SOURCE_GEOMETRY_VERIFIED';b['line_geometry_status']='SOURCE_REVIEWED_COMPLETE'
 page['notes']='Full source page inspected at page scale and writing inspected in an enlarged source view/crop or numbered overlay. reviewed=true denotes this completed visual inspection; geometry_complete separately distinguishes unfinished fine segmentation. All visible writing retained as body/isolated fields or explicit abstention: tiny foliation and edge/non-body marginal marks are outside P registration and their line geometry is not certified. No words transcribed; no picture categories or outcomes consulted.'
# Corrected native observation, keeping the superseded 15-row candidate record separately.
res['pages'][35]['blocks'][0]['reason']='Native source inspection shows six upper rows plus eight lower rows, correcting the earlier provisional 15-row claim. This 14-row observation agrees with H/F counts but does not independently certify complete line endpoints through drawing interruptions. Source field retained without forced registration.'
res['pages'][35]['blocks'][0]['registration_status']='UNFINISHED_FINE_SEGMENTATION';res['pages'][35]['geometry_complete']=False;unfinished.add(35)
# Validate certified geometry only, plus every retained observed region.
errors=[];verified=[];abstained=[]
for i,page in enumerate(res['pages']):
 for b in page['blocks']:
  x,y,w,h=b['box'];nw=a[i]['native_width'];nh=a[i]['native_height']
  if min(x,y,w,h)<0 or x+w>nw+.1 or y+h>nh+.1:errors.append([page['folio'],b['block_id'],'bounds'])
  if b['decision']=='VERIFIED':
   verified.append([page['folio'],b['block_id'],b['unit'],len(b['lines'])]);prev=-1
   for k,q in enumerate(b['lines']):
    xx,yy,ww,hh=q['box'];
    if q['line_number']!=k+1 or yy<prev or xx<x-.1 or yy<y-.1 or xx+ww>x+w+.1 or yy+hh>y+h+.1:errors.append([page['folio'],b['block_id'],k,'line QA'])
    prev=yy
  else:abstained.append([page['folio'],b['block_id'],b['registration_status']])
assert not errors,errors
(p/'REVIEW.v05.json').write_text(json.dumps(res,indent=2));(p/'REVIEW.json').write_text(json.dumps(res,indent=2));sha=hashlib.sha256((p/'REVIEW.json').read_bytes()).hexdigest()
receipt={'registrar_id':'blind_registrar_B','final_review_sha256':sha,'inspection_pass_complete':True,'geometry_registration_complete':False,'assigned_pages':51,'source_pages_visually_inspected':51,'uninspected_pages':[],'verified_blocks':verified,'verified_block_count':len(verified),'abstained_block_count':len(abstained),'unfinished_fine_segmentation_pages':[a[i]['folio'] for i in sorted(unfinished)],'unfinished_fine_segmentation_is_not_intrinsic_ambiguity':True,'remaining_work':'Fine segmentation and source overlay correction remain unfinished on listed pages. Other unregistered fields retain source mapping abstentions because physical regions do not identify a one-to-one P locator. These distinctions must survive aggregation.','actual_views':{'page_contact_sheets':['sheet%02d.jpg'%i for i in range(0,51,3)],'numbered_baseline_and_rectangle_crops':['rows%02d.png'%i for i in [3,9,11,13,16,17,20,23,28,29,30,34,35,38,39,40,41]],'verified_rectangle_crops':['verified%02d.png'%i for i in [3,9,11,13,16,17,20,23,28,29,30,34,39,40,41]],'dense_baseline_crops':['dense%02d.png'%i for i in [0,1,2,4,5,6]],'dense_rectangle_crops_downgraded_after_QA':['finaldense%02d.png'%i for i in [1,2,4,6]],'original_source_views':['source%d.png'%i for i in [7,8,10,12,14,15]],'native_source_crops':['sourcecrop%02d.png'%i for i in [18,19,21,22,24,25,26,27,31,32,33,35,36,37,38,42,43,44,45,46,47,48,49,50]],'f1r_four_field_overlay':'final12.png'},'checkpoints':['REVIEW.v01.json','REVIEW.v02.json','REVIEW.v03.json','REVIEW.v04.json','REVIEW.v05.json'],'corrections':['Downgraded tentative dense-row completions after source QA; count agreement was insufficient.','Downgraded f20v/f51r/f6v lateral endpoints rather than certify incomplete rectangles.','Corrected f52v earlier provisional 15-row claim to 14 physical source rows; retained superseded candidates.','Separated candidate_lines from certified lines on all abstentions.'],'validation':{'native_region_bounds':'pass','verified_line_number_order':'pass','verified_block_containment':'pass','H_F_verified_counts_checked_separately':True},'blindness':{'fresh_context':True,'outcome_blind':True,'picture_boxes_unseen':True,'transcription_bodies_unseen':True,'words_not_transcribed':True,'no_picture_classification':True,'outside_allowlist_not_accessed':True},'limitations':['Page visual inspection completion does not mean all page geometry is complete.','UNREGISTERED candidate_lines are explicitly provisional and must never be used as registered line geometry.','Native-coordinate source rectangles are conservative enclosures, not pixel masks.','No external or outcome analysis was performed.']}
(p/'SOURCE-QA-RECEIPT.json').write_text(json.dumps(receipt,indent=2));(p/'PROGRESS.txt').write_text('Source visual inspection: 51/51 pages. Final checkpoint v05 saved with SHA256 receipt. Certified blocks: %d. Geometry registration is PARTIAL: unfinished fine-segmentation pages and separate source mapping abstentions are explicit. Candidate lines are not certified.\n'%len(verified))
print(json.dumps({'sha256':sha,'verified_blocks':len(verified),'abstained_blocks':len(abstained),'unfinished_pages':receipt['unfinished_fine_segmentation_pages'],'validation_errors':errors}))
