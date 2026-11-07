import json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:\Users\lewis\OneDrive\Documents\ChatGPT\Voynich\image-context-v4\registration\registrar-B')
a=json.loads((p/'PAGES.json').read_text())
for start in range(0,len(a),3):
 out=Image.new('RGB',(1800,900),'white');d=ImageDraw.Draw(out)
 for k,v in enumerate(a[start:start+3]):
  im=Image.open(p/v['image']);im.thumbnail((600,850));out.paste(im,(k*600,30));d.text((k*600+5,5),str(start+k)+' '+v['folio'],fill='black')
  for y in range(100,851,100): d.text((k*600,y+30),str(y),fill='red')
  for x in range(100,600,100):d.text((k*600+x,30),str(x),fill='red')
 out.save(p/('sheet%02d.jpg'%start))
