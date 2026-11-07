"""Phase11 control-only instrument. No function reads Voynich target files."""
import ast
import csv
import hashlib
import json
import math
import random
import re
import sys
import types
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'extensions/prior_work_v1'
for p in [ROOT / '.analysis-runtime', ROOT / '.runtime']:
    sys.path.insert(0, str(p))
import numpy as np
import scipy
from scipy.cluster.hierarchy import linkage, cut_tree

SEEDS = list(range(11001, 11021))
METHODS = ['T-Z', 'T-N', 'T-MDL']
KEYS = ['inventory', 'h1', 'h2', 'ratio', 'slope', 'word_length', 'positional_entropy']
RATES = dict(substitution=.021595507891541885, insertion=.010565686968838526,
             deletion=.010565686968838526)
SOURCES = {c: ROOT / f'data/controls/{c}/clean.csv' for c in ['C1','C2','C3','C13','C7','C9','C11']}
SOURCES.update(C8=OLD/'data/C8_published/native.csv', C17=OLD/'data/C17_human/native.csv',
               Occitan=OLD/'raw/chirila/Corpora/Wikipedia_texts/full/Occitan')
TABLE = OLD/'raw/greshko/references/naibbe_tables.csv'
AUTHOR = OLD/'raw/greshko/naibbe.py'
JAVA = next((OLD/'raw/mzattera').rglob('SlotAlphabet.java'))

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p, data):
    p = Path(p)
    tmp = p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    tmp.replace(p)
def rng(seed, label): return random.Random(hashlib.sha256(f'{seed}:{label}'.encode()).hexdigest())
def entropy(counts):
    n = sum(counts)
    return -sum(c/n*math.log2(c/n) for c in counts if c) if n else 0.
def nll(counts):
    n = sum(counts)
    return n*math.log2(n)-sum(c*math.log2(c) for c in counts if c) if n else 0.
def counts_words(words): return Counter(w for line in words for w in line)

def published():
    block = JAVA.read_text(encoding='utf-8').split('public static String fromEva(String txt)')[1].split('public static Set<String> fromEva')[0]
    pairs = [(json.loads(a),json.loads(b)) for a,b in re.findall(r'txt = txt\.replace\(("[^"\n]*"), ("[^"\n]*")\);',block)]
    pairs = [(a,b) for a,b in pairs if a in ['ckh','cfh','cth','cph','ch','sh','eee','ee','iii','ii']]
    assert len(pairs)==10
    with TABLE.open(encoding='utf-8-sig', newline='') as f:
        chunks = sorted({r['glyphs'] for r in csv.DictReader(f) if r['glyphs']})
    return pairs, chunks

class Tokenizer:
    def __init__(self, method, train):
        self.method = method
        self.alphabet = sorted({c for w in train for c in w})
        self.meta = {}
        self.pairs, self.chunks = published()
        self.merges = []
        if method=='T-N':
            inventory = sorted(set(self.chunks)|set(self.alphabet))
            byfirst = defaultdict(list)
            for c in inventory: byfirst[c[0]].append(c)
            self.byfirst = {k:sorted(v,key=lambda t:(-len(t),t)) for k,v in byfirst.items()}
            counts = Counter()
            for w,n in Counter(train).items():
                i = 0
                while i<len(w):
                    t = next((s for s in self.byfirst[w[i]] if w.startswith(s,i)), w[i])
                    counts[t] += n
                    i += len(t)
            den = sum(counts.values())+.5*len(inventory)
            self.cost = {s:-math.log2((counts[s]+.5)/den) for s in inventory}
            self.escape = -math.log2(.5/den)
            self.meta = dict(inventory=inventory, costs=self.cost, escape=self.escape)
        elif method=='T-MDL':
            current = {tuple(w):n for w,n in Counter(train).items()}
            path = []
            for step in range(65):
                c = Counter()
                for w,n in current.items():
                    for t in w: c[t]+=n
                N,V = sum(c.values()),len(c)
                value = nll(c.values())+.5*(V-1)*math.log2(max(N,2))
                value += sum((len(a+b)+1)*math.log2(len(self.alphabet)+1) for a,b in self.merges)
                path.append(dict(step=step, mdl=value, tokens=N, inventory=V))
                if step==64: break
                pairs = Counter()
                for w,n in current.items():
                    for pair in zip(w,w[1:]): pairs[pair]+=n
                if not pairs or max(pairs.values())<2: break
                pair = min(pairs, key=lambda p:(-pairs[p],p))
                self.merges.append(pair)
                new = Counter()
                for w,n in current.items(): new[tuple(self.apply_pair(w,pair))]+=n
                current = new
            best = min(path,key=lambda r:(r['mdl'],r['step']))['step']
            self.meta = dict(path=path, selected_prefix=best, full_path=self.merges,
                             cap_reached=len(path)==65)
            self.merges = self.merges[:best]
    @staticmethod
    def apply_pair(w,pair):
        out=[]; i=0
        while i<len(w):
            if i+1<len(w) and (w[i],w[i+1])==pair:
                out.append(w[i]+w[i+1]); i+=2
            else: out.append(w[i]); i+=1
        return out
    @lru_cache(maxsize=200000)
    def word(self, w):
        if self.method=='T-Z':
            # Segment original spans by ordered replacements, preserving unknowns.
            spans=list(w)
            for a,_ in self.pairs:
                spans=self.apply_sequence(spans,tuple(a))
            return tuple(spans)
        if self.method=='T-N':
            dp=[None]*(len(w)+1); dp[-1]=(0.,())
            for i in range(len(w)-1,-1,-1):
                options=[s for s in self.byfirst.get(w[i],[]) if w.startswith(s,i)]
                if w[i] not in options: options.append(w[i])
                dp[i]=min((self.cost.get(s,self.escape)+dp[i+len(s)][0],
                           (s,)+dp[i+len(s)][1]) for s in options)
            return dp[0][1]
        out=list(w)
        for pair in self.merges: out=self.apply_pair(out,pair)
        return tuple(out)
    @staticmethod
    def apply_sequence(spans, chars):
        # Earlier multiglyph units are atomic, as in published replacement order.
        out=[]; i=0; n=len(chars)
        while i<len(spans):
            if tuple(spans[i:i+n])==chars:
                out.append(''.join(chars)); i+=n
            else: out.append(spans[i]); i+=1
        return out

