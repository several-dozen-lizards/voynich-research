from source_cut_probe import get
from pathlib import Path
from bs4 import BeautifulSoup
import json,urllib.parse,hashlib
p=Path(__file__).parent/'source-cut-2';dest=p/'development/occitan';dest.mkdir(exist_ok=True)
u='https://www.rialc.unina.it/jaufre-i.htm'
b=get(u);(dest/'rialc-index.html').write_bytes(b);s=BeautifulSoup(b,'html.parser')
print('FRAMES',[(f.get('name'),f.get('src')) for f in s.select('frame')],flush=True)
for i,f in enumerate(s.select('frame')):
    url=urllib.parse.urljoin(u,f['src']);b=get(url);path=dest/f'frame-{i}.html';path.write_bytes(b);s=BeautifulSoup(b,'html.parser')
    print(url,'TEXT',s.get_text(' ',strip=True)[:1700].encode('ascii','backslashreplace').decode(),flush=True)
    print('LINKS',json.dumps([(a.get_text(' ',strip=True),urllib.parse.urljoin(url,a['href'])) for a in s.select('a[href]')],ensure_ascii=True)[:7000],flush=True)
    (dest/f'frame-{i}.url').write_text(url)
