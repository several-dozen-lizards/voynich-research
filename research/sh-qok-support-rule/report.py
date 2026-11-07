from pathlib import Path
import json,html
R=Path(__file__).resolve().parent;s=json.loads((R/'SUMMARY.json').read_text())
rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [r['lines'],r['layout'],r['scenario'],r['admitted'],r['flags'],round(r['V_median'],2),r['status']])+'</tr>' for r in s['results'])
doc='''<!doctype html><meta charset="utf-8"><title>Minimum-support qualification</title><style>body{font:16px/1.55 system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f8faf7;color:#173c30}td,th{padding:8px;border-bottom:1px solid #c4d4c9;text-align:left}table{border-collapse:collapse}</style><h1>Proposed minimum-support rule: '''+s['status']+'''</h1>
<p>Frozen before 1,600 fresh synthetic datasets. No manuscript files opened or rescored; H/F remain separate. The proposed threshold is not proven to be the smallest sufficient threshold.</p>
<p>For each group of n discordant rows, with k sh forms in the left position, define support Vg=k(n−k)/n. Admit only if total V≥80, at least8 pages contribute, and no page supplies more than25% of V. Matching and eligibility use bodies, coordinates and prefix margins only, never following-qok outcomes. This measures available prefix reassignment, not observed qok variation.</p>
<p>The target is a +15-percentage-point local association at baseline .2 or .6, using the existing exact null and Bonferroni8. It is not a claim of sensitivity to arbitrarily small effects. Two null scenarios are tested: homogeneous and additive page/line/position variation.</p>
<table><tr><th>Lines/page</th><th>Layout</th><th>Scenario</th><th>Admitted/100</th><th>Flags among admitted</th><th>Median V</th><th>Gate</th></tr>'''+rows+'''</table>
<p>Each admitted cell requires at least50 accepted datasets. Positive-cell Wilson95 lower power bound must be≥.80; null upper false-flag bound must be≤.10. Zero admissions is excluded scope, not evidence of absence. 1–49 admissions is insufficient qualification. Rejected datasets remain in TRIALS.json and are not scored.</p>
<p>Do not turn this support rule into a semantic or grammatical test. Even sufficient power would establish sensitivity only for the authored conditional effects. Real parsing, missing tokens, different line lengths, broader vocabulary and transcription alignment are untested. No manuscript application is authorized by these results.</p>
<p>The implementation exposes support(a,b) without an outcome argument. The repeated-call check after creating complemented outcomes confirms determinism; structural exclusion of qok is the main safeguard. The exact test itself is reused unchanged from its frozen source. All historical failed controls remain untouched.</p>
<p><a href="PROTOCOL.json">Frozen rule and gates</a> · <a href="FREEZE.json">Hashes</a> · <a href="SUMMARY.json">Results and confidence intervals</a> · <a href="TRIALS.json">Every dataset</a> · <a href="VERIFICATION.json">Verification</a></p>'''
(R/'report.html').write_text(doc,encoding='utf-8')
assert all((R/f).exists() for f in ['PROTOCOL.json','FREEZE.json','SUMMARY.json','TRIALS.json','VERIFICATION.json'])
print(json.dumps(s,indent=2))
