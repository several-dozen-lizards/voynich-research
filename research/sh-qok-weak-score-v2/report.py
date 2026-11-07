"""Audit stored probabilities and choices independently; never refit a model."""
from pathlib import Path
import ast,collections,hashlib,html,json,math
from datetime import datetime,timezone
import numpy as np
from scipy import stats,optimize

R=Path(__file__).resolve().parent
def read(name):return json.loads((R/name).read_text(encoding='utf-8'))
def esc(x):return html.escape(str(x))
# Reuse only the independently written scalar-score audit function, not its I/O.
tree=ast.parse((R.parent/'sh-qok-weak-score-v1/report.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_score'],type_ignores=[]),'prior_score_audit','exec'),globals())

def audit_nuisance(s,events=None):
    if s['status']!='SCORED':return 0
    c=s['calibration'];n=len(c['learning_events']);y=np.array(c['learning_y']);constant=np.array(c['oof']['constant']);base=float(np.mean(-(y*np.log(constant)+(1-y)*np.log(1-constant))))
    assert n==s['train_n'] and abs(base-c['baseline_cv_loss_nats'])<1e-12
    assert set(c['learning_folios'])==set(s['train_folios'])
    for f in c['assignments']:
        assert set(f['fit_folios'])==set(s['train_folios'])-{f['validation_folio']}
        assert set(f['fit_folios']).isdisjoint(s['test_folios'])
    assert sum(f['validation_events'] for f in c['assignments'])==n
    penalty=(math.log(n)/2+math.log(4))/n;assert abs(penalty-c['penalty_nats'])<1e-12
    choices=[]
    for m in ('P','J','L','F'):
        candidate=np.array(c['oof'][m]);d=candidate-constant
        def derivative(w):
            p=constant+w*d
            return float(np.mean(d*(p-y)/(p*(1-p))))
        w=0. if derivative(0)>=0 else 1. if derivative(1)<=0 else float(optimize.brentq(derivative,0,1,xtol=1e-14))
        p=constant+w*d;gain=base-float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))
        stored=next(q for q in c['candidates'] if q['model']==m)
        expected_weight=w if gain>1/n else 0.
        assert abs(stored['weight']-expected_weight)<1e-8 and abs(stored['gain_nats']-gain)<1e-10
        choices.append((m,expected_weight,gain-penalty))
    best=max(choices,key=lambda x:x[2]);chosen=best[0] if best[2]>0 else 'constant';weight=best[1] if chosen!='constant' else 0.
    assert c['selected']==chosen and abs(c['weight']-weight)<1e-8
    rate=(y.sum()+.5)/(n+1);assert abs(rate-c['full_learning_constant'])<1e-12
    raw=c['selected_raw_probabilities'];assert len(raw)==n+s['test_n']
    for j,p in enumerate(s['heldout']):
        assert abs(p['baseline']-((1-weight)*rate+weight*raw[n+j]))<1e-10
    if events is not None:
        assert y.tolist()==[events[i]['y'] for i in c['learning_events']]
        assert {events[i]['folio'] for i in c['learning_events']}==set(s['train_folios'])
        for p in s['heldout']:
            e=events[p['event']];assert e['folio']==p['folio'] and e['y']==p['y']
    return s['test_n']

freeze=read('FREEZE.json');assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in freeze['hashes'].items())
assert read('SCORE-ENGINEERING.json')['status']=='PASS'
q=read('QUALIFICATION.json');cells=collections.defaultdict(list);nuisance_checked=0;score_checked=0
for p in sorted((R/'trials').glob('*.json')):
    rec=json.loads(p.read_text());score_checked+=verify_score(rec['result']);nuisance_checked+=audit_nuisance(rec['result']);cells[rec['design'],rec['regime']].append(rec)
for s in q['cells']:
    rr=cells[s['design'],s['regime']];assert len(rr)==s['n']==100
    k=sum(r['result'].get('flag4',False) for r in rr);assert k==s['flags4']
    z=stats.norm.ppf(.975);p=k/100;den=1+z*z/100;mid=(p+z*z/200)/den;rad=z*math.sqrt(p*(1-p)/100+z*z/(4*10000))/den;bounds=[max(0,mid-rad),min(1,mid+rad)]
    assert np.allclose(bounds,s['wilson95'],atol=1e-12)
    expected=bounds[1]<=.10 if s['regime'] in ('position','junction','phrase','proxy_phrase','position_proxy','additive_far') else bounds[0]>=.80 if s['regime'] in ('weak','strong') else None
    assert s['required_gate']==expected
    if 'paired_factor24' in s:
        pp=s['paired_factor24'];win=sum(r['result'].get('flag24',False) and not r['old_v2']['flag'] for r in rr);lose=sum(r['old_v2']['flag'] and not r['result'].get('flag24',False) for r in rr)
        pv=float(stats.binom.sf(win-1,win+lose,.5)) if win+lose else 1.
        assert win==pp['new_only'] and lose==pp['old_only'] and abs(pv-pp['p'])<1e-12 and pp['required_gate']==(pv<=.01)
