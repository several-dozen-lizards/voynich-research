"""Exploratory ey-alone profile; eey separate, H/F separate, both views."""
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util

R=Path(__file__).resolve().parent;P=R.parent;A=P/'sh-qok-ending-blocking-v3-2';V=P/'sh-qok-context-map-v3'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve earlier output.'
    old_manifest=json.loads((A/'DELIVERY-MANIFEST.json').read_text())['hashes']
    for n in ['analyze.py','FAMILY-ROWS.json','PROTOCOL.json','PRECHECK.json']:assert sha(A/n)==old_manifest[n]
    for p,h in json.loads((A/'FREEZE.json').read_text())['hashes'].items():assert sha(p)==h
    spec=importlib.util.spec_from_file_location('verified_v32_arithmetic',A/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), retrospective ey-alone refinement after v3.2 family outcomes were seen',utc=datetime.now(timezone.utc).isoformat(),
        scope='C1-C7 xH/F xall/available. Main table ey only. Separate eey companion, never combined with ey. Both are original disjoint longest-first ending families; eey is not reassigned to ey.',
        source='Unchanged v3 EVENTS.csv; v3.1 available excludes followers opening sh,ch,cth,ckh,cph,cfh.',
        report='Raw sh/ch next-qok counts and rates, pooled family rate, same within-folio MH effect/weight and context share, total/matched/zero-qok strata, and <20event flag for the individual reported family. Small rows retained descriptively; no test or threshold imposed on another family.',
        comparator='For descriptive context only, retain original edy+y+other pooled rate. Both ey and eey excluded from that comparator. No new hypothesis score or numerator/denominator headline.',
        limits='All family outcomes were already reported in v3.2. C1/C4 discovery and historically posthoc; C3 known-origin Rosettes. This refinement is posthoc exploratory in every context, with no p-values, confidence intervals, formal eligibility decisions, pass/fail, fitting, qualification or prospective claim.',
        hashes={str(p):sha(p) for p in [Path(__file__),A/'analyze.py',A/'FAMILY-ROWS.json',A/'PROTOCOL.json',A/'PRECHECK.json',V/'EVENTS.csv']}))
    records=list(csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')));eligible=[]
    for r in records:
        if r['exclusion_reason'] or r['context'] not in a.CONTEXTS or r['reading'] not in ['H','F']:continue
        r=dict(r);r['qok']=int(r['follower'].startswith('qok'))
        av=not r['follower'].startswith(('sh','ch','cth','ckh','cph','cfh'));assert av==(r['available']=='True')
        r['is_available']=av;eligible.append(r)
    previous=json.loads((A/'FAMILY-ROWS.json').read_text());out=[];comparators=[];checks=0
    for c in a.CONTEXTS:
        for tr in ['H','F']:
            for view in ['all','available']:
                rows=[r for r in eligible if r['context']==c and r['reading']==tr and (view=='all' or r['is_available'])]
                baseline=a.stats(rows);rest=a.stats([r for r in rows if r['family'] in ['edy','y','other']])
                assert rest['exact_MH_effect_points']==a.independent([r for r in rows if r['family'] in ['edy','y','other']]);checks+=1
                comps=dict(context=c,context_name=a.CONTEXTS[c],reading=tr,view=view,comparison_family_set=['edy','y','other'],**rest)
                comparators.append(comps)
                for fam in ['ey','eey']:
                    rr=[r for r in rows if r['family']==fam];s=a.stats(rr)
                    assert s['exact_MH_effect_points']==a.independent(rr);checks+=1
                    old=next(v for v in previous if (v['context'],v['reading'],v['view'],v['family'])==(c,tr,view,fam))
                    for k,value in s.items():assert value==old[k],(c,tr,view,fam,k)
                    s.update(context=c,context_name=a.CONTEXTS[c],reading=tr,view=view,family=fam,
                        exploratory=True,previously_exposed_family_outcomes=True,discovery=c in ['C1','C4'],known_origin=c=='C3',
                        events_at_least20=s['events']>=20,context_V_share=s['V']/baseline['V'] if baseline['V'] else None,
                        reference_edy_y_other_rate=rest['pooled_qok_rate'],family_minus_reference_rate_points=100*(s['pooled_qok_rate']-rest['pooled_qok_rate']) if s['pooled_qok_rate'] is not None and rest['pooled_qok_rate'] is not None else None)
                    out.append(s)
    assert len(out)==56 and len(comparators)==28
    save('EY-ROWS.json',[r for r in out if r['family']=='ey']);save('EEY-SEPARATE.json',[r for r in out if r['family']=='eey']);save('REFERENCE-ROWS.json',comparators)
    with (R/'FAMILY-ROWS.csv').open('w',encoding='utf-8',newline='') as f:
        flat=[{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()} for r in out]
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    def qn(r):return f"{r['pooled_qok']}/{r['events']}"
    def rate(v):return 'NA' if v is None else f'{100*v:.2f}%'
    def gap(v):return 'NA' if v is None else f'{v:+.2f}'
    text='EXPLORATORY (E) — ey alone across C1-C7; eey kept separate\n\n'
    text+='This is a retrospective refinement after the v3.2 family-level outcomes were already seen. C1/C4 are discovery/posthoc; C3 is the known Rosettes origin. H/F are separate alternate readings, not independent samples. No p-values, intervals or inferential decisions are calculated.\n\n'
    text+='## ey pooled counts\n\nCounts below combine sh/ch only for a raw family follower rate; the next table retains separate arms and within-folio matched effects. eey never enters these ey rows.\n\n'
    text+='| Context | H all qok/events | H available qok/events | F all qok/events | F available qok/events |\n|---|---:|---:|---:|---:|\n'
    for c in a.CONTEXTS:
        cells=[next(r for r in out if (r['context'],r['reading'],r['view'],r['family'])==(c,tr,view,'ey')) for tr,view in [('H','all'),('H','available'),('F','all'),('F','available')]]
        text+='| '+c+' '+a.CONTEXTS[c]+' | '+' | '.join(qn(r)+' ('+rate(r['pooled_qok_rate'])+')' for r in cells)+' |\n'
    for fam in ['ey','eey']:
        text+=f'\n## {fam} — separate arm counts and MH effects\n\n'
        text+='| Context | Reading | View | sh qok/events | sh rate | ch qok/events | ch rate | Pooled rate | MH pts | V | Context V share | Zero-qok supported/total supported strata | <20 events |\n|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n'
        for r in out:
            if r['family']!=fam:continue
            text+=f"| {r['context']} | {r['reading']} | {r['view']} | {r['sh_qok']}/{r['sh_events']} | {rate(r['sh_qok_rate'])} | {r['ch_qok']}/{r['ch_events']} | {rate(r['ch_qok_rate'])} | {rate(r['pooled_qok_rate'])} | {gap(r['MH_effect_points'])} | {r['V']:.3f} | {rate(r['context_V_share'])} | {r['zero_qok_both_supported_strata']}/{r['supported_strata']} | {not r['events_at_least20']} |\n"
    text+='\n## Interpretation\n\n'
    text+='Among C1-C7, ey has zero observed qok followers only in C3 Rosettes:0/25 in each all-follower reading and0/22 in each available-only reading. Every other context has observed ey→qok events. This is a local zero, not a general prohibition.\n\n'
    text+='The all-follower ey MH differences are: C1 +14.10 H/+10.73 F; C2 0.00 H/+18.07 F; C3 0.00 both; C4 +12.15 H/+8.61 F; C5 +33.33 H/unavailable F; C6 -4.51 H/-3.60 F; C7 +13.76 H/+19.25 F. Available-only values and all weights appear above. Raw pooled-arm differences and within-folio MH differences can differ in direction because single-prefix strata do not contribute to the latter.\n\n'
    text+='C2 H illustrates why zero MH does not mean no qok: it has2/31 ey→qok events overall, but no qok in its supported sh/ch comparison strata. C5 F has qok events but no matched within-folio ey comparison at all; its MH gap is unavailable, not zero. C5 ey counts are below20 in both readings/views and remain small descriptive cells.\n\n'
    text+='The eey companion rows remain separate throughout. In particular C3 eey has3/15 H and2/10 F qok followers despite zero MH effects, as previously audited. Longest-first assignment prevents eey words from entering ey.\n\n'
    text+='REFERENCE-ROWS.json retains the original edy+y+other group solely as descriptive context, excluding both ey and eey. The CSV includes each family-minus-reference pooled rate difference without a test or hypothesis tally. No earlier eligibility rule was relaxed or primary result changed.\n\n'
    text+='## Verification\n\nAll56 separate ey/eey rows reproduce the saved v3.2 counts, rates, weights and exact MH effects. Independent event regrouping verified those56 MH calculations and28 reference effects (84 checks), with longest-first origin endings, x/y labels, literal follower outcomes and availability independently checked. Earlier files are unchanged.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    for p,h in json.loads((R/'PROTOCOL.json').read_text())['hashes'].items():assert sha(p)==h
    save('VERIFICATION.json',dict(status='VERIFIED',individual_family_rows=56,ey_rows=28,eey_rows=28,independent_exact_MH_checks=checks,all_saved_v32_family_quantities_reproduced=True,all_input_hashes_unchanged=True,no_inferential_calculations=True))
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps(dict(classification='EXPLORATORY',ey_zero_qok_cells=[dict(context=r['context'],reading=r['reading'],view=r['view'],events=r['events']) for r in out if r['family']=='ey' and r['pooled_qok']==0],checks=checks,rows=len(out)),indent=2))

if __name__=='__main__':main()
