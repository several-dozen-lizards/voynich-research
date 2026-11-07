from pathlib import Path
import json,html
R=Path(__file__).resolve().parent
s=json.loads((R/'SUMMARY.json').read_text());primary=[x for x in s['results'] if x['view']=='exact_body']
rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [x['regime'],str(x['flags'])+'/200',str(x['old_flags'])+'/200',x['not_estimable'],x['pass_gate']])+'</tr>' for x in primary)
doc='''<!doctype html><meta charset="utf-8"><title>Expanded conditional sh → qok null</title><style>body{font:17px/1.55 system-ui;max-width:1050px;margin:40px auto;padding:20px;background:#f7faf8;color:#193c30}td,th{padding:9px;border-bottom:1px solid #c4d4c9;text-align:left}table{border-collapse:collapse}</style><h1>More legal arrangements, same controls</h1>
<p>Frozen synthetic revision. All compatible lines in each page can exchange sh/ch orientations within four preselected, disjoint position pairs. Each line retains its prefix count, each exact position retains its prefix count, and primary matching retains literal word bodies. Qok outcomes remain fixed. This expands beyond isolated four-cell swaps, but is not the entire set of all possible margin-preserving arrangements.</p>
<p>The exact conditional distribution uses integer subset-sum dynamic programming, checked against exhaustive enumeration in 35 small cases. No Monte Carlo p-values or MCMC convergence assumptions. Bonferroni8 retained. Ending families edy/eey/ey/y remain disjoint. Fresh seeds were frozen before outcomes.</p>
<table><tr><th>Primary regime</th><th>Expanded flags</th><th>Old method, same data</th><th>Not estimable</th><th>Gate</th></tr>'''+rows+'''</table>
<p>All 1,800 fresh datasets were evaluated in both views; 3,600 records are preserved. The old method runs on exactly the same generated datasets for descriptive paired comparison. These are not additional independent experiments.</p>
<p>Nuisance gates require Wilson95 upper rejection bound ≤.05; every positive regime requires lower detection bound ≥.80. The small effect is a 15-point increase; strong effects are 45 points. Dense controls have 12 pages ×24 lines; sparse controls have6lines/page and independently varying bodies. These sizes and effects are synthetic, not estimates of manuscript coverage.</p>
<h2>Status: '''+s['status']+'''</h2><p>Any failed gate blocks broad qualification. No manuscript files were opened or rescored. H/F remain separate in any future application. No thresholds or generators changed after outcomes.</p>
<p>The two matching views coincide here because each synthetic body is itself one ending; agreement is not independent replication. This tests the event-level engine, not token parsing, missing-glyph barriers, variable-length source processing or transcription alignment. Conditional exchangeability covers the authored additive-logit nuisance regimes, not arbitrary line-by-position interactions.</p>
<p>If sparse power remains inadequate, the result is a support limitation for this candidate—not evidence against a manuscript association. Further expansion would need its own frozen exact-null checks and fresh power controls.</p>
<p><a href="PROTOCOL.json">Protocol</a> · <a href="FREEZE.json">Freeze hashes</a> · <a href="SUMMARY.json">Results and intervals</a> · <a href="TRIALS.json">All trials</a> · <a href="VERIFICATION.json">Verification</a></p>'''
(R/'report.html').write_text(doc,encoding='utf-8')
for n in ['PROTOCOL.json','FREEZE.json','SUMMARY.json','TRIALS.json','VERIFICATION.json']:assert (R/n).exists()
print(json.dumps(primary,indent=2))
