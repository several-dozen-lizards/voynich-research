"""Seal completed source queue and registrar provenance; no downstream analysis."""
from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 combined=json.loads((R/'REVIEW-COMBINED.json').read_text());status=json.loads((R/'STATUS.json').read_text());assignment=json.loads((R/'PARALLEL-REGISTRAR-FREEZE.json').read_text())
 assert not combined['unreviewed_pages'] and len(combined['pages'])==168 and status['reviewed_pages']==status['ready_pages']==168
 assert not status['outcomes_joined'] and not status['picture_boxes_used']
 receipts={};checks=0
 for role,part in assignment['partitions'].items():
  folder=Path(part['directory']);review=folder/'REVIEW.json';receipt=folder/'SOURCE-QA-RECEIPT.json';assert receipt.exists(),role+' source QA receipt missing'
  assert sha(review) in receipt.read_text(),role+' final review hash missing from QA receipt'
  assert sha(review)==combined['sources'][role]['sha256'],role+' changed after combined checkpoint'
  for name,h in part['input_hashes'].items():assert sha(folder/name)==h,(role,name);checks+=1
  receipts[role]=dict(review_sha256=sha(review),QA_receipt_sha256=sha(receipt),pages=len(json.loads(review.read_text())['pages']),source_directory=str(folder))
 extra=[]
 if (R/'FINE-COMPLETION-FREEZE.json').exists():
  fine=json.loads((R/'FINE-COMPLETION-FREEZE.json').read_text());folder=Path(fine['directory']);review=folder/'REVIEW.json';receipt=folder/'SOURCE-QA-RECEIPT.json';assert receipt.exists()
  assert sha(review) in receipt.read_text() and combined['sources']['C-followup']['sha256']==sha(review)
  for name,h in fine['input_hashes'].items():assert sha(folder/name)==h;checks+=1
  receipts['C-followup']=dict(review_sha256=sha(review),QA_receipt_sha256=sha(receipt),pages=14,source_directory=str(folder));extra=[('C-followup',dict(directory=str(folder)))]
 old=json.loads((R/'BASELINE-REVIEW.json').read_text());current=json.loads((R/'registrar-only/REVIEW.json').read_text());pmap={p['task_id']:p for p in current['pages']}
 assert all(all(pmap[p['task_id']].get(k)==v for k,v in p.items()) for p in old['pages']),'Original ten-page review changed'
 baseline=json.loads((R/'BASELINE-45-LINES.json').read_text())['lines'];geometry=json.loads((R/'SHARED-LINE-GEOMETRY.json').read_text())['lines'];gmap={l['shared_line_id']:l for l in geometry};assert all(gmap.get(l['shared_line_id'])==l for l in baseline)
 assert status['registered_reading_blocks']+status['excluded_present_reading_units']==467
 out=R/'completed-source-freeze';out.mkdir(exist_ok=False)
 names=['REGISTRATION.json','SHARED-LINE-GEOMETRY.json','DROPPED-BLOCKS.csv','VISUAL-DROPPED-BLOCKS.csv','BLOCK-AUDIT.json','STATUS.json','REGISTRATION-SNAPSHOT.json','REVIEW-COMBINED.json','VERIFICATION.json','REPORT.txt','README.txt','GEOMETRY-RETENTION-DECISION.json','V4.2-TIMING-AUDIT.json','RESUME-AUTHORIZATION.json','PARALLEL-REGISTRAR-FREEZE.json','register.py','merge_reviews.py','verify.py','report_registration.py','finalize_registration.py']
 if extra:names.append('FINE-COMPLETION-FREEZE.json')
 names+=['FINE-COMPLETION-PRIMARY-QA-NOTE.json','HISTORICAL-DROPPED-BLOCKS.csv','DROP-HISTORY-INDEX.json','index_drop_history.py']
 for name in names:shutil.copy2(R/name,out/name)
 worker_provenance={}
 for role,part in list(assignment['partitions'].items())+extra:
  folder=Path(part['directory']);dest=out/('registrar-'+role);dest.mkdir()
  files=[p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.txt') and (p.name.upper().startswith(('REVIEW','CORRECTION','SOURCE-QA')) or p.name=='PROGRESS.txt')]
  for p in files:
   target=dest/p.relative_to(folder);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
  worker_provenance[role]={str(p.relative_to(folder)):sha(p) for p in files}
 freeze=dict(status='FULL_AVAILABLE_SOURCE_QUEUE_REVIEWED_AND_REGISTRATION_SEALED; DROPS_RETAINED',utc=datetime.now(timezone.utc).isoformat(),available_pages_reviewed=168,withheld_folios=34,shared_physical_lines=len(geometry),original45_unchanged=True,original_ten_page_review_unchanged=True,registered_reading_blocks=status['registered_reading_blocks'],excluded_present_reading_units=status['excluded_present_reading_units'],absent_reading_slots=status['absent_reading_slots'],physical_visual_drops=status['visual_dropped_blocks'],registrar_QA=receipts,assignment_input_hashes_verified=checks,worker_checkpoints_and_corrections=worker_provenance,files={n:sha(R/n) for n in names},timing_exception='v4.2 pre-registration freeze requirement NOT satisfied; prior geometry retained under explicit exception and human resume authorization.',scope='Registration only. No picture ratings, image labels, agreement, support, scientific controls, outcome joins or inferential tests.',geometry_limit='Conservative enclosing native writing-row rectangles; overlap may represent sloping spans/tall initials. Not pixel-tight ink masks or independent context validity.',v103='PARKED',Rosettes='No new leave-out grids',output_archive=str(out))
 (R/'FINAL-REGISTRATION-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n',encoding='utf-8');shutil.copy2(R/'FINAL-REGISTRATION-FREEZE.json',out/'FINAL-REGISTRATION-FREEZE.json')
 print(json.dumps({k:v for k,v in freeze.items() if k not in ('files','worker_checkpoints_and_corrections','registrar_QA')},indent=2))
if __name__=='__main__':main()
