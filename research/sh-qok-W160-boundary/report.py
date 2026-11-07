from pathlib import Path
import json,html
R=Path(__file__).resolve().parent;s=json.loads((R/'SUMMARY.json').read_text())
rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [r['architecture'],r['scenario'],f"{r['W_range'][0]:.3f}–{r['W_range'][1]:.3f}",str(r['flags'])+'/200',f"{r['wilson95'][0]:.3f}–{r['wilson95'][1]:.3f}",r['pass_gate']])+'</tr>' for r in s['results'])
doc='''<!doctype html><meta charset="utf-8"><title>W160 boundary controls</title><style>body{font:17px/1.55 system-ui;max-width:1200px;margin:40px auto;padding:20px;background:#f8faf7;color:#173c30}td,th{padding:8px;border-bottom:1px solid #c5d4c9;text-align:left}table{border-collapse:collapse}</style><h1>Just above W=160: '''+s['status']+'''</h1>
<p>Rules were frozen before600fresh group layouts and2,400outcomes. Every layout has160&lt;W&lt;161, at least8supported pages and no page exceeding25% of W. Fully blocked strata contribute zero; removing them leaves support unchanged.</p>
<p>The +15-point positive is.20 versus.35 among available followers. Nulls use.2,.6 or additive page/line/position probabilities independent of prefix. Exact availability-pattern conditional scoring and Bonferroni8 remain unchanged. Each layout supplies four independently drawn outcome scenarios; these are paired layouts, not four independent designs.</p>
<table><tr><th>Architecture</th><th>Scenario</th><th>W range</th><th>Flags</th><th>Wilson95</th><th>Gate</th></tr>'''+rows+'''</table>
<p>Positive gates require lower confidence bound≥.80; null upper bounds≤.05. All false flags and missed positives remain in TRIALS.json. Source hashes, exact small-orbit probabilities, support bounds and blocked-support invariance were verified.</p>
<h2>Boundary and scope</h2><p>This closes the previous gap between160 and164.6 for these constructed availability patterns. It does not prove160is minimal, cover every possible value immediately above160, or guarantee power for imbalanced groups, sparse token layouts, arbitrary nuisance interactions or weaker effects. The actual tested range is about160.286–160.763.</p>
<p>These are conditional group fixtures. The test has not passed through the manuscript token extractor here; structural availability is supplied by construction. Source parsing, missingness, H/F alignment and real manuscript coverage remain separate requirements. No manuscript files were read or scored. H/F remain separate.</p>
<p><a href="PROTOCOL.json">Frozen rules</a> · <a href="FREEZE.json">Hashes</a> · <a href="SUMMARY.json">Results</a> · <a href="DESIGNS.json">All layouts</a> · <a href="TRIALS.json">All outcomes</a> · <a href="VERIFICATION.json">Verification</a></p>'''
(R/'report.html').write_text(doc,encoding='utf-8')
assert all((R/f).exists() for f in ['PROTOCOL.json','FREEZE.json','SUMMARY.json','DESIGNS.json','TRIALS.json','VERIFICATION.json'])
for r in s['results']:print(r['architecture'],r['scenario'],r['flags'],r['pass_gate'],r['W_range'])
