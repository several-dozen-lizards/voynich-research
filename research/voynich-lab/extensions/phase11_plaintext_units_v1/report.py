"""Verify saved Phase11 control artifacts and write the factual readout."""
import csv
import json
import math
from collections import Counter
import run as p

def main():
    p.verify()
    qual=json.loads((p.HERE/'QUALIFICATION.json').read_text())
    bands=json.loads((p.HERE/'BAND.json').read_text())
    records=[]; vectors={}; raw=[]; expected=set()
    for code in ['C1','C2','C3','C13','Occitan']:
        for seed in p.SEEDS:
            train,test,truth,split=p.split_noise(p.source(code),seed)
            raw.append(p.metrics([tuple(w) for w in test]))
            for method in p.METHODS:
                name=f'natural-{code}-{seed}-{method}.json'; expected.add(name)
                r=json.loads((p.HERE/'results'/name).read_text())
                assert r['split']==split
                for stage in ['pre','post']: vectors.setdefault((method,stage),[]).append(r[stage])
    assert p.band(raw)==bands['raw_letters']
    for (method,stage),rows in vectors.items(): assert p.band(rows)==bands[method][stage]
    for code in ['C1','C2']:
        for deck in [52,78]:
            for seed in p.SEEDS:
                for method in p.METHODS: expected.add(f'positive-{code}-{deck}-{seed}-{method}.json')
    for code in ['C7','C8','C9','C11','C17']:
        for seed in p.SEEDS:
            for method in p.METHODS: expected.add(f'negative-{code}-{seed}-{method}.json')
    actual={f.name for f in (p.HERE/'results').glob('*.json')}
    assert actual==expected,(len(actual),len(expected),expected-actual,actual-expected)
    for name in sorted(actual):
        r=json.loads((p.HERE/'results'/name).read_text())
        for stage in ['pre','post']:
            records.append(dict(kind=name.split('-')[0],family=r['family'],deck=r.get('deck'),seed=r['seed'],
                                method=r['method'],stage=stage,
                                **{k:r[stage][k] for k in p.KEYS},valid=r[stage]['valid'],
                                pipeline_band=p.inside(r[stage],bands[r['method']][stage]),
                                literal_letter_band=p.inside(r[stage],bands['raw_letters']),
                                primary_membership=p.primary(r[stage],bands,r['method']) if stage=='post' else None,
                                boundary_f1=r.get('boundary',{}).get('f1'),
                                train_words=r['split']['train_words'],test_words=r['split']['test_words'],
                                K=r['merge']['selected_K'],mdl_cap=r['tokenizer'].get('cap_reached'),
                                unknown_units=r['unknown_units']))
    with (p.HERE/'METRICS.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
    for c in qual['positive_cells']:
        rows=[r for r in records if r['kind']=='positive' and r['family']==c['family'] and r['deck']==c['deck'] and r['method']==c['method'] and r['stage']=='post']
        n=sum(r['primary_membership'] and r['boundary_f1'] is not None and r['boundary_f1']>=.8 for r in rows)
        assert n==c['successes'] and c['passed']==(n>=16)
    for c in qual['negatives']:
        rows=[r for r in records if r['kind']=='negative' and r['family']==c['family'] and r['stage']=='post']
        n=sum(any(r['primary_membership'] for r in rows if r['seed']==seed) for seed in p.SEEDS)
        assert n==c['hits'] and c['non_discriminating']==(n>=4)
    assert qual['band_sha256']==p.sha(p.HERE/'BAND.json')
    assert qual['registration_sha256']==p.sha(p.HERE/'REGISTRATION.json')
    eligible=[m for m in p.METHODS if all(c['passed'] for c in qual['positive_cells'] if c['method']==m)]
    specificity=all(not c['non_discriminating'] for c in qual['negatives'])
    assert qual['eligible_tokenizers']==eligible and qual['calibration_pass']==bool(eligible)
    assert qual['specificity_pass']==specificity
    assert qual['status']==('PASS' if eligible and specificity else 'NON_DISCRIMINATING' if not specificity else 'CALIBRATION_FAILED')
    # Reconstruct the user's stated pipeline-only gate as well as the extra
    # conservative gate in our seal. No refits, altered intervals or selection.
    requested_positive=[]
    for c in qual['positive_cells']:
        rows=[r for r in records if r['kind']=='positive' and r['family']==c['family'] and r['deck']==c['deck'] and r['method']==c['method'] and r['stage']=='post']
        n=sum(r['pipeline_band'] and r['boundary_f1'] is not None and r['boundary_f1']>=.8 for r in rows)
        requested_positive.append(dict(family=c['family'],deck=c['deck'],method=c['method'],successes=n,passed=n>=16))
    requested_eligible=[m for m in p.METHODS if all(c['passed'] for c in requested_positive if c['method']==m)]
    requested_negative=[]
    for c in qual['negatives']:
        rows=[r for r in records if r['kind']=='negative' and r['family']==c['family'] and r['stage']=='post']
        n=sum(any(r['pipeline_band'] for r in rows if r['seed']==seed) for seed in p.SEEDS)
        requested_negative.append(dict(family=c['family'],hits=n,rate=n/20,non_discriminating=n>=4))
    requested_specificity=all(not c['non_discriminating'] for c in requested_negative)
    requested_status='PASS' if requested_eligible and requested_specificity else 'NON_DISCRIMINATING' if not requested_specificity else 'CALIBRATION_FAILED'
    disjoint={m:[k for k in p.KEYS if max(bands[m]['post']['intervals'][k][0],bands['raw_letters']['intervals'][k][0])>
                    min(bands[m]['post']['intervals'][k][1],bands['raw_letters']['intervals'][k][1])] for m in p.METHODS}
    p.dump(p.HERE/'REQUESTED_RULE_AUDIT.json',dict(status=requested_status,
           label='User-stated pipeline-only membership, reconstructed without any refit or changed band; extra anchor excluded',
           positive_cells=requested_positive,eligible_tokenizers=requested_eligible,negatives=requested_negative,
           calibration_pass=bool(requested_eligible),specificity_pass=requested_specificity,
           extra_anchor_design_error=dict(disjoint_dimensions=disjoint,
                limitation='Extra anchor made some combined gates impossible; preserve sealed results but do not substitute them for requested gate'),
           band_sha256=p.sha(p.HERE/'BAND.json'),qualification_sha256=p.sha(p.HERE/'QUALIFICATION.json')))
    lines=['# Phase 11 — plaintext-unit search', '',f"Requested identical-pipeline rule: **{requested_status}**. Sealed extra-anchor rule: **{qual['status']}**.", '',
           f"Pipeline-only positive calibration: {'PASS' if requested_eligible else 'FAIL'}. Pipeline-only full-search specificity: {'PASS' if requested_specificity else 'FAIL'}. Voynich: **{qual['voynich']}**. Two-table secondary: **CLOSED**.", '',
           'All 840 registered fits completed: 300 natural-band fits, 240 positive fits, 300 negative fits. Twenty split/noise replicates per frozen source; these are not independent texts. Registration preceded fitting; the natural band was sealed before positive/negative fitting. No target A/B feature computation, segmentation or scoring was performed by this instrument.', '',
           '**Protocol limitation:** I added a literal-letter anchor beyond the requested identical-pipeline band. The frozen bands have disjoint ranges in '+str(disjoint)+', making those combined gates impossible to pass. That is an implementation-design error, not a scientific failure of tokenization. Both rules are reported; REQUESTED_RULE_AUDIT.json applies the user-stated pipeline band without the extra anchor to exactly the same saved results, without refits, revised intervals, or winner selection. The sealed protocol and original qualification remain unchanged.', '',
           '## Positive calibration', '',
           'A pipeline joint success requires boundary F1 >= .8 and post-merge membership in the identical-pipeline band in the same replicate. The sealed extra-anchor joint success additionally requires literal-letter membership. A branch needs >=16/20 successes in every language/deck cell.', '',
           '| Source | Deck | Tokenizer | Pipeline joint successes | Extra-anchor joint successes | Median boundary F1 | Pipeline-only hits | Literal-letter hits |',
           '|---|---:|---|---:|---:|---:|---:|---:|']
    for c in qual['positive_cells']:
        rows=[r for r in records if r['kind']=='positive' and r['family']==c['family'] and r['deck']==c['deck'] and r['method']==c['method'] and r['stage']=='post']
        f1=[r['boundary_f1'] for r in rows if r['boundary_f1'] is not None]
        med=float(p.np.median(f1)) if f1 else None
        req=next(x['successes'] for x in requested_positive if x['family']==c['family'] and x['deck']==c['deck'] and x['method']==c['method'])
        lines.append(f"| {c['family']} | {c['deck']} | {c['method']} | {req}/20 | {c['successes']}/20 | {med:.3f} | {sum(r['pipeline_band'] for r in rows)}/20 | {sum(r['literal_letter_band'] for r in rows)}/20 |" if med is not None else f"| {c['family']} | {c['deck']} | {c['method']} | {req}/20 | {c['successes']}/20 | NA | NA | NA |")
    lines += ['', 'Eligible tokenizer branches under requested rule: '+(', '.join(requested_eligible) or 'none')+'.', '',
              '## Specificity', '',
              'Pipeline-only family union counts follow; the extra-anchor counts remain in QUALIFICATION.json.', '',
              '| Negative | Any-tokenizer pipeline hits | Rate | Descriptive Wilson 95% interval | >=20% stop rule |', '|---|---:|---:|---:|---|']
    for c in requested_negative:
        rate=c['rate']; den=1+1.96**2/20
        center=(rate+1.96**2/40)/den
        half=1.96*math.sqrt(rate*(1-rate)/20+1.96**2/(4*20**2))/den
        lines.append(f"| {c['family']} | {c['hits']}/20 | {rate:.0%} | {max(0,center-half):.1%}–{min(1,center+half):.1%} | {'TRIGGERED' if c['non_discriminating'] else 'not triggered'} |")
    lines += ['', 'The denominator is fixed at 20 for each family. Wilson intervals are descriptive only: these dependent fixed-source/noise replicates do not justify independent-trial population inference. C13 and C17 retain their shorter real source size. C8 is the real pinned Timm–Schinner output; its generator seed was not resampled. C11 retains its manuscript dependence. Passing this finite negative bank is not a general proof that gibberish cannot reach natural statistics.', '',
              '## Band and selection checks', '',
              'h1=H(U), h2=H(next U | U), no spaces and no cross-word transitions. Seven marginal 95% ranges are intersected, so overall acceptance coverage is not 95%. Post-merge acceptance additionally requires the frozen raw-letter reference. No metric is used to choose tokenizer length or context inventory; training description lengths select those quantities.', '',
              '| Tokenizer | Pre-merge natural self-coverage | Post-merge natural self-coverage |', '|---|---:|---:|']
    for m in p.METHODS:
        lines.append(f"| {m} | {bands['self_coverage'][m]['pre']:.0%} | {bands['self_coverage'][m]['post']:.0%} |")
    lines += ['', '## Descriptive failure diagnosis (not a new gate)', '',
              '| Positive tokenizer | F1 >= .8 | Post-merge vectors in pipeline band | Post-merge vectors in literal-letter band |',
              '|---|---:|---:|---:|']
    for m in p.METHODS:
        rows=[r for r in records if r['kind']=='positive' and r['method']==m and r['stage']=='post']
        lines.append(f"| {m} | {sum(r['boundary_f1'] is not None and r['boundary_f1']>=.8 for r in rows)}/80 | {sum(r['pipeline_band'] for r in rows)}/80 | {sum(r['literal_letter_band'] for r in rows)}/80 |")
    failures={}; pipeline_failures={}
    for m in p.METHODS:
        rows=[r for r in records if r['kind']=='positive' and r['method']==m and r['stage']=='post']
        failures[m]={k:dict(below=sum(r[k]<bands['raw_letters']['intervals'][k][0] for r in rows if r[k] is not None),
                           above=sum(r[k]>bands['raw_letters']['intervals'][k][1] for r in rows if r[k] is not None)) for k in p.KEYS}
        pipeline_failures[m]={k:dict(below=sum(r[k]<bands[m]['post']['intervals'][k][0] for r in rows if r[k] is not None),
                           above=sum(r[k]>bands[m]['post']['intervals'][k][1] for r in rows if r[k] is not None)) for k in p.KEYS}
    p.dump(p.HERE/'DIAGNOSTICS.json',dict(label='posthoc description only, no method or gate changes',
                literal_letter_coordinate_failures=failures,pipeline_coordinate_failures=pipeline_failures))
    lines += ['', 'The literal-letter mean word-length reference is '+str(bands['raw_letters']['intervals']['word_length'])+' units per observed word. Naibbe standard respacing discards original plaintext word boundaries and creates one/two-letter groups. Correct chunk recovery therefore does not imply ordinary plaintext word lengths under ciphertext spaces. This is a calibration-design limitation, not evidence against language in the manuscript. Context-only homophone merging can also erase distinctions; inspect saved maps and inventory counts. DIAGNOSTICS.json records coordinate failure counts without changing the frozen rules.', '']
    lines += ['', 'Full pre/post vectors, word counts, OOV units and MDL endpoint flags: METRICS.csv. BAND.json contains all intervals; results/*.json contain split receipts, tokenizer paths, maps, context-merge objectives and boundary counts. Low reference self-coverage limits the test; it is not repaired after the scores.', '',
              '## Interpretation and relation to prior work', '',
              'This is a bounded operational search, not an exhaustive theorem about possible segmentations. T-MDL has a frozen 64-merge BPE-path cap. Tokenizers are independently fitted on training halves; context merges are distributional and selected by training MDL. Published Naibbe and Zattera inventories are non-blind. Noise/boundary survival, OCR, genre, short-source bias, and original-space conventions limit interpretation.', '',
              '[Zattera](https://ceur-ws.org/Vol-3313/paper10.pdf) supplies the published alphabet proposal, used with explicit lossless fallback. [Greshko](https://doi.org/10.1080/01611194.2025.2566408) supplies the published Naibbe encoder/inventory and known-boundary positive controls. [Lindemann & Bowern](https://arxiv.org/abs/2010.14697) motivate segmentation-sensitive entropy comparisons and supply the cited modern Occitan sample. [Gaskell & Bowern](https://ceur-ws.org/Vol-3313/paper4.pdf) motivate testing specificity against structured human gibberish. This experiment does not reproduce all methods or numerical results in those papers.', '',
              'No letter values, language claims or translations. Earlier phase results and gates remain unchanged. The two-table secondary was not run because the required primary gates were not reached.' if qual['status']!='PASS' else 'No letter values, language claims or translations. A separate sealed target stage is required next; the two-table secondary is still closed.', '']
    (p.HERE/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    p.dump(p.HERE/'VERIFICATION.json',dict(status='PASS',checks=['all registered input/code hashes unchanged',
           '840/840 fits present with exact cell names','bands reconstructed from saved natural metrics',
           'group splits reproduced','positive gates reconstructed','negative search-union gates reconstructed',
           'band and registration joins verified'],fits=len(actual),metric_rows=len(records),
           qualification_status=qual['status'],requested_rule_status=requested_status,
           target_access='control-only instrument; no target reader implemented',
           report_sha256=p.sha(p.HERE/'REPORT.md'),metrics_sha256=p.sha(p.HERE/'METRICS.csv'),
           output_hashes={name:p.sha(p.HERE/'results'/name) for name in sorted(actual)}))
    print(qual['status'],len(actual),'fits verified')

if __name__=='__main__': main()
