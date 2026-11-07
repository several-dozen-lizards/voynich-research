"""Frozen synthetic-only T1 scan diagnostic; no source-text access."""
import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import importlib.util,json,hashlib,collections,time
import numpy as np
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
s=importlib.util.spec_from_file_location('old_controls',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
freeze=read(P/'AUDIT-FREEZE.json')
assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in freeze['inputs'].items())
rows=read(OLD/'SUPPORT-ROWS.json');trials=read(OLD/'CONTROL-TRIALS.json');maxline=collections.defaultdict(int)
for r in read(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines']:maxline[(r['task_id'],r['block_id'])]=max(maxline[(r['task_id'],r['block_id'])],r['line_number'])
results=[]
for reading in ('H','F'):
 rr=rows[reading];g=c.Geometry(rr,10000,c.PLAN['seeds']['permutation_'+reading]);assert np.array_equal(g.L,np.load(OLD/('PERMUTATION-'+reading+'.npy')))
 selections=[]
 for scenario,flag in [('independent-null',True),('independent-null',False),('position-null',True)]:
  selections.append(next(t for t in trials if t['reading']==reading and t['scenario']==scenario and t['scan_estimable_classes']==17 and t['scan_family_flag']==flag))
 for t in selections:
  Y=c.simulate(rr,t['scenario'],reading,t['trial'],maxline);tot=np.zeros((g.S,17));np.add.at(tot,g.si,Y[g.keep]);A=(g.assign@Y[g.keep]).reshape(g.B+1,g.S,6,17)
  record=dict(reading=reading,scenario=t['scenario'],trial=t['trial'],flag=t['scan_family_flag'],classes=[])
  for j,feature in enumerate(c.m.CLASSES):
   D=np.zeros((g.B+1,6));V=np.zeros((g.B+1,6,6));active=np.zeros(g.B+1,int)
   for k in range(g.S):
    if g.N[k]<=1 or tot[k,j]==0 or tot[k,j]==g.N[k]:continue
    E=g.E[:,k,:];delta=A[:,k,:,j]-E*tot[k,j]/g.N[k];delta[~g.multi[:,k]]=0.;D+=delta
    cov=-E[:,:,None]*E[:,None,:]/g.N[k]
    for a in range(6):cov[:,a,a]+=E[:,a]
    cov*=tot[k,j]*(g.N[k]-tot[k,j])/(g.N[k]*(g.N[k]-1));cov[~g.multi[:,k]]=0.;V+=cov;active+=g.multi[:,k]
   rank=np.linalg.matrix_rank(V,tol=1e-10);inv=np.linalg.pinv(V,rcond=1e-10);stat=np.einsum('bi,bij,bj->b',D,inv,D);p=(1+sum(stat[1:]>=stat[0]-1e-12))/10001
   ref=c.m.cmh(c.refrows(rr,Y),feature);assert abs(ref['statistic']-stat[0])<1e-8 and ref['rank']==rank[0] and abs(p-t['scan_p'][j])<1e-12
   r0=int(rank[0]);mask=rank[1:]==r0
   record['classes'].append(dict(feature=feature,p=p,holm=t['scan_holm'][j],observed_statistic=float(stat[0]),observed_rank=r0,permuted_rank_counts={str(k):int(v) for k,v in collections.Counter(rank[1:]).items()},permuted_statistic_quantiles=np.quantile(stat[1:],[0,.5,.95,.99,1]).tolist(),rank_matched_count=int(sum(mask)),rank_matched_tail=float((1+sum(stat[1:][mask]>=stat[0]-1e-12))/(1+sum(mask))),active_strata_observed=int(active[0]),permuted_active_strata_quantiles=np.quantile(active[1:],[0,.5,1]).tolist(),observed_rank_trace=float(np.trace(V[0])),mean_permuted_trace=float(np.trace(V[1:],axis1=1,axis2=2).mean()),null_observed_expected_statistic=r0))
  results.append(record);print(reading,t['scenario'],t['trial'],'flag',t['scan_family_flag'],'flagged',[(x['feature'],x['observed_rank'],x['permuted_rank_counts'],x['rank_matched_tail']) for x in record['classes'] if x['holm']<.05],flush=True)
(P/'DIAGNOSTICS.json').write_text(json.dumps(dict(status='COMPLETE',records=results,real_word_classes_computed=0,outcome_join=False,vault='CLOSED'),indent=2)+'
',encoding='utf-8')
