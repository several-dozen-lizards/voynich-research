from pathlib import Path
import json,sys
from PIL import Image,ImageDraw
R=Path(sys.argv[1]);entries=json.loads((R/'ENTRY-BOUNDARIES.json').read_text())['entries'];q=json.loads((R/'REFLOWED-A-INSPECTION.json').read_text());bounds={r['scan']:r for r in q['bounds']};out=R/'qa-incbits';out.mkdir(exist_ok=True)
for e in entries:
 im=Image.open(R/'qa-pages'/('page-'+str(e['scan']+1)+'.png'));b=bounds[e['scan']];sx=im.width/2470;sy=im.height/3585
 x=b['start']+e['col']*870;y=max(0,e['y']-35)
 crop=im.crop((int(x*sx),int(y*sy),min(im.width,int((x+880)*sx)),min(im.height,int((y+750)*sy))))
 crop.thumbnail((500,420));canvas=Image.new('RGB',(520,450),'white');canvas.paste(crop,(10,25));ImageDraw.Draw(canvas).text((10,5),str(e['chapter'])+' '+e['name']+' scan'+str(e['scan']),fill='black');canvas.save(out/(str(e['chapter']).zfill(2)+'.png'))
for batch in range(6):
 sheet=Image.new('RGB',(1560,900),'white')
 for k in range(6):
  i=batch*6+k
  if i<len(entries):sheet.paste(Image.open(out/(str(i+1).zfill(2)+'.png')),((k%3)*520,(k//3)*450))
 sheet.save(R/('QA-SHEET-'+str(batch+1)+'.png'))
