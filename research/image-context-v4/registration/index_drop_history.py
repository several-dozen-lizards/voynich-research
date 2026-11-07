"""Index every distinct saved source-review version's physical drops; no geometry admission."""
from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parent
def main():
 rows=[];seen=set();versions=[]
 for name in ('registrar-only','registrar-B','registrar-C','registrar-C-followup'):
  folder=R/name
  for path in sorted(folder.rglob('*.json')):
   if not path.name.upper().startswith('REVIEW'):continue
   raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
   if (name,digest) in seen:continue
   data=json.loads(raw)
   if not isinstance(data,dict) or not isinstance(data.get('pages'),list):continue
   seen.add((name,digest));versions.append(dict(path=str(path.relative_to(R)),sha256=digest))
   for page in data['pages']:
    for b in page.get('blocks',[]):
     if b.get('decision')!='VERIFIED' or not b.get('unit'):
      rows.append(dict(worker=name,review_file=str(path.relative_to(R)),review_sha256=digest,folio=page.get('folio'),task_id=page.get('task_id'),block_id=b.get('block_id'),unit=b.get('unit'),decision=b.get('decision'),visible_lines=len(b['lines']) if b.get('lines') else None,reason=b.get('reason',''),native_box=json.dumps(b.get('box'))))
 with (R/'HISTORICAL-DROPPED-BLOCKS.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['worker','review_file','review_sha256','folio','task_id','block_id','unit','decision','visible_lines','reason','native_box']);w.writeheader();w.writerows(rows)
 (R/'DROP-HISTORY-INDEX.json').write_text(json.dumps(dict(status='Distinct source-review versions; repeated physical regions across versions are not independent blocks.',versions=versions,versioned_drop_records=len(rows)),indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(distinct_review_versions=len(versions),versioned_drop_records=len(rows))))
if __name__=='__main__':main()
