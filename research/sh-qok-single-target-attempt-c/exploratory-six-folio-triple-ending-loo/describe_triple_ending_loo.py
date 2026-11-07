"""Exploratory all100 omitted-triple x omitted-family combinations per reading."""
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
    assert not (R/'PROTOCOL.json').exists(), 'Preserve previous output.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['STRATA.csv','EVENTS.csv','DESCRIPTIVE.json','PROTOCOL.json']:assert sha(S/n)==manifest[n]
    helper=A/'describe_ending_loo.py'
    assert sha(helper)==json.loads((A/'MANIFEST.json').read_text())['hashes'][helper.name]
    spec=importlib.util.spec_from_file_location('descriptive_arithmetic',helper);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    prior=json.loads((S/'DESCRIPTIVE.json').read_text());folios=[r['folio'] for r in prior['H']['per_folio']]
    assert len(folios)==6 and folios==[r['folio'] for r in prior['F']['per_folio']]
    triples=list(combinations(folios,3));jobs=list(product(triples,FAMILIES));assert len(triples)==20 and len(jobs)==100
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,omitted_triples=triples,ending_families=FAMILIES,
        plan='All20 unordered triples x5 ending families per reading. Remove all events on any of the three named physical folios OR belonging to the named family across remaining folios. Retain only folio outside omitted triple AND family not omitted. No data-selected pruning; no suffix reclassification.',
        estimand='Original within-folio x ending-family MH next-qok risk difference, percentage points sh minus ch:100*sum[w*(a/ns-b/nc)]/sum(w), w=ns*nc/(ns+nc). Recompute numerator and denominator after union deletion. Unsupported strata weight0. Zero denominator=>unavailable, never zero effect. Endings remain longest-first eey,edy,ey,y,other.',
        report='Keep every one of200 combinations, including negative, equal and unavailable descriptions. Record effects and shifts from each full baseline, counts, weights, matched strata, retained/contributing folios and extremes/ties. H/F separate; no p-values, intervals, power, inferential decisions, new qualification, revised gates or fitting.',
        limits='Post-outcome exploratory influence description on a subset already scored in attempt C. Shared observations make grid cells dependent. Effect range is not an uncertainty interval and sign counts are not independent evidence.',
        hashes={str(p):sha(p) for p in [Path(__file__),helper,S/'STRATA.csv',S/'EVENTS.csv',S/'DESCRIPTIVE.json',S/'PROTOCOL.json']}))
    strata=list(csv.DictReader((S/'STRATA.csv').open(encoding='utf-8',newline='')))
    events=list(csv.DictReader((S/'EVENTS.csv').open(encoding='utf-8',newline='')))
    results={};checks=0
    for tr in ['H','F']:
        rows=[r for r in strata if r['reading']==tr];raw=[r for r in events if r['cell']=='P1-'+tr]
        baseline=a.summarize(rows)
        assert baseline['exact_effect_points']==prior[tr]['aggregate']['exact_effect_points']
        assert baseline['exact_effect_points']==str(a.independent(raw));checks+=1
        omissions=[]
        for triple,fam in jobs:
            kept=[r for r in rows if r['folio'] not in triple and r['family']!=fam]
            r=a.summarize(kept)
            independently=a.independent([v for v in raw if v['folio'] not in triple and v['family']!=fam])
            assert r['exact_effect_points']==(str(independently) if independently is not None else None);checks+=1
            r.update(omitted_folios=list(triple),omitted_family=fam,retained_folios=[pg for pg in folios if pg not in triple],
                contributing_folios=sorted({v['folio'] for v in kept if int(v['sh'])>0 and int(v['ch'])>0}),
                change_points=r['effect_points']-baseline['effect_points'] if r['effect_points'] is not None else None,
                removed_V=baseline['V']-r['V'],removed_V_share=(baseline['V']-r['V'])/baseline['V'])
            omissions.append(r)
        assert len(omissions)==100 and len({(tuple(r['omitted_folios']),r['omitted_family']) for r in omissions})==100
        available=[r for r in omissions if r['effect_points'] is not None]
        low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        def receipt(r):return {k:r[k] for k in ['omitted_folios','omitted_family','retained_folios','contributing_folios','effect_points','exact_effect_points','change_points','V','comparison_pages','matched_strata','eligible_sh','eligible_ch','direction']}
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,direction_counts=dict(Counter(r['direction'] for r in omissions)),
            range_points=[low['effect_points'],high['effect_points']],minimum=receipt(low),maximum=receipt(high),
            minimum_ties=[receipt(r) for r in available if r['exact_effect_points']==low['exact_effect_points']],maximum_ties=[receipt(r) for r in available if r['exact_effect_points']==high['exact_effect_points']],
            nonpositive_or_unavailable=[receipt(r) for r in omissions if r['direction']!='higher after sh'],
            remaining_V_range=[min(r['V'] for r in omissions),max(r['V'] for r in omissions)],comparison_page_range=[min(r['comparison_pages'] for r in omissions),max(r['comparison_pages'] for r in omissions)])
    save('DESCRIPTIVE-TRIPLE-ENDING-LOO.json',results)
    with (R/'COMBINATIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rr=[dict(reading=tr,**{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()}) for tr,res in results.items() for r in res['omissions']]
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_comparisons=checks,all100_combinations_per_reading=True,baselines_reproduced=True,source_strata_and_separate_event_regrouping_agree=True,union_deletion_used=True,zero_weight_unavailable_preserved=True,inferential_calculations_performed=False))
    def fmt(v):return 'unavailable' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — joint leave-three-folios-and-one-ending-family-out description\n\n'
    text+='Each combination deletes all three named physical folios, plus the named ending family on the remaining folios. Effects are percentage-point sh-minus-ch next-qok differences using the original within-folio x ending-family harmonic-exposure weights. The complete20x5 grid is reported separately for each reading, with no suffix fallback or discarded cases.\n\n'
    text+=f"Full six-folio baseline: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    for tr,res in results.items():
        text+=f'## {tr} reading\n\nRows name omitted triples; columns name omitted ending families.\n\n'
        text+='| Omitted folio triple | '+' | '.join(FAMILIES)+' |\n|---|'+ '|'.join(['---:']*5)+'|\n'
        lookup={(tuple(r['omitted_folios']),r['omitted_family']):r for r in res['omissions']}
        for triple in triples:text+='| '+' + '.join(triple)+' | '+' | '.join(fmt(lookup[triple,f]['effect_points']) for f in FAMILIES)+' |\n'
        text+='\nDirections: '+', '.join(f'{n} {d}' for d,n in res['direction_counts'].items())+'.\n\n'
        low,high=res['minimum'],res['maximum']
        text+=f"Smallest defined effect {fmt(low['effect_points'])} after omitting "+' + '.join(low['omitted_folios'])+f" and {low['omitted_family']}; change {fmt(low['change_points'])}; V={low['V']:.3f}, {low['comparison_pages']} contributing pages, {low['matched_strata']} matched strata.\n\n"
        text+=f"Largest defined effect {fmt(high['effect_points'])} after omitting "+' + '.join(high['omitted_folios'])+f" and {high['omitted_family']}. All extreme ties remain in JSON. Range excludes unavailable ratios.\n\n"
    text+='## All nonpositive or unavailable cases\n\n| Reading | Omitted triple | Omitted family | Effect | V | Contributing pages |\n|---|---|---|---:|---:|---:|\n'
    for tr,res in results.items():
        for r in res['nonpositive_or_unavailable']:text+='| '+tr+' | '+' + '.join(r['omitted_folios'])+f" | {r['omitted_family']} | {fmt(r['effect_points'])} | {r['V']:.3f} | {r['comparison_pages']} |\n"
    text+='\nZero is an exact equality of observed weighted rates; unavailable means no remaining matched comparison weight and is not treated as zero. F f85r2 and f86v3 have zero matched weight before any ending omission. Some retained triples therefore have only one contributing page, and deleting its sole matched family can remove all comparison support. Exact contributing pages and retained counts are recorded per cell.\n\n'
    text+='This is post-outcome exploratory influence description on an already scored subset. The grid cells share observations, so counts of positive/negative/tied cells are not independent evidence. Extremes and ranges describe these particular deletions, not uncertainty or a statistical robustness claim. No p-values, confidence intervals, power calculations, inferential decisions, new support gates or fitting were used. Previous files remain unchanged.\n\n'
    text+='Independent exact-rational event regrouping reproduced all200 joint effects/undefined ratios and both baselines (202 checks). All cases, count/weight details, directions and extreme ties are preserved in DESCRIPTIVE-TRIPLE-ENDING-LOO.json and COMBINATIONS.csv.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:{k:r[k] for k in ['direction_counts','range_points','minimum','maximum','nonpositive_or_unavailable']} for tr,r in results.items()},indent=2))

if __name__=='__main__':main()
