import collections,random
import numpy as np
from scipy.stats import rankdata
TARGETS=['ol','qokedy','qol']
LABELS=['ol -> qokedy minus reverse','ol -> qol minus reverse','qokedy -> qol minus reverse','ol -> other two minus incoming','qokedy -> other two minus incoming','qol -> other two minus incoming']
def buckets(rows,mode):
 g=collections.defaultdict(list)
 for ri,r in enumerate(rows):
  ws=r['tokens'];n=len(ws)
  if mode=='exact_slot':
   mask=tuple(i for i,w in enumerate(ws) if w is None)
   for i,w in enumerate(ws):
    if w is not None:g[(r['page'],n,i,mask)].append((ri,i))
  else:
   start=1
   for i in range(1,n):
    if i<n-1 and ws[i] is not None:continue
    if i>start:g[(ri,start,i)]=[(ri,k) for k in range(start,i)]
    start=i+1
 return [b for b in g.values() if len(b)>=2]
def shuffled(rows,bs,rng):
 out=[r['tokens'][:] for r in rows]
 for b in bs:
  vs=[rows[ri]['tokens'][i] for ri,i in b];rng.shuffle(vs)
  for (ri,i),v in zip(b,vs):out[ri][i]=v
 return out
def score(lines):
 c=collections.Counter();excluded=collections.Counter()
 for ws in lines:
  for i,w in enumerate(ws):
   if w not in TARGETS:continue
   if i and i+1<len(ws) and ws[i-1]==ws[i+1]=='shedy':excluded[w]+=1;continue
   if i+1<len(ws) and ws[i+1] in TARGETS:c[(w,ws[i+1])]+=1
 a=c[('ol','qokedy')]-c[('qokedy','ol')];b=c[('ol','qol')]-c[('qol','ol')];z=c[('qokedy','qol')]-c[('qol','qokedy')]
 return np.array([a,b,z,a+b,-a+z,-b-z],dtype=np.int32),c,excluded
def calibration(scores):
 N=len(scores);tails=[];minimum=np.ones(N)
 for j in range(scores.shape[1]):
  v=scores[:,j];up=rankdata(-v,method='max')/N;lo=rankdata(v,method='max')/N;t=np.minimum(up,lo);minimum=np.minimum(minimum,t);tails.append((up,lo,t))
 out=[]
 for j,(up,lo,t) in enumerate(tails):
  v=scores[:,j];out.append(dict(label=LABELS[j],observed=int(v[0]),null_mean=float(v[1:].mean()),null_95=[float(x) for x in np.quantile(v[1:],[.025,.975])],p_upper=float(up[0]),p_lower=float(lo[0]),p_raw_two_sided=min(1,float(2*t[0])),p_triad_family=float(np.mean(minimum<=t[0]+1e-14))))
 return out
def test(rows,mode,B,seed):
 bs=buckets(rows,mode);rng=random.Random(seed);scores=np.zeros((B+1,6),dtype=np.int32);scores[0],counts,excluded=score([r['tokens'] for r in rows])
 for b in range(1,B+1):scores[b]=score(shuffled(rows,bs,rng))[0]
 movable={s for b in bs if len({rows[ri]['tokens'][i] for ri,i in b})>=2 for s in b}
 pairslots={(ri,k) for ri,r in enumerate(rows) for i in range(len(r['tokens'])-1) if r['tokens'][i] in TARGETS and r['tokens'][i+1] in TARGETS for k in (i,i+1)}
 return dict(mode=mode,permutations=B,tests=calibration(scores),observed_excluded_centers=dict(excluded),directed_cells={' '.join((a,b)):counts[(a,b)] for a in TARGETS for b in TARGETS},mobility=dict(movable_slots=len(movable),observed_target_pair_slots=len(pairslots),movable_target_pair_slots=len(pairslots&movable))),scores
