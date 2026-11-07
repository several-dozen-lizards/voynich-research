"""Fresh single-page, picture-only calls. No geometry, text or other ratings reach models."""
from pathlib import Path
import json,subprocess,shutil,uuid,base64,concurrent.futures,hashlib,time
from datetime import datetime,timezone
from agreement import validate_response
R=Path(__file__).resolve().parent;V=R.parent
WORK=Path(r'C:\Users\lewis\.codex\visualizations\2026\10\25\01a170af-9b54-7122-8b1a-552c946aea4c\picture-calls')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
def call_one(job,freeze):
 role,task=job;tid=task['task_id'];result_path=R/'responses'/role/(tid+'.json');attempt_path=R/'attempts'/role/(tid+'.json')
 if result_path.exists():return dict(role=role,task_id=tid,status='EXISTING_RESPONSE_RETAINED')
 if attempt_path.exists():return dict(role=role,task_id=tid,status='PRIOR_TERMINAL_ATTEMPT_RETAINED')
 session=str(uuid.uuid4());folder=WORK/session;folder.mkdir(parents=True,exist_ok=False)
 source=V/'rater-only'/task['image'];assert sha(source)==freeze['image_sha256'][tid]
 image=folder/'image.jpg';shutil.copy2(source,image)
 manual=(R/'MANUAL-RATER.md').read_text(encoding='utf-8');assert sha(R/'MANUAL-RATER.md')==freeze['manual_sha256']
 (folder/'MANUAL.md').write_text(manual,encoding='utf-8')
 # Refuse applicable instruction files; personal instructions must never enter the rater.
 applicable=[Path.home()/'.claude/CLAUDE.md']+[p/'CLAUDE.md' for p in [folder,*folder.parents]]
 assert not any(p.exists() for p in applicable)
 schema=json.loads((R/'RESPONSE-SCHEMA.json').read_text());assert sha(R/'RESPONSE-SCHEMA.json')==freeze['response_schema_sha256']
 executable=shutil.which('claude');assert executable
 cmd=[executable,'--print','--output-format','stream-json','--input-format','stream-json','--verbose','--tools','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--setting-sources','','--disable-slash-commands','--system-prompt',manual,'--json-schema',json.dumps(schema),'--session-id',session,'--model',freeze['models'][role]]
 message=dict(type='user',message=dict(role='user',content=[dict(type='image',source=dict(type='base64',media_type='image/jpeg',data=base64.b64encode(image.read_bytes()).decode()))]))
 started=datetime.now(timezone.utc).isoformat();out='';err='';timeout=False
 try:
  process=subprocess.run(cmd,input=json.dumps(message)+'\n',capture_output=True,text=True,encoding='utf-8',cwd=folder,timeout=240);code=process.returncode;out=process.stdout;err=process.stderr
 except subprocess.TimeoutExpired as e:
  timeout=True;code=None;out=e.stdout or '';err=e.stderr or ''
  if isinstance(out,bytes):out=out.decode('utf-8',errors='replace')
  if isinstance(err,bytes):err=err.decode('utf-8',errors='replace')
 events=[]
 for line in out.splitlines():
  try:events.append(json.loads(line))
  except json.JSONDecodeError:pass
 init=next((e for e in events if e.get('type')=='system' and e.get('subtype')=='init'),{})
 final=next((e for e in reversed(events) if e.get('type')=='result'),{})
 rawdir=R/'raw'/role;rawdir.mkdir(parents=True,exist_ok=True);(rawdir/(tid+'.jsonl')).write_text(out,encoding='utf-8');(rawdir/(tid+'.stderr.txt')).write_text(err,encoding='utf-8')
 record=dict(role=role,task_id=tid,session_id=session,started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),working_directory=str(folder),manual_sha256=freeze['manual_sha256'],image_sha256=sha(image),response_schema_sha256=freeze['response_schema_sha256'],model=init.get('model'),cli_version=init.get('claude_code_version'),available_tools=init.get('tools'),mcp_servers=init.get('mcp_servers'),exit_code=code,timeout=timeout,rerating_or_response_repair='NONE',raw_events_sha256=sha(rawdir/(tid+'.jsonl')),status='FAILED',failure=None,provider_usage=final.get('usage'),provider_cost_estimate_usd=final.get('total_cost_usd'))
 try:
  assert not timeout and code==0,'TRANSPORT_OR_PROCESS_FAILURE'
  assert init.get('model')==freeze['models'][role],'MODEL_MISMATCH'
  assert init.get('tools')==['StructuredOutput'] and init.get('mcp_servers')==[],'ISOLATION_TOOL_VIOLATION'
  assert final.get('subtype')=='success' and not final.get('is_error'),'MODEL_CALL_FAILURE'
  # No execution-capable tool can be present; the sole tool is the output schema.
  for e in events:
   if e.get('type')=='assistant':
    for c in e.get('message',{}).get('content',[]):
     if c.get('type')=='tool_use':assert c.get('name')=='StructuredOutput','UNEXPECTED_TOOL_USE'
  annotation=validate_response(final.get('structured_output'))
  record.update(status='VALID',annotation=annotation);save(result_path,record)
 except (AssertionError,ValueError,TypeError) as e:record['failure']=str(e)
 save(attempt_path,record)
 return dict(role=role,task_id=tid,status=record['status'],failure=record['failure'])
def main():
 freeze=json.loads((R/'RATING-FREEZE.json').read_text());authorization=json.loads((R/'AUTHORIZATION.json').read_text());assert authorization['collection_status']=='AUTHORIZED_COLLECTION'
 for name,digest in freeze['code_sha256'].items():assert sha(R/name)==digest,name
 assert sha(V/'registration/SHARED-LINE-GEOMETRY.json')==freeze['geometry_sha256']
 tasks=json.loads((V/'rater-only/TASKS.json').read_text());assert len(tasks)==168
 jobs=[(role,t) for t in tasks for role in ['A','B']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(call_one,j,freeze) for j in jobs]
  for i,f in enumerate(concurrent.futures.as_completed(futures),1):
   try:row=f.result()
   except Exception as e:
    row=dict(status='RUNNER_ERROR',error=repr(e));save(R/'RUNNER-ERROR.json',row);print(json.dumps(row),flush=True);raise
   with (R/'PROGRESS.jsonl').open('a',encoding='utf-8') as out:out.write(json.dumps(row)+'\n')
   if i%8==0 or row['status']=='FAILED':print(json.dumps(dict(completed=i,total=len(jobs),last=row)),flush=True)
 counts={role:len(list((R/'responses'/role).glob('*.json'))) if (R/'responses'/role).exists() else 0 for role in ['A','B']};save(R/'COLLECTION-STATUS.json',dict(status='ALL PLANNED CALLS TERMINAL; FAILURES RETAINED',valid_pages=counts,planned_calls=len(jobs),adjudication='NOT RUN',outcome_join='NOT RUN',v103='PARKED'));print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
