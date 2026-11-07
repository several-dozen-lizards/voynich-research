import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'attempt-2-v7.1/vendor'))
from bs4 import BeautifulSoup
r=Path(__file__).parent
out=[]
for p in sorted((r/'sources').glob('boudet-0*.html')):
 s=BeautifulSoup(p.read_bytes(),'html.parser'); t=s.select_one('div.text') or s
 out.append(dict(page=p.stem[-4:],text=t.get_text(' ',strip=True)))
(r/'sources/boudet-all-pages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for p in out:
 if any(x in p['text'].lower() for x in ['bohel','saturn','samael','orphani']): print(p['page'],p['text'])
