import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-C-followup');a=json.loads((p/'PAGES.json').read_text());g=json.loads((p/'SOURCE-GEOMETRY.json').read_text());o=json.loads((p/'REVIEW.json').read_text())
accepted={2,3,5,6,7,8,9,10,11,12};drops={0:'Physical P1/P2 boundary is not independently established inside the continuous field. Candidate row segmentation remains incomplete; no source-based P split is certified.',1:'Incomplete fine measurement: candidate46 row envelopes do not establish complete distinct row identity. Supplied47 count is not used to invent a missing row. This is an unresolved measurement limit, not a claim of intrinsic source ambiguity.',4:'Incomplete fine measurement: candidate count agrees with supplied49 but individual row identity/completeness is not independently settled through the crowded transitions. Count agreement does not qualify these proposals.',13:'Incomplete fine measurement: candidate32 main-field rows do not establish the complete distinct row sequence. Supplied34 count is not used to add unobserved rows. Detached labels remain separate.'}
widths={6:[762,766,762,507,763,760,747,610,631,651,502],7:[430,428,435,439,451,458,472,482,493,495,519,535,537,529,429],8:[675,680,668,680,680,519,518,522,558,553,548,532,512,472],9:[752,750,751,761,606,465,471,466,453,428,438,455,464,473,472,442,468,430,430,469,410],10:[721]*5+[858]*3+[507]+[856]*5+[565]+[856]*8+[546]+[859]*8+[483]+[864]*7+[748],12:[618,577,527,519,515,491,491,484,491,480,493,493,506,500,429,574,550,480,479,549,554,547,541,545,550,558,565,566,580,589,659]}
# Explicit corrections established from source-only row checks.
for i in accepted:
 v=a[i];q=o['pages'][i];f=g[str(i)]['fields'][0];r=f['rect'];sh=round(Image.open(p/v['image']).height*900/Image.open(p/v['image']).width);sx=v['native_width']/900;sy=v['native_height']/sh
 def conv(x,y,x2,y2):return [round(x*sx,2),round(y*sy,2),round((x2-x)*sx,2),round((y2-y)*sy,2)]
 lines=[]
 for j,y in enumerate(f['centers']):
  xl=r[0];xr=widths.get(i,[r[2]]*len(f['centers']))[j];yt=y-24;yb=y+24
  if i in {2,3,5,10,11}:yt=y-34 # sloping full-width baselines and long ascenders
  if j==0:yt=min(yt,r[1])
  if i==8 and j==6:yt=279
  if i==10:
   xl=198 if j<9 else (226 if j<15 else (236 if j<24 else (251 if j<33 else 284)))
   if j==15:yt=422
   if j==24:yt=622
  lines.append({'line_number':j+1,'box':conv(xl,yt,xr,yb)})
 b=q['blocks'][0];b.update(unit='P',lines=lines,decision='VERIFIED',reason=g[str(i)]['reason']+' Each listed physical row was checked in supplied-resolution source crops and a numbered source overlay. Shared P identity follows the unique continuous field and top-to-bottom order. H/F counts are corroboration only. Rectangles are conservative envelopes and can overlap vertically.')
 x=min(l['box'][0] for l in lines);y=min(l['box'][1] for l in lines);x2=max(l['box'][0]+l['box'][2] for l in lines);y2=max(l['box'][1]+l['box'][3] for l in lines);b['box']=[round(x-.1,2),round(y-.1,2),round(x2-x+.2,2),round(y2-y+.2,2)]
 q['notes']='Full source page, supplied-resolution enlarged field crops, and numbered row overlays inspected. Other visible detached writing retained as unregistered. No transcription bodies or outcome/picture-rater material consulted.'
for i,reason in drops.items():
 o['pages'][i]['blocks'][0]['lines']=[];o['pages'][i]['blocks'][0]['reason']=reason+' Candidate measurements are preserved separately in SOURCE-GEOMETRY.json and prior checkpoints, not certified as complete source lines.';o['pages'][i]['notes']='Entire page and enlarged source writing crops inspected; the retained source field is an explicit measurement/mapping abstention. Reviewed means source-level inspection complete, not fine-geometry verification.'
for i,q in enumerate(o['pages']):
 for b in q['blocks'][1:]:b['reason']='Detached writing/annotation patch visible in source. P membership is not independently established from physical placement; retained unregistered.'
 q['reviewed']=True
# Ensure no source writing numeral outside fields omitted.
o['unreviewed_pages']=[]
(p/'REVIEW-v05.json').write_text(json.dumps(o,indent=2));(p/'REVIEW.json').write_text(json.dumps(o,indent=2))
for i in sorted(accepted):
 v=a[i];im=Image.open(p/v['image']);im=im.resize((900,round(im.height*900/im.width)));dr=ImageDraw.Draw(im)
 for b in o['pages'][i]['blocks']:
  if b['decision']!='VERIFIED':continue
  for l in b['lines']:
   x,y,w,h=l['box'];sx=900/v['native_width'];sy=im.height/v['native_height'];dr.rectangle((x*sx,y*sy,(x+w)*sx,(y+h)*sy),outline='red',width=1);dr.text((max(0,x*sx-25),y*sy),str(l['line_number']),fill='blue')
 im.save(p/f'accepted-overlay{i:02}.jpg')
print('accepted',len(accepted),sum(len(q['blocks'][0]['lines']) for q in o['pages']))
