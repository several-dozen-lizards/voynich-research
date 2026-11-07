"""Retrospective eligibility, separate from unchanged v7.2 prospective custody."""
RESERVED={'f72v1','f72v2','f73r','f73v'}
TIER='RETROSPECTIVE: built-on status unknown'
class NotTestable(ValueError):pass

def select(rows,examples,reading):
    if reading not in ('H','F'):raise NotTestable('explicit reading required')
    if examples.get('unresolved'):raise NotTestable('unresolved cited-example identity')
    if not examples.get('source_manifest_sha256'):raise NotTestable('frozen primary example provenance required')
    ids=set(examples.get('record_ids',[]));folios=set(examples.get('folios',[]));loci=set(examples.get('loci',[]))
    seen=set();kept=[];excluded=[]
    for row in rows:
        if row['id'] in seen:raise NotTestable('duplicate source record')
        seen.add(row['id'])
        if row.get('reading')!=reading:raise NotTestable('missing or pooled reading')
        reason=None
        if row.get('folio') in RESERVED or row.get('vault'):reason='VAULT CLOSED'
        elif row['id'] in ids or row.get('folio') in folios or row.get('locus') in loci:reason='AUTHOR CITED EXAMPLE'
        if reason:excluded.append(dict(id=row['id'],reason=reason));continue
        # Preserve raw source custody; never manufacture independent held-out status.
        kept.append(row)
    if not kept:raise NotTestable('empty admitted retrospective cohort')
    return dict(tier=TIER,reading=reading,rows=kept,excluded=excluded,unknown_built_on_allowed=True,independent_holdout_claim=False)

def interpret(verdict,qualified):
    if not qualified:return 'NOT TESTABLE: scorer/input regime not qualified'
    return {'FAIL':'REJECT FIXED KEY ON DECLARED TESTED SCOPE','PASS':'RETROSPECTIVE COMPATIBILITY ONLY; PROSPECTIVE FOLLOW-UP REQUIRED','PARTIAL':'DESCRIPTIVE ONLY; DO NOT PROMOTE','NOT TESTABLE':'NO SCIENTIFIC VERDICT'}[verdict]
