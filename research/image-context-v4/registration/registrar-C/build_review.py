import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-C'); a=json.loads((p/'PAGES.json').read_text())
# Rectangles use source-only contact-sheet pixel frame, x local to page, y includes the 35px title margin.
R={0:[(90,60,565,691),(565,140,600,780)],1:[(65,62,540,785),(0,90,35,700)],2:[(130,70,565,773),(560,150,600,740)],3:[(65,60,528,774),(0,63,28,752)],4:[(135,72,556,761)],5:[(50,57,539,744),(0,65,35,650)],6:[(49,79,509,485),(60,488,510,790),(0,80,30,750)],7:[(85,125,455,325)],8:[(155,110,525,300)],9:[(83,126,522,211),(86,211,373,372)],10:[(165,175,446,567)],11:[(85,127,449,357)],12:[(114,419,259,508),(329,436,541,514),(108,510,304,636),(320,529,533,644)],13:[(75,158,450,422)],14:[(155,119,390,421),(458,132,539,203)],15:[(80,109,333,468)],16:[(170,104,525,225)],17:[(88,120,478,269),(98,515,450,675)],18:[(180,123,540,285)],19:[(80,135,470,270),(78,452,465,594)],20:[(142,133,555,290)],21:[(75,100,515,215)],22:[(150,120,565,285)],23:[(82,113,448,309)],24:[(147,128,410,546)],25:[(55,105,480,350)],26:[(100,120,361,402),(468,292,555,379)],27:[(82,116,346,272),(82,267,465,459),(89,466,398,642)],28:[(165,103,550,315)],29:[(57,119,430,315)],30:[(110,100,533,208),(345,181,532,254)],31:[(63,93,470,222)],32:[(163,121,465,599),(461,383,544,599)],33:[(73,108,495,275)],34:[(183,121,406,348),(450,127,561,249)],35:[(60,510,300,677),(307,579,416,656)],36:[(145,125,459,393)],37:[(72,124,428,477)],38:[(115,95,495,673)],39:[(155,160,510,292)],40:[(100,112,470,192),(43,192,500,646)],41:[(79,98,240,438),(295,109,525,440),(82,436,527,721),(190,163,241,247)],42:[(92,148,478,358),(98,373,488,707),(32,79,508,150),(36,370,91,400),(44,620,103,649)],43:[(203,95,555,352),(205,486,548,678)],44:[(59,141,481,418),(60,435,476,520),(111,517,459,623),(72,617,462,718),(53,51,492,148)],45:[(172,109,540,477),(165,586,231,615)],46:[(86,87,497,445),(254,445,491,740),(41,651,245,723),(90,482,243,644)],47:[(128,141,527,675),(383,87,519,125),(523,393,568,462),(521,538,561,620)],48:[(119,219,523,308),(137,437,496,525),(121,605,472,708),(125,99,496,144),(113,550,220,592),(110,313,558,370),(437,520,482,550)],49:[(82,94,494,641)],50:[(95,210,526,286),(110,358,530,429),(98,497,525,576),(78,701,459,811),(94,65,528,202),(128,278,540,310),(115,427,514,463),(134,578,197,611)]}
# Manually located source-row centers. Each remains a geometric envelope, not transcription.
V={7:('P',[155,172.5,190.5,208,227.5,245.5,264,283,300,316.5],12),8:('P',[142.5,161.5,180,198.5,217,235.5,252.5,270.5,287.5],13),13:('P',[199.5,218,236.5,263.5,281.5,299.5,317,338,356,374,392.5,409.5],13),16:('P',[122,138.5,155,171.5,188,205,220],12),21:('P',[120,135.5,150.5,165.5,179,193.5,208],11),22:('P',[142,155.5,167.5,179.5,192,210.5,223.5,237,250.5,264,278.5],10),29:('P',[146,163,178,194,212,229,245,263,280,295,309],13),31:('P',[115,127,139.5,151.5,164,175.5,187,199.5,211],12),33:('P',[130,145,160,175,189.5,204,219.5,234,249,265],12),39:('P',[184,205,224,244,261,282],14),40:('P',[130,148,165,182],13)}
# Accepted separated rows on the final two pages, source-order and distinct physical fields.
M={48:[('P1',[237,255,271,287.5,301.5],13),('P2',[455,473,488.5,505,516.5],13),('P3',[620,637.5,652.5,669,687.5,702.5],13)],50:[('P1',[230,246.5,264,280.5],15),('P2',[375,392,408.5,423],14),('P3',[522,538.5,555,569],14)]}
def native(v,r):
 x1,y1,x2,y2=r; sw=600; sh=round(Image.open(p/v['image']).height*600/Image.open(p/v['image']).width)
 return [round(x1*v['native_width']/sw,2),round((y1-35)*v['native_height']/sh,2),round((x2-x1)*v['native_width']/sw,2),round((y2-y1)*v['native_height']/sh,2)]
