import subprocess,sys,time,json
p=subprocess.Popen([sys.executable,"-I","-S","-u","-c","import time; time.sleep(60)"])
print(json.dumps({"descendant_pid":p.pid}),flush=True)
time.sleep(60)
