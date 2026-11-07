"""Exploratory descriptive leave-four-folios-out; all15 unordered quartets."""
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
    assert not (R/'PROTOCOL.json').exists(), 'Preserve existing output.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['STRATA.csv','EVENTS.csv','DESCRIPTIVE.json','PROTOCOL.json']:assert sha(S/n)==manifest[n]
    helper=A/'describe_ending_loo.py'
    assert sha(helper)==json.loads((A/'MANIFEST.json').read_text())['hashes'][helper.name]
    spec=importlib.util.spec_from_file_location('descriptive_arithmetic',helper);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    previous=json.loads((S/'DESCRIPTIVE.json').read_text());folios=[r['folio'] for r in previous['H']['per_folio']]
    assert len(folios)==6 and folios==[r['folio'] for r in previous['F']['per_folio']]
    quartets=list(combinations(folios,4));assert len(quartets)==15
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,omitted_quartets=quartets,
        plan='All15 unordered omitted quartets. Remove all events on the four named physical folios, retaining the complementary two and every original ending family. H/F separate. No pruning of negative, tied or unavailable cases.',
        estimand='Original within-folio x ending-family Mantel-Haenszel next-qok difference in percentage points, sh minus ch:100*sum[w*(a/ns-b/nc)]/sum(w),w=ns*nc/(ns+nc). Ratio recomputed after deletion. Single-prefix strata comparison weight0; zero total weight means unavailable, never a zero effect. Longest-first eey,edy,ey,y,other families unchanged.',
        reporting='Record every effect, baseline shift, direction, comparison weight, matched strata, retained/contributing physical folios and remaining origin counts. No p-values, confidence intervals, power, inferential decisions, new gates, fitting or qualification.',
        limits='Post-outcome exploratory sensitivity of an already scored subset. Two retained nominal folios can yield only one contributing folio or no matched support. Overlapping deletions are not independent evidence; range is not an uncertainty interval.',
        hashes={str(p):sha(p) for p in [Path(__file__),helper,S/'STRATA.csv',S/'EVENTS.csv',S/'DESCRIPTIVE.json',S/'PROTOCOL.json']}))
    strata=list(csv.DictReader((S/'STRATA.csv').open(encoding='utf-8',newline='')))
    events=list(csv.DictReader((S/'EVENTS.csv').open(encoding='utf-8',newline='')))
    results={};checks=0
    for tr in ['H','F']:
        rows=[r for r in strata if r['reading']==tr];raw=[r for r in events if r['cell']=='P1-'+tr]
        baseline=a.summarize(rows)
        assert baseline['exact_effect_points']==previous[tr]['aggregate']['exact_effect_points']
        assert baseline['exact_effect_points']==str(a.independent(raw));checks+=1
        omissions=[]
        for quartet in quartets:
            kept=[r for r in rows if r['folio'] not in quartet];r=a.summarize(kept)
            value=a.independent([v for v in raw if v['folio'] not in quartet])
            assert r['exact_effect_points']==(str(value) if value is not None else None);checks+=1
            r.update(omitted_folios=list(quartet),retained_folios=[pg for pg in folios if pg not in quartet],
                contributing_folios=sorted({v['folio'] for v in kept if int(v['sh'])>0 and int(v['ch'])>0}),
                change_points=r['effect_points']-baseline['effect_points'] if r['effect_points'] is not None else None,
                removed_V=baseline['V']-r['V'],removed_V_share=(baseline['V']-r['V'])/baseline['V'])
            omissions.append(r)
        assert len(omissions)==15 and len({tuple(r['omitted_folios']) for r in omissions})==15
        available=[r for r in omissions if r['effect_points'] is not None]
        low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        def receipt(r):return {k:r[k] for k in ['omitted_folios','retained_folios','contributing_folios','effect_points','exact_effect_points','change_points','V','comparison_pages','matched_strata','eligible_sh','eligible_ch','direction']}
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,
            direction_counts=dict(Counter(r['direction'] for r in omissions)),range_points=[low['effect_points'],high['effect_points']],minimum=receipt(low),maximum=receipt(high),
            minimum_ties=[receipt(r) for r in available if r['exact_effect_points']==low['exact_effect_points']],maximum_ties=[receipt(r) for r in available if r['exact_effect_points']==high['exact_effect_points']],
            nonpositive_or_unavailable=[receipt(r) for r in omissions if r['direction']!='higher after sh'],remaining_V_range=[min(r['V'] for r in omissions),max(r['V'] for r in omissions)])
    save('DESCRIPTIVE-QUARTET-LOO.json',results)
    with (R/'QUARTET-OMISSIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rr=[dict(reading=tr,**{k:(';'.join(v) if isinstance(v,list) else v) for k,v in row.items()}) for tr,res in results.items() for row in res['omissions']]
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_comparisons=checks,all15_quartets_per_reading=True,baselines_reproduced=True,stratum_counts_and_independent_event_regrouping_agree=True,nonpositive_and_undefined_cases_retained=True,inferential_calculations_performed=False))
    def fmt(v):return 'unavailable' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — descriptive leave-four-folios-out, all15 quartets\n\n'
    text+='Each row omits four complete physical folios and retains the complementary pair with all original ending families. Effects are percentage-point sh-minus-ch differences in next-qok rates using the original within-folio x ending-family harmonic-exposure weights. The ratio is recomputed for each retained pair. H/F remain separate.\n\n'
    text+=f"Full six-folio baseline: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    text+='| Omitted quartet | Retained pair | H effect | H contributing pages | F effect | F contributing pages |\n|---|---|---:|---:|---:|---:|\n'
    for h,f in zip(results['H']['omissions'],results['F']['omissions']):text+='| '+' + '.join(h['omitted_folios'])+' | '+' + '.join(h['retained_folios'])+f" | {fmt(h['effect_points'])} | {h['comparison_pages']} | {fmt(f['effect_points'])} | {f['comparison_pages']} |\n"
    text+='\n'
    for tr,res in results.items():
        text+=tr+': '+', '.join(f'{n} {direction}' for direction,n in res['direction_counts'].items())+f". Defined range {fmt(res['range_points'][0])} to {fmt(res['range_points'][1])} points.\n\n"
        low,high=res['minimum'],res['maximum']
        text+='Smallest defined effect retains '+' + '.join(low['retained_folios'])+f": {fmt(low['effect_points'])}; V={low['V']:.3f}, {low['comparison_pages']} contributing pages and {low['matched_strata']} matched strata.\n\n"
        text+='Largest defined effect retains '+' + '.join(high['retained_folios'])+f": {fmt(high['effect_points'])}. All tied extremes remain in JSON.\n\n"
    text+='## All nonpositive or unavailable descriptions\n\n| Reading | Retained pair | Effect | V | Contributing folios |\n|---|---|---:|---:|---|\n'
    for tr,res in results.items():
        for r in res['nonpositive_or_unavailable']:text+='| '+tr+' | '+' + '.join(r['retained_folios'])+f" | {fmt(r['effect_points'])} | {r['V']:.3f} | "+(', '.join(r['contributing_folios']) or 'none')+' |\n'
    text+='\nUnavailable means no matched comparison weight, not zero. A zero effect means an exact equality of weighted observed rates; a negative effect means a higher observed matched next-qok rate after ch in that retained subset. None is an inferential decision about a population effect. F f85r2 and f86v3 have no matched weight, so retaining them both cannot define a matched effect.\n\n'
    text+='This is post-outcome exploratory influence description on pages already scored in attempt C. The15 overlapping subsets are not independent evidence and their range is not a confidence interval. Counts and tiny remaining comparison weights matter; these descriptions do not establish statistical robustness or generality. No p-values, confidence intervals, power calculations, inferential decisions, new support gates or model fitting were used.\n\n'
    text+='All30 omitted-quartet effects/undefined ratios and both baselines were independently reproduced using exact-rational regrouping of the saved event ledger (32 checks). Previous analyses are unchanged. All counts, support, directions and ties are retained in DESCRIPTIVE-QUARTET-LOO.json and QUARTET-OMISSIONS.csv.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:{k:r[k] for k in ['direction_counts','range_points','minimum','maximum','nonpositive_or_unavailable']} for tr,r in results.items()},indent=2))

if __name__=='__main__':main()
