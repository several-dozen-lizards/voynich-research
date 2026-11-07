"""Download public source pages only. No annotations, corpus or scoring imports."""
import concurrent.futures, hashlib, json, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
JOBS={
 **{f'gro_{c}':f'https://www.handschriftenzentren.de/materialien/grotefend/g_{c}.htm' for c in ['a','b','h','m','w']},
 **{f'cat_{w}':f'https://dcvb.iec.cat/results.asp?word={w}' for w in ['abril','maig','juny','juliol','agost','setembre','octubre','novembre','desembre','mes','comptar','verema']},
 'cat_marc':'https://dcvb.iec.cat/results.asp?word=mar%E7',
 'rodez':'https://www.occitan-aveyron.fr/fr/diffusio/source/rodez/livre-d-heures-libre-d-oras-en-latin-occitan-xve-siecle_SRC15748',
 'month_collection14':'https://www.voynich.ninja/printthread.php?page=14&tid=4751',
}
def fetch(pair):
 name,url=pair; record={'id':name,'url':url}
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (historical source research)'})
  with urllib.request.urlopen(request,timeout=25) as response:
   raw=response.read();charset=response.headers.get_content_charset() or 'utf-8';final=response.url
  path=ROOT/'sources'/f'{name}.html';path.write_bytes(raw)
  record.update(status='OK',path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),charset=charset,final_url=final)
 except Exception as exc:record.update(status='ERROR',error=str(exc))
 return record
if __name__=='__main__':
 (ROOT/'sources').mkdir(exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:records=list(pool.map(fetch,JOBS.items()))
 (ROOT/'SOURCE_RETRIEVAL.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
 print(json.dumps({r['id']:r['status'] for r in records}))
