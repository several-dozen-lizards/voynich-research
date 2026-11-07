import urllib.request,json,re,concurrent.futures,hashlib
from pathlib import Path
r=Path(__file__).parent
s=(r/'sources/boudet-article.html').read_text(encoding='utf8')
u=re.findall('data-content-url="([^"]+)"',s)
def fetch(x):
 n=x.rsplit('_',2)[-2]; f=r/'sources'/('boudet-'+n+'.html')
 try:
  a=urllib.request.urlopen(x,timeout=35).read();f.write_bytes(a);return dict(page=n,status='OK',file=f.name,sha256=hashlib.sha256(a).hexdigest())
 except Exception as e:return dict(page=n,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e: result=list(e.map(fetch,u))
(r/'BOUDET-ACQUISITION.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
