"""Exploratory descriptive union deletion of one folio and one ending family."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv,json,hashlib,importlib.util

R=Path(__file__).resolve().parent
S=R.parent/'exploratory-six-folio-descriptive'
A=R.parent/'exploratory-six-folio-ending-loo'
FAMILIES=['eey','edy','ey','y','other']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve prior analysis.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for name in ['STRATA.csv','EVENTS.csv','DESCRIPTIVE.json','PROTOCOL.json']:assert sha(S/name)==manifest[name]
    helper=A/'describe_ending_loo.py'
    assert sha(helper)==json.loads((A/'MANIFEST.json').read_text())['hashes'][helper.name]
    spec=importlib.util.spec_from_file_location('verified_descriptive_arithmetic',helper);arithmetic=importlib.util.module_from_spec(spec);spec.loader.exec_module(arithmetic)
    previous=json.loads((S/'DESCRIPTIVE.json').read_text());folios=[r['folio'] for r in previous['H']['per_folio']]
    assert len(folios)==6 and folios==[r['folio'] for r in previous['F']['per_folio']]
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,ending_families=FAMILIES,
        plan='Complete 6x5 Cartesian grid, 30 joint omissions per reading. Remove every event on the named physical folio OR belonging to the named ending family; retain only folio!=omitted_folio AND family!=omitted_family. This is union deletion, not deletion of only their intersection. Retain all other physical pages and ending families.',
        estimand='Same harmonic-exposure weighted Mantel-Haenszel next-qok risk difference: 100*sum_s[w_s*(a/ns-b/nc)]/sum_s(w_s), within physical folio x ending family, w=ns*nc/(ns+nc). Recompute numerator and denominator after each union deletion. Unsupported strata weight0. Original longest-first families eey,edy,ey,y,other remain fixed; no suffix fallback.',
        report='H/F separate; all 60 descriptive effects, shifts from each six-folio baseline, remaining support/origin counts, direction, and complete matrices. No p-values, intervals, inferential decisions, model selection, new gates or qualification.',
        limitations='Post-outcome exploratory influence description of an already scored subset. Joint omissions overlap heavily; they are not independent samples, and their range is not an uncertainty interval. Named physical folios are the same units used throughout attempt C.',
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
        for pg in folios:
            for fam in FAMILIES:
                left=[r for r in rows if r['folio']!=pg and r['family']!=fam]
                r=arithmetic.summarize(left)
                independently=arithmetic.independent([v for v in raw if v['folio']!=pg and v['family']!=fam])
                assert r['exact_effect_points']==(str(independently) if independently is not None else None);checks+=1
                r.update(omitted_folio=pg,omitted_family=fam,change_points=r['effect_points']-baseline['effect_points'] if r['effect_points'] is not None else None,
                    removed_V=baseline['V']-r['V'],removed_V_share=(baseline['V']-r['V'])/baseline['V'])
                omissions.append(r)
        assert len(omissions)==30 and len({(r['omitted_folio'],r['omitted_family']) for r in omissions})==30
        available=[r for r in omissions if r['effect_points'] is not None];low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,
            direction_counts=dict(Counter(r['direction'] for r in omissions)),range_points=[low['effect_points'],high['effect_points']],
            minimum=dict(omitted_folio=low['omitted_folio'],omitted_family=low['omitted_family'],effect_points=low['effect_points'],change_points=low['change_points'],V=low['V'],comparison_pages=low['comparison_pages'],matched_strata=low['matched_strata']),
            maximum=dict(omitted_folio=high['omitted_folio'],omitted_family=high['omitted_family'],effect_points=high['effect_points'],change_points=high['change_points'],V=high['V']),
            remaining_V_range=[min(r['V'] for r in omissions),max(r['V'] for r in omissions)])
    save('DESCRIPTIVE-JOINT-LOO.json',results)
    with (R/'JOINT-OMISSIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rows=[dict(reading=tr,**v) for tr,r in results.items() for v in r['omissions']]
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_effect_checks=checks,all_60_joint_omissions_retained=True,baselines_reproduced=True,arithmetic='Stratum-count ratio compared with independent regrouping and fractional rate differences from saved event ledger.',union_deletion_used=True,no_inferential_calculations=True))
    def fmt(v):return 'unavailable' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — joint leave-one-folio-and-one-ending-family-out description\n\n'
    text+='For each combination, delete all events on the named folio and all events in the named ending family across the remaining folios. Recompute the original within-folio x ending-family Mantel-Haenszel weighted next-qok difference, sh minus ch, in percentage points. H/F remain separate. The omitted family is not reassigned to a shorter suffix.\n\n'
    text+=f"Full six-folio baseline: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    for tr,r in results.items():
        text+=f'## {tr} reading\n\nRows identify the omitted folio; columns identify the omitted ending family.\n\n'
        text+='| Omitted folio | '+' | '.join(FAMILIES)+' |\n|---|'+ '|'.join(['---:']*len(FAMILIES))+'|\n'
        lookup={(v['omitted_folio'],v['omitted_family']):v for v in r['omissions']}
        for pg in folios:text+='| '+pg+' | '+' | '.join(fmt(lookup[pg,fam]['effect_points']) for fam in FAMILIES)+' |\n'
        text+='\nDescriptive directions: '+', '.join(f'{n} {d}' for d,n in r['direction_counts'].items())+'.\n\n'
        low,high=r['minimum'],r['maximum']
        text+=f"Smallest remaining effect: {fmt(low['effect_points'])} points after jointly omitting {low['omitted_folio']} and {low['omitted_family']} (change {fmt(low['change_points'])} from baseline). Remaining comparison weight V={low['V']:.3f}, {low['comparison_pages']} contributing pages, {low['matched_strata']} matched strata.\n\n"
        text+=f"Largest remaining effect: {fmt(high['effect_points'])} points after jointly omitting {high['omitted_folio']} and {high['omitted_family']}. Across all combinations remaining comparison weight ranges {r['remaining_V_range'][0]:.3f} to {r['remaining_V_range'][1]:.3f}.\n\n"
    text+='## Interpretation and verification\n\n'
    if all(r['direction_counts'].get('higher after sh',0)==30 for r in results.values()):text+='The descriptive positive sign remains in all 30 joint omissions in each reading. No tested one-folio/one-family union is necessary for that sign. Contributions are unequal, and this does not establish statistical robustness or show that the effect is broadly distributed.\n\n'
    else:text+='Directions vary across the complete grid; all combinations, including unavailable or nonpositive comparisons, are retained.\n\n'
    text+='F f85r2 and f86v3 carry no matched comparison weight. Their omissions therefore reproduce the corresponding ending-only omission, so nominal grid rows are not independent evidence. Other combinations also share most events.\n\n'
    text+='This is post-outcome exploratory description of the already scored six-folio subset. No p-values, confidence intervals, power calculations, significance claims, revised support gates or model fitting are involved. The grid range describes influence, not sampling uncertainty.\n\n'
    text+='Independent exact-rational calculations from the event ledger reproduced all 60 joint effects and both full-subset baselines (62 checks). Prior frozen data and reports remain unchanged. Full support weights, retained origin counts and changes are in JOINT-OMISSIONS.csv and DESCRIPTIVE-JOINT-LOO.json.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:{k:r[k] for k in ['direction_counts','range_points','minimum','maximum','remaining_V_range']} for tr,r in results.items()},indent=2))

if __name__=='__main__':main()
