import ssl,urllib.request,json,hashlib,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).parent
context=ssl.create_default_context()
for cert,encoding,trust in ssl.enum_certificates('ROOT'):
 if encoding=='x509_asn':
  try:context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(cert))
  except ssl.SSLError:pass
SOURCES={
 'lapidario-boe2021.pdf':'https://www.boe.es/biblioteca_juridica/abrir_pdf.php?id=PUB-LH-2021-208',
 'arsnotoria-yale-catalog.html':'https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.mell001.htm',
 'boudet-article.html':'https://www.persee.fr/doc/mefr_1123-9883_2002_num_114_2_9254',
 'biruni-sachau1879.pdf':'https://www.culture-islam.fr/wp-content/uploads/2013/01/biruni.pdf'
}
def get(item):
 name,url=item;r={'file':name,'url':url,'utc':time.time()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=context,timeout=45) as stream:b=stream.read()
  if name.endswith('.pdf') and not b.startswith(b'%PDF'):raise ValueError('notPDF')
  (P/'sources'/name).write_bytes(b);r.update(status='OK',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r.update(status='FAILED',error=str(e))
 print(json.dumps(r),flush=True);return r
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:rr=list(pool.map(get,SOURCES.items()))
 (P/'ACQUISITION-RETRY.json').write_text(json.dumps(rr,indent=2)+'\n')
