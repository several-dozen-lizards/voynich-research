from pathlib import Path
import json,html,hashlib,collections
import run_suite as engine
P=Path(__file__).resolve().parent
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(n,o): (P/n).write_text(json.dumps(o,indent=2),encoding='utf-8')
def esc(x): return html.escape(str(x))
rows=[json.loads(s) for s in (P/'replicates.jsonl').read_text().splitlines()]
jobs=load(P/'JOBS.json'); assert len(rows)==len(jobs)==900
assert {(r['regime'],r['replicate'],r['seed']) for r in rows}=={tuple(j) for j in jobs}
engine.verify(); freeze=load(P/'FREEZE.json')
assert all(engine.sha(P/n)==v for n,v in freeze['inherited'].items())
assert engine.sha(P.parent/'zodiac-mapping-v84/ANNOTATIONS.json')==freeze['inventory_sha256']
assert all(r['true_key'][7]=='457' for r in rows if 'signal' in r['regime'])
summaries=[]
for regime in engine.REGIMES:
    rr=[r for r in rows if r['regime']==regime]; k=sum(r['p_two_features']<=.05 for r in rr); n=len(rr)
    lo,hi=engine.wilson(k,n)
    if regime=='clean_signal': passed=lo>=.9; gate='lower >=90%'; bound=lo
    elif regime=='noisy_masked_signal': passed=lo>=.8; gate='lower >=80%'; bound=lo
    else: passed=hi<=.1; gate='upper <=10%'; bound=hi
    summaries.append(dict(regime=regime,n=n,flags=k,rate=k/n,lower_one_sided95=lo,upper_one_sided95=hi,gate=gate,gate_bound=bound,passed=passed))
passed=all(r['passed'] for r in summaries)
failures=[r for r in rows if ('signal' in r['regime'])!=(r['p_two_features']<=.05)]
dump('FAILURES.json',failures)
coverage=[]
keys=load(P/'keys.json')
for regime in ['clean_signal','noisy_masked_signal']:
    rr=[r for r in rows if r['regime']==regime]
    coverage.append({'regime':regime,'unique_planted_templates':len({r['true_template'] for r in rr}),'phase_counts':dict(sorted(collections.Counter(r['true_key'][6] for r in rr).items())),'observed_slots_range':[min(r['observed'] for r in rr),max(r['observed'] for r in rr)],'winning_table_diagnostic':dict(collections.Counter(keys[r['winner']][7] for r in rr))})
