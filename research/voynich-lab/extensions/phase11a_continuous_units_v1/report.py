"""Reconstruct amended bands/gates from saved outputs; preserve Phase11."""
import csv
from collections import Counter
import run as a

def main():
    registration=a.verify(); frozen=a.read(a.HERE/'BAND.json'); regions=frozen['regions']
    q=a.read(a.HERE/'QUALIFICATION.json'); audit=a.read(a.HERE/'READ_ONLY_AUDIT.json')
    files=sorted((a.HERE/'results').glob('*.json')); assert len(files)==840
    rows=[a.read(f) for f in files]
    assert Counter(r['kind'] for r in rows)==dict(natural=300,positive=240,negative=300)
    identities={(r['kind'],r['family'],r['deck'],r['seed'],r['method']) for r in rows}; assert len(identities)==840
    assert all(r['reproduction']=='EXACT' for r in rows)
    for r in rows:
        name=f"{r['kind']}-{r['family']}-"+(str(r['deck'])+'-' if r['deck'] else '')+f"{r['seed']}-{r['method']}.json"
        assert r['prior_model_sha256']==a.p.sha(a.PRIOR/'results'/name)
    for m in a.p.METHODS:
        selected=[r for r in rows if r['kind']=='natural' and r['method']==m]
        for stage in ['pre','post']:
            b=a.joint_band([r[stage] for r in selected])
            # Ordering of the natural freeze is source-list then seed; reconstruct it.
            selected=sorted(selected,key=lambda r:(a.NATURAL.index(r['family']),r['seed']))
            b=a.joint_band([r[stage] for r in selected])
            for k,v in b.items(): assert regions[m][stage][k]==v,(m,stage,k)
    rebuilt=a.summarize([r for r in rows if r['kind']!='natural'],regions)
    for k,v in rebuilt.items(): assert q[k]==v,k
    assert q['band_sha256']==a.p.sha(a.HERE/'BAND.json')
    assert q['registration_sha256']==a.p.sha(a.HERE/'REGISTRATION.json')
    metric_rows=[]
    for r in rows:
        for stage in ['pre','post']:
            b=regions[r['method']][stage]
            metric_rows.append(dict(kind=r['kind'],family=r['family'],deck=r['deck'],seed=r['seed'],method=r['method'],stage=stage,
                **{k:r[stage][k] for k in a.KEYS},valid=r[stage]['valid'],units=r[stage]['units'],
                adjacent_pairs=r[stage]['adjacent_pairs'],source_groups=r[stage]['groups'],
                distance_squared=a.distance(r[stage],b),threshold=b['threshold'],inside=a.inside(r[stage],b),
                boundary_f1=r['boundary']['f1'] if r['boundary'] else None,
                word_length_descriptive=r['descriptive'][stage]['word_length'],
                positional_entropy_descriptive=r['descriptive'][stage]['positional_entropy'],
                selected_K=r['selected_K'],mdl_cap=r['mdl_cap']))
    with (a.HERE/'METRICS.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(metric_rows[0])); w.writeheader(); w.writerows(metric_rows)
    lines=['# Phase 11a — declared continuous-stream amendment','',f"**{q['status']}**. Voynich **{q['voynich']}**; conditional secondary **{q['secondary']}**.",'',
           'All 840 registered evaluations completed using the saved Phase11 training-selected models: 300 natural, 240 positive, 300 negative. **Zero refits.** Every replay exactly reproduced its original within-word metrics; positive boundary counts also reproduced exactly. The amended natural region was frozen before amended positive/negative evaluation. Original Phase11 scientific files remain byte-identical. This is a control-informed amendment on the same banks, not independent confirmation.','',
           '## Read-only prerequisite: merge failure, not spaces alone','',
           'Saved Phase11 T-N positive failures against the corresponding pre/post pipeline bands (80 runs each):','',
           '| Coordinate | Pre below | Pre above | Post below | Post above |','|---|---:|---:|---:|---:|']
    for k in a.p.KEYS:
        pre=audit['pipeline_band']['pre'][k]; post=audit['pipeline_band']['post'][k]
        lines.append(f"| {k} | {pre['below']} | {pre['above']} | {post['below']} | {post['above']} |")
    lines += ['','Inventory/h1/h2 fail in every saved T-N positive before and after merging, changing from too high to too low. Inventory falls from 318–345 chunks to 2–18 post-merge units. **The merge stage is the primary diagnosed problem.** Space-dependent metrics and the old marginal-coverage gate were additional limitations. This amendment changes evaluation/coverage only and deliberately leaves the failing merge stage intact.','',
              '## Joint region and binomial reference','',
              'Five continuous-stream coordinates: inventory, h1=H(U), h2=H(next U | U), h2/h1, and rank-frequency slope. Transitions ignore ciphertext spaces within each source group, without bridging separate source documents or held-out gaps. Word length and positional entropy are descriptive only. There is no literal-letter anchor. Each tokenizer/stage has one standardized Mahalanobis region with frozen .05 covariance shrinkage and empirical 95th percentile (`higher`, inclusive).','',
              '| Tokenizer | Pre self-coverage | Post self-coverage | Post cutoff d² |','|---|---:|---:|---:|']
    for m in a.p.METHODS:
        lines.append(f"| {m} | {regions[m]['pre']['self_coverage']:.0%} | {regions[m]['post']['self_coverage']:.0%} | {regions[m]['post']['threshold']:.4f} |")
    e=a.expectation(.95)
    lines += ['',f"For perfect boundary recovery and independent .95 band acceptance, X~Binomial(20,.95): **E[X]=19/20; P(X≥16)={e['probability_at_least_16']:.6%}; P(X<16)={e['probability_below_16']:.6%}.** Actual-coverage references are in BAND.json. This is a hypothetical benchmark: in-sample natural self-coverage does not establish predictive positive coverage, and fixed-source/noise replicates are dependent. Source-wise natural coverage/distances are retained in BAND.json.",'',
              '## Positive calibration','',
              'A cell requires ≥16/20 joint boundary-F1≥.8 and post-merge-region successes. All four language/deck cells must pass for a tokenizer to become eligible.','',
              '| Source | Deck | Tokenizer | Boundary passes | Post-region hits | Joint successes | Cell |',
              '|---|---:|---|---:|---:|---:|---|']
    for c in q['positive_cells']:
        lines.append(f"| {c['family']} | {c['deck']} | {c['method']} | {sum(x['f1'] is not None and x['f1']>=.8 for x in c['detail'])}/20 | {sum(x['band'] for x in c['detail'])}/20 | {c['successes']}/20 | {'PASS' if c['passed'] else 'FAIL'} |")
    lines += ['','Eligible tokenizers: '+(', '.join(q['eligible_tokenizers']) or 'none')+'.','',
              '## Negative numerical counts; interpretation is conditional','',f"Specificity status: **{q['specificity']}**.",'',
              '| Family | Any-tokenizer post-region hits | Rate | Numerical ≥20% trigger |','|---|---:|---:|---|']
    for c in q['negatives']:
        lines.append(f"| {c['family']} | {c['hits']}/20 | {c['rate']:.0%} | {'yes' if c['stop_threshold_triggered'] else 'no'} |")
    if not q['calibration_pass']:
        lines += ['','These are raw diagnostic counts, **not interpretable specificity success or failure**, because positive calibration failed. Preserve every numerical STOP trigger; none authorizes target scoring.']
    lines += ['','## Limits and deliverables','',
              'The old training-only MDL tokenizer/merge rules, source sizes, 20 seeds, noise channel, positive boundary truth, four Naibbe source/deck cells and five negative families are unchanged. The T-MDL 64-merge path remains a bounded search. Naibbe/Zattera inventories are non-blind; modern Occitan, OCR, genre, smaller C13/C17, manuscript-dependent negatives and reused control outcomes limit interpretation. The context merge was not retrained on continuous contexts. Joint-region self-coverage is in-sample; it is not an unseen-text false-positive guarantee.','',
              'See METRICS.csv for all five coordinates pre/post and descriptive word/position measures, READ_ONLY_AUDIT.json for the initial saved-data diagnosis, BAND.json for all frozen natural vectors/regions, QUALIFICATION.json for all control cells, and VERIFICATION.json for preservation and gate reconstruction. Original citations and licenses remain in [Phase11 SOURCES](../phase11_plaintext_units_v1/SOURCES.md), including Zattera, Greshko, Lindemann & Bowern and Gaskell & Bowern.','',
              'No letter values, language claims, translation, manuscript A/B scoring, or two-table secondary scoring. The failed control instrument does not answer whether another segmentation of Voynich could work. No automatic merge repair or further sweep was run.','']
    (a.HERE/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    a.verify()
    dumpdata=dict(status='PASS',checks=['Phase11 scientific artifact set and every hash unchanged',
             'all840 model replays exact against old within-word metrics','all240 positive boundary receipts exact',
             'six joint regions reconstructed with natural self-coverage >=95%',
             'positive and negative gates reconstructed','band/registration hashes verified'],
             evaluations=840,refits=0,metric_rows=1680,qualification_status=q['status'],specificity=q['specificity'],
             prior_scientific_files=len(registration['phase11']),
             output_hashes={str(f.relative_to(a.HERE)):a.p.sha(f) for f in files},
             report_sha256=a.p.sha(a.HERE/'REPORT.md'),metrics_sha256=a.p.sha(a.HERE/'METRICS.csv'),
             band_sha256=a.p.sha(a.HERE/'BAND.json'),qualification_sha256=a.p.sha(a.HERE/'QUALIFICATION.json'))
    a.dump(a.HERE/'VERIFICATION.json',dumpdata)
    print(q['status'],q['specificity'],'840 replays verified')

if __name__=='__main__': main()
