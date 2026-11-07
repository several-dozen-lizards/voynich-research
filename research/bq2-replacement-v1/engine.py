import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np
import math,collections,hashlib
CONTEXTS=['C1','C2','C3','C4','C5'];B=10000
SCENES=['homogeneous_null','homogeneous_positive','scribe_baseline_homogeneous','section_baseline_homogeneous','available_homogeneous','heterogeneous_positive','available_heterogeneous_positive']
class Geometry:
 def __init__(self,events):
  groups=collections.defaultdict(list)
  for i,e in enumerate(events):groups[e['folio'],e['family']].append(i)
  supported=set()
  for (pg,f),ix in groups.items():
   ns=sum(events[i]['x'] for i in ix)
   if 0<ns<len(ix):supported.add(pg)
  self.events=[e for e in events if e['folio'] in supported];self.pages=sorted(supported);self.pi={pg:i for i,pg in enumerate(self.pages)}
  self.labels=np.array([CONTEXTS.index(next(e['context'] for e in self.events if e['folio']==pg)) for pg in self.pages]);self.hands=np.array([2 if c<3 else 3 for c in self.labels]);self.x=np.array([e['x'] for e in self.events]);self.av=np.array([e['available'] for e in self.events]);self.ec=np.array([CONTEXTS.index(e['context']) for e in self.events])
  gg=collections.defaultdict(list)
  for i,e in enumerate(self.events):gg[e['folio'],e['family']].append(i)
  self.group=[]
  for (pg,f),ix in gg.items():
   sh=[i for i in ix if self.events[i]['x']];ch=[i for i in ix if not self.events[i]['x']]
   if sh and ch:self.group.append((self.pi[pg],f,sh,ch))
  self.ns=np.array([len(z[2]) for z in self.group]);self.nc=np.array([len(z[3]) for z in self.group]);self.gp=np.array([z[0] for z in self.group]);self.w=self.ns*self.nc/(self.ns+self.nc);self.D=np.bincount(self.gp,weights=self.w,minlength=len(self.pages));self.dc=np.bincount(self.labels,weights=self.D,minlength=5)
  self.six=np.array([i for z in self.group for i in z[2]]);self.cix=np.array([i for z in self.group for i in z[3]]);self.sg=np.repeat(np.arange(len(self.group)),self.ns);self.cg=np.repeat(np.arange(len(self.group)),self.nc)
  avgsh=np.bincount(self.sg,weights=self.av[self.six],minlength=len(self.group))/self.ns;avgch=np.bincount(self.cg,weights=self.av[self.cix],minlength=len(self.group))/self.nc;gc=self.labels[self.gp]
  self.fsh=np.bincount(gc,weights=self.w*avgsh,minlength=5)/self.dc;self.fch=np.bincount(gc,weights=self.w*avgch,minlength=5)/self.dc
 def support(self):
  counts={c:int((self.labels==j).sum()) for j,c in enumerate(CONTEXTS)};feasible=bool(np.all(self.fsh>=.32)&np.all(self.fch>=.20))
  return dict(supported_folios=len(self.pages),eligible_events=len(self.events),discordant_strata=len(self.group),context_pages=counts,context_V={c:float(self.dc[j]) for j,c in enumerate(CONTEXTS)},minimum_page_V=float(self.D.min()),max_page_shares={c:float(self.D[self.labels==j].max()/self.dc[j]) for j,c in enumerate(CONTEXTS)},weighted_available_sh=self.fsh.tolist(),weighted_available_ch=self.fch.tolist(),available_control_feasible=feasible,gate=all(n>=2 for n in counts.values()) and bool(np.all(self.D>0)) and feasible,pages=self.pages)
 def terms(self,y):
  ys=np.bincount(self.sg,weights=y[self.six],minlength=len(self.group));yc=np.bincount(self.cg,weights=y[self.cix],minlength=len(self.group));ps=(ys+.5)/(self.ns+1);pc=(yc+.5)/(self.nc+1);n=self.ns+self.nc
  Ng=self.w*(ys/self.ns-yc/self.nc);Vg=(self.nc/n)**2*self.ns*ps*(1-ps)+(self.ns/n)**2*self.nc*pc*(1-pc)
  N=np.bincount(self.gp,weights=Ng,minlength=len(self.pages));V=np.bincount(self.gp,weights=Vg,minlength=len(self.pages));assert np.isfinite(N).all() and np.isfinite(V).all() and np.all(V>0)
  return N,V
 def generate(self,scene,seed):
  rng=np.random.default_rng(seed);x=self.x;c=self.ec
  if scene=='homogeneous_null':prob=np.full(len(x),.2)
  elif scene=='homogeneous_positive':prob=.2+.08*x
  elif scene=='scribe_baseline_homogeneous':prob=np.where(c<3,.12,.40)+.08*x
  elif scene=='section_baseline_homogeneous':prob=np.array([.10,.40,.20,.15,.45])[c]+.08*x
  elif scene=='heterogeneous_positive':prob=.2+.12*x*(c==0)
  elif scene in ['available_homogeneous','available_heterogeneous_positive']:
   assert self.support()['available_control_feasible'];target=np.full(5,.28) if scene=='available_homogeneous' else np.array([.32,.20,.20,.20,.20]);prob=np.where(x==1,(target/self.fsh)[c],(.20/self.fch)[c])*self.av
  else:raise ValueError(scene)
  assert np.all((0<=prob)&(prob<=1));y=(rng.random(len(x))<prob).astype(np.int8)
  if scene.startswith('available_'):assert not y[~self.av].any()
  return y
