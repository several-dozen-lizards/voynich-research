"""Authored-data prototype only; imports no manuscript files or earlier runners."""
from collections import Counter
from functools import lru_cache
from fractions import Fraction

class BudgetExceeded(RuntimeError): pass

def contribution(a,b,c,neutral=False):
    if neutral and b[0]!=2:return 0
    return int(bool(a[1]&1) and bool(c[1]&2))-int(bool(a[1]&2) and bool(c[1]&1))

def edges(seq):
    out=[0]*9
    for a,b in zip(seq,seq[1:]):out[3*a[0]+b[0]]+=1
    return tuple(out)

def score(seq,neutral=False):
    return sum(contribution(a,b,c,neutral) for a,b,c in zip(seq,seq[1:],seq[2:]))

def marginal(start,end,interior,edge_counts,neutral=False,budget=250000):
    """Count distinct signature paths with pinned endpoints, inventory and edges.

    Signature=(S/Q/N class 0/1/2, A/B membership bit mask 0..3).
    Constant within-signature literal assignment multiplicities cancel.
    """
    kinds=tuple(sorted(interior));initial=tuple(interior[k] for k in kinds);calls=0
    @lru_cache(None)
    def visit(previous,current,left,remaining):
        nonlocal calls
        calls+=1
        if calls>budget:raise BudgetExceeded('Frozen 250000-state per-span/column/view cap exceeded')
        if not any(left):
            edge=3*current[0]+end[0]
            if sum(remaining)!=1 or remaining[edge]!=1:return ()
            d=0 if previous is None else contribution(previous,current,end,neutral)
            return ((d,1),)
        out=Counter()
        for i,n in enumerate(left):
            if not n:continue
            nxt=kinds[i];edge=3*current[0]+nxt[0]
            if not remaining[edge]:continue
            rest=list(remaining);rest[edge]-=1;counts=list(left);counts[i]-=1
            d=0 if previous is None else contribution(previous,current,nxt,neutral)
            for k,weight in visit(current,nxt,tuple(counts),tuple(rest)):out[k+d]+=weight
        return tuple(sorted(out.items()))
    if not sum(edge_counts):
        assert start==end and not sum(initial)
        return {0:1},1
    result=dict(visit(None,start,initial,tuple(edge_counts)))
    if not result:raise ValueError('No compatible paths; never drop a span silently')
    return result,calls

def tails(weights):
    total=sum(weights.values());moment=sum(k*n for k,n in weights.items())
    distances={k:abs(k*total-moment) for k in weights}
    return {k:Fraction(sum(n for x,n in weights.items() if distances[x]>=distances[k]),total) for k in weights}

def calibrated(target_p,calibration_minima,multiplier=28):
    return min(Fraction(1),multiplier*Fraction(1+sum(x<=target_p for x in calibration_minima),1+len(calibration_minima)))
