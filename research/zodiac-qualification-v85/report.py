from pathlib import Path
import json, math, html, hashlib, time
P=Path(__file__).resolve().parent
def read(n): return json.loads((P/n).read_text(encoding='utf-8'))
def esc(v): return html.escape(str(v))
rows=[json.loads(s) for s in (P/'replicates.jsonl').read_text().splitlines()]
protocol=read('PROTOCOL.json'); tables=read('TABLES.json'); search=read('SEARCH.json')
assert len(rows)==280, 'Do not present unfinished suite as complete'
def wilson(k,n):
    z=1.96; c=(k/n+z*z/(2*n))/(1+z*z/n); h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n)
    return [round(c-h,4),round(c+h,4)]
summary=[]
for regime in protocol['regimes']:
    rr=[r for r in rows if r['regime']==regime]; k=sum(r['p_two_features']<=.05 for r in rr)
    positive='signal' in regime; limit=36 if regime=='clean_signal' else 32 if positive else 4
    summary.append(dict(regime=regime,n=len(rr),flags=k,wilson95=wilson(k,len(rr)),pass_gate=k>=limit if positive else k<=limit,gate=('>=' if positive else '<=')+str(limit)))
passed=all(r['pass_gate'] for r in summary)
status={'qualification':'PASS within frozen synthetic suite' if passed else 'FAIL; manuscript alignment remains closed','regimes':summary,'voynich_alignment_scored':False,'heldout_signs_scored':False,'heldout_signs':['Virgo','Libra','Scorpio','Sagittarius'],'source_verified':'Two visual readbacks of one Wright1934 scan, not independent textual witness','transcribed_rows':24,'each_row_degrees':30,'raw_candidates':search['raw'],'unique_candidates':search['unique']}
coverage=[]
for regime in ['clean_signal','noisy_masked_signal']:
    for table in ['457','458']:
        rr=[r for r in rows if r['regime']==regime and search['keys'][r['true_template']][7]==table]
        coverage.append({'regime':regime,'table':table,'n':len(rr),'detected':sum(r['p_two_features']<=.05 for r in rr)})
