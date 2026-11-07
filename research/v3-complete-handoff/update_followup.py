"""Read finished reports and update the handoff; never execute research engines."""
from pathlib import Path
import datetime,hashlib,html,json
R=Path(__file__).resolve().parent;P=R.parent;run=P/'sh-qok-qualification-followup-v1/run-2026-10-24'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while True:
   b=f.read(65536)
   if not b:break
   h.update(b)
 return h.hexdigest()
verified=load(run/'FINAL-VERIFICATION.json');assert verified['status']=='COMPLETE_FIXED_RUN_VERIFIED'
checks=[]
for name,h in verified['artifact_hashes'].items():
 p=run/name;checks.append(dict(file=str(p),sha256=h,match=sha(p)==h))
assert all(x['match'] for x in checks)
for x in load(R/'SOURCE-RECEIPTS.json')['delivery_checks']:assert sha(Path(x['file']))==x['sha256']
primary=load(run/'PRIMARY-SUMMARY.json');bq=load(run/'BQ2-SUMMARY.json');assert primary['total_trials']==396000 and bq['outer_trials']==800
v4=P/'image-context-v4';receipt=load(v4/'AMENDMENT-v4.2-RECEIPT.json');assert sha(v4/receipt['amendment_file'])==receipt['amendment_sha256']
hold=load(v4/'registration/HOLD.json');timing=load(v4/'registration/V4.2-TIMING-AUDIT.json');rater=load(P/'sh-qok-image-context-v4/CLI-HOLD-RECEIPT.json')
assert hold['status']=='HOLD_BY_HUMAN_V4.2' and rater['annotation_inference_calls']==0
assert load(P/'v103-qualification-v104/PARKED.json')['status']=='PARKED_BY_USER'
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
save('FOLLOWUP-UPDATE.json',dict(checked_utc=stamp,source_status=verified['status'],primary_trials=396000,primary_cells=primary['cells'],BQ2=bq,source_hash_checks=checks,old_v31_files_preserved=verified['original_v31_files_unchanged'],new_manuscript_scores=verified['new_manuscript_scores'],interpretation='New synthetic qualification result only; historical v3.1 failures and manuscript statuses remain unchanged. B-Q2 diagnostic cannot qualify or repair heterogeneity.',v4_2=dict(sha256=receipt['amendment_sha256'],forwarded_to=['Finish v3 and build rater packet','Blind-rate Voynich image context'],authority='Direct user authorization in this chat',registration_hold=hold['status'],timing_status=timing['status'],annotation_calls_in_audited_rater_chat=rater['annotation_inference_calls'],optional_retrospective_OR_companion='NOT RUN'),v103='PARKED',Rosettes_leave_out_grids='NONE'))
e=html.escape
def table(h,rows):return '<table><tr>'+''.join('<th>'+e(x)+'</th>' for x in h)+'</tr>'+''.join('<tr>'+''.join('<td>'+e(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
block='<section id="followup-update"><h2>Completed calibration follow-up and B-Q2 diagnostic</h2><p><strong>Fixed run complete and independently verified.</strong> 396,000 fresh A/Q1 trials; 800 existing B-Q2 outer trials with original plus two fresh permutation banks. These are new qualification findings, not new manuscript results. All 39 preserved v3.1 files remain unchanged.</p>'
block+=table(['Follow-up cell','H qualification','F qualification'],[[cell,primary['cells'][cell+'-H']['status'],primary['cells'][cell+'-F']['status']] for cell in ['A-P1','A-bath','A-starred','B-Q1']])
block+='<p>All required null upper bounds met the frozen5% practical tolerance, all positive lower bounds met80%, and no exchangeable-null nominal alarm was detected. The larger fixed series supports insufficient precision of the old200-trial certification as the explanation for the P1-F/bath near misses under these generators. It does not erase the old failures, prove calibration under every mechanism, or automatically promote previously blocked manuscript cells. B-Q1 retains its abstract-generator limits, including possible qok on structurally blocked followers.</p>'
block+='<h3>B-Q2: extra inner permutations did not resolve qualification</h3>'+table(['Reading','Scenario','Flags/200: original / fresh1 / fresh2','Undefined trials: original / fresh1 / fresh2'],[[x['reading'],x['scenario'],' / '.join(str(y['flags']) for y in x['banks']),' / '.join(str(y['undefined']) for y in x['banks'])] for x in bq['results']])
block+='<p>All six undefined context receipts were classified as genuine zero variance by direct and80-digit calculations on saved terms. More shuffles do not repair that structural limitation. Reusing the same outer outcomes across banks does not create additional independent outer trials. B-Q2 remains diagnostic and unqualified; no conclusion of context heterogeneity or its absence is permitted.</p><p>The owner independently audited4,810 false-flag/trial0 cases (maximum p difference3.33×10⁻¹⁶), replayed old generator seeds and exact fixtures, and verified protocol/preservation hashes. This handoff separately verified every file hash in its final artifact manifest; it did not rerun the controls.</p>'
block+='<p><a href="../sh-qok-qualification-followup-v1/run-2026-10-24/REPORT.md">Completed follow-up report</a> · <a href="../sh-qok-qualification-followup-v1/run-2026-10-24/PRIMARY-SUMMARY.json">H/F primary summary</a> · <a href="../sh-qok-qualification-followup-v1/run-2026-10-24/BQ2-SUMMARY.json">B-Q2 banks and abstentions</a> · <a href="../sh-qok-qualification-followup-v1/run-2026-10-24/FINAL-VERIFICATION.json">Final independent audit</a> · <a href="FOLLOWUP-UPDATE.json">Handoff update receipt</a></p>'
block+='<h2>Amendment v4.2: hashed and forwarded; timing hold preserved</h2><p>The user supplied v4.2 and authorized forwarding it to both v4 chats. It makes MH log-OR primary, keeps RD descriptive, adds base-rate-null controls and OR-scale positives, and adds the post-join abstain-only qok support rule; v4.1 stands. The exact text is hashed separately and was not given to blind raters or the registrar.</p><p><strong>Pre-registration timing was not met.</strong> Existing geometry/registration predates the amendment. Those outputs are preserved as actually timed, not relabelled or silently restarted. Both analyst chats acknowledged a hold; the audited rater chat reports zero annotation inference calls. No image labels, support, join or H-IMG/H-PLANT results are claimed. The optional retrospective OR companion was not run here.</p><p><a href="../image-context-v4/AMENDMENT-v4.2-effect-scale.md">Exact v4.2 text</a> · <a href="../image-context-v4/AMENDMENT-v4.2-RECEIPT.json">Freeze and forwarding receipt</a> · <a href="../image-context-v4/registration/V4.2-TIMING-AUDIT.json">Registration timing audit</a> · <a href="../image-context-v4/registration/HOLD.json">Hold</a> · <a href="../sh-qok-image-context-v4/CLI-HOLD-RECEIPT.json">Rater no-inference receipt</a></p><p><strong>v103 remains PARKED. No Rosettes leave-out grids or new manuscript scoring.</strong></p></section>'
page=R/'report.html';before=page.read_bytes();backup=R/'report.before-followup.html'
if not backup.exists():backup.write_bytes(before)
text=before.decode('utf-8');assert 'id="followup-update"' not in text,'Preserve previous update before another snapshot'
text=text.replace('<h2>Amendment 3.1: what remains supported</h2>',block+'<h2>Sealed v3.1 decisions — preserved historical statuses</h2>')
text=text.replace('The calibration follow-up and B-Q2 diagnostic are separate, currently active work. Their eventual report cannot silently replace v3.1’s qualification status. An inconclusive or failed follow-up is reportable.','The calibration follow-up and B-Q2 diagnostic are now complete and linked above. Their new qualification findings do not silently replace v3.1’s historical statuses; B-Q2 remains unqualified.')
full=(run/'REPORT.md').read_text(encoding='utf-8');text=text.replace('</main>','<details><summary>Full completed follow-up report (verbatim text)</summary><pre>'+e(full)+'</pre></details></main>');assert page.read_bytes()==before
page.write_text(text,encoding='utf-8')
statuspath=R/'STATUS.json';oldstatus=statuspath.read_bytes();(R/'STATUS.before-followup.json').write_bytes(oldstatus);status=json.loads(oldstatus.decode('utf-8'));status.update(qualification_followup='COMPLETE_FIXED_RUN_VERIFIED: all A/Q1 cells qualified H/F; v3.1 preserved, no manuscript re-adjudication',BQ2='DIAGNOSTIC COMPLETE; remains unqualified, genuine-zero-variance receipts preserved',v4='Amendment4.2 received/hashed/forwarded; registration timing not met; analyst/rater hold',latest_update_utc=stamp);assert statuspath.read_bytes()==oldstatus;statuspath.write_text(json.dumps(status,indent=2),encoding='utf-8')
for x in load(R/'SOURCE-RECEIPTS.json')['delivery_checks']:assert sha(Path(x['file']))==x['sha256']
save('FOLLOWUP-UPDATE-VERIFICATION.json',dict(followup_artifact_hashes_checked=len(checks),all_match=True,prior_sealed_delivery_hashes_unchanged=True,amendment4_2_hash_matches=True,all_HF_statuses_included=True,prior_handof_snapshot_preserved=True,original_v31_statuses_rewritten=False,v103='PARKED',research_engines_executed_by_this_updater=0))
save('DELIVERY-HASHES.json',{p.name:sha(p) for p in R.iterdir() if p.is_file() and p.name!='DELIVERY-HASHES.json'})
print(json.dumps(dict(followup=verified['status'],source_artifact_hashes=len(checks),primary_cells=primary['cells'],BQ2='still unqualified',v4_2='hold; timing exception',v103='PARKED')))
