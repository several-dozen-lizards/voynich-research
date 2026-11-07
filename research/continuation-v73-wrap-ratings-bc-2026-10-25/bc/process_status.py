import psutil,json
out=[]
for p in psutil.process_iter(['pid','name']):
 try:
  if 'python' not in (p.info['name'] or '').lower():continue
  c=p.cmdline()
  if any(str(a).endswith('bridge-v5-compiled.py') or str(a).endswith('launch_bridge.py') for a in c):out.append(dict(pid=p.pid,cpu=list(p.cpu_times()),children=[dict(pid=x.pid,cpu=list(x.cpu_times())) for x in p.children()]))
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
print(json.dumps(out))
