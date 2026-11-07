from source_cut_probe import get
from source_cut2 import CUT,dump
from core import sha
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import urllib.parse,urllib.error,re,json,time
dest=CUT/'development/petrarch';dest.mkdir(exist_ok=True)
url='https://it.wikisource.org/wiki/Canzoniere_(Rerum_vulgarium_fragmenta)'
index=dest/'index-wiki.html'
if not index.exists():index.write_bytes(get(url))
s=BeautifulSoup(index.read_bytes(),'html.parser')
prefix='/wiki/Canzoniere_(Rerum_vulgarium_fragmenta)/'
links=[]
for a in s.select('.mw-parser-output a[href]'):
    u=urllib.parse.quote(urllib.parse.urljoin(url,a['href']),safe=':/?=&%');path=urllib.parse.unquote(urllib.parse.urlparse(u).path)
    if path.startswith(prefix) and '#' not in u and u not in links:links.append(u)
print('poems on index',len(links),'transcluded',len(s.select('.poem')),flush=True)
if len(links)!=366:raise ValueError('expected complete366poem collection from index')
def one(pair):
    i,u=pair;path=dest/f'poem-{i:03d}.html'
    if not path.exists():
        for attempt in range(5):
            try:path.write_bytes(get(u));break
            except urllib.error.HTTPError as e:
                if e.code!=429 or attempt==4:raise
                delay=max(30*(attempt+1),int(e.headers.get('Retry-After','60')))
                print('Rate limited; honoring backoff seconds',delay,flush=True);time.sleep(delay)
        time.sleep(.35)
    if i%30==0:print('poems cached',i,flush=True)
    return dict(order=i,path=str(path.relative_to(CUT)),url=u,sha256=sha(path),partition='development')
print('cached files',len(list(dest.glob('poem-*.html'))),flush=True)
records=[one(pair) for pair in enumerate(links,1)]
dump(CUT/'PETRARCH-ACQUISITION.json',dict(index_sha256=sha(index),url=url,files=records,role='whole independent-author development work; no reserve use',reuse='Underlying medieval work public domain; Wikisource transcription attribution CC BY-SA/GFDL as declared by source.'))
print('Downloaded complete Petrarch collection',len(records),flush=True)
