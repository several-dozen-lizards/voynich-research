from pathlib import Path
import json,hashlib,re,urllib.request,urllib.parse,urllib.error,time
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
URL='https://cs.wikisource.org/wiki/Rýmovaná_kronika_česká_tak_řečeného_Dalimila'

def get(url):
    url=urllib.parse.quote(url,safe=':/%?=&')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Voynich-source-controls/1.0'}),timeout=60) as r:return r.read()
        except urllib.error.HTTPError as error:
            if error.code!=429 or attempt==2:raise
            delay=min(60,max(30,int(error.headers.get('Retry-After','60'))))
            print(json.dumps(dict(status=429,wait_seconds=delay,url=url)),flush=True)
            time.sleep(delay)

def main():
    folder=ROOT/'SOURCES/old-czech-complete';folder.mkdir(exist_ok=True)
    raw=(folder/'index.html').read_bytes() if (folder/'index.html').exists() else get(URL);(folder/'index.html').write_bytes(raw)
    soup=BeautifulSoup(raw,'html.parser')
    lists=[ol for ol in soup.select('ol') if len(ol.find_all('li',recursive=False))==106]
    if len(lists)!=1:raise ValueError(('expected one106-chapter list',len(lists)))
    links=[]
    for i,li in enumerate(lists[0].find_all('li',recursive=False)):
        a=li.find('a',href=True);links.append((i+1,urllib.parse.urljoin(URL,a['href'])))
    def one(item):
        i,url=item;name=f'chapter-{i:03d}.html';data=(folder/name).read_bytes() if (folder/name).exists() else get(url);(folder/name).write_bytes(data)
        revision=re.search(r'"wgRevisionId"\s*:\s*(\d+)',data.decode('utf-8',errors='replace'))
        return dict(chapter=i,path=name,url=url,revision=revision[1] if revision else None,sha256=hashlib.sha256(data).hexdigest())
    with ThreadPoolExecutor(max_workers=1) as pool:records=list(pool.map(one,links))
    manifest=dict(language='Old Czech',work='Rymovana kronika ceska tak receneho Dalimila',work_period='early14th century',
        edition='Josef Jirecek, Prague, Matice ceska,1877',source_kind='edited historical text; not modern Czech retelling',genre='chronicle verse, not medical',
        selection='main106 numbered chapters; exclude editorial introduction and later-redaction appendices',
        reuse='Underlying work and1877 edition declared PD-old70; Wikisource transcription under its posted CC BY-SA terms; retain attribution',
        attribution='Anonymous medieval author; Josef Jirecek edition; Czech Wikisource contributors',
        files=[dict(path='index.html',url=URL,sha256=hashlib.sha256(raw).hexdigest())]+records)
    (folder/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(dict(chapters=len(records))))

if __name__=='__main__':main()
