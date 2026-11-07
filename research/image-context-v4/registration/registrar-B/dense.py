import json,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());out={}
for i in [0,1,2,4,5,6,42,43,44,45,46,47]:
 v=a[i];src=Image.open(p/v['image']);src.thumbnail((600,850)); ar=np.array(src);x,y,w,h=r[str(i)][0];y-=30
 gray=ar.mean(2);dark=np.clip(150-gray,0,100)
 # Central-left text strip avoids marginal symbols and most illustration edges.
 x1=x+30;x2=x+int(w*.63)
 sig=gaussian_filter1d(dark[y:y+h,x1:x2].mean(1),1)
 peaks,_=find_peaks(sig,distance=9,prominence=1.3)
 cs=[int(z+y+30) for z in peaks];out[i]=cs
 d=ImageDraw.Draw(src)
 for j,cy in enumerate(cs):d.line((x,cy-30,x+w,cy-30),fill='red');d.text((x-16,cy-37),str(j+1),fill='blue')
 src.crop((max(0,x-20),max(0,y-10),min(600,x+w+10),min(src.height,y+h+10))).resize(((w+30)*2,(h+20)*2)).save(p/('dense%02d.png'%i))
 print(i,len(cs),cs)
(p/'dense_centers.json').write_text(json.dumps(out))
