import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import importlib.util,json,collections,numpy as np
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
s=importlib.util.spec_from_file_location('c',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
d=json.loads((OLD/'SUPPORT-ROWS.json').read_text(encoding='utf-8'));out={}
for reading,rows in d.items():
 g=c.Geometry(rows,10000,c.PLAN['seeds']['permutation_'+reading]);out[reading]=[]
 for k,key in enumerate(g.strata):
  if not g.multi[0,k]:continue
  item=dict(stratum=list(key),original_exposure=g.E[0,k].tolist(),permuted_exposure_median=np.median(g.E[1:,k],axis=0).tolist(),permuted_exposure_min=g.E[1:,k].min(axis=0).tolist(),permuted_exposure_max=g.E[1:,k].max(axis=0).tolist())
  out[reading].append(item)
 print(reading,json.dumps(out[reading]),flush=True)
(P/'EXPOSURE-DIAGNOSTIC.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
