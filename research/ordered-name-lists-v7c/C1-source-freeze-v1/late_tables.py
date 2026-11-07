import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent/'attempt-2-v7.1/vendor'))
from bs4 import BeautifulSoup
r=Path(__file__).parent
s=BeautifulSoup((r/'sources/heptameron-peterson.html').read_text(encoding='cp1252'),'html.parser')
out=[]
for t in s.find_all('table'):
 st=t.get_text(' ',strip=True)
 if ('Yayn' in st or 'yayn' in st) and len(st)<10000:
  out.append([[c.get_text(' ',strip=True) for c in row.find_all(['td','th'],recursive=False)] for row in t.find_all('tr',recursive=False)])
(r/'sources/heptameron-hour-tables.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
