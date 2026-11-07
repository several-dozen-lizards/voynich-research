"""Exploratory descriptive leave-one-ending-family-out influence audit."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
from datetime import datetime,timezone
import csv,json,hashlib

R=Path(__file__).resolve().parent
S=R.parent/'exploratory-six-folio-descriptive'
FAMILIES=['eey','edy','ey','y','other']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def summarize(rows):
    numerator=Fraction(0);denominator=Fraction(0);matched=0;pages=set()
    for r in rows:
        sh,ch,a,b=[int(r[k]) for k in ['sh','ch','sh_qok','ch_qok']]
        if not sh or not ch:continue
        numerator+=Fraction(a*ch-b*sh,sh+ch);denominator+=Fraction(sh*ch,sh+ch)
        matched+=1;pages.add(r['folio'])
    gap=100*numerator/denominator if denominator else None
    return dict(effect_points=float(gap) if gap is not None else None,exact_effect_points=str(gap) if gap is not None else None,
        weighted_numerator=float(numerator),V=float(denominator),matched_strata=matched,comparison_pages=len(pages),
        eligible_sh=sum(int(r['sh']) for r in rows),eligible_ch=sum(int(r['ch']) for r in rows),
        direction='higher after sh' if gap is not None and gap>0 else 'higher after ch' if gap is not None and gap<0 else 'equal' if gap is not None else 'no matched comparison')

def independent(rows):
    groups=defaultdict(lambda:[0,0,0,0])
    for r in rows:
        if r['exclusion_reason']:continue
        # Recompute the ending from the literal origin, independently of stored family.
        fam=next((s for s in FAMILIES[:-1] if r['origin'].endswith(s)),'other')
        assert fam==r['family']
        j=0 if r['origin'].startswith('sh') else 1
        z=groups[r['folio'],fam];z[j]+=1;z[2+j]+=int(r['outcome'])
    numerator=Fraction(0);denominator=Fraction(0)
    for sh,ch,a,b in groups.values():
        if not sh or not ch:continue
        w=1/(Fraction(1,sh)+Fraction(1,ch));numerator+=w*(Fraction(a,sh)-Fraction(b,ch));denominator+=w
    return 100*numerator/denominator if denominator else None

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve earlier analysis.'
    hashes=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['STRATA.csv','EVENTS.csv','DESCRIPTIVE.json','PROTOCOL.json']:assert sha(S/n)==hashes[n]
    prior=json.loads((S/'DESCRIPTIVE.json').read_text());folios=[r['folio'] for r in prior['H']['per_folio']]
    assert len(folios)==6 and folios==[r['folio'] for r in prior['F']['per_folio']]
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,families=FAMILIES,
        plan='For H and F separately, omit all events in each one of the five frozen ending families across the same six physical folios. Recompute the original within-folio x ending-family Mantel-Haenszel risk difference from remaining strata.',
        family_rule='Original longest-first suffix eey,edy,ey,y; otherwise other. Omit whole existing family. Never reclassify an omitted ending into a shorter suffix.',
        estimand='Percentage-point sh-minus-ch next-qok rate difference: 100*sum[w*(a/ns-b/nc)]/sum(w), w=ns*nc/(ns+nc). Unsupported strata contribute zero weight. Ratio recomputed after omission, not an equal-family average.',
        report='Full baseline, each remaining effect, change from baseline, omitted comparison support/share, and the descriptive effect within each omitted family itself. No p-values, intervals, power or inferential decision. Retain every family, including other and zero-comparison-weight families.',
        exposure='Post-outcome exploratory sensitivity of a subset already included in scored attempt C. H/F are not pooled or treated as independent replications.',
        hashes={str(p):sha(p) for p in [Path(__file__),S/'STRATA.csv',S/'EVENTS.csv',S/'DESCRIPTIVE.json',S/'PROTOCOL.json']}))
    strata=list(csv.DictReader((S/'STRATA.csv').open(encoding='utf-8',newline='')))
    events=list(csv.DictReader((S/'EVENTS.csv').open(encoding='utf-8',newline='')))
    results={};checks=0
    for tr in ['H','F']:
        rows=[r for r in strata if r['reading']==tr];raw=[r for r in events if r['cell']=='P1-'+tr]
        assert all(r['folio'] in folios and r['family'] in FAMILIES for r in rows)
        baseline=summarize(rows)
        assert baseline['exact_effect_points']==prior[tr]['aggregate']['exact_effect_points']
        assert baseline['exact_effect_points']==str(independent(raw));checks+=1
        omissions=[]
        for fam in FAMILIES:
            left=summarize([r for r in rows if r['family']!=fam]);removed=summarize([r for r in rows if r['family']==fam])
            for result,kept in [(left,[r for r in raw if r['family']!=fam]),(removed,[r for r in raw if r['family']==fam])]:
                value=independent(kept)
                assert result['exact_effect_points']==(str(value) if value is not None else None);checks+=1
            left.update(omitted_family=fam,change_points=left['effect_points']-baseline['effect_points'] if left['effect_points'] is not None else None,
                omitted_V=removed['V'],omitted_V_share=removed['V']/baseline['V'],omitted_family_effect_points=removed['effect_points'],omitted_family_matched_strata=removed['matched_strata'],omitted_family_sh=removed['eligible_sh'],omitted_family_ch=removed['eligible_ch'])
            omissions.append(left)
        available=[r for r in omissions if r['effect_points'] is not None];low=min(available,key=lambda r:r['effect_points']);high=max(available,key=lambda r:r['effect_points'])
        results[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,
            range_points=[low['effect_points'],high['effect_points']],greatest_attenuation_omitted_family=low['omitted_family'],largest_remaining_effect_omitted_family=high['omitted_family'],
            every_single_family_omission_remains_positive=all(r['direction']=='higher after sh' for r in omissions))
    save('DESCRIPTIVE-ENDING-LOO.json',results)
    with (R/'OMISSIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rr=[dict(reading=tr,**v) for tr,r in results.items() for v in r['omissions']];w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_comparisons=checks,source_strata_and_event_recounts_agree=True,ending_families_recomputed_from_origins=True,baselines_reproduced=True,inferential_calculations_performed=False))
    def fmt(v):return 'unavailable' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — six-folio leave-one-ending-family-out description\n\n'
    text+='Each effect is a percentage-point difference in matched next-qok rates after sh minus ch. The original folio x ending-family strata and harmonic-exposure weights are retained; removing one family recomputes the ratio over all remaining families and the same six folios. H/F remain separate.\n\n'
    text+=f"Full subset: H {fmt(results['H']['baseline']['effect_points'])}; F {fmt(results['F']['baseline']['effect_points'])}.\n\n"
    text+='| Omitted family | H remaining effect | H change | F remaining effect | F change |\n|---|---:|---:|---:|---:|\n'
    for h,f in zip(results['H']['omissions'],results['F']['omissions']):text+=f"| {h['omitted_family']} | {fmt(h['effect_points'])} | {fmt(h['change_points'])} | {fmt(f['effect_points'])} | {fmt(f['change_points'])} |\n"
    text+='\n| Family considered alone | H effect | H comparison-weight share | F effect | F comparison-weight share |\n|---|---:|---:|---:|---:|\n'
    for h,f in zip(results['H']['omissions'],results['F']['omissions']):text+=f"| {h['omitted_family']} | {fmt(h['omitted_family_effect_points'])} | {h['omitted_V_share']*100:.2f}% | {fmt(f['omitted_family_effect_points'])} | {f['omitted_V_share']*100:.2f}% |\n"
    text+='\n'
    for tr,r in results.items():
        text+=f"{tr}: remaining effects range from {fmt(r['range_points'][0])} to {fmt(r['range_points'][1])} points. The smallest remaining effect follows omission of {r['greatest_attenuation_omitted_family']}. "
        text+='Every single-family omission retains a positive descriptive effect.\n\n' if r['every_single_family_omission_remains_positive'] else 'At least one omission does not retain a positive descriptive effect; see every row above.\n\n'
    text+='A family’s influence depends on both its effect and its comparison weight. This check addresses dependence of the observed sign on a single family; it does not establish statistical robustness, equivalence across families, or a grammar/spelling mechanism. Unsupported comparisons are unavailable, not zero. The other family is retained as defined, and omitted families never fall back into shorter-suffix groups.\n\n'
    text+='This is post-outcome exploratory description on a subset already scored within attempt C. No p-values, confidence intervals, inferential claims, new support gates or model fitting are involved. Earlier files remain unchanged.\n\n'
    text+='Verification independently regrouped the saved event ledger, checked longest-first endings against literal origins, and reproduced all 22 full-subset/remaining/removed-family effects using exact rational arithmetic.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
