"""Full-family qualification engine. No manuscript-data loader or scoring CLI."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations,product
import hashlib,importlib.util,math
import numpy as np
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v103_authored_dp',ROOT.parent/'retrospective-order-design-v103/engine.py')
dp=importlib.util.module_from_spec(spec);spec.loader.exec_module(dp)

def state(w):return 0 if w.startswith('sh') else 1 if w.startswith('qok') else 2
def belongs(w,label):
    if label.startswith('prefix:'):return w.startswith(label[7:])
    if label=='union:l/s':return w.startswith(('l','s'))
    if label=='exact:ol/or':return w in ('ol','or')
    raise ValueError(label)
def edgecounts(seq):
    a=[0]*9
    for x,y in zip(seq,seq[1:]):a[3*x+y]+=1
    return tuple(a)
@lru_cache(None)
def paths(start,end,counts):
    out=[]
    def visit(cur,left,seq):
        if not any(left):
            if cur==end:out.append(seq)
            if len(out)>20000:raise RuntimeError('20000 class-path cap')
            return
        for nxt in range(3):
            k=3*cur+nxt
            if left[k]:
                rest=list(left);rest[k]-=1;visit(nxt,tuple(rest),seq+(nxt,))
    visit(start,counts,(start,));return tuple(out)
def spans(rows):
    out=[]
    for row in rows:
        start=0
        for j in range(len(row)+1):
            if j<len(row) and row[j] is not None:continue
            if j>start:out.append(tuple(row[start:j]))
            start=j+1
    return tuple(out)
def convolve(a,b):
    out=Counter()
    for x,n in a.items():
        for y,m in b.items():out[x+y]+=n*m
    return dict(out)
def seed(text):return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big')
def oracle_span(s):
    if len(s)<=2:return (s,)
    ec=edgecounts(tuple(map(state,s)))
    return tuple((s[0],)+p+(s[-1],) for p in sorted(set(permutations(s[1:-1]))) if edgecounts(tuple(map(state,(s[0],)+p+(s[-1],))))==ec)
def oracle_layout(rows,cap=20000):
    pools=[oracle_span(s) for s in spans(rows)];n=math.prod(map(len,pools))
    if n>cap:raise RuntimeError('Authored literal-orbit cap')
    return tuple(product(*pools))
def draw(rows,n,rng):
    ss=spans(rows);out=[]
    for _ in range(n):
        arr=[]
        for s in ss:
            if len(s)<=2:arr.append(s);continue
            seq=tuple(map(state,s));pp=paths(seq[0],seq[-1],edgecounts(seq));order=pp[int(rng.integers(len(pp)))];pools=[]
            for c in range(3):
                pool=[w for w in s[1:-1] if state(w)==c]
                for j in range(len(pool)-1,0,-1):
                    k=int(rng.integers(j+1));pool[j],pool[k]=pool[k],pool[j]
                pools.append(iter(pool))
            arr.append((s[0],)+tuple(next(pools[c]) for c in order[1:-1])+(s[-1],))
        out.append(tuple(arr))
    return tuple(out)
def invariant(layout,rows):
    original=spans(rows);assert len(layout)==len(original)
    for s,t in zip(original,layout):
        assert len(s)==len(t) and s[0]==t[0] and s[-1]==t[-1] and Counter(s)==Counter(t)
        assert edgecounts(tuple(map(state,s)))==edgecounts(tuple(map(state,t)))
def direct(layout,A,B,neutral):
    total=0
    for s in layout:
        for a,b,c in zip(s,s[1:],s[2:]):
            if neutral and state(b)!=2:continue
            total+=int(belongs(a,A) and belongs(c,B))-int(belongs(a,B) and belongs(c,A))
    return total
def build(rows,labels,neutral):
    """Retain every column; share only identical complete signature inputs."""
    ss=spans(rows);words=sorted({w for s in ss for w in s});wid={w:i for i,w in enumerate(words)}
    pairs=[(a,b) for i,a in enumerate(labels) for b in labels[i+1:]]
    grouped={};groups=[];column_group=[];span_cache={}
    for A,B in pairs:
        masks={w:int(belongs(w,A))+2*int(belongs(w,B)) for w in words}
        descriptors=[]
        for s in ss:
            sig=tuple((state(w),masks[w]) for w in s)
            descriptors.append((sig[0],sig[-1],tuple(sorted(Counter(sig[1:-1]).items())),edgecounts(tuple(map(state,s)))))
        # Include the complete literal-vocabulary membership map for score identity.
        key=(tuple(masks[w] for w in words),tuple(descriptors),neutral)
        if key not in grouped:
            h={0:1};calls=0
            for desc in descriptors:
                cache_key=(desc,neutral)
                if cache_key not in span_cache:
                    start,end,ct,ec=desc;span_cache[cache_key]=dp.marginal(start,end,dict(ct),ec,neutral)
                hist,ncall=span_cache[cache_key];calls+=ncall;h=convolve(h,hist)
            lut=np.array([int(bool(masks[a]&1) and bool(masks[b]&2))-int(bool(masks[a]&2) and bool(masks[b]&1)) for a in words for b in words],dtype=np.int32)
            grouped[key]=len(groups);groups.append(dict(A=A,B=B,hist=h,tails=dp.tails(h),lut=lut,states=calls))
        column_group.append(grouped[key])
    return dict(labels=labels,pairs=pairs,groups=groups,column_group=np.array(column_group,dtype=np.int32),words=words,wid=wid,neutral=neutral)
def scores(layouts,p):
    n=len(p['words']);counts=np.zeros((len(layouts),n*n),dtype=np.int32)
    for j,layout in enumerate(layouts):
        for s in layout:
            for a,b,c in zip(s,s[1:],s[2:]):
                if p['neutral'] and state(b)!=2:continue
                counts[j,p['wid'][a]*n+p['wid'][c]]+=1
    lut=np.stack([g['lut'] for g in p['groups']],axis=1)
    return counts@lut
def minima(gs,p):
    result=[Fraction(1)]*len(gs)
    for j,g in enumerate(p['groups']):
        for i,d in enumerate(gs[:,j]):result[i]=min(result[i],g['tails'][int(d)])
    return result
def rational(x):return [x.numerator,x.denominator]
def target(p):
    A,B=sorted(('prefix:sh','prefix:qok'));col=p['pairs'].index((A,B));return col,int(p['column_group'][col]),(1 if A=='prefix:sh' else -1)
