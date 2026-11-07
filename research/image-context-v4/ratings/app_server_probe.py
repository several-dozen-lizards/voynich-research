"""Inspect fresh no-environment app-server context using synthetic input only."""
from pathlib import Path
import json,subprocess,shutil,queue,threading,time,base64
from isolation_probe import W,options
R=Path(__file__).resolve().parent
def main():
 exe=shutil.which('codex');log=[];q=queue.Queue()
 proc=subprocess.Popen([exe,'app-server',*options()],cwd=W,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
 def reader():
  for line in proc.stdout:
   try:q.put(json.loads(line))
   except json.JSONDecodeError:pass
 threading.Thread(target=reader,daemon=True).start()
 def send(x):proc.stdin.write(json.dumps(x)+'\n');proc.stdin.flush()
 def request(i,method,params):
  send(dict(id=i,method=method,params=params));deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   msg=q.get(timeout=max(.01,deadline-time.monotonic()));log.append(msg)
   if msg.get('id')==i:
    if 'error' in msg:raise RuntimeError(str(msg['error']))
    return msg['result']
  raise TimeoutError(method)
 try:
  request(1,'initialize',dict(clientInfo=dict(name='image_isolation_probe',version='1'),capabilities=dict(experimentalApi=True)));send(dict(method='initialized'))
  models=request(2,'model/list',dict(limit=100,includeHidden=False))
  safe_models=[{k:x.get(k) for k in ['id','model','inputModalities','defaultReasoningEffort','isDefault']} for x in models['data']]
  (R/'available-vision-models.json').write_text(json.dumps(safe_models,indent=2),encoding='utf-8')
  manual=(W/'MANUAL.md').read_text(encoding='utf-8')
  started=request(3,'thread/start',dict(ephemeral=True,cwd=str(W),environments=[],selectedCapabilityRoots=[],dynamicTools=[],baseInstructions=manual,developerInstructions='',approvalPolicy='never',sandbox='read-only',experimentalRawEvents=True))
  (R/'app-probe-start.json').write_text(json.dumps(started,indent=2),encoding='utf-8')
  sources=started.get('instructionSources',[])
  print(json.dumps(dict(stage='start',model=started['model'],instructionSources=sources,ephemeral=started['thread'].get('ephemeral'))),flush=True)
  if sources:print('PROBE_STOPPED: additional instruction sources present.',flush=True);return
  schema=json.loads((W/'schema.json').read_text())
  image='data:image/png;base64,'+base64.b64encode((W/'image.png').read_bytes()).decode()
  result=request(4,'turn/start',dict(threadId=started['thread']['id'],environments=[],input=[dict(type='image',url=image)],outputSchema=schema))
  deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   msg=q.get(timeout=max(.01,deadline-time.monotonic()));log.append(msg)
   if msg.get('method')=='turn/completed':print(json.dumps(dict(stage='complete',status=msg['params']['turn']['status'])),flush=True);break
 finally:
  (R/'app-probe-events.json').write_text(json.dumps(log,indent=2),encoding='utf-8');proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
  (R/'app-probe-stderr.txt').write_text(proc.stderr.read(),encoding='utf-8')
if __name__=='__main__':main()
