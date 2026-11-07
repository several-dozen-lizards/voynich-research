from source_cut_probe import get
from pathlib import Path
from bs4 import BeautifulSoup
import json
p=Path(__file__).parent/'source-cut-2'
urls=[
'https://web.archive.org/web/20240000000000id_/http://www.rialc.unina.it/jaufre-i.htm',
'https://arquivo.pt/textsearch?versionHistory=www.rialc.unina.it%2Fjaufre-i.htm&maxItems=3',
]
for i,u in enumerate(urls):
    try:
        b=get(u);(p/f'jaufre-archive-{i}.data').write_bytes(b)
        s=BeautifulSoup(b,'html.parser');print(u, len(b),s.get_text(' ',strip=True)[:1200].encode('ascii','backslashreplace').decode(),flush=True)
        print(json.dumps([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]')],ensure_ascii=True)[:5000],flush=True)
    except Exception as e:print(u,str(e),flush=True)
