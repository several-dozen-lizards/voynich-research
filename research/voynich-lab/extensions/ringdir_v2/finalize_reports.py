"""Post-run report-only completion. Never generates, fits, or scores calibration."""
import argparse
import json
from pathlib import Path
import run_v2 as v

RECEIPT=v.HERE/'reporting_receipt'


def register():
    v.check()
    assert not (v.OUT/'STATUS.json').exists(), 'Do not replace an existing run summary'
    RECEIPT.mkdir()
    v.save(RECEIPT/'REGISTRATION.json',dict(utc=v.stamp(),scope='Report-only path normalization after all arm receipts; no calibration rerun',
        reason='Registered aggregate plot lookup used forward slashes; Windows chain labels used backslashes; StopIteration before aggregate summary.',
        finalizer_sha256=v.rd.sha(Path(__file__)),
        calibration_registration_sha256=v.rd.sha(v.REG/'REGISTRATION.json'),
        prior_outputs={str(p.relative_to(v.OUT)):v.rd.sha(p) for p in sorted(v.OUT.rglob('*')) if p.is_file()}))
    print('Registered report-only finalizer after calibration; source arm artifacts committed')


def run():
    receipt=v.load(RECEIPT/'REGISTRATION.json')
    assert v.rd.sha(Path(__file__))==receipt['finalizer_sha256']
    v.check()
    for name,h in receipt['prior_outputs'].items():assert v.rd.sha(v.OUT/name)==h,name
    results=[]
    for p in sorted(v.OUT.rglob('STATUS.json')):
        if p.parent==v.OUT:continue
        results.append(dict(chain=p.parent.relative_to(v.OUT).as_posix(),**v.load(p)))
    assert len(results)==36, len(results)
    v.plot_results(results)
    def result(chain):return next((r for r in results if r['chain']==chain),None)
    summary=[]
    for corpus in ['ZL','Latin','G2','G3','G4','Naibbe']:
        for signal in ['word','glyph','stem','pos','p1','S-m','combination']:
            d=result(f'D/{corpus}/{signal}');p=result(f'P/{corpus}/{signal}');ud=result(f'U/{corpus}/{signal}/D')
            up=result(f'U/{corpus}/{signal}/P');f=result(f'F/{corpus}/{signal}')
            def passing(r):return r.get('passing_bins',[]) if r and r['status']=='PASS' else []
            summary.append(dict(corpus=corpus,signal=signal,
                D_L_min=d.get('L_min') if d else None,D_status=d['status'] if d else ('NOT_RUN_MISSING_SOURCE' if signal=='stem' else 'NOT_APPLICABLE'),
                D_passing_bins=json.dumps(passing(d)),P_status=p['status'] if p else 'NOT_APPLICABLE',P_passing_bins=json.dumps(passing(p)),
                U_D_status=ud['status'] if ud else 'NOT_APPLICABLE',U_P_status=up['status'] if up else 'NOT_APPLICABLE',
                matched_D_U_bins=json.dumps(sorted(set(passing(d))&set(passing(ud)))),
                matched_P_U_bins=json.dumps(sorted(set(passing(p))&set(passing(up)))),
                K_status=(result(f'K/{corpus}') or {}).get('status','NOT_APPLICABLE'),
                O_pos_status=(result(f'O/{corpus}/pos') or {}).get('status','NOT_APPLICABLE'),
                O_p1_status=(result(f'O/{corpus}/p1') or {}).get('status','NOT_APPLICABLE'),
                O_specified_combination='NOT_RUN_MISSING_SOURCE',
                F_status=f['status'] if f else 'NOT_APPLICABLE',F_L_min=f.get('L_min') if f else None))
    v.save(v.OUT/'SUMMARY.json',results)
    v.rd.table(v.OUT/'summary.csv',summary)
    v.save(v.OUT/'REPORTING_FAILURE.json',dict(status='PRESERVED_REPORTING_ONLY_FAILURE',
        error='StopIteration in registered plot_results: Windows path separator mismatch',
        calibration_rerun=False,registered_instrument_edited=False,
        completed_by='extensions/ringdir_v2/reporting_receipt/REGISTRATION.json'))
    status=dict(status='PHASE0_COMPLETE_WITH_FAILURES',registered='RD-v2',
        failed_chains=[r['chain'] for r in results if r['status'].startswith('FAIL')],
        prior_runs_unchanged=True,radial='HELD',real_ring_scores_computed=False,
        phases_1_plus_run=False,corrected_order_generated=False,
        report_only_recovery=True,calibration_rerun=False,utc=v.stamp())
    v.save(v.OUT/'STATUS.json',status)
    text=['# RD-v2 Phase 0','', '| Chain | Outcome |','|---|---|']
    text += [f"| {r['chain']} | {r['status']} |" for r in results]
    text += ['', '| ZL direction signal | 6–10 | 11–20 | 21–40 | 41–80 |', '|---|---:|---:|---:|---:|']
    for sig in ['word','glyph']:
        d=result('D/ZL/'+sig)
        text.append('| '+sig+' | '+' | '.join(f"{m['accuracy']:.1%}" for m in d['bins'] if m['bin']>=2)+' |')
    text += ['', '**Cross-boundary unit direction:** freshly qualified ZL bins6–10,11–20,21–40,41–80. '
        'Its uncertainty-inclusive counterpart also qualifies those bins. Every word/glyph direction '
        'shuffle-null check is retained in its chain receipt; failures cannot be overridden by prior runs.','',
        '**Fresh word-bigram direction:** ZL no bin qualifies; 41–80 accuracy77.5% with '
        'cluster95% CI64.4–87.3%, below the registered80% threshold. RD-v1/C2 are not overwritten.','',
        '**Pooled direction:** ZL clean and uncertainty-inclusive word/glyph pooled chains do not qualify. '
        'Clean21–40 comprises13 loci; the uncertainty-inclusive planned21–40 set comprises47. '
        'The full mixed-condition, forward/reverse and weighting rates appear in each P/U-P bin table. '
        'Limited family-level power is retained, not replaced by individual-locus accuracy.','',
        '**Paragraph-origin S-p1:** isolated known-direction21–40 gate passes:98 paragraphs, '
        '57.1% hit,16.9% mean chance, excess95% CI31.0–48.8 percentage points. '
        'End-to-end with freshly inferred word direction is38.8% (descriptive, not a passed end-to-end gate). '
        'At41–80 isolated hits41.7% fail the50% threshold despite positive excess. '
        'S-pos origin does not qualify. The paragraph-to-ring transfer assumption remains untested.','',
        '**Seam count:** unsupported in both corpora. ZL k=1 at21–40 has3 examples from1 family, '
        'and41–80 has0. No seam-count accuracy was invented.','',
        'Stem-collapse, S-m and the specified three-signal combination are NOT_RUN_MISSING_SOURCE. '
        'The exact Oct22 definitions were not substituted. F uses bound engineering generators and '
        'Naibbe source/table; its full direction curves are descriptive, not mechanism identification. '
        'T is registered for a later descriptive comparison only.','',
        'U preserves first alternatives and unknown barriers. Latin has no independent uncertainty '
        'annotation and is an unmarked control; K/O Latin uses artificial layout. Shared-source '
        'Monte Carlo sets are not independent manuscript replications. All predictions and failures '
        'are reported without choosing a successful replacement pipeline.','',
        'Every calibration chain completed or stopped before final aggregation. A Windows path-label '
        'mismatch then failed report assembly. The frozen instrument and all arm artifacts were left '
        'unchanged. The report-only finalizer is separately hash-bound in reporting_receipt, and no '
        'calibration was rerun. See REPORTING_FAILURE.json.','',
        '**Preservation:** earlier run hashes unchanged; radial held; no real-ring scores, '
        'Phase1+ comparisons or corrected-order export.','']
    (v.OUT/'report.md').write_text('\n'.join(text),encoding='utf-8')
    for name,h in receipt['prior_outputs'].items():assert v.rd.sha(v.OUT/name)==h,name
    v.check()
    v.save(v.OUT/'ARTIFACT_MANIFEST.json',dict(hashes={str(p.relative_to(v.OUT)):v.rd.sha(p)
        for p in sorted(v.OUT.rglob('*')) if p.is_file()}))
    print('Report-only completion finished; 36 chain receipts; no calibration rerun')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','run'])
    register() if p.parse_args().action=='register' else run()
