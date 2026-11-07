"""C16-KH re-derived algorithms. See DECISIONS.md for replication deviations."""
import math, re, unicodedata, itertools
from collections import Counter,defaultdict
HEB='אבגדהוזחטיכלמנסעפצקרשת'
FINAL=str.maketrans('ךםןףץ','כמנפצ')
UNK='<UNK>'; BOS='<s>'; EOS='</s>'
def hebrew(text):
    text=re.sub(r'<sup\b[^>]*>.*?</sup>',' ',text,flags=re.S|re.I)
    text=re.sub(r'<i\b[^>]*class=[^>]*footnote[^>]*>.*?</i>',' ',text,flags=re.S|re.I)
    text=re.sub(r'<[^>]*>',' ',text)
    text=''.join(c for c in unicodedata.normalize('NFKD',text) if not unicodedata.combining(c)).translate(FINAL)
    return re.findall('[א-ת]+',text)
def alpha(w):return ''.join(sorted(w))
def pattern(ws):
    counts=[Counter(w) for w in ws]; chars=set(''.join(ws))
    return tuple(sorted(tuple(c[x] for c in counts) for x in chars))
def signatures(ws):
    counts=[Counter(w) for w in ws]; out=defaultdict(list)
    for x in set(''.join(ws)):out[tuple(c[x] for c in counts)].append(x)
    return out
class LM:
    def __init__(self,seqs, alphagrams=False):
        self.u=Counter();self.b=Counter();self.t=Counter();self.ctx=Counter();self.bctx=Counter();self.alphagrams=alphagrams
        for seq in seqs:
            ws=[alpha(w) for w in seq] if alphagrams else list(seq)
            ws=[BOS,BOS]+ws+[EOS]
            self.u.update(ws[2:]);self.b.update(zip(ws[1:],ws[2:]));self.t.update(zip(ws,ws[1:],ws[2:]));self.ctx.update(zip(ws,ws[1:]));self.bctx.update(ws[1:-1])
        self.n=sum(self.u.values());self.v=len(self.u);mass=[0.,0.,0.]
        for (a,b,c),n in self.t.items():
            q=[(self.u[c]-1)/max(1,self.n-1),(self.b[b,c]-1)/max(1,self.bctx[b]-1),(n-1)/max(1,self.ctx[a,b]-1)]
            mass[max(range(3),key=lambda i:q[i])]+=n
        total=sum(mass) or 1;self.weights=[x/total for x in mass]
        self.unkp=max(1/self.n,sum(n==1 for n in self.u.values())/self.n)
        self.cache={}
    def logp(self,a,b,c):
        k=(a,b,c)
        if k not in self.cache:
            p1=(1-self.unkp)*self.u[c]/self.n if self.u[c] else self.unkp
            p2=self.b[b,c]/max(1,self.bctx[b])
            p3=self.t[a,b,c]/max(1,self.ctx[a,b])
            self.cache[k]=math.log(max(1e-12,sum(x*y for x,y in zip(self.weights,[p1,p2,p3]))))
        return self.cache[k]
    def score(self,ws):
        a=b=BOS;s=0.
        for c in list(ws)+[EOS]:s+=self.logp(a,b,c);a,b=b,c
        return s/(len(ws)+1)
class Model:
    def __init__(self,seqs):
        self.seqs=seqs;self.lm=LM(seqs);self.alm=LM(seqs,True)
        self.lex=defaultdict(list);self.freq=Counter(w for s in seqs for w in s)
        for w in sorted(self.freq):self.lex[alpha(w)].append(w)
        self.chars=Counter(''.join(w for s in seqs for w in s));self.ct=Counter();self.cb=Counter();self.patterns=defaultdict(Counter)
        for seq in seqs:
            for w in seq:
                aw='^^'+alpha(w)+'$';self.ct.update(zip(aw,aw[1:],aw[2:]));self.cb.update(zip(aw,aw[1:]))
            for n in (1,2,3):
                for i in range(len(seq)-n+1):
                    ws=tuple(seq[i:i+n]);self.patterns[pattern(ws)][ws]+=1
        self.targets={p:[w for w,n in sorted(v.items(),key=lambda x:(-x[1],x[0]))[:3]] for p,v in self.patterns.items()}
        del self.patterns
        self.charcache={}
    def charscore(self,w):
        if w not in self.charcache:
            t='^^'+w+'$';v=24
            self.charcache[w]=sum(math.log((self.ct[a,b,c]+.1)/(self.cb[a,b]+.1*v)) for a,b,c in zip(t,t[1:],t[2:]))/(len(w)+1)
        return self.charcache[w]
    def decode(self,words,key):
        mapped=[''.join(key.get(c,'\ufffd') for c in w) for w in words]
        candidates=[self.lex.get(alpha(w),[]) if '\ufffd' not in w else [] for w in mapped]
        states={(BOS,BOS):(0.,None)};history=[]
        for cs in candidates:
            nxt={}
            for (a,b),(s,_) in states.items():
                for c in cs or [UNK]:
                    q=s+self.lm.logp(a,b,c);k=(b,c)
                    if k not in nxt or q>nxt[k][0]:nxt[k]=(q,(a,b))
            history.append(nxt);states=nxt
        if not states:return [],[],[],float('-inf')
        end=max(sorted(states),key=lambda ab:states[ab][0]+self.lm.logp(*ab,EOS))
        score=(states[end][0]+self.lm.logp(*end,EOS))/(len(words)+1)
        out=[]
        for h in reversed(history):out.append(end[1]);end=h[end][1]
        return mapped,candidates,list(reversed(out)),score
