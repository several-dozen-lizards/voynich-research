from source_cut_probe import get
from pathlib import Path
from bs4 import BeautifulSoup
import json
p=Path(__file__).parent/'source-cut-2'
for u in ['http://www.rialto.unina.it/poesia_narrativa/jaufre/','https://rialto.unina.it/poesia_narrativa/jaufre/','http://www.rialto.unina.it/Jaufre/Jaufre.htm']:
    try:
        b=get(u);s=BeautifulSoup(b,'html.parser');(p/'jaufre-route.html').write_bytes(b)
        print(u,json.dumps([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]')],ensure_ascii=True)[:15000],flush=True)
        print('BODY',s.get_text(' ',strip=True)[:1400].encode('ascii','backslashreplace').decode(),flush=True)
        break
    except Exception as e:print(u,str(e),flush=True)
