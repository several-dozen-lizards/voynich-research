import collections,random
import numpy as np

def buckets(rows,mode):
 groups=collections.defaultdict(list)
 for ri,r in enumerate(rows):
  ws=r['tokens'];n=len(ws)
  if mode=='exact_slot':
   mask=tuple(i for i,w in enumerate(ws) if w is None)
   for i,w in enumerate(ws):
    if w is not None:groups[(r['page'],n,i,mask)].append((ri,i))
  else:
   start=1
   for i in range(1,n):
    if i<n-1 and ws[i] is not None:continue
    if i>start:groups[(ri,start,i)]=[(ri,k) for k in range(start,i)]
    start=i+1
 return [v for v in groups.values() if len(v)>=2]

def shuffled(rows,bs,rng):
 out=[r['tokens'][:] for r in rows]
 for slots in bs:
  vals=[rows[ri]['tokens'][i] for ri,i in slots];rng.shuffle(vals)
  for (ri,i),v in zip(slots,vals):out[ri][i]=v
 return out

def frames(lines,folios):
 totals=collections.Counter();middle_folios=collections.defaultdict(set)
 for ws,folio in zip(lines,folios):
  for i in range(1,len(ws)-1):
   l,m,r=ws[i-1:i+2]
   if l is None or m is None or r is None:continue
   totals[(l,r)]+=1;middle_folios[(l,r,m)].add(folio)
 recurring=collections.Counter()
 for (l,r,m),fs in middle_folios.items():
  if len(fs)>=2:recurring[(l,r)]+=1
 return totals,recurring

def test(rows,mode,B,seed,target=('shedy','shedy')):
 lines=[r['tokens'] for r in rows];folios=[r['folio'] for r in rows];obs=frames(lines,folios);bs=buckets(rows,mode);rng=random.Random(seed)
 scores=np.zeros((B,2),dtype=np.int32);maxima=np.zeros_like(scores)
 for b in range(B):
  stats=frames(shuffled(rows,bs,rng),folios)
  for k,counts in enumerate(stats):scores[b,k]=counts[target];maxima[b,k]=max(counts.values(),default=0)
 results=[]
 for k,label in enumerate(['total_frame_occurrences','crossfolio_recurring_middle_types']):
  v=obs[k][target]
  results.append(dict(statistic=label,observed=int(v),null_mean=float(scores[:,k].mean()),null_95=[float(x) for x in np.quantile(scores[:,k],[.025,.975])],
   p_raw=(1+int((scores[:,k]>=v).sum()))/(B+1),p_all_frames_max=(1+int((maxima[:,k]>=v).sum()))/(B+1)))
 movable={s for bs1 in bs if len({rows[ri]['tokens'][i] for ri,i in bs1})>=2 for s in bs1}
 targetslots={(ri,k) for ri,ws in enumerate(lines) for i in range(1,len(ws)-1) if ws[i-1]==target[0] and ws[i+1]==target[1] and ws[i] is not None for k in (i-1,i,i+1)}
 return dict(mode=mode,results=results,mobility=dict(shuffle_buckets=len(bs),movable_word_slots=len(movable),observed_frame_unique_slots=len(targetslots),movable_observed_frame_slots=len(targetslots&movable))),scores,maxima
