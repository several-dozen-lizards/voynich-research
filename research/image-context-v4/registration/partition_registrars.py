from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;W=R/'registrar-only'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pages=json.loads((W/'PAGES.json').read_text());units=json.loads((W/'EVT-STRUCTURE.json').read_text());candidates=json.loads((W/'GEOMETRY-CANDIDATES.json').read_text());review=json.loads((W/'REVIEW.json').read_text());done={p['task_id'] for p in review['pages']}
 remaining=[p for p in pages if p['task_id'] not in done];groups={'A':[p for p in pages if p['task_id'] in done]+remaining[::3],'B':remaining[1::3],'C':remaining[2::3]}
 assert len({p['task_id'] for g in groups.values() for p in g})==sum(map(len,groups.values()))==len(pages)
 manifests={}
 for role,assigned in groups.items():
  dest=W if role=='A' else R/('registrar-'+role);dest.mkdir(exist_ok=True);(dest/'images').mkdir(exist_ok=True)
  ids={p['task_id'] for p in assigned};folios={p['folio'] for p in assigned}
  assignment=dict(registrar=role,scope='Only assigned source pages. No other registrar records, analyst data, text outcomes, picture-rater boxes or category labels.',pages=[dict(task_id=p['task_id'],folio=p['folio']) for p in assigned],expected_pages=len(assigned),supplied_order='Frozen source queue order within this deterministic every-third remaining-page partition.',geometry_rule='Source geometry first. Paragraph starts/indentation/markers alone do not necessarily split a writing field. Do not merge/split to fit EVT counts. Separate fields, drawing interruption and genuinely ambiguous mapping must be logged; exact H/F counts are necessary but never sufficient for verification.')
  save(dest/('ASSIGNMENT-A.json' if role=='A' else 'ASSIGNMENT.json'),assignment)
  if role!='A':
   save(dest/'PAGES.json',assigned);save(dest/'EVT-STRUCTURE.json',[u for u in units if u['folio'] in folios]);save(dest/'GEOMETRY-CANDIDATES.json',[c for c in candidates if c['task_id'] in ids]);shutil.copy2(W/'REGISTRAR-MANUAL.txt',dest/'REGISTRAR-MANUAL.txt')
   for p in assigned:
    target=dest/p['image']
    if not target.exists():shutil.copy2(W/p['image'],target)
    assert sha(target)==sha(W/p['image'])
  manifests[role]=dict(directory=str(dest),task_ids=sorted(ids),pages=len(assigned),input_hashes={str(p.relative_to(dest)):sha(p) for p in dest.rglob('*') if p.is_file() and (p.name in (['ASSIGNMENT-A.json'] if role=='A' else ['ASSIGNMENT.json','PAGES.json','EVT-STRUCTURE.json','GEOMETRY-CANDIDATES.json','REGISTRAR-MANUAL.txt']) or role!='A' and p.parent.name=='images')})
 save(R/'PARALLEL-REGISTRAR-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),authority='Human explicitly approved three blind registrars in parallel.',partitions=manifests,baseline_review_sha256=sha(W/'REVIEW.json'),original45_retained=True,independence='Each worker has a disjoint assigned source page set. B/C have separate allowlisted source-only folders; no review records from other workers. No analyst amendment/rationale provided to workers.'))
 print(json.dumps({k:v['pages'] for k,v in manifests.items()}))
if __name__=='__main__':main()
