from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;B=R/'registrar-B';D=R/'registrar-C-followup'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
 receipt=json.loads((B/'SOURCE-QA-RECEIPT.json').read_text());review=json.loads((B/'REVIEW.json').read_text());folios=set(receipt['unfinished_fine_segmentation_pages']);assert len(folios)==14
 chosen=[p for p in review['pages'] if p['folio'] in folios];assert len(chosen)==14 and not any(b['decision']=='VERIFIED' for p in chosen for b in p['blocks'])
 D.mkdir(exist_ok=False);(D/'images').mkdir()
 pages=[p for p in json.loads((B/'PAGES.json').read_text()) if p['folio'] in folios];ids={p['task_id'] for p in pages}
 for name,rows in [('PAGES.json',pages),('EVT-STRUCTURE.json',[u for u in json.loads((B/'EVT-STRUCTURE.json').read_text()) if u['folio'] in folios]),('GEOMETRY-CANDIDATES.json',[u for u in json.loads((B/'GEOMETRY-CANDIDATES.json').read_text()) if u['task_id'] in ids])]:save(D/name,rows)
 for p in pages:shutil.copy2(B/p['image'],D/p['image'])
 shutil.copy2(B/'REGISTRAR-MANUAL.txt',D/'REGISTRAR-MANUAL.txt')
 save(D/'ASSIGNMENT.json',dict(pages=[dict(task_id=p['task_id'],folio=p['folio']) for p in pages],scope='Independent source-only completion of writing-field line geometry. Inspect all14 supplied source pages; no other registrar records or analyst material. Source-first geometry, paragraph starts alone not mandatory block splits, exact H/F counts separately. Overlapping conservative row rectangles allowed. No forced count matching or invented geometry. Record unresolved work distinctly from actual source ambiguity.'))
 freeze=dict(utc=datetime.now(timezone.utc).isoformat(),reason='Fourteen originally assigned B pages have no accepted block and explicitly unfinished fine segmentation. Second blind source-only completion before picture ratings or outcome analysis; no selection on image labels, support, power or effects.',folios=sorted(folios),task_ids=sorted(ids),directory=str(D),original_B_review_sha256=sha(B/'REVIEW.json'),original_B_QA_sha256=sha(B/'SOURCE-QA-RECEIPT.json'),original_records_retained=True,acceptance='Apply same independent visual and exact-count rules. Completed follow-up page record supersedes incomplete page record, retaining prior provenance. No existing accepted geometry can be replaced by this pass.',input_hashes={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file()})
 save(R/'FINE-COMPLETION-FREEZE.json',freeze);print(json.dumps(dict(pages=len(pages),directory=str(D))))
if __name__=='__main__':main()
