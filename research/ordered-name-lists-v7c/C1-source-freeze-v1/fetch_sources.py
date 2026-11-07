import urllib.request,json,hashlib,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).parent
SOURCES={
 'boudet2002.pdf':'https://www.persee.fr/docAsPDF/mefr_1123-9883_2002_num_114_2_9254.pdf',
 'lapidario-boe2021.pdf':'https://www.boe.es/biblioteca_juridica/abrir_pdf.php?id=PUB-LH-2021-208',
 'heptameron-peterson.html':'https://esotericarchives.com/solomon/heptamer.htm',
 'arsnotoria-yale-catalog.html':'https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.mell001.htm',
 'lapidario-catalog.html':'https://rbdigital.realbiblioteca.es/s/rbme-expo/item/13127',
 'lapidario-cervantes.html':'https://www.cervantesvirtual.com/obra-visor/lapidario--0/html/001a37de-82b2-11df-acc7-002185ce6064_2.html',
 'liberjuratus-peterson.html':'https://www.esotericarchives.com/juratus/juratus.htm',
 'reglat1300-manifest.json':'https://digi.vatlib.it/iiif/MSS_Reg.lat.1300/manifest.json'
}
def get(item):
 name,url=item;result={'file':name,'url':url,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(request,timeout=45) as r:b=r.read();result['final_url']=r.url;result['content_type']=r.headers.get('Content-Type')
  if name.endswith('.pdf') and not b.startswith(b'%PDF'):raise ValueError('not PDF')
  (P/'sources'/name).write_bytes(b);result.update(status='OK',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:result.update(status='FAILED',error=str(e))
 print(json.dumps({k:v for k,v in result.items() if k not in ('url','final_url')}),flush=True);return result
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:receipts=list(pool.map(get,SOURCES.items()))
 (P/'ACQUISITION.json').write_text(json.dumps(receipts,indent=2)+'\n')
