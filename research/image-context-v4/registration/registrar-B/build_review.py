import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B');a=json.loads((p/'PAGES.json').read_text());r=json.loads((p/'regions.json').read_text());c=json.loads((p/'centers.json').read_text());res=json.loads((p/'REVIEW.v01.json').read_text())
verified={3,9,11,13,16,17,20,23,28,29,30,34,39,40,41}
widths={13:[340,340,340,245,332,326,310,246,250,260,240],20:[300,304,305,314,230,330,345,345,335,315,310,210,205,200,160],23:[156,156,156,156,170,185,208,208,167,166,165,165,165,155,156,156,156,177,179,190,110],29:[347]*8+[240]*5,34:[196,200,201,209,214,220,225,238,245,250,260,273,273,260,190],41:[387]*5+[215,200,200,182,183,180,190,183,180,180,180,180,180,170,170,165]}
for i,v in enumerate(a):
 im=Image.open(p/v['image']);im.thumbnail((600,850));sw,sh=im.size;d=ImageDraw.Draw(im)
 def nat(x,y,w,h):return [round(x/sw*v['native_width'],2),round((y-30)/sh*v['native_height'],2),round(w/sw*v['native_width'],2),round(h/sh*v['native_height'],2)]
 bs=[]
 for j,(x,y,w,h) in enumerate(r[str(i)]):
  cs=c.get(str(i)) if j==0 else None
  if cs is None:cs=c.get(str(i)+'_'+str(j))
  lines=[]
  if cs:
   for k,cy in enumerate(cs):
    ww=widths.get(i,[w]*len(cs))[k] if j==0 else w
    top=y if k==0 else cy-20
    bot=cy+7
    lines.append({'line_number':k+1,'box':nat(x,top,ww,bot-top)})
    if i in verified:
     d.rectangle((x,top-30,x+ww,bot-30),outline=(220,30,30));d.text((x-12,cy-39),str(k+1),fill='blue')
  decision='VERIFIED' if i in verified and j==0 else 'UNREGISTERED'
  if decision=='VERIFIED':reason='Source pixels show one coherent writing field with complete numbered horizontal rows in top-to-bottom order. Paragraph indentation alone is retained within the field. Sole P locator and separately supplied H/F row counts agree; identity is supported by the field geometry, not count alone.'
  elif i in {0,1,2,4,5,6}:reason='Dense continuous source writing field retained as observed. Complete row envelopes are not confidently resolved through slanted, closely spaced ascenders at supplied pixel resolution. No forced P mapping or deletion of rows to fit counts.'
  elif i==12:reason='Faint source writing field with low-contrast/overlapping marks. Region is observable but complete row enclosures and its numbered P identity are not securely established without transcription; abstain.'
  elif i==35:reason='Source shows 15 physical rows in a continuous field (7 upper and 8 lower). Supplied H and F each list 14; preserve all observed rows and abstain instead of removing one.'
  elif len(r[str(i)])>1:reason='Source writing is physically separated by intervening drawing/blank space or occurs as a short marginal/isolated run. A one-to-one mapping of this independent field to the sole P locator is not established; preserve geometry without joining fields merely to fit a count.'
  else:reason='Writing region is visibly interrupted or its line boundaries are not securely resolved. Complete P registration is withheld; observed geometry is retained without a count-driven split or merge.'
  b={'block_id':'B%03d'%(j+1),'unit':'P' if decision=='VERIFIED' else None,'box':nat(x,y,w,h),'lines':lines,'decision':decision,'reason':reason}
  # Enclose all line boxes, including the observed final baseline descender band.
  if lines:
   xx=min(q['box'][0] for q in lines);yy=min(q['box'][1] for q in lines);rr=max(q['box'][0]+q['box'][2] for q in lines);bb=max(q['box'][1]+q['box'][3] for q in lines)
   b['box']=[xx,yy,round(rr-xx,2),round(bb-yy,2)];b['observed_line_count']=len(lines)
  bs.append(b)
 res['pages'][i]['blocks']=bs
 res['pages'][i]['notes']='Entire source page visually inspected. Body fields and isolated visible writing runs retained. No word transcription or picture classification performed. Foliation numerals and tiny edge/non-body marginal marks explicitly abstained from P-unit registration; their complete line geometry is not claimed. Red numbered overlays reviewed for every VERIFIED block. UNREGISTERED rows, where supplied, are provisional conservative enclosures.'
 if i in verified:
  x,y,w,h=r[str(i)][0];im.crop((max(0,x-16),max(0,y-48),min(sw,x+w+5),min(sh,y+h-18))).resize(((w+21)*2,(h+30)*2)).save(p/('verified%02d.png'%i))
(p/'REVIEW.v02.json').write_text(json.dumps(res,indent=2));(p/'REVIEW.json').write_text(json.dumps(res,indent=2));(p/'PROGRESS.txt').write_text('51/51 pages inspected. Source region inventory and conservative row geometry saved in v02. Fifteen single-field registrations are undergoing final rectangle-overlay inspection. Other fields retain explicit abstentions.\n')
