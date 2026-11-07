"""Separate CLI context audit and no-tool inference; never resume project sessions."""
from pathlib import Path
import json, os, shutil, subprocess, sys, hashlib
import prepare as core

BASE=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\25\01a170b3-70b1-7a93-ae85-265320a37745\isolated-cli')
CODEX=Path(r'C:\Users\lewis\AppData\Local\OpenAI\Codex\bin\2993767bd1dfb009\codex.exe')
CONFIG={
    'memories.use_memories':'false','memories.generate_memories':'false',
    'features.memories':'false','project_doc_max_bytes':'0',
    'developer_instructions':'""','mcp_servers':'{}',
    'web_search':'"disabled"','history.persistence':'"none"',
    'tools.view_image':'false',
}
for feature in ['apps','plugins','remote_plugin','shell_tool','multi_agent','browser_use','browser_use_external',
                'computer_use','image_generation','in_app_browser','skill_search','skill_mcp_dependency_install',
                'hooks','tool_suggest','workspace_dependencies','sleep_tool','view_image','code_mode_host']:
    CONFIG['features.'+feature]='false'
CONFIG['features.skip_host_skill_discovery']='true'

def flags():
    return [part for k,v in CONFIG.items() for part in ('-c',k+'='+v)]

def initialize():
    BASE.mkdir(exist_ok=True)
    control=BASE/'control';control.mkdir(exist_ok=True)
    for role in ['registrar','rater-A','rater-B']:
        d=BASE/role/'page-001';d.mkdir(parents=True,exist_ok=True)
        source=BASE.parent/'blind-annotations/page-001'
        shutil.copyfile(source/'PAGE.jpg',d/'PAGE.jpg')
        if role=='registrar':shutil.copyfile(source/'LOCUS-HEADERS.json',d/'LOCUS-HEADERS.json')
        else:shutil.copyfile(core.R/'MANUAL.md',d/'MANUAL.md')
    core.save('private/ISOLATED-CLI-PLAN.json',dict(status='CONFIGURED FOR PROMPT AUDIT; NO ANNOTATIONS',
        executable=str(CODEX),cli_version='0.164.0-alpha.11.1',role_folders=[str(BASE/r/'page-001') for r in ['registrar','rater-A','rater-B']],
        config_overrides=CONFIG,process_mode='new CLI process per role per page; no resume or fork; exec ephemeral; no shared app daemon',
        model_selection='No model override: use CLI-selected model and record returned runtime version.',
        isolation='No tool access intended. Folder membership alone is not a read-access sandbox. Audit rendered prompt before inference.',
        credentials='Use existing CLI authentication; no credentials copied into role folders or printed.',
        required_audit='Memory/project content absent; no unapproved skill catalog, MCP or external tools; exact task inputs only. A failed audit blocks inference.'))
    core.seal('isolated_cli_plan_before_prompt_audit',['isolated_cli.py','private/ISOLATED-CLI-PLAN.json'])

def probe():
    d=BASE/'rater-A/page-001'
    # No manuscript image or manual is supplied during this environment-only audit.
    prompt='Environment audit only. Do not annotate anything. Report whether project memory or earlier chat context was supplied, and name any available tools. Do not infer missing context.'
    cmd=[str(CODEX),'--no-daemon','debug','prompt-input',*flags(),prompt]
    out=subprocess.run(cmd,cwd=d,capture_output=True,timeout=90)
    (BASE/'control/prompt-audit.json').write_bytes(out.stdout)
    (BASE/'control/prompt-audit.stderr.txt').write_bytes(out.stderr)
    print(json.dumps(dict(returncode=out.returncode,stdout_bytes=len(out.stdout),stderr=out.stderr.decode('utf-8',errors='replace')[:1800])))
    if out.returncode==0:
        data=json.loads(out.stdout)
        print(json.dumps(dict(type=type(data).__name__,keys=list(data) if isinstance(data,dict) else None,preview=str(data)[:1800]),ensure_ascii=False))

