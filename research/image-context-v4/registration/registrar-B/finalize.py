import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());res=json.loads((p/'REVIEW.v03.json').read_text());i=12;v=a[i];im=Image.open(p/v['image']);im.thumbnail((600,850));sw,sh=im.size;d=ImageDraw.Draw(im)
csall=[[139,158,176,196,215],[249,269,287],[339,358,376,393,409,426,442,459,477,495],[540,559,579,600,620,640]]
for j,cs in enumerate(csall):
 x,y,w,h=r[str(i)][j];lines=[]
 for k,cy in enumerate(cs):
  top=y if k==0 else cy-22;bottom=cy+9
  box=[round(x/sw*v['native_width'],2),round((top-30)/sh*v['native_height'],2),round(w/sw*v['native_width'],2),round((bottom-top)/sh*v['native_height'],2)];lines.append({'line_number':k+1,'box':box});d.rectangle((x,top-30,x+w,bottom-30),outline='red');d.text((x-15,cy-38),str(k+1),fill='blue')
 b=res['pages'][i]['blocks'][j];b.update(unit='P'+str(j+1),lines=lines,decision='VERIFIED',observed_line_count=len(lines),reason='Source image and numbered enclosure overlay show four vertically ordered writing fields separated by clear blank gaps. This field occupies that independently observed position. Complete physical row order supports the corresponding P number; H/F counts agree separately. No words read.');b['box'][3]=round(max(q['box'][1]+q['box'][3] for q in lines)-b['box'][1],2)
im.resize((1200,im.height*2)).save(p/'final12.png')
# Projection completions failed detailed row-identity QA. Preserve checkpoints, withhold certification.
for i in [1,2,4,6]:
 b=res['pages'][i]['blocks'][0];b.update(unit=None,decision='UNREGISTERED',reason='Detailed numbered source-overlay QA did not securely resolve every physical row: projection peaks can fall on ascenders or split one slanted row while missing a short row. Candidate row rectangles remain retained for correction, but their apparent H/F count agreement is insufficient. This is unresolved fine segmentation in this pass, not evidence that the source field is intrinsically unregistrable.');b['candidate_line_count']=b.pop('observed_line_count');b['line_geometry_status']='PROVISIONAL_NOT_COMPLETE'
# Correct the earlier mistaken 15-row claim on f52v after native source inspection.
b=res['pages'][35]['blocks'][0];b['reason']='Native source inspection corrected the earlier provisional double-count in the upper field: six upper rows and eight lower rows are visible, consistent with 14 H/F rows. Complete lateral line enclosures through the drawing interruption remain unverified. Abstention concerns unresolved geometry, not a count mismatch.';b['candidate_line_count']=b.pop('observed_line_count');b['line_geometry_status']='PROVISIONAL_CONTAINS_SUPERSEDED_ROW_PROPOSAL';b['correction_note']='The retained 15 rectangles are superseded proposals, not 15 observed source rows; source count is 14.';b['observed_source_line_count']=14
# Do not misrepresent provisional unregistered rows as complete observed counts.
for page in res['pages']:
 for b in page['blocks']:
  if b['decision']=='UNREGISTERED' and 'observed_line_count' in b:b['candidate_line_count']=b.pop('observed_line_count');b['line_geometry_status']='PROVISIONAL_NOT_COMPLETE'
(p/'REVIEW.v04.json').write_text(json.dumps(res,indent=2));(p/'REVIEW.json').write_text(json.dumps(res,indent=2))
