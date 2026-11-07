import collections,math
from fractions import Fraction

def convolve(a,b):
 out=collections.Counter()
 for x,n in a.items():
  for y,m in b.items():out[x+y]+=n*m
 return dict(out)
def tilt_integer(dist,ratio):
 a,b=ratio.numerator,ratio.denominator;lo,hi=min(dist),max(dist)
 return {d:n*pow(a,d-lo)*pow(b,hi-d) for d,n in dist.items()}
def moments(dist):
 total=sum(dist.values());mean=Fraction(sum(d*n for d,n in dist.items()),total)
 var=Fraction(sum(d*d*n for d,n in dist.items()),total)-mean*mean
 return total,mean,var
def rejection_regions(null,budget):
 total,mean,var=moments(null);moment=mean.numerator*(total//mean.denominator)
 distances=collections.defaultdict(list)
 for d,n in null.items():distances[abs(d*total-moment)].append((d,n))
 cumulative=0;forward=set();reverse=set();tails={}
 for distance,items in sorted(distances.items(),reverse=True):
  cumulative+=sum(n for _,n in items)
  for d,n in items:
   tails[d]=Fraction(cumulative,total)
   if cumulative*budget*20<=total:
    if d*total>moment:forward.add(d)
    elif d*total<moment:reverse.add(d)
 return dict(total=total,mean=mean,variance=var,forward=forward,reverse=reverse,tails=tails)
def evaluate(alternative,regions,direction):
 total,mean,var=moments(alternative);plus=sum(n for d,n in alternative.items() if d in regions['forward']);minus=sum(n for d,n in alternative.items() if d in regions['reverse'])
 right=plus if direction=='forward' else minus if direction=='reverse' else plus+minus
 wrong=minus if direction=='forward' else plus if direction=='reverse' else 0
 nullsd=math.sqrt(float(regions['variance']))
 return dict(correct_direction_power=float(Fraction(right,total)),any_rejection=float(Fraction(plus+minus,total)),wrong_direction_rejection=float(Fraction(wrong,total)),alternative_mean=float(mean),alternative_SD=math.sqrt(float(var)),mean_shift_D=float(mean-regions['mean']),mean_shift_in_null_SD=float(mean-regions['mean'])/nullsd if nullsd else None,power_numerator_hex=hex(right),alternative_total_hex=hex(total))
