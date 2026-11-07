"""Fetch pinned primary research sources; raw bytes and SHA256 receipts retained."""
import concurrent.futures,hashlib,json,urllib.request,urllib.parse,time,functools,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPOS=['greshko/naibbe-cipher','danielgaskell/voynich','chirila/Voynich-public','mzattera/v4j','TorstenTimm/SelfCitationTextgenerator']
def fetch(url):
    for attempt in range(3):
        try:return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Voynich-research-local'}),timeout=120).read()
        except Exception:
            if attempt==2:raise
            time.sleep(2)
@functools.lru_cache(maxsize=None)
def metadata(repo):
    folder=ROOT/'raw'/repo.split('/')[0];folder.mkdir(parents=True,exist_ok=True)
    path=folder/'repository.json'
    if path.exists():return json.loads(path.read_text())
    meta=json.loads(fetch('https://api.github.com/repos/'+repo))
    commit=json.loads(fetch('https://api.github.com/repos/'+repo+'/commits/'+meta['default_branch']))['sha']
    tree=json.loads(fetch('https://api.github.com/repos/'+repo+'/git/trees/'+commit+'?recursive=1'))
    result=dict(repo=repo,commit=commit,meta=meta,tree=tree)
    path.write_text(json.dumps(result,indent=2),encoding='utf-8');return result
def save(repo,path):
    m=metadata(repo);folder=ROOT/'raw'/repo.split('/')[0];target=folder/path;target.parent.mkdir(parents=True,exist_ok=True)
    url='https://raw.githubusercontent.com/'+repo+'/'+m['commit']+'/'+urllib.parse.quote(path)
    raw=target.read_bytes() if target.exists() else fetch(url)
    if not target.exists():target.write_bytes(raw)
    return dict(repository=repo,commit=m['commit'],path=path,url=url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
if __name__=='__main__':
    if '--download' in sys.argv:
        jobs=[]
        for repo in REPOS:
            m=metadata(repo)
            for item in m['tree']['tree']:
                if item['type']!='blob':continue
                p=item['path'];take=p in ['README.md','LICENSE','PROPERTIES.md']
                if repo.startswith('greshko/'):take |= p in ['naibbe.py','naibbe_v2.py','naibbe_cv_vc_reuse.py','decrypt_naibbe.py','references/naibbe_tables.csv']
                if repo.startswith('danielgaskell/'):take |= p.startswith('data/') or p in ['stats.py','rstats.r','results/metadata.csv']
                if repo.startswith('chirila/'):
                    take |= (p.startswith('Corpora/Historical_texts/') or p.startswith('Corpora/Wikipedia_texts/full/')) and not p.endswith('.DS_Store')
                    take |= p in ['Corpora/Historical_texts_list.xlsx','Corpora/Wikipedia_texts_list.xlsx','Corpora/Historical_texts_statistics.csv','Corpora/Wikipedia_texts_statistics.csv'] or p.startswith('R code/')
                if repo.startswith('TorstenTimm/'):take |= p.startswith('source/') or p in ['executable/conf.properties','executable/generate/generated_text.txt','executable/text-generator.jar']
                if repo.startswith('mzattera/'):
                    take |= p.endswith('SlotAlphabet.java') or p.endswith('SlotBasedModel.java') or p.endswith('WordModelEvaluator.java') or p in ['docs/005/index.md','resources/analysis/slots/StateMachine05_grammar.txt'] or p.endswith('/slot/FromEva.java')
                if take:jobs.append((repo,p))
        receipts=[];errors=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            futures={pool.submit(save,*job):job for job in jobs}
            for i,f in enumerate(concurrent.futures.as_completed(futures),1):
                try:receipts.append(f.result())
                except Exception as e:errors.append(dict(job=futures[f],error=str(e)))
                if i%25==0:print(f'{i}/{len(jobs)} sources fetched; failures={len(errors)}',flush=True)
        (ROOT/'SOURCE_MANIFEST.json').write_text(json.dumps(dict(files=receipts,errors=errors),indent=2),encoding='utf-8')
        print(f'COMPLETE: {len(receipts)} files, {sum(r["bytes"] for r in receipts):,} bytes; errors={errors}',flush=True)
        sys.exit(bool(errors))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for m in pool.map(metadata,REPOS):
            paths=[r for r in m['tree']['tree'] if r['type']=='blob']
            selected=paths if len(paths)<160 else [r for r in paths if any(k in r['path'].lower() for k in ['slot','grammar','selfcitation','properties','readme','license','generated_text.txt','pom.xml','.jar'])]
            print(json.dumps(dict(repo=m['repo'],commit=m['commit'],files=[(r['path'],r.get('size')) for r in selected])),flush=True)
