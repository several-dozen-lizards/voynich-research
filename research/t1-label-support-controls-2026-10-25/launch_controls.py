from pathlib import Path
import os,subprocess,sys
P=Path(__file__).parent
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
with (P/'RUN.log').open('ab') as out:result=subprocess.run([sys.executable,'-X','utf8',str(P/'controls.py')],stdout=out,stderr=subprocess.STDOUT,cwd=P.parent,env=env)
print('controls_exit',result.returncode,flush=True);sys.exit(result.returncode)
