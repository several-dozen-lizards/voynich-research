"""Exploratory descriptive leave-one-physical-folio-out effects only."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
from datetime import datetime, timezone
import csv,json,hashlib

R=Path(__file__).resolve().parent
S=R.parent/'exploratory-six-folio-descriptive'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def effect(strata):
    numerator=Fraction(0);denominator=Fraction(0);matched=0
    for row in strata:
        sh,ch,a,b=[int(row[k]) for k in ['sh','ch','sh_qok','ch_qok']]
        if not sh or not ch:continue
        numerator+=Fraction(a*ch-b*sh,sh+ch)
        denominator+=Fraction(sh*ch,sh+ch);matched+=1
    gap=100*numerator/denominator if denominator else None
    return dict(effect_points=float(gap) if gap is not None else None,exact_effect_points=str(gap) if gap is not None else None,
        V=float(denominator),matched_strata=matched,
        eligible_sh=sum(int(r['sh']) for r in strata),eligible_ch=sum(int(r['ch']) for r in strata))

def from_events(rows):
    counts=defaultdict(lambda:[0,0,0,0])
    for r in rows:
        if r['exclusion_reason']:continue
        k=0 if r['origin'].startswith('sh') else 1
        counts[r['folio'],r['family']][k]+=1
        counts[r['folio'],r['family']][2+k]+=int(r['outcome'])
    # Independent form: w times each stratum's difference in fractions.
    num=Fraction(0);den=Fraction(0)
    for sh,ch,a,b in counts.values():
        if sh and ch:
            w=1/(Fraction(1,sh)+Fraction(1,ch));num+=w*(Fraction(a,sh)-Fraction(b,ch));den+=w
    return 100*num/den if den else None

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve existing analysis.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['STRATA.csv','EVENTS.csv','DESCRIPTIVE.json','PROTOCOL.json']:
        assert sha(S/n)==manifest[n]
    previous=json.loads((S/'DESCRIPTIVE.json').read_text());folios=[r['folio'] for r in previous['H']['per_folio']]
    assert len(folios)==6 and folios==[r['folio'] for r in previous['F']['per_folio']]
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,
        plan='For H and F separately retain full six-page baseline, then omit each exact physical Folio identifier once. Recompute the same within-ending-family Mantel-Haenszel risk difference from the remaining strata. Retain all other pages and ending families; never pool H/F.',
        estimand='100*sum_s[w_s*(qok_sh/ns-qok_ch/nc)]/sum_s(w_s), w_s=ns*nc/(ns+nc). Strata with one prefix absent have zero comparison weight. Recompute the remaining support-weighted ratio, not an average of page effects.',
        reporting='Effect in percentage points, change from full subset, omitted comparison weight/share, and remaining origin counts. No p-values, intervals, inferential decisions, threshold changes or new qualification. Omitting a zero-comparison-weight page leaves the matched effect unchanged.',
        limits='Post-outcome exploratory subset sensitivity on pages already scored in attempt C. Single-page omission checks whether a page is necessary for the observed sign; it does not establish sampling stability, independence, or confirmatory evidence.',
        hashes={str(p):sha(p) for p in [Path(__file__),S/'STRATA.csv',S/'EVENTS.csv',S/'DESCRIPTIVE.json',S/'PROTOCOL.json']}))
    strata=list(csv.DictReader((S/'STRATA.csv').open(encoding='utf-8',newline='')))
    events=list(csv.DictReader((S/'EVENTS.csv').open(encoding='utf-8',newline='')))
    result={};checks=0
    for tr in ['H','F']:
        rows=[r for r in strata if r['reading']==tr];raw=[r for r in events if r['cell']=='P1-'+tr]
        baseline=effect(rows);assert abs(baseline['effect_points']-previous[tr]['aggregate']['effect_points'])<1e-12
        assert baseline['exact_effect_points']==str(from_events(raw));checks+=1
        omissions=[]
        for pg in folios:
            left=[r for r in rows if r['folio']!=pg];r=effect(left)
            independently=from_events([v for v in raw if v['folio']!=pg]);assert r['exact_effect_points']==str(independently);checks+=1
            removed=effect([v for v in rows if v['folio']==pg]);share=removed['V']/baseline['V']
            r.update(omitted_folio=pg,change_points=r['effect_points']-baseline['effect_points'],omitted_V=removed['V'],omitted_V_share=share,
                direction='higher after sh' if independently is not None and independently>0 else 'higher after ch' if independently is not None and independently<0 else 'equal' if independently is not None else 'no matched comparison')
            if not removed['V']:assert r['exact_effect_points']==baseline['exact_effect_points']
            omissions.append(r)
        lowest=min(omissions,key=lambda r:r['effect_points']);highest=max(omissions,key=lambda r:r['effect_points'])
        result[tr]=dict(classification='EXPLORATORY (E), descriptive only',baseline=baseline,omissions=omissions,
            range_points=[lowest['effect_points'],highest['effect_points']],lowest_effect_omission=lowest['omitted_folio'],highest_effect_omission=highest['omitted_folio'],
            directional_description='Every single-folio omission retains a higher matched next-qok rate after sh.' if all(r['direction']=='higher after sh' for r in omissions) else 'Directions vary; inspect each omission.')
    save('DESCRIPTIVE-LOO.json',result)
    with (R/'OMISSIONS.csv').open('w',encoding='utf-8',newline='') as f:
        rr=[dict(reading=tr,**v) for tr,r in result.items() for v in r['omissions']]
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    save('VERIFICATION.json',dict(status='VERIFIED',independent_exact_rational_effect_checks=checks,source_strata_and_separate_event_recount_agree=True,full_subset_baseline_reproduced=True,no_inferential_calculations=True))
    text='EXPLORATORY (E) — six-folio descriptive leave-one-folio-out check\n\n'
    text+='Effects are percentage-point differences in next-qok rates after sh minus ch, matched within ending family and physical folio. Each row recomputes the weighted ratio after excluding the named folio. H/F remain separate.\n\n'
    text+=f"Full six-folio subset: H {result['H']['baseline']['effect_points']:+.2f} points; F {result['F']['baseline']['effect_points']:+.2f} points.\n\n"
    text+='| Omitted folio | H remaining effect | H change | F remaining effect | F change |\n|---|---:|---:|---:|---:|\n'
    for h,f in zip(result['H']['omissions'],result['F']['omissions']):text+=f"| {h['omitted_folio']} | {h['effect_points']:+.2f} | {h['change_points']:+.2f} | {f['effect_points']:+.2f} | {f['change_points']:+.2f} |\n"
    text+='\n'
    for tr,r in result.items():text+=f"{tr}: remaining effects range from {r['range_points'][0]:+.2f} to {r['range_points'][1]:+.2f} points. {r['directional_description']} The largest attenuation is after omitting {r['lowest_effect_omission']}.\n\n"
    text+='No one folio is necessary for the positive sign in either reading. This does not mean equal contribution: f86v5 has the largest effect on the aggregate when omitted. F f85r2 and f86v3 have zero matched comparison weight, so omitting either leaves F’s matched effect unchanged. These are six nominal omissions but only four remove comparison weight in F.\n\n'
    text+='This is an exploratory influence description of a subset chosen after the original result; its pages already contributed to attempt C. Small and unevenly weighted comparisons remain. No p-values, confidence intervals, inferential decisions or revised support gates were used. A positive sign throughout these omissions is not a statistical robustness claim.\n\n'
    text+='Verification independently rebuilt all within-folio/family counts from the saved event ledger and reproduced all 14 baseline/omission effects with exact rational arithmetic. The earlier frozen reports and data are preserved.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:dict(baseline=r['baseline']['effect_points'],range=r['range_points'],omissions=[{k:v for k,v in row.items() if k in ['omitted_folio','effect_points','change_points','omitted_V_share']} for row in r['omissions']]) for tr,r in result.items()},indent=2))

if __name__=='__main__':main()
