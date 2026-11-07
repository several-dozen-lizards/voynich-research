from source_cut_probe import get
from pathlib import Path
from bs4 import BeautifulSoup
import json,sys
p=Path(__file__).parent/'source-cut-2';dest=p/'development/occitan';dest.mkdir(exist_ok=True)
names=['jaufre-indice.htm','jaufre-1.htm'] if len(sys.argv)==1 else sys.argv[1:]
for name in names:
    u='https://web.archive.org/web/20240000000000id_/http://www.rialc.unina.it/_private/'+name
    path=dest/name
    try:
        if not path.exists():path.write_bytes(get(u))
        (dest/(name+'.url')).write_text(u)
        s=BeautifulSoup(path.read_bytes(),'html.parser')
        print(name,'bytes',path.stat().st_size,'text',s.get_text(' ',strip=True)[:1900].encode('ascii','backslashreplace').decode(),flush=True)
        print('LINKS',json.dumps([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]')],ensure_ascii=True)[:8000],flush=True)
    except Exception as e:print(name,str(e),flush=True)
