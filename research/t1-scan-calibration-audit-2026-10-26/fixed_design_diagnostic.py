"""Causal diagnostic: fixed margins and fixed label exposures, synthetic only."""
import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import importlib.util,json,collections,math
import numpy as np
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
s=importlib.util.spec_from_file_location('c',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
rows=read(OLD/'SUPPORT-ROWS.json');diag=read(P/'DIAGNOSTICS.json');maxline=collections.defaultdict(int)
for r in read(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines']:maxline[(r['task_id'],r['block_id'])]=max(maxline[(r['task_id'],r['block_id'])],r['line_number'])
def setup(rr,Y):
 groups=collections.defaultdict(list)
 for i,r in enumerate(rr):groups[(r['folio'],r['length_bin'])].append(i)
 D=np.zeros((17,6));V=np.zeros((17,6,6));tables=[]
 for k,ix in groups.items():
  n=np.array([sum(rr[i]['n'] for i in ix if rr[i]['label']==l) for l in c.m.LABELS],dtype=np.int64);N=int(sum(n));a=np.array([Y[[i for i in ix if rr[i]['label']==l]].sum(axis=0) if any(rr[i]['label']==l for i in ix) else np.zeros(17,int) for l in c.m.LABELS],int);tot=a.sum(axis=0)
  if N<=1 or sum(n>0)<2:continue
  base=np.diag(n)-np.outer(n,n)/N;factor=tot*(N-tot)/(N*(N-1));D+=(a-n[:,None]*tot/N).T;V+=factor[:,None,None]*base[None,:,:];tables.append((k,n,tot,a))
 inv=np.linalg.pinv(V,rcond=1e-10);stat=np.einsum('qi,qij,qj->q',D,inv,D)
 return tables,D,V,inv,stat
result={'iid_fixed_design':{},'conditional_examples':[]}
for reading in ('H','F'):
 rr=rows[reading];stats=[];Ds=[];Vs=[]
 for trial in range(200):
  Y=c.simulate(rr,'independent-null',reading,trial,maxline);tables,D,V,inv,stat=setup(rr,Y);stats.append(stat);Ds.append(D);Vs.append(V)
 stats=np.array(stats);Ds=np.array(Ds);Vs=np.array(Vs)
 result['iid_fixed_design'][reading]=dict(mean_statistics=stats.mean(axis=0).tolist(),statistic_quantiles=np.quantile(stats,[.5,.95,.99],axis=0).tolist(),mean_D=Ds.mean(axis=0).tolist(),empirical_cov_D=[np.cov(Ds[:,j,:],rowvar=False).tolist() for j in range(17)],mean_CMH_cov=Vs.mean(axis=0).tolist())
 for rec in diag['records']:
  if rec['reading']!=reading:continue
  Y=c.simulate(rr,rec['scenario'],reading,rec['trial'],maxline);tables,D,V,inv,stat=setup(rr,Y);B=10000;rng=np.random.default_rng(c.seed(8251801,reading,rec['scenario'],rec['trial']));nullD=np.zeros((B,17,6))
  for key,n,tot,a in tables:
   N=int(sum(n));expected=n[:,None]*tot/N
   for j in range(17):
    alloc=rng.multivariate_hypergeometric(n,int(tot[j]),size=B,method='marginals');nullD[:,j,:]+=alloc-expected[:,j]
  nullstat=np.einsum('bqi,qij,bqj->bq',nullD,inv,nullD);ps=((nullstat>=stat[None,:]-1e-12).sum(axis=0)+1)/(B+1);holm=c.m.holm(ps.tolist())
  record=dict(reading=reading,scenario=rec['scenario'],trial=rec['trial'],observed_statistics=stat.tolist(),conditional_p=ps.tolist(),conditional_holm=holm,conditional_flag=any(p<.05 for p in holm),old_flag=rec['flag'],conditional_mean_stat=nullstat.mean(axis=0).tolist(),conditional_stat_quantiles=np.quantile(nullstat,[.5,.95,.99,1],axis=0).tolist(),old_p=[v['p'] for v in rec['classes']])
  result['conditional_examples'].append(record);print(reading,rec['scenario'],rec['trial'],'old flag',rec['flag'],'conditional flag',record['conditional_flag'],'old flagged conditional ps',[(c.m.CLASSES[j],rec['classes'][j]['p'],float(ps[j]),float(stat[j])) for j in range(17) if rec['classes'][j]['holm']<.05],flush=True)
(P/'FIXED-DESIGN-DIAGNOSTICS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