failed=[s for s in q['cells'] if s['required_gate'] is False or s.get('paired_factor24',{}).get('required_gate',True) is False]
assert q['manuscript_allowed']==(not failed)
phases=[json.loads(line) for line in (R/'PHASES.jsonl').read_text().splitlines()]
if failed:assert not any(p['phase']=='manuscript_read_start' for p in phases)
results=read('RESULTS.json') if (R/'RESULTS.json').exists() else []
coverage=[]
if results:
    assert not failed
    old=json.loads((R.parent/'sh-qok-ending-qualification-reed-v94/EVENTS.json').read_text())
    for pi,p in enumerate(results):
        events=read(p['panel']+'-events.json');s=p['result'];verify_score(s);audit_nuisance(s,events)
        expected={(r['locator'],r['index'],r['word']) for r in old if r['panel']==pi};actual={(e['locator'],e['index'],e['word']) for e in events};assert expected==actual
        coverage.append(dict(panel=p['panel'],events=len(events),coverage_matches_v94=True,score_and_nuisance_replayed=True))
audit=dict(status='PASS',audited_at_utc=datetime.now(timezone.utc).isoformat(),trials=sum(len(rr) for rr in cells.values()),individual_scores=score_checked,nuisance_predictions_replayed=nuisance_checked,
           all_gate_decisions_replayed=True,OOF_choices_independently_replayed=True,paired_test_replayed=True,hashes_unchanged=True,
           manuscript_panels=coverage,manuscript_block_was_required=bool(failed),
           manuscript_block_respected=(not failed or not any(p['phase']=='manuscript_read_start' for p in phases)))
(R/'INDEPENDENT-AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')

parts=['<!doctype html><meta charset="utf-8"><title>Nuisance repair qualification</title>',
'''<style>body{font:17px/1.6 system-ui;max-width:1250px;margin:40px auto;padding:24px;background:#fafbf7;color:#203c32}h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%;font-size:14px;margin:24px 0}td,th{text-align:left;padding:9px;border-bottom:1px solid #cbd7cf}th{background:#e6eee7}.note{padding:18px;background:#edf0e3}a{color:#1a624b}</style>''',
f'<h1>Nuisance-predictor repair: {esc(q["status"])}</h1><p>Frozen {esc(freeze["utc"])}. Prior failed attempt and all pass/fail thresholds preserved.</p>',
'<p class="note">Only the nuisance estimator changes: leave-one-learning-folio-out predictions select one raw model blended with constant, using a prespecified one-parameter/finite-choice penalty. The honest testing split, interaction score, support, adequacy, correction and required confidence bounds remain unchanged. A passing synthetic study is bounded methodological qualification, not grammar or semantics.</p>',
'<p><a href="PROTOCOL.md">Frozen repair</a> · <a href="FREEZE.json">Hashes</a> · <a href="QUALIFICATION.json">All gates</a> · <a href="INDEPENDENT-AUDIT.json">Independent probability/choice replay</a> · <a href="PHASES.jsonl">Chronology</a> · <a href="../sh-qok-weak-score-v1/report.html">Preserved failed weak-score v1</a></p>',
'<h2>Fresh controls: unchanged gates</h2><p>Null Wilson95 upper rejection bound≤.10; weak and strong lower detection bound≥.80 in every design. Adequacy remains testing loss≤learning-rate constant+.01bits/event. Tiny power is descriptive. Every inadequate or unsupported positive counts as a nondetection. No design is dropped after failure.</p>',
'<table><tr><th>Folios × events</th><th>Regime</th><th>Flags ×4 /100</th><th>Flags ×24 /100</th><th>Adequate /100</th><th>Wilson95 ×4</th><th>Gate</th></tr>']
for s in q['cells']:
    gate='descriptive' if s['required_gate'] is None else 'PASS' if s['required_gate'] else 'FAIL'
    parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [f'{s["folios"]} × {s["events_per_folio"]}',s['regime'],s['flags4'],s['flags24'],s['adequate'],[round(x,4) for x in s['wilson95']],gate])+'</tr>')
