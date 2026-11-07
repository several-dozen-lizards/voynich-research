import subprocess,os
from pathlib import Path
p=Path(__file__).parent
with (p/'REPAIR-RUN.log').open('wb') as log:
 r=subprocess.run([r'C:\Users\lewis\AppData\Local\Programs\Python\Python310\python.exe',str(p/'repaired_controls.py')],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
print('repair_exit',r.returncode,flush=True)
raise SystemExit(r.returncode)
