from pathlib import Path
import psutil,json
P=Path(__file__).parent.resolve();stopped=[]
for process in psutil.process_iter(['pid','name']):
 try:
  if 'python' not in (process.info['name'] or '').lower():continue
  args=process.cmdline()
  if not any(Path(arg).name=='bridge-v5-compiled.py' and Path(arg).resolve().parent==P for arg in args):continue
  children=process.children(recursive=True)
  for child in reversed(children):child.terminate()
  process.terminate();gone,alive=psutil.wait_procs([process]+children,timeout=4)
  for child in alive:child.kill()
  stopped.append(dict(parent=process.pid,children=[x.pid for x in children]))
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
(P/'PURE-EXECUTION-STOP.json').write_text(json.dumps(dict(reason='Exact same-version native accelerator verified; preserve partial pure run and restart same frozen score experiment',stopped=stopped),indent=2)+'\n',encoding='utf-8');print(json.dumps(stopped))
