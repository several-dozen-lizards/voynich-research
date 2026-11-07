"""Record current annotation hold after the role-specific CLI prompt audit."""
import json
import prepare as core
from setup_packets import archive,replace_json

audit=json.loads((core.R/'ISOLATED-CLI-AUDIT.json').read_text(encoding='utf-8'))
delivery=json.loads((core.R/'DELIVERY.json').read_text(encoding='utf-8'))
delivery.update(status='THREE CLEAN CLI ROLE PROMPTS AUDITED; ANNOTATION LAUNCH HELD FOR V4.2',
    cli_prompt_audits={r['role']:r['status'] for r in audit['roles']},
    memory_injection_disabled_in_audited_contexts=True,cli_inference_sessions_launched=0,
    hard_filesystem_isolation_certified=False,
    hold='Forwarded user-authorized v4.2 hold; no restart or waiver inferred from handoff.',
    timing_here=audit['timing_here'],timing_elsewhere=audit['timing_elsewhere'],
    next_step='Resolve v4.2 freeze/timing hold before annotation inference. Additional generic tools remain exposed, so strict filesystem access isolation is not certified.',
    cli_audit='ISOLATED-CLI-AUDIT.json',registration_completed=False,ratings_collected=0,scientific_results=None)
replace_json('DELIVERY.json',delivery)
report=core.R/'REPORT.md';archive(report)
text=report.read_text(encoding='utf-8')
text+='\nSeparate CLI audit: registrar, Rater A and Rater B exact prompts were rendered with one image apiece under three empty process-specific Codex homes, memory use/generation disabled, and external command/image/browser/plugin/app tools disabled. All three supplied-context audits passed: no project memory, prior chat, personal instructions, study outcomes or amendment entered those prompts. This is not a model inference or annotation call. Generic apply_patch/resource and collaboration tool declarations remain; an OS-enforced read boundary has not been certified. No credentials were copied.\n'
text+='\nv4.2 hold: received and hash-verified analyst-only amendment; it changes the primary effect scale and adds controls/support rules. No registration, rating, support, qualification or joins have run in this chat before the amendment. The separate image-context-v4 working folder has earlier registration artifacts per its handoff receipt; global pre-registration timing cannot be certified. Further annotation inference remains held. No freeze exception is silently waived and no exposed registrar is reused.\n'
report.write_text(text,encoding='utf-8')
core.save('CLI-HOLD-RECEIPT.json',dict(status=delivery['status'],hold=delivery['hold'],
    exact_amendment_sha256=audit['source_amendment_sha256'],
    context_audits_complete=True,annotation_inference_calls=0,
    model_version='Not selected: no inference launched; CLI version 0.164.0-alpha.11.1.',
    current_chat_timing='Pre-annotation amendment recorded; only metadata inventories and prompt-rendering audits performed.',
    other_chat_timing='Separate folder has pre-amendment registration; retain that exception.',
    pending=['v4.2 timing/freeze hold resolution','Strict tool/filesystem access boundary or explicitly qualified alternative'],
    note='Passing supplied-context audit proves the recorded prompt lacks those project inputs, not absence of relevant model training knowledge.'))
core.seal('v4_2_hold_and_current_chat_annotation_timing_audit',['record_cli_hold.py','CLI-HOLD-RECEIPT.json','DELIVERY.json','REPORT.md'])
core.verify()
