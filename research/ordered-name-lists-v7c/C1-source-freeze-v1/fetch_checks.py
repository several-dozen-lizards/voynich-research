import urllib.request,re,json,concurrent.futures,hashlib
from pathlib import Path
r=Path(__file__).parent
urls=[]
for n in [851,852,871,876,877,882,883,884]:
 s=(r/'sources'/('boudet-%04d.html'%n)).read_text(encoding='utf8');url=re.search(r'<img src="([^"]+)"',s).group(1);urls.append((url,'boudet-%d.jpg'%n))
urls += [('https://rbdigital.realbiblioteca.es/files/manifests/esc_h-I-15.json','lapidario-manifest.json'),('https://www.astrologicon.org/bibliotheca/apotelesmatiki/37-apotelesmatika-syntagmata-tomos-b.html','hephaestion-vol2-catalog.html')]
def f(x):
 u,n=x
 try:
  a=urllib.request.urlopen(u,timeout=30).read();(r/'sources'/n).write_bytes(a);return dict(url=u,file=n,status='OK',bytes=len(a),sha256=hashlib.sha256(a).hexdigest())
 except Exception as e:return dict(url=u,file=n,status='FAILED',error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:a=list(e.map(f,urls))
(r/'CHECK-ACQUISITION.json').write_text(json.dumps(a,indent=2));print(json.dumps(a))
