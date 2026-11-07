import urllib.request,json,hashlib,datetime,concurrent.futures
from pathlib import Path
P=Path(__file__).parent
jobs=[["lapidary-1881.pdf","https://archive.org/download/lapidariodelreyd00alfo/lapidariodelreyd00alfo.pdf"],["lapidary-scandata.xml","https://archive.org/download/lapidariodelreyd00alfo/lapidariodelreyd00alfo_scandata.xml"],["lapidary-page-numbers.json","https://archive.org/download/lapidariodelreyd00alfo/lapidariodelreyd00alfo_page_numbers.json"],["xenophon-perseus.xml","https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0032/tlg001/tlg0032.tlg001.perseus-grc2.xml"]]
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'VoynichSourceCollation/1.0 (research; public primary sources)'})
  data=urllib.request.urlopen(req,timeout=45).read();(P/'sources'/name).write_bytes(data)
  return dict(file=name,url=url,status='OK',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 except Exception as e:return dict(file=name,url=url,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:res=list(ex.map(fetch,jobs))
(P/'ACQUISITION-2.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
