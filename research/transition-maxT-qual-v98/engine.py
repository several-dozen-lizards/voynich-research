from pathlib import Path
import collections,functools,importlib.util,itertools,math
import numpy as np
P=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('gap_encoder',P/'one-gap-order-v78/engine.py');gap=importlib.util.module_from_spec(spec);spec.loader.exec_module(gap)

@functools.lru_cache(maxsize=None)
def paths(start,end,counts):
 out=[]
 def visit(current,remaining,seq):
  if len(out)>20000:raise RuntimeError('Frozen20000class-path resource limit exceeded; cannot drop source span.')
  if not any(remaining):
   if current==end:out.append(seq)
   return
  for nxt in range(3):
   j=current*3+nxt
   if remaining[j]:
    q=list(remaining);q[j]-=1;visit(nxt,tuple(q),seq+(nxt,))
 visit(start,counts,(start,))
 return np.array(out,dtype=np.int8)
def state(w):return 0 if w.startswith('sh') else 1 if w.startswith('qok') else 2
def edgecounts(seq):
 out=[0]*9
 for a,b in zip(seq,seq[1:]):out[a*3+b]+=1
 return tuple(out)
def build(rows):
 p=gap.prepare(rows);specs=[];offset=0
 for r in rows:
  begin=0;ws=r['tokens']
  for i in range(len(ws)+1):
   if i<len(ws) and ws[i] is not None:continue
   part=ws[begin:i]
   if part:
    seq=tuple(map(state,part));orders=paths(seq[0],seq[-1],edgecounts(seq));assert len(orders)>0
    rank=np.full(orders.shape,-1,dtype=np.int16)
    for c in range(3):
     mask=orders[:,1:-1]==c;rank[:,1:-1]=np.where(mask,np.cumsum(mask,axis=1)-1,rank[:,1:-1])
    pools=[np.array([p['wordid'][w] for w in part[1:-1] if state(w)==c],dtype=np.int32) for c in range(3)]
    specs.append(dict(offset=offset+begin,length=len(part),orders=orders,ranks=rank,pools=pools))
   begin=i+1
  offset+=len(ws)
 return p,specs
def draw(p,specs,n,rng):
 a=np.tile(p['original'],(n,1));row=np.arange(n)
 for s in specs:
  length=s['length']
  if length<=2:continue
  oi=rng.integers(0,len(s['orders']),size=n) if len(s['orders'])>1 else np.zeros(n,dtype=int);orders=s['orders'][oi];ranks=s['ranks'][oi]
  for c,pool in enumerate(s['pools']):
   m=len(pool)
   if not m:continue
   perm=np.tile(pool,(n,1))
   if len(set(pool.tolist()))>1:
    for j in range(m-1,0,-1):
     swap=rng.integers(0,j+1,size=n);tmp=perm[:,j].copy();perm[:,j]=perm[row,swap];perm[row,swap]=tmp
   for j in range(1,length-1):
    yes=orders[:,j]==c
    if np.any(yes):a[yes,s['offset']+j]=perm[yes,ranks[yes,j]]
 return a
def invariants(a,p,specs):
 for s in specs:
  start=s['offset'];stop=start+s['length'];orig=p['original'][start:stop]
  assert np.all(a[:,start]==orig[0]) and np.all(a[:,stop-1]==orig[-1])
  expected=collections.Counter(orig.tolist());ec=edgecounts(tuple(state(p['words'][i]) for i in orig))
  for ws in a[:,start:stop]:
   assert collections.Counter(ws.tolist())==expected;assert edgecounts(tuple(state(p['words'][i]) for i in ws))==ec
 assert np.all((a<0)==(p['original'][None,:]<0))
def score_batch(a,p):
 out={view:np.empty((len(a),len(p['ia'])),dtype=np.int16) for view in ['any_middle','non_target_middle']}
 for i,arr in enumerate(a):
  for view in out:
   _,v=gap.count(arr,p,view=='non_target_middle');assert np.max(np.abs(v),initial=0)<=32767;out[view][i]=v
 return out
