"""Combine disjoint source-only registrar records with per-page provenance."""
from pathlib import Path
import json,hashlib,importlib.util
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;W=R/'registrar-only'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 freeze=json.loads((R/'PARALLEL-REGISTRAR-FREEZE.json').read_text());allpages=json.loads((W/'PAGES.json').read_text());pmap={p['task_id']:p for p in allpages}
 spec=importlib.util.spec_from_file_location('registration',R/'register.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 combined={};sources={}
 for role,assignment in freeze['partitions'].items():
  path=Path(assignment['directory'])/'REVIEW.json'
  if not path.exists():continue
  raw=path.read_bytes();review=json.loads(raw);allowed=set(assignment['task_ids'])
  assert all(p['task_id'] in allowed for p in review.get('pages',[])),role+' reviewed another partition'
  m.validate_review(review,pmap)
  for page in review.get('pages',[]):
   tid=page['task_id'];assert tid not in combined
   combined[tid]=dict(page,registrar_id=review['registrar_id'],registrar_partition=role,review_source_sha256=sha(raw))
  sources[role]=dict(path=str(path),sha256=sha(raw),registrar_id=review['registrar_id'],saved_pages=len(review.get('pages',[])))
 follow_freeze=R/'FINE-COMPLETION-FREEZE.json'
 if follow_freeze.exists():
  f=json.loads(follow_freeze.read_text());folder=Path(f['directory']);path=folder/'REVIEW.json';receipt=folder/'SOURCE-QA-RECEIPT.json'
  if path.exists() and receipt.exists():
   raw=path.read_bytes();follow=json.loads(raw);assert sha(raw) in receipt.read_text()
   assert {p['task_id'] for p in follow['pages']}==set(f['task_ids'])
   m.validate_review(follow,pmap)
   for page in follow['pages']:
    tid=page['task_id'];prior=combined[tid];certified=[b for b in prior['blocks'] if b['decision']=='VERIFIED']
    if certified:
     # Preserve first source certification when late primary QA finished during follow-up.
     later={b['unit']:b for b in page['blocks'] if b['decision']=='VERIFIED'}
     assert all(b['unit'] in later and len(b['lines'])==len(later[b['unit']]['lines']) for b in certified),'Conflicting source unit/count requires explicit adjudication.'
     prior['secondary_source_review']=dict(registrar_id=follow['registrar_id'],review_source_sha256=sha(raw),page=page,disposition='Primary source-certified geometry preserved; independent unit/count agrees. Follow-up geometry not substituted.')
    else:
     combined[tid]=dict(page,registrar_id=follow['registrar_id'],registrar_partition='C-followup',review_source_sha256=sha(raw),superseded_incomplete_review_provenance={k:prior[k] for k in ('registrar_id','registrar_partition','review_source_sha256')})
   sources['C-followup']=dict(path=str(path),sha256=sha(raw),registrar_id=follow['registrar_id'],saved_pages=len(follow['pages']),reason='Source-only fine segmentation completion; original B records retained.')
 output=dict(registrar_id='INDEPENDENT_REGISTRARS; SEE PER_PAGE_PROVENANCE',fresh_context=True,outcome_blind=True,picture_boxes_unseen=True,pages=[combined[p['task_id']] for p in allpages if p['task_id'] in combined],unreviewed_pages=[p['task_id'] for p in allpages if p['task_id'] not in combined or not combined[p['task_id']].get('reviewed')],sources=sources)
 target=R/'REVIEW-COMBINED.json'
 if target.exists():
  archive=R/'combined-review-snapshots';archive.mkdir(exist_ok=True);(archive/(sha(target.read_bytes())+'.json')).write_bytes(target.read_bytes())
 temp=R/'REVIEW-COMBINED.tmp';temp.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8');temp.replace(target)
 print(json.dumps(dict(saved_pages=len(combined),unreviewed_pages=len(output['unreviewed_pages']),sources=sources),indent=2))
if __name__=='__main__':main()
