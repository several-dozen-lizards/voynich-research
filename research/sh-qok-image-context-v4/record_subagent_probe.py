"""Preserve failed fresh-context eligibility probe; no annotation or gate scoring."""
import json
import prepare as core
from setup_packets import archive, replace_json

receipt = {
  'page_id':'page-001',
  'source_image_raster_width':None,
  'source_image_raster_height':None,
  'coordinate_system':'raster_pixels_xywh',
  'blocks':[],
  'abstentions':[{
    'scope':'entire_page', 'status':'UNREGISTERED',
    'reason':'Stopped before accessing either permitted input because automatically supplied context contained Voynich research hypotheses and outcome summaries. Their relationship to this page cannot be established without further exposure.'
  }],
  'exposure_declaration':{
    'exposed':True,
    'source':'Automatically supplied memory summary in inherited context',
    'description':'Context included Voynich astrology/name hypotheses and structural association and ordering outcomes. No page-specific relationship was checked.',
    'action':'Stopped without viewing the image or reading locus headers.'
  },
  'accessed_inputs':[], 'tools_used':[], 'model_version':'unknown'
}
core.save('private/subagent-receipts/registrar-001-context-failure.json',receipt)
audit=dict(
    status='FRESH-SUBAGENT BLINDNESS ELIGIBILITY FAILED; NO SCIENTIFIC GATE EVALUATED',
    authorization='User explicitly requested fresh subagents, no inherited context, permitted inputs only.',
    dispatch=dict(task_name='/root/blind_registrar_001',fork_turns='none',role='independent registrar',page='page-001',
        permitted_inputs=['PAGE.jpg','LOCUS-HEADERS.json'],scope_instruction='Read only these two files; stop if automatically supplied context reveals project hypotheses or outcomes; no directory listing, searching, other project files or agents.'),
    observed='Agent reported automatically injected project memory and stopped before reading either permitted file.',
    evidence_type='Exact returned registrar declaration; no independent audit of hidden agent context is available to coordinator.',
    scientific_eligibility=False,
    no_memory_requirement='Original spec: a fresh session with no project memory. fork_turns=none was insufficient in the observed run.',
    interpretation='Eligibility probe only. This is not an image reliability failure, support result, page geometry judgment or manuscript negative.',
    annotation_use='Exclude this agent from registration and rating. Preserve its refusal receipt; do not fabricate line boxes or treat the page as intrinsically unregistrable.',
    rater_A_dispatched=False,rater_B_dispatched=False,
    reason_no_more_dispatch='Same known context-injection route; further exposure would not satisfy the original requirement.',
    model_version='unknown; runtime did not expose an exact version in the returned receipt.',
    next_step='Use an environment that omits project memory as well as chat history, or independent unexposed humans using the ready offline packets. Existing subagent tool has no exposed memory-suppression control.',
    raw_receipt='private/subagent-receipts/registrar-001-context-failure.json')
core.save('BLINDNESS-AUDIT.json',audit)
delivery=json.loads((core.R/'DELIVERY.json').read_text(encoding='utf-8'))
delivery.update(status='OFFLINE PACKETS READY; FRESH-SUBAGENT ELIGIBILITY FAILED BEFORE ANNOTATION',
    registrar_assigned=False,registrar_dispatch_attempts=1,eligible_registrar_dispatches=0,raters_assigned=False,
    ratings_collected=0,registration_completed=False,scientific_results=None,
    next_step=audit['next_step'],blindness_audit='BLINDNESS-AUDIT.json')
replace_json('DELIVERY.json',delivery)
preflight=json.loads((core.R/'PREFLIGHT.json').read_text(encoding='utf-8'))
for issue in preflight['issues']:
    if issue['id']=='rater_isolation':
        issue.update(status='SUBAGENT_ROUTE_FAILED_ELIGIBILITY',detail=audit['observed']+' No picture raters were dispatched. See BLINDNESS-AUDIT.json.')
replace_json('PREFLIGHT.json',preflight)
report=core.R/'REPORT.md'
archive(report)
text=report.read_text(encoding='utf-8')
text+='\nFresh-subagent eligibility probe: fork_turns=none was requested, but the registrar reported automatically supplied project memory and stopped before opening either permitted input. Its receipt is retained and ineligible for analysis. No picture raters were dispatched through the same known failure. This is a failure of the available execution setup, not NOT RELIABLE, NOT ESTIMABLE, or a manuscript finding. See BLINDNESS-AUDIT.json.\n'
report.write_text(text,encoding='utf-8')
core.seal('fresh_subagent_context_failure_retained_no_annotations',[
    'record_subagent_probe.py','BLINDNESS-AUDIT.json',
    'private/subagent-receipts/registrar-001-context-failure.json','DELIVERY.json','PREFLIGHT.json','REPORT.md'])
core.verify()
print(json.dumps(dict(status=audit['status'],ratings=0,eligible_registrations=0)))
