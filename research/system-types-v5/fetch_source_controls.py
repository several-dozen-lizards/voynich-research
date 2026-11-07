"""Pinned primary corpus metadata and GT text/XML only; no predictions or models."""
from pathlib import Path
import hashlib,json,urllib.request,urllib.parse,sys
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parent

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Voynich-source-controls/1.0'})
    with urllib.request.urlopen(req,timeout=60) as response:return response.read()

def repo(owner,name,folder,metadata,select=None):
    base=f'https://api.github.com/repos/{owner}/{name}'
    info=json.loads(get(base));branch=info['default_branch']
    commit=json.loads(get(base+'/commits/'+branch))['sha']
    tree=json.loads(get(base+'/git/trees/'+commit+'?recursive=1'))
    dest=ROOT/'SOURCES'/folder;dest.mkdir(exist_ok=True)
    (dest/'TREE.json').write_text(json.dumps(tree),encoding='utf-8')
    paths=[r['path'] for r in tree['tree'] if r['type']=='blob' and (r['path'] in metadata or (select and select(r['path'])))]
    def download(path):
        target=(dest/path).resolve()
        if not target.is_relative_to(dest.resolve()):raise ValueError('unsafe path')
        url=f'https://raw.githubusercontent.com/{owner}/{name}/{commit}/'+urllib.parse.quote(path)
        data=get(url);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=data:raise FileExistsError(target)
        target.write_bytes(data)
        return dict(path=path,url=url,sha256=hashlib.sha256(data).hexdigest())
    with ThreadPoolExecutor(max_workers=6) as pool:records=list(pool.map(download,paths))
    manifest=dict(repository=f'https://github.com/{owner}/{name}',commit=commit,files=records,github_license_metadata=info.get('license'))
    (dest/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(dict(folder=folder,commit=commit,files=len(records))),flush=True)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='metadata':
        repo('HTR-United','CREMMA-Medieval-LAT','cremma-lat',['README.md','htr-united.yml','data-registry.csv','table.csv','datapaper.tex','CITATION.cff'])
        repo('UniversalDependencies','UD_Old_Occitan-CorAG','old-occitan-corag',['README.md','LICENSE.txt','LICENSE','CITATION.cff'])
    elif mode=='latin-gt':
        # Selection by pre-existing manuscript genre/date metadata, never by fit scores.
        selection=json.loads((ROOT/'SOURCE-CONTROL-SELECTION.json').read_text())['latin_manuscripts']
        repo('HTR-United','CREMMA-Medieval-LAT','cremma-lat',['README.md','htr-united.yml','data-registry.csv','table.csv','datapaper.tex','CITATION.cff'],
             lambda p:any(p.startswith('data/'+m+'/') for m in selection) and (p.endswith('.chocomufin.xml') or p.endswith('.txt')))
    elif mode=='occitan':
        repo('UniversalDependencies','UD_Old_Occitan-CorAG','old-occitan-corag',['README.md','LICENSE.txt','LICENSE','CITATION.cff'],lambda p:p.endswith('.conllu'))
