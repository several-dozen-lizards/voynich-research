"""Analytic mean drift under frozen synthetic position null; no token/class input."""
import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
from collections import defaultdict
import importlib.util,json,numpy as np
P=Path(__file__).parent;ROOT=P.parent;OLD=ROOT/'t1-label-support-controls-2026-10-25'
s=importlib.util.spec_from_file_location('c',OLD/'controls-v2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=lambda p:json.loads(p.read_text(encoding='utf-8'));rows=read(OLD/'SUPPORT-ROWS.json');ml=defaultdict(int)
for r in read(ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json')['lines']:ml[(r['task_id'],r['block_id'])]=max(ml[(r['task_id'],r['block_id'])],r['line_number'])
results={}
for reading,rr in rows.items():
 groups=defaultdict(list)
 for i,r in enumerate(rr):groups[(r['folio'],r['length_bin'])].append(i)
 results[reading]={}
 for scenario in ('independent-null','wrap-null','position-null'):
  means=np.zeros((len(rr),17));variances=np.zeros_like(means)
  for i,r in enumerate(rr):
   if not r['n']:continue
   if scenario=='position-null':
    pos=(np.flatnonzero(r['mask'])+1)/len(r['mask']);factor=(2*pos-1)+(2*r['line_number']/ml[(r['id'].split('/')[0],r['block_id'])]-1)
    po=np.exp(factor[:,None]*c.OP[None,:]);po/=po.sum(axis=1,keepdims=True);pe=np.exp(factor[:,None]*c.END[None,:]);pe/=pe.sum(axis=1,keepdims=True);probs=np.c_[po,pe]
   else:
    po=np.ones(13)/13;pe=np.ones(4)/4
    if scenario=='wrap-null':po=c.probabilities(c.OP,int(r['length_bin']=='short'));pe=c.probabilities(c.END,int(r['length_bin']=='short'))
    probs=np.broadcast_to(np.r_[po,pe],(r['n'],17))
   means[i]=probs.sum(axis=0);variances[i]=(probs*(1-probs)).sum(axis=0)
  D=np.zeros((17,6));V=np.zeros((17,6,6));true_cov=np.zeros_like(V)
  for key,ix in groups.items():
   n=np.array([sum(rr[i]['n'] for i in ix if rr[i]['label']==lab) for lab in c.m.LABELS],float);N=sum(n)
   if N<=1 or sum(n>0)<2:continue
   mu=np.array([sum((means[i] for i in ix if rr[i]['label']==lab),np.zeros(17)) for lab in c.m.LABELS]);vs=np.array([sum((variances[i] for i in ix if rr[i]['label']==lab),np.zeros(17)) for lab in c.m.LABELS]);mt=mu.sum(axis=0);vt=vs.sum(axis=0)
   D+=(mu-n[:,None]*mt/N).T;f=(mt*(N-mt)-vt)/(N*(N-1));V+=f[:,None,None]*(np.diag(n)-np.outer(n,n)/N)[None,:,:]
   C=np.eye(6)-n[:,None]/N
   for j in range(17):true_cov[j]+=C@np.diag(vs[:,j])@C.T
  lam=np.einsum('qi,qij,qj->q',D,np.linalg.pinv(V,rcond=1e-10),D)
  results[reading][scenario]=dict(expected_score=D.tolist(),noncentrality_proxy=lam.tolist(),max_absolute_expected_score=float(np.max(np.abs(D))),expected_working_covariance=V.tolist(),exact_score_covariance=true_cov.tolist())
  if scenario!='position-null':assert np.max(np.abs(D))<1e-10
  print(reading,scenario,'max drift',float(np.max(np.abs(D))),'noncentrality',lam.tolist(),flush=True)
(P/'POSITION-NULL-DRIFT.json').write_text(json.dumps(dict(status='COMPLETE',profiles=results,real_word_classes_computed=0,outcome_join=False,vault='CLOSED'),indent=2)+'\n',encoding='utf-8')
