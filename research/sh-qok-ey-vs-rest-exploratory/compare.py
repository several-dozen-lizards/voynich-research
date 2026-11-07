"""Exploratory ey vs edy/y/other descriptions, excluding eey on both sides."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
from datetime import datetime,timezone
import csv,json,hashlib

R=Path(__file__).resolve().parent;P=R.parent;S=P/'sh-qok-ey-alone-exploratory';V=P/'sh-qok-context-map-v3'
CONTEXTS={'C1':'hand2 bath','C2':'hand2 botanical','C3':'hand2 Rosettes','C4':'hand3 starred','C5':'hand3 botanical','C6':'hand1 botanical','C7':'hand1 recipes'}
FAMILIES=['eey','edy','ey','y','other']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def independently_recount(rows,fams):
    counts=[0,0,0,0];strata=defaultdict(lambda:[0,0,0,0])
    for r in rows:
        family=next((f for f in FAMILIES[:-1] if r['origin'].endswith(f)),'other');assert family==r['family']
        if family not in fams:continue
        j=0 if r['origin'].startswith('sh') else 1;y=int(r['follower'].startswith('qok'))
        assert y==int(r['y'])==int(r['outcome']);assert int(r['x'])==1-j
        counts[j]+=1;counts[2+j]+=y;strata[r['folio'],family][j]+=1;strata[r['folio'],family][2+j]+=y
    num=Fraction(0);den=Fraction(0)
    for ns,nc,a,b in strata.values():
        if ns and nc:
            w=1/(Fraction(1,ns)+Fraction(1,nc));num+=w*(Fraction(a,ns)-Fraction(b,nc));den+=w
    return counts,str(100*num/den) if den else None

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve prior output.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['EY-ROWS.json','REFERENCE-ROWS.json','PROTOCOL.json']:assert sha(S/n)==manifest[n]
    old_sources=json.loads((S/'PROTOCOL.json').read_text())['hashes'];assert sha(V/'EVENTS.csv')==old_sources[str(V/'EVENTS.csv')]
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), retrospective posthoc ey-vs-rest comparison after v3.2 and ey-alone outcomes were seen',utc=datetime.now(timezone.utc).isoformat(),
        scope='C1-C7 xH/F xall/available. Ey group is exact original ey family; comparison is edy,y,other. Eey excluded from both groups. No suffix fallback. H/F separate.',
        main_estimand='Event-pooled next-qok rate in ey minus event-pooled next-qok rate in edy/y/other, in percentage points, within each context,reading,view. Sh/ch pooled only within each group. This is not a folio-adjusted causal ending effect.',
        extra_descriptions='Same rate contrast separately after sh and ch; retain original within-folio x original-family MH sh-minus-ch gaps and weights for ey and reference group separately. Their gaps answer a different question than the direct ending-group rate contrast. No new matching across ending groups.',
        availability='Unchanged v3.1: remove followers starting sh,ch,cth,ckh,cph,cfh. Recompute group denominators. Qok followers remain available.',
        reporting='Every row, arm counts,rates,pooled rate difference,existing MH gaps/weights and <20-event flag for ey. Sparse or missing arm values remain visible; no formal scoring or support-gate changes.',
        limits='All outcomes already exposed. C1/C4 discovery/posthoc and C3 known-origin flagged; all comparisons exploratory. No p-values, confidence intervals, pass/fail, hypothesis denominator, prospective freezing, model fitting or mechanism claims.',
        hashes={str(p):sha(p) for p in [Path(__file__),S/'EY-ROWS.json',S/'REFERENCE-ROWS.json',S/'PROTOCOL.json',V/'EVENTS.csv']}))
    ey=json.loads((S/'EY-ROWS.json').read_text());reference=json.loads((S/'REFERENCE-ROWS.json').read_text())
    raw=list(csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')));out=[];checks=0
    for c in CONTEXTS:
        for tr in ['H','F']:
            for view in ['all','available']:
                a=next(r for r in ey if (r['context'],r['reading'],r['view'])==(c,tr,view));b=next(r for r in reference if (r['context'],r['reading'],r['view'])==(c,tr,view))
                rr=[]
                for r in raw:
                    if r['context']!=c or r['reading']!=tr or r['exclusion_reason']:continue
                    av=not r['follower'].startswith(('sh','ch','cth','ckh','cph','cfh'));assert av==(r['available']=='True')
                    if view=='all' or av:rr.append(r)
                for s,fams in [(a,['ey']),(b,['edy','y','other'])]:
                    counts,exact=independently_recount(rr,fams)
                    assert counts==[s[k] for k in ['sh_events','ch_events','sh_qok','ch_qok']]
                    assert exact==s['exact_MH_effect_points'];checks+=1
                def contrast(n1,d1,n2,d2):
                    value=100*(Fraction(n1,d1)-Fraction(n2,d2)) if d1 and d2 else None
                    return dict(effect_points=float(value) if value is not None else None,exact_effect_points=str(value) if value is not None else None)
                pooled=contrast(a['pooled_qok'],a['events'],b['pooled_qok'],b['events'])
                assert abs(pooled['effect_points']-a['family_minus_reference_rate_points'])<1e-12
                arms={}
                for prefix in ['sh','ch']:
                    arms[prefix]=dict(ey_qok=a[prefix+'_qok'],ey_events=a[prefix+'_events'],reference_qok=b[prefix+'_qok'],reference_events=b[prefix+'_events'],ey_rate=a[prefix+'_qok_rate'],reference_rate=b[prefix+'_qok_rate'],**contrast(a[prefix+'_qok'],a[prefix+'_events'],b[prefix+'_qok'],b[prefix+'_events']))
                out.append(dict(classification='EXPLORATORY (E)',context=c,context_name=CONTEXTS[c],reading=tr,view=view,discovery=c in ['C1','C4'],known_origin=c=='C3',
                    ey_events=a['events'],ey_qok=a['pooled_qok'],ey_rate=a['pooled_qok_rate'],reference_events=b['events'],reference_qok=b['pooled_qok'],reference_rate=b['pooled_qok_rate'],
                    rate_difference_points=pooled['effect_points'],exact_rate_difference_points=pooled['exact_effect_points'],arms=arms,ey_events_below20=a['events']<20,
                    ey_MH_sh_minus_ch_points=a['MH_effect_points'],reference_MH_sh_minus_ch_points=b['MH_effect_points'],ey_V=a['V'],reference_V=b['V'],ey_matched_strata=a['supported_strata'],reference_matched_strata=b['supported_strata']))
    assert len(out)==28
    save('COMPARISONS.json',out)
    with (R/'COMPARISONS.csv').open('w',encoding='utf-8',newline='') as f:
        flat=[{k:v for k,v in r.items() if k!='arms'} for r in out];w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    with (R/'ARM-COMPARISONS.csv').open('w',encoding='utf-8',newline='') as f:
        flat=[dict(context=r['context'],reading=r['reading'],view=r['view'],prefix=prefix,**a) for r in out for prefix,a in r['arms'].items()];w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    def fmt(v):return 'NA' if v is None else f'{v:+.2f}'
    def rate(v):return 'NA' if v is None else f'{100*v:.2f}%'
    text='EXPLORATORY (E) — ey compared with edy/y/other, eey excluded\n\n'
    text+='All comparisons are retrospective posthoc descriptions. Ey is the disjoint original ending family; eey is excluded from both sides. H/F remain separate readings. All and available-only views retain v3.1 definitions. No p-values, intervals or inferential decisions are computed.\n\n'
    text+='## Direct pooled next-qok rate comparison\n\nThe difference is ey rate minus edy/y/other rate in percentage points, pooling sh/ch within each side. Negative means a lower observed rate after ey; positive means higher. This raw rate comparison does not adjust for folio or opener composition. It is distinct from the within-family MH sh-minus-ch comparison.\n\n'
    text+='| Context | Reading | View | ey qok/events | ey rate | edy/y/other qok/events | Reference rate | Difference pts | ey <20 events |\n|---|---|---|---:|---:|---:|---:|---:|---|\n'
    for r in out:text+=f"| {r['context']} {r['context_name']} | {r['reading']} | {r['view']} | {r['ey_qok']}/{r['ey_events']} | {rate(r['ey_rate'])} | {r['reference_qok']}/{r['reference_events']} | {rate(r['reference_rate'])} | {fmt(r['rate_difference_points'])} | {r['ey_events_below20']} |\n"
    text+='\n## Direct differences by opener\n\nWithin each opener, compare ey with the same edy/y/other reference; these also remain raw event-pooled descriptions.\n\n| Context | Reading | View | Opener | ey qok/events | ey rate | Reference qok/events | Reference rate | Difference pts |\n|---|---|---|---|---:|---:|---:|---:|---:|\n'
    for r in out:
        for prefix,a in r['arms'].items():text+=f"| {r['context']} | {r['reading']} | {r['view']} | {prefix} | {a['ey_qok']}/{a['ey_events']} | {rate(a['ey_rate'])} | {a['reference_qok']}/{a['reference_events']} | {rate(a['reference_rate'])} | {fmt(a['effect_points'])} |\n"
    text+='\n## Separate matched sh/ch effects within each side\n\nThese are original within-folio x original-family MH effects, not adjusted estimates of the direct ey-vs-reference contrast. The reference retains edy,y,other as separate strata rather than merging their family labels.\n\n| Context | Reading | View | ey MH sh-ch pts | Reference MH sh-ch pts | ey V | Reference V |\n|---|---|---|---:|---:|---:|---:|\n'
    for r in out:text+=f"| {r['context']} | {r['reading']} | {r['view']} | {fmt(r['ey_MH_sh_minus_ch_points'])} | {fmt(r['reference_MH_sh_minus_ch_points'])} | {r['ey_V']:.3f} | {r['reference_V']:.3f} |\n"
    text+='\n## Interpretation and verification\n\nThe descriptive contrast varies by context and reading. C2/C3 have lower pooled ey rates in both readings/views; C1/C4/C5/C6 have higher pooled ey rates in both readings/views. C7 is mixed: H is slightly higher with all followers but lower among available followers; F is slightly lower in both views. No categorical qok-blocking claim follows.\n\n'
    text+='C5 ey is below20 events in each reading/view and has no matched within-folio comparison in F. Raw rates can exist despite unavailable MH effects. C1/C4 are discovery contexts and C3 motivated the refinement; all these family outcomes were already examined in v3.2. No prospective evidence or new hypothesis score is claimed. Context and opener composition, sparse counts and selection remain unresolved.\n\n'
    text+='Independent event regrouping verified every arm count and all56 component MH effects. Exact-rational raw rate contrasts reproduce the previously saved ey-minus-reference quantities. Literal origin endings and follower outcomes were checked, availability recomputed and all frozen source hashes remained unchanged. No previous reports, v3 primary engines or results were changed.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    for p,h in json.loads((R/'PROTOCOL.json').read_text())['hashes'].items():assert sha(p)==h
    save('VERIFICATION.json',dict(status='VERIFIED',pooled_comparisons=28,opener_specific_comparisons=56,independent_component_MH_and_count_checks=checks,eey_excluded=True,all_input_hashes_unchanged=True,inferential_calculations_performed=False))
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps([{k:r[k] for k in ['context','reading','view','rate_difference_points','ey_rate','reference_rate']} for r in out],indent=2))

if __name__=='__main__':main()