parts.append('</table>')
for s in q['cells']:
    if 'prior_weak_v1_diagnostic' in s:
        prior=s['prior_weak_v1_diagnostic'];parts.append(f'<h2>Same fresh strong cases, old versus repaired nuisance</h2><p>Repaired: {s["adequate"]}/100 adequate and{s["flags4"]}/100 valid detections. Unchanged weak-score v1: {prior["adequate"]}/100 adequate and{prior["flags4"]}/100 valid detections. This paired diagnosis is reported without introducing another pass threshold.</p>')
    if 'paired_factor24' in s:
        pp=s['paired_factor24'];parts.append(f'<h2>Same ×24 correction on fresh weak cases</h2><p>Repair: {s["flags24"]}/100 detections; old context-transfer v2: {pp["old_detections"]}/100. New-only{pp["new_only"]}; old-only{pp["old_only"]}; exact paired p={pp["p"]:.6g}. Existing p≤.01 gate: {"PASS" if pp["required_gate"] else "FAIL"}.</p>')
if failed:parts.append(f'<h2>Manuscript stays closed</h2><p>{len(failed)} required cells failed. No manuscript scoring is permitted or performed in this attempt. All failures remain retained; no threshold or scope was relaxed.</p>')
else:parts.append('<h2>Qualification passed for the stated synthetic scope</h2><p>All original required gates pass. This permits the frozen four-panel application only. Uniform synthetic layouts do not establish power or calibration for every empirical body distribution, lexical dependency, missingness pattern, or latent folio effect.</p>')
if results:
    parts.append('<h2>Frozen retrospective manuscript application</h2><p>A zero learned direction is uninformative: its stored p=1 is a computational default, not evidence for absence. An inadequate nuisance baseline also blocks interpretation. Remote vocabulary counts are descriptive coverage diagnostics, not newly selected tests or changed thresholds.</p><table><tr><th>Panel</th><th>Learn/test events</th><th>Learn/test folios</th><th>Nuisance choice</th><th>Far columns</th><th>Mean score</th><th>p ×4</th><th>Adequate</th><th>Screen</th></tr>')
    for p in results:
        s=p['result'];cal=s.get('calibration',{});selected=cal.get('selected','—');weight=cal.get('weight')
        ncols=sum(len(v) for v in s.get('vocab',{}).values());zero=bool(s.get('heldout')) and all(x['direction']==0 for x in s['heldout'])
        screen='uninformative: zero direction' if zero else 'inadequate baseline' if s.get('adequate') is False else 'PASS' if s.get('flag4') else s['status'] if s['status']!='SCORED' else 'no pass'
        vals=[p['panel'],f'{s.get("train_n")} / {s.get("test_n")}',f'{len(s.get("train_folios",[]))} / {len(s.get("test_folios",[]))}',selected+(f' ({weight:.3f})' if weight is not None else ''),ncols,s.get('mean_score'),'uninformative (stored1)' if zero else s.get('p4'),s.get('adequate'),screen]
        parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in vals)+'</tr>')
    parts.append('</table><p><a href="RESULTS.json">Every result and exclusion</a> · <a href="APPLICATION-DIAGNOSTICS.json">Feature support and nuisance failures</a>. Each panel has event, source-line and score JSON files. Complete nuisance receipts include OOF predictions, model weights, selection cost, raw/final probabilities, learned direction and per-folio scores.</p>')
parts.append('<h2>Interpretation limits</h2><p>A positive screen is conditional dependence beyond a specified nuisance predictor, not proof that position, spelling, phrases or latent registers are exhausted. Constant fallback can meet the adequacy rule while still omitting meaningful local structure. The t procedure is approximate and relies on independent testing folios and score calibration. Actual event counts approximate the synthetic sizes but not their four-body vocabulary or uniform layouts. H/F are alternative readings, not independent manuscripts. Grammar and variable-slot templates may generate identical text. A negative screen cannot exclude smaller or differently represented dependencies.</p>')
if results:
    qualified=sum(p['result'].get('flag4',False) for p in results);inadequate=sum(p['result'].get('adequate') is False for p in results)
    parts.insert(3,f'<p class="note"><b>Control qualification is separate from the manuscript outcome.</b> Qualifying manuscript panels: {qualified}/4. Inadequate nuisance baselines: {inadequate}/4. Zero-direction panels are uninformative; their stored p=1 is not a negative finding. All failures and unchanged thresholds are retained.</p>')
(R/'report.html').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps(audit))
