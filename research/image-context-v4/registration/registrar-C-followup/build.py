import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-C-followup');a=json.loads((p/'PAGES.json').read_text());g=json.loads((p/'SOURCE-GEOMETRY.json').read_text());o={'registrar_id':'blind_registrar_C_followup','fresh_context':True,'outcome_blind':True,'picture_boxes_unseen':True,'pages':[],'unreviewed_pages':[]}
for i,v in enumerate(a):
 sh=round(Image.open(p/v['image']).height*900/Image.open(p/v['image']).width);sx=v['native_width']/900;sy=v['native_height']/sh
 def conv(r):x,y,x2,y2=r;return [round(x*sx,2),round(y*sy,2),round((x2-x)*sx,2),round((y2-y)*sy,2)]
 q={'task_id':v['task_id'],'folio':v['folio'],'reviewed':str(i) in g,'blocks':[],'notes':'Fine row geometry QA ongoing.'}
 if str(i) in g:
  d=g[str(i)];im=Image.open(p/f'page{i:02}.jpg');dr=ImageDraw.Draw(im)
  for j,f in enumerate(d['fields']):
   r=f['rect'];rows=f.get('centers',[]);rr=[r[0],min(r[1],min(rows)-24) if rows else r[1],r[2],max(r[3],max(rows)+24) if rows else r[3]]
   b={'block_id':f'B{j+1:03}','unit':None,'box':conv(rr),'lines':[{'line_number':n+1,'box':conv([r[0],y-24,r[2],y+24])} for n,y in enumerate(rows)],'decision':'UNREGISTERED','reason':d['reason']+' Row envelopes are provisional source-based manual measurements; line completeness and identity QA pending.'}
   q['blocks'].append(b)
   for n,y in enumerate(rows):dr.line((r[0],y,r[2],y),fill='red',width=1);dr.text((max(0,r[0]-35),y-7),str(n+1),fill='blue')
  for j,r in enumerate(d.get('extras',[])):q['blocks'].append({'block_id':f'M{j+1:03}','unit':None,'box':conv(r),'lines':[],'decision':'UNREGISTERED','reason':'Detached source-margin ink/annotation region. P identity unresolved.'})
  im.save(p/f'rowcheck{i:02}.jpg')
 else:o['unreviewed_pages'].append(v['task_id'])
 o['pages'].append(q)
(p/'REVIEW.json').write_text(json.dumps(o,indent=2))
print('saved',len(g),'fine review pages')
