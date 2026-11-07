from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
R=Path(__file__).resolve().parent;D=R/'images';D.mkdir(exist_ok=True)
def get(x):
 name='f70v1' if '/1006201/' in x['url'] else 'f'+x['label']
 p=D/(name+'.jpg')
 if not p.exists():
  with urllib.request.urlopen(x['url'],timeout=90) as r:p.write_bytes(r.read())
 return dict(**x,file=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
xs=json.loads((R/'IMAGE-SOURCES.json').read_text())
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(get,xs))
(R/'IMAGE-RECEIPTS.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps([dict(label=x['label'],bytes=x['bytes']) for x in out]))
