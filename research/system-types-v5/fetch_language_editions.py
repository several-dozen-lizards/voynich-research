"""Archive primary language-edition pages; extraction and source controls are separate."""
from pathlib import Path
import json,re,hashlib,urllib.request,urllib.parse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Voynich-source-controls/1.0'}),timeout=60) as r:return r.read()

def store(folder,name,url):
    path=ROOT/'SOURCES'/folder/name;path.parent.mkdir(parents=True,exist_ok=True)
    data=get(url);path.write_bytes(data)
    revision=re.search(r'"wgRevisionId"\s*:\s*(\d+)',data.decode('utf-8',errors='replace'))
    return dict(path=name,url=url,sha256=hashlib.sha256(data).hexdigest(),revision=revision[1] if revision else None)

def main():
    url='https://it.wikisource.org/wiki/Divina_Commedia'
    first=store('italian-dante','index.html',url)
    soup=BeautifulSoup((ROOT/'SOURCES/italian-dante/index.html').read_bytes(),'html.parser')
    links=sorted(set(urllib.parse.urlparse(urllib.parse.urljoin(url,a['href'])).path for a in soup.select('a[href]') if re.fullmatch(r'/wiki/Divina_Commedia/Inferno/Canto_[IVXLCDM]+',urllib.parse.urlparse(urllib.parse.urljoin(url,a['href'])).path)))
    if len(links)!=34:raise ValueError(('expected34 Inferno cantos',len(links)))
    def one(href):return store('italian-dante',href.rsplit('/',1)[1]+'.html','https://it.wikisource.org'+href)
    with ThreadPoolExecutor(max_workers=6) as pool:records=list(pool.map(one,links))
    manifest=dict(language='Italian',work='Dante, Commedia, Inferno',work_period='early14th century',genre='literary verse, not medical',
        source_kind='edited Wikisource text',attribution='Dante Alighieri; Italian Wikisource contributors',
        reuse='Public-domain underlying work; transcription CC BY-SA3.0/GFDL as declared by source index',files=[first]+records)
    (ROOT/'SOURCES/italian-dante/MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    rec=store('old-czech-dalimil','source.html','https://czech.mml.ox.ac.uk/dalimilova-kronika')
    (ROOT/'SOURCES/old-czech-dalimil/MANIFEST.json').write_text(json.dumps(dict(language='Old Czech',work='Dalimilova kronika',work_period='early14th century',
        source_kind='Oxford parallel diplomatic/transliterated teaching edition; critical edition1958 and Porak1980',genre='chronicle verse, not medical',
        reuse='No open redistribution license established; internal research source only, do not package in public releases',
        attribution='Oxford Czech and Slovak Resources; see source editorial provenance; Havranek and Danhelka1958, Porak Chrestomatie',files=[rec]),indent=2),encoding='utf-8')
    print(json.dumps(dict(italian_cantos=len(records),old_czech_pages=1)))

if __name__=='__main__':main()
