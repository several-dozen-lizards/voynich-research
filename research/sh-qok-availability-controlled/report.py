from pathlib import Path
import json,html,statistics
R=Path(__file__).resolve().parent;rows='';coverage=[]
for mode in ['sh','ch','both']:
 s=json.loads((R/mode/'SUMMARY.json').read_text());tr=json.loads((R/mode/'TRIALS.json').read_text())
 for r in s['results']:
  rr=[x for x in tr if x['scenario']==r['scenario']]
  vals=[mode,r['scenario'],str(r['flags'])+'/200',round(statistics.median(x['V'] for x in rr),2),sum(x['not_estimable'] for x in rr),r['pass_gate']]
  rows+='<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in vals)+'</tr>'
 coverage.append(dict(boundary=mode,median_newV=statistics.median(x['V'] for x in tr),notestimable=sum(x['not_estimable'] for x in tr)))
doc='''<!doctype html><meta charset="utf-8"><title>Availability-controlled qualification</title><style>body{font:17px/1.55 system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f8faf7;color:#173c30}td,th{padding:8px;border-bottom:1px solid #c5d4c9;text-align:left}table{border-collapse:collapse}</style><h1>Availability control fixes these false alarms; power fails</h1>
<p>Three revisions were frozen before outcomes.600fresh accepted boundary layouts,2,400outcomes retained. No manuscript files read; H/F remain separate.</p>
<p>Each existing exact-body discordant group is split by its ordered pair of follower-availability flags. Prefix orientations can only rearrange within the same availability pattern. This preserves each line's counts, exact-position margins and prefix-availability margins. The resulting exact subset-sum null therefore cannot explain away availability differences by moving prefixes across incompatible patterns.</p>
<table><tr><th>Boundary</th><th>Scenario</th><th>Flags</th><th>Median conditional V</th><th>Not estimable</th><th>Gate</th></tr>'''+rows+'''</table>
<p>All nine null cells meet the frozen95% upper false-flag bound≤.05. All three positive cells fail the required lower power bound≥.80. Broad qualification FAILS. The source-layout V≈82.29 describes the old support; it does not qualify the newly partitioned conditional test. Some remaining support may sit in both-blocked groups and carry no outcome information.</p>
<h2>The target changed for a reason</h2><p>The planted positive is now qok probability.20 after ch versus.35 after sh among AVAILABLE matched followers. The old15-point aggregate difference could be produced by unequal availability alone; it is not a valid positive target for isolating direct choice beyond availability. Thus these power rates are not a like-for-like comparison with the older aggregate-effect successes.</p>
<p>Every exact small-orbit subset calculation was checked before simulation. Pattern-specific assignment counts are preserved by construction. Frozen sources and histories remain intact. The reused SUMMARY field mean_observed_gap is the old aggregate matched descriptive gap, not the new available-follower estimand; the protocol defines the planted conditional effect.</p>
<p>These are authored balancedfour-body layouts with fixed chx blockers. Availability is known structurally in the generators; that does not establish how to infer it in a manuscript. The surviving null behavior is finite synthetic evidence, not a universal validity theorem. A further candidate needs power at the new conditional support and effect target before any manuscript application.</p>
<p>All rejected masks, nondetections and false flags remain in the per-boundary records. No manuscript scoring or threshold relaxation occurred.</p>
<p><a href="sh/PROTOCOL.json">sh protocol</a> · <a href="ch/PROTOCOL.json">ch protocol</a> · <a href="both/PROTOCOL.json">Joint protocol</a> · <a href="sh/TRIALS.json">sh trials</a> · <a href="ch/TRIALS.json">ch trials</a> · <a href="both/TRIALS.json">Joint trials</a> · <a href="sh/SUMMARY.json">sh results</a> · <a href="ch/SUMMARY.json">ch results</a> · <a href="both/SUMMARY.json">Joint results</a></p>'''
(R/'report.html').write_text(doc,encoding='utf-8');(R/'CONDITIONAL-SUPPORT.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
for mode in ['sh','ch','both']:
 for name in ['PROTOCOL.json','SUMMARY.json','TRIALS.json','FREEZE.json','VERIFICATION.json']:assert (R/mode/name).exists()
print(json.dumps(coverage))
