"""Exploratory all75 pair-of-folios x ending-family union deletions per reading."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from itertools import combinations,product
import csv,json,hashlib,importlib.util

R=Path(__file__).resolve().parent
S=R.parent/'exploratory-six-folio-descriptive'
A=R.parent/'exploratory-six-folio-ending-loo'
FAMILIES=['eey','edy','ey','y','other']

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
    pairs=list(combinations(folios,2));jobs=list(product(pairs,FAMILIES));assert len(jobs)==75
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,ending_families=FAMILIES,omitted_pairs=pairs,
        plan='Complete15 unordered folio pairs x5 ending families,75 combinations per reading. Remove all events on either named physical folio OR in the named family. Retain only events whose folio is outside the pair AND whose family differs from the omitted family. Retain every remaining original stratum; no data-selected pruning.',
        estimand='Same Mantel-Haenszel next-qok risk difference in percentage points, sh minus ch:100*sum[w*(a/ns-b/nc)]/sum(w), w=ns*nc/(ns+nc), within physical folio x ending family. Recompute ratio after each union deletion. Unsupported strata weight0. Families remain longest-first eey,edy,ey,y,other; no suffix fallback.',
        report='All150 effects, shifts from full six-folio baselines, directions, remaining comparison weight, matched strata, contributing physical pages and eligible origins. Keep unavailable and nonpositive results. No p-values, intervals, inferential decisions, qualification, power calculations, model fitting or new gates.',
        limits='Exploratory post-outcome influence description on a subset already scored in attempt C. Overlapping combinations are not independent samples; their effect range is not an uncertainty interval. H/F are separate alternate readings.',
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
        for pair,fam in jobs:
            left=arithmetic.summarize([r for r in rows if r['folio'] not in pair and r['family']!=fam])
            independently=arithmetic.independent([r for r in raw if r['folio'] not in pair and r['family']!=fam])
            assert left['exact_effect_points']==(str(independently) if independently is not None else None);checks+=1
            left.update(omitted_folio_1=pair[0],omitted_folio_2=pair[1],omitted_family=fam,retained_folios=[p for p in folios if p not in pair],
                change_points=left['effect_points']-baseline['effect_points'] if left['effect_points'] is not None else None,
                removed_V=baseline['V']-left['V'],removed_V_share=(baseline['V']-left['V'])/baseline['V'])
            omissions.append(left)
        assert len(omissions)==75 and len({(r['omitted_folio_1'],r['omitted_folio_2'],r['omitted_family']) for r in omissions})==75
        available=[r for r in omissions if r['effect_points'] is not None]
        low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        def receipt(r):return {k:r[k] for k in ['omitted_folio_1','omitted_folio_2','omitted_family','effect_points','exact_effect_points','change_points','V','comparison_pages','matched_strata','eligible_sh','eligible_ch']}
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,
            direction_counts=dict(Counter(r['direction'] for r in omissions)),range_points=[low['effect_points'],high['effect_points']],minimum=receipt(low),maximum=receipt(high),
            minimum_ties=[receipt(r) for r in available if r['exact_effect_points']==low['exact_effect_points']],maximum_ties=[receipt(r) for r in available if r['exact_effect_points']==high['exact_effect_points']],
            nonpositive_or_unavailable=[receipt(r) for r in omissions if r['direction']!='higher after sh'],
            remaining_V_range=[min(r['V'] for r in omissions),max(r['V'] for r in omissions)],comparison_page_range=[min(r['comparison_pages'] for r in omissions),max(r['comparison_pages'] for r in omissions)])
    save('DESCRIPTIVE-PAIR-ENDING-LOO.json',results)
    with (R/'COMBINATIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rr=[dict(reading=tr,**{k:v for k,v in row.items() if k!='retained_folios'},retained_folios=';'.join(row['retained_folios'])) for tr,res in results.items() for row in res['omissions']]
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_comparisons=checks,all75_combinations_per_reading=True,baselines_reproduced=True,event_regrouping_and_stratum_counts_agree=True,union_deletion_used=True,inferential_calculations_performed=False))
    def fmt(v):return 'unavailable' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — joint leave-two-folios-and-one-ending-family-out description\n\n'
    text+='Every combination deletes both named physical folios in full, plus the named ending family across the remaining folios. Effects are percentage-point sh-minus-ch next-qok differences, recomputed using the original within-folio x ending-family harmonic-exposure weights. All15 unordered folio pairs and all5 original families are retained. H/F remain separate.\n\n'
    text+=f"Full six-folio baseline: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    for tr,res in results.items():
        text+=f'## {tr} reading\n\nRows name the omitted pair; columns name the omitted ending family.\n\n'
        text+='| Omitted folio pair | '+' | '.join(FAMILIES)+' |\n|---|'+ '|'.join(['---:']*5)+'|\n'
        lookup={(r['omitted_folio_1'],r['omitted_folio_2'],r['omitted_family']):r for r in res['omissions']}
        for p,q in pairs:text+=f'| {p} + {q} | '+' | '.join(fmt(lookup[p,q,f]['effect_points']) for f in FAMILIES)+' |\n'
        text+='\nDirections: '+', '.join(f'{n} {d}' for d,n in res['direction_counts'].items())+'.\n\n'
        low,high=res['minimum'],res['maximum']
        text+=f"Smallest remaining effect: {fmt(low['effect_points'])} points after omitting {low['omitted_folio_1']} + {low['omitted_folio_2']} and {low['omitted_family']} (change {fmt(low['change_points'])}). Remaining V={low['V']:.3f}, {low['comparison_pages']} comparison-contributing pages and {low['matched_strata']} matched strata.\n\n"
        text+=f"Largest remaining effect: {fmt(high['effect_points'])} points after omitting {high['omitted_folio_1']} + {high['omitted_folio_2']} and {high['omitted_family']}. All ties are preserved in the JSON.\n\n"
        text+=f"Across the complete grid, V ranges {res['remaining_V_range'][0]:.3f} to {res['remaining_V_range'][1]:.3f}; contributing pages range {res['comparison_page_range'][0]} to {res['comparison_page_range'][1]}.\n\n"
    text+='## Interpretation and verification\n\n'
    if all(r['direction_counts'].get('higher after sh',0)==75 for r in results.values()):text+='All75 joint omissions retain a positive descriptive sign in each reading. No tested two-folio/one-family union is necessary for that sign. This describes influence rather than statistical robustness or generality.\n\n'
    else:text+='At least one combination does not retain a positive descriptive sign. All directions, unavailable effects and remaining support are retained without reinterpretation; see the complete matrices and nonpositive_or_unavailable lists in the JSON.\n\n'
    text+='F f85r2 and f86v3 carry zero matched comparison weight; their nominal omissions can duplicate results from smaller omission sets. Many other grid cells share most observations. All150 combinations are overlapping descriptions, not independent evidence, and their range is not a sampling-uncertainty interval. Very small remaining comparison weights or few contributing pages can make an effect sensitive to individual observations.\n\n'
    text+='This is post-outcome exploratory analysis of a subset already included in scored attempt C. No p-values, confidence intervals, inferential decisions, revised support gates, new qualification, power calculations or model fitting were used. Omitted ending families are not reassigned to shorter suffixes. Previous analyses remain unchanged.\n\n'
    text+='Independent exact-rational event regrouping reproduced all150 omitted-combination effects and both baselines (152 checks). COMBINATIONS.csv and DESCRIPTIVE-PAIR-ENDING-LOO.json preserve all retained origin counts, support, matched strata, directions, changes and extreme ties.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:{k:r[k] for k in ['direction_counts','range_points','minimum','maximum','comparison_page_range','nonpositive_or_unavailable']} for tr,r in results.items()},indent=2))

if __name__=='__main__':main()