def clean_probe():
    home=BASE/'control/clean-home-probe'
    home.mkdir(exist_ok=True)
    env=dict(os.environ)
    env['CODEX_HOME']=str(home)
    prompt='Environment audit only. Do not annotate anything. Report whether project memory or earlier chat context was supplied, and name any available tools. Do not infer missing context.'
    cmd=[str(CODEX),'--no-daemon','debug','prompt-input',*flags(),prompt]
    result=subprocess.run(cmd,cwd=BASE/'rater-A/page-001',env=env,capture_output=True,timeout=90)
    (BASE/'control/clean-prompt-audit.json').write_bytes(result.stdout)
    (BASE/'control/clean-prompt-audit.stderr.txt').write_bytes(result.stderr)
    print(json.dumps(dict(returncode=result.returncode,stdout_bytes=len(result.stdout),stderr=result.stderr.decode('utf-8',errors='replace')[:1500])))
    if result.returncode==0:
        data=json.loads(result.stdout)
        print(json.dumps(dict(markers={w:w.lower() in str(data).lower() for w in ['MEMORY_SUMMARY','memories_v2','Voynich','JNSQ','Reed mode','skills_instructions']},
            types=[x.get('type') for x in data],tools=[t.get('name') for x in data if x.get('type')=='additional_tools' for ns in x.get('tools',[]) for t in ns.get('tools',[])]),ensure_ascii=True))

