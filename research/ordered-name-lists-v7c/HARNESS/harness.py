"""v7 reading-harness infrastructure. No manuscript loader or vault runner.
Input records have explicit unit arrays; None is an uncertainty barrier.
Only demonstrably unbuilt, non-vault records may reach evaluate().
"""
import copy, hashlib, json, math, random, statistics, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/"vendor"))
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from collections import Counter, defaultdict

RESERVED={'f72v2','f72v1','f73r','f73v'}
EIDS=('E1','E2','E3','E4','E5')

class NotTestable(ValueError): pass

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate_key(k):
    required={'id','units','map','rules','target','built_on','provenance','value_inventory','condition_inventory','process_evidence'}
    if not required <= k.keys(): raise NotTestable('key not fixed: missing '+str(sorted(required-k.keys())))
    if not k['process_evidence']: raise NotTestable('unknown training exposure; everything defaults to built-on')
    if not k['provenance'] or not k['target'].get('resources'): raise NotTestable('missing provenance/reference resources')
    units=k['units']; values=k['value_inventory']
    if not units or len(set(units))!=len(units) or any(not isinstance(x,str) or not x for x in units): raise NotTestable('invalid unit inventory')
    if not values or len(set(values))!=len(values): raise NotTestable('invalid value inventory')
    if set(k['map'])!=set(units): raise NotTestable('base map must cover exactly declared units')
    if any(v not in values for v in k['map'].values()): raise NotTestable('value not declared')
    allowed={'position','left','right','section'}
    conditions=k['condition_inventory']
    for r in k['rules']:
        if set(r)!={'unit','when','value','source'} or r['unit'] not in units or r['value'] not in values or not r['source']: raise NotTestable('invalid rule')
        if not r['when'] or not set(r['when'])<=allowed: raise NotTestable('unsupported context condition')
        if r['when'] not in conditions: raise NotTestable('condition not in predeclared inventory')
    for u in units:
        if u not in k['provenance']: raise NotTestable('missing mapping source '+u)
    return k

def complexity(k):
    validate_key(k)
    # Each conjunction is one explicitly enumerated condition in the finite inventory.
    # Section overrides are ordinary explicit rule slots and incur the same cost.
    v=math.log2(len(k['value_inventory'])); c=math.log2(max(1,len(k['condition_inventory'])))
    return len(k['map'])*v+len(k['rules'])*(c+v)

def decode_word(word,k,section=''):
    if word is None or not word: return None
    out=[]
    for i,u in enumerate(word):
        if u is None or u not in k['map']: return None
        pos='single' if len(word)==1 else 'first' if i==0 else 'last' if i==len(word)-1 else 'interior'
        ctx={'position':pos,'left':word[i-1] if i else '^','right':word[i+1] if i+1<len(word) else '$','section':section}
        active=[r for r in k['rules'] if r['unit']==u and all(ctx.get(a)==b for a,b in r['when'].items())]
        vals={r['value'] for r in active}
        if len(vals)>1: return None
        out.append(next(iter(vals)) if vals else k['map'][u])
    return ''.join(out)

def decode_record(r,k): return [decode_word(w,k,r.get('section','')) for w in r['words']]

def random_key(k,rng):
    # Preserve base and context value-frequency multisets separately, positions untouched.
    z=copy.deepcopy(k); vals=list(z['map'].values()); rng.shuffle(vals)
    z['map']=dict(zip(z['map'],vals))
    vals=[r['value'] for r in z['rules']]; rng.shuffle(vals)
    for r,v in zip(z['rules'],vals): r['value']=v
    return z

def edit(a,b):
    prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        cur=[i]
        for j,y in enumerate(b,1): cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=cur
    return prev[-1]

def ned(a,b): return edit(a,b)/max(len(a),len(b),1)

def shuffle_lines(records,rng):
    z=copy.deepcopy(records)
    for r in z:
        # Unknown slots are barriers; shuffle within each contiguous readable segment.
        start=0
        for stop in range(len(r['words'])+1):
            if stop==len(r['words']) or r['words'][stop] is None:
                part=r['words'][start:stop]; rng.shuffle(part);r['words'][start:stop]=part;start=stop+1
    return z