status['planted_table_coverage']=coverage
(P/'RESULTS.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
ann=json.loads((P.parent/'zodiac-mapping-v84/ANNOTATIONS.json').read_text(encoding='utf-8'))
frozen=read('FREEZE.json'); assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in frozen['sha256'].items())
audit={'freeze_hashes_unchanged':True,'all_24_rows_sum_30':all(len(t[k])==30 for t in tables.values() for k in ['457_degrees','458_degrees']),'all_280_seeded_records_present':len(rows)==280,'all_scores_bounded':all(-1e-6<=r['score']<=1.000001 for r in rows),'no_real_feature_input_in_simulation':'run.py uses only synthetic shapes and historical tables; annotations loaded only by this report','clean_signal_scores_min':min(r['score'] for r in rows if r['regime']=='clean_signal'),'annotation_sha256':hashlib.sha256((P.parent/'zodiac-mapping-v84/ANNOTATIONS.json').read_bytes()).hexdigest()}
(P/'AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
css='body{font:17px/1.55 system-ui;background:#101820;color:#e2e9eb;margin:0 auto;max-width:1180px;padding:36px}h1,h2{color:#a4e2cc}a{color:#93cef0}table{border-collapse:collapse;width:100%;margin:20px 0;font-size:14px}td,th{padding:9px;border:1px solid #43545e;text-align:left;vertical-align:top}th{background:#243640}code{white-space:pre-wrap}.callout{background:#293e48;padding:18px;border-left:5px solid #c0ab73}summary{cursor:pointer;color:#a4e2cc}img{max-width:100%}.fail{color:#ffba9f}.pass{color:#a4e2cc}'
h=['<!doctype html><meta charset="utf-8"><title>v85 · Degree-table qualification</title><style>'+css+'</style><h1>Degree tables: transcription & synthetic qualification</h1><p>v85 · 23 October 2026 · Historical scheme, no manuscript alignment scores</p>',f'<div class="callout"><b>{esc(status["qualification"])}</b><br>Held-out Virgo, Libra, Scorpio and Sagittarius remain unscored. No development-sign feature alignment was run either.</div>', '<h2>What was transcribed</h2><p>§457 male/female runs and §458 brightness runs, all twelve signs: 24 rows, 30 degrees each. Two visual readings of the same Wright scan, with enlarged inspection of the faint Aries d8. This verifies the numeric tables and operative legend; it is not a diplomatic transcription of all surrounding prose or an independent Arabic-source audit.</p><p><a href="SOURCE-READBACK.txt">Readback and normalization notes</a> · <a href="TABLES.json">Run and degree data</a> · <a href="../zodiac-mapping-v84/wright-pdf-63.png">§457 scan</a> · <a href="../zodiac-mapping-v84/wright-pdf-64.png">§458 scan</a> · <a href="table458-detail.png">Enlarged table</a></p><p>F marks starred entries in §457; M marks unstarred entries. In §458: b brilliant, L luminous, d dusky, s dark/shadowed, v void. Adjacent same-category runs remain exactly as printed. Table sex is not inferred figure sex. Wright’s surrounding text itself emphasizes disagreement among schemes.</p><table><tr><th>Sign</th><th>§457 runs</th><th>§458 runs</th></tr>']
for s,t in tables.items(): h.append(f'<tr><td>{s}</td><td>{t["457_runs"]}</td><td>{t["458_runs"]}</td></tr>')
h+=['</table><h2>Frozen scoring</h2><p>Four eligible synthetic sign shapes: Aries, Taurus, Gemini, Cancer (120 slots). Pisces has 29 visible figures; Leo has an unresolved fold figure, so neither is forced into a thirty-slot model. Six binary traversal choices × 30 shared offsets × 16 table/category hypotheses = 30,720 candidates; 18,424 distinct patterns after exact deduplication. No per-sign offset fitting.</p><p>The score is absolute correlation after centering within each panel/ring. Every one of 199 cyclic-shift nulls repeats the full search. Missing values move with their ring sequence and remain missing; observed-slot means and norms are recalculated. A further factor of two reserves correction for garment and enclosure tests. Pigment and text labels are not scored.</p><p><a href="PROTOCOL.json">Frozen protocol</a> · <a href="FREEZE.json">Pre-run hashes/time</a> · <a href="SEEDS.json">Seeds</a> · <a href="run.py">Reproduction code</a> · <a href="replicates.jsonl">All outcomes, including failures</a> · <a href="AUDIT.json">Audit</a></p><h2>Qualification outcomes</h2><p>Forty fresh replicates per regime. Gates frozen before execution: no more than 4 false flags per negative regime; at least 36 clean signals and 32 noisy/masked signals detected. All seven gates must pass. Intervals below are 95% Wilson intervals on the flag rate; forty trials give only coarse calibration.</p><table><tr><th>Regime</th><th>Flags / 40</th><th>95% interval</th><th>Gate</th><th>Result</th></tr>']
for r in summary:
    lo,hi=r['wilson95']; h.append(f'<tr><td>{r["regime"]}</td><td>{r["flags"]}</td><td>{lo:.1%}–{hi:.1%}</td><td>{r["gate"]}</td><td>{"PASS" if r["pass_gate"] else "FAIL"}</td></tr>')
h+=['</table><details open><summary>Preserved misses and false flags</summary><table><tr><th>Regime</th><th>Replicate / seed</th><th>Score</th><th>Adjusted p</th><th>Exception</th></tr>']
for r in rows:
    positive='signal' in r['regime']; flagged=r['p_two_features']<=.05
    if positive!=flagged:
        h.append(f'<tr><td>{r["regime"]}</td><td>{r["replicate"]} / {r["seed"]}</td><td>{r["score"]:.4f}</td><td>{r["p_two_features"]:.3f}</td><td>{"Missed planted signal" if positive else "False flag"}</td></tr>')
h+=['</table></details><p>The clean-signal miss at seed 855015 has score approximately 1 but adjusted p=.21: a perfect fit alone does not distinguish it from shifted alternatives. Detection is not unique rule recovery; this experiment does not measure whether a winning traversal is identifiable.</p><table style="display:none">']
h+=['</table><p>Positive templates were sampled uniformly from distinct candidate patterns, not balanced by source table. The pooled gate therefore does not separately qualify each historical table or every category mapping. Coverage:</p><ul>']
for c in coverage: h.append(f'<li>{c["regime"]}, §{c["table"]}: {c["detected"]}/{c["n"]} detected.</li>')
h+=['</ul><table style="display:none">']
h+=['</table><p>Negatives: independent binary draws; different ring frequencies; clustered runs; a common image-top layout split; and clustered runs with fixed missing arcs. Positives: an exact rule drawn from the frozen family, then the same family with 10% independent flips and 15% missing slots. Positive controls measure recovery under the assumed model, not historical plausibility. These controls do not exhaust possible layout confounds, nor test the empirical ambiguity masks.</p><h2>Ambiguity remains part of the record</h2><p>The unchanged v84 inventory contains 179 locations (one uncertain-presence fold location), 177 candidate label anchors and two unresolved anchors, 30 torso ambiguities and eight enclosure ambiguities. All star-pigmentation classifications remain unresolved. Label adjacency is a candidate association, not established ownership. The inventory was frozen before the table was read; it was created by the same agent, not an independent annotator.</p><p><a href="../zodiac-mapping-v84/report.html">Original image map and overlays</a> · <a href="../zodiac-mapping-v84/ANNOTATIONS.json">Unchanged full inventory</a></p><details><summary>All development records, including uncertain features and labels</summary><table><tr><th>Figure</th><th>Torso</th><th>Enclosure</th><th>Label</th><th>Ambiguity</th></tr>']
for panel in ann:
    for r in panel['rows']:
        h.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [r['id'],r.get('body'),r.get('enclosure'),str(r.get('label_anchor'))+'; '+r.get('label_association',''),r.get('ambiguity','')])+'</tr>')
h+=['</table></details><h2>Boundary for the next step</h2><p>No historical match is claimed. Passing this suite would justify considering a separately frozen development fit, with one rule carried unchanged to whole held-out signs. A failed gate keeps that application closed. No synthetic winner has been chosen as a manuscript rule, and no figure ambiguity has been resolved using these tables.</p>']
(P/'report.html').write_text('\n'.join(h),encoding='utf-8')
manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.iterdir() if f.is_file() and f.name!='SHA256SUMS.json'}
(P/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(status,indent=2))
