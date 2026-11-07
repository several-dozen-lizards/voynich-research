from pathlib import Path
import json,html
R=Path(__file__).resolve().parent
s=json.loads((R/'SUMMARY.json').read_text())
audit={'secondary_ending_family_valid':False,'reason':'Implementation grouped eey with ey instead of keeping the frozen disjoint ending families. Secondary results are invalid and retained as a failure. Exact-body primary uses literal bodies and is unaffected.','scope':'Synthetic event-level engine tested; no corpus tokenizer or H/F loader exercised. Full manuscript pipeline remains unqualified.','action':'No post-outcome code repair or manuscript rescore.'}
(R/'AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [x['regime'],f"{x['flags']}/200",x['not_estimable'],f"{x['wilson95'][0]:.3f}–{x['wilson95'][1]:.3f}",x['criterion_pass']])+'</tr>' for x in s['results'] if x['view']=='exact_body')
text='''<!doctype html><meta charset="utf-8"><title>Position-controlled sh → qok qualification</title><style>body{max-width:1000px;margin:40px auto;padding:20px;font:17px/1.55 system-ui;background:#f8faf7;color:#19372d}td,th{padding:9px;border-bottom:1px solid #ccd7ce;text-align:left}table{border-collapse:collapse}a{color:#176c52}</style>
<h1>Position control helps, but qualification fails</h1>
<p>Rules and fresh seeds were frozen before 1,200 synthetic datasets. Each was scored in two views with 1,999 conditional draws and Bonferroni8. No Voynich text was read or rescored. H/F remain separate in the prospective plan.</p>
<p>The primary comparison conditions on page, exact source-line length, exact interior index and exact body after sh/ch. Prefix labels are permuted conditional on each stratum's margins; following-qok outcomes stay fixed. Only strata with both prefixes contribute. The score averages page-level weighted differences.</p>
<table><tr><th>Primary exact-body regime</th><th>Flags</th><th>Not estimable</th><th>Wilson95 flag rate</th><th>Frozen criterion</th></tr>'''+rows+'''</table>
<p>Nuisance gates required the false-flag interval's upper bound ≤.05; the local positive required a detection lower bound ≥.80. No-overlap required all datasets to be not estimable. Intervals describe these authored generators, not the manuscript.</p>
<h2>What failed</h2><p>A shared line-level setting raises both sh prevalence and following-qok prevalence without direct dependence between them conditional on that setting. Exact position matching still compares across lines, so it cannot remove this cause. Its high rejection rate is a failure of mechanism specificity, not a numerical failure or proof of grammar. Sparse nonoverlap is explicitly unresolved.</p>
<p>The page-only control must also meet its exact frozen confidence gate; a near-threshold result is retained as a failure rather than rounded into a pass. The entire qualification stops when any primary gate fails.</p>
<h2>Implementation exception retained</h2><p>The secondary ending-family implementation incorrectly merged eey with ey. Those secondary results are invalid. Exact-body primary retains the literal body and is unaffected. No post-outcome repair was made. All 2,400 records remain available, including invalid secondary diagnostics.</p>
<p>This tests a synthetic event-level statistical engine, not the complete transcription parser. The next candidate would need to preserve line-level prefix composition as well as position, with fresh calibration and power checks for the resulting sparse comparisons. It has not been selected or run. Existing manuscript findings remain retrospective associations under their older nulls.</p>
<p><a href="PROTOCOL.json">Frozen rules</a> · <a href="FREEZE.json">Hashes</a> · <a href="SUMMARY.json">All summaries</a> · <a href="TRIALS.json">All trials</a> · <a href="VERIFICATION.json">Verification</a> · <a href="AUDIT.json">Implementation exception</a></p>'''
(R/'report.html').write_text(text,encoding='utf-8')
assert all((R/p).exists() for p in ['PROTOCOL.json','FREEZE.json','SUMMARY.json','TRIALS.json','VERIFICATION.json','AUDIT.json'])
print(json.dumps([x for x in s['results'] if x['view']=='exact_body'],indent=2))
