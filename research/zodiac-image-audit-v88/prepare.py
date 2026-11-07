from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent; OLD=P.parent/'zodiac-mapping-v84'
ann=json.loads((OLD/'ANNOTATIONS.json').read_text(encoding='utf-8'))
files={'f70v1':'f70v1.jpg','f71r':'f71r.jpg','f71v':'f71v.jpg','f72r1':'f72r1.jpg','f70v2':'f70v2.jpg','f72r2':'f72r2.jpg','f72r3':'f72r3-expanded.jpg','f72v3':'leo-crop.jpg'}
manifest=[]
for panel in ann:
    f=panel['folio']; im=Image.open(OLD/files[f]); w,h=im.size; region=panel['region']; tiles=[]
    for r in panel['rows']:
        x=(r['head'][0]-region[0])*w/region[2]; y=(r['head'][1]-region[1])*h/region[3]
        # Shift modestly inward to include torso/vessel; retain broad source context.
        vx=w/2-x; vy=h/2-y; length=max(1,math.hypot(vx,vy)); shift=min(w,h)*.055
        cx=x+vx/length*shift; cy=y+vy/length*shift; side=round(min(w,h)*.28)
        box=(round(cx-side/2),round(cy-side/2),round(cx+side/2),round(cy+side/2))
        crop=im.crop(box)
        # Rotate around crop center so the inward torso direction points down.
        angle=math.degrees(math.atan2(vy,vx))-90
        crop=crop.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(235,225,204))
        crop.thumbnail((300,300)); tile=Image.new('RGB',(320,335),'#eee6d4'); tile.paste(crop,((320-crop.width)//2,25+(300-crop.height)//2)); ImageDraw.Draw(tile).text((8,7),r['id'],fill='black')
        tiles.append(tile); manifest.append({'id':r['id'],'source':files[f],'source_size':[w,h],'box':box,'rotation':angle})
    for start in range(0,len(tiles),12):
        batch=tiles[start:start+12]; canvas=Image.new('RGB',(960,335*math.ceil(len(batch)/3)),'#eee6d4')
        for j,t in enumerate(batch): canvas.paste(t,((j%3)*320,(j//3)*335))
        canvas.save(P/f'{f}-{start//12+1}.jpg',quality=95)
(P/'CROP-MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(P/'AUDIT-PROTOCOL.json').write_text(json.dumps({'scope':'Eight development panels only; no held-out images, degree sequences or alignment fits consulted during visual readback. Same agent, previously exposed; not independently blinded human annotation. First two whole-panel images and first-pass script inspected before this protocol.', 'method':'Use image-only crops with location IDs and source context, no prior feature values on sheets. Record visible garment/bare/uncertain and vessel/absent/uncertain with evidence; compare to frozen old labels after saving observations. Rotation/cropping for inspection only; original pixels remain reference. Approximate existing locations may misregister; do not resolve from old classification.', 'criteria':'Garment requires visible neckline/sleeve/fabric structure; paint alone insufficient. Bare requires readable exposed torso anatomy/contour without garment structure. Vessel requires rim and containing wall around lower body; a decorative border alone insufficient. Unclear, occluded or cut-off remains uncertain. Presence uncertainty remains separate. No sex inference, glyph reading or pigment classification.', 'no_scoring':'No alignment scoring or new winning rule in this audit. Revised features require a separately frozen subsequent application.', 'source_sha256':{n:hashlib.sha256((OLD/n).read_bytes()).hexdigest() for n in files.values()},'inventory_sha256':hashlib.sha256((OLD/'ANNOTATIONS.json').read_bytes()).hexdigest()},indent=2),encoding='utf-8')
print('Prepared development-only image sheets; prior feature labels omitted.')
