import urllib.request,json,hashlib,datetime,concurrent.futures
from pathlib import Path
P=Path(__file__).parent
jobs=[["lapidary-1881-ocr.xml","https://archive.org/download/lapidariodelreyd00alfo/lapidariodelreyd00alfo_djvu.xml"],["riemann-0137.html","https://www.persee.fr/doc/page/bch_0007-4217_1878_num_2_1_4446/bch_0007-4217_1878_num_2_1_T1_0137_0000"],["riemann-0138.html","https://www.persee.fr/doc/page/bch_0007-4217_1878_num_2_1_4446/bch_0007-4217_1878_num_2_1_T1_0138_0000"],["riemann-0139.html","https://www.persee.fr/doc/page/bch_0007-4217_1878_num_2_1_4446/bch_0007-4217_1878_num_2_1_T1_0139_0000"]]
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'VoynichSourceCollation/1.0 (research; public primary sources)'})
  data=urllib.request.urlopen(req,timeout=45).read();(P/'sources'/name).write_bytes(data)
  return dict(file=name,url=url,status='OK',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 except Exception as e:return dict(file=name,url=url,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:res=list(ex.map(fetch,jobs))
(P/'ACQUISITION-4.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
