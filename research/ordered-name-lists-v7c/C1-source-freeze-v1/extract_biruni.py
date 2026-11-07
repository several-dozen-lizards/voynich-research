import pypdf,json
from pathlib import Path
r=Path(__file__).parent
d=pypdf.PdfReader(r/'sources/biruni-sachau1879.pdf')
t=[p.extract_text() for p in d.pages]
(r/'sources/biruni-pages.json').write_text(json.dumps(t,ensure_ascii=False),encoding='utf8')
for i,s in enumerate(t):
 if ('Mansions' in s or 'mansions' in s or 'Edinburgh' in s): print(i+1,s[:100].replace('\n',' '))