out={'registrar_id':'blind_registrar_C','fresh_context':True,'outcome_blind':True,'picture_boxes_unseen':True,'pages':[],'unreviewed_pages':[]}
for i,v in enumerate(a):
 blocks=[]
 for j,r in enumerate(R[i]):
  blocks.append({'block_id':f'B{j+1:03}','unit':None,'box':native(v,r),'lines':[],'decision':'UNREGISTERED','reason':'Visible writing region inspected in source pixels. Complete individual row envelopes and/or unique P-unit identity remain unresolved; region retained as an explicit abstention, without forcing the supplied counts.'})
 out['pages'].append({'task_id':v['task_id'],'folio':v['folio'],'reviewed':True,'blocks':blocks,'notes':'Entire assigned source page inspected. Broad abstention envelopes can contain intervening drawing where writing is interrupted; these are not verified line geometry. Small marginal numerals or isolated marks are not assigned to P units. No words were transcribed or picture categories assigned.'})
(p/'REVIEW-v01.json').write_text(json.dumps(out,indent=2))
for i,(unit,centers,h) in V.items():
 b=out['pages'][i]['blocks'][0]; r=R[i][0]; b.update(unit=unit,lines=[{'line_number':k+1,'box':native(a[i],(r[0],y-h,r[2],y+h))} for k,y in enumerate(centers)],decision='VERIFIED',reason='Enlarged source pixels show this single coherent writing field with the listed physical rows in top-to-bottom order. Paragraph starts do not create additional fields. Unique supplied P locator agrees with the independently observed field; geometry was not removed to fit a count.')
 # expand block to contain all envelopes
 b['box']=native(a[i],(r[0],min(r[1],min(centers)-h),r[2],max(r[3],max(centers)+h)))
for i,vals in M.items():
 for j,(unit,centers,h) in enumerate(vals):
  b=out['pages'][i]['blocks'][j];r=R[i][j];b.update(unit=unit,lines=[{'line_number':k+1,'box':native(a[i],(r[0],y-h,r[2],y+h))} for k,y in enumerate(centers)],decision='VERIFIED',reason='Enlarged source shows a separate horizontal writing field between intervening non-writing areas. Physical top-to-bottom order identifies this supplied P unit independently; all visible rows are retained.')
  b['box']=native(a[i],(r[0],min(r[1],min(centers)-h),r[2],max(r[3],max(centers)+h)))
(p/'REVIEW-v02.json').write_text(json.dumps(out,indent=2))
(p/'REVIEW.json').write_text(json.dumps(out,indent=2))
# Overlay accepted rectangles, with original source underlying. These are reviewed before final acceptance.
for n in range(0,51,3):
 sheet=Image.new('RGB',(1800,920),'#dddddd');d=ImageDraw.Draw(sheet)
 for j,v in enumerate(a[n:n+3]):
  im=Image.open(p/v['image']); im.thumbnail((600,880)); dr=ImageDraw.Draw(im)
  for b in out['pages'][n+j]['blocks']:
   if b['decision']!='VERIFIED':continue
   for l in b['lines']:
    x,y,w,h=l['box'];sx=im.width/v['native_width'];sy=im.height/v['native_height'];dr.rectangle((x*sx,y*sy,(x+w)*sx,(y+h)*sy),outline='red',width=1);dr.text((x*sx,y*sy),str(l['line_number']),fill='blue')
  sheet.paste(im,(j*600,35));d.text((j*600+8,8),str(n+j)+' '+v['folio'],fill='black')
 sheet.save(p/f'overlay{n//3:02}.jpg')
print('51 reviewed; verified',sum(b['decision']=='VERIFIED' for q in out['pages'] for b in q['blocks']))