def shuffle_glyphs(records,rng):
    z=copy.deepcopy(records)
    for r in z:
        for w in r['words']:
            if w and len(w)>2 and None not in w:
                middle=w[1:-1];rng.shuffle(middle);w[1:-1]=middle
    return z

class LM:
    def __init__(self,records,alphabet,order=2,smoothing=.5):
        self.alphabet=set(alphabet)|{' '};self.order=order;self.a=smoothing;self.c=defaultdict(Counter)
        for words in records:
            for text in segments(words):
                h='^'*order
                for ch in text:
                    self.c[h][ch]+=1;h=(h+ch)[-order:]
    def loss(self,records):
        total=0.;n=0;invalid=False
        for words in records:
            if any(w is None for w in words): invalid=True
            for text in segments(words):
                h='^'*self.order
                for ch in text:
                    if ch not in self.alphabet: return None,n,'out-of-target-alphabet'
                    row=self.c[h];p=(row[ch]+self.a)/(sum(row.values())+self.a*len(self.alphabet))
                    total-=math.log2(p);n+=1;h=(h+ch)[-self.order:]
        if invalid:return None,n,'ambiguous-or-unknown-token'
        return (total/n if n else None),n,None if n else 'no-characters'

def segments(words):
    buf=[]
    for w in words+[None]:
        if w is None:
            if buf: yield ' '.join(buf)
            buf=[]
        else: buf.append(w)

def rate(success,n): return {'kind':'rate','success':success,'n':n,'value':success/n if n else None}

def raw_scores(k,train,held,target,lexicons,pairs=(),number_checks=(),seed=701):
    dtrain=[decode_record(r,k) for r in train];dh=[decode_record(r,k) for r in held]
    decoded={(r['id'],i):w for r,ws in zip(held,dh) for i,w in enumerate(ws)}
    n=s=0
    for r,ws in zip(held,dh):
        if r.get('class') in lexicons:
            lex=lexicons[r['class']]
            for w in ws:
                n+=1;s+=w is not None and process.extractOne(w,lex,scorer=Levenshtein.normalized_distance,score_cutoff=.25) is not None
    scores={'E1':rate(s,n)}
    s=n=0
    for pair in pairs:
        a,b=pair['a'],pair['b'];x=decoded.get(tuple(a));y=decoded.get(tuple(b));n+=1
        # Lexical relations must be explicitly supplied, never inferred from labels.
        s+=x is not None and y is not None and (x==y or [x,y] in pair.get('relations',[]) or [y,x] in pair.get('relations',[]))
    scores['E2']=rate(s,n)
    alphabet=k['target']['alphabet'];lm=LM(dtrain,alphabet)
    shuffled=shuffle_lines(held,random.Random(seed));ds=[decode_record(r,k) for r in shuffled]
    real,n,err=lm.loss(dh);shuf,ns,es=lm.loss(ds)
    scores['E3']={'kind':'bits','value':shuf-real if real is not None and shuf is not None else None,'n':n,'real_bpc':real,'shuffled_bpc':shuf,'reason':err or es}
    tlm=LM(target,alphabet);real,n,err=tlm.loss(dh)
    scores['E4']={'kind':'bits','value':-real if real is not None else None,'n':n,'loss_bpc':real,'reason':err}
    s=n=0
    for check in number_checks:
        vals=[decoded.get(tuple(loc)) for loc in check['locations']];n+=1
        if check['kind']=='exact_sequence': s+=None not in vals and vals==check['expected']
        elif check['kind']=='sum':
            try:s+=all(v is not None for v in vals) and sum(float(v) for v in vals)==check['expected']
            except (TypeError,ValueError): pass
        else:raise NotTestable('number constraint not implemented')
    scores['E5']=rate(s,n)
    types=defaultdict(set);tokens=bad=0
    for r,ws in zip(held,dh):
        for src,w in zip(r['words'],ws):
            tokens+=1;bad+=w is None
            if src is not None:types[tuple(src)].add(w)
    scores['E6']={'tokens':tokens,'ambiguous_or_unknown':bad,'ambiguous_rate':bad/tokens if tokens else None,'types':len(types),'consistent_types':sum(len(v)==1 and None not in v for v in types.values())}
    return scores

