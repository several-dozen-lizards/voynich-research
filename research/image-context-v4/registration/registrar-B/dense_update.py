import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());c=json.loads((p/'dense_centers.json').read_text());res=json.loads((p/'REVIEW.v02.json').read_text())
adds={1:[138,227,240,455,651,760],2:[251,343,378,528],4:[257,407,421,668,680],6:[375]}
for i,ys in adds.items():
 cs=sorted(c[str(i)]+ys);v=a[i];im=Image.open(p/v['image']);im.thumbnail((600,850));sw,sh=im.size;x,y,w,h=r[str(i)][0];d=ImageDraw.Draw(im)
 def nat(xx,yy,ww,hh):return [round(xx/sw*v['native_width'],2),round((yy-30)/sh*v['native_height'],2),round(ww/sw*v['native_width'],2),round(hh/sh*v['native_height'],2)]
 lines=[]
 for k,cy in enumerate(cs):
  top=y if k==0 else cy-21;bottom=cy+9
  lines.append({'line_number':k+1,'box':nat(x,top,w,bottom-top)});d.rectangle((x,top-30,x+w,bottom-30),outline='red');d.text((x-17,cy-37),str(k+1),fill='blue')
 b=res['pages'][i]['blocks'][0];b.update(unit='P',lines=lines,observed_line_count=len(lines),decision='VERIFIED',reason='Enlarged source overlay reviewed row by row. Projection proposals missed visible rows, which were restored from pixels rather than count-fitting. One coherent uninterrupted writing field, complete source row order and sole P locator independently support identity; H/F counts agree separately. Overlapping ascender/descender envelopes are retained.')
 bottom=max(q['box'][1]+q['box'][3] for q in lines);b['box']=nat(x,y,w,h);b['box'][3]=round(max(b['box'][3],bottom-b['box'][1]),2)
 im.crop((x-20,y-40,x+w+5,min(sh,cs[-1]-30+15))).resize(((w+25)*2,(cs[-1]-y+25)*2)).save(p/('finaldense%02d.png'%i))
# Actual overlays revealed unresolved lateral extents; retain these as abstentions.
for i in [13,34,41]:
 b=res['pages'][i]['blocks'][0];b.update(unit=None,decision='UNREGISTERED',reason='Numbered source overlay confirms the retained visible rows, but lateral writing endpoints near drawing interruptions are not securely enclosed by all proposed line rectangles. Preserve this source field without certifying complete line geometry or P identity. No rows were deleted to fit counts.')
for i in [0,5]:
 res['pages'][i]['blocks'][0]['reason']='Enlarged source-only overlay inspected. Automated projection proposals disagree with visible source row geometry: slanted baselines, short rows and tall markers/ascenders produce missed or duplicate proposals. A complete corrected set is not securely resolved; observed field retained and P registration withheld. This is an explicit segmentation abstention, not rejection of overlapping boxes.'
# Save before final crop inspection.
(p/'REVIEW.v03.json').write_text(json.dumps(res,indent=2));(p/'REVIEW.json').write_text(json.dumps(res,indent=2))
print([(a[i]['folio'],len(res['pages'][i]['blocks'][0]['lines'])) for i in adds])