def labels_bank(g,seed):
 rng=np.random.default_rng(seed);mat=np.tile(g.labels,(B+1,1))
 for hand in [2,3]:
  ix=np.where(g.hands==hand)[0];mat[1:,ix]=rng.permuted(np.tile(g.labels[ix],(B,1)),axis=1)
 return mat
def statistic(g,N,V,mat):
 quantities=np.column_stack([N,g.D,V]);effects=[];weights=[]
 for j in range(5):
  vals=(mat==j).astype(float)@quantities;nc,dc,vc=vals.T;assert np.all(dc>0)&np.all(vc>0);effects.append(nc/dc);weights.append(dc**2/vc)
 effects=np.array(effects).T;weights=np.array(weights).T;scores=np.zeros(len(mat))
 for ix in [[0,1,2],[3,4]]:
  mu=(weights[:,ix]*effects[:,ix]).sum(axis=1)/weights[:,ix].sum(axis=1);scores+=(weights[:,ix]*(effects[:,ix]-mu[:,None])**2).sum(axis=1)
 assert np.isfinite(scores).all() and np.all(scores>=0)
 return scores,effects[0],1/weights[0]
def scalar(g,N,V,labels):
 effects=[];weights=[]
 for j in range(5):
  ix=[i for i,c in enumerate(labels) if c==j];d=math.fsum(float(g.D[i]) for i in ix);n=math.fsum(float(N[i]) for i in ix);v=math.fsum(float(V[i]) for i in ix);effects.append(n/d);weights.append(d*d/v)
 total=0.
 for ix in [[0,1,2],[3,4]]:
  mu=math.fsum(weights[j]*effects[j] for j in ix)/math.fsum(weights[j] for j in ix);total+=math.fsum(weights[j]*(effects[j]-mu)**2 for j in ix)
 return total
def test(g,y,seed,probe=False):
 N,V=g.terms(y);mat=labels_bank(g,seed);scores,effects,vars=statistic(g,N,V,mat);tol=128*np.finfo(float).eps*max(1.,float(scores.max()));k=int((scores[1:]>=scores[0]-tol).sum());p=(1+k)/(B+1);degenerate=bool(scores.max()-scores.min()<=tol)
 if probe:
  indices=sorted(set([0,*range(1,33),int(scores.argmin()),int(scores.argmax()),int(np.abs(scores[1:]-scores[0]).argmin())+1]));error=max(abs(float(scores[i])-scalar(g,N,V,mat[i])) for i in indices);assert error<=1e-10*max(1,float(scores.max()))
 else:error=None
 return dict(p=p,Q=float(scores[0]),exceedances=k,shuffles=B,flag=p<=.025,degenerate=degenerate,minimum_working_page_variance=float(V.min()),Q_range=[float(scores.min()),float(scores.max())],score_tolerance=tol,permutation_Q_sha256=hashlib.sha256(scores.tobytes()).hexdigest(),outcome_sha256=hashlib.sha256(y.tobytes()).hexdigest(),context_effects=effects.tolist(),context_working_variances=vars.tolist(),scalar_probe_error=error)
