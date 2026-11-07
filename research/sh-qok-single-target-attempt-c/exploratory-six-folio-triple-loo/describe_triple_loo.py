"""Exploratory descriptive leave-three-folios-out, all20 unordered triples."""
from pathlib import Path
from datetime import datetime,timezone
from itertools import combinations
from collections import Counter
import csv,json,hashlib,importlib.util

R=Path(__file__).resolve().parent
S=R.parent/'exploratory-six-folio-descriptive'
A=R.parent/'exploratory-six-folio-ending-loo'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve existing analysis.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['STRATA.csv','EVENTS.csv','DESCRIPTIVE.json','PROTOCOL.json']:assert sha(S/n)==manifest[n]
    helper=A/'describe_ending_loo.py'
    assert sha(helper)==json.loads((A/'MANIFEST.json').read_text())['hashes'][helper.name]
    spec=importlib.util.spec_from_file_location('descriptive_arithmetic',helper);arithmetic=importlib.util.module_from_spec(spec);spec.loader.exec_module(arithmetic)
    previous=json.loads((S/'DESCRIPTIVE.json').read_text());folios=[r['folio'] for r in previous['H']['per_folio']]
    assert len(folios)==6 and folios==[r['folio'] for r in previous['F']['per_folio']]
    triples=list(combinations(folios,3));assert len(triples)==20
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,omitted_triples=triples,
        authorization='User explicitly selected Run the20 triples first after appended stop-slicing note conflicted with opening request. No v3 files are modified.',
        plan='All20 unordered triples of six exact physical folios. Delete the three whole named folios, retain the complementary three and all original ending families. Recompute the original within-folio x ending-family Mantel-Haenszel next-qok difference separately for H/F. No new pruning or data-selected exceptions.',
        estimand='Percentage points sh minus ch:100*sum[w*(a/ns-b/nc)]/sum(w), w=ns*nc/(ns+nc). Recompute ratio, not equal-page mean. Original longest-first eey,edy,ey,y,other families unchanged. Single-prefix strata comparison weight0; an undefined ratio stays unavailable, not zero.',
        report='All40 effects, changes from full six-folio baseline, directions, remaining weights/origin counts/matched strata and contributing pages. Preserve positive, zero, negative and unavailable cases. No p-values, confidence intervals, power, inferential decisions, refitting or support-gate changes.',
        limits='Post-outcome exploratory influence description on a subset already scored in attempt C. These overlapping subsets are not independent evidence; the range is not a confidence interval. H/F remain separate alternate readings.',
        hashes={str(p):sha(p) for p in [Path(__file__),helper,S/'STRATA.csv',S/'EVENTS.csv',S/'DESCRIPTIVE.json',S/'PROTOCOL.json']}))
    strata=list(csv.DictReader((S/'STRATA.csv').open(encoding='utf-8',newline='')))
    events=list(csv.DictReader((S/'EVENTS.csv').open(encoding='utf-8',newline='')))
    results={};checks=0
    for tr in ['H','F']:
        rows=[r for r in strata if r['reading']==tr];raw=[r for r in events if r['cell']=='P1-'+tr]
        baseline=arithmetic.summarize(rows)
        assert baseline['exact_effect_points']==previous[tr]['aggregate']['exact_effect_points']
        assert baseline['exact_effect_points']==str(arithmetic.independent(raw));checks+=1
        omissions=[]
        for triple in triples:
            left=arithmetic.summarize([r for r in rows if r['folio'] not in triple])
            value=arithmetic.independent([r for r in raw if r['folio'] not in triple])
            assert left['exact_effect_points']==(str(value) if value is not None else None);checks+=1
            left.update(omitted_folios=list(triple),retained_folios=[p for p in folios if p not in triple],
                contributing_folios=sorted({r['folio'] for r in rows if r['folio'] not in triple and int(r['sh'])>0 and int(r['ch'])>0}),
                change_points=left['effect_points']-baseline['effect_points'] if left['effect_points'] is not None else None,
                removed_V=baseline['V']-left['V'],removed_V_share=(baseline['V']-left['V'])/baseline['V'])
            omissions.append(left)
        assert len(omissions)==20 and len({tuple(r['omitted_folios']) for r in omissions})==20
        available=[r for r in omissions if r['effect_points'] is not None]
        low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        def receipt(r):return {k:r[k] for k in ['omitted_folios','retained_folios','contributing_folios','effect_points','exact_effect_points','change_points','V','comparison_pages','matched_strata','eligible_sh','eligible_ch','weighted_numerator','direction']}
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,direction_counts=dict(Counter(r['direction'] for r in omissions)),
            range_points=[low['effect_points'],high['effect_points']],minimum=receipt(low),maximum=receipt(high),
            minimum_ties=[receipt(r) for r in available if r['exact_effect_points']==low['exact_effect_points']],maximum_ties=[receipt(r) for r in available if r['exact_effect_points']==high['exact_effect_points']],
            nonpositive_or_unavailable=[receipt(r) for r in omissions if r['direction']!='higher after sh'],
            remaining_V_range=[min(r['V'] for r in omissions),max(r['V'] for r in omissions)],comparison_page_range=[min(r['comparison_pages'] for r in omissions),max(r['comparison_pages'] for r in omissions)])
    save('DESCRIPTIVE-TRIPLE-LOO.json',results)
    with (R/'TRIPLE-OMISSIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rr=[dict(reading=tr,**{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()}) for tr,res in results.items() for r in res['omissions']]
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_comparisons=checks,all20_triples_retained_per_reading=True,baselines_reproduced=True,source_strata_and_independent_event_regrouping_agree=True,no_inferential_calculations=True))
    def fmt(v):return 'unavailable' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — descriptive leave-three-folios-out, all20 triples\n\n'
    text+='Each omission removes three complete named folios; all original ending families on the complementary three folios remain. The original within-folio x ending-family harmonic-exposure weights are used to recompute the sh-minus-ch next-qok difference in percentage points. H/F remain separate.\n\n'
    text+=f"Full six-folio baseline: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    text+='| Omitted triple | H effect | H contributing pages | F effect | F contributing pages |\n|---|---:|---:|---:|---:|\n'
    for h,f in zip(results['H']['omissions'],results['F']['omissions']):text+='| '+' + '.join(h['omitted_folios'])+f" | {fmt(h['effect_points'])} | {h['comparison_pages']} | {fmt(f['effect_points'])} | {f['comparison_pages']} |\n"
    text+='\n'
    for tr,res in results.items():
        low,high=res['minimum'],res['maximum'];text+=tr+': '+', '.join(f'{n} {d}' for d,n in res['direction_counts'].items())+f". Descriptive range {fmt(res['range_points'][0])} to {fmt(res['range_points'][1])} points.\n\n"
        text+='Smallest effect follows omission of '+' + '.join(low['omitted_folios'])+f": {fmt(low['effect_points'])}, change {fmt(low['change_points'])}; V={low['V']:.3f}, {low['comparison_pages']} contributing pages and {low['matched_strata']} matched strata. Contributing folios: "+', '.join(low['contributing_folios'])+'.\n\n'
        text+='Largest effect follows omission of '+' + '.join(high['omitted_folios'])+f": {fmt(high['effect_points'])}. All tied extremes are preserved in JSON. Across all20 omissions, contributing pages range {res['comparison_page_range'][0]} to {res['comparison_page_range'][1]}.\n\n"
    text+='## Nonpositive or unavailable descriptions\n\n'
    cases=[(tr,r) for tr,res in results.items() for r in res['nonpositive_or_unavailable']]
    if cases:
        for tr,r in cases:text+=f"- {tr}, omit "+' + '.join(r['omitted_folios'])+f": {fmt(r['effect_points'])} points ({r['direction']}); retain "+', '.join(r['retained_folios'])+f". Only {r['comparison_pages']} page(s) contribute weight; contributing folios "+', '.join(r['contributing_folios'])+f"; V={r['V']:.3f}, matched strata={r['matched_strata']}.\n"
    else:text+='None; all retained descriptions have a positive sign.\n'
    text+='\nThis is post-outcome exploratory influence description on a subset already included in attempt C. The omissions overlap heavily and are not independent observations. Their numerical range is not a confidence interval. F f85r2 and f86v3 have no matched comparison weight; three retained nominal folios can leave only one contributing page. Zero effects mean an exact equality of weighted observed rates, not unavailable support and not evidence that a population dependency is absent.\n\n'
    text+='No p-values, confidence intervals, power estimates, inferential decisions, refitting or revised support gates were used. The original request to run triples first was explicitly confirmed after the appended stop-slicing note; v3 and other concurrent work were left unchanged.\n\n'
    text+='Independent exact-rational event regrouping reproduced all40 triple-omission effects and both full baselines (42 checks). Every case is retained, including zeros, unavailable results and extreme ties. See TRIPLE-OMISSIONS.csv, DESCRIPTIVE-TRIPLE-LOO.json and VERIFICATION.json.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:{k:r[k] for k in ['direction_counts','range_points','minimum','maximum','nonpositive_or_unavailable']} for tr,r in results.items()},indent=2))

if __name__=='__main__':main()
