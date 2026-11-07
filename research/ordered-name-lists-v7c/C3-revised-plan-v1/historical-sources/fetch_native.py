import json,urllib.request,concurrent.futures,hashlib,datetime
from pathlib import Path
R=Path(__file__).parent
old=R.parent.parent/'C1-source-freeze-v1/sources/lapidario-manifest.json'
m=json.loads(old.read_text())
canvases=m['sequences'][0]['canvases']
urls=[]
for c in canvases:
 if c['label'] in ['FOL-0001R.jpg','FOL-0001V.jpg','FOL-0002R.jpg','FOL-0002V.jpg']:
  urls.append((c['label'],c['images'][0]['resource']['@id']))
def get(item):
 name,url=item
 try:
  b=urllib.request.urlopen(url,timeout=40).read();(R/name).write_bytes(b)
  return dict(file=name,url=url,status='OK',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:return dict(file=name,url=url,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:out=list(e.map(get,urls))
(R/'NATIVE-ACQUISITION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
