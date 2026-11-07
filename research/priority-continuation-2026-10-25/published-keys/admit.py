"""Qualified-harness admission audit; no corpus loader and no score fabrication."""
import hashlib,json,sys
from pathlib import Path
P=Path(__file__).parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/HARNESS'))
import harness
qpath=ROOT/'ordered-name-lists-v7c/attempt-3-v7.2/QUALIFICATION.json'
q=json.loads(qpath.read_text(encoding='utf-8'))
if q['status']!='QUALIFIED_V7.2_ON_DECLARED_SCOPE' or not all(q['gates'].values()) or len(q['gates'])!=11:raise SystemExit('Qualification receipt not accepted')
results=[]
for item in json.loads((P/'INTAKE.json').read_text(encoding='utf-8'))['candidates']:
    reasons=list(item['barriers'])
    try:
        harness.validate_key(item['key'] or {})
    except (harness.NotTestable,TypeError) as exc:reasons.append('Qualified key validator: '+str(exc))
    if not item.get('heldout'):reasons.append('Custody gate: no cohort to pass to custody_check; no corpus opened')
    # This is an intake runner only. A fully admitted packet requires the owning v7.2
    # source-first dual-bank evaluator, never the original v7.0 evaluate() shortcut.
    results.append(dict(id=item['id'],status='NOT_TESTABLE_AT_INTAKE' if reasons else 'READY_FOR_V7_2_DUAL_BANK_DISPATCH',reasons=reasons,scientific_verdict=None,numeric_scores=None,manuscript_rows_loaded=0))
out=dict(qualification_status=q['status'],qualification_sha256=hashlib.sha256(qpath.read_bytes()).hexdigest(),gates_checked=11,candidates=results,scored=0,not_testable=sum(r['status']=='NOT_TESTABLE_AT_INTAKE' for r in results),source_transcription_complete=False,vault_project_data_accessed=False)
(P/'ADMISSION-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(scored=out['scored'],not_testable=out['not_testable'],qualification=out['qualification_status'])))
