"""Qualify each MXC role profile, then dispatch only audited fresh CLI contexts."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,sys,shutil,hashlib
from concurrent.futures import ThreadPoolExecutor
import prepare as core
import isolated_cli as cli
import enforce_isolation as iso

ROLES=['registrar','rater-A','rater-B']
def flags(folder):return iso.role_flags(folder)+['-c','windows.sandbox="mxc"']
def env_for(role):
    home=cli.BASE/'control'/('runtime-'+role)
    home.mkdir(exist_ok=True)
    env=dict(os.environ);env['CODEX_HOME']=str(home)
    return home,env

def qualify():
    assert json.loads((core.R/'V4.2-FREEZE.json').read_text(encoding='utf-8'))['hold'].startswith('LIFTED')
    assert json.loads((core.R/'ISOLATION-BOUNDARY-PROBE-mxc-inline.json').read_text(encoding='utf-8'))['status']=='PASS'
    def one(role):
        folder=cli.BASE/role/'page-001'
        home,env=env_for(role)
        other=cli.BASE/('rater-A' if role=='registrar' else 'registrar')/'page-001/PAGE.jpg'
        denied=cli.BASE/'control/boundary-probe/outside/CANARY.txt'
        ps=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
        q=lambda x:"'"+str(x).replace("'","''")+"'"
        script="$ErrorActionPreference='Stop'; $r=@{}; try { $b=[System.IO.File]::ReadAllBytes("+q(folder/'PAGE.jpg')+"); $r.allowed_read=$b.Length -gt 0 } catch { $r.allowed_read=$false }; "
        for name,path in [('outside_read_denied',denied),('other_role_read_denied',other)]:
            script+='try { $null=[System.IO.File]::ReadAllBytes('+q(path)+'); $r.'+name+'=$false } catch { $r.'+name+'=$true }; '
        script+='$r | ConvertTo-Json -Compress'
        command=[str(cli.CODEX),'sandbox',*flags(folder),'-P','blind','-C',str(folder),'--',str(ps),'-NoProfile','-NonInteractive','-Command',script]
        run=subprocess.run(command,cwd=folder,env=env,capture_output=True,timeout=120)
        out=cli.BASE/'control'/('qualification-'+role);out.mkdir(exist_ok=True)
        (out/'boundary.stdout.txt').write_bytes(run.stdout);(out/'boundary.stderr.txt').write_bytes(run.stderr)
        result=json.loads(run.stdout) if run.returncode==0 else None
        assert run.returncode==0 and result and all(result.values()),(role,run.returncode,result,run.stderr.decode(errors='replace'))
        prompt=(cli.BASE/'control'/('audit-'+role)/'exact-task-prompt.txt').read_text(encoding='utf-8')
        command=[str(cli.CODEX),'--no-daemon','debug','prompt-input',*flags(folder),'--image',str(folder/'PAGE.jpg'),'--',prompt]
        run=subprocess.run(command,cwd=folder,env=env,capture_output=True,timeout=90)
        (out/'rendered-model-input.json').write_bytes(run.stdout);(out/'prompt.stderr.txt').write_bytes(run.stderr)
        assert run.returncode==0
        data=json.loads(run.stdout)
        texts='\n'.join(p.get('text','') for m in data for p in m.get('content',[]))
        assert all(x not in texts for x in ['MEMORY_SUMMARY','memories_v2','Reed mode','JNSQ','sh-qok','sh→qok','Holm p','AMENDMENT-v4.2'])
        assert '<special>:root</special>' in texts and 'access="deny" escalatable="false"' in texts and 'access="read"' in texts
        assert any(p.get('text')==prompt for m in data if m.get('role')=='user' for p in m.get('content',[]))
        return dict(role=role,status='PASS',mxc_canaries=result,permission_profile=iso.permissions(folder),
            rendered_input_sha256=core.sha(out/'rendered-model-input.json'),prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
            supplied_files={p.name:core.sha(p) for p in folder.iterdir()},runtime_home=str(home),memory_use=False,memory_generation=False,
            filesystem_access='Root deny; minimal system runtime read; this role folder read-only; other role and neutral outside reads tested denied.',
            limitation='Empirical filesystem tests cover these native paths; minimal system runtime access remains for execution. Training knowledge cannot be erased. No task-result exposure is supplied.')
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,ROLES))
    core.save('ISOLATION-QUALIFICATION.json',dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),roles=results,
        no_inference_yet=True,model_can_use_shell=False,local_image_tool=False,apps=False,plugins=False,mcp_servers={},
        generic_tools='Remaining native declarations constrained by named filesystem profile; no global filesystem-read grant.',
        cross_role_receipts='Independent native process and process-specific Codex home for each role. No input includes another role response.'))
    core.seal('mxc_role_specific_context_and_filesystem_qualification_before_inference',['ISOLATION-QUALIFICATION.json','start_blind_run.py','enforce_isolation.py'])
    print(json.dumps(dict(status='PASS',roles=results),ensure_ascii=True))

def run_role(role):
    assert role in ROLES
    qualification=json.loads((core.R/'ISOLATION-QUALIFICATION.json').read_text(encoding='utf-8'))
    assert qualification['status']=='PASS'
    record=next(r for r in qualification['roles'] if r['role']==role)
    folder=cli.BASE/role/'page-001'
    assert {p.name:core.sha(p) for p in folder.iterdir()}==record['supplied_files']
    prompt=(cli.BASE/'control'/('audit-'+role)/'exact-task-prompt.txt').read_text(encoding='utf-8')
    assert hashlib.sha256(prompt.encode()).hexdigest()==record['prompt_sha256']
    if role!='registrar':
        reg=json.loads((core.R/'private/cli-runs/registrar-page-001/RECEIPT.json').read_text(encoding='utf-8'))
        assert reg['status']=='COMPLETED_NO_TOOL_CALLS'
    home,env=env_for(role)
    outdir=core.R/'private/cli-runs'/(role+'-page-001');outdir.mkdir(parents=True,exist_ok=True)
    if (outdir/'RECEIPT.json').exists():raise SystemExit('Prior attempt exists; preserve it rather than overwriting.')
    # Existing account credentials are copied by the coordinator, outside the
    # permitted input folder and outside the model's read boundary. Never print.
    auth=home/'auth.json'
    assert not auth.exists()
    shutil.copyfile(Path(r'C:\Users\lewis\.codex\auth.json'),auth)
    cmd=[str(cli.CODEX),'--no-daemon','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
         '--json','--color','never',*flags(folder),'-o',str(outdir/'FINAL.txt'),'--image',str(folder/'PAGE.jpg'),'--','-']
    receipt=dict(role=role,page_id='page-001',utc_started=datetime.now(timezone.utc).isoformat(),status='STARTED',
        prompt_sha256=record['prompt_sha256'],input_files=record['supplied_files'],
        process_specific_home=str(home),memory_use=False,memory_generation=False,
        read_boundary='MXC: deny root, minimal runtime read, this role input folder read-only.',
        command=cmd,credentials='Temporary copy in denied runtime home, removed after run; never in model prompt or role folder.',
        model='Runtime-selected CLI default; exact runtime metadata retained when available.')
    core.save(str((outdir/'START.json').relative_to(core.R)),receipt)
    core.seal('independent_'+role+'_first_page_before_inference',[str((outdir/'START.json').relative_to(core.R)),'start_blind_run.py'])
    result=None
    try:
        with (outdir/'EVENTS.jsonl').open('wb') as stdout,(outdir/'STDERR.txt').open('wb') as stderr:
            result=subprocess.run(cmd,input=prompt.encode('utf-8'),cwd=folder,env=env,stdout=stdout,stderr=stderr,timeout=900)
    finally:
        # Exact single-file removal only; no recursive cleanup or global changes.
        if auth.exists():auth.unlink()
    events=[];invalid_lines=0
    for line in (outdir/'EVENTS.jsonl').read_text(encoding='utf-8').splitlines():
        try:events.append(json.loads(line))
        except Exception:invalid_lines+=1
    tools=[e for e in events if e.get('item',{}).get('type') in ['command_execution','mcp_tool_call','web_search','file_change','collaboration_tool_call']]
    completed=any(e.get('type')=='turn.completed' for e in events)
    success=result.returncode==0 and completed and (outdir/'FINAL.txt').exists() and not tools and not invalid_lines
    receipt.update(status='COMPLETED_NO_TOOL_CALLS' if success else 'FAILED_OR_INELIGIBLE',
        returncode=result.returncode,utc_finished=datetime.now(timezone.utc).isoformat(),
        turn_completed=completed,observed_tool_events=len(tools),invalid_event_lines=invalid_lines,
        event_types=sorted({e.get('type','') for e in events}),credential_copy_removed=not auth.exists(),
        files={p.name:core.sha(p) for p in outdir.iterdir() if p.is_file()})
    core.save(str((outdir/'RECEIPT.json').relative_to(core.R)),receipt)
    core.seal('independent_'+role+'_first_page_response_sealed',[str((outdir/p).relative_to(core.R)) for p in ['RECEIPT.json','FINAL.txt','EVENTS.jsonl','STDERR.txt'] if (outdir/p).exists()])
    print(json.dumps(dict(role=role,status=receipt['status'],returncode=result.returncode,tool_events=len(tools),completed=completed,output=str(outdir/'FINAL.txt'))))

if __name__=='__main__':
    {'qualify':qualify,'registrar':lambda:run_role('registrar'),'rater-A':lambda:run_role('rater-A'),'rater-B':lambda:run_role('rater-B')}[sys.argv[1]]()
