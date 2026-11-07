"""Image-only provisional writing geometry. No transcription or rater-picture inputs."""
from pathlib import Path
import json,hashlib,cv2,numpy as np
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).resolve().parent;W=R/'registrar-only'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def geometry(path,nw,nh):
 im=cv2.imread(str(path));assert im is not None
 gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);h,w=gray.shape
 # Adaptive local contrast: thresholds scale with image dimensions and measured ink size.
 window=max(15,int(min(h,w)*.025)//2*2+1)
 ink=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,window,15)
 hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV);ink[hsv[:,:,1]>150]=0
 n,lab,stats,_=cv2.connectedComponentsWithStats(ink,8)
 candidates=[s for s in stats[1:] if 2<=s[cv2.CC_STAT_HEIGHT]<=h*.035 and 1<=s[cv2.CC_STAT_WIDTH]<=w*.06 and 3<=s[cv2.CC_STAT_AREA]<=h*w*.001]
 typical=float(np.median([s[cv2.CC_STAT_HEIGHT] for s in candidates])) if candidates else 6.
 typical=max(3.,typical)
 clean=np.zeros_like(ink)
 for i,s in enumerate(stats[1:],1):
  x,y,cw,ch,area=map(int,s)
  if 2<=ch<=max(typical*3,h*.012) and 1<=cw<=w*.06 and 3<=area<=h*w*.001:clean[lab==i]=255
 # Horizontal joining proposes lines; drawings can survive, so independent review is mandatory.
 joined=cv2.dilate(clean,cv2.getStructuringElement(cv2.MORPH_RECT,(max(3,round(typical*2)),1)))
 nn,ll,ss,_=cv2.connectedComponentsWithStats(joined,8);lines=[]
 for s in ss[1:]:
  x,y,cw,ch,area=map(int,s)
  if cw<w*.075 or ch<typical*.45 or ch>typical*3.5:continue
  yy,xx=np.where(clean[y:y+ch,x:x+cw]>0)
  if not len(xx):continue
  bx,by=x+int(xx.min()),y+int(yy.min());bw,bh=int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)
  lines.append([bx,by,bw,bh])
 lines.sort(key=lambda b:(b[1]+b[3]/2,b[0]));groups=[]
 # Group proximate horizontal writing runs by measured line height and overlap.
 for b in lines:
  possible=[]
  for gi,g in enumerate(groups):
   prev=g[-1];gap=b[1]-(prev[1]+prev[3]);overlap=min(b[0]+b[2],prev[0]+prev[2])-max(b[0],prev[0]);mh=max(typical,float(np.median([r[3] for r in g])))
   if -.3*mh<=gap<=2.5*mh and overlap>=.3*min(b[2],prev[2]):possible.append((gap,gi))
  if possible:groups[min(possible)[1]].append(b)
  else:groups.append([b])
 def native(b):return [round(b[0]/w*nw,3),round(b[1]/h*nh,3),round(b[2]/w*nw,3),round(b[3]/h*nh,3)]
 blocks=[]
 for g in groups:
  x=min(b[0] for b in g);y=min(b[1] for b in g);x2=max(b[0]+b[2] for b in g);y2=max(b[1]+b[3] for b in g)
  blocks.append(dict(box=native([x,y,x2-x,y2-y]),lines=[dict(line_number=i+1,box=native(b)) for i,b in enumerate(g)],status='PROVISIONAL_UNREVIEWED'))
 blocks.sort(key=lambda b:(b['box'][1],b['box'][0]))
 for i,b in enumerate(blocks):b['block_id']=f'B{i+1:03}'
 return dict(blocks=blocks,parameters=dict(raster_width=w,raster_height=h,measured_component_height=typical,adaptive_window=window),status='CANDIDATES_ONLY_NOT_ACCEPTED')
def main():
 pages=json.loads((W/'PAGES.json').read_text());out=[]
 for i,p in enumerate(pages):
  try:r=geometry(W/p['image'],p['native_width'],p['native_height']);r.update(task_id=p['task_id'],folio=p['folio'])
  except Exception as exc:r=dict(task_id=p['task_id'],folio=p['folio'],blocks=[],status='EXTRACTION_FAILED',error=str(exc))
  out.append(r)
  if (i+1)%20==0:print('Geometry',i+1,'/',len(pages),flush=True)
 save(W/'GEOMETRY-CANDIDATES.json',out)
 print('Candidate blocks',sum(len(r['blocks']) for r in out),flush=True)
if __name__=='__main__':main()
