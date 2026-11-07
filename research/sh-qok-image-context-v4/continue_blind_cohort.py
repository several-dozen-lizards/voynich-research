"""Frozen coordinate transport; independently isolated calls for remaining pages."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from collections import defaultdict
import csv,hashlib,json,os,re,shutil,subprocess,sys,threading,time
from PIL import Image
import prepare as core
import isolated_cli as cli
import enforce_isolation as iso

MODEL='gpt-6.1-sol'
EFFORT='medium'
VERSION='0.164.0-alpha.11.1'
ROOT=cli.BASE.parent/'blind-cohort-v2'
RUNS=core.R/'private/cohort-v2'
LOCK=threading.Lock()
ROLES=['registrar','rater-A','rater-B']

def now():return datetime.now(timezone.utc).isoformat()
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha_text(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def seal(name,paths):
    with LOCK:core.seal(name,[str(p.relative_to(core.R)) for p in paths])
def cfg(folder):
    config=dict(cli.CONFIG)
    config.pop('tools.view_image',None)  # CLI explicitly reported this legacy key ignored.
    config.update({'features.shell_snapshot':'false','approval_policy':'"never"',
                   'model':json.dumps(MODEL),'model_reasoning_effort':json.dumps(EFFORT),
                   'windows.sandbox':'"mxc"'})
    config.update(iso.permissions(folder))
    return [arg for k,v in config.items() for arg in ('-c',k+'='+v)]

def schemas(w,h):
    box={'type':'array','items':{'type':'number','minimum':0},'minItems':4,'maxItems':4,
         'description':f'JPEG raster pixels [x,y,width,height], top-left origin, inside {w} by {h}. No canvas coordinates or normalized values.'}
    def obj(properties):return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
    common={'coordinate_system':{'type':'string','enum':['jpeg_raster_xywh']},
            'raster_width':{'type':'integer','enum':[w]},'raster_height':{'type':'integer','enum':[h]}}
    line=obj({'ordinal':{'type':'integer','minimum':1},'box':box,
              'H_locus':{'type':['string','null']},'F_locus':{'type':['string','null']}})
    block=obj({'block_id':{'type':'string'},'box':box,'source_unit':{'type':['string','null']},
               'status':{'type':'string','enum':['REGISTERED','UNREGISTERED']},'reason':{'type':'string'},
               'visible_line_count':{'type':'integer','minimum':0},'lines':{'type':'array','items':line}})
    reg=obj(common|{'blocks':{'type':'array','items':block},'notes':{'type':'string'}})
    picture=obj({'box':box,'category':{'type':'string','enum':['PL','VE','FG','CE','OT']},'note':{'type':'string'}})
    rating=obj(common|{'picture_elements':{'type':'array','items':picture},'notes':{'type':'string'}})
    return reg,rating

def task_list():
    return json.loads((core.R/'private/IMAGE-QUEUE.json').read_text(encoding='utf-8'))['tasks']

def prepare():
    if (core.R/'COHORT-V2-FREEZE.json').exists():raise SystemExit('Already frozen; do not overwrite.')
    ROOT.mkdir(exist_ok=True);RUNS.mkdir(parents=True,exist_ok=True)
    sources=json.loads((core.R/'private/LINE-REGISTRATION-QUEUE.json').read_text(encoding='utf-8'))
    bypage=defaultdict(list)
    for row in sources:bypage[row['folio']].append(row)
    tasks=task_list();assert len(tasks)==161
    catalog=json.loads((core.R/'private/CLI-BUNDLED-MODELS.json').read_text(encoding='utf-8'))['models']
    model_entry=next(m for m in catalog if m['slug']==MODEL)
    entry_hash=sha_text(json.dumps(model_entry,sort_keys=True))
    manifest=[]
    for index,t in enumerate(tasks[1:],2):
        assert t['folio'] not in core.RESERVED
        page=f'page-{index:03d}'
        image=core.R/'private'/t['image']
        w,h=Image.open(image).size
        native_transform=dict(x_scale=t['native_width']/w,y_scale=t['native_height']/h,
                              formula='native xywh = raster xywh * [x_scale,y_scale,x_scale,y_scale] without rounding')
        units=defaultdict(list)
        for s in bypage[t['folio']]:
            units[s['unit']].append(dict(locus=s['locus'],line_number=s['line_number'],readings=s['readings']))
        meta=dict(page_id=page,coordinate_system='jpeg_raster_xywh',raster_width=w,raster_height=h,
            source_units=[dict(unit=u,H_count=sum('H' in x['readings'] for x in rows),
                              F_count=sum('F' in x['readings'] for x in rows),ordered_locus_headers=rows) for u,rows in units.items()])
        row=dict(page_id=page,task_id=t['task_id'],folio=t['folio'],raster_width=w,raster_height=h,
                 native_width=t['native_width'],native_height=t['native_height'],native_transform=native_transform,
                 image_sha256=core.sha(image),roles={})
        for role in ROLES:
            folder=ROOT/role/page;folder.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(image,folder/'PAGE.jpg')
            if role=='registrar':
                dump(folder/'LOCUS-HEADERS.json',meta)
                prompt=('Independently outline writing blocks and every physical line inside them in the attached JPEG. '
                        f'The JPEG raster is exactly {w} pixels wide and {h} pixels high. All boxes must be [x,y,width,height] in that JPEG raster, top-left origin. '
                        'Use image geometry and within-block line order only to map supplied P-unit locus headers. Never transcribe or interpret writing. '
                        'Header line numbers may continue across units; use within-unit ordinal order. Supplied headers describe P-unit writing only; other writing may remain unmatched. '
                        'Assess each block independently. A mismatch or ambiguous mapping makes that block UNREGISTERED; preserve the reason. '
                        'Do not force source-unit or locus assignments. Registered blocks must have a visible-line count matching the mapped unit count in each supplied reading. '
                        'Do not annotate or categorize pictures. Return the requested structured geometry.\n\n'+json.dumps(meta,ensure_ascii=False))
            else:
                shutil.copyfile(core.R/'MANUAL.md',folder/'MANUAL.md')
                prompt=(folder/'MANUAL.md').read_text(encoding='utf-8')
            control=RUNS/page/role;control.mkdir(parents=True,exist_ok=True)
            (control/'PROMPT.txt').write_text(prompt,encoding='utf-8')
            reg_schema,rater_schema=schemas(w,h)
            dump(control/'OUTPUT-SCHEMA.json',reg_schema if role=='registrar' else rater_schema)
            row['roles'][role]=dict(folder=str(folder),control=str(control),prompt_sha256=sha_text(prompt),
                schema_sha256=core.sha(control/'OUTPUT-SCHEMA.json'),input_files={p.name:core.sha(p) for p in folder.iterdir()})
        manifest.append(row)
    dump(RUNS/'MANIFEST.json',manifest)
    core.save('COHORT-V2-FREEZE.json',dict(utc=now(),authority='User: fix coordinate handling, pin and record model/version, preserve first-page failure, continue remaining pages under same isolation.',
        pages=len(manifest),order='Original image queue order, omitting page-001 only. No selection by labels, registration success or text outcomes.',
        first_page='Preserved unchanged and excluded from this corrected transport cohort; no retry or substitution.',
        coordinate_contract='Measured JPEG raster pixels xywh canonical; native dimensions and exact scaling retained only by coordinator. Never supply native dimensions as raster dimensions.',
        source_header_cleanup='Remove pre-existing workflow status fields. Registrar gets only geometry dimensions and ordered locus headers/counts, never labels or outcomes.',
        model_identifier=MODEL,model_selection='Explicit --model and model config override on every audit and inference call; never CLI default.',
        model_snapshot='Official public identifier; no dated immutable snapshot or server weight revision is published/exposed. No claim of an immutable backend revision.',
        model_reference='https://developers.openai.com/api/docs/models/gpt-6.1-sol',
        reasoning_effort=EFFORT,cli_version=VERSION,cli_executable_sha256=core.sha(cli.CODEX),model_catalog_entry_sha256=entry_hash,
        transport_format='Structured output schema fixes raster dimensions and xywh convention without changing the scientific picture-category manual.',
        manual_sha256=core.sha(core.R/'MANUAL.md'),manifest_sha256=core.sha(RUNS/'MANIFEST.json'),
        isolation='Fresh ephemeral CLI process and dedicated memory-disabled home per role per page. MXC root deny, minimal runtime read, own folder read-only; no escalation; no external tools. Test each folder before inference.',
        phase_order='Each registrar response and validation sealed before that page rater calls. No cross-role outputs supplied. Entire remaining corpus is attempted; disagreements/abstentions retained.',
        eligibility='Nonzero tool call, malformed output, coordinate overflow, duplicate or invalid source mapping, or block count mismatch cannot be silently accepted.',
        concurrency=3,no_statistical_scoring_in_runner=True))
    seal('corrected_coordinate_and_explicit_model_cohort_frozen_before_calls',[
        core.R/'COHORT-V2-FREEZE.json',RUNS/'MANIFEST.json',Path(__file__).resolve()])
    print(json.dumps(dict(status='FROZEN',pages=len(manifest),model=MODEL,cli_version=VERSION)))

def native_box(box,page):
    sx=page['native_transform']['x_scale'];sy=page['native_transform']['y_scale']
    return [box[0]*sx,box[1]*sy,box[2]*sx,box[3]*sy]

def validate_output(role,data,page):
    w,h=page['raster_width'],page['raster_height']
    assert data['coordinate_system']=='jpeg_raster_xywh' and data['raster_width']==w and data['raster_height']==h
    def good(box):
        return isinstance(box,list) and len(box)==4 and all(type(x) in (int,float) for x in box) and box[0]>=0 and box[1]>=0 and box[2]>0 and box[3]>0 and box[0]+box[2]<=w+.01 and box[1]+box[3]<=h+.01
    if role!='registrar':
        errors=[i for i,p in enumerate(data['picture_elements']) if not good(p['box']) or p['category'] not in ['PL','VE','FG','CE','OT']]
        return dict(status='VALID' if not errors else 'INVALID_COORDINATES',elements=len(data['picture_elements']),invalid_elements=errors,
                    rows=[dict(page=page['page_id'],element=i+1,box=p['box'],native_box=native_box(p['box'],page),category=p['category'],note=p['note']) for i,p in enumerate(data['picture_elements']) if i not in errors])
    meta=json.loads((Path(page['roles']['registrar']['folder'])/'LOCUS-HEADERS.json').read_text(encoding='utf-8'))
    source={u['unit']:u for u in meta['source_units']}
    accepted=[];dropped=[];seen=set();seen_units=set()
    for b in data['blocks']:
        reasons=[]
        if not good(b['box']):reasons.append('block box outside raster')
        if b['status']!='REGISTERED':reasons.append('registrar abstained: '+b['reason'])
        u=source.get(b['source_unit'])
        if u is None:reasons.append('no valid source unit')
        if b['source_unit'] in seen_units:reasons.append('duplicate source unit')
        lines=b['lines']
        if len(lines)!=b['visible_line_count']:reasons.append('visible count differs from returned line rows')
        if [l['ordinal'] for l in lines]!=list(range(1,len(lines)+1)):reasons.append('line ordinals not contiguous')
        if u:
            for reading in ['H','F']:
                expected=[r['locus'] for r in u['ordered_locus_headers'] if reading in r['readings']]
                supplied=[l[reading+'_locus'] for l in lines if l[reading+'_locus'] is not None]
                if expected and (len(lines)!=len(expected) or supplied!=expected):reasons.append(reading+' source count/order mismatch')
                if not expected and supplied:reasons.append(reading+' unexpected loci')
        for line in lines:
            if not good(line['box']):reasons.append('line box outside raster')
            else:
                x,y,bw,bh=b['box'];lx,ly,lw,lh=line['box']
                if lx<x-.01 or ly<y-.01 or lx+lw>x+bw+.01 or ly+lh>y+bh+.01:reasons.append('line box outside its block')
            for reading in ['H','F']:
                loc=line[reading+'_locus']
                if loc is not None and (reading,loc) in seen:reasons.append('duplicate source locus')
        if reasons:
            dropped.append(dict(block_id=b['block_id'],source_unit=b['source_unit'],reasons=sorted(set(reasons))))
        else:
            seen_units.add(b['source_unit'])
            for line in lines:
                for reading in ['H','F']:
                    if line[reading+'_locus'] is not None:seen.add((reading,line[reading+'_locus']))
            accepted.append(b)
    return dict(status='VALIDATED',accepted_blocks=len(accepted),accepted_lines=sum(len(b['lines']) for b in accepted),
        accepted_geometry=accepted,dropped_blocks=dropped,
        source_units_not_registered=sorted(set(source)-{b['source_unit'] for b in accepted}),
        interpretation='Geometry and source-locus validation only; not independent accuracy confirmation or text-outcome scoring.')

def run_call(page,role):
    control=Path(page['roles'][role]['control'])
    receipt_path=control/'RECEIPT.json'
    if receipt_path.exists():return json.loads(receipt_path.read_text(encoding='utf-8'))
    if (control/'START.json').exists():raise RuntimeError('Prior incomplete attempt retained; refusing automatic retry: '+str(control))
    folder=Path(page['roles'][role]['folder'])
    assert {p.name:core.sha(p) for p in folder.iterdir()}==page['roles'][role]['input_files']
    home=ROOT/'runtime'/role/page['page_id'];home.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ);env['CODEX_HOME']=str(home)
    prompt=(control/'PROMPT.txt').read_text(encoding='utf-8')
    assert sha_text(prompt)==page['roles'][role]['prompt_sha256']
    assert core.sha(control/'OUTPUT-SCHEMA.json')==page['roles'][role]['schema_sha256']
    other=ROOT/('rater-A' if role=='registrar' else 'registrar')/page['page_id']/'PAGE.jpg'
    outside=cli.BASE/'control/boundary-probe/outside/CANARY.txt'
    ps=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    quote=lambda x:"'"+str(x).replace("'","''")+"'"
    script="$ErrorActionPreference='Stop'; $r=@{}; try { $r.own_read=[IO.File]::ReadAllBytes("+quote(folder/'PAGE.jpg')+").Length -gt 0 } catch { $r.own_read=$false }; "
    for name,path in [('outside_denied',outside),('other_role_denied',other)]:
        script+='try { $null=[IO.File]::ReadAllBytes('+quote(path)+'); $r.'+name+'=$false } catch { $r.'+name+'=$true }; '
    script+='$r | ConvertTo-Json -Compress'
    command=[str(cli.CODEX),'sandbox',*cfg(folder),'-P','blind','-C',str(folder),'--',str(ps),'-NoProfile','-NonInteractive','-Command',script]
    check=subprocess.run(command,cwd=folder,env=env,capture_output=True,timeout=120)
    (control/'BOUNDARY.stdout.txt').write_bytes(check.stdout);(control/'BOUNDARY.stderr.txt').write_bytes(check.stderr)
    boundary=json.loads(check.stdout) if check.returncode==0 else None
    if check.returncode or not boundary or not all(boundary.values()):raise RuntimeError('Isolation failed for '+str(control))
    audit=subprocess.run([str(cli.CODEX),'--no-daemon','debug','prompt-input',*cfg(folder),'--image',str(folder/'PAGE.jpg'),'--',prompt],cwd=folder,env=env,capture_output=True,timeout=120)
    (control/'RENDERED-PROMPT.json').write_bytes(audit.stdout);(control/'AUDIT.stderr.txt').write_bytes(audit.stderr)
    assert audit.returncode==0
    rendered=json.loads(audit.stdout)
    texts='\n'.join(p.get('text','') for m in rendered for p in m.get('content',[]))
    forbidden=['MEMORY_SUMMARY','memories_v2','Reed mode','JNSQ','sh-qok','sh→qok','Holm p','AMENDMENT-v4.2']
    assert not any(s in texts for s in forbidden)
    assert 'access="deny" escalatable="false"' in texts and '<special>:root</special>' in texts
    assert any(p.get('text')==prompt for m in rendered if m.get('role')=='user' for p in m.get('content',[]))
    assert sum(p.get('type')=='input_image' for m in rendered if m.get('role')=='user' for p in m.get('content',[]))==1
    if role!='registrar':assert (folder/'MANUAL.md').read_bytes()==(core.R/'MANUAL.md').read_bytes()
    command=[str(cli.CODEX),'--no-daemon','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
        '--model',MODEL,'--json','--color','never',*cfg(folder),'--output-schema',str(control/'OUTPUT-SCHEMA.json'),
        '-o',str(control/'FINAL.json'),'--image',str(folder/'PAGE.jpg'),'--','-']
    start=dict(page=page['page_id'],role=role,status='STARTED',utc_started=now(),model_identifier=MODEL,
        server_revision='Not exposed; public identifier explicitly pinned.',cli_version=VERSION,cli_sha256=core.sha(cli.CODEX),
        reasoning_effort=EFFORT,command=command,prompt_sha256=sha_text(prompt),schema_sha256=core.sha(control/'OUTPUT-SCHEMA.json'),
        rendered_prompt_sha256=core.sha(control/'RENDERED-PROMPT.json'),inputs=page['roles'][role]['input_files'],
        boundary_checks=boundary,memory_use=False,memory_generation=False,ephemeral=True)
    dump(control/'START.json',start)
    seal('cohort_v2_'+page['page_id']+'_'+role+'_before_inference',[control/'START.json'])
    auth=home/'auth.json';assert not auth.exists()
    shutil.copyfile(Path(r'C:\Users\lewis\.codex\auth.json'),auth)
    timed_out=False
    try:
        with (control/'EVENTS.jsonl').open('wb') as output,(control/'STDERR.txt').open('wb') as errors:
            try:result=subprocess.run(command,input=prompt.encode('utf-8'),cwd=folder,env=env,stdout=output,stderr=errors,timeout=900)
            except subprocess.TimeoutExpired:result=None;timed_out=True
    finally:
        if auth.exists():auth.unlink()
    events=[];bad_events=0
    for line in (control/'EVENTS.jsonl').read_text(encoding='utf-8').splitlines():
        try:events.append(json.loads(line))
        except Exception:bad_events+=1
    tools=[e for e in events if e.get('item',{}).get('type') in ['command_execution','mcp_tool_call','web_search','file_change','collaboration_tool_call']]
    complete=any(e.get('type')=='turn.completed' for e in events)
    validation=None;parse_error=None
    if (control/'FINAL.json').exists():
        try:validation=validate_output(role,json.loads((control/'FINAL.json').read_text(encoding='utf-8')),page)
        except Exception as exc:parse_error=str(exc)
    ok=bool(result and result.returncode==0 and complete and not tools and not bad_events and validation and validation['status'] in ['VALID','VALIDATED'])
    receipt=start|dict(status='COMPLETED_VALIDATED' if ok else 'FAILED_RETAINED',utc_finished=now(),
        returncode=result.returncode if result else None,timed_out=timed_out,turn_completed=complete,
        observed_tool_events=len(tools),bad_event_lines=bad_events,parse_error=parse_error,validation=validation,
        credential_removed=not auth.exists(),thread_id=next((e['thread_id'] for e in events if e.get('type')=='thread.started'),None),
        artifacts={p.name:core.sha(p) for p in control.iterdir() if p.is_file() and p.name!='RECEIPT.json'})
    dump(receipt_path,receipt)
    seal('cohort_v2_'+page['page_id']+'_'+role+'_response_retained',[receipt_path]+[control/n for n in ['FINAL.json','EVENTS.jsonl','STDERR.txt'] if (control/n).exists()])
    print(json.dumps(dict(page=page['page_id'],role=role,status=receipt['status'],accepted_lines=(validation or {}).get('accepted_lines'),elements=(validation or {}).get('elements')),ensure_ascii=True),flush=True)
    return receipt

def state(manifest,active=None,terminal=False):
    counts=defaultdict(int);accepted=0;elements=defaultdict(int)
    for page in manifest:
        for role in ROLES:
            p=Path(page['roles'][role]['control'])/'RECEIPT.json'
            if p.exists():
                r=json.loads(p.read_text(encoding='utf-8'));counts[role]+=1
                counts['failed']+=r['status']!='COMPLETED_VALIDATED'
                accepted+=(r.get('validation') or {}).get('accepted_lines',0)
                elements[role]+=(r.get('validation') or {}).get('elements',0)
    result=dict(status='COMPLETE' if terminal else 'RUNNING',utc=now(),model=MODEL,cli_version=VERSION,total_pages=len(manifest),
        completed_calls=dict(counts),accepted_registered_lines=accepted,picture_elements=dict(elements),active=active or [],
        first_page='Original failure preserved; not retried.',scientific_results=None,
        note='Counts reflect validated execution and annotations, not independent geometry accuracy or agreement/support tests.')
    dump(RUNS/'RUN-STATE.json',result)
    return result

def run():
    freeze=json.loads((core.R/'COHORT-V2-FREEZE.json').read_text(encoding='utf-8'))
    assert core.sha(RUNS/'MANIFEST.json')==freeze['manifest_sha256']
    assert core.sha(cli.CODEX)==freeze['cli_executable_sha256']
    assert core.sha(core.R/'MANUAL.md')==freeze['manual_sha256']
    manifest=json.loads((RUNS/'MANIFEST.json').read_text(encoding='utf-8'))
    # Keep at most three inference processes active. Registrar gets priority;
    # each page's raters are queued only after its registrar receipt is sealed.
    pending=[(page,'registrar') for page in manifest]
    active={};finished=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        while pending or active:
            while pending and len(active)<3:
                page,role=pending.pop(0)
                future=pool.submit(run_call,page,role);active[future]=(page,role)
            state(manifest,[dict(page=p['page_id'],role=r) for p,r in active.values()])
            done,_=wait(active,timeout=30,return_when=FIRST_COMPLETED)
            for future in done:
                page,role=active.pop(future)
                try:receipt=future.result()
                except Exception as exc:
                    # Infrastructure/isolation exception stops new dispatch;
                    # already running calls finish and retain their own receipts.
                    dump(RUNS/'INFRASTRUCTURE-STOP.json',dict(utc=now(),page=page['page_id'],role=role,error=str(exc)))
                    raise
                if role=='registrar':
                    # All raw ratings remain useful annotation receipts even on
                    # a registrar-abstained page; no source lines are invented.
                    pending[0:0]=[(page,'rater-A'),(page,'rater-B')]
                finished.append((page['page_id'],role,receipt['status']))
    summary=state(manifest,terminal=True)
    seal('remaining_blind_cohort_v2_annotation_calls_complete',[RUNS/'RUN-STATE.json'])
    print(json.dumps(summary),flush=True)

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
