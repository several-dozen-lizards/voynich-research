"""Add count-based interpretation receipts; preserve frozen analysis definitions."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json,csv,hashlib

R=Path(__file__).resolve().parent;V=R.parent/'sh-qok-context-map-v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def main():
    assert not (R/'FINDINGS.json').exists()
    for p,h in json.loads((R/'FREEZE.json').read_text())['hashes'].items():assert sha(p)==h
    families=json.loads((R/'FAMILY-ROWS.json').read_text());cells=json.loads((R/'PREDICTIONS.json').read_text())
    raw=[r for r in csv.DictReader((V/'EVENTS.csv').open(encoding='utf-8',newline='')) if r['context']=='C3' and not r['exclusion_reason']]
    counts=Counter((r['reading'],r['folio'],r['family'],r['prefix']) for r in raw)
    examples=[]
    for r in raw:
        if r['family']=='eey' and r['follower'].startswith('qok'):
            ns=counts[r['reading'],r['folio'],'eey','sh'];nc=counts[r['reading'],r['folio'],'eey','ch']
            assert not(ns and nc)
            examples.append({k:r[k] for k in ['reading','folio','line','position','origin','follower','prefix','family','available']}|dict(stratum_sh_events=ns,stratum_ch_events=nc,matched_comparison_weight=0))
    assert Counter(r['reading'] for r in examples)=={'H':3,'F':2}
    with (R/'ROSETTES-EEY-QOK-EVENTS.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(examples[0]));w.writeheader();w.writerows(examples)
    restros=[]
    for reading in ['H','F']:
        for fam in ['eey','ey']:
            r=next(v for v in families if v['context']=='C3' and v['reading']==reading and v['view']=='all' and v['family']==fam)
            restros.append(dict(reading=reading,family=fam,qok=r['pooled_qok'],events=r['events'],MH_effect_points=r['MH_effect_points'],V=r['V']))
    actual_descriptive=[]
    for c in cells:
        a,b=c['blocked_group'],c['comparison_group']
        actual_descriptive.append(dict(context=c['context'],reading=c['reading'],view=c['view'],posthoc=c['posthoc'],known_origin=c['known_origin'],formal_estimable=c['prediction_a_estimable'],
            raw_lower_rate_observed=a['pooled_qok_rate']<b['pooled_qok_rate'] if a['pooled_qok_rate'] is not None and b['pooled_qok_rate'] is not None else None,
            ey_eey_qok=a['pooled_qok'],ey_eey_events=a['events'],comparison_qok=b['pooled_qok'],comparison_events=b['events']))
    save('FINDINGS.json',dict(classification='RETROSPECTIVE DESCRIPTIVE; no inferential claims',
        correction='Rosettes eey MH0 reflects qok-free supported strata, not absence of qok after every eey origin. Actual qok events are in single-prefix strata and have zero MH weight.',
        Rosettes_counts=restros,ey_eey_pooled_rate_descriptions=actual_descriptive,
        headline='No non-posthoc context is estimable under the frozen per-individual-family20-event rule in either reading/view. N/A with denominator0 is not 0% or a failed prediction.',
        conclusion='The combined ey/eey categorical blocking idea is not supported by these counts. Lower pooled rates occur in C2/C3 but are not general; C5/C6/C7 show the opposite descriptive direction in both readings/views. C1/C4 are posthoc and also mostly opposite. Do not advance a general blocking rule from this check. Formal predictions for sparse non-posthoc contexts remain unscored, not negative tests.',
        sensitivity='Zero-qok removal is outcome-selected denominator reduction; it cannot by itself establish a substantive difference or validate a blocking mechanism.'))
    text=(R/'REPORT.md').read_text(encoding='utf-8')
    text+='\n## Count audit: the origin story needs correction\n\n'
    text+='Rosettes eey has three qok followers among15 events in H (2/9 after sh,1/6 after ch), and two among10 events in F (2/6 after sh,0/4 after ch). Every one is on a folio/family stratum with only one prefix represented, so none contributes to the matched MH comparison. The supported eey strata are qok-free. The aggregate eey MH difference is therefore exactly0 despite nonzero qok followers in the family as a whole. ROSETTES-EEY-QOK-EVENTS.csv identifies all five reading-specific receipts.\n\n'
    text+='Rosettes ey has0/25 qok followers in each reading. That is a local observed zero; it does not establish an exception-free manuscript rule. Zero MH must not be used as a shortcut for zero events.\n\n'
    text+='## Descriptive scope of the proposed blocking pattern\n\n'
    text+='The two combined-family pooled rates are lower in C2/C3. They are higher in C5/C6/C7 in both readings and both views. The most direct sizable non-discovery examples are hand1 botanical C6 and hand1 recipes C7:\n\n'
    text+='| Context | Reading | View | eey+ey qok/events | eey+ey rate | edy+y+other qok/events | Comparison rate |\n|---|---|---|---:|---:|---:|---:|\n'
    for c in cells:
        if c['context'] not in ['C6','C7']:continue
        a,b=c['blocked_group'],c['comparison_group']
        text+=f"| {c['context']} | {c['reading']} | {c['view']} | {a['pooled_qok']}/{a['events']} | {100*a['pooled_qok_rate']:.2f}% | {b['pooled_qok']}/{b['events']} | {100*b['pooled_qok_rate']:.2f}% |\n"
    text+='\nThese are direct descriptive rate contrasts, not scored predictions: edy is below20 events in C6/C7, so the frozen individual-family estimability rule prevents either from entering the requested headline. No non-posthoc context is fully estimable; the headline is N/A (denominator0), not0% and not a failed test. No thresholds were relaxed to create a denominator.\n\n'
    text+='The broad combined ey/eey blocking idea should not be promoted from these retrospective observations. The narrower ey zero on the six Rosettes remains local and exploratory. Formal non-posthoc predictions remain unscored because of the frozen support rule; the descriptive exceptions and original count correction are preserved rather than hidden behind that rule. No future prospective protocol was silently established.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    verification=json.loads((R/'VERIFICATION.json').read_text());verification['Rosettes_eey_qok_event_receipts_checked']=len(examples);verification['Rosettes_eey_qok_receipts_all_in_single_prefix_strata']=True
    save('VERIFICATION.json',verification)
    save('DELIVERY-MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='DELIVERY-MANIFEST.json'}))
    print(json.dumps(dict(status='VERIFIED',Rosettes_counts=restros,nonposthoc_headline_denominator=0,primary_inputs_unchanged=True),indent=2))

if __name__=='__main__':main()