def signed_binomial_bits(s,n,p0):
    if not n:return 0.
    q=s/n;ans=0.
    if s:ans+=s*math.log2(q/p0)
    if s<n:ans+=(n-s)*math.log2((1-q)/(1-p0))
    return ans if q>=p0 else -ans

def custody_check(k,train,held):
    built=set(k['built_on'])
    ids=[r['id'] for r in train+held]
    if len(ids)!=len(set(ids)):raise NotTestable('duplicate/overlapping train and held IDs')
    for r in train+held:
        if r.get('folio') in RESERVED or r.get('vault',False):raise NotTestable('vault forbidden in infrastructure evaluator')
    for r in train:
        if r['id'] not in built and r.get('folio') not in built:raise NotTestable('training row missing from built_on')
    for r in held:
        if r['id'] in built or r.get('folio') in built or r.get('custody')!='demonstrated_unbuilt':raise NotTestable('unknown or exposed held-out row')

def evaluate(k,train,held,target,lexicons,controls,pairs=(),number_checks=(),n_random=1000,seed=714):
    validate_key(k);custody_check(k,train,held)
    if n_random<1000:raise NotTestable('at least 1000 equal-complexity random keys required')
    if set(controls)!={'C1-word','C1-glyph','C2'} or not controls['C2']:raise NotTestable('required C1/C2 controls missing')
    for rows in controls.values():
        for r in rows:
            if r.get('folio') in RESERVED or r.get('vault'):raise NotTestable('vault in control')
    obs=raw_scores(k,train,held,target,lexicons,pairs,number_checks)
    rng=random.Random(seed);null=[];null_hash=[]
    for _ in range(n_random):
        rk=random_key(k,rng);null_hash.append(digest(rk));null.append(raw_scores(rk,train,held,target,lexicons,pairs,number_checks))
    K=complexity(k);gain=0.;above=[];comparisons={}
    for e in EIDS:
        val=obs[e]['value'];vals=[z[e]['value'] for z in null]
        if val is None or any(v is None for v in vals):
            comparisons[e]={'status':'NOT_ESTIMABLE'};continue
        median=statistics.median(vals);tail=(1+sum(v>=val for v in vals))/(n_random+1)
        if obs[e]['kind']=='rate':
            # Fixed Jeffreys smoothing prevents an infinite gain at a zero null median.
            nn=obs[e]['n'];base=(median*nn+.5)/(nn+1);bits=signed_binomial_bits(obs[e]['success'],nn,base)
        else:bits=(val-median)*obs[e]['n']
        gain+=bits
        # Conservative ties: require a strictly better rank, with finite-MC p <= .01.
        if tail<=.01:above.append(e)
        comparisons[e]={'value':val,'C3_median':median,'gain_bits':bits,'mc_p':tail,'at_or_above_99_percentile':tail<=.01}
    control_scores={name:raw_scores(k,train,rows,target,lexicons,seed=701) for name,rows in controls.items()}
    control_gate=all(obs[e]['value'] is not None and c[e]['value'] is not None and obs[e]['value']>c[e]['value'] for c in control_scores.values() for e in ('E3','E4'))
    coherence=gain-K
    passed=coherence>0 and len(above)>=2 and control_gate
    return {'key_id':k['id'],'K_bits':K,'coherence_bits':coherence,'evaluations':obs,'C3':comparisons,'C3_raw':null,'C3_key_hashes':null_hash,'C3_count':n_random,'seed':seed,'controls':control_scores,'control_gate':control_gate,'above_99':above,'single_reading_verdict':'PASS' if passed else 'PARTIAL' if above else 'FAIL','input_sha256':digest({'key':k,'train':train,'held':held,'target':target,'lexicons':lexicons,'controls':controls,'pairs':pairs,'number_checks':number_checks})}

def paired_verdict(h,f):
    vals=[h['single_reading_verdict'],f['single_reading_verdict']]
    return 'PASS' if vals==['PASS','PASS'] else 'PARTIAL' if any(v in ('PASS','PARTIAL') for v in vals) else 'FAIL'
