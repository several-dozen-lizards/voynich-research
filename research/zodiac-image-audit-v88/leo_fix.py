from pathlib import Path
from PIL import Image,ImageDraw
import json,math
P=Path(__file__).resolve().parent; old=P.parent/'zodiac-mapping-v84'
bad=P/'misregistered-leo'; bad.mkdir(exist_ok=True)
for p in P.glob('f72v3-*.jpg'): p.rename(bad/p.name)
ann=json.loads((old/'ANNOTATIONS.json').read_text()); panel=next(p for p in ann if p['folio']=='f72v3')
im=Image.open(old/'leo-wide.jpg'); w,h=im.size; region=panel['region']; tiles=[]; manifest=[]
for r in panel['rows']:
    x=(r['head'][0]-region[0])*w/region[2]; y=(r['head'][1]-region[1])*h/region[3]
    vx=w/2-x; vy=h/2-y; length=max(1,math.hypot(vx,vy)); shift=min(w,h)*.045
    cx=x+vx/length*shift; cy=y+vy/length*shift; side=round(min(w,h)*.21)
    box=(max(0,round(cx-side/2)),max(0,round(cy-side/2)),min(w,round(cx+side/2)),min(h,round(cy+side/2)))
    angle=math.degrees(math.atan2(vy,vx))-90
    crop=im.crop(box).rotate(angle,resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(235,225,204));crop.thumbnail((300,300))
    tile=Image.new('RGB',(320,335),'#eee6d4');tile.paste(crop,((320-crop.width)//2,25+(300-crop.height)//2));ImageDraw.Draw(tile).text((8,7),r['id'],fill='black');tiles.append(tile)
    manifest.append({'id':r['id'],'source':'leo-wide.jpg','box':box,'rotation':angle})
for start in range(0,len(tiles),12):
    batch=tiles[start:start+12];out=Image.new('RGB',(960,335*math.ceil(len(batch)/3)),'#eee6d4')
    for j,t in enumerate(batch):out.paste(t,((j%3)*320,(j//3)*335))
    out.save(P/f'f72v3-{start//12+1}.jpg',quality=95)
(P/'LEO-CROP-CORRECTION.json').write_text(json.dumps({'reason':'Initial audit used leo-crop.jpg but v84 coordinates correspond to leo-wide.jpg. Initial sheets retained in misregistered-leo, not admissible figure-level audit evidence. Corrected sheets use canonical wide image, limited local crops only. No new Leo count inferred.','crops':manifest},indent=2),encoding='utf-8')
