import urllib.request,json,hashlib
from pathlib import Path
r=Path(__file__).parent
m=json.loads((r/'sources/reglat1300-manifest.json').read_text())
c=next(c for c in m['sequences'][0]['canvases'] if c['label']=='45v')
s=c['images'][0]['resource']['service']['@id']
u=[(s+'/full/full/0/default.jpg','reglat1300-f45v.jpg'),('https://www.persee.fr/doc/bec_0373-6237_2004_num_162_2_463454?pageId=T1_331','raziel-date-grevin-veronese.html')]
a=[]
for url,n in u:
 try:
  b=urllib.request.urlopen(url,timeout=40).read();(r/'sources'/n).write_bytes(b);a.append(dict(url=url,file=n,status='OK',sha256=hashlib.sha256(b).hexdigest()))
 except Exception as e:a.append(dict(url=url,status='FAILED',error=str(e)))
(r/'RAZIEL-ACQUISITION.json').write_text(json.dumps(a,indent=2));print(json.dumps(a))
