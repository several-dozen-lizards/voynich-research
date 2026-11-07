"""Presentation and independent saved-prediction audit; does not refit models."""
from pathlib import Path
import collections, hashlib, html, itertools, json, math
import numpy as np

R=Path(__file__).resolve().parent
def read(name):return json.loads((R/name).read_text(encoding='utf-8'))
def esc(x):return html.escape(str(x))
def fmt(x):return '—' if x is None else f'{x:.5f}'
q=read('QUALIFICATION.json');frozen=read('FREEZE.json')
integrity=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in frozen['hashes'].items())
assert integrity
panels=read('RESULTS.json') if (R/'RESULTS.json').exists() else []
audit=[]
for panel in panels:
    label=panel['panel'];ev=read(label+'-events.json')
    if panel['status']!='SCORED':continue
    pp=read(label+'-predictions.json');fm=read(label+'-folds.json')
    assert len(ev)==len(pp)
    for i,(e,p) in enumerate(zip(ev,pp)):
        assert p['fold']==fm[e['folio']]
        tr=[a for a in ev if fm[a['folio']]!=p['fold']]
        expected=(e['context']['-1'],e['body'],e['context']['1']) not in {(a['context']['-1'],a['body'],a['context']['1']) for a in tr}
        assert p['novel']==expected
        for m,prob in p['probability'].items():
            loss=-math.log2(prob if e['y'] else 1-prob)
            assert abs(loss-p['loss'][m])<1e-10
    for s in panel['scores']:
        high,low=s['contrast'].split('-');ii=[i for i,p in enumerate(pp) if s['view']=='all' or p['novel']]
        by=collections.defaultdict(list)
        for i in ii:by[ev[i]['folio']].append(pp[i]['loss'][low]-pp[i]['loss'][high])
        gain=float(np.mean([np.mean(v) for v in by.values()])) if by else None
        assert (gain is None and s['gain_bits'] is None) or abs(gain-s['gain_bits'])<1e-12
        assert len(ii)==s['n'] and len(by)==s['folios']
        if s['supported'] and len(by)<=18:
            a=[float(np.mean(v)) for v in by.values()]
            tail=sum(sum(x*y for x,y in zip(sign,a))/len(a)>=gain-1e-12 for sign in itertools.product((-1,1),repeat=len(a)))/(2**len(a))
            assert abs(tail-s['p'])<1e-12
    audit.append(dict(panel=label,events=len(ev),probabilities_checked=sum(len(p['probability']) for p in pp),novelty_replayed=True,all_gains_replayed=True,exact_sign_tails_independently_replayed=True))
(R/'REPORT-AUDIT.json').write_text(json.dumps(dict(status='PASS',frozen_unchanged=integrity,panels=audit),indent=2),encoding='utf-8')

