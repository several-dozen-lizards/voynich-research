"""Independent audit and presentation of the frozen trial records; no fitting."""
from pathlib import Path
import collections,hashlib,html,json,math
import numpy as np
from scipy import stats

R=Path(__file__).resolve().parent
def read(name):return json.loads((R/name).read_text(encoding='utf-8'))
def esc(v):return html.escape(str(v))
def verify_score(result):
    if result['status']!='SCORED':return 0
    assert not set(result['train_folios'])&set(result['test_folios'])
    sums=collections.defaultdict(list)
    for p in result['heldout']:
        assert p['folio'] in result['test_folios']
        score=(p['y']-p['baseline'])*p['direction'];assert abs(score-p['score'])<1e-12
        sums[p['folio']].append(score)
    assert len(result['heldout'])==result['test_n']
    means=[]
    for f in result['per_folio']:
        mean=sum(sums[f['folio']])/len(sums[f['folio']]);assert abs(mean-f['score'])<1e-12;means.append(mean)
    avg=sum(means)/len(means);sd=math.sqrt(sum((v-avg)**2 for v in means)/(len(means)-1));t=avg/(sd/math.sqrt(len(means))) if sd>1e-15 else 0.
    p=float(stats.t.sf(t,len(means)-1)) if sd>1e-15 else 1.
    assert abs(t-result['t'])<1e-8 and abs(p-result['p'])<1e-10
    baseline_loss=sum(-math.log2(p['baseline'] if p['y'] else 1-p['baseline']) for p in result['heldout'])/len(result['heldout'])
    assert abs(baseline_loss-result['loss'])<1e-10
    assert result['adequate']==(baseline_loss<=result['constant']+.01)
    assert result['flag4']==bool(result['adequate'] and p*4<=.05)
    assert result['flag24']==bool(result['adequate'] and p*24<=.05)
    return len(result['heldout'])

freeze=read('FREEZE.json');assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in freeze['hashes'].items())
assert read('ZERO-FIXTURE.json')['status']=='PASS'
q=read('QUALIFICATION.json');cells=collections.defaultdict(list);audited_events=0
for p in sorted((R/'trials').glob('*.json')):
    record=json.loads(p.read_text());audited_events+=verify_score(record['result'])
    cells[(record['design'],record['regime'])].append(record)
for s in q['cells']:
    rr=cells[s['design'],s['regime']];assert len(rr)==s['n']==100
    k=sum(r['result'].get('flag4',False) for r in rr);assert k==s['flags4']
    phat=k/100;z=stats.norm.ppf(.975);den=1+z*z/100;center=(phat+z*z/200)/den;radius=z*math.sqrt(phat*(1-phat)/100+z*z/(4*10000))/den
    bounds=[max(0,center-radius),min(1,center+radius)];assert np.allclose(bounds,s['wilson95'],atol=1e-12)
    if s['regime'] not in ('weak','strong','tiny'):assert s['required_gate']==(bounds[1]<=.10)
    if s['regime'] in ('weak','strong'):assert s['required_gate']==(bounds[0]>=.80)
    if 'paired_factor24' in s:
        win=sum(r['result'].get('flag24',False) and not r['old_v2']['flag'] for r in rr);lose=sum(r['old_v2']['flag'] and not r['result'].get('flag24',False) for r in rr)
        p=float(stats.binom.sf(win-1,win+lose,.5)) if win+lose else 1.
        assert win==s['paired_factor24']['new_only'] and lose==s['paired_factor24']['old_only'] and abs(p-s['paired_factor24']['p'])<1e-12
failed=[s for s in q['cells'] if s['required_gate'] is False or s.get('paired_factor24',{}).get('required_gate',True) is False]
assert q['manuscript_allowed']==(not failed)
phases=[json.loads(line) for line in (R/'PHASES.jsonl').read_text().splitlines()]
if failed:assert not any(p['phase']=='manuscript_read_start' for p in phases)
audit=dict(status='PASS',trials=sum(len(x) for x in cells.values()),individual_scores=audited_events,all_gates_replayed=True,paired_test_replayed=True,zero_direction_fixture_executed=True,hashes_unchanged=True,failed_attempt_did_not_read_manuscript=bool(failed))
(R/'INDEPENDENT-AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')

