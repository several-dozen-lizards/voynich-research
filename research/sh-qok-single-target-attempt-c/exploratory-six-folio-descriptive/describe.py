"""Descriptive effects only. No inferential calculations or gate decisions."""
from pathlib import Path
from collections import defaultdict, Counter
from fractions import Fraction
from datetime import datetime, timezone
import json,csv,hashlib,sys

R=Path(__file__).resolve().parent
C=R.parent
sys.path.insert(0,str(C))
import engine

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def summarize(rows,folios):
    strata=defaultdict(lambda:[0,0,0,0])
    for v in rows:
        j=0 if v['x'] else 1
        z=strata[v['folio'],v['family']];z[j]+=1;z[j+2]+=v['y']
    terms={pg:[Fraction(0),Fraction(0),Fraction(0)] for pg in folios};details=[]
    for (pg,f),(ns,nc,a,b) in sorted(strata.items()):
        v=Fraction(ns*nc,ns+nc)
        sr=v*Fraction(a,ns) if ns else Fraction(0);cr=v*Fraction(b,nc) if nc else Fraction(0)
        terms[pg][0]+=sr;terms[pg][1]+=cr;terms[pg][2]+=v
        details.append(dict(folio=pg,family=f,sh=ns,ch=nc,sh_qok=a,ch_qok=b,comparison_available=bool(ns and nc),V=float(v)))
    def record(selected):
        sr=sum((terms[p][0] for p in selected),Fraction(0));cr=sum((terms[p][1] for p in selected),Fraction(0));V=sum((terms[p][2] for p in selected),Fraction(0))
        delta=(sr-cr)/V if V else None
        rr=[v for v in rows if v['folio'] in selected]
        return dict(eligible_origins=len(rr),sh=sum(v['x'] for v in rr),ch=sum(1-v['x'] for v in rr),
            matched_strata=sum(z['comparison_available'] for z in details if z['folio'] in selected),V=float(V),
            matched_sh_qok_percent=float(100*sr/V) if V else None,matched_ch_qok_percent=float(100*cr/V) if V else None,
            effect_points=float(100*delta) if delta is not None else None,exact_effect_points=str(100*delta) if delta is not None else None,
            direction='higher after sh' if delta is not None and delta>0 else 'higher after ch' if delta is not None and delta<0 else 'equal' if delta is not None else 'no matched comparison',
            explanation=None if V else 'No eligible sh/ch pair within any folio x ending-family stratum; no descriptive matched effect can be computed.')
    per=[dict(folio=p,**record([p])) for p in folios]
    return dict(aggregate=record(folios),per_folio=per,strata=details,directions=dict(Counter(v['direction'] for v in per)))

