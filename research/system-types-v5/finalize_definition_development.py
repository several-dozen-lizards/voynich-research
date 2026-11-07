"""Publish synthetic arithmetic progress while retaining every scientific execution gate."""
from pathlib import Path
import json,shutil,sys
from core import sha

ROOT=Path(__file__).resolve().parent;HERE=ROOT/'held-definition-development'
def save(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')

def stage():
    manifest=json.loads((ROOT/'DELIVERY-HASHES.json').read_text())
    assert all((ROOT/n).is_file() and sha(ROOT/n)==h for n,h in manifest.items())
    dest=HERE/'previous-cut2';dest.mkdir(exist_ok=True)
    for name in ('REPORT.md','STATUS.json','PROTOCOL.json','VERIFICATION.json','TEST-RESULTS.json','DELIVERY-HASHES.json','RETAINED-FAILURES.json','prepare.py'):
        if not (dest/name).exists():shutil.copyfile(ROOT/name,dest/name)
    save(HERE/'PREVIOUS-DELIVERY-AUDIT.json',dict(files=len(manifest),mismatches=[],previous_report_sha256=sha(dest/'REPORT.md')))
    print('Source-cut2 delivery verified and preserved:',len(manifest),'files')

def main():
    assert (HERE/'previous-cut2/REPORT.md').exists(),'preserve prior delivery before updating dispatcher'
    result=json.loads((HERE/'RESULTS.json').read_text());plan=json.loads((HERE/'REFERENCE-PLAN.json').read_text())
    assert all(sha(HERE/n)==h for n,h in plan['files'].items())
    assert sha(ROOT/'held.py')==plan['held_owner_sha256'] and not (ROOT/'FREEZE.json').exists()
    assert result['engineering_tests']==16 and not result['errors'] and not result['failures'] and result['decimal_oracle_cases']==250
    from finalize_source_cut2 import main as base
    base() # verifies source-cut2 owners, raw/source seals,50source tests and both execution locks
    report='''# H1/H2 log-odds reference arithmetic: synthetic qualification

This is an arithmetic reference tested only on hand-written and seeded synthetic integer tables. It does not implement scientific H1/H2 event extraction or recompute their targets. **H3 remains unresolved. No manuscript, real-source or G1–G6 output counts were used. Fresh reserves remain unparsed and held-out scoring stays locked.**

## What is implemented

For each stratum, the table is `[[a,b],[c,d]]`: exposure/reference rows and outcome yes/no columns. The reference calculates the natural logarithm of the Mantel–Haenszel pooled odds ratio:

`beta = log[(sum a*d/n) / (sum b*c/n)]`, with `n = a+b+c+d`.

It pools weighted cross-products rather than averaging stratum log odds or collapsing the tables first. The point-estimate formula was checked against the [official statsmodels implementation](https://www.statsmodels.org/stable/_modules/statsmodels/stats/contingency_tables.html#StratifiedTable.oddsratio_pooled). The installed Python environment has no statsmodels package; no statsmodels execution is claimed and no package was installed.

The API accepts immutable, explicitly synthetic tables. It has no word, corpus, availability-classifier or generator adapters. `held.py` is byte-for-byte unchanged; its score calls still refuse to execute without a complete claim freeze.

## Zero and support rules in the reference

- Empty tables and tables without exposure contrast or outcome variation contribute no information. Their full counts and exclusion reasons remain in the ledger.
- A zero cell alone does not force abstention: opposing separated strata can still produce a finite pooled estimate.
- Zero pooled denominator or numerator produces an explicit positive/negative-infinity status; neither becomes a finite estimate through half-counts or clipping. If both sums are zero, the result is `NO_INFORMATION`.
- Exact integer/rational sums preserve an odds ratio of exactly one. Near-one effects use a stable logarithm; effects outside floating-point range remain `NUMERIC_RANGE`, with the exact ratio retained. No arbitrary near-zero threshold is used.

These are qualified arithmetic behaviors, not an adopted scientific support policy. Finite-input rules for predictive intervals and elimination must still be fixed before claim scoring.

## H2 must use the approved log-odds scale explicitly

The user's decision to use log odds is retained. The literal reading of the spec's “H1 effect among available followers divided by aggregate effect,” with H1 on that approved scale, is `beta_available / beta_all`. The reference implements this as a **candidate scientific definition**, with componentwise-subset validation of available counts. The approved scale is not being reopened; the event and uncertainty protocol has not yet been frozen.

| Synthetic example | Overall OR | Available OR | Ratio of log effects | Ratio of ORs |
|---|---:|---:|---:|---:|
| Counts `[[10,10],[5,10]]`; subset `[[4,1],[1,2]]` |2|8|3|4|

If the overall OR is exactly one, its log effect is zero and this ratio is undefined, including the 0/0 case. The reference returns no H2 point value. It records the log-effect difference separately for diagnosis; **that difference has not replaced H2**. Direction reversal remains explicit. Small finite denominators are not clipped into apparent stability.

Uncertainty remains unqualified: a denominator distribution crossing zero can make a ratio interval unbounded, and event dependence prevents assuming an iid-table standard error is appropriate. Bootstrap/resampling units, near-null interval behavior and simultaneous predictive support still need a fixed protocol. The old 1.16–1.32 risk-difference ratios have not been imported as log-odds targets.

## Verification and remaining work

**16/16 synthetic engineering tests pass**, covering hand calculations, a stratification reversal, orientation/scaling invariance, support failures, separation, near-null numerical precision, subset constraints and the distinct ratio definitions. **250/250 seeded cases agree with a separate 80-digit Decimal implementation**, which uses no Fraction code from the reference. Maximum absolute log-effect error is reported in `RESULTS.json` (about 5.8e-15). This qualifies arithmetic, not uncertainty coverage or mechanism recovery.

Still pending: exact opener/context/ending selection and tie rules; within-page event construction; follower availability; H/F, hand and section strata; uncertainty/resampling; H5's between-section variance estimator; and a complete claim freeze. H3, H6–H8 method issues, layout conditioning and source/register limits remain as recorded. No definitions were inferred from fresh-reserve outcomes.

The preceding source-cut2 report and 1,158-file delivery audit are preserved under `previous-cut2/`; the source-cut2 report, 50 tests, 60 mapping checks and 22 generation checks remain a separate qualification. Reproduce this phase with `python system-types-v5/held-definition-development/qualify_arithmetic.py`, then `python system-types-v5/prepare.py`.
'''
    (HERE/'REPORT.md').write_text(report,encoding='utf-8')
    source_report=(ROOT/'REPORT.md').read_text()
    prefix='Latest continuation: synthetic H1/H2 log-odds arithmetic is qualified (16 engineering tests;250 independent high-precision checks). Scientific event definitions, uncertainty and targets remain unfrozen. H3 unresolved; held-out scoring locked. See `held-definition-development/REPORT.md`.\n\n'
    (ROOT/'REPORT.md').write_text(prefix+source_report,encoding='utf-8')
    status=json.loads((ROOT/'STATUS.json').read_text());status['status']='SOURCE_CUT2_AND_SYNTHETIC_ARITHMETIC_QUALIFIED_CLAIM_LOCKED'
    status['reference_arithmetic']=dict(report='held-definition-development/REPORT.md',tests=16,decimal_oracle_cases=250,event_builder=False,uncertainty_qualified=False,H2_estimand_adopted=False)
    for blocker in status['blockers']:
        if blocker['id']=='H1_H2_H5':
            blocker['status']='REFERENCE_MATH_QUALIFIED_SCIENTIFIC_DEFINITIONS_PENDING'
            blocker['detail']='Synthetic MH log-OR and candidate ratio-of-log-effects arithmetic qualified. No event builder, uncertainty or target recomputation. Availability/opener/context choices and H5 estimator remain to freeze; null log denominator is undefined, not epsilon-rescued.'
    save(ROOT/'STATUS.json',status)
    protocol=json.loads((ROOT/'PROTOCOL.json').read_text());protocol.update(version='v5-source-cut2-reference-arithmetic',status=status['status'],
        synthetic_arithmetic_reference='held-definition-development/REFERENCE-PLAN.json',synthetic_arithmetic_adopted_for_claim=False,
        H2_log_effect_ratio='candidate only; exact-null denominator undefined; no target values recomputed',blockers=status['blockers'])
    save(ROOT/'PROTOCOL.json',protocol)
    verification=json.loads((ROOT/'VERIFICATION.json').read_text());verification.update(status=status['status'],reference_arithmetic_tests=16,reference_decimal_oracle_cases=250,
        reference_event_builder=False,reference_uncertainty_qualified=False,H2_estimand_adopted=False,reference_plan_sha256=sha(HERE/'REFERENCE-PLAN.json'),
        reference_held_owner_unchanged=True,report_sha256=sha(ROOT/'REPORT.md'))
    save(ROOT/'VERIFICATION.json',verification);save(HERE/'VERIFICATION.json',dict(**result,root_report_sha256=sha(ROOT/'REPORT.md')))
    tests=json.loads((ROOT/'TEST-RESULTS.json').read_text());tests['separate_reference_arithmetic_qualification']=dict(tests=16,failures=0,errors=0,decimal_oracle_cases=250,command='python system-types-v5/held-definition-development/qualify_arithmetic.py',scope='synthetic counts only; separate from preceding50source tests')
    save(ROOT/'TEST-RESULTS.json',tests)
    save(HERE/'DELIVERY-HASHES.json',{str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=HERE/'DELIVERY-HASHES.json'})
    save(ROOT/'DELIVERY-HASHES.json',{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(ROOT/'RUNTIME') and not p.is_relative_to(ROOT/'G5-BUILD/classes') and p!=ROOT/'DELIVERY-HASHES.json'})
    print(json.dumps(dict(status=status['status'],synthetic_tests=16,decimal_oracle_cases=250,H3='UNRESOLVED',held_scoring=False,fresh_reserve_bodies_parsed=0)))

if __name__=='__main__':stage() if '--stage' in sys.argv else main()
