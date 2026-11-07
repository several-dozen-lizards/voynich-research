import pypdf,json,re
from pathlib import Path
R=Path(__file__).parent
p=pypdf.PdfReader(R/'modernized-locator.pdf');pages=[x.extract_text() for x in p.pages]
(R/'locator-pages.json').write_text(json.dumps(pages,ensure_ascii=False),encoding='utf8')
for i in [0,1,2,3,7,13,14,15]:print('\nPAGE',i+1,'\n',pages[i][:2000])
