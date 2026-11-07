from pathlib import Path
import os,subprocess,sys
P=Path(__file__).parent
with (P/'REFERENCE-COMPLETE-RUN.log').open('ab') as out:result=subprocess.run([sys.executable,'-X','utf8',str(P/'reference_complete_null_replay.py')],stdout=out,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
print('reference_exit',result.returncode,flush=True);sys.exit(result.returncode)
