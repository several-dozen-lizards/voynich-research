import collections,itertools,random
import numpy as np
from scipy.stats import rankdata

def buckets(rows,mode,anchor='qol'):
 groups=collections.defaultdict(list)
 for ri,r in enumerate(rows):
  ws=r['tokens'];n=len(ws)
  if mode=='exact_slot':
   mask=tuple(i for i,w in enumerate(ws) if w is None)
   for i,w in enumerate(ws):
    if w is not None and w!=anchor:groups[(r['page'],n,i,mask)].append((ri,i))
  else:
   start=1
   # Every anchor, unknown and endpoint is a barrier. Line composition fixed.
   for i in range(1,n):
    if i<n-1 and ws[i] is not None and ws[i]!=anchor:continue
    if i>start:groups[(ri,start,i)]=[(ri,k) for k in range(start,i)]
    start=i+1
 return [v for v in groups.values() if len(v)>=2]

def shuffle(rows,bs,rng):
 out=[r['tokens'][:] for r in rows]
 for slots in bs:
  vals=[rows[ri]['tokens'][i] for ri,i in slots];rng.shuffle(vals)
  for (ri,i),v in zip(slots,vals):out[ri][i]=v
 return out

def vocab_pairs(lines):
 vocab={w for ws in lines for w in ws if w is not None}
 return sorted((w,w[2:]) for w in vocab if w.startswith('qo') and len(w)>2 and w[2:] in vocab)

def directional(lines,pairs,anchor='qol'):
 left=collections.Counter();right=collections.Counter()
 for ws in lines:
  for i,w in enumerate(ws):
   if w!=anchor:continue
   if i and ws[i-1] is not None:left[ws[i-1]]+=1
   if i+1<len(ws) and ws[i+1] is not None:right[ws[i+1]]+=1
 values=np.array([left[p]-right[p]+right[b]-left[b] for p,b in pairs],dtype=np.int32)
 cells=[dict(prefixed_left=left[p],prefixed_right=right[p],base_left=left[b],base_right=right[b]) for p,b in pairs]
 return values,cells

def subsets(k):
 out=[(i,) for i in range(k)]+list(itertools.combinations(range(k),2))
 full=tuple(range(k))
 if full and full not in out:out.append(full)
 return out

def calibrate(pair_scores,sets):
 # All rows (observed + sampled permutations) are ranked symmetrically.
 # MinP family includes both signs; no assumption of equal pair variances.
 N=len(pair_scores);minimum=np.ones(N);observed=[]
 for s in sets:
  v=pair_scores[:,s].sum(axis=1)
  upper=rankdata(-v,method='max')/N;lower=rankdata(v,method='max')/N
  both=np.minimum(upper,lower);minimum=np.minimum(minimum,both)
  observed.append((int(v[0]),float(upper[0]),float(lower[0]),float(both[0]),float(v[1:].mean()),float(np.quantile(v[1:],.025)),float(np.quantile(v[1:],.975))))
 return [dict(observed=v[0],p_upper=v[1],p_lower=v[2],p_two_sided=min(1,2*v[3]),p_search_family=float(np.mean(minimum<=v[3]+1e-14)),null_mean=v[4],null_95=[v[5],v[6]]) for v in observed]

def run(rows,mode,B,seed,pairs=None):
 lines=[r['tokens'] for r in rows];pairs=pairs if pairs is not None else vocab_pairs(lines);sets=subsets(len(pairs));bs=buckets(rows,mode);rng=random.Random(seed)
 scores=np.zeros((B+1,len(pairs)),dtype=np.int32);scores[0],cells=directional(lines,pairs)
 for j in range(1,B+1):scores[j]=directional(shuffle(rows,bs,rng),pairs)[0]
 vals=calibrate(scores,sets)
 movable={s for b in bs if len({rows[ri]['tokens'][i] for ri,i in b})>=2 for s in b}
 neighbor_slots={(ri,i+d) for ri,r in enumerate(rows) for i,w in enumerate(r['tokens']) if w=='qol' for d in (-1,1) if 0<=i+d<len(r['tokens']) and r['tokens'][i+d] is not None}
 records=[dict(pair_indices=list(s),pairs=[list(pairs[i]) for i in s],**v) for s,v in zip(sets,vals)]
 return dict(mode=mode,permutations=B,pairs=[list(p) for p in pairs],family_size=len(sets),records=records,cells=cells,
  mobility=dict(shuffle_buckets=len(bs),movable_slots=len(movable),readable_neighbor_slots=len(neighbor_slots),movable_neighbor_slots=len(neighbor_slots&movable))),scores,bs
