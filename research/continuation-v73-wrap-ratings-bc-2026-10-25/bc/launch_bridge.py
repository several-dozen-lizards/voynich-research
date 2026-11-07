import subprocess,sys
from pathlib import Path
P=Path(__file__).parent
with (P/'E2-RUN-v5.log').open('ab') as log:
 result=subprocess.run([sys.executable,'-X','utf8',str(P/'bridge-v5-compiled.py')],stdout=log,stderr=subprocess.STDOUT,cwd=P.parents[1])
print('bridge_exit',result.returncode,flush=True)
sys.exit(result.returncode)
