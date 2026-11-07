from pathlib import Path
from pypdf import PdfReader
import json
P=Path(__file__).parent
r=PdfReader(P/'sources/xenophon-bude.pdf');pages=[p.extract_text() for p in r.pages]
(P/'sources/xenophon-bude-pages.json').write_text(json.dumps(pages,ensure_ascii=False)+'\n')
print('pages',len(pages))
for i,p in enumerate(pages):
 if any(x in p for x in ('Πολυχ','Μηλόβ','Μηλόβ','Parisinus 1738')):print(i+1,p[:6500])
