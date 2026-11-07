"""Read-only cohort audit; writes a separate receipt, never changes the run."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json
from PIL import Image
import prepare as core
import continue_blind_cohort as runner
import enforce_isolation as iso

def main():
    frozen=json.loads((core.R/'COHORT-V2-FREEZE.json').read_text(encoding='utf-8'))
    manifest=json.loads((runner.RUNS/'MANIFEST.json').read_text(encoding='utf-8'))
    errors=[];warnings=[];counts=Counter();registered=0;elements=Counter();abstained=[];fully_done=[];active=[]
    def check(condition,reason):
        if not condition:errors.append(reason)
    check(core.sha(runner.RUNS/'MANIFEST.json')==frozen['manifest_sha256'],'manifest drift')
    check(core.sha(runner.cli.CODEX)==frozen['cli_executable_sha256'],'CLI executable drift')
    check(core.sha(core.R/'MANUAL.md')==frozen['manual_sha256'],'manual drift')
    check(len(manifest)==160 and len({p['page_id'] for p in manifest})==160,'cohort page count/uniqueness')
    check(all(p['page_id']!='page-001' and p['folio'] not in core.RESERVED for p in manifest),'first/reserved page entered cohort')
    # Audit all staged input folders, including pages not yet dispatched.
    staged_folders=0;started_calls=0;tool_events=0;boundary_checks=0
    completed_threads=[];homes=[]
    for page in manifest:
        page_finished=0
        for role in runner.ROLES:
            entry=page['roles'][role];folder=Path(entry['folder']);control=Path(entry['control'])
            actual={p.name:core.sha(p) for p in folder.iterdir() if p.is_file()}
            check(actual==entry['input_files'],f'{page["page_id"]}/{role}: input files changed')
            check(set(actual)==({'PAGE.jpg','LOCUS-HEADERS.json'} if role=='registrar' else {'PAGE.jpg','MANUAL.md'}),f'{page["page_id"]}/{role}: forbidden staged file')
            if role!='registrar':check(actual.get('MANUAL.md')==frozen['manual_sha256'],'staged manual mismatch')
            else:
                meta=json.loads((folder/'LOCUS-HEADERS.json').read_text(encoding='utf-8'))
                check('native_width' not in meta and 'native_height' not in meta,'native dimensions leaked into raster header')
                check(not any('status' in h for u in meta['source_units'] for h in u['ordered_locus_headers']),'workflow status in source headers')
                check((meta['raster_width'],meta['raster_height'])==Image.open(folder/'PAGE.jpg').size,'raster header mismatch')
            check(runner.sha_text((control/'PROMPT.txt').read_text(encoding='utf-8'))==entry['prompt_sha256'],'staged prompt drift')
            check(core.sha(control/'OUTPUT-SCHEMA.json')==entry['schema_sha256'],'staged schema drift')
            staged_folders+=1
            start_path=control/'START.json'
            if not start_path.exists():continue
            try:start=json.loads(start_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                warnings.append(f'{page["page_id"]}/{role}: START being written; not yet included')
                continue
            started_calls+=1
            command=start['command'];settings={}
            for i,arg in enumerate(command[:-1]):
                if arg=='-c':
                    k,_,v=command[i+1].partition('=');settings[k]=v
            check('--model' in command and command[command.index('--model')+1]==frozen['model_identifier'],'explicit --model mismatch')
            check(start['model_identifier']==frozen['model_identifier'] and settings.get('model')==json.dumps(frozen['model_identifier']),'model receipt/config drift')
            check(start['cli_sha256']==frozen['cli_executable_sha256'] and start['cli_version']==frozen['cli_version'],'CLI pin mismatch')
            check(start['reasoning_effort']==frozen['reasoning_effort'] and settings.get('model_reasoning_effort')==json.dumps(frozen['reasoning_effort']),'reasoning setting mismatch')
            for key in ['memories.use_memories','memories.generate_memories','features.memories','features.shell_tool','features.apps','features.plugins','features.browser_use','features.view_image','features.multi_agent']:
                check(settings.get(key)=='false',key+' enabled/missing')
            check(settings.get('web_search')=='"disabled"' and settings.get('mcp_servers')=='{}','external tool channel enabled')
            check(settings.get('windows.sandbox')=='"mxc"' and settings.get('approval_policy')=='"never"','sandbox/escalation mode drift')
            check(settings.get('permissions.blind.filesystem')==iso.permissions(folder)['permissions.blind.filesystem'],'role filesystem grant changed')
            check(settings.get('permissions.blind.network.enabled')=='false','command networking enabled')
            check('--ephemeral' in command and '--ignore-user-config' in command,'session persistence/config flag missing')
            check(not any(s in command for s in ['--add-dir','--sandbox','--dangerously-bypass-approvals-and-sandbox','resume','fork']),'broader access or inherited session requested')
            check(start['boundary_checks']=={'own_read':True,'outside_denied':True,'other_role_denied':True},'canary denial failed')
            boundary_checks+=1
            prompt=json.loads((control/'RENDERED-PROMPT.json').read_text(encoding='utf-8'))
            texts='\n'.join(p.get('text','') for m in prompt for p in m.get('content',[]))
            check(not any(t in texts for t in ['MEMORY_SUMMARY','memories_v2','Reed mode','JNSQ','sh-qok','sh→qok','Holm p','AMENDMENT-v4.2']),'forbidden project content in rendered prompt')
            check('access="deny" escalatable="false"' in texts and '<special>:root</special>' in texts,'rendered root deny absent')
            check(core.sha(control/'RENDERED-PROMPT.json')==start['rendered_prompt_sha256'],'audited prompt artifact changed')
            homes.append(str(runner.ROOT/'runtime'/role/page['page_id']))
            if role!='registrar':
                reg_path=Path(page['roles']['registrar']['control'])/'RECEIPT.json'
                check(reg_path.exists(),'rater started before registrar receipt')
                if reg_path.exists():
                    reg=json.loads(reg_path.read_text(encoding='utf-8'))
                    check(reg['utc_finished']<=start['utc_started'],'rater preceded registrar seal sequence')
            receipt_path=control/'RECEIPT.json'
            if not receipt_path.exists():
                active.append(dict(page=page['page_id'],role=role,utc_started=start['utc_started']))
                continue
            try:receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                warnings.append(f'{page["page_id"]}/{role}: RECEIPT being written; not yet included')
                continue
            counts[role]+=1;counts['failed']+=receipt['status']!='COMPLETED_VALIDATED';page_finished+=1
            tool_events+=receipt['observed_tool_events']
            check(receipt['observed_tool_events']==0,'observed inference tool event')
            check(receipt['credential_removed'] and not (Path(homes[-1])/'auth.json').exists(),'completed runtime credential copy remains')
            check(receipt['model_identifier']==frozen['model_identifier'],'completed model mismatch')
            completed_threads.append(receipt['thread_id'])
            for name,h in receipt['artifacts'].items():check(core.sha(control/name)==h,f'completed artifact changed: {page["page_id"]}/{role}/{name}')
            validation=receipt.get('validation') or {}
            if role=='registrar':
                registered+=validation.get('accepted_lines',0)
                if validation.get('accepted_lines')==0:
                    abstained.append(dict(page=page['page_id'],folio=page['folio'],dropped_blocks=validation.get('dropped_blocks'),not_registered=validation.get('source_units_not_registered')))
            else:elements[role]+=validation.get('elements',0)
        if page_finished==3:fully_done.append(page['page_id'])
    check(len(homes)==len(set(homes)),'runtime home reused across calls')
    check(len(completed_threads)==len(set(completed_threads)),'inference thread reused')
    first=json.loads((core.R/'FIRST-BLIND-PAGE.json').read_text(encoding='utf-8'))
    for role,r in first['actual_calls'].items():check(core.sha(core.R/'private/cli-runs'/(role+'-page-001')/'FINAL.txt')==r['raw_final_sha256'],'original first-page response changed')
    prohibited_results=['AGREEMENT.json','SUPPORT.json','EVENTS.csv','H-IMG.json','H-PLANT.json']
    check(not any((core.R/n).exists() for n in prohibited_results),'later scientific phase artifact appeared')
    helper=json.loads((core.R/'COHORT-COMPLETION-HELPER.json').read_text(encoding='utf-8'))
    check(core.sha(core.R/'collect_blind_cohort.py')==helper['collector_sha256'],'completion collector changed')
    check(core.sha(core.R/'finish_cohort_when_ready.py')==helper['helper_sha256'],'completion helper changed')
    # Validate a stable complete prefix of the append-only phase chain. New
    # appends may occur while this independent read-only audit is running.
    raw_chain=(core.R/'PHASES.jsonl').read_bytes();parts=raw_chain.splitlines(keepends=True)
    if parts and not parts[-1].endswith(b'\n'):warnings.append('Phase append in progress; last partial line excluded');parts=parts[:-1]
    previous=b''
    for raw in parts:
        phase=json.loads(raw)
        check(phase['previous_log_sha256']==(hashlib.sha256(previous).hexdigest() if previous else None),'phase chain broken')
        for name,h in phase['files'].items():
            path=core.R/name;archive=core.R/'private/hash-history'/h
            check(core.sha(path)==h or (archive.exists() and core.sha(archive)==h),'sealed file changed: '+name)
        previous+=raw
    result=dict(status='PASS' if not errors else 'FAIL',utc=datetime.now(timezone.utc).isoformat(),
        fully_processed_pages=len(fully_done),total_pages=160,completed_calls=dict(counts),started_calls=started_calls,
        registered_lines_passing_structural_checks=registered,picture_elements=dict(elements),
        registration_abstentions=abstained,active_calls=active,staged_input_folders_checked=staged_folders,
        per_call_boundary_audits_checked=boundary_checks,unique_completed_threads=len(set(completed_threads)),
        model=frozen['model_identifier'],reasoning_effort=frozen['reasoning_effort'],cli_version=frozen['cli_version'],
        model_snapshot_limit=frozen['model_snapshot'],observed_tool_events=tool_events,
        first_page_preserved=True,phase_lines_verified=len(parts),errors=errors,warnings=warnings,
        later_scientific_phases_started=False,
        behavior='Read-only audit of active run. No protocol/configuration/input changes or model calls made.')
    name='LIVE-AUDIT-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json'
    core.save(name,result)
    print(json.dumps({k:result[k] for k in ['status','fully_processed_pages','completed_calls','started_calls','registered_lines_passing_structural_checks','picture_elements','staged_input_folders_checked','per_call_boundary_audits_checked','observed_tool_events','errors','warnings']}|dict(receipt=name),ensure_ascii=True))

if __name__=='__main__':main()