parts=['<!doctype html><meta charset="utf-8"><title>Weak sh/ch–qok interaction qualification</title>',
'''<style>body{font:17px/1.6 system-ui;max-width:1200px;margin:40px auto;padding:24px;background:#fafbf7;color:#203b33}h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}td,th{padding:9px;text-align:left;border-bottom:1px solid #ccd7ce}th{background:#e8eee8}.note{background:#eef0e5;padding:18px}a{color:#17604b}</style>''',
f'<h1>Weak sh/ch–qok interaction score: {esc(q["status"])}</h1>',
f'<p>Frozen {esc(freeze["utc"])} before fresh control outcomes. Development used48 old exposed synthetic cases and is separately retained. Earlier failures remain unchanged.</p>',
'<p class="note">One targeted qok-by-distant-context score replaces a broad prediction-gain search. It learns a direction on separate folios and evaluates that direction on testing folios. Grammar, phrase templates, latent registers, and contextual spelling can still be observationally indistinguishable. Synthetic qualification establishes only the authored scope.</p>',
'<p><a href="PROTOCOL.md">Frozen protocol</a> · <a href="FREEZE.json">Hashes</a> · <a href="QUALIFICATION.json">Every gate</a> · <a href="DEVELOPMENT.json">Development including false flags</a> · <a href="INDEPENDENT-AUDIT.json">Independent replay</a> · <a href="PHASES.jsonl">Chronology</a></p>',
'<h2>Required gates and retained failures</h2>',
'<p>Nulls require Wilson95 upper false-flag bound≤.10. Weak (.65 logit interaction) and strong (2.5) positives require lower detection bound≥.80 in every design. Tiny (.35) is descriptive. Unsupported and inadequate trials count as nondetections. Factor4 is the prespecified four-panel family; factor24 remains a sensitivity and paired comparison.</p>',
'<table><tr><th>Folios × events</th><th>Regime</th><th>Flags ×4 /100</th><th>Flags ×24 /100</th><th>Wilson95 ×4</th><th>Adequate</th><th>Gate</th></tr>']
for s in q['cells']:
    gate='descriptive' if s['required_gate'] is None else 'PASS' if s['required_gate'] else 'FAIL'
    parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [f'{s["folios"]} × {s["events_per_folio"]}',s['regime'],s['flags4'],s['flags24'],[round(x,4) for x in s['wilson95']],s['adequate'],gate])+'</tr>')
parts.append('</table>')
paired=[s for s in q['cells'] if 'paired_factor24' in s]
for s in paired:
    pp=s['paired_factor24'];parts.append(f'<h2>Paired comparison at unchanged ×24 correction</h2><p>New score detected {s["flags24"]}/100; old v2 detected {pp["old_detections"]}/100 on the same fresh weak datasets. New-only {pp["new_only"]}; old-only {pp["old_only"]}; exact paired p={pp["p"]:.6g}. Required gate: {"PASS" if pp["required_gate"] else "FAIL"}. This tests sensitivity to the specified interaction generator, not general superiority.</p>')
for s in q['cells']:
    if s['regime']=='strong' and s['required_gate'] is False:
        rr=cells[s['design'],'strong'];p_pass=sum(r['result'].get('p4',1)<=.05 for r in rr)
        parts.append(f'<h2>Strong-control failure diagnosis: design{s["design"]}</h2><p>{p_pass}/100 interaction scores clear ×4, but only{s["adequate"]}/100 nuisance baselines meet the unchanged constant+.01bits adequacy rule. Valid detections={s["flags4"]}/100. A strong score does not override that gate. Failure remains part of the frozen result; no nuisance model or threshold was repaired after these outcomes.</p>')
if failed:
    parts.append(f'<h2>Manuscript remains closed</h2><p>{len(failed)} required cells failed. The frozen protocol therefore blocks every new manuscript fit in this attempt. A sensitivity improvement does not override a specificity, power, or adequacy failure. No scope was narrowed after outcomes.</p>')
else:
    parts.append('<h2>Qualification permits only the frozen application</h2><p>All required controls passed. This does not establish power for actual lexical sparsity, missingness, layout, or latent folio dependence. Any manuscript result must retain these limits and H/F separation.</p>')
if (R/'RESULTS.json').exists():
    results=read('RESULTS.json');parts.append('<h2>Frozen retrospective manuscript application</h2><table><tr><th>Panel</th><th>Train/test events</th><th>Mean score</th><th>Adjusted p ×4</th><th>Adequate</th></tr>')
    for p in results:
        s=p['result'];verify_score(s)
        parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [p['panel'],f'{s.get("train_n")} / {s.get("test_n")}',s.get('mean_score'),s.get('p4'),s.get('adequate')])+'</tr>')
    parts.append('</table><p><a href="RESULTS.json">All results</a>. Supplied prefixes are conditionally predicted from context; these are not translations or causal effects.</p>')
parts.append('<h2>Scope and limits</h2><p>The three layouts approximate earlier event counts but not the empirical distribution of word bodies, gaps, ambiguous readings, page clusters, or nuisance complexity. Student inference over a small number of folios is approximate. The null model does not exhaust junction spelling or phrase copying. A general distant dependency can coexist with a qok-specific interaction. Strong and weak labels refer to frozen logit coefficients, not measured manuscript effects or a universal minimum detectable effect.</p><p><a href="../sh-qok-context-transfer-v1/report.html">Preserved context-transfer failure A</a> · <a href="../sh-qok-context-transfer-v2/report.html">Earlier backoff study and weak-power limitation</a></p>')
(R/'report.html').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps(audit))
