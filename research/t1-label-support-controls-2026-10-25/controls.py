"""T1 synthetic controls at fixed real support. No native text loader or real feature input."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict,Counter
import copy,hashlib,importlib.util,json,math,time
import numpy as np
from scipy.sparse import csr_matrix
P=Path(__file__).parent;ROOT=P.parent
s=importlib.util.spec_from_file_location('frozen_t1',ROOT/'priority-continuation-2026-10-25/T1-freeze/methods.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
PLAN=json.loads((P/'CONTROL-FREEZE.json').read_text(encoding='utf-8'))
ORACLES=Counter()
def save(name,obj):(P/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def seed(*p):return int.from_bytes(hashlib.sha256(':'.join(map(str,p)).encode()).digest()[:8],'big')
def wilson(k,n):
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0.,c-r),min(1.,c+r)]

def refrows(rows,events,labels=None):
 return [dict(id=r['id'],folio=r['folio'],reading=r['reading'],label=m.LABELS[int(labels[i])] if labels is not None else r['label'],length_bin=r['length_bin'],n=r['n'],counts={k:int(v) for k,v in zip(m.CLASSES,events[i])}) for i,r in enumerate(rows)]

class Geometry:
 def __init__(self,rows,B=10000,bank_seed=8251702):
  self.rows=rows;self.n=np.array([r['n'] for r in rows],dtype=np.float64);self.labels=np.array([m.LABELS.index(r['label']) for r in rows],dtype=np.uint8)
  groups=defaultdict(list)
  for i,r in enumerate(rows):groups[r['folio']].append(i)
  self.groups=list(groups.values());self.B=B;self.L=np.empty((B+1,len(rows)),dtype=np.uint8);self.L[0]=self.labels;rng=np.random.default_rng(bank_seed)
  for b in range(1,B+1):
   self.L[b]=self.labels
   for ix in self.groups:
    labels=self.labels[ix].tolist();rng.shuffle(labels);self.L[b,ix]=labels
  keepfolios={folio for folio,ix in groups.items() if len(set(self.labels[ix]))>=2}
  self.keep=np.array([i for i,r in enumerate(rows) if r['folio'] in keepfolios],dtype=np.int32);rr=[rows[i] for i in self.keep]
  self.strata=list(dict.fromkeys((r['folio'],r['length_bin']) for r in rr));self.folios=list(dict.fromkeys(r['folio'] for r in rr));sd={v:i for i,v in enumerate(self.strata)};fd={v:i for i,v in enumerate(self.folios)}
  self.si=np.array([sd[(r['folio'],r['length_bin'])] for r in rr],dtype=np.int32);self.sf=np.array([fd[f] for f,b in self.strata],dtype=np.int32);self.S=len(self.strata);self.F=len(self.folios);self.N=np.bincount(self.si,weights=self.n[self.keep],minlength=self.S);self.Nsafe=np.where(self.N>0,self.N,1.)
  self.E=np.empty((B+1,self.S,6))
  for b in range(B+1):self.E[b]=np.bincount(self.si*6+self.L[b,self.keep],weights=self.n[self.keep],minlength=self.S*6).reshape(self.S,6)
  self.multi=np.count_nonzero(self.E,axis=2)>=2
  self.trace=self.Nsafe[None,:]-(self.E*self.E).sum(axis=2)/self.Nsafe[None,:];self.trace[~self.multi]=0.;self.trace[:,self.N<=1]=0.
  assert np.min(self.trace)>=-1e-12
  # One immutable sparse assignment represents every label/stratum/line permutation.
  loc=np.arange(B+1,dtype=np.int32)[:,None]*(self.S*6)+self.si[None,:]*6+self.L[:,self.keep]
  cols=np.broadcast_to(np.arange(len(self.keep),dtype=np.int32),loc.shape)
  self.assign=csr_matrix((np.ones(loc.size,dtype=np.int8),(loc.ravel(),cols.ravel())),shape=((B+1)*self.S*6,len(self.keep)))
 def weights(self,cs,start,stop):
  result=np.zeros((stop-start,self.F,cs.shape[1]))
  for s,f in enumerate(self.sf):result[:,f,:]+=self.trace[start:stop,s,None]*cs[None,s,:]
  total=result.sum(axis=1);count=(result>0).sum(axis=1);mx=np.divide(result.max(axis=1),total,out=np.full_like(total,np.inf),where=total>0)
  return (count>=8)&(mx<=.25),mx
 def scan(self,events):
  Y=np.asarray(events,dtype=np.int32);Q=17;tot=np.zeros((self.S,Q),dtype=np.float64)
  np.add.at(tot,self.si,Y[self.keep]);cs=np.zeros_like(tot);valid=self.N>1
  cs[valid]=tot[valid]*(self.N[valid,None]-tot[valid])/(self.N[valid,None]*(self.N[valid,None]-1))
  observed,_=self.weights(cs,0,1);eligible=observed[0].copy();failure=np.full(Q,-2,dtype=int);failure[eligible]=-1
  for start in range(1,self.B+1,64):
   jj=np.flatnonzero(eligible)
   if not len(jj):break
   gates,_=self.weights(cs[:,jj],start,min(self.B+1,start+64))
   for local,j in enumerate(jj):
    bad=np.flatnonzero(~gates[:,local])
    if len(bad):failure[j]=start+int(bad[0]);eligible[j]=False
  js=np.flatnonzero(eligible);stats={};ps=[None]*17;fallbacks=0
  if len(js):
   A=(self.assign@Y[self.keep][:,js]).reshape(self.B+1,self.S,6,len(js))
   for local,j in enumerate(js):
    D=np.zeros((self.B+1,6));V=np.zeros((self.B+1,6,6))
    for s in range(self.S):
     if not cs[s,j]:continue
     E=self.E[:,s,:];delta=A[:,s,:,local]-E*tot[s,j]/self.N[s];delta[~self.multi[:,s]]=0.;D+=delta
     cov=-E[:,:,None]*E[:,None,:]/self.N[s]
     for c in range(6):cov[:,c,c]+=E[:,c]
     cov*=cs[s,j];cov[~self.multi[:,s]]=0.;V+=cov
    inv=np.linalg.pinv(V,rcond=1e-10);mid=np.matmul(D[:,None,:],inv);values=np.matmul(mid,D[:,:,None])[:,0,0]
    # The frozen reference sets the observed value and resolves every numerical tie neighborhood.
    observed_ref=m.cmh(refrows(self.rows,Y),m.CLASSES[j])['statistic'];ORACLES['observed_statistic']+=1
    assert abs(values[0]-observed_ref)<1e-8
    near=np.flatnonzero(np.abs(values[1:]-observed_ref)<=1e-8)+1
    for b in near:values[b]=m.cmh(refrows(self.rows,Y,self.L[b]),m.CLASSES[j])['statistic'];ORACLES['tie_replays']+=1;fallbacks+=1
    values[0]=observed_ref;ps[j]=(1+int((values[1:]>=observed_ref-1e-12).sum()))/(self.B+1);stats[int(j)]=values
  return dict(p=ps,holm=m.holm(ps),failure=failure.tolist(),estimable=int(sum(p is not None for p in ps)),stats=stats,tie_replays=fallbacks)
 def audit(self,events,result,all_classes=True):
  for j in range(17) if all_classes else (0,13):
   fail=result['failure'][j];b=0 if fail==-2 else fail if fail>=1 else 0
   rr=refrows(self.rows,events,self.L[b]);expected_undefined=fail!=-1
   try:value=m.cmh(rr,m.CLASSES[j]);undefined=False
   except m.NotEstimable:undefined=True
   assert undefined==expected_undefined,(j,fail,undefined)
   if not undefined:assert abs(value['statistic']-result['stats'][j][b])<1e-8
   ORACLES['support_and_statistic']+=1
   if fail==-1:
    for ix in (1,self.B):
     got=m.cmh(refrows(self.rows,events,self.L[ix]),m.CLASSES[j])['statistic'];assert abs(got-result['stats'][j][ix])<1e-8;ORACLES['permuted_statistic']+=1

OP=np.linspace(-math.log(2),math.log(2),13);END=np.linspace(-math.log(1.5),math.log(1.5),4)
def probabilities(slopes,factor):
 v=np.exp(slopes*factor);return v/v.sum(axis=-1,keepdims=True)
def simulate(rows,scenario,reading,trial,maxline):
 rng=np.random.default_rng(seed(PLAN['seeds']['data_base'],scenario,reading,trial));latent_rng=np.random.default_rng(seed(PLAN['seeds']['data_base'],'latent',scenario,trial));folios=sorted({r['folio'] for r in rows});latent={f:latent_rng.normal()/1.959963984540054 for f in folios};Y=np.zeros((len(rows),17),dtype=np.int32)
 for i,r in enumerate(rows):
  n=r['n']
  if not n:continue
  if scenario=='position-null':
   pos=(np.flatnonzero(r['mask'])+1)/len(r['mask']);task=r['id'].split('/')[0];linefrac=r['line_number']/maxline[(task,r['block_id'])];factor=(2*pos-1)+(2*linefrac-1)
   po=np.exp(factor[:,None]*OP[None,:]);po/=po.sum(axis=1,keepdims=True);pe=np.exp(factor[:,None]*END[None,:]);pe/=pe.sum(axis=1,keepdims=True)
   io=(rng.random(n)[:,None]>po.cumsum(axis=1)).sum(axis=1);ie=(rng.random(n)[:,None]>pe.cumsum(axis=1)).sum(axis=1);Y[i,:13]=np.bincount(io,minlength=13);Y[i,13:]=np.bincount(ie,minlength=4)
  else:
   po=np.full(13,1/13);pe=np.full(4,1/4)
   if scenario=='wrap-null':po=probabilities(OP,int(r['length_bin']=='short'));pe=probabilities(END,int(r['length_bin']=='short'))
   elif scenario=='folio-latent-null':po=probabilities(OP,latent[r['folio']]);pe=probabilities(END,latent[r['folio']])
   elif scenario=='positive-1.5x' and r['label'] in ('FG','VE'):po[0]=1.5/13;po[1:]=(1-po[0])/12
   Y[i,:13]=rng.multinomial(n,po);Y[i,13:]=rng.multinomial(n,pe)
 return Y

def engineering():
 rng=np.random.default_rng(8251704);rows=[]
 for f in range(12):
  for label in m.LABELS:
   rows.append(dict(id=f'e{f}:{label}',folio='engineering'+str(f),reading='H',label=label,length_bin='normal',n=60))
 g=Geometry(rows,B=20,bank_seed=8251705);Y=np.array([np.r_[rng.multinomial(60,np.ones(13)/13),rng.multinomial(60,np.ones(4)/4)] for r in rows]);result=g.scan(Y);g.audit(Y,result)
 # Exact permutation stream replay against the untouched frozen implementation.
 rr=refrows(rows,Y);rrng=np.random.default_rng(8251705)
 for b in range(1,21):
  perm=m.permute(rr,rrng);assert [m.LABELS.index(r['label']) for r in perm]==g.L[b].tolist();ORACLES['permutation_order']+=1
 save('ENGINEERING.json',dict(status='PASS',oracles=dict(ORACLES),real_feature_data_read=False))

def main():
 begin=time.time();engineering();data=json.loads((P/'SUPPORT-ROWS.json').read_text(encoding='utf-8'));geometry=json.loads((ROOT/'image-context-v4/registration/SHARED-LINE-GEOMETRY.json').read_text(encoding='utf-8'))['lines'];maxline=defaultdict(int)
 for r in geometry:maxline[(r['task_id'],r['block_id'])]=max(maxline[(r['task_id'],r['block_id'])],r['line_number'])
 summaries={};details=[]
 for reading in ('H','F'):
  rows=data[reading];g=Geometry(rows,10000,PLAN['seeds']['permutation_'+reading]);np.save(P/('PERMUTATION-'+reading+'.npy'),g.L)
  for scenario in PLAN['scenarios']:
   cell=[]
   for trial in range(200):
    Y=simulate(rows,scenario,reading,trial,maxline)
    # Probe the actual frozen primary engine: all source support counts remain real, outcomes synthetic.
    try:primary=m.permutation_test(refrows(rows,Y),draws=10000,seed=seed(8251706,reading,scenario,trial))
    except m.NotEstimable as exc:primary=dict(status='NOT_ESTIMABLE',p=None,reason=str(exc),draws=0)
    scan=g.scan(Y)
    if trial in (0,199):g.audit(Y,scan)
    row=dict(reading=reading,scenario=scenario,trial=trial,primary=primary,scan_p=scan['p'],scan_holm=scan['holm'],scan_estimable_classes=scan['estimable'],scan_first_failure=scan['failure'],scan_family_flag=any(p is not None and p<.05 for p in scan['holm']),qok_scan_flag=scan['holm'][0] is not None and scan['holm'][0]<.05)
    cell.append(row);details.append(row)
    if (trial+1)%50==0:print(reading,scenario,trial+1,'primary_defined',sum(r['primary'].get('p') is not None for r in cell),'scan_complete',sum(r['scan_estimable_classes']==17 for r in cell),flush=True)
   pe=sum(r['primary'].get('p') is not None for r in cell);pf=sum(r['primary'].get('p') is not None and r['primary']['p']<.05 for r in cell);se=sum(r['scan_estimable_classes']==17 for r in cell);sf=sum(r['scan_family_flag'] for r in cell);qp=sum(r['qok_scan_flag'] for r in cell);positive=scenario=='positive-1.5x'
   result=dict(n=200,primary_estimable=pe,primary_flags=pf,primary_unconditional_detection=pf/200,primary_false_flag_rate=pf/200 if pe==200 and not positive else None,primary_Wilson95=wilson(pf,200) if pe==200 else None,primary_gate=(pf/200>=.8 and pe==200) if positive else (pe==200 and wilson(pf,200)[1]<=.05),scan_complete_estimable=se,scan_family_flags=sf,scan_qok_flags=qp,scan_unconditional_qok_detection=qp/200,scan_false_family_flag_rate=sf/200 if se==200 and not positive else None,scan_Wilson95=wilson(sf,200) if se==200 else None,scan_gate=(qp/200>=.8 and se==200) if positive else (se==200 and wilson(sf,200)[1]<=.05),per_class_estimable=[sum(r['scan_p'][j] is not None for r in cell) for j in range(17)],per_class_flags=[sum(r['scan_holm'][j] is not None and r['scan_holm'][j]<.05 for r in cell) for j in range(17)],undefined_results_are_not_validated_negatives=True)
   summaries[reading+':'+scenario]=result;save('CONTROL-TRIALS.json',details);save('CONTROL-SUMMARY.json',summaries);print(reading,scenario,json.dumps(result),flush=True)
 out=dict(status='QUALIFIED_ON_DECLARED_REAL_SUPPORT_SYNTHETIC_PROFILE' if all(v['primary_gate'] and v['scan_gate'] for v in summaries.values()) else 'NOT_QUALIFIED_ON_DECLARED_REAL_SUPPORT',cells=summaries,trials=len(details),oracles=dict(ORACLES),seconds=time.time()-begin,real_word_classes_computed=0,real_word_outcome_join=False,vault='CLOSED',scope='Exact-consensus geometry, real readability masks and positions; synthetic uniform13/4 baseline only; no real prevalence calibration',invariance='UNRESOLVED: all15 pair design gate fails; no unsupported bootstrap or invariant claim')
 save('QUALIFICATION.json',out);print(json.dumps(dict(status=out['status'],trials=out['trials'],oracles=out['oracles'],seconds=out['seconds'])),flush=True)
if __name__=='__main__':main()
