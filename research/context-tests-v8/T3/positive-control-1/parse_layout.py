import xml.etree.ElementTree as ET,json,sys
from pathlib import Path
R=Path(sys.argv[1]);root=ET.parse(R/'circa-djvu.xml').getroot();pages=[]
for i,obj in enumerate(root.findall('.//OBJECT')):
 lines=[]
 for line in obj.findall('.//LINE'):
  words=[{'text':(w.text or ''),'coords':list(map(int,w.attrib['coords'].split(',')))} for w in line.findall('WORD')]
  if words:lines.append({'text':' '.join(w['text'] for w in words),'words':words})
 pages.append({'scan':i,'width':int(obj.attrib['width']),'height':int(obj.attrib['height']),'lines':lines})
(R/'OCR-LAYOUT.json').write_text(json.dumps(pages,ensure_ascii=False),encoding="utf-8")
print('pages',len(pages))
for p in pages:
 text=' '.join(l['text'] for l in p['lines'])
 if any(s in text.lower() for s in ['circa in','platear','de aloe','a loe']):
  if p['scan']>250: print(p['scan'],p['width'],p['height'],text[:300].encode('ascii','backslashreplace').decode())
