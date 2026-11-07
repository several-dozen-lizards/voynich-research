from pathlib import Path
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
import json
P=Path(__file__).parent
r=PdfReader(P/'sources/lapidary-1881.pdf');pages=[p.extract_text() for p in r.pages]
(P/'sources/lapidary-1881-pages.json').write_text(json.dumps(pages,ensure_ascii=False)+'\n')
print('Lapidary pages',len(pages))
for i,p in enumerate(pages):
 if 'magn' in p.lower() or 'zurud' in p.lower():print(i+1,p[:100])
doc=pdfium.PdfDocument(str(P/'sources/xenophon-bude.pdf'))
nums=list(range(125,154,2));out=Image.new('RGB',(1250,400*((len(nums)+4)//5)),'white');draw=ImageDraw.Draw(out)
for j,num in enumerate(nums):
 im=doc[num-1].render(scale=.5).to_pil();im.thumbnail((245,370));x=(j%5)*250;y=(j//5)*400;out.paste(im,(x,y+25));draw.text((x,y),str(num),fill='black')
out.save(P/'qa/xenophon-contact.png')
