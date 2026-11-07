"""Descriptive leave-two-folios-out; all 15 unordered pairs per reading."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from itertools import combinations
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
    pairs=list(combinations(folios,2));assert len(pairs)==15
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,omitted_pairs=pairs,
        plan='For each of all15 unordered pairs, remove both complete physical folios; retain the other4 declared folios and every original ending family. Recompute the same within-folio x ending-family Mantel-Haenszel risk difference separately for H and F. No data-selected exclusions.',
        estimand='Percentage points:100*sum[w*(a/ns-b/nc)]/sum(w), w=ns*nc/(ns+nc). Unsupported strata weight0. Original longest-first suffix families eey,edy,ey,y,other remain unchanged. Ratio recomputed over retained strata, not equal-page average.',
        report='Every pair, effect, shift from full baseline, remaining support, matched strata, contributing pages and origin counts. Preserve zero-weight omissions. No p-values, confidence intervals, power, inferential decisions, refitting or revised gates.',
        limits='Post-outcome exploratory influence description of an already scored subset. Pair omissions overlap and are not independent evidence. Their range is not a confidence interval. H/F remain separate alternate readings.',
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
        for pair in pairs:
            left=arithmetic.summarize([r for r in rows if r['folio'] not in pair])
            value=arithmetic.independent([r for r in raw if r['folio'] not in pair])
            assert left['exact_effect_points']==(str(value) if value is not None else None);checks+=1
            left.update(omitted_folio_1=pair[0],omitted_folio_2=pair[1],retained_folios=[p for p in folios if p not in pair],
                change_points=left['effect_points']-baseline['effect_points'] if left['effect_points'] is not None else None,
                removed_V=baseline['V']-left['V'],removed_V_share=(baseline['V']-left['V'])/baseline['V'])
            omissions.append(left)
        available=[r for r in omissions if r['effect_points'] is not None]
        low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        def receipt(r):return {k:r[k] for k in ['omitted_folio_1','omitted_folio_2','effect_points','change_points','V','comparison_pages','matched_strata','eligible_sh','eligible_ch']}
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,
            direction_counts=dict(Counter(r['direction'] for r in omissions)),range_points=[low['effect_points'],high['effect_points']],minimum=receipt(low),maximum=receipt(high),
            remaining_V_range=[min(r['V'] for r in omissions),max(r['V'] for r in omissions)],comparison_page_range=[min(r['comparison_pages'] for r in omissions),max(r['comparison_pages'] for r in omissions)])
    save('DESCRIPTIVE-PAIR-LOO.json',results)
    with (R/'PAIR-OMISSIONS.csv').open('w',encoding='utf-8',newline='') as f:
        records=[dict(reading=tr,**{k:v for k,v in r.items() if k!='retained_folios'},retained_folios=';'.join(r['retained_folios'])) for tr,res in results.items() for r in res['omissions']]
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_comparisons=checks,all15_pairs_retained_per_reading=True,baselines_reproduced=True,source_strata_and_independent_event_regrouping_agree=True,no_inferential_calculations=True))
    def fmt(x):return 'unavailable' if x is None else f'{x:+.2f}'
    text='EXPLORATORY (E) — descriptive leave-two-folios-out across all15 pairs\n\n'
    text+='Each row removes both named folios in full and retains all ending families on the other four declared folios. Effects are percentage-point sh-minus-ch differences in next-qok rates, with the original within-folio x ending-family harmonic-exposure weights. H/F remain separate.\n\n'
    text+=f"Full six-folio baseline: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    text+='| Omitted pair | H effect | H change | H contributing pages | F effect | F change | F contributing pages |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for h,f in zip(results['H']['omissions'],results['F']['omissions']):text+=f"| {h['omitted_folio_1']} + {h['omitted_folio_2']} | {fmt(h['effect_points'])} | {fmt(h['change_points'])} | {h['comparison_pages']} | {fmt(f['effect_points'])} | {fmt(f['change_points'])} | {f['comparison_pages']} |\n"
    text+='\n'
    for tr,res in results.items():
        low,high=res['minimum'],res['maximum']
        text+=f"{tr}: "+', '.join(f'{n} {d}' for d,n in res['direction_counts'].items())+f". Remaining effect range {fmt(res['range_points'][0])} to {fmt(res['range_points'][1])} points.\n\n"
        text+=f"Smallest effect follows omission of {low['omitted_folio_1']} + {low['omitted_folio_2']}: {fmt(low['effect_points'])}, change {fmt(low['change_points'])}; V={low['V']:.3f}, {low['comparison_pages']} contributing pages and {low['matched_strata']} matched strata.\n\n"
        text+=f"Largest effect follows omission of {high['omitted_folio_1']} + {high['omitted_folio_2']}: {fmt(high['effect_points'])}. Remaining support weight ranges {res['remaining_V_range'][0]:.3f} to {res['remaining_V_range'][1]:.3f}.\n\n"
    if all(r['direction_counts'].get('higher after sh',0)==15 for r in results.values()):text+='Every tested pair omission retains a positive descriptive effect in both readings. No tested pair is necessary for the observed positive sign. This is an influence description, not a statistical robustness claim.\n\n'
    else:text+='The complete table retains all directional changes; inspect the smallest effects and their remaining support.\n\n'
    text+='F f85r2 and f86v3 have zero matched comparison weight. Removing both therefore leaves F’s baseline matched effect unchanged; removing either with a contributing page reproduces a single contributing-page omission. Four retained declared folios can therefore include only two comparison-contributing pages in F. Pair results overlap heavily and are not independent evidence.\n\n'
    text+='This is post-outcome exploratory description on pages already scored in attempt C. No p-values, confidence intervals, significance decisions, power calculations, refitting or revised support gates were used. The observed range is not a sampling-uncertainty interval.\n\n'
    text+='Independent exact-rational calculations using the saved event ledger reproduced all30 omitted-pair effects and both baselines (32 checks). Previous frozen analyses remain unchanged. Per-pair counts, weights, retained folios and directions are preserved in DESCRIPTIVE-PAIR-LOO.json and PAIR-OMISSIONS.csv.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:{k:r[k] for k in ['direction_counts','range_points','minimum','maximum','comparison_page_range']} for tr,r in results.items()},indent=2))

if __name__=='__main__':main()
