from pathlib import Path
import urllib.request,json,hashlib,time
P=Path(__file__).parent
sources={'bax-2014-v1':'https://citeseerx.ist.psu.edu/document?doi=2385c05d205f691cb766eb997840a563af56d61b&repid=rep1&type=pdf','cheshire-2019':'https://research-information.bris.ac.uk/files/201563069/Full_text_PDF_accepted_author_manuscript_.pdf'}
rows=[]
for ident,url in sources.items():
 r={'id':ident,'url':url,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as response:data=response.read();r['final_url']=response.url
  assert data.startswith(b'%PDF'),'not PDF'
  (P/'sources'/(ident+'.pdf')).write_bytes(data);r.update(status='OK',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:r.update(status='FAILED',error=str(e))
 rows.append(r);print(json.dumps(r),flush=True)
 (P/'ALTERNATE-ACQUISITION.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
