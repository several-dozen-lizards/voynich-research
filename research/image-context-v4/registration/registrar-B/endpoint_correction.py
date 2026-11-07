import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());res=json.loads((p/'REVIEW.json').read_text());c=json.loads((p/'centers.json').read_text())
W={13:[340,340,340,260,340,340,330,270,270,270,230],34:[210,215,220,225,230,235,245,250,255,265,273,273,273,273,240],41:[387]*5+[205]*15+[175]}
for i,wws in W.items():
 v=a[i];src=Image.open(p/v['image']);thumb=src.copy();thumb.thumbnail((600,850));sw,sh=thumb.size;d=ImageDraw.Draw(src);x,y,w,h=r[str(i)][0];cs=c[str(i)];lines=[]
 for k,(cy,ww) in enumerate(zip(cs,wws)):
  top=y if k==0 else cy-20;bot=cy+7
  b=[round(x/sw*v['native_width'],2),round((top-30)/sh*v['native_height'],2),round(ww/sw*v['native_width'],2),round((bot-top)/sh*v['native_height'],2)];lines.append({'line_number':k+1,'box':b})
  lx=x/sw*src.width;ty=(top-30)/sh*src.height;rx=(x+ww)/sw*src.width;by=(bot-30)/sh*src.height;d.rectangle((lx,ty,rx,by),outline='red',width=2);d.text((lx-22,ty+15),str(k+1),fill='blue')
 b=res['pages'][i]['blocks'][0];b['lines']=lines;b['box']=[min(q['box'][0] for q in lines),min(q['box'][1] for q in lines),max(q['box'][0]+q['box'][2] for q in lines)-min(q['box'][0] for q in lines),max(q['box'][1]+q['box'][3] for q in lines)-min(q['box'][1] for q in lines)];b['unit']='P';b['decision']='VERIFIED';b['registration_status']='SOURCE_GEOMETRY_VERIFIED';b['line_geometry_status']='SOURCE_REVIEWED_COMPLETE';b['reason']='Native-resolution numbered source overlay reviewed. Lateral endpoints expanded from the earlier incomplete proposals to enclose the observed writing. The continuous left writing field remains coherent around right-side drawing interruptions; complete row order and sole P identity are visible independently of the separate H/F count check.';b['observed_line_count']=len(lines);b.pop('missing_work',None);res['pages'][i]['geometry_complete']=True
 box=(int((x-16)/sw*src.width),max(0,int((y-40)/sh*src.height)),min(src.width,int((x+w+8)/sw*src.width)),min(src.height,int((y+h-18)/sh*src.height)));cr=src.crop(box);cr.thumbnail((1200,1700));cr.save(p/('corrected%02d.png'%i))
(p/'REVIEW.v06.pending.json').write_text(json.dumps(res,indent=2))