def fit(seqs,model):
    cf=Counter(''.join(w for s in seqs for w in s if '\ufffd' not in w))
    syms=sorted(cf,key=lambda x:(-cf[x],x));tgt=sorted(HEB,key=lambda x:(-model.chars[x],x))
    tgt += [chr(0xe000+i) for i in range(max(0,len(syms)-22))]
    initial=tuple(tgt[:len(syms)]);index={c:i for i,c in enumerate(syms)}
    ng=Counter()
    for s in seqs:
        for n in (1,2,3):ng.update(tuple(s[i:i+n]) for i in range(len(s)-n+1) if all('\ufffd' not in w for w in s[i:i+n]))
    # Top 24 per n, keeping unigram and multiword proposals represented.
    selected=[]
    for n in (1,2,3):selected += sorted((w for w in ng if len(w)==n),key=lambda w:(-ng[w],w))[:24]
    constraints=[]
    for ws in selected:
        sg=signatures(ws)
        for ts in model.targets.get(pattern(ws),[]):
            tg=signatures(ts);pairs=[]
            for sig,chars in sorted(sg.items()):
                left=sorted(chars,key=lambda c:(-cf[c],c));right=sorted(tg[sig],key=lambda c:(-model.chars[c],c));pairs += list(zip(left,right))
            constraints.append(pairs)
    # Objective uses counted ngrams; all keys evaluated on the same page.
    uc=Counter(w for s in seqs for w in s);b=Counter();t=Counter()
    for s in seqs:
        ss=[BOS,BOS]+s+[EOS];b.update(zip(ss[1:],ss[2:]));t.update(zip(ss,ss[1:],ss[2:]))
    evaluations=0
    def objective(k):
        nonlocal evaluations;evaluations+=1
        d=dict(zip(syms,k));mapped={w:alpha(''.join(d.get(c,'\ufffd') for c in w)) for w in uc};mapped.update({BOS:BOS,EOS:EOS})
        char=sum(n*model.charscore(mapped[w]) for w,n in uc.items())/max(1,sum(uc.values()))
        word=sum(n*model.alm.logp(mapped[a],mapped[b],mapped[c]) for (a,b,c),n in t.items())/max(1,sum(t.values()))
        return (char+word)/2
    start=objective(initial);beam=[(start,initial)];seen={initial};rounds=0
    for rounds in range(1,13):
        proposals={k:s for s,k in beam}
        for s,k in beam:
            for pairs in constraints:
                new=list(k)
                for c,h in pairs:
                    i=index[c]
                    if h in new:j=new.index(h);new[i],new[j]=new[j],new[i]
                    else:new[i]=h # Target absent from shorter source alphabet: replaces unused plaintext target.
                nk=tuple(new)
                if nk in seen:continue
                assert len(set(nk))==len(nk)
                seen.add(nk);proposals[nk]=objective(nk)
        nb=sorted(((s,k) for k,s in proposals.items()),key=lambda x:(-x[0],x[1]))[:3]
        if nb==beam:break
        beam=nb
    return dict(zip(syms,beam[0][1])),dict(initial_objective=start,objective=beam[0][0],rounds=rounds,evaluations=evaluations,alphabet=len(syms),dummy_targets=sum(ord(c)>=0xe000 for c in beam[0][1]),constraints=len(constraints))
VARIANTS=list(itertools.product(('LTR','RTL'),('LTR','RTL'),('TB','BT'),('row','column','boustro')))
def variant_id(v):return '-'.join(v)
def traverse(rows,v):
    char,word,line,mode=v
    rs=rows if line=='TB' else list(reversed(rows));units=[]
    for j,r in enumerate(rs):
        toks=[dict(word=w,slot=i,row=r) for i,w in enumerate(r['text_eva'].split())]
        if word=='RTL':toks.reverse()
        if mode=='boustro' and j%2:toks.reverse()
        if char=='RTL':toks=[dict(t,word=t['word'][::-1]) for t in toks]
        units.append(toks)
    if mode=='column':units=[[u[k] for u in units if k<len(u)] for k in range(max(map(len,units),default=0))]
    return [u for u in units if u]
