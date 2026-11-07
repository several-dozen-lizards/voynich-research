import urllib.request,json,hashlib,datetime,concurrent.futures
from pathlib import Path
P=Path(__file__).parent
jobs=[["FOL-0039R.jpg","https://imagenes.patrimonionacional.es/iiif/2/h-I-15%2FFOL-0039R.jpg/full/full/0/default.jpg"],["FOL-0039V.jpg","https://imagenes.patrimonionacional.es/iiif/2/h-I-15%2FFOL-0039V.jpg/full/full/0/default.jpg"],["FOL-0040R.jpg","https://imagenes.patrimonionacional.es/iiif/2/h-I-15%2FFOL-0040R.jpg/full/full/0/default.jpg"],["FOL-0091V.jpg","https://imagenes.patrimonionacional.es/iiif/2/h-I-15%2FFOL-0091V.jpg/full/full/0/default.jpg"],["FOL-0092R.jpg","https://imagenes.patrimonionacional.es/iiif/2/h-I-15%2FFOL-0092R.jpg/full/full/0/default.jpg"]]
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'VoynichSourceCollation/1.0 (research; public primary sources)'})
  data=urllib.request.urlopen(req,timeout=45).read();(P/'sources'/name).write_bytes(data)
  return dict(file=name,url=url,status='OK',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 except Exception as e:return dict(file=name,url=url,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:res=list(ex.map(fetch,jobs))
(P/'ACQUISITION-7.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