def merge_fit(words):
    freq=Counter(t for w in words for t in w)
    vocab=sorted(freq); V=len(vocab)
    contexts=Counter()
    for w in words:
        for i,t in enumerate(w):
            contexts[t,('L',w[i-1] if i else '<EDGE>')]+=1
            contexts[t,('R',w[i+1] if i+1<len(w) else '<EDGE>')]+=1
    features=sorted({f for t,f in contexts}); vi={v:i for i,v in enumerate(vocab)}
    fi={v:i for i,v in enumerate(features)}
    matrix=np.zeros((V,len(features)))
    for (t,f),n in contexts.items(): matrix[vi[t],fi[f]]=n
    if V==1: return {vocab[0]:'M0'},dict(selected_K=1,path=[])
    probs=matrix/matrix.sum(axis=1,keepdims=True)
    tree=linkage(np.sqrt(probs),method='average',metric='euclidean')
    cuts=cut_tree(tree,n_clusters=list(range(1,V+1)))
    M=matrix.sum(); D=len(features); path=[]; mappings=[]
    for col,k in enumerate(range(1,V+1)):
        labels=cuts[:,col]
        mdl=0.
        for label in range(k):
            ix=np.where(labels==label)[0]
            mdl += nll(matrix[ix].sum(axis=0)) + nll([freq[vocab[i]] for i in ix])
        mdl += .5*k*(D-1)*math.log2(max(M,2))+V*math.log2(k+1)
        path.append(dict(K=k,mdl=mdl)); mappings.append(labels)
    best=min(range(V),key=lambda i:(path[i]['mdl'],-path[i]['K']))
    mapping={t:'M'+str(int(mappings[best][i])) for i,t in enumerate(vocab)}
    return mapping,dict(selected_K=path[best]['K'],path=path,training_types=V,context_dimensions=D)

def metrics(words):
    counts=Counter(t for w in words for t in w); n=sum(counts.values())
    pairs=Counter(p for w in words for p in zip(w,w[1:])); left=Counter()
    for (a,b),c in pairs.items(): left[a]+=c
    h1=entropy(counts.values())
    h2=sum(-c*math.log2(c/left[a]) for (a,b),c in pairs.items())/sum(pairs.values()) if pairs else None
    bins=defaultdict(Counter)
    for w in words:
        for i,t in enumerate(w):
            key='singleton' if len(w)==1 else 'initial' if i==0 else 'final' if i==len(w)-1 else 'interior'
            bins[key][t]+=1
    pe=sum(sum(c.values())*entropy(c.values()) for c in bins.values())/n if n else None
    slope=float(np.polyfit(np.log(np.arange(1,len(counts)+1)),np.log(sorted(counts.values(),reverse=True)),1)[0]) if len(counts)>1 else None
    result=dict(inventory=len(counts),h1=h1,h2=h2,ratio=h2/h1 if h1 and h2 is not None else None,
                slope=slope,word_length=n/len(words) if words else None,positional_entropy=pe,
                words=len(words),units=n,adjacent_pairs=sum(pairs.values()),
                bins={b:dict(count=sum(c.values()),entropy=entropy(c.values())) for b,c in bins.items()})
    result['valid']=len(counts)>1 and h1>0 and all(result[k] is not None and math.isfinite(result[k]) for k in KEYS)
    return result

