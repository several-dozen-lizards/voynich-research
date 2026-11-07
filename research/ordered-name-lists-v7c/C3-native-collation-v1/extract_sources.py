from pathlib import Path
from lxml import etree as E
import json,re
P=Path(__file__).parent
root=E.parse(str(P/'sources/lapidary-1881-ocr.xml'))
pages=[]
for i,obj in enumerate(root.findall('.//OBJECT'),1):
 lines=[' '.join(''.join(w.itertext()) for w in line.findall('WORD')) for line in obj.findall('.//LINE')]
 pages.append(dict(pdf_page=i,text='\n'.join(lines)))
(P/'sources/lapidary-1881-ocr-pages.json').write_text(json.dumps(pages,ensure_ascii=False)+'\n')
print('OCR objects',len(pages))
for x in pages:
 if 328<=x['pdf_page']<=333 or 356<=x['pdf_page']<=360:
  for m in re.finditer(r'.{0,65}(?:sufre|Piscos|Piseos|Tezc|Yeth|treinta|treinteno).{0,150}',x['text'],re.I):print(x['pdf_page'],m.group(0))
# TEI list boundaries are edition-specific: carry the final four names from section3.
x=E.parse(str(P/'sources/xenophon-perseus.xml'));ns={'t':'http://www.tei-c.org/ns/1.0'}
base=x.xpath("//t:div[@subtype='book'][@n='2']/t:div[@subtype='chapter'][@n='3']",namespaces=ns)[0]
sections={s.get('n'):' '.join(''.join(s.itertext()).split()) for s in base.findall('{*}div')}
a=sections['2'].split('οἵδε·',1)[1];b=sections['3'].split('τούτων',1)[0]
names=[s.strip(' .\n') for s in (a+b).split(',') if s.strip(' .\n')]
assert len(names)==30
rows=[dict(position=i+1,name=n,script='Greek',edition='Marchant1900_Perseus',section='2.3.2' if i<26 else '2.3.3',modernized_English_is_not_variant=True) for i,n in enumerate(names)]
(P/'GREEK-ROSTER-EXTRACT.json').write_text(json.dumps(dict(rows=rows,source='sources/xenophon-perseus.xml',status='DIGITAL_EDITION_EXTRACT_NOT_MANUSCRIPT_DIPLOMATIC'),ensure_ascii=False,indent=2)+'\n')
print('Greek roster',names)
