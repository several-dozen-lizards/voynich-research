import collections,functools,math
@functools.lru_cache(maxsize=None)
def loose_distribution(start,end,interior,neutral=False,single=False,budget=250000):
 if single:return {0:1},1
 calls=0
 @functools.lru_cache(maxsize=None)
 def walk(previous,current,remaining):
  nonlocal calls
  calls+=1
  if calls>budget:raise RuntimeError('Frozen exact-DP budget exceeded; no dropped spans or approximations.')
  if not any(remaining):
   delta=(1 if previous==0 and end==1 else -1 if previous==1 and end==0 else 0) if not neutral or current==2 else 0
   return ((delta,1),)
  out=collections.Counter()
  for nxt in range(3):
   if not remaining[nxt]:continue
   r=list(remaining);r[nxt]-=1;delta=(1 if previous==0 and nxt==1 else -1 if previous==1 and nxt==0 else 0) if not neutral or current==2 else 0
   for value,n in walk(current,nxt,tuple(r)):out[value+delta]+=n
  return tuple(sorted(out.items()))
 return dict(walk(-1,start,tuple(interior))),calls