parts=['<!doctype html><meta charset="utf-8"><title>sh/ch–qok context transfer</title>',
'''<style>body{font:17px/1.6 system-ui;max-width:1180px;margin:40px auto;padding:24px;background:#fafbf8;color:#203930}h1,h2{line-height:1.2}table{border-collapse:collapse;font-size:14px;width:100%;margin:22px 0}td,th{text-align:left;padding:9px;border-bottom:1px solid #ccd6cf}th{background:#e8eee8}a{color:#19604a}.note{padding:16px;background:#eef1e7}code{font-size:14px}</style>''',
'<h1>Can the sh/ch–qok relationship exceed local writing and phrases?</h1>',
'<p>Frozen retrospective predictive comparison. H/F and bathing/starred panels remain separate. No meanings assigned.</p>',
f'<p><b>Qualification: {esc(q["status"])}</b>. Freeze time: {esc(frozen["utc"])}. Frozen hashes remain unchanged.</p>',
'<p class="note">A grammar-like rule and a variable-slot phrase template can generate identical observations. The saved equal-output control verifies this directly. A gain from distant context can reject the specified bounded local predictor; it cannot uniquely establish grammar. G also includes additive distant predictors, so G−L is not an isolated test of a qok-by-context interaction.</p>',
'<p><a href="PROTOCOL.md">Frozen protocol</a> · <a href="FREEZE.json">Hashes</a> · <a href="PHASES.jsonl">Chronology</a> · <a href="IDENTIFIABILITY.json">Equal-output control</a> · <a href="QUALIFICATION.json">All qualification gates</a></p>',
'<h2>Qualification before manuscript fitting</h2>',
'<p>60 fresh datasets per regime, 16 synthetic folios ×48 events. The full fivefold fitting, scoring, and ×24 correction is reused. Controls are authored logistic mechanisms, not known historical grammar. Small-effect and novel-frame power are descriptive, not qualified. Dense controls cannot establish sensitivity on sparse manuscript support.</p>',
'<table><tr><th>Regime</th><th>View</th><th>Supported</th><th>G−L flags /60</th><th>Wilson95</th><th>Mean bits</th><th>Required gate</th></tr>']
for s in q['results']:
    parts.append('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in [s['regime'],s['view'],s['supported'],s['flags'],[round(v,4) for v in s['wilson95']],fmt(s['mean_gain']),'descriptive' if s['required_gate'] is None else 'PASS' if s['required_gate'] else 'FAIL'])+'</tr>')
parts.append('</table>')
ladder=[]
for regime in ('position','junction','phrase','distant_strong','distant_small'):
    files=sorted((R/'synthetic').glob(regime+'-*.json'))
    for view in ('all','novel'):
        for contrast in ('J-P','L-J','G-L'):
            ss=[next(s for s in json.loads(p.read_text())['scores'] if s['view']==view and s['contrast']==contrast) for p in files]
            ladder.append(dict(regime=regime,view=view,contrast=contrast,n=len(ss),supported=sum(s['supported'] for s in ss),flags=sum(s['flag'] for s in ss),mean_gain=float(np.mean([s['gain_bits'] for s in ss]))))
(R/'CONTROL-LADDER.json').write_text(json.dumps(ladder,indent=2),encoding='utf-8')
parts.append('<p><a href="CONTROL-LADDER.json">All three model contrasts on every control regime</a>. Every synthetic prediction is retained in the synthetic/ directory with its fixed seed.</p>')
if not panels:
    parts.append('<h2>Manuscript not scored</h2><p>A required qualification failed, or manuscript fitting has not been run. This is not a null result about Voynich. All synthetic files and original frozen code are retained; no threshold or source definition was revised.</p>')
else:
    parts.extend(['<h2>Held-out manuscript results</h2>',
    '<p>P = body/position; J adds written junctions; L adds exact local words and a masked five-word frame; G adds context at offsets ±3/±4. Positive gain favors the larger model. Novel means the immediate (left word, body, right word) frame was absent from that fold’s training data. All splits group numbered folios. These are new fitting holdouts on previously explored manuscript material.</p>',
    '<p>Sign-randomization p-values are model-comparison diagnostics with symmetry/folio-independence assumptions and overlapping CV training. ×24 correction covers only this frozen study. Baseline adequacy compares token-weighted loss with a training-rate constant; gains weight folios equally. Unsupported comparisons are retained without significance scores.</p>',
    '<table><tr><th>Panel</th><th>View</th><th>Contrast</th><th>Events / folios</th><th>Gain bits</th><th>Adjusted p</th><th>Baseline adequate</th><th>Screen</th></tr>'])
    for p in panels:
        if not p['scores']:parts.append(f'<tr><td>{esc(p["panel"])}</td><td colspan="7">NOT ESTIMABLE; {p["events"]} events</td></tr>')
        for s in p['scores']:
            cells=[p['panel'],s['view'],s['contrast'],f'{s["n"]} / {s["folios"]}',fmt(s['gain_bits']),fmt(s['p_adjusted']),s['baseline_adequate'],'PASS' if s['flag'] else 'not estimable' if not s['supported'] else 'no pass']
            parts.append('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in cells)+'</tr>')
    parts.append('</table>')
    for p in panels:
        parts.append(f'<h2>{esc(p["panel"])} details</h2><p>{p["events"]} eligible origins, {p["folios"]} numbered folios. Exclusions: <code>{esc(p["excluded"])}</code>. <a href="{p["panel"]}-events.json">Every event</a> · <a href="{p["panel"]}-source-lines.json">Source lines</a></p>')
        if p['status']=='SCORED':
            parts.append(f'<p><a href="{p["panel"]}-predictions.json">Every held-out probability and loss</a> · <a href="{p["panel"]}-folds.json">Folio split</a></p><pre>'+esc(json.dumps(p.get('qok_diagnostics',{}),indent=2))+'</pre>')
    parts.append('<p><a href="RESULTS.json">All scores, constant-baseline losses, per-folio gains, and failures</a> · <a href="REPORT-AUDIT.json">Independent saved-probability and novelty replay</a></p>')
parts.append('<h2>Limits that remain</h2><p>These model classes do not exhaust position, junction spelling, copying, or phrases. Prediction of a supplied prefix from surrounding text is conditional analysis, not left-to-right text generation. Local-model failure can mean sparse vocabulary, missing interactions, or regularization error. Longer templates, latent registers, and context-sensitive orthography can mimic an extended relation. A negative extended-context result cannot establish absence of grammar, particularly where power or novel-frame coverage is weak. No reserved zodiac material was opened.</p>')
(R/'report.html').write_text('\n'.join(parts),encoding='utf-8')
print('Report and independent audit written.')
