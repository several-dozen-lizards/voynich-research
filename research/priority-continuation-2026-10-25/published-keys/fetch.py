from pathlib import Path
import urllib.request,ssl,json,hashlib,time
P=Path(__file__).parent
plan=json.loads((P/'BATCH.json').read_text(encoding='utf8'));records=[]
for item in plan['candidates']:
 r={'id':item['id'],'url':item['url'],'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 try:
  req=urllib.request.Request(item['url'],headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35) as response:data=response.read();r['final_url']=response.url
  assert data.startswith(b'%PDF'), 'not PDF'
  (P/'sources'/(item['id']+'.pdf')).write_bytes(data);r.update(status='OK',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:r.update(status='FAILED',error=str(e))
 records.append(r);print(json.dumps(r),flush=True)
 (P/'ACQUISITION.json').write_text(json.dumps(records,indent=2),encoding='utf8')
