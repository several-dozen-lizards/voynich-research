import urllib.request,json,hashlib,datetime,concurrent.futures
from pathlib import Path
P=Path(__file__).parent
jobs=[('ia-lapidary-metadata.json','https://archive.org/metadata/lapidariodelreyd00alfo'),('lapidary-1881-ocr.txt','https://archive.org/download/lapidariodelreyd00alfo/lapidariodelreyd00alfo_djvu.txt'),('greek-repo-tree.json','https://api.github.com/repos/PerseusDL/canonical-greekLit/contents/data/tlg0032/tlg001'),('riemann-1878.html','https://www.persee.fr/doc/bch_0007-4217_1878_num_2_1_4446'),('xenophon-bude.pdf','https://upload.wikimedia.org/wikipedia/commons/5/59/X%C3%A9nophon_-_Hell%C3%A9niques%2C_Les_Belles_Lettres%2C_tome_I.pdf')]
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'VoynichSourceCollation/1.0 (research; public primary sources)'})
  data=urllib.request.urlopen(req,timeout=45).read();(P/'sources'/name).write_bytes(data)
  return dict(file=name,url=url,status='OK',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 except Exception as e:return dict(file=name,url=url,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:res=list(ex.map(fetch,jobs))
(P/'ACQUISITION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
