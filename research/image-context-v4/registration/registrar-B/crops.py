import json
from PIL import Image
from pathlib import Path
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text())
for i in [18,19,21,22,24,25,26,27,31,32,33,35,36,37,38,42,43,44,45,46,47,48,49,50]:
 v=a[i];im=Image.open(p/v['image']);w,h=im.size;thumb=im.copy();thumb.thumbnail((600,850));sw,sh=thumb.size
 regs=r[str(i)];x=min(q[0] for q in regs);y=min(q[1] for q in regs)-30;rr=max(q[0]+q[2] for q in regs);bb=max(q[1]+q[3] for q in regs)-30
 box=(max(0,(x-12)/sw*w),max(0,(y-10)/sh*h),min(w,(rr+10)/sw*w),min(h,(bb+10)/sh*h));cr=im.crop(tuple(map(int,box)));cr.thumbnail((1300,1700));cr.save(p/('sourcecrop%02d.png'%i))
