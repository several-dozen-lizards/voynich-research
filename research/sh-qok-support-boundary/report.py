from pathlib import Path
import json,html
R=Path(__file__).resolve().parent;s=json.loads((R/'SUMMARY.json').read_text())
rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [r['layout'],r['scenario'],str(r['flags'])+'/'+str(r['n']),f"{r['wilson95'][0]:.3f}–{r['wilson95'][1]:.3f}",r['not_estimable'],r['pass_gate']])+'</tr>' for r in s['results'])
doc='''<!doctype html><meta charset="utf-8"><title>Support boundary qualification</title><style>body{font:17px/1.55 system-ui;max-width:1050px;margin:40px auto;padding:20px;background:#f8faf7;color:#173c30}td,th{padding:9px;border-bottom:1px solid #c5d4ca;text-align:left}table{border-collapse:collapse}</style><h1>Just above V=80: '''+s['status']+'''</h1>
<p>Frozen before fresh outcomes. Only datasets with80≤V&lt;84, at least8supported pages and no page supplying more than25% of support are accepted. Every attempted design and rejection remains recorded. Qok outcomes are generated only after support selection.</p>
<p>Each of two layouts has200 accepted iid-prefix designs tested with four independently drawn outcome scenarios, plus200 accepted additive-nuisance designs. Within a layout the four iid scenarios reuse prefix designs: their results are paired, not independent replications. Seed formula and attempted seeds are saved; streams across generator families are not asserted mutually independent.</p>
<table><tr><th>Layout</th><th>Scenario</th><th>Flags</th><th>Wilson95</th><th>Not estimable</th><th>Gate</th></tr>'''+rows+'''</table>
<p>Positive scenarios add15 percentage points to qok probability after sh, at baseline.2 or.6. Each requires a95% lower power bound≥.80. Null scenarios require a95% upper false-positive bound≤.05, stricter than the earlier support test. The additive null includes page, line and position variation. Exact conditional p-values and Bonferroni8 are unchanged.</p>
<p>Every result, including failed cells, is retained. A pass supports only the tested narrow band, effect sizes and synthetic layouts. It does not prove that80 is the smallest sufficient threshold, guarantee detection of weaker effects or arbitrary alternatives, or establish support in the manuscript. The event-level engine does not qualify source parsing or H/F alignment.</p>
<p>Voynich remained closed. H/F remain separate in any future protocol; no manuscript scoring was performed or authorized by this result.</p>
<p><a href="PROTOCOL.json">Frozen rules</a> · <a href="FREEZE.json">Hashes</a> · <a href="SUMMARY.json">Results</a> · <a href="TRIALS.json">Accepted trials</a> · <a href="ATTEMPTS.json">All support attempts</a> · <a href="VERIFICATION.json">Verification</a></p>'''
(R/'report.html').write_text(doc,encoding='utf-8')
assert all((R/f).exists() for f in ['PROTOCOL.json','FREEZE.json','SUMMARY.json','TRIALS.json','ATTEMPTS.json','VERIFICATION.json'])
print(json.dumps(s,indent=2))
