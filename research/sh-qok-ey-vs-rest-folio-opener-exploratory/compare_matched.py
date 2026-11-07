"""Descriptive ey vs edy/y/other, matched within physical folio x opener."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
from datetime import datetime,timezone
import csv,json,hashlib

R=Path(__file__).resolve().parent;P=R.parent;S=P/'sh-qok-ey-vs-rest-exploratory';V=P/'sh-qok-context-map-v3'
CONTEXTS={'C1':'hand2 bath','C2':'hand2 botanical','C3':'hand2 Rosettes','C4':'hand3 starred','C5':'hand3 botanical','C6':'hand1 botanical','C7':'hand1 recipes'}
FAMILIES=['eey','edy','ey','y','other']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def match(rows):
    counts=defaultdict(lambda:[0,0,0,0])
    for r in rows:
        group=0 if r['family']=='ey' else 1;z=counts[r['folio'],r['prefix']]
        z[group]+=1;z[2+group]+=int(r['outcome'])
    num=Fraction(0);den=Fraction(0);ey_num=Fraction(0);rest_num=Fraction(0);strata=[]
    matched_counts=[0,0,0,0]
    for (pg,prefix),(ne,nr,a,b) in sorted(counts.items()):
        w=Fraction(ne*nr,ne+nr);delta=Fraction(a,ne)-Fraction(b,nr) if ne and nr else None
        if w:
            num+=w*delta;den+=w;ey_num+=w*Fraction(a,ne);rest_num+=w*Fraction(b,nr)
            matched_counts=[x+y for x,y in zip(matched_counts,[ne,nr,a,b])]
        strata.append(dict(folio=pg,opener=prefix,ey_events=ne,reference_events=nr,ey_qok=a,reference_qok=b,ey_rate=a/ne if ne else None,reference_rate=b/nr if nr else None,
            matched=bool(w),weight=float(w),exact_weight=str(w),effect_points=float(100*delta) if delta is not None else None,exact_effect_points=str(100*delta) if delta is not None else None))
    ne=sum(r['family']=='ey' for r in rows);nr=len(rows)-ne
    a=sum(int(r['outcome']) for r in rows if r['family']=='ey');b=sum(int(r['outcome']) for r in rows if r['family']!='ey')
    gap=100*num/den if den else None
    raw=100*(Fraction(a,ne)-Fraction(b,nr)) if ne and nr else None
    return dict(ey_events=ne,reference_events=nr,ey_qok=a,reference_qok=b,
        matched_ey_events=matched_counts[0],matched_reference_events=matched_counts[1],matched_ey_qok=matched_counts[2],matched_reference_qok=matched_counts[3],
        unmatched_ey_events=ne-matched_counts[0],unmatched_reference_events=nr-matched_counts[1],
        ey_event_coverage=matched_counts[0]/ne if ne else None,reference_event_coverage=matched_counts[1]/nr if nr else None,
        pooled_raw_difference_points=float(raw) if raw is not None else None,
        matched_difference_points=float(gap) if gap is not None else None,exact_matched_difference_points=str(gap) if gap is not None else None,
        matched_ey_rate=float(ey_num/den) if den else None,matched_reference_rate=float(rest_num/den) if den else None,
        weight_sum=float(den),exact_weight_sum=str(den),matched_strata=sum(s['matched'] for s in strata),total_strata=len(strata),
        contributing_folios=sorted({s['folio'] for s in strata if s['matched']}),strata=strata)

def independent(rows):
    # Re-derive exposure, opener and outcome from literal tokens; use covariance form.
    g=defaultdict(lambda:[0,0,0,0])
    for r in rows:
        word=r['origin'];fam=next((s for s in FAMILIES[:-1] if word.endswith(s)),'other');assert fam==r['family'] and fam!='eey'
        opener='sh' if word.startswith('sh') else 'ch';assert opener==r['prefix']
        j=0 if fam=='ey' else 1;z=g[r['folio'],opener];z[j]+=1;z[2+j]+=int(r['follower'].startswith('qok'))
    numerator=Fraction(0);weight=Fraction(0)
    for ne,nr,a,b in g.values():
        if ne and nr:
            numerator+=Fraction(a*nr-b*ne,ne+nr);weight+=1/(Fraction(1,ne)+Fraction(1,nr))
    return (str(100*numerator/weight) if weight else None),str(weight),g

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve existing output.'
    manifest=json.loads((S/'MANIFEST.json').read_text())['hashes']
    for n in ['COMPARISONS.json','PROTOCOL.json']:assert sha(S/n)==manifest[n]
    previous_protocol=json.loads((S/'PROTOCOL.json').read_text());assert sha(V/'EVENTS.csv')==previous_protocol['hashes'][str(V/'EVENTS.csv')]
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), retrospective posthoc matching refinement after raw ending-group contrasts were seen',utc=datetime.now(timezone.utc).isoformat(),
        context_map=CONTEXTS,groups=dict(exposure=['ey'],reference=['edy','y','other'],excluded=['eey']),
        strata='Within each context x reading x view: exact physical Folio identifier x literal opener sh/ch. Both ending groups must be present in that stratum; zero-overlap strata are retained with weight0. This matching is distinct from earlier sh/ch comparisons stratified by ending family.',
        estimand='MH-style weighted next-qok rate difference ey minus pooled edy/y/other, percentage points. In stratum s, w=ne*nr/(ne+nr); sum[w*(a/ne-b/nr)]/sum(w). Same weights compute both matched rates. No matching on original reference-ending family, since ending group is the exposure. No exact-position or line matching.',
        supplementary='Same ratio separately by opener (then strata are folios), complete per-folio/opener counts and rates; compare raw pooled context contrasts to previous saved values. Report retained/unmatched counts and coverage for each side. No support or power thresholds applied.',
        follower_views='All eligible events, and available-only with followers starting sh/ch/cth/ckh/cph/cfh excluded under unchanged v3.1 rule. Eey remains excluded from both ending groups, using original longest-first labels.',
        limits='All outcomes exposed; C1/C4 discovery, C3 known origin. H/F separate alternate readings. No p-values, confidence intervals, pass/fail, eligibility gates, qualification, fitting or causal/mechanistic claim. Matching controls recorded folio and opener composition only; sparse overlap and other confounding remain.',
        hashes={str(p):sha(p) for p in [Path(__file__),V/'EVENTS.csv',S/'COMPARISONS.json',S/'PROTOCOL.json']}))
    prior=json.loads((S/'COMPARISONS.json').read_text());records=list(csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')))
    eligible=[]
    for r in records:
        if r['context'] not in CONTEXTS or r['reading'] not in ['H','F'] or r['exclusion_reason'] or r['family']=='eey':continue
        assert r['family'] in ['ey','edy','y','other']
        assert int(r['outcome'])==int(r['y'])==int(r['follower'].startswith('qok'))
        assert int(r['x'])==int(r['prefix']=='sh')
        av=not r['follower'].startswith(('sh','ch','cth','ckh','cph','cfh'));assert av==(r['available']=='True')
        eligible.append(r)
    out=[];opener_rows=[];stratum_rows=[];checks=0
    for c in CONTEXTS:
        for tr in ['H','F']:
            for view in ['all','available']:
                rows=[r for r in eligible if r['context']==c and r['reading']==tr and (view=='all' or r['available']=='True')]
                meta=dict(context=c,context_name=CONTEXTS[c],reading=tr,view=view,exploratory=True,discovery=c in ['C1','C4'],known_origin=c=='C3')
                result=match(rows);value,weight,groups=independent(rows)
                assert result['exact_matched_difference_points']==value and result['exact_weight_sum']==weight;checks+=1
                for s in result['strata']:
                    assert groups[s['folio'],s['opener']]==[s[k] for k in ['ey_events','reference_events','ey_qok','reference_qok']]
                    stratum_rows.append(meta|s)
                old=next(r for r in prior if (r['context'],r['reading'],r['view'])==(c,tr,view))
                assert abs(result['pooled_raw_difference_points']-old['rate_difference_points'])<1e-12
                for k in ['ey_events','reference_events','ey_qok','reference_qok']:assert result[k]==old[k]
                out.append(meta|result)
                combined_num=Fraction(0);combined_weight=Fraction(0)
                for opener in ['sh','ch']:
                    rr=[r for r in rows if r['prefix']==opener];s=match(rr);v,w,g=independent(rr)
                    assert s['exact_matched_difference_points']==v and s['exact_weight_sum']==w;checks+=1
                    opener_rows.append(meta|dict(opener=opener)|{k:v for k,v in s.items() if k!='strata'})
                    if w!='0':combined_num+=Fraction(v)*Fraction(w);combined_weight+=Fraction(w)
                assert (str(combined_num/combined_weight) if combined_weight else None)==value
    save('MATCHED-COMPARISONS.json',out);save('OPENER-COMPARISONS.json',opener_rows)
    for name,rr in [('MATCHED-COMPARISONS.csv',[{k:v for k,v in r.items() if k!='strata'} for r in out]),('OPENER-COMPARISONS.csv',opener_rows),('STRATA.csv',stratum_rows)]:
        with (R/name).open('w',encoding='utf-8',newline='') as f:
            flat=[{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()} for r in rr]
            writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    def fmt(v):return 'NA' if v is None else f'{v:+.2f}'
    def rate(v):return 'NA' if v is None else f'{100*v:.2f}%'
    text='EXPLORATORY (E) — ey vs edy/y/other within physical folio and opener\n\n'
    text+='Eey is excluded from both ending groups. Within each context/reading/view, compare ey with pooled edy/y/other only in folio x opener strata containing both ending groups. Weight each rate difference by ne*nr/(ne+nr). H/F remain separate. This is a descriptive matching refinement after the raw contrasts were seen, with no p-values or intervals.\n\n'
    text+='## Matched ending-group differences\n\nEffects are percentage points, ey minus reference. Positive means higher next-qok rate after ey; negative means lower. These are ending-group contrasts adjusted for recorded folio and sh/ch opener composition, not the earlier sh-minus-ch H1 effects and not causal effects.\n\n'
    text+='| Context | Reading | View | Matched ey rate | Matched reference rate | Matched difference pts | Raw pooled difference pts | Matched strata | Contributing folios | Weight sum |\n|---|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in out:text+=f"| {r['context']} {r['context_name']} | {r['reading']} | {r['view']} | {rate(r['matched_ey_rate'])} | {rate(r['matched_reference_rate'])} | {fmt(r['matched_difference_points'])} | {fmt(r['pooled_raw_difference_points'])} | {r['matched_strata']} | {len(r['contributing_folios'])} | {r['weight_sum']:.3f} |\n"
    text+='\n## Comparison overlap\n\nCounts are eligible events covered by matched folio x opener strata divided by all eligible events on that side. Unmatched events remain in STRATA.csv with weight0; unavailable effects are not replaced with zero.\n\n| Context | Reading | View | ey covered/total | Reference covered/total | Unmatched ey | Unmatched reference |\n|---|---|---|---:|---:|---:|---:|\n'
    for r in out:text+=f"| {r['context']} | {r['reading']} | {r['view']} | {r['matched_ey_events']}/{r['ey_events']} | {r['matched_reference_events']}/{r['reference_events']} | {r['unmatched_ey_events']} | {r['unmatched_reference_events']} |\n"
    text+='\n## Each opener separately\n\nHere comparisons remain within folio, retaining just the named opener. Their component weighted numerators/denominators exactly recombine to the pooled folio x opener result.\n\n| Context | Reading | View | Opener | Matched difference pts | ey rate | Reference rate | Matched strata | Weight sum |\n|---|---|---|---|---:|---:|---:|---:|---:|\n'
    for r in opener_rows:text+=f"| {r['context']} | {r['reading']} | {r['view']} | {r['opener']} | {fmt(r['matched_difference_points'])} | {rate(r['matched_ey_rate'])} | {rate(r['matched_reference_rate'])} | {r['matched_strata']} | {r['weight_sum']:.3f} |\n"
    text+='\n## Limits and verification\n\nThe matched result targets the strata with overlap, not all events in a context. Small or selective overlap can strongly limit interpretation; counts, weights and each individual stratum are supplied. Matched rates use common harmonic-exposure weights and are not simple pooled rates. Removing structurally unavailable followers changes both denominators and stratum weights.\n\n'
    text+='C1/C4 are discovery/posthoc contexts; C3 motivated this refinement. All family-level outcomes were already examined, and H/F are two readings of the same manuscript. No new significance score, support gate, hypothesis denominator, model, qualification or prospective claim is introduced. Other spelling, layout and context differences remain uncontrolled; no meanings or grammar/junction conclusion follows.\n\n'
    text+='Independent exact-rational regrouping from literal origins/followers reproduced all28 combined and56 opener-specific matched effects (84 checks) and every stratum count. Component opener effects recombine exactly. All28 earlier raw contrasts and group totals were reproduced. Eey exclusion and v3.1 availability were rechecked, source hashes stayed unchanged, and previous analyses remain intact.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    for p,h in json.loads((R/'PROTOCOL.json').read_text())['hashes'].items():assert sha(p)==h
    save('VERIFICATION.json',dict(status='VERIFIED',combined_comparisons=28,opener_comparisons=56,independent_exact_rational_checks=checks,all_stratum_counts_reproduced=True,opener_components_recombine_exactly=True,all_previous_raw_contrasts_and_totals_reproduced=True,eey_excluded=True,availability_recomputed=True,all_input_hashes_unchanged=True,inferential_calculations_performed=False))
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps([{k:r[k] for k in ['context','reading','view','matched_difference_points','pooled_raw_difference_points','matched_ey_events','ey_events','matched_reference_events','reference_events','matched_strata','weight_sum']} for r in out],indent=2))

if __name__=='__main__':main()
