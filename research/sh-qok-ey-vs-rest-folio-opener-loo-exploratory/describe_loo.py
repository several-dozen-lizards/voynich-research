"""Exploratory per-folio omission of matched ey-vs-rest effects in C2/C3."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util

R=Path(__file__).resolve().parent;P=R.parent;S=P/'sh-qok-ey-vs-rest-folio-opener-exploratory';V=P/'sh-qok-context-map-v3'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def independent(strata):
    num=Fraction(0);den=Fraction(0)
    for r in strata:
        ne,nr,a,b=[int(r[k]) for k in ['ey_events','reference_events','ey_qok','reference_qok']]
        if ne and nr:
            num+=Fraction(a*nr-b*ne,ne+nr);den+=Fraction(ne*nr,ne+nr)
    return (str(100*num/den) if den else None),str(den)

def direction(x):
    return 'unavailable' if x is None else 'lower after ey' if Fraction(x)<0 else 'higher after ey' if Fraction(x)>0 else 'equal'

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve existing analysis.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['compare_matched.py','MATCHED-COMPARISONS.json','STRATA.csv','PROTOCOL.json']:assert sha(S/n)==manifest[n]
    previous_protocol=json.loads((S/'PROTOCOL.json').read_text());assert sha(V/'EVENTS.csv')==previous_protocol['hashes'][str(V/'EVENTS.csv')]
    spec=importlib.util.spec_from_file_location('verified_matching',S/'compare_matched.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    raw=list(csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')))
    folios={c:sorted({r['folio'] for r in raw if r['context']==c}) for c in ['C2','C3']}
    assert len(folios['C2'])==20 and len(folios['C3'])==6
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), retrospective posthoc leave-one-physical-folio-out sensitivity',utc=datetime.now(timezone.utc).isoformat(),folios=folios,
        plan='Each recorded physical folio in C2/C3 is omitted once, including folios with zero comparison weight. Same omission list across H/F and views. C2 has20 nominal omissions; C3 has6. Recompute matched ey-vs-edy/y/other effects in remaining folio x opener strata; no reference-family change.',
        estimand='Original matched ending-group contrast:100*sum_s[w_s*(qok_ey/ne-qok_ref/nr)]/sum_s(w_s),w=ne*nr/(ne+nr),s=physical folio x sh/ch opener. Reference pools edy,y,other within stratum. Eey excluded from both groups, using longest-first family labels. Also describe each opener separately without pooling H/F.',
        views='All eligible events, and unchanged v3.1 available-only events (followers opening sh/ch/cth/ckh/cph/cfh excluded). Recompute overlap after omission; zero-overlap strata weight0.',
        report='Every omission and baseline, change, exact descriptive direction, remaining weight/matched strata/contributing folios, covered/unmatched counts, excluded folio weight, and opener-specific components. Preserve ties, reversals and unavailable values; no p-values, confidence intervals, power, inferential decisions, model fits or gates.',
        limits='Post-outcome selection of C2/C3 because their matched effects were lower after ey. Omissions overlap and are not independent evidence. Their range measures influence, not uncertainty or statistical robustness. H/F are alternate readings, not replications.',
        hashes={str(p):sha(p) for p in [Path(__file__),S/'compare_matched.py',S/'MATCHED-COMPARISONS.json',S/'STRATA.csv',S/'PROTOCOL.json',V/'EVENTS.csv']}))
    parent=json.loads((S/'MATCHED-COMPARISONS.json').read_text());stored=list(csv.DictReader((S/'STRATA.csv').open(encoding='utf-8',newline='')))
    eligible=[]
    for r in raw:
        if r['context'] not in folios or r['reading'] not in ['H','F'] or r['exclusion_reason'] or r['family']=='eey':continue
        fam=next((f for f in a.FAMILIES[:-1] if r['origin'].endswith(f)),'other');assert fam==r['family']
        assert fam in ['ey','edy','y','other'] and int(r['outcome'])==int(r['follower'].startswith('qok'))
        av=not r['follower'].startswith(('sh','ch','cth','ckh','cph','cfh'));assert av==(r['available']=='True')
        eligible.append(r)
    results=[];opener_rows=[];checks=0
    for c in ['C2','C3']:
        for reading in ['H','F']:
            for view in ['all','available']:
                rows=[r for r in eligible if r['context']==c and r['reading']==reading and (view=='all' or r['available']=='True')]
                strata=[r for r in stored if (r['context'],r['reading'],r['view'])==(c,reading,view)]
                meta=dict(context=c,reading=reading,view=view,classification='EXPLORATORY (E)')
                baseline=a.match(rows);old=next(r for r in parent if (r['context'],r['reading'],r['view'])==(c,reading,view))
                assert baseline=={k:v for k,v in old.items() if k not in ['context','context_name','reading','view','exploratory','discovery','known_origin']}
                omissions=[]
                for omit in [None]+folios[c]:
                    remaining=[r for r in rows if r['folio']!=omit];kept=[r for r in strata if r['folio']!=omit]
                    result=a.match(remaining);value,weight=independent(kept)
                    assert result['exact_matched_difference_points']==value and result['exact_weight_sum']==weight;checks+=1
                    if omit is not None:
                        result.update(omitted_folio=omit,direction=direction(value),change_points=result['matched_difference_points']-baseline['matched_difference_points'] if value is not None else None,
                            removed_weight=baseline['weight_sum']-result['weight_sum'],removed_weight_share=(baseline['weight_sum']-result['weight_sum'])/baseline['weight_sum'])
                        omissions.append({k:v for k,v in result.items() if k!='strata'})
                    sum_num=Fraction(0);sum_weight=Fraction(0)
                    for opener in ['sh','ch']:
                        arm=a.match([r for r in remaining if r['prefix']==opener]);v,w=independent([r for r in kept if r['opener']==opener])
                        assert arm['exact_matched_difference_points']==v and arm['exact_weight_sum']==w;checks+=1
                        if Fraction(w):sum_num+=Fraction(v)*Fraction(w);sum_weight+=Fraction(w)
                        opener_rows.append(meta|dict(opener=opener,omitted_folio=omit,direction=direction(v))|{k:x for k,x in arm.items() if k!='strata'})
                    assert (str(sum_num/sum_weight) if sum_weight else None)==value
                available=[r for r in omissions if r['matched_difference_points'] is not None]
                low=min(available,key=lambda r:r['matched_difference_points']);high=max(available,key=lambda r:r['matched_difference_points'])
                def receipt(r):return {k:r[k] for k in ['omitted_folio','matched_difference_points','exact_matched_difference_points','change_points','weight_sum','matched_strata','contributing_folios','matched_ey_events','matched_reference_events','direction']}
                results.append(meta|dict(baseline={k:v for k,v in baseline.items() if k!='strata'},nominal_folio_count=len(folios[c]),omissions=omissions,
                    direction_counts=dict(Counter(r['direction'] for r in omissions)),range_points=[low['matched_difference_points'],high['matched_difference_points']],
                    minimum_ties=[receipt(r) for r in available if r['exact_matched_difference_points']==low['exact_matched_difference_points']],maximum_ties=[receipt(r) for r in available if r['exact_matched_difference_points']==high['exact_matched_difference_points']],
                    nonnegative_or_unavailable=[receipt(r) for r in omissions if r['direction']!='lower after ey'],zero_weight_omissions=[r['omitted_folio'] for r in omissions if r['removed_weight']==0]))
    save('LEAVE-ONE-FOLIO-OUT.json',results);save('OPENER-SPECIFIC.json',opener_rows)
    for name,rr in [('OMISSIONS.csv',[{k:r[k] for k in ['context','reading','view']}|row for r in results for row in r['omissions']]),('OPENER-SPECIFIC.csv',opener_rows)]:
        with (R/name).open('w',encoding='utf-8',newline='') as f:
            flat=[{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()} for r in rr]
            w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    def fmt(x):return 'NA' if x is None else f'{x:+.2f}'
    text='EXPLORATORY (E) — leave-one-folio-out matched ey-vs-edy/y/other in C2/C3\n\n'
    text+='Eey is excluded from both ending groups. Every omission deletes one complete physical folio and recomputes the remaining folio x opener matched MH-style rate difference, ey minus pooled edy/y/other, in percentage points. All20 C2 folios and all6 C3 folios are retained as nominal omissions even if some have zero comparison weight. H/F and both follower views remain separate.\n\n'
    text+='| Context | Reading | View | Baseline pts | Omission range pts | Direction counts | Zero-weight omissions |\n|---|---|---|---:|---|---|---|\n'
    for r in results:text+=f"| {r['context']} | {r['reading']} | {r['view']} | {fmt(r['baseline']['matched_difference_points'])} | {fmt(r['range_points'][0])} to {fmt(r['range_points'][1])} | "+', '.join(f'{n} {d}' for d,n in r['direction_counts'].items())+' | '+(', '.join(r['zero_weight_omissions']) or 'none')+' |\n'
    for c in ['C2','C3']:
        text+='\n## '+c+' complete omission table\n\n| Omitted folio | H all | H available | F all | F available |\n|---|---:|---:|---:|---:|\n'
        selected=[next(r for r in results if (r['context'],r['reading'],r['view'])==(c,tr,view)) for tr,view in [('H','all'),('H','available'),('F','all'),('F','available')]]
        for pg in folios[c]:text+='| '+pg+' | '+' | '.join(fmt(next(row for row in r['omissions'] if row['omitted_folio']==pg)['matched_difference_points']) for r in selected)+' |\n'
        text+='\n### Largest reductions in the negative magnitude\n\n'
        for r in selected:
            for extreme in r['maximum_ties']:text+=f"- {r['reading']} {r['view']}, omit {extreme['omitted_folio']}: {fmt(extreme['matched_difference_points'])} points (change {fmt(extreme['change_points'])}); weight {extreme['weight_sum']:.3f}, {extreme['matched_strata']} strata, {len(extreme['contributing_folios'])} contributing folios, matched ey/reference events {extreme['matched_ey_events']}/{extreme['matched_reference_events']}.\n"
    text+='\n## Nonnegative or unavailable omissions\n\n'
    cases=[(r,v) for r in results for v in r['nonnegative_or_unavailable']]
    if cases:
        for cell,v in cases:text+=f"- {cell['context']} {cell['reading']} {cell['view']}, omit {v['omitted_folio']}: {fmt(v['matched_difference_points'])}; {v['direction']}; remaining weight {v['weight_sum']:.3f}.\n"
    else:text+='Every single-folio omission retains a negative descriptive matched ey-minus-reference difference in both contexts, readings and views.\n'
    text+='\n## Limits and verification\n\nOnly folio x opener strata containing both ending groups contribute. Coverage/unmatched counts and exact weights are retained for every omission in JSON/CSV; zero-weight omissions leave the estimand unchanged and are not additional evidence. Opener-specific effects are preserved separately and their weighted components exactly recombine to each combined effect.\n\n'
    text+='These are post-outcome exploratory descriptions of C2/C3 selected after their negative matched differences were seen. Overlapping omissions are not independent evidence, and the observed range is not a confidence interval or statistical robustness claim. No p-values, intervals, power calculations, inferential decisions, refitting or changed gates were used. Matching controls recorded folio and opener, not every spelling or layout difference.\n\n'
    text+=f'All8 full baselines and104 omission effects were recomputed from the event ledger and independently verified from the previously saved integer stratum counts. Including opener-specific components, {checks} exact-rational comparisons agreed. Prior raw and matched analyses remain unchanged.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    for p,h in json.loads((R/'PROTOCOL.json').read_text())['hashes'].items():assert sha(p)==h
    save('VERIFICATION.json',dict(status='VERIFIED',combined_baselines=8,combined_omission_effects=104,independent_exact_rational_checks=checks,event_recompute_and_prior_integer_strata_agree=True,all_opener_components_recombine_exactly=True,all_input_hashes_unchanged=True,inferential_calculations_performed=False))
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps([{k:r[k] for k in ['context','reading','view','range_points','direction_counts','maximum_ties','nonnegative_or_unavailable']} for r in results],indent=2))

if __name__=='__main__':main()
