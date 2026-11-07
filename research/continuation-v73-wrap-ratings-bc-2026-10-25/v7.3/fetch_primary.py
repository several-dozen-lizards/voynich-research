import concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
P=Path(__file__).parent;D=P/'sources';D.mkdir(exist_ok=True)
urls=[('bax-2014-author','https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf'),('cheshire-2019-bristol','https://research-information.bris.ac.uk/files/201563069/Full_text_PDF_accepted_author_manuscript_.pdf'),('cheshire-2019-author','https://www.researchgate.net/profile/Gerard-Cheshire-Phd/publication/332745116_The_Language_and_Writing_System_of_MS408_Voynich_Explained/links/6190e2b0d7d1af224bea3b6e/The-Language-and-Writing-System-of-MS408-Voynich-Explained.pdf')]
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/pdf'})
  with urllib.request.urlopen(req,timeout=35) as r:data=r.read()
  if not data.startswith(b'%PDF-'):return dict(id=name,url=url,status='NON_PDF_RESPONSE',bytes=len(data))
  path=D/(name+'.pdf');path.write_bytes(data);return dict(id=name,url=url,status='DOWNLOADED',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as exc:return dict(id=name,url=url,status='FAILED',error=str(exc))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,urls))
(P/'PRIMARY-ACQUISITION.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');print(json.dumps(results))