def noise(text, labels, randomizer):
    alphabet=sorted(set(text)|{' '}); out=[]; ids=[]
    for i,(c,lab) in enumerate(zip(text,labels)):
        x=randomizer.random()
        if x<RATES['substitution']:
            ch=randomizer.choice([s for s in alphabet if s!=c]); out.append(ch); ids.append(lab)
        elif x<RATES['substitution']+RATES['deletion']: continue
        elif x<sum(RATES.values()):
            out.extend([randomizer.choice(alphabet),c]); ids.extend([('INSERT',i),lab])
        else: out.append(c); ids.append(lab)
    # Whitespace is canonicalized by splitting while preserving truth labels.
    words=[]; truth=[]; w=[]; labs=[]
    for c,lab in list(zip(out,ids))+[(' ',None)]:
        if c.isspace():
            if w: words.append(''.join(w)); truth.append(labs); w=[]; labs=[]
        else: w.append(c); labs.append(lab)
    return words,truth

def source(code):
    if code=='Occitan':
        raw=SOURCES[code].read_text(encoding='utf-8-sig').lower()
        normalized=''.join(c for c in unicodedata.normalize('NFKD',raw) if not unicodedata.combining(c))
        words=re.findall(r'[^\W\d_]+',normalized,flags=re.UNICODE)[:34509]
        assert len(words)==34509
        return [dict(text_eva=' '.join(words[i:i+200]),group=str(i//200)) for i in range(0,len(words),200)]
    with SOURCES[code].open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    result=[]; pos=0
    for r in rows:
        if code=='C13': group=re.sub(r'[rv].*$','',r['folio'])
        elif code=='C17': group=r.get('source_group') or r['folio']
        else:
            # Exact source blocks; split long/crossing borrowed-layout rows.
            pieces=[]; current_group=None
            for w in r['text_eva'].split():
                group=str(pos//200)
                if current_group is not None and group!=current_group:
                    result.append(dict(text_eva=' '.join(pieces),group=current_group)); pieces=[]
                pieces.append(w); current_group=group
                pos+=1
            if pieces: result.append(dict(text_eva=' '.join(pieces),group=current_group))
            continue
        result.append(dict(text_eva=r['text_eva'],group=group))
    return result

def split_noise(rows,seed):
    groups=sorted({r['group'] for r in rows},key=lambda g:hashlib.sha256(f'{seed}:{g}'.encode()).hexdigest())
    train_groups=set(groups[:len(groups)//2]); train=[]; test=[]; truth=[]
    for i,r in enumerate(rows):
        labels=r.get('labels',list(range(len(r['text_eva']))))
        words,labs=noise(r['text_eva'],labels,rng(seed,'noise:'+str(i)))
        if r['group'] in train_groups: train.extend(words)
        else: test.extend(words); truth.extend(labs)
    return train,test,truth,dict(train_groups=sorted(train_groups),test_groups=sorted(set(groups)-train_groups),
                                train_words=len(train),test_words=len(test),train_characters=sum(map(len,train)),
                                test_characters=sum(map(len,test)))

def author_module(seed):
    tree=ast.parse(AUTHOR.read_text(encoding='utf-8')); selected=[]
    for node in tree.body:
        if isinstance(node,ast.Import):
            node.names=[n for n in node.names if n.name not in ['pandas','random']]
            if not node.names: continue
        if isinstance(node,ast.If): continue
        selected.append(node)
    with TABLE.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    mod=types.ModuleType('author_naibbe')
    mod.__dict__.update(random=random.Random(seed),pd=types.SimpleNamespace(read_csv=lambda _: {k:[r[k] for r in rows] for k in rows[0]}))
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected,type_ignores=[])),str(AUTHOR),'exec'),mod.__dict__)
    return mod

def positive(code,deck,seed):
    mod=author_module(seed); events=[]
    class Capture(dict):
        def get(self,k,default=None):
            value=super().get(k,default); events.append((k,value)); return value
    plain=' '.join(r['text_eva'] for r in source(code))
    encoded=mod.encrypt_naibbe(mod.clean_line(plain),mod.naibbe_tables,Capture(mod.placeholder_to_glyph),use_78=deck==78)
    # Replay author lookup events, dropping exactly the ambiguity-rejected pair draws.
    actual=[]; e=0
    while e<len(events):
        key,glyph=events[e]; e+=1
        if key.startswith('unigram_'): actual.append([glyph])
        else:
            assert key.startswith('prefix_')
            key2,suffix=events[e]; e+=1
            assert key2.startswith('suffix_')
            if glyph+suffix not in mod.unigram_glyphs: actual.append([glyph,suffix])
    assert [''.join(v) for v in actual]==encoded
    assert len(encoded)>=34509, (code,deck,len(encoded))
    rows=[]
    for i in range(0,34509,200):
        words=actual[i:min(i+200,34509)]; text=[]; labels=[]
        for j,chunks in enumerate(words):
            if j: text.append(' '); labels.append(None)
            for k,chunk in enumerate(chunks):
                text.extend(chunk); labels.extend([(i+j,k)]*len(chunk))
        rows.append(dict(text_eva=''.join(text),labels=labels,group=str(i//200)))
    return rows,dict(encoded_words=len(encoded),selected_words=34509,ambiguity_retries=mod.ambiguity_retries,
                     truth_chunks=sum(len(w) for w in actual[:34509]))

def boundary(words,truth,tokenizer):
    tp=fp=fn=0
    for w,labs in zip(words,truth):
        gold={i for i in range(1,len(w)) if labs[i]!=labs[i-1]}
        chunks=tokenizer.word(w); assert ''.join(chunks)==w
        pred=set(); p=0
        for t in chunks[:-1]: p+=len(t); pred.add(p)
        tp+=len(pred&gold); fp+=len(pred-gold); fn+=len(gold-pred)
    return dict(tp=tp,fp=fp,fn=fn,precision=tp/(tp+fp) if tp+fp else 0.,
                recall=tp/(tp+fn) if tp+fn else None,
                f1=2*tp/(2*tp+fp+fn) if tp+fn else None,observable=tp+fn)

def fit_evaluate(train,test,method,truth=None):
    tok=Tokenizer(method,train)
    tw=[tok.word(w) for w in train]; hw=[tok.word(w) for w in test]
    mapping,merge=merge_fit(tw)
    post=[tuple(mapping.get(t,'UNKNOWN:'+t) for t in w) for w in hw]
    result=dict(pre=metrics(hw),post=metrics(post),merge=merge,
                tokenizer=tok.meta,merge_map=mapping,
                unknown_units=sum(t not in mapping for w in hw for t in w),
                fallback_glyphs=sum(len(t) for w in hw for t in w if len(t)==1 and t not in tok.chunks))
    if truth is not None: result['boundary']=boundary(test,truth,tok)
    # Cached bound-method keys hold self; clear explicitly between fits.
    tok.word.cache_clear()
    return result

def band(rows):
    if any(not r['valid'] for r in rows): return dict(valid=False,reason='nonestimable natural vector')
    return dict(valid=True,intervals={k:[float(x) for x in np.quantile([r[k] for r in rows],[.025,.975],method='linear')] for k in KEYS})
def inside(m,b): return bool(m['valid'] and b['valid'] and all(b['intervals'][k][0]<=m[k]<=b['intervals'][k][1] for k in KEYS))
def primary(m,bands,method): return inside(m,bands[method]['post']) and inside(m,bands['raw_letters'])

def sealed_files():
    return [HERE/'PROTOCOL.md',HERE/'SOURCES.md',HERE/'run.py',HERE/'test_instrument.py',TABLE,AUTHOR,JAVA,
            ROOT/'report/noise_model.json',OLD/'SOURCE_AUDIT.json',ROOT/'SOURCES.md',OLD/'SOURCES.md']+list(SOURCES.values())
def register():
    assert not (HERE/'REGISTRATION.json').exists(), 'Registration is immutable'
    assert json.loads((ROOT/'report/noise_model.json').read_text())['rates']==RATES
    dump(HERE/'REGISTRATION.json',dict(phase=11,status='REGISTERED_BEFORE_CONTROL_FITS',
         time=datetime.now(timezone.utc).isoformat(),seeds=SEEDS,methods=METHODS,metrics=KEYS,
         python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
         files={str(p.relative_to(ROOT)):sha(p) for p in sealed_files()},voynich='CLOSED',secondary='CLOSED'))
def verify():
    reg=json.loads((HERE/'REGISTRATION.json').read_text())
    bad=[p for p,h in reg['files'].items() if sha(ROOT/p)!=h]
    if bad: raise RuntimeError('Seal mismatch: '+str(bad))
    assert reg['python']==sys.version and reg['numpy']==np.__version__ and reg['scipy']==scipy.__version__
    return reg

def controls():
    verify(); out=HERE/'results'; out.mkdir(exist_ok=True)
    assert not (HERE/'QUALIFICATION.json').exists(), 'Do not rerun a completed bank'
    natural=['C1','C2','C3','C13','Occitan']
    vectors=defaultdict(list); raw=[]
    for code in natural:
        rows=source(code)
        for seed in SEEDS:
            train,test,truth,split=split_noise(rows,seed)
            raw.append(metrics([tuple(w) for w in test]))
            for method in METHODS:
                path=out/f'natural-{code}-{seed}-{method}.json'
                if path.exists(): result=json.loads(path.read_text())
                else:
                    result=dict(family=code,seed=seed,method=method,split=split,**fit_evaluate(train,test,method))
                    dump(path,result)
                for stage in ['pre','post']: vectors[method,stage].append(result[stage])
            print('natural',code,seed,flush=True)
    bands={method:{stage:band(vectors[method,stage]) for stage in ['pre','post']} for method in METHODS}
    bands['raw_letters']=band(raw)
    bands['self_coverage']={method:{stage:sum(inside(m,bands[method][stage]) for m in vectors[method,stage])/100 for stage in ['pre','post']} for method in METHODS}
    bands['registration_sha256']=sha(HERE/'REGISTRATION.json')
    # Do not overwrite a previous frozen band on resume.
    if (HERE/'BAND.json').exists(): assert json.loads((HERE/'BAND.json').read_text())==bands
    else: dump(HERE/'BAND.json',bands)
    positive_cells=[]
    for code in ['C1','C2']:
        for deck in [52,78]:
            successes=Counter(); detail=[]
            for seed in SEEDS:
                rows,encoding=positive(code,deck,seed)
                train,test,truth,split=split_noise(rows,seed)
                for method in METHODS:
                    path=out/f'positive-{code}-{deck}-{seed}-{method}.json'
                    if path.exists(): result=json.loads(path.read_text())
                    else:
                        result=dict(family=code,deck=deck,seed=seed,method=method,encoding=encoding,split=split,
                                    **fit_evaluate(train,test,method,truth))
                        dump(path,result)
                    compatible=primary(result['post'],bands,method)
                    f1=result['boundary']['f1']; passed=compatible and f1 is not None and f1>=.8
                    successes[method]+=int(passed)
                    detail.append(dict(seed=seed,method=method,f1=f1,band=compatible,pass_both=passed))
                print('positive',code,deck,seed,flush=True)
            for method in METHODS:
                positive_cells.append(dict(family=code,deck=deck,method=method,successes=successes[method],
                    replicates=20,passed=successes[method]>=16,detail=[r for r in detail if r['method']==method]))
    negatives=[]
    for code in ['C7','C8','C9','C11','C17']:
        rows=source(code); union=0; detail=[]; hits=Counter()
        for seed in SEEDS:
            train,test,truth,split=split_noise(rows,seed); branch=[]
            for method in METHODS:
                path=out/f'negative-{code}-{seed}-{method}.json'
                if path.exists(): result=json.loads(path.read_text())
                else:
                    result=dict(family=code,seed=seed,method=method,split=split,**fit_evaluate(train,test,method))
                    dump(path,result)
                hit=primary(result['post'],bands,method); branch.append(hit); hits[method]+=int(hit)
                detail.append(dict(seed=seed,method=method,hit=hit))
            union+=int(any(branch)); print('negative',code,seed,flush=True)
        negatives.append(dict(family=code,hits=union,replicates=20,rate=union/20,
                              non_discriminating=union>=4,branch_hits=dict(hits),detail=detail))
    eligible=[m for m in METHODS if all(c['passed'] for c in positive_cells if c['method']==m)]
    calibration=bool(eligible)
    specificity=all(not c['non_discriminating'] for c in negatives)
    state='PASS' if calibration and specificity else 'NON_DISCRIMINATING' if not specificity else 'CALIBRATION_FAILED'
    dump(HERE/'QUALIFICATION.json',dict(status=state,calibration_pass=calibration,specificity_pass=specificity,
         eligible_tokenizers=eligible,positive_cells=positive_cells,negatives=negatives,band_sha256=sha(HERE/'BAND.json'),
         registration_sha256=sha(HERE/'REGISTRATION.json'),voynich='ELIGIBLE_FOR_SEPARATE_TARGET_SEAL' if state=='PASS' else 'CLOSED',
         secondary='CLOSED',completed=datetime.now(timezone.utc).isoformat()))
    print(state,flush=True)

if __name__=='__main__':
    {'register':register,'verify':verify,'controls':controls}[sys.argv[1]]()