def main():
    assert not (R/'PROTOCOL.json').exists(), 'Preserve prior output.'
    membership=json.loads((C/'PANELS.json').read_text())
    folios=sorted(v['folio'] for v in membership['freshness_audit'] if v['panel']=='P1' and not v['prior_runs']['v75']['scored_sh_qok'] and not v['prior_runs']['v77']['scored_sh_qok'])
    assert len(folios)==6
    sources=json.loads((C/'PROTOCOL.json').read_text())['sources']
    source=next(Path(p) for p in sources if 'text16e6' in p);metadata=next(Path(p) for p in sources if 'Davis-hands' in p)
    for p,h in sources.items():assert sha(Path(p))==h
    for n in ['EVENTS.csv','PANELS.json','engine.py']:
        assert sha(C/n)==json.loads((C/'DELIVERY-MANIFEST.json').read_text())['files'][n]
    save('PROTOCOL.json',dict(classification='EXPLORATORY (E), descriptive only',utc=datetime.now(timezone.utc).isoformat(),folios=folios,
        authorization='User requested subset descriptive H1 effect sizes and per-folio directions with H/F separate, no p-values and no pass/fail claim.',
        estimand='Same Mantel-Haenszel risk difference as attempt C: stratum folio x ending family; w=ns*nc/(ns+nc); effect=100*sum(w*(a/ns-b/nc))/sum(w). Unsupported strata have weight0. Per-folio effects use that same formula across families on each page. Subset aggregate weights folios by their summed w, not equally.',
        reporting='Report matched effect and both matched next-qok rates, sh/ch counts, matched strata, support weight and direction. No inference, confidence interval, significance calculation, power calculation or threshold relaxation. A missing matched effect is not zero.',
        freshness='Six folios outside listed v75/v77 sh-qok searches, but already included in scored attempt C; subset analysis requested after aggregate outcome and support check. Not fresh held-out evidence.',
        hashes={str(p):sha(p) for p in [Path(__file__),C/'engine.py',C/'EVENTS.csv',C/'PANELS.json',source,metadata]}))
    meta={r['Folio']:r for r in csv.DictReader(metadata.open(encoding='utf-8-sig'))}
    lines=[r for r in engine.parse(source,meta) if r['panel']=='P1' and r['folio'] in folios]
    events,ex,ledger=engine.extract(lines,True)
    result={}
    # Reparse the original raw source, then check every event against the separately saved attempt-C ledger.
    old=[r for r in csv.DictReader((C/'EVENTS.csv').open(encoding='utf-8',newline='')) if r['cell'].startswith('P1-') and r['folio'] in folios]
    assert len(old)==len(ledger)
    expected={(r['cell'],r['line'],r['position']):r for r in old}
    for r in ledger:
        oldrow=expected[r['cell'],r['line'],str(r['position'])]
        for key in ['origin','follower','family','exclusion_reason','outcome']:
            actual='' if r[key] is None else str(r[key]);assert actual==oldrow[key],(key,r)
    for tr in ['H','F']:
        cell='P1-'+tr
        ev=[v for v in events if v['cell']==cell];res=summarize(ev,folios)
        prior=[r for r in old if r['cell']==cell and not r['exclusion_reason']]
        independent=defaultdict(lambda:[0,0,0,0])
        for v in prior:
            i=0 if v['origin'].startswith('sh') else 1;z=independent[v['folio'],v['family']];z[i]+=1;z[2+i]+=int(v['outcome'])
        num=Fraction(0);den=Fraction(0);page=defaultdict(lambda:[Fraction(0),Fraction(0)])
        for (pg,f),(ns,nc,a,b) in independent.items():
            if not ns or not nc:continue
            w=Fraction(1,Fraction(1,ns)+Fraction(1,nc));term=Fraction(a*nc-b*ns,ns+nc)
            num+=term;den+=w;page[pg][0]+=term;page[pg][1]+=w
        exact=100*num/den if den else None
        assert str(exact)==res['aggregate']['exact_effect_points']
        floating=engine.page_effects(ev)
        for r in res['per_folio']:
            n,d=page[r['folio']];other=100*n/d if d else None
            assert (str(other) if other is not None else None)==r['exact_effect_points']
            fp=floating.get(r['folio'],[0,0]);assert abs(float(d)-fp[1])<1e-10
            if d:assert abs(float(other)-100*fp[0]/fp[1])<1e-10
        result[tr]=dict(classification='EXPLORATORY (E), descriptive only',**res,exclusions=dict(ex.get(cell,{})))
    save('DESCRIPTIVE.json',result)
    with (R/'STRATA.csv').open('w',encoding='utf-8',newline='') as f:
        rows=[dict(reading=tr,**r) for tr,res in result.items() for r in res['strata']]
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (R/'EVENTS.csv').open('w',encoding='utf-8',newline='') as f:
        fields=list(dict.fromkeys(k for r in ledger for k in r));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(ledger)
    save('VERIFICATION.json',dict(status='VERIFIED',source_ledger_rows_checked=len(ledger),eligible_events_checked=len(events),raw_source_and_saved_ledger_agree=True,exact_rational_aggregate_and_per_folio_effects_agree=True,floating_attempt_C_effect_formula_agrees=True,inferential_calculations_performed=False))
    def fmt(x):return 'not available' if x is None else f'{x:+.2f}'
    text='EXPLORATORY (E) — descriptive H1 effects on six P1 folios\n\n'
    text+='Same next-qok comparison as attempt C, stratified by folio x ending family. Effects are percentage points, sh minus ch. H/F are separate readings of the same manuscript. No p-values, confidence intervals, or inferential decision are calculated.\n\n'
    text+='| Reading | Matched rate after sh | Matched rate after ch | Difference (points) | Eligible sh / ch | Matched strata |\n|---|---:|---:|---:|---:|---:|\n'
    for tr,res in result.items():
        a=res['aggregate'];text+=f"| {tr} | {a['matched_sh_qok_percent']:.2f}% | {a['matched_ch_qok_percent']:.2f}% | {fmt(a['effect_points'])} | {a['sh']} / {a['ch']} | {a['matched_strata']} |\n"
    text+='\n| Folio | H difference (points) | H direction | F difference (points) | F direction |\n|---|---:|---|---:|---|\n'
    for h,f in zip(result['H']['per_folio'],result['F']['per_folio']):text+=f"| {h['folio']} | {fmt(h['effect_points'])} | {h['direction']} | {fmt(f['effect_points'])} | {f['direction']} |\n"
    text+='\n'
    for tr,res in result.items():text+=tr+' directions: '+', '.join(f'{v} {k}' for k,v in res['directions'].items())+'.\n\n'
    text+='Matched rates use identical harmonic-exposure weights w=ns*nc/(ns+nc) for each sh/ch comparison within ending family and folio. Their difference is the requested Mantel-Haenszel risk difference. The aggregate is weighted by comparison support, not an equal-folio average. Single-prefix strata are retained in the inventory but contribute zero weight. These are not raw pooled next-qok rates.\n\n'
    text+='F f85r2 has no eligible origins; F f86v3 has only three eligible ch origins and no sh origins. Their matched effects are unavailable, not zero. Other small per-folio comparisons are descriptive and can be unstable; STRATA.csv and DESCRIPTIVE.json preserve all counts and weights.\n\n'
    text+='These six pages were outside the listed historical searches, but already contributed to attempt C. The subset was requested after its aggregate outcome and support audit were known. This is exploratory description, not fresh held-out confirmation. The earlier support limitations are unchanged. No testing thresholds were relaxed and no new inference was performed.\n\n'
    text+='Every subset event was reparsed from the original EVT and matched to the saved attempt-C ledger. Independent exact-rational calculations reproduced every aggregate/per-folio effect and agreed with the original floating-point formula. See VERIFICATION.json.\n'
    (R/'REPORT.md').write_text(text,encoding='utf-8')
    save('MANIFEST.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='MANIFEST.json'}))
    print(json.dumps({tr:dict(aggregate=res['aggregate'],per_folio=[{k:v for k,v in r.items() if k in ['folio','effect_points','direction','sh','ch','V']} for r in res['per_folio']],directions=res['directions']) for tr,res in result.items()},indent=2))

if __name__=='__main__':main()
