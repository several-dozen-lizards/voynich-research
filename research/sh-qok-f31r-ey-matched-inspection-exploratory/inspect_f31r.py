"""Exploratory event/count inspection of f31r matched ey-vs-reference influence."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
from datetime import datetime,timezone
import csv,json,hashlib,re,importlib.util

R=Path(__file__).resolve().parent;P=R.parent;M=P/'sh-qok-ey-vs-rest-folio-opener-exploratory';L=P/'sh-qok-ey-vs-rest-folio-opener-loo-exploratory';V=P/'sh-qok-context-map-v3'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def write_csv(n,rows):
    with (R/n).open('w',encoding='utf-8',newline='') as f:
        flat=[{k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()} for r in rows]
        fields=list(dict.fromkeys(k for r in flat for k in r));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve existing output.'
    for folder,names in [(M,['compare_matched.py','MATCHED-COMPARISONS.json','STRATA.csv','PROTOCOL.json']),(L,['LEAVE-ONE-FOLIO-OUT.json','PROTOCOL.json'])]:
        manifest=json.loads((folder/'MANIFEST.json').read_text())['hashes']
        for n in names:assert sha(folder/n)==manifest[n]
    source_protocol=json.loads((V/'PROTOCOL.json').read_text());source=next(Path(p) for p in source_protocol['sources'] if 'text16e6' in p)
    assert sha(source)==source_protocol['sources'][str(source)]
    assert sha(V/'EVENTS.csv')==json.loads((M/'PROTOCOL.json').read_text())['hashes'][str(V/'EVENTS.csv')]
    spec=importlib.util.spec_from_file_location('verified_matching',M/'compare_matched.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), retrospective event inspection selected after f31r influence was observed',utc=datetime.now(timezone.utc).isoformat(),
        focus='C2 f31r, literal sh/ch opener strata; ey versus pooled edy/y/other. Eey excluded from all focal matched counts. H/F separate and all/available views separate.',
        report='Counts/rates/weights in each stratum; family composition of reference; all eligible source-event receipts and blocked events; local matched effect and contribution to full C2 weighted numerator; exact reconstruction with and without folio. Audit excluded events separately, not as included counts.',
        influence='Stratum signed numerator=w*(ey_rate-reference_rate). Contribution to full C2 effect in points=100*numerator/full_C2_weight. Local folio effect uses local weight denominator. These are different quantities. Remove folio subtracts its numerator and weight, no model refit.',
        limits='No p-values, confidence intervals, inferential decisions, deletion recommendations or new gates. Small observed zero is not a prohibition. H/F are alternate readings of common source events; reading differences remain unharmonized.',
        hashes={str(p):sha(p) for p in [Path(__file__),M/'compare_matched.py',M/'MATCHED-COMPARISONS.json',M/'STRATA.csv',L/'LEAVE-ONE-FOLIO-OUT.json',V/'EVENTS.csv',source]}))
    ledger=list(csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')))
    raw_f31=[r for r in ledger if r['context']=='C2' and r['folio']=='f31r']
    # Independent raw-EVT tokenization and locator audit; preserve raw line text as receipt.
    rawlines={};wordlines={}
    for raw in source.read_text(encoding='latin1').splitlines():
        m=re.match(r'^<(f31r\.[^.]+\.[^;]+);([HF])>\s*(.*)',raw)
        if not m:continue
        loc,tr,txt=m.groups();clean=re.sub(r'\{[^}]*\}','',txt.partition('#')[0]);clean=re.sub(r'[!\s]','',clean)
        words=[w if re.fullmatch('[a-z]+',w) else None for w in re.split(r'[.,=\-]',clean) if w]
        rawlines[loc,tr]=raw;wordlines[loc,tr]=words
    for r in raw_f31:
        ws=wordlines[r['line'],r['reading']];i=int(r['position']);origin=ws[i];follower=ws[i+1] if i+1<len(ws) else None
        assert (origin or '')==r['origin'] and (follower or '')==r['follower']
        if not r['exclusion_reason']:
            assert int(r['outcome'])==int(follower.startswith('qok'))
            assert (not follower.startswith(('sh','ch','cth','ckh','cph','cfh')))==(r['available']=='True')
    eligible=[r for r in ledger if r['context']=='C2' and not r['exclusion_reason'] and r['family']!='eey']
    parent=json.loads((M/'MATCHED-COMPARISONS.json').read_text());omissions=json.loads((L/'LEAVE-ONE-FOLIO-OUT.json').read_text())
    strata=[];summary=[];family_rows=[];view_events=[];checks=0
    for tr in ['H','F']:
        for view in ['all','available']:
            rr=[r for r in eligible if r['reading']==tr and (view=='all' or r['available']=='True')]
            local=[r for r in rr if r['folio']=='f31r'];other=[r for r in rr if r['folio']!='f31r']
            context=a.match(rr);focal=a.match(local);remaining=a.match(other)
            old=next(r for r in parent if (r['context'],r['reading'],r['view'])==('C2',tr,view))
            loo=next(r for r in omissions if (r['context'],r['reading'],r['view'])==('C2',tr,view));omit=next(r for r in loo['omissions'] if r['omitted_folio']=='f31r')
            assert context['exact_matched_difference_points']==old['exact_matched_difference_points']
            assert remaining['exact_matched_difference_points']==omit['exact_matched_difference_points']
            W=Fraction(context['exact_weight_sum']);wlocal=Fraction(focal['exact_weight_sum']);Wother=Fraction(remaining['exact_weight_sum'])
            N=Fraction(context['exact_matched_difference_points'])*W/100
            nlocal=Fraction(focal['exact_matched_difference_points'])*wlocal/100
            Nother=Fraction(remaining['exact_matched_difference_points'])*Wother/100
            assert W==wlocal+Wother and N==nlocal+Nother
            for result,events in [(context,rr),(focal,local),(remaining,other)]:
                value,weight,g=a.independent(events);assert value==result['exact_matched_difference_points'] and weight==result['exact_weight_sum'];checks+=1
            for s in focal['strata']:
                w=Fraction(s['exact_weight']);d=Fraction(s['exact_effect_points']);num=w*d/100
                strata.append(dict(reading=tr,view=view,**s,weighted_numerator=float(num),exact_weighted_numerator=str(num),C2_weight_share=float(w/W),contribution_to_C2_points=float(100*num/W)))
            for opener in ['sh','ch']:
                for family in ['ey','edy','y','other']:
                    selected=[r for r in local if r['prefix']==opener and r['family']==family]
                    family_rows.append(dict(reading=tr,view=view,opener=opener,family=family,events=len(selected),qok=sum(int(r['outcome']) for r in selected)))
            for r in local:
                view_events.append(dict(view=view,**r,ending_group='ey' if r['family']=='ey' else 'edy/y/other',raw_source_line=rawlines[r['line'],r['reading']]))
            blocked=[r for r in eligible if r['folio']=='f31r' and r['reading']==tr and r['available']=='False']
            assert all(r['outcome']=='0' for r in blocked)
            summary.append(dict(reading=tr,view=view,context_C2_difference_points=context['matched_difference_points'],f31r_difference_points=focal['matched_difference_points'],
                without_f31r_difference_points=remaining['matched_difference_points'],f31r_weight=float(wlocal),C2_weight=float(W),f31r_weight_share=float(wlocal/W),
                C2_weighted_numerator=float(N),f31r_weighted_numerator=float(nlocal),other_folios_weighted_numerator=float(Nother),
                f31r_component_of_full_C2_points=float(100*nlocal/W),other_folios_component_of_full_C2_points=float(100*Nother/W),
                f31r_counts={k:focal[k] for k in ['ey_events','ey_qok','reference_events','reference_qok','matched_strata']},
                unavailable_follower_counts=dict(ey=sum(r['family']=='ey' for r in blocked),reference=sum(r['family']!='ey' for r in blocked)),
                caution='Local folio gap, weighted full-context contribution and deletion shift use different denominators.'))
    save('STRATA.json',strata);save('INFLUENCE.json',summary)
    write_csv('STRATA.csv',strata);write_csv('FAMILY-COMPOSITION.csv',family_rows);write_csv('EVENTS-BY-VIEW.csv',view_events)
    write_csv('QOK-REFERENCE-EVENTS.csv',[r for r in view_events if r['view']=='all' and r['outcome']=='1'])
    write_csv('BLOCKED-EVENTS.csv',[dict(**r,raw_source_line=rawlines[r['line'],r['reading']]) for r in raw_f31 if not r['exclusion_reason'] and r['family']!='eey' and r['available']=='False'])
    write_csv('EXCLUSION-AUDIT.csv',[dict(**r,inspection_exclusion='original_'+r['exclusion_reason'] if r['exclusion_reason'] else 'eey_excluded',raw_source_line=rawlines[r['line'],r['reading']]) for r in raw_f31 if r['exclusion_reason'] or r['family']=='eey'])
    def fmt(v):return f'{v:+.2f}'
    text='EXPLORATORY (E) — f31r matched ey-versus-edy/y/other count inspection in C2\n\n'
    text+='The ending groups are compared within each literal opener on this physical folio. Eey is excluded from all matched counts. Each view and reading is separate. This folio was selected after its influence was seen; no p-values or inferential decisions are computed.\n\n'
    text+='## Stratum counts and local differences\n\n| Reading | View | Opener | ey qok/events | Reference qok/events | ey rate | Reference rate | Difference pts | Weight | Contribution to full C2 pts |\n|---|---|---|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in strata:text+=f"| {r['reading']} | {r['view']} | {r['opener']} | {r['ey_qok']}/{r['ey_events']} | {r['reference_qok']}/{r['reference_events']} | {100*r['ey_rate']:.2f}% | {100*r['reference_rate']:.2f}% | {fmt(r['effect_points'])} | {r['weight']:.3f} | {fmt(r['contribution_to_C2_points'])} |\n"
    text+='\nThe dominant contrast is the sh stratum: ey0/2 versus reference3/7 in each reading. Available-only retains all3 reference qok events while reducing that reference denominator to5 in H and4 in F, yielding -60 and -75 point local sh contrasts. The ch stratum is also negative but smaller. These are small observed samples, not evidence of a prohibition.\n\n'
    text+='## Influence decomposition\n\n| Reading | View | f31r local combined gap | f31r share of C2 weight | f31r contribution to full C2 pts | Other folios contribution to full C2 pts | Full C2 gap | C2 without f31r |\n|---|---|---:|---:|---:|---:|---:|---:|\n'
    for r in summary:text+=f"| {r['reading']} | {r['view']} | {fmt(r['f31r_difference_points'])} | {100*r['f31r_weight_share']:.2f}% | {fmt(r['f31r_component_of_full_C2_points'])} | {fmt(r['other_folios_component_of_full_C2_points'])} | {fmt(r['context_C2_difference_points'])} | {fmt(r['without_f31r_difference_points'])} |\n"
    text+='\nThe two contribution columns share the full C2 denominator and sum to its gap. The last column instead uses the reduced denominator after deleting f31r. F31r’s strongly negative local numerator outweighs a small positive numerator from the other folios in three cells; in H available, the other folios remain negative. No event or folio is removed from the actual analysis by this inspection.\n\n'
    text+='## Reference qok source receipts\n\nThe three sh events are the same recorded source loci in H/F: sheoody→qokeor (y) at f31r.P.5 position1; sheol→qokedy (other) at f31r.P.7 position3; shedy→qokedy (edy) at f31r.P.8 position0. All are available. The shared ch event is cheod→qokeody (other), f31r.P.8 position3. F adds chedy→qokey (edy), f31r.P.4 position8; H has an unknown origin in that slot and excludes it. Positions are zero-based source-token indices. H/F therefore do not constitute independent event samples.\n\n'
    text+='Every ey event, reference event and raw source line is in EVENTS-BY-VIEW.csv. There are no ey→qok events on f31r: H0/6 and F0/5 in all-follower views, H0/5 and F0/4 among available followers. Both readings have the same two sh ey examples: shckhey→qef at P.2 position6 and shcthey→okeol at P.9 position2.\n\n'
    text+='## Availability and reading differences\n\nUnavailable followers on f31r are all non-qok. H filtering removes1 ey event and5 reference events (ch reference10→7; sh reference7→5). F removes1 ey event and6 reference events (ch reference13→10; sh reference7→4). The removed ey event is checkhey→sheol at P.7 position2 in each reading. BLOCKED-EVENTS.csv identifies every removed event; none is classified as a missed qok outcome.\n\n'
    text+='FAMILY-COMPOSITION.csv separates edy,y,other within each reference stratum. EXCLUSION-AUDIT.csv preserves eey and original extraction exclusions separately; these rows never enter the focal counts. The extra F ch qok event reflects a transcription/uncertainty difference, not an inferred manuscript change or harmonized spelling.\n\n'
    text+='## Verification and limits\n\nAll saved f31r ledger origins/followers were independently matched to newly tokenized original EVT lines. Exact-rational regrouping reproduced all12 context/local/without-folio effects and every numerator/weight deletion identity, agreeing with previous matched and leave-one-out results. The eight strata and both opener contributions are preserved. Input hashes stayed unchanged.\n\n'
    text+='The influence is explained arithmetically by a small ey zero alongside several reference qok events, especially after sh, plus the availability denominator change. This does not establish statistical robustness, a special status for f31r, a general ey blocker, meanings or a grammar/junction mechanism. The inspection is exploratory posthoc, with no p-values, intervals, model fitting or new tests; previous results remain unchanged.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    for p,h in json.loads((R/'PROTOCOL.json').read_text())['hashes'].items():assert sha(p)==h
    save('VERIFICATION.json',dict(status='VERIFIED',raw_EVT_ledger_rows_matched=len(raw_f31),context_local_and_without_effect_checks=checks,eight_strata_preserved=True,weighted_numerator_and_weight_deletion_identities=True,previous_context_and_omission_effects_reproduced=True,all_input_hashes_unchanged=True,inferential_calculations_performed=False))
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
