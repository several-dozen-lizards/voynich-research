import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import importlib.util,math,hashlib
import numpy as np
from scipy.stats import chi2
sp=importlib.util.spec_from_file_location('r1_geometry',Path(__file__).resolve().parent.parent/'bq2-replacement-v1/engine.py');r1=importlib.util.module_from_spec(sp);sp.loader.exec_module(r1)
CONTEXTS=r1.CONTEXTS
SCENES=r1.SCENES[:5]+['folio_baseline_homogeneous','stratum_baseline_homogeneous','folio_effect_homogeneous']+r1.SCENES[5:]+['section_baseline_heterogeneous_positive']
class Geometry(r1.Geometry):
 def __init__(self,events):
  super().__init__(events);self.ep=np.array([self.pi[e['folio']] for e in self.events]);self.cells,self.coeff,self.neff=self.pool_design(self.labels)
  strata={}
  self.eg=np.array([strata.setdefault((e['folio'],e['family']),len(strata)) for e in self.events]);self.total_strata=len(strata)
 def pool_design(self,labels):
  dc=np.bincount(labels,weights=self.D,minlength=5);gc=labels[self.gp];n=self.ns+self.nc;coef=np.zeros(len(self.events));coef[self.six]=np.repeat((self.nc/n)/dc[gc],self.ns);coef[self.cix]=-np.repeat((self.ns/n)/dc[gc],self.nc);ec=labels[np.array([self.pi[e['folio']] for e in self.events])];cells=[];neffs=[]
  for c in range(5):
   pair=[];nn=[]
   for x in [0,1]:
    ix=np.where((ec==c)&(self.x==x)&(coef!=0))[0];u=coef[ix]**2;A=float(u.sum());neff=A*A/float((u*u).sum());assert neff>1;pair.append((ix,u,A,neff));nn.append(neff)
   cells.append(pair);neffs.append(nn)
  return cells,coef,neffs
 def support(self):
  result=super().support();result['context_prefix_effective_N_ch_sh']=self.neff;result['maximum_context_leverage']=max(float(self.D[self.labels==c].max()/self.dc[c]) for c in range(5));result['gate']=result['gate'] and all(n>1 for p in self.neff for n in p) and result['maximum_context_leverage']<1;return result
 def raw_terms(self,y):
  ys=np.bincount(self.sg,weights=y[self.six],minlength=len(self.group));yc=np.bincount(self.cg,weights=y[self.cix],minlength=len(self.group));N=np.bincount(self.gp,weights=self.w*(ys/self.ns-yc/self.nc),minlength=len(self.pages));return N
 def moments(self,y,labels=None):
  lab=self.labels if labels is None else labels;cells=self.cells if labels is None else self.pool_design(lab)[0];N=self.raw_terms(y);dc=np.bincount(lab,weights=self.D,minlength=5);nc=np.bincount(lab,weights=N,minlength=5);effect=nc/dc;pool=[];cluster=[];probabilities=[]
  for c in range(5):
   variance=0.;pp=[]
   for ix,u,A,neff in cells[c]:
    rate=float(u@y[ix])/A;mean=(neff*rate+.5)/(neff+1);product=min(.25,mean*(1-mean)/(1-1/neff));variance+=A*product;pp.append(dict(weighted_rate=rate,regularized_rate=mean,effective_N=neff,variance_product=product))
   ix=np.where(lab==c)[0];h=self.D[ix]/dc[c];res=N[ix]-self.D[ix]*effect[c];hc3=float(np.square(res/(1-h)).sum()/dc[c]**2);pool.append(variance);cluster.append(hc3);probabilities.append(pp)
  pool=np.array(pool);cluster=np.array(cluster);variance=np.maximum(pool,cluster);assert np.all(pool>0)&np.isfinite(variance).all();return effect,variance,pool,cluster,probabilities
 def generate(self,scene,seed):
  if scene in r1.SCENES:return super().generate(scene,seed)
  rng=np.random.default_rng(seed)
  if scene=='folio_baseline_homogeneous':prob=rng.choice([.10,.40],size=len(self.pages))[self.ep]+.08*self.x
  elif scene=='stratum_baseline_homogeneous':prob=rng.choice([.08,.42],size=self.total_strata)[self.eg]+.08*self.x
  elif scene=='folio_effect_homogeneous':prob=.20+(.08+rng.choice([-.04,.04],size=len(self.pages))[self.ep])*self.x
  elif scene=='section_baseline_heterogeneous_positive':prob=np.array([.10,.40,.20,.15,.45])[self.ec]+.12*self.x*(self.ec==0)
  else:raise ValueError(scene)
  assert np.all((prob>=0)&(prob<=1));return (rng.random(len(prob))<prob).astype(np.int8)
def statistic(effects,variance):
 T=0.
 for ix in [[0,1,2],[3,4]]:
  w=1/variance[ix];mu=float((w*effects[ix]).sum()/w.sum());T+=float((w*(effects[ix]-mu)**2).sum())
 return T
def scalar(g,y):
 N=[]
 for pg in range(len(g.pages)):
  terms=[]
  for p,f,sh,ch in g.group:
   if p==pg:ns=len(sh);nc=len(ch);terms.append(ns*nc/(ns+nc)*(math.fsum(float(y[i]) for i in sh)/ns-math.fsum(float(y[i]) for i in ch)/nc))
  N.append(math.fsum(terms))
 effects=[];variances=[]
 for c in range(5):
  pages=[i for i,cc in enumerate(g.labels) if cc==c];D=math.fsum(float(g.D[i]) for i in pages);rd=math.fsum(N[i] for i in pages)/D;pooled=0.
  for ix,u,A,n in g.cells[c]:
   r=math.fsum(float(uu)*float(y[i]) for i,uu in zip(ix,u))/A;m=(n*r+.5)/(n+1);pooled+=A*min(.25,m*(1-m)/(1-1/n))
  cluster=math.fsum(((N[i]-float(g.D[i])*rd)/(1-float(g.D[i])/D))**2 for i in pages)/D**2;effects.append(rd);variances.append(max(pooled,cluster))
 value=0.
 for ix in [[0,1,2],[3,4]]:
  mu=math.fsum(effects[i]/variances[i] for i in ix)/math.fsum(1/variances[i] for i in ix);value+=math.fsum((effects[i]-mu)**2/variances[i] for i in ix)
 return value,effects,variances
def test(g,y,probe=False):
 effects,var,pool,cluster,probs=g.moments(y);T=statistic(effects,var);p=float(chi2.sf(T,3));uniform=bool(np.all(y[np.r_[g.six,g.cix]]==y[np.r_[g.six,g.cix]][0]));err=None
 if probe:
  val,ef,vv=scalar(g,y);err=max(abs(val-T),float(np.abs(np.array(ef)-effects).max()),float(np.abs(np.array(vv)-var).max()));assert err<1e-10*max(1,T)
 return dict(T=T,df=3,p=p,flag=p<=.025,informative_outcomes_uniform=uniform,context_effects=effects.tolist(),context_variances=var.tolist(),pooled_variances=pool.tolist(),HC3_variances=cluster.tolist(),HC3_dominates=(cluster>pool).tolist(),pooled_probability_details=probs,outcome_sha256=hashlib.sha256(y.tobytes()).hexdigest(),scalar_error=err)
