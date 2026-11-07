"""Frozen minimal scan repair: fixed-margin conditional event allocations; synthetic only."""
import sys,os
sys.dont_write_bytecode=True
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,importlib.util,math,time
import numpy as np
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
s=importlib.util.spec_from_file_location('prior',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);m=c.m
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
save=lambda n,v:(P/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
COUNTERS=Counter()
class ConditionalGeometry:
 def __init__(self,rows):
  self.rows=rows;self.groups=defaultdict(list)
  for i,r in enumerate(rows):self.groups[(r['folio'],r['length_bin'])].append(i)
  self.tables=[]
  for key,ix in self.groups.items():
   n=np.array([sum(rows[i]['n'] for i in ix if rows[i]['label']==lab) for lab in m.LABELS],dtype=np.int64)
   if sum(n)<=1 or sum(n>0)<2:continue
   self.tables.append((key,ix,n))
 def reference_allocation(self,Y,j,tables,which):
  z=Y.copy()
  for key,ix,n,tot,allocation in tables:
   remaining=allocation[which].copy()
   for i in ix:
    lab=m.LABELS.index(self.rows[i]['label']);v=min(int(self.rows[i]['n']),int(remaining[lab]));remaining[lab]-=v
    if j<13:z[i,:13]=0;z[i,j]=v;z[i,(j+1)%13]=self.rows[i]['n']-v
    else:z[i,13:]=0;z[i,j]=v;z[i,13+(j-13+1)%4]=self.rows[i]['n']-v
   assert not remaining.any()
  return m.cmh(c.refrows(self.rows,z),m.CLASSES[j])['statistic']
 def scan(self,Y,reading,scenario,trial,audit=False):
  B=10000;ps=[];observed=[];ranks=[];failures=[];nullquantiles=[]
  for j,feature in enumerate(m.CLASSES):
   d=np.zeros(6);V=np.zeros((6,6));fw=defaultdict(float);active=[]
   for key,ix,ni in self.tables:
    n=ni.astype(float);N=float(sum(n));a=np.array([sum(int(Y[i,j]) for i in ix if self.rows[i]['label']==lab) for lab in m.LABELS],float);n1=float(sum(a));n0=N-n1
    if not n1 or not n0:continue
    cov=n1*n0/(N*(N-1))*(np.diag(n)-np.outer(n,n)/N);d+=a-n*n1/N;V+=cov;fw[key[0]]+=float(np.trace(cov));active.append((key,ix,ni,int(n1)))
   total=sum(fw.values());gate=bool(total and len(fw)>=8 and max(fw.values())/total<=.25)
   try:ref=m.cmh(c.refrows(self.rows,Y),feature);refgate=True
   except m.NotEstimable:refgate=False
   COUNTERS['original_observed_support']+=1;assert gate==refgate
   if not gate:ps.append(None);observed.append(None);ranks.append(None);failures.append('observed_support');nullquantiles.append(None);continue
   inv=np.linalg.pinv(V,rcond=1e-10);value=float(d@inv@d);assert abs(value-ref['statistic'])<1e-8;value=ref['statistic'];COUNTERS['original_observed_statistics']+=1
   rank=int(np.linalg.matrix_rank(V,tol=1e-10));assert rank==ref['rank']
   rng=np.random.default_rng(c.seed(c.PLAN['seeds']['permutation_'+reading],'fixed-margins-v1',scenario,trial,feature));nullD=np.zeros((B,6));saved=[]
   for key,ix,n,ntot in active:
    allocation=rng.multivariate_hypergeometric(n,ntot,size=B,method='marginals')
    assert np.all(allocation.sum(axis=1)==ntot) and np.all(allocation>=0) and np.all(allocation<=n[None,:]);COUNTERS['conditional_table_margin_checks']+=B
    nullD+=allocation-n.astype(float)*ntot/float(sum(n))
    if audit:saved.append((key,ix,n,ntot,allocation[[0,-1]]))
   values=np.einsum('bi,ij,bj->b',nullD,inv,nullD)
   # Preserve the original scalar multiplication on every numerical boundary.
   near=np.flatnonzero(np.abs(values-value)<=1e-8)
   for b in near:values[b]=float(nullD[b]@inv@nullD[b])
   COUNTERS['scalar_tie_replays']+=len(near)
   if audit:
    for which,b in ((0,0),(1,B-1)):
     rr=self.reference_allocation(Y,j,saved,which);assert abs(rr-values[b])<1e-8;assert (rr>=value-1e-12)==(values[b]>=value-1e-12);COUNTERS['original_conditional_reference_statistics']+=1
   ps.append((1+int(sum(values>=value-1e-12)))/(B+1));observed.append(value);ranks.append(rank);failures.append(None);nullquantiles.append(np.quantile(values,[.5,.95,.99]).tolist())
  return dict(p=ps,holm=m.holm(ps),observed=observed,rank=ranks,failure=failures,estimable=sum(p is not None for p in ps),null_quantiles=nullquantiles)
def engineering():
 from math import comb
 rng=np.random.default_rng(8251802);n=np.array([2,3,0,0,0,0]);a=rng.multivariate_hypergeometric(n,2,size=10000,method='marginals');pmf=[comb(2,k)*comb(3,2-k)/comb(5,2) for k in range(3)];freq=[int(sum(a[:,0]==k)) for k in range(3)]
 assert np.all(a.sum(axis=1)==2) and np.all(a<=n)
 assert all(abs(f-10000*p)<=6*math.sqrt(10000*p*(1-p))+1 for f,p in zip(freq,pmf))
 save('REPAIR-ENGINEERING.json',dict(status='PASS',toy_exposures=n.tolist(),event_total=2,exact_enumerated_probabilities=pmf,Monte_Carlo_counts=freq,draws=10000,real_feature_inputs=False))
def main():
 start=time.time();freeze=read(P/'AUDIT-FREEZE.json');assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in freeze['inputs'].items())
 seal=read(P/'REPAIR-CODE-SEAL.json');assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in seal['files'].items())
 engineering();data=read(OLD/'SUPPORT-ROWS.json');old={(r['reading'],r['scenario'],r['trial']):r for r in read(OLD/'CONTROL-TRIALS.json')};ml=defaultdict(int)
 for r in read(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines']:ml[(r['task_id'],r['block_id'])]=max(ml[(r['task_id'],r['block_id'])],r['line_number'])
 details=[];summaries={}
 for reading in ('H','F'):
  rows=data[reading];g=ConditionalGeometry(rows)
  for scenario in c.PLAN['scenarios']:
   cell=[]
   for trial in range(200):
    Y=c.simulate(rows,scenario,reading,trial,ml);m.validate(c.refrows(rows,Y));COUNTERS['partition_consistent_observed_datasets']+=1
    try:primary=m.permutation_test(c.refrows(rows,Y),draws=10000,seed=c.seed(8251706,reading,scenario,trial))
    except m.NotEstimable as exc:primary=dict(status='NOT_ESTIMABLE',p=None,reason=str(exc),draws=0)
    previous=old[(reading,scenario,trial)];assert primary==previous['primary'];scan=g.scan(Y,reading,scenario,trial,audit=trial in (0,199));flags=any(p is not None and p<.05 for p in scan['holm']);qflag=scan['holm'][0] is not None and scan['holm'][0]<.05
    row=dict(reading=reading,scenario=scenario,trial=trial,primary=primary,scan_p=scan['p'],scan_holm=scan['holm'],scan_estimable_classes=scan['estimable'],scan_observed_statistic=scan['observed'],scan_rank=scan['rank'],scan_failure=scan['failure'],scan_null_quantiles=scan['null_quantiles'],scan_family_flag=flags,qok_scan_flag=qflag,original_family_flag=previous['scan_family_flag'],original_complete=previous['scan_estimable_classes']==17,original_qok_flag=previous['qok_scan_flag'],synthetic_counts_sha256=hashlib.sha256(Y.astype('<i4').tobytes()).hexdigest());cell.append(row);details.append(row)
    if (trial+1)%50==0:print(reading,scenario,trial+1,'complete',sum(v['scan_estimable_classes']==17 for v in cell),'flags',sum(v['scan_family_flag'] for v in cell),'qok',sum(v['qok_scan_flag'] for v in cell),flush=True)
   complete=sum(v['scan_estimable_classes']==17 for v in cell);flags=sum(v['scan_family_flag'] for v in cell);qflags=sum(v['qok_scan_flag'] for v in cell);pos=scenario=='positive-1.5x';gate=complete==200 and (qflags/200>=.8 if pos else c.wilson(flags,200)[1]<=.05)
   summaries[reading+':'+scenario]=dict(n=200,primary_estimable=0,scan_complete_estimable=complete,scan_family_flags=flags,scan_qok_flags=qflags,scan_unconditional_qok_detection=qflags/200,scan_false_family_flag_rate=flags/200 if not pos and complete==200 else None,scan_Wilson95=c.wilson(flags,200) if not pos and complete==200 else None,scan_gate=gate,original_family_flags=sum(v['original_family_flag'] for v in cell),original_complete=sum(v['original_complete'] for v in cell),original_qok_flags=sum(v['original_qok_flag'] for v in cell),paired_old_flag_new_no_flag=sum(v['original_family_flag'] and not v['scan_family_flag'] for v in cell),paired_old_no_flag_new_flag=sum(not v['original_family_flag'] and v['scan_family_flag'] for v in cell),complete_family_flags=sum(v['scan_family_flag'] for v in cell if v['scan_estimable_classes']==17),per_class_estimable=[sum(v['scan_p'][j] is not None for v in cell) for j in range(17)])
   save('REPAIRED-TRIALS.json',details);save('REPAIRED-SUMMARY.json',summaries);print(reading,scenario,json.dumps(summaries[reading+':'+scenario]),flush=True)
 qualification=dict(status='SCAN_QUALIFIED_ON_DECLARED_SYNTHETIC_PROFILE' if all(v['scan_gate'] for v in summaries.values()) else 'SCAN_NOT_QUALIFIED',T1_primary='NOT_ESTIMABLE',T1_overall='NOT_QUALIFIED',cells=summaries,trials=len(details),oracles=dict(COUNTERS),seconds=time.time()-start,original_failures_preserved=True,real_word_classes_computed=0,outcome_join=False,vault='CLOSED',alpha_V='UNCHANGED_UNSPENT',scope='Exposed paired diagnostic follow-up; fixed-margin exchangeability within folio/wrap, not within-stratum position adjustment')
 save('REPAIRED-QUALIFICATION.json',qualification);print(json.dumps(dict(status=qualification['status'],trials=len(details),seconds=qualification['seconds'])),flush=True)
if __name__=='__main__':main()
