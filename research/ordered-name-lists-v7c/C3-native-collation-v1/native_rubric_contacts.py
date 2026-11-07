from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
P=Path(__file__).parent
old=P.parent/'C3-revised-plan-v1/historical-sources'
files=[old/'FOL-0001V.jpg',old/'FOL-0002R.jpg',old/'FOL-0002V.jpg']+sorted((P/'sources').glob('FOL-*.jpg'))
strips=[];receipts=[]
for path in files:
 im=Image.open(path).convert('RGB');w,h=im.size;a=np.asarray(im).astype(float)
 for col,(x0,x1) in enumerate(((.18,.49),(.49,.81)),1):
  l,r=int(w*x0),int(w*x1);mask=(a[:,:,0]>a[:,:,1]*1.25)&(a[:,:,0]>a[:,:,2]*1.20)&(a[:,:,0]>75)
  counts=mask[:,l:r].sum(axis=1);ys=np.where((counts>4)&(np.arange(h)>h*.18)&(np.arange(h)<h*.76))[0]
  groups=[]
  for y in ys:
   if not groups or y-groups[-1][-1]>14:groups.append([y])
   else:groups[-1].append(y)
  for j,g in enumerate(groups):
   if len(g)<2:continue
   box=(l,max(0,int(g[0])-8),r,min(h,int(g[-1])+72))
   crop=im.crop(box);crop=crop.resize((600,round(crop.height*600/crop.width)))
   if crop.height>650:crop=crop.crop((0,0,600,650))
   label=f'{path.stem} col{col} red{j+1}'
   strips.append((label,crop));receipts.append(dict(id=label,source=str(path),box=list(box),status='AUTO_RED_REGION_LOCATOR_NOT_TEXT_VERIFICATION'))
for page in range(0,len(strips),10):
 rows=strips[page:page+10];height=sum(max(rows[i][1].height,rows[i+1][1].height if i+1<len(rows) else 0)+32 for i in range(0,len(rows),2))
 out=Image.new('RGB',(1220,height),'white');draw=ImageDraw.Draw(out);y=0
 for i in range(0,len(rows),2):
  hh=0
  for k in range(2):
   if i+k>=len(rows):continue
   label,im=rows[i+k];draw.text((k*610,y),label,fill='black');out.paste(im,(k*610,y+24));hh=max(hh,im.height)
  y+=hh+32
 out.save(P/'qa'/f'native-aries-rubrics-{page//10+1}.png')
(P/'qa/NATIVE-CROP-LOCATORS.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('native red regions',len(strips),'contact pages',(len(strips)+9)//10)
