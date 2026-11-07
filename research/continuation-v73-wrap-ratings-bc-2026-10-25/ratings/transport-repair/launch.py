from pathlib import Path
import subprocess,sys
P=Path(__file__).parent
with (P/'RUN.log').open('ab') as log:
 p=subprocess.run([sys.executable,'-X','utf8',str(P/'complete.py')],stdout=log,stderr=subprocess.STDOUT,cwd=P.parents[2])
 print('completion_exit',p.returncode,flush=True)
 sys.exit(p.returncode)
