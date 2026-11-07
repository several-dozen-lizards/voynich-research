"""EOS counting repair only; v2 scoring/search otherwise unchanged."""
import sys,math
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent/'inputs'))
import legacy_core as legacy
UNK=legacy.UNK;BOS=legacy.BOS;EOS=legacy.EOS;HEB=legacy.HEB
alpha=legacy.alpha;VARIANTS=legacy.VARIANTS;traverse=legacy.traverse;variant_id=legacy.variant_id
class LM:
    def __init__(self,seqs,alphagrams=False):
        self.u=Counter();self.b=Counter();self.t=Counter();self.ctx=Counter();self.bctx=Counter()
        for i,seq in enumerate(list(seqs)+[[UNK]]):
            ws=[alpha(w) for w in seq] if alphagrams and i<len(seqs) else list(seq)
            ss=[BOS,BOS]+ws+[EOS]
            tr=list(zip(ss,ss[1:],ss[2:]))
            self.u.update(ss[2:]);self.b.update(zip(ss[1:],ss[2:]));self.t.update(tr)
            self.ctx.update((a,b) for a,b,c in tr);self.bctx.update(ss[1:-1])
        self.n=sum(self.u.values());self.vocab=frozenset(self.u);self.v=len(self.u);mass=[0.,0.,0.]
        for (a,b,c),n in self.t.items():
            q=[(self.u[c]-1)/max(1,self.n-1),(self.b[b,c]-1)/max(1,self.bctx[b]-1),(n-1)/max(1,self.ctx[a,b]-1)]
            mass[max(range(3),key=lambda i:q[i])]+=n
        total=sum(mass);self.weights=[x/total for x in mass];self.cache={}
    def canonical(self,w):return w if w in self.vocab or w==BOS else UNK
    def prob(self,a,b,c):
        a,b,c=map(self.canonical,(a,b,c))
        if c==BOS:raise ValueError('BOS is not a prediction event')
        p1=self.u[c]/self.n;p2=self.b[b,c]/self.bctx[b] if self.bctx[b] else p1;p3=self.t[a,b,c]/self.ctx[a,b] if self.ctx[a,b] else p2
        return sum(x*y for x,y in zip(self.weights,(p1,p2,p3)))
    def logp(self,a,b,c):
        k=tuple(map(self.canonical,(a,b,c)))
        if k not in self.cache:self.cache[k]=math.log(self.prob(*k))
        return self.cache[k]
    def score(self,ws):
        if not ws:raise ValueError('Empty line is not rankable')
        a=b=BOS;total=0.
        for c in ws:total+=self.logp(a,b,c);a,b=b,c
        return total/len(ws)
legacy.LM=LM
class Model(legacy.Model):
    def decode(self,words,key):
        mapped,candidates,outputs,_=super().decode(words,key)
        return mapped,candidates,outputs,self.lm.score(outputs)
fit=legacy.fit
def key_objective(seqs,model,key):
    uc=Counter(w for s in seqs for w in s);tr=Counter()
    for s in seqs:
        ss=[BOS,BOS]+s+[EOS];tr.update(zip(ss,ss[1:],ss[2:]))
    mapped={w:alpha(''.join(key.get(c,'\ufffd') for c in w)) for w in uc};mapped.update({BOS:BOS,EOS:EOS})
    a=sum(n*model.charscore(mapped[w]) for w,n in uc.items())/max(1,sum(uc.values()))
    b=sum(n*model.alm.logp(mapped[x],mapped[y],mapped[z]) for (x,y,z),n in tr.items())/max(1,sum(tr.values()))
    return (a+b)/2
