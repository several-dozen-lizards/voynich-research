"""Explicit retrospective schema adapter; never converts rows to unbuilt custody."""
from pathlib import Path
import sys,copy,json,hashlib
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/HARNESS'))
import harness
from custody import TIER,select,NotTestable

def admit(key,rows,examples,reading,publication):
    if not publication or not isinstance(publication,str):raise NotTestable('primary publication citation required')
    cohort=select(rows,examples,reading);normalized=copy.deepcopy(key)
    # The old schema requires a truthy process_evidence field. Supply the actual
    # retrospective process record, explicitly stating unknown exposure, never a fictitious holdout proof.
    normalized['process_evidence']=dict(tier=TIER,publication=publication,built_on_status='unknown outside author examples',prior_process_evidence=copy.deepcopy(key.get('process_evidence')),independent_holdout_claim=False)
    normalized['built_on']=sorted(set(normalized.get('built_on',[]))|set(examples.get('record_ids',[]))|set(examples.get('folios',[])))
    harness.validate_key(normalized)
    if normalized['map']!=key['map'] or normalized['rules']!=key['rules']:raise AssertionError('key changed')
    return dict(tier=TIER,key=normalized,cohort=cohort,publication=publication,independent_holdout_claim=False,scientific_scoring='Still requires qualified tokenizer/uncertainty/target resources and unchanged dual-bank evaluation')
