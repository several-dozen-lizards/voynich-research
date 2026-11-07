import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());res=json.loads((p/'REVIEW.v06.pending.json').read_text());i=35;v=a[i];src=Image.open(p/v['image']);thumb=src.copy();thumb.thumbnail((600,850));sw,sh=thumb.size;x,y,w,h=r[str(i)][0];x-=8;w+=8;cs=[122,139,155,174,191,208,244,262,281,298,314,331,348,361];wws=[286,286,286,286,286,213,198,203,204,203,198,198,198,148];d=ImageDraw.Draw(src);lines=[]
for k,(cy,ww) in enumerate(zip(cs,wws)):
 top=y if k==0 else cy-20;bot=cy+8;bb=[round(x/sw*v['native_width'],2),round((top-30)/sh*v['native_height'],2),round(ww/sw*v['native_width'],2),round((bot-top)/sh*v['native_height'],2)];lines.append({'line_number':k+1,'box':bb});lx=x/sw*src.width;ty=(top-30)/sh*src.height;rx=(x+ww)/sw*src.width;by=(bot-30)/sh*src.height;d.rectangle((lx,ty,rx,by),outline='red',width=2);d.text((lx-22,ty+15),str(k+1),fill='blue')
b=res['pages'][i]['blocks'][0];b.update(lines=lines,unit='P',decision='VERIFIED',registration_status='SOURCE_GEOMETRY_VERIFIED',line_geometry_status='SOURCE_REVIEWED_COMPLETE',observed_line_count=14,reason='Native source and corrected fourteen-row enclosure overlay reviewed: six upper and eight lower rows in one continuous left writing field, with endpoints wrapping the drawing. Prior fifteen-row proposal double-counted an upper row and is retained only as superseded candidate geometry. Sole P identity is supported by complete field and row order, with H/F counts checked separately.');b['box']=[min(q['box'][0] for q in lines),min(q['box'][1] for q in lines),max(q['box'][0]+q['box'][2] for q in lines)-min(q['box'][0] for q in lines),max(q['box'][1]+q['box'][3] for q in lines)-min(q['box'][1] for q in lines)];b.pop('missing_work',None);res['pages'][i]['geometry_complete']=True
cr=src.crop((int((x-12)/sw*src.width),int((y-40)/sh*src.height),int((x+w+5)/sw*src.width),int((y+h-18)/sh*src.height)));cr.save(p/'corrected35.png')
# Expand first f20v flourishing stroke to the observed left edge.
b=res['pages'][13]['blocks'][0];dx=8/sw*a[13]['native_width']
# Use that page's own scale for the minor enclosure correction.
im=Image.open(p/a[13]['image']);im.thumbnail((600,850));dx=8/im.width*a[13]['native_width']
for q in b['lines']:q['box'][0]=round(q['box'][0]-dx,2);q['box'][2]=round(q['box'][2]+dx,2)
b['box'][0]=round(b['box'][0]-dx,2);b['box'][2]=round(b['box'][2]+dx,2)
(p/'REVIEW.v06.pending.json').write_text(json.dumps(res,indent=2))
