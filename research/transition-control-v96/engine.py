import collections,functools,math
from fractions import Fraction

class BudgetExceeded(RuntimeError):pass
def state(w):return 0 if w.startswith('sh') else 1 if w.startswith('qok') else 2
def edges(seq):
 out=[0]*9
 for a,b in zip(seq,seq[1:]):out[3*a+b]+=1
 return tuple(out)
def score(seq,neutral=False):return sum((1 if a==0 and c==1 else -1 if a==1 and c==0 else 0) for a,b,c in zip(seq,seq[1:],seq[2:]) if not neutral or b==2)

@functools.lru_cache(maxsize=None)
def distribution(start,end,counts,neutral=False,budget=250000):
 calls=0
 @functools.lru_cache(maxsize=None)
 def visit(previous,current,remaining):
  nonlocal calls
  calls+=1
  if calls>budget:raise BudgetExceeded('Exact DP exceeded frozen 250000-state budget; no approximation or source truncation.')
  if not any(remaining):return ((0,1),) if current==end else ()
  out=collections.Counter()
  for nxt in range(3):
   k=3*current+nxt
   if not remaining[k]:continue
   rest=list(remaining);rest[k]-=1
   delta=(1 if previous==0 and nxt==1 else -1 if previous==1 and nxt==0 else 0) if (not neutral or current==2) else 0
   for value,n in visit(current,nxt,tuple(rest)):out[value+delta]+=n
  return tuple(sorted(out.items()))
 result=dict(visit(-1,start,counts))
 return result,calls

def convolve(a,b):
 out=collections.Counter()
 for x,n in a.items():
  for y,m in b.items():out[x+y]+=n*m
 return dict(out)
def assess(dist,observed,budget):
 total=sum(dist.values());moment=sum(k*v for k,v in dist.items());mean=Fraction(moment,total);threshold=abs(observed*total-moment)
 tail=sum(v for k,v in dist.items() if abs(k*total-moment)>=threshold)
 up=sum(v for k,v in dist.items() if k>=observed);p=Fraction(tail,total)
 far=max(abs(k*total-moment) for k in dist);floor=Fraction(sum(v for k,v in dist.items() if abs(k*total-moment)==far),total)
 cumulative=0;low=high=None
 for k,v in sorted(dist.items()):
  cumulative+=v
  if low is None and cumulative*40>=total:low=k
  if high is None and cumulative*40>=39*total:high=k
 variance=sum(Fraction(v,total)*(k-mean)**2 for k,v in dist.items())
 return dict(observed_D=observed,conditional_mean=float(mean),conditional_SD=math.sqrt(float(variance)),null_95=[low,high],raw_two_sided_p=float(p),raw_upper_p=float(Fraction(up,total)),corrected_p=float(min(1,p*budget)),correction_factor=budget,support_min=min(dist),support_max=max(dist),support_values=len(dist),constant=len(dist)==1,minimum_attainable_corrected_p=float(min(1,floor*budget)),can_reject_at_05=len(dist)>1 and floor*budget<=Fraction(1,20),tail_numerator_hex=hex(tail),total_ways_hex=hex(total))

def binomial_null(n):return {2*k-n:math.comb(n,k) for k in range(n+1)}
def exact_power(n,q,budget):
 null=binomial_null(n);power=Fraction(0)
 for k in range(n+1):
  d=2*k-n
  if d<=0:continue
  if assess(null,d,budget)['corrected_p']<=.05:power+=math.comb(n,k)*q**k*(1-q)**(n-k)
 return float(power)