def role_audits():
    from concurrent.futures import ThreadPoolExecutor
    amendment=core.R.parent/'image-context-v4/AMENDMENT-v4.2-effect-scale.md'
    receipt=core.R.parent/'image-context-v4/AMENDMENT-v4.2-RECEIPT.json'
    received=json.loads(receipt.read_text(encoding='utf-8'))
    assert core.sha(amendment)==received['amendment_sha256']
    # Analyst-only copies. Never placed in role inputs or submitted to a model.
    shutil.copyfile(amendment,core.R/'AMENDMENT-v4.2-effect-scale.md')
    shutil.copyfile(receipt,core.R/'AMENDMENT-v4.2-RECEIVED.json')
    roles=['registrar','rater-A','rater-B']
    def one(role):
        folder=BASE/role/'page-001'
        home=BASE/'control'/('empty-home-'+role)
        home.mkdir(exist_ok=True)
        env=dict(os.environ);env['CODEX_HOME']=str(home)
        if role=='registrar':
            prompt=('Outline every writing block and physical line in the attached page. Use geometry and line order only to map the supplied locus headers; do not transcribe or interpret writing. '
                    'Return block and line boxes in JPEG raster x,y,width,height coordinates, image dimensions, visible and H/F source block counts, ordered source crosswalks, uncertainty, and every unmatched block. '
                    'Count mismatch or ambiguous mapping means UNREGISTERED; do not force it. No picture judgments.\n\n'+(folder/'LOCUS-HEADERS.json').read_text(encoding='utf-8'))
            allowed={'PAGE.jpg','LOCUS-HEADERS.json'}
        else:
            prompt=(folder/'MANUAL.md').read_text(encoding='utf-8')
            allowed={'PAGE.jpg','MANUAL.md'}
        assert {p.name for p in folder.iterdir()}==allowed
        outdir=BASE/'control'/('audit-'+role);outdir.mkdir(exist_ok=True)
        (outdir/'exact-task-prompt.txt').write_text(prompt,encoding='utf-8')
        cmd=[str(CODEX),'--no-daemon','debug','prompt-input',*flags(),'--image',str(folder/'PAGE.jpg'),'--',prompt]
        result=subprocess.run(cmd,cwd=folder,env=env,capture_output=True,timeout=90)
        raw=outdir/'rendered-model-input.json'
        if raw.exists() and not (outdir/'first-attempt-image-argument-parsing-failure.json').exists():
            shutil.copyfile(raw,outdir/'first-attempt-image-argument-parsing-failure.json')
        raw.write_bytes(result.stdout)
        (outdir/'stderr.txt').write_bytes(result.stderr)
        if result.returncode:return dict(role=role,status='PROMPT_AUDIT_FAILED',returncode=result.returncode)
        data=json.loads(result.stdout)
        texts=[part.get('text','') for x in data for part in x.get('content',[]) if isinstance(part,dict)]
        combined='\n'.join(texts)
        prohibited=['MEMORY_SUMMARY','memories_v2','Reed mode','JNSQ','v100/v102','sh→qok','sh-qok','Holm p','AMENDMENT-v4.2']
        found=[w for w in prohibited if w.casefold() in combined.casefold()]
        user_messages=[x for x in data if x.get('type')=='message' and x.get('role')=='user']
        exact_prompt=any(part.get('text')==prompt for x in user_messages for part in x.get('content',[]))
        images=[part for x in user_messages for part in x.get('content',[]) if part.get('type')=='input_image']
        tools=[t.get('name') for x in data if x.get('type')=='additional_tools' for ns in x.get('tools',[]) for t in ns.get('tools',[])]
        assert not found and exact_prompt and len(images)==1,(role,found,exact_prompt,len(images))
        # These audits do not invoke a model. Tool declarations remain visible;
        # distinguish an audited clean prompt from enforced filesystem isolation.
        return dict(role=role,status='PASS_SUPPLIED_CONTEXT_ONLY',model_inference_started=False,
            role_folder=str(folder),input_files={p.name:core.sha(p) for p in folder.iterdir()},
            empty_process_home=str(home),memory_disabled=True,history_inherited=False,
            exact_task_prompt_present=exact_prompt,attached_images=len(images),prohibited_markers_found=found,
            generic_tool_declarations=tools,filesystem_access_enforced=False,
            limitation='Shell, local image loading, browser, plugins and apps disabled; generic apply_patch/resource and collaboration declarations remain exposed. No credential copied and no model invoked.',
            rendered_input_file=str(raw),rendered_input_sha256=core.sha(raw))
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,roles))
    core.save('ISOLATED-CLI-AUDIT.json',dict(status='CLEAN_ROLE_PROMPTS_VERIFIED; ANNOTATION_LAUNCH_HELD',
        config_overrides=CONFIG,roles=results,
        context_evidence='Codex debug prompt-input renders each exact task with its one attached image before inference. Separate empty CODEX_HOME per role; no auth copies required for rendering.',
        inference_sessions_launched=0,registration_calls=0,rating_calls=0,
        hold='Forwarded user-authorized v4.2 hold; no annotation launch pending timing/freeze audit.',
        timing_here='No registration or ratings in this chat before v4.2: only rejected exposed subagent and no-inference CLI prompt rendering.',
        timing_elsewhere='Forwarding receipt records registration artifacts in the distinct image-context-v4 folder before amendment freeze. Do not certify global pre-registration timing.',
        access_boundary='Role folders contain only permitted inputs. This does not constitute an OS read sandbox. Generic tool declarations remain, so unrestricted file-access isolation is not certified.',
        source_amendment_sha256=core.sha(amendment),scientific_results=None))
    core.seal('isolated_cli_role_prompt_audits_and_v4_2_hold',[
        'isolated_cli.py','ISOLATED-CLI-AUDIT.json','AMENDMENT-v4.2-effect-scale.md','AMENDMENT-v4.2-RECEIVED.json'])
    core.verify()
    print(json.dumps(dict(status='CLEAN_ROLE_PROMPTS_VERIFIED; ANNOTATION_LAUNCH_HELD',roles=[dict(role=r['role'],status=r['status']) for r in results],inference_calls=0)))

if __name__=='__main__':{'initialize':initialize,'probe':probe,'clean-probe':clean_probe,'role-audits':role_audits}[sys.argv[1]]()