status={'qualification':'PASS' if passed else 'FAIL','scope':'Section457 signals under unchanged v85 detection search, not unique rule recovery or historical identification','regimes':summaries,'coverage':coverage,'failure_records':len(failures),'all900_retained':True,'v85_scoring_unchanged':True,'v84_inventory_unchanged':True,'development_manuscript_scored':False,'heldout_signs_scored':False,'heldout':['Virgo','Libra','Scorpio','Sagittarius']}
dump('RESULTS.json',status)
dump('AUDIT.json',{'frozen_hashes_verified':True,'inherited_hashes_verified':True,'inventory_hash_verified':True,'all_jobs_unique_complete':True,'all_positive_sources_section457':True,'zero_manuscript_features_loaded_by_runner':True,'reproduction':'python run_suite.py freeze then python run_suite.py run in a fresh directory; existing freeze and outcomes are intentionally protected against overwrite. Existing original paths required.'})
css='body{font:17px/1.55 system-ui;background:#111d25;color:#e6eeee;max-width:1150px;margin:auto;padding:36px}h1,h2{color:#a7e5cb}a{color:#9ed3f5}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}td,th{border:1px solid #455a63;padding:9px;text-align:left}th{background:#243942}.box{background:#263e48;padding:20px;border-left:5px solid #c7ae71}summary{cursor:pointer;color:#b0e6d0}.fail{color:#ffb59e}'
h=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>v86 · Section457 qualification</title><style>'+css+'</style><h1>§457: separate synthetic qualification</h1><p>v86 · 900 fresh trials · Frozen v85 scorer</p>',f'<div class="box"><b>{status["qualification"]}: all seven gates required.</b><br>No development manuscript alignment or held-out sign was scored.</div>', '<h2>What changed—and what stayed frozen</h2><p>The positive controls now come exclusively from §457, the male/female degree table. There are 200 clean signals and 200 with 10% independent flips and 15% missing slots. Each of the five nuisance regimes receives 100 fresh trials. Seeds do not overlap v85.</p><p>The original scoring function is imported unchanged and verified by hash. It still searches all 18,424 distinct patterns from both tables, all admitted traversals and shared offsets. Every one of 199 within-group cyclic-shift nulls repeats that full search. Absolute block-centered correlation, missing-value handling, tie tolerance and the two-feature correction are unchanged. The extra top group retains the same cyclic-shift treatment as v85.</p><p><a href="PROTOCOL.json">Pre-run protocol</a> · <a href="FREEZE.json">Freeze receipt</a> · <a href="JOBS.json">900 frozen jobs/seeds</a> · <a href="run_suite.py">Runner</a> · <a href="../zodiac-qualification-v85/run.py">Original scorer</a> · <a href="AUDIT.json">Audit</a></p><h2>Results</h2><p>Flags mean adjusted p ≤ .05. Each negative must have a one-sided 95% Wilson upper bound ≤10%. Clean-signal detection must have a lower bound ≥90%; noisy/masked detection ≥80%. These are separate per-regime bounds, not simultaneous confidence intervals. Gates were frozen before any v86 simulation; there is no early stopping or seed replacement.</p><table><tr><th>Regime</th><th>Flags / trials</th><th>Relevant bound</th><th>Frozen gate</th><th>Outcome</th></tr>']
for r in summaries: h.append(f'<tr><td>{r["regime"]}</td><td>{r["flags"]}/{r["n"]}</td><td>{r["gate_bound"]:.2%}</td><td>{esc(r["gate"])}</td><td>{"PASS" if r["passed"] else "FAIL"}</td></tr>')
h+=['</table><p>The nuisance controls cover independent draws, ring-specific rates, clustered runs, a common top-of-image layout split, and clustered runs with missing arcs. They do not exhaust all possible layout confounds. Synthetic figures share the development geometry but do not use the observed Voynich feature values or actual ambiguity masks.</p><h2>Preserved failures</h2><p>Every miss and false flag appears below. A suite pass does not erase these cases. <a href="FAILURES.json">Complete failure records</a> · <a href="replicates.jsonl">All 900 records, including generated values and missing slots</a> · <a href="RESULTS.json">Machine-readable summary</a></p><table><tr><th>Regime</th><th>Replicate / seed</th><th>Score</th><th>Adjusted p</th><th>Exception</th></tr>']
for r in sorted(failures,key=lambda r:(r['regime'],r['replicate'])): h.append(f'<tr><td>{r["regime"]}</td><td>{r["replicate"]} / {r["seed"]}</td><td>{r["score"]:.4f}</td><td>{r["p_two_features"]:.3f}</td><td>{"Missed signal" if "signal" in r["regime"] else "False flag"}</td></tr>')
h+=['</table><h2>Coverage and limits</h2><ul>']
for c in coverage: h.append(f'<li>{c["regime"]}: {c["unique_planted_templates"]} distinct planted patterns; {len(c["phase_counts"])} of 30 phases represented; {c["observed_slots_range"]} observed slots. Winning-table counts (diagnostic only): {esc(c["winning_table_diagnostic"])}.</li>')
h+=['</ul><p>The planted patterns are sampled from 1,472 distinct §457 patterns in the admitted family. Passing supports detection under these assumptions. It does not establish a uniquely recoverable traversal, identify figure sex, demonstrate a historical relationship, or validate noisy observations not represented by these generators. No winning synthetic rule is being promoted to a manuscript rule.</p><h2>Ambiguous figures and labels remain unchanged</h2><p>The v84 image inventory is hash-verified unchanged: 179 locations including one uncertain-presence Leo fold point; 177 candidate label anchors and two unresolved anchors; 30 torso and eight enclosure ambiguities. Pigment remains unresolved throughout. Label proximity is not unique ownership. Pisces has only 29 visible figures; neither Pisces nor uncertain Leo is forced into a thirty-degree alignment.</p><p><a href="../zodiac-mapping-v84/report.html">Image map and original exceptions</a> · <a href="../zodiac-mapping-v84/ANNOTATIONS.json">Full unchanged annotation inventory</a> · <a href="../zodiac-qualification-v85/SOURCE-READBACK.txt">Source readback caveats</a> · <a href="../zodiac-qualification-v85/TABLES.json">Frozen source tables</a></p><details><summary>Show all development figure records without alignment scores</summary><table><tr><th>Figure</th><th>Torso</th><th>Enclosure</th><th>Candidate label anchor</th><th>Ambiguity</th></tr>']
ann=load(P.parent/'zodiac-mapping-v84/ANNOTATIONS.json')
for panel in ann:
    for r in panel['rows']: h.append('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in [r['id'],r.get('body'),r.get('enclosure'),r.get('label_anchor'),r.get('ambiguity','')])+'</tr>')
h+=['</table></details><h2>Held-out boundary</h2><p>Virgo, Libra, Scorpio and Sagittarius remain unscored. There are also no development-sign manuscript scores in this run. Any eventual manuscript rule must be selected on development signs, frozen, and carried unchanged to held-out signs. The table transcription still rests on one translated witness, with same-agent image readback rather than an independent second source.</p></html>']
(P/'report.html').write_text('\n'.join(h),encoding='utf-8')
from html.parser import HTMLParser
class QA(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k=='href': assert (P/v).exists(),v
s=(P/'report.html').read_text(encoding='utf-8'); QA().feed(s)
assert s.count('<table')==s.count('</table>')
dump('REPORT-QA.json',{'html_parsed':True,'local_links_exist':True,'tables_balanced':True,'rendered_ui_checked':False})
dump('SHA256SUMS.json',{p.name:engine.sha(p) for p in P.iterdir() if p.is_file() and p.name!='SHA256SUMS.json'})
print(json.dumps(status,indent=2))
