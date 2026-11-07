"""Consolidate existing reports only. No statistical engines are imported or run."""
from pathlib import Path
import datetime,hashlib,html,json
R=Path(__file__).resolve().parent;P=R.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=P/'sh-qok-context-map-v3';b=P/'sh-qok-ending-blocking-v3-2'
v31=load(a/'VERIFICATION.json');v32=load(b/'DELIVERY-MANIFEST.json')
checks=[]
for name,h in v31['delivery_hashes'].items():checks.append(dict(package='v3.1',file=str(a/'delivery'/name),sha256=h,match=sha(a/'delivery'/name)==h))
for name,h in v32['hashes'].items():checks.append(dict(package='v3.2',file=str(b/name),sha256=h,match=sha(b/name)==h))
assert all(x['match'] for x in checks)
reports={'v3.1':(a/'delivery/REPORT.md').read_text(encoding='utf-8'),'v3.2':(b/'REPORT.md').read_text(encoding='utf-8')}
save('SOURCE-RECEIPTS.json',dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),delivery_checks=checks,original_reports_unchanged=True,activity='Consolidation of existing results only'))
# Update only stale coordination fields; preserve originals and compare bytes before writing.
changes=[]
for path,field,value in [
 (a/'FOLLOWUP-STATUS.json','v3_2','LOCATED AND REPORTED: ../sh-qok-ending-blocking-v3-2/ORIGINAL-AMENDMENT.md and REPORT.md; descriptive only, non-posthoc headline NOT ESTIMABLE; no new run.'),
 (P/'v103-qualification-v104/PARKED.json','v3_3_2','Located and descriptively reported in ../sh-qok-ending-blocking-v3-2/; consolidated at ../v3-complete-handoff/report.html. v103 remains PARKED; no resumption authorized.')]:
 before=path.read_bytes();old=json.loads(before.decode('utf-8-sig'));snapshot=path.parent.name+'-'+path.name+'.before.json'
 if not (R/snapshot).exists():(R/snapshot).write_bytes(before)
 new=dict(old);new[field]=value
 if path.name=='FOLLOWUP-STATUS.json':new['complete_v3_handoff']='../v3-complete-handoff/report.html — v3.1 and descriptive v3.2 consolidated; calibration follow-up separate.'
 assert path.read_bytes()==before,'Concurrent coordination edit; preserve and retry deliberately'
 path.write_text(json.dumps(new,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 changes.append(dict(file=str(path),before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=sha(path),fields=[field]+(['complete_v3_handoff'] if path.name=='FOLLOWUP-STATUS.json' else [])))
assert load(P/'v103-qualification-v104/PARKED.json')['status']=='PARKED_BY_USER'
save('COORDINATION-UPDATES.json',changes)
status=dict(status='V3_REPORTING_CONSOLIDATED_WITH_AMENDMENTS_3_1_AND_3_2',classification='RETROSPECTIVE; H/F separate; original qualification failures retained',v3_1='Reported and sealed; starred both-reading pass, P1 H-only; other qualification blocks retained',v3_2='Reported and sealed descriptive ending-family audit; non-posthoc headline not estimable; no inferential claim',qualification_followup='Separate active workstream at sh-qok-qualification-followup-v1; no automatic upgrade of v3.1 results',v4='Separate image-context workstream; not an amendment3.2 substitute',v103='PARKED; explicit decision required before any resumption',Rosettes='No new leave-out grids',new_statistics='NONE',original_analysis_files_modified=False)
save('STATUS.json',status)
e=html.escape
body='''<p>VOYNICH · CONSOLIDATED v3 HANDOFF</p><h1>v3, with Amendments 3.1 and 3.2</h1><p class="notice"><strong>RETROSPECTIVE — text exposed or uncertified.</strong> Existing reports consolidated; no new calculation, control, power test, manuscript score or Rosettes grid. H/F remain separate. v103 remains PARKED.</p>
<h2>Amendment 3.1: what remains supported</h2><table><tr><th>Cell</th><th>H</th><th>F</th><th>Headline</th></tr><tr><td>Starred, hand3</td><td>PASS; +12.3 points</td><td>PASS; +11.4 points</td><td>Availability alone does not explain this retrospective association</td></tr><tr><td>P1</td><td>PASS</td><td>BLOCKED: null qualification</td><td>No both-reading headline</td></tr><tr><td>Bath, hand2</td><td>BLOCKED: null qualification</td><td>BLOCKED: null qualification</td><td>Qualification failures, not negative manuscript results</td></tr><tr><td>Currier A and heterogeneity questions</td><td>Qualification blocks retained</td><td>Qualification blocks retained</td><td>No inferential conclusion</td></tr><tr><td>Exact-body W sensitivity</td><td>UNSUPPORTED</td><td>UNSUPPORTED</td><td>Cannot rescue or overturn the primary</td></tr></table>
<p>Values and decisions above are inherited from the sealed v3.1 report. Its full effects, intervals, correction, controls and failures are retained below. No existing blocked cell is promoted.</p>
<h2>Amendment 3.2: ending-family descriptive check</h2><p>The amendment was found and completed; it is not the v4 image-context spec. The pre-check found prior ending-family outcome breakdowns in C1 bath and C4 starred, so those contexts are excluded from its headline counts. C3 is the known exploratory origin.</p><p>Under the frozen requirement that each individual ending family has at least20 events, no non-posthoc context is fully estimable. The requested headline is <strong>N/A, denominator0</strong> in H/F and both follower views—not0%, and not a negative statistical test. Descriptive exceptions remain visible: pooled ey/eey rates are higher, rather than lower, in C5/C6/C7 in both readings and views. No broad blocking claim follows.</p>
<h3>The origin correction must travel with the handoff</h3><table><tr><th>Rosettes ending</th><th>H qok/events</th><th>F qok/events</th><th>Meaning of matched MH0</th></tr><tr><td>eey</td><td>3/15</td><td>2/10</td><td>qok events lie in single-prefix strata and contribute zero matched comparison weight</td></tr><tr><td>ey</td><td>0/25</td><td>0/25</td><td>Local observed zero only; no manuscript-wide prohibition</td></tr></table><p>Zero matched effect must not be used as a shortcut for zero observed followers. The supplied 3.2 report preserves the five reading-specific eey receipts and all family rows.</p>
<h2>Completion and separate work</h2><ul><li>Both amendment reports are now linked here, with their original delivery hashes checked.</li><li>The stale “3.2 missing” coordination field is corrected. Previous status files are preserved as snapshots; the v103 marker still says PARKED.</li><li>The calibration follow-up and B-Q2 diagnostic are separate, currently active work. Their eventual report cannot silently replace v3.1’s qualification status. An inconclusive or failed follow-up is reportable.</li><li>The v4 image-context packet and registration/agreement work are separate. This handoff does not authorize ratings, joins or tests.</li><li>Completion of this reporting task does not authorize resuming v103. No further Rosettes leave-out grids.</li></ul>
<p>No additional analysis is required to report the existing v3/3.1/3.2 outcomes. Original analysis code, frozen sources, event files and sealed reports were not changed. Only stale coordination metadata was updated.</p>
<h2>Primary reports and receipts</h2><p><a href="../sh-qok-context-map-v3/delivery/REPORT.md">Sealed v3.1 report</a> · <a href="../sh-qok-ending-blocking-v3-2/ORIGINAL-AMENDMENT.md">Original Amendment3.2</a> · <a href="../sh-qok-ending-blocking-v3-2/REPORT.md">Completed v3.2 report</a> · <a href="../sh-qok-ending-blocking-v3-2/ROSETTES-EEY-QOK-EVENTS.csv">eey event receipts</a> · <a href="SOURCE-RECEIPTS.json">Delivery hash audit</a> · <a href="COORDINATION-UPDATES.json">Exact metadata changes</a> · <a href="STATUS.json">Completion status</a> · <a href="../sh-qok-qualification-followup-v1/REPORT.md">Separate follow-up protocol/diagnosis</a></p>'''
for label,text in reports.items():body+='<details><summary>Full original '+e(label)+' report (verbatim text)</summary><pre>'+e(text)+'</pre></details>'
body+='<p>Snapshot of reporting status while other research chats remain active. Browser appearance unreviewed. No mechanism, meaning or translation claim.</p>'
style='<style>body{max-width:1200px;margin:auto;padding:30px;background:#f5f2e9;color:#203f35;font:17px/1.6 system-ui}h1{font-size:32px;line-height:1.2}h2{margin-top:32px}.notice{background:#e0e9d8;padding:16px}table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #bac9bb}a{color:inherit}details{margin:24px 0}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,monospace}</style>'
(R/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Complete v3 reporting handoff · 3.1 and3.2</title>'+style+'<main>'+body+'</main></html>',encoding='utf-8')
for x in checks:assert sha(Path(x['file']))==x['sha256']
save('VERIFICATION.json',dict(status='PASS_REPORTING_AND_PRESERVATION_CHECKS',sealed_delivery_files_checked=len(checks),all_hashes_unchanged=True,verbatim_reports_included=True,original_qualification_blocks_preserved=True,v103='PARKED_BY_USER',new_Rosettes_grids=0,statistical_engines_run=0,coordination_changes=changes))
save('DELIVERY-HASHES.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='DELIVERY-HASHES.json'})
print(json.dumps(status))
