"""Retrieve primary source bytes; preserve successes and failures."""
from pathlib import Path
import urllib.request, json, hashlib, concurrent.futures
R=Path(__file__).resolve().parent; S=R/'sources'; S.mkdir(exist_ok=True)
def get(url,name):
    p=S/name
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'C16-KH academic replication'})
        with urllib.request.urlopen(req,timeout=45) as f: b=f.read(); final=f.url
        p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
        return dict(url=url,path=str(p.relative_to(R)),final_url=final,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
    except Exception as e:return dict(url=url,path=name,error=str(e))
jobs=[('https://api.github.com/repos/danielgaskell/voynich/commits/main','c17-commit.json'),('https://api.github.com/repos/danielgaskell/voynich/git/trees/main?recursive=1','c17-tree.json'),('https://raw.githubusercontent.com/danielgaskell/voynich/main/README.md','C17-LICENSE-README.md'),('https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/books.json','sefaria-books.json'),('https://aclanthology.org/Q16-1006.pdf','Q16-1006.pdf'),('http://webdocs.cs.ualberta.ca/~kondrak/','kondrak-http.html'),('https://webdocs.cs.ualberta.ca/~kondrak/index.html','kondrak-index.html')]
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: rows=list(ex.map(lambda x:get(*x),jobs))
    (S/'retrieval.json').write_text(json.dumps(rows,indent=2)); print(json.dumps(rows,indent=2))
