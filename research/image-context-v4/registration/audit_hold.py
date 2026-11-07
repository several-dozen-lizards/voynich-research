"""Administrative phase/timing audit only. Does not register, rate, join or score."""
from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
V=Path(__file__).resolve().parent.parent;R=V/'registration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 receipt=json.loads((V/'AMENDMENT-v4.2-RECEIPT.json').read_text());amend=V/receipt['amendment_file'];assert sha(amend)==receipt['amendment_sha256']
 now=datetime.now(timezone.utc).isoformat();archive=R/'hold-snapshots'/('v4.2-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));archive.mkdir(parents=True,exist_ok=False)
 names=['STATUS.json','PROTOCOL-v4.1.json','AMENDMENT-v4.2-effect-scale.md','AMENDMENT-v4.2-RECEIPT.json','registration/PROTOCOL.json','registration/GEOMETRY-FREEZE.json','registration/GEOMETRY-FREEZE-original.json','registration/GEOMETRY-FREEZE-v2.json','registration/REGISTRATION.json','registration/REGISTRATION-SNAPSHOT.json','registration/SHARED-LINE-GEOMETRY.json','registration/DROPPED-BLOCKS.csv','registration/BLOCK-AUDIT.json','registration/STATUS.json','registration/VERIFICATION.json','registration/registrar-only/REVIEW.json','registration/registrar-only/GEOMETRY-CANDIDATES.json','registration/GEOMETRY-CANDIDATES-failed-fleck-scale.json','registration/register.py','registration/extract.py','registration/extract-original.py','registration/extract-failed-fleck-scale.py','registration/registrar-only/PAGES.json','registration/registrar-only/EVT-STRUCTURE.json']
 snapshots={}
 for name in names:
  p=V/name
  if not p.exists():continue
  out=archive/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
  snapshots[name]=dict(sha256=sha(p),bytes=p.stat().st_size,last_write_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat())
 comparison={name:dict(at_sender_receipt=s['sha256'],at_local_hold=sha(V/name),unchanged=s['sha256']==sha(V/name)) for name,s in receipt['snapshot'].items() if (V/name).exists()}
 review=json.loads((R/'registrar-only/REVIEW.json').read_text());status=json.loads((R/'STATUS.json').read_text())
 audit=dict(status='HOLD; V4.2 PRE_REGISTRATION_TIMING_NOT_MET',audited_utc=now,amendment_received_utc=receipt['received_utc'],amendment_hash_verified=True,
  authority='Forwarded human-authorized v4.2 hold request received in coordinating chat; stop next safe boundary.',
  timing='Independent geometry review and registration ran before the v4.2 freeze. Cannot certify the requested pre-registration timing. Current registration ledger was regenerated after sender receipt to retain detailed visual abstention reasons; accepted shared geometry hash is unchanged relative to sender snapshot. Receipt file time is not a guarantee of when this coordinating chat learned of the amendment. Original artifacts and snapshots retained.',
  completed_before_hold=dict(source_input_preparation='168 native source pages and 34 withheld folios; EVT header-only manifest',candidate_extraction='First fleck-scale pass failed independent visual review and was retained; second proposal pass completed, unaccepted without review.',independent_registrar='Fresh agent, source-only inputs; no picture-box set, category labels or text outcomes supplied.',reviewed_source_pages=len(review['pages']),reviewed_folios=[p.get('folio',p['task_id']) for p in review['pages']],verified_physical_blocks=sum(b['decision']=='VERIFIED' for p in review['pages'] for b in p['blocks']),registered_reading_blocks=status['registered_reading_blocks'],shared_physical_lines=status['shared_physical_lines'],excluded_reading_units=status['excluded_reading_units']),
  visual_discrepancies='f94r nine visible writing rows vs eight H/F loci; f9r ten vs nine. Split-region ambiguities on f7r/f2r/f2v/f3r retained; no forced mapping.',
  rating_audit=dict(scope='This chat and its authorized registrar only; no claim about unobserved external rating calls.',picture_raters_launched=0,actual_picture_rating_responses=0,actual_rater_CSVs='None found; RATER-A/B/C files were blank .csv.template files only.',registrar_not_picture_rater=True,agreement='NOT RUN',picture_boxes_applied_to_lines=False),
  later_phases=dict(image_context_derivation='NOT RUN',outcome_blind_support='NOT RUN',synthetic_qualification='NOT RUN',outcome_join='NOT RUN',H_IMG='NOT RUN',H_PLANT='NOT RUN',optional_retrospective_OR_companion='NOT RUN'),
  current_hold='Registrar interrupted and given neutral stop instructions without amendment rationale/effect scales; administrative stop receipt requested. No further rating, geometry review, registration, support, joining or analysis.',v103='PARKED',Rosettes='No additional leave-out grids',sender_snapshot_comparison=comparison,preserved_files=snapshots,archive=str(archive))
 save(R/'V4.2-TIMING-AUDIT.json',audit);save(archive/'AUDIT.json',audit)
 marker=dict(status='HOLD_BY_HUMAN_V4.2',utc=now,authority='AMENDMENT-v4.2-RECEIPT.json',scope='No rating, geometry review, registration, support, controls, joining, agreement or scientific analysis until explicitly released after timing audit. Administrative preservation/audit only.',blindness='Do not show v4.2 or analyst rationale/outcomes to blind registrar or raters.',timing='Pre-registration freeze NOT certified; prior outputs retained as actually timed.',v103='PARKED',audit='registration/V4.2-TIMING-AUDIT.json')
 save(V/'HOLD.json',marker);save(R/'HOLD.json',marker)
 print(json.dumps(dict(status=audit['status'],reviewed_pages=len(review['pages']),shared_lines=status['shared_physical_lines'],picture_rating_calls=0,archive=str(archive),snapshot_comparison=comparison),indent=2))
if __name__=='__main__':main()
