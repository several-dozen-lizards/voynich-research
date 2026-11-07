from pathlib import Path
import json,html
R=Path(__file__).resolve().parent
rows=''
for mode in ['ch','both']:
 s=json.loads((R/mode/'SUMMARY.json').read_text())
 for r in s['results']:
  rows+='<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [mode,r['scenario'],str(r['flags'])+'/200',round(r['mean_observed_gap'],4),r['pass_gate']])+'</tr>'
doc='''<!doctype html><meta charset="utf-8"><title>ch and joint feasibility boundaries</title><style>body{font:17px/1.55 system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f8faf7;color:#173c30}td,th{padding:8px;border-bottom:1px solid #c5d4c9;text-align:left}table{border-collapse:collapse}</style><h1>Both boundary challenges FAIL specificity</h1>
<p>Both protocols were frozen before fresh outcomes. Each constructed200accepted layouts with V≈82.286 and four target bodies. At the ch boundary availability is34–40/336 after ch and134–140/336 after sh. At the joint boundary it is34–40/336 after ch and84–90/336 after sh. Artificial chx blockers remain fixed.</p>
<table><tr><th>Boundary</th><th>Scenario</th><th>Flags</th><th>Mean matched gap</th><th>Gate</th></tr>'''+rows+'''</table>
<h2>The failure is meaningful, but name it precisely</h2><p>The nominal null generators choose qok independently of prefix among available followers. However, masks are sampled conditional on different availability counts for ch and sh. That creates a real unconditional association through availability. The current reference null does not preserve that relationship. These are nuisance-only false alarms for a claim beyond availability, not false positives under an actual no-association null.</p>
<p>For constant available-follower qok probability p, the induced matched gap is p×(f_sh−f_ch). The observed null gaps follow this prediction: roughly.06/.18 for the ch boundary and.03/.09 for the joint boundary. Thus high detection does not demonstrate a direct sh-dependent choice. The calibrated positive targets.15, but it cannot rescue specificity.</p>
<p>Sampling masks within prefix classes supplies accepted boundary cases efficiently. It is not independent-mask sampling, and the frozen reports explicitly retain that distinction. These controls expose an architecture the earlier sh-boundary success did not cover. They do not retroactively change that run's numbers, but they block generalizing its qualification.</p>
<p>All1,600outcomes and400layouts are retained, including every failure. Existing exact scoring and Bonferroni8 were unchanged. A later candidate would need to condition on structural follower availability or define an available-follower estimand and test its resulting support/power. That revision has not been made here.</p>
<p>No manuscript files were read or scored. H/F remain separate. This is a synthetic limitation of the joint rule, not a finding about Voynich grammar or the absence of its local association.</p>
<p><a href="ch/PROTOCOL.json">ch frozen protocol</a> · <a href="both/PROTOCOL.json">Joint frozen protocol</a> · <a href="ch/SUMMARY.json">ch results</a> · <a href="both/SUMMARY.json">Joint results</a> · <a href="ch/TRIALS.json">ch trials</a> · <a href="both/TRIALS.json">Joint trials</a> · <a href="ch/DESIGNS.json">ch layouts</a> · <a href="both/DESIGNS.json">Joint layouts</a></p>'''
(R/'report.html').write_text(doc,encoding='utf-8')
for mode in ['ch','both']:
 for n in ['PROTOCOL.json','SUMMARY.json','TRIALS.json','DESIGNS.json','VERIFICATION.json']:assert (R/mode/n).exists()
print('Report saved; local links verified.')
