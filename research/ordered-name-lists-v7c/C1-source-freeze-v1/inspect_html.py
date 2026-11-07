import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'attempt-2-v7.1/vendor'))
from bs4 import BeautifulSoup
r=Path(__file__).parent
s=BeautifulSoup((r/'sources/boudet-article.html').read_text(encoding='utf8'),'html.parser')
t=[{'id':p.get('id'),'text':p.get_text(' ',strip=True)} for p in s.select('div.page')]
(r/'sources/boudet-pages.json').write_text(json.dumps(t,ensure_ascii=False),encoding='utf8')
for p in t:
 if any(x in p['text'].lower() for x in ['bohel','caspiel','cafziel','saturn','orphaniel','3854']): print(p['id'],p['text'][:18000])
