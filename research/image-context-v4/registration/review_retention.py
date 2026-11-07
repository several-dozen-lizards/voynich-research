"""Administrative retention decision. Never rates, registers, joins or scores."""
from pathlib import Path
import json,hashlib,collections
from datetime import datetime,timezone
V=Path(__file__).resolve().parent.parent;R=V/'registration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit=json.loads((R/'V4.2-TIMING-AUDIT.json').read_text());receipt=json.loads((V/'AMENDMENT-v4.2-RECEIPT.json').read_text())
 assert sha(V/receipt['amendment_file'])==receipt['amendment_sha256']
 integrity={n:sha(V/n)==s['sha256'] for n,s in audit['preserved_files'].items()};assert all(integrity.values())
 hold_hashes=json.loads((R/'HOLD-AUDIT-HASHES.json').read_text());assert all(sha(R/n)==h for n,h in hold_hashes.items())
 target=receipt['snapshot']['registration/REGISTRATION.json']['sha256'];prior=[p for p in (R/'snapshots').rglob('REGISTRATION.json') if sha(p)==target];assert prior
 old=json.loads(prior[0].read_text());current=json.loads((R/'REGISTRATION.json').read_text());geometry=json.loads((R/'SHARED-LINE-GEOMETRY.json').read_text())
 assert old['accepted']==current['accepted']
 assert set(old)==set(current) and all(old[k]==current[k] for k in old if k!='dropped')
 assert len(old['dropped'])==len(current['dropped'])
 fields=collections.Counter()
 for a,b in zip(old['dropped'],current['dropped']):
  assert (a['folio'],a['unit'],a['reading'])==(b['folio'],b['unit'],b['reading'])
  changed={k for k in set(a)|set(b) if a.get(k)!=b.get(k)};fields.update(changed)
  assert changed <= {'block_id','visible_lines','detail'}
  assert all(a.get(k)==b.get(k) for k in ('status','reason','expected_lines'))
 expected_geom=receipt['snapshot']['registration/SHARED-LINE-GEOMETRY.json']['sha256'];assert sha(R/'SHARED-LINE-GEOMETRY.json')==expected_geom
 assert len(geometry['lines'])==45 and len(current['accepted'])==8
 saved=json.loads((R/'REGISTRAR-HOLD-RECEIPT.json').read_text())
 decision=dict(status='RETAIN_EXISTING_BLIND_GEOMETRY_WITH_DOCUMENTED_TIMING_EXCEPTION',decided_utc=datetime.now(timezone.utc).isoformat(),authority='User requested review and a decision on retention before resuming registration; no resumption requested by this record.',
  retained=dict(shared_line_file='SHARED-LINE-GEOMETRY.json',sha256=expected_geom,physical_lines=45,physical_blocks=4,folios=['f3v','f7v','f9v','f93v'],reading_specific_block_maps=8,review_file='registrar-only/REVIEW.json',review_sha256=sha(R/'registrar-only/REVIEW.json'),saved_reviewed_pages=10),
  grounds=[
   'The registrar used a fresh isolated context with source images, dimensions and header-only P-unit locator/count inputs; no text-event outcomes or either picture-rater set was supplied. Blindness is supported by task/input provenance and the registrar receipt, not claimed as an OS-enforced access guarantee.',
   'v4.2 changes the analytical effect scale, variances, controls, base-rate reporting and a post-join abstain-only gate; it does not change the writing-box geometry, EVT line order or exact per-reading registration rule.',
   'The accepted geometry and accepted locus mappings exactly match the sender amendment-receipt snapshot. Subsequent changes are limited to explanatory/exclusion metadata; no admission/drop decision, expected count or accepted line mapping changed.',
   'No picture-rating calls, picture-box application, image-context derivation, agreement, outcome-blind support, synthetic qualification, outcome join or inferential test ran in this chat before the hold.',
   'Discarding independent source measurements and repeating them now would not restore the missed pre-registration timing. Retaining the original evidence with its actual chronology is more transparent.'
  ],
  timing_exception=dict(preserved=True,pre_registration_v42_freeze_satisfied=False,classification='Procedural exception: source geometry/registration preceded v4.2. Do not describe the entire pipeline as prospectively frozen before registration.',earliest_saved_geometry='See original snapshot/file chronology; timestamps are recorded evidence rather than proof of when amendment notice was read.',audit_file='V4.2-TIMING-AUDIT.json',audit_sha256=sha(R/'V4.2-TIMING-AUDIT.json')),
  scope_limits=[
   'Retention establishes eligibility of the existing source-only measurements; it is not a re-certification of every box or a scientific result.',
   'The 45 lines are partial coverage, not a chosen inferential cohort. Continue the frozen full source-page queue only after explicit release; do not score this convenient subset.',
   'Preserve every mismatch, ambiguous block and unreviewed unit. f94r and f9r remain excluded; disconnected-region ambiguities remain unresolved.',
   'All later geometry corrections must be based only on source geometry, logged as new versions with reasons; no replacement based on effects, image-category agreement, support, power or passing a test.',
   'The second automatic proposal pass remains unaccepted until independent visual review. The failed first pass remains retained.',
   'Four additional images were already viewed before interruption without saved geometry: '+', '.join(saved['additional_source_images_viewed_before_interrupt'])+'. They are not newly unseen registrar material.',
   'Before analysis, freeze all unresolved numerical conventions and control generators under v4.1/v4.2. This retention decision does not approve or implement the statistical specification.'
  ],
  blindness=dict(raters='No analyst amendment, rationale, results, source crosswalk or shared writing geometry sent to picture raters; picture-only manual stands.',registrar='Remain blind to both picture-rater box sets and outcomes. Any future resume message must be neutral and contain no v4.2 rationale, scales, base rates or expectations.'),
  verification=dict(held_artifacts_checked=len(integrity),all_held_hashes_unchanged=True,accepted_mapping_unchanged=True,geometry_unchanged=True,drop_decisions_unchanged=True,exclusion_metadata_fields_changed=dict(fields),sender_registration_snapshot=str(prior[0]),hold_receipt_verified=True),
  phase_permissions=dict(retention_decision='COMPLETE',registration='STILL ON HOLD; no registrar resumed',picture_rating='STILL ON HOLD',support_controls_join_analysis='STILL ON HOLD',v103='PARKED',Rosettes='No additional leave-out grids'),
  no_new_scientific_data=True)
 (R/'GEOMETRY-RETENTION-DECISION.json').write_text(json.dumps(decision,indent=2)+'\n',encoding='utf-8')
 (R/'GEOMETRY-RETENTION-DECISION.txt').write_text('Decision: retain the existing blind geometry with the documented v4.2 timing exception.\n\n45 shared physical lines across f3v/f7v/f9v/f93v and their 8 H/F block mappings remain unchanged. All held artifact hashes match. The later ledger revision altered exclusion metadata only; accepted geometry/mappings and drop decisions are unchanged.\n\nv4.2 changes analysis, not writing geometry or exact-count registration. The independent registrar had no picture-rater boxes or text outcomes, and no picture ratings, image contexts, agreement, support, controls, joins or inference ran here. Repeating the same source measurement now would not undo the actual timing failure.\n\nThe required pre-registration v4.2 freeze was NOT met. Preserve that procedural exception in all later reports; do not claim blanket prospective preregistration. Retention is not full-cohort completion or a guarantee of pixel-perfect annotation. Keep all drops, discrepancies and failed candidate passes. Any future source-based correction needs a reason and version; never replace geometry to improve downstream outcomes. The 45 lines must not become a conveniently selected test subset.\n\nNo work was resumed. Registration, rating, support and analysis remain on hold until explicitly released. Keep the registrar and raters blind; v103 stays parked; no Rosettes leave-out grids.\n',encoding='utf-8')
 names=['review_retention.py','GEOMETRY-RETENTION-DECISION.json','GEOMETRY-RETENTION-DECISION.txt']
 (R/'RETENTION-DECISION-HASHES.json').write_text(json.dumps({n:sha(R/n) for n in names},indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status=decision['status'],lines=45,checks=decision['verification'],resumed=False),indent=2))
if __name__=='__main__':main()
