"""Frozen adapter-only qualification; never imports a corpus/vault runner."""
import sys
sys.dont_write_bytecode=True
import copy,hashlib,importlib.util,itertools,json,math,random,time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import beta
P=Path(__file__).parent;ROOT=P.parents[1]
PLAN=json.loads((P/'PLAN.json').read_text(encoding='utf-8'));B=PLAN['permutations'];T=PLAN['trials_per_cell'];ALPHA=PLAN['alpha']
sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/HARNESS'))
sys.path.insert(0,str(ROOT/'ordered-name-lists-v7c/attempt-3-v7.2'))
import harness as h
from role_preserving_keys import random_role_key,invariants
s=importlib.util.spec_from_file_location('adapters',ROOT/PLAN['inputs']['adapters']);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
READS=[];ORACLES=Counter()
def load(rel):
    if rel!=PLAN['inputs']['known_text']:raise RuntimeError('data read outside frozen allowlist')
    READS.append(rel);return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def save(n,x):
    (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def seed(*parts):return int.from_bytes(hashlib.sha256(':'.join(map(str,parts)).encode()).digest()[:8],'big')
def pvalue(obs,null):return (1+int(np.count_nonzero(np.asarray(null)>=obs)))/(len(null)+1)
def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0.,c-r),min(1.,c+r)]
def summarize(rows,positive=False,wrong=False):
    k=sum(r['flag'] for r in rows);n=len(rows);ci=wilson(k,n)
    cp=float(beta.ppf(.95,k+1,n-k)) if k<n else 1.
    gate=(k/n>=.8) if positive else ((1-k/n>=.99 and cp<=.03) if wrong else (k/n<=.05 and ci[1]<=.05))
    return dict(n=n,flags=k,rate=k/n,Wilson95=ci,CP_one_sided95_upper=cp,gate=gate,kind='power' if positive else 'false_flags',rejected=sum(r.get('rejected',False) for r in rows))

def cipher(alphabet,twins=False):
    rr=random.Random(PLAN['seeds']['codebook']+len(alphabet));codes=[''.join(p) for p in itertools.product('abcdefghijklmnopqrstuvwxyz',repeat=2)];rr.shuffle(codes)
    units=codes[:len(alphabet)*(2 if twins else 1)];mapping={u:alphabet[i%len(alphabet)] for i,u in enumerate(units)}
    rules=[dict(unit=u,when={'position':'first'},value=mapping[u],source='fixed initial identity rule') for u in units[:len(alphabet)]] if twins else []
    k=dict(id='synthetic-known-cipher',units=units,map=mapping,rules=rules,target=dict(alphabet=list(alphabet),resources=[PLAN['inputs']['known_text']],system='known synthetic control'),built_on=['control-training'],provenance={u:'seeded fixed cipher; not fitted' for u in units},value_inventory=list(alphabet),condition_inventory=[{'position':'first'}] if twins else [],process_evidence='Fixed independently of held text; synthetic control only')
    h.validate_key(k)
    books=[dict(zip(alphabet,units[i*len(alphabet):(i+1)*len(alphabet)])) for i in range(2 if twins else 1)]
    return k,books

def encode_word(w,book):return None if w is None else ''.join(book[c] for c in w)
def decode_word_source(w,book,key):
    raw=encode_word(w,book);tokens=a.tokenize_unique(raw,key['units']);return tokens

def pair_fixture(left,right,reading,key,books):
    records=[];pairs=[]
    for i,(ls,rs) in enumerate(zip(left,right)):
        spans=[]
        for side,ws in enumerate((ls,rs)):
            rid=f'pair-{i}-{side}';words=[decode_word_source(w,books[side],key) for w in ws]
            records.append(dict(id=rid,folio='synthetic-control',reading=reading,words=words))
            spans.append([[rid,j] for j in range(len(words))])
        pairs.append(dict(id=f'p{i}',a=spans[0],b=spans[1]))
    return records,pairs

def e2_oracle(left,right,reading,key,books):
    records,pairs=pair_fixture(left,right,reading,key,books);z=a.e2_spans(records,pairs,key,h.decode_word);ORACLES['e2_panels']+=1;return z['success']
def exact_pair_count(l,r):return sum(None not in x and None not in y and x==y for x,y in zip(l,r))

def e2_nulls(left,right,kind,rng,pools):
    n=len(left);L=np.array([['' if w is None else w for w in ws] for ws in left]);R=np.array([['' if w is None else w for w in ws] for ws in right]);lc=np.all(L!='',axis=1);rc=np.all(R!='',axis=1)
    def masked(arr,original):return [[None if original[i][j] is None else str(arr[i,j]) for j in range(3)] for i in range(n)]
    if kind=='fake-pair':
        ids=np.argsort(rng.random((B,n)),axis=1);eq=(L[None,:,:]==R[ids]).all(axis=2)&lc[None,:]&rc[ids]
        witnesses=[(left,[right[i] for i in ids[b]]) for b in (0,B-1)]
    elif kind=='word-shuffle':
        li=np.argsort(rng.random((B,n,3)),axis=2);ri=np.argsort(rng.random((B,n,3)),axis=2)
        # Incomplete spans retain all slots; readable complete spans are permuted source-first.
        li[:,~lc,:]=np.arange(3);ri[:,~rc,:]=np.arange(3)
        ll=L[np.arange(n)[None,:,None],li];rr=R[np.arange(n)[None,:,None],ri]
        eq=(ll==rr).all(axis=2)&lc[None,:]&rc[None,:]
        witnesses=[(masked(ll[b],left),masked(rr[b],right)) for b in (0,B-1)]
    elif kind=='glyph-shuffle':
        eq=np.broadcast_to(lc&rc,(B,n)).copy();wl=[[list(ws) for ws in left] for _ in range(2)];wr=[[list(ws) for ws in right] for _ in range(2)]
        for i in range(n):
            for j in range(3):
                x,y=left[i][j],right[i][j]
                mats=[]
                for word in (x,y):
                    if word is None:mats.append(None);continue
                    chars=np.array(list(word));out=np.broadcast_to(chars,(B,len(chars))).copy()
                    if len(chars)>2:out[:,1:-1]=chars[1:-1][np.argsort(rng.random((B,len(chars)-2)),axis=1)]
                    mats.append(out)
                if x is None or y is None or len(x)!=len(y):eq[:,i]=False
                else:eq[:,i]&=(mats[0]==mats[1]).all(axis=1)
                for wi,b in enumerate((0,B-1)):
                    wl[wi][i][j]=None if mats[0] is None else ''.join(mats[0][b]);wr[wi][i][j]=None if mats[1] is None else ''.join(mats[1][b])
        witnesses=list(zip(wl,wr))
    elif kind=='length-fake':
        rr=np.empty((B,n,3),dtype=object)
        for i,ws in enumerate(left):
            for j,w in enumerate(ws):
                pool=[None] if w is None else pools[len(w)]
                rr[:,i,j]=np.array(pool,dtype=object)[rng.integers(len(pool),size=B)]
        eq=(L[None,:,:]==rr).all(axis=2)&lc[None,:]
        witnesses=[(left,rr[b].tolist()) for b in (0,B-1)]
    else:raise ValueError(kind)
    return eq.sum(axis=1),witnesses

def text_trials(phrases,pools,key,books):
    out={};details=[];families=['fake-pair','word-shuffle','glyph-shuffle','length-fake']
    for reading,noise in [('H',.10),('F',.20)]:
        for scenario in ['positive']+families:
            rows=[]
            for trial in range(T):
                rng=np.random.default_rng(seed(82502,scenario,trial));ix=rng.choice(len(phrases),24,replace=False);left=[list(phrases[i]) for i in ix];right=copy.deepcopy(left)
                if scenario=='fake-pair':right=[right[i] for i in rng.permutation(24)]
                elif scenario=='word-shuffle':
                    for side in (left,right):
                        for ws in side:rng.shuffle(ws)
                elif scenario=='glyph-shuffle':
                    for side in (left,right):
                        for ws in side:
                            for j,w in enumerate(ws):
                                mid=list(w[1:-1]);rng.shuffle(mid);ws[j]=w[0]+''.join(mid)+w[-1] if len(w)>1 else w
                elif scenario=='length-fake':right=[[str(rng.choice(pools[len(w)])) for w in ws] for ws in right]
                maskrng=np.random.default_rng(seed(82502,'mask',reading,scenario,trial))
                for side in (left,right):
                    for ws in side:
                        for j in range(3):
                            if maskrng.random()<noise:ws[j]=None
                rng=np.random.default_rng(seed(82502,'null',reading,scenario,trial))
                obs=exact_pair_count(left,right);assert e2_oracle(left,right,reading,key,books)==obs
                ps={}
                for kind in families:
                    null,witnesses=e2_nulls(left,right,kind,rng,pools)
                    for wi,(ll,rr) in enumerate(witnesses):
                        expected=int(null[0 if wi==0 else B-1]);assert e2_oracle(ll,rr,reading,key,books)==expected
                    ps[kind]=pvalue(obs,null)
                row=dict(route='E2',reading=reading,scenario=scenario,trial=trial,success=obs,n=24,p=ps,flag=all(p<=ALPHA for p in ps.values()));rows.append(row);details.append(row)
            out[f'{reading}:{scenario}']=summarize(rows,positive=scenario=='positive');print('E2',reading,scenario,out[f'{reading}:{scenario}'],flush=True);save('RUN-STATE.json',dict(phase='E2',cell=f'{reading}:{scenario}',complete=len(details)))
    save('E2-TRIALS.json',details);return out

def key_banks(phrases,key,books):
    left=[list(x) for x in phrases[:24]];right=copy.deepcopy(left);records,pairs=pair_fixture(left,right,'H',key,books)
    obs=a.e2_spans(records,pairs,key,h.decode_word)['success'];banks={};receipts={};K=h.complexity(key)
    for kind,fn,ss in [('original',h.random_key,82503),('role',random_role_key,82504)]:
        rng=random.Random(ss);scores=[];hashes=[]
        for i in range(B):
            k=fn(key,rng);assert h.complexity(k)==K
            if kind=='role':assert invariants(key,k)
            scores.append(a.e2_spans(records,pairs,k,h.decode_word)['success']);hashes.append(h.digest(k))
        banks[kind]=scores;receipts[kind]=dict(n=B,seed=ss,K_bits=K,distinct_keys=len(set(hashes)),key_hashes=hashes,scores=scores,true_key_p=pvalue(obs,scores),true_key_gate=pvalue(obs,scores)<=ALPHA)
    rows=[];summary={}
    for kind,fn,ss in [('original',h.random_key,82505),('role',random_role_key,82506)]:
        rng=random.Random(ss);rr=[]
        for i in range(T):
            k=fn(key,rng);v=a.e2_spans(records,pairs,k,h.decode_word)['success'];ps={b:pvalue(v,z) for b,z in banks.items()};row=dict(bank=kind,trial=i,success=v,p=ps,flag=all(p<=ALPHA for p in ps.values()),key_sha256=h.digest(k));rows.append(row);rr.append(row)
        summary[kind]=summarize(rr,wrong=True)
    save('KEY-BANKS.json',receipts);save('WRONG-KEY-TRIALS.json',rows);save('KNOWN-KEY.json',key)
    return dict(true_success=obs,n=24,K_bits=K,true_key_gates={k:v['true_key_gate'] for k,v in receipts.items()},negative=summary,scope='E2 component discrimination only; not whole-key coherence/PASS')

class Geometry:
    def __init__(self,lengths):
        self.lengths=lengths;self.n=sum(lengths);self.rows=[];start=0
        for b,n in enumerate(lengths):
            for i in range(n):self.rows.append(dict(id=f'g{start+i}',folio='f70v2',reading='H',band=str(b),position=i,label_span=None,order_source='geometry-only'))
            start+=n
        self.candidates=list(a.alignments(self.rows,100000));self.index={r['id']:i for i,r in enumerate(self.rows)};self.A=np.array([[self.index[i] for i in c['ids']] for c in self.candidates]);self.bands=[];start=0
        for n in lengths:self.bands.append(np.arange(start,start+n));start+=n
        self.orders=list(itertools.permutations(range(len(lengths))));self.local=[np.array([[band[(rot+d*i)%len(band)] for i in range(len(band))] for rot in range(len(band)) for d in (1,-1)]) for band in self.bands]
    def score(self,values,target):
        values=np.atleast_2d(values);target=np.asarray(target)
        if len(target)!=self.n:raise a.NotAdmitted('incompatible unit cardinality; no truncation/wrapping')
        cache={};out=np.zeros(len(values),dtype=int)
        for order in self.orders:
            offset=0;total=np.zeros(len(values),dtype=int)
            for band in order:
                ck=(band,offset)
                if ck not in cache:cache[ck]=(values[:,self.local[band]]==target[offset:offset+self.lengths[band]]).sum(axis=2).max(axis=1)
                total+=cache[ck];offset+=self.lengths[band]
            out=np.maximum(out,total)
        return out
    def oracle(self,values,target):
        fast=int(self.score(values,target)[0]);slow=int((np.asarray(values)[self.A]==np.asarray(target)).sum(axis=1).max());assert fast==slow
        # Reference path through the original adapter, not only a parallel matrix implementation.
        dd=dict(zip((r['id'] for r in self.rows),values));tar=list(target)
        z=a.full_search(self.rows,lambda ids:int(sum(dd[k]==t for k,t in zip(ids,tar))),100000);assert z['value']==fast;assert z['evaluated']==len(self.candidates);ORACLES['alignment_panels']+=1
        return fast
    def shuffle(self,values,rng):
        z=np.broadcast_to(values,(B,self.n)).copy()
        for band in self.bands:z[:,band]=np.asarray(values)[band][np.argsort(rng.random((B,len(band))),axis=1)]
        return z

def order_trials(phrases,pools,text_key,text_books,number_key,number_book):
    out={};details=[]
    for lengths in PLAN['numerals_and_order']['geometries']:
        g=Geometry(lengths);n=g.n
        for route in ('numeral','known-text-order'):
            for reading,noise in [('H',.10),('F',.20)]:
                scenarios=['positive','within-band-null','layout-null','wrong-unit']+(['length-fake'] if route=='known-text-order' else [])
                for scenario in scenarios:
                    rows=[]
                    for trial in range(T):
                        rng=np.random.default_rng(seed(82507,lengths,route,scenario,trial));target=np.arange(1,n+1)
                        # Unknown has numeric identity -1; target labels all have distinct identities.
                        chosen=g.A[int(rng.integers(len(g.A)))];values=np.empty(n,dtype=int);values[chosen]=target
                        if scenario in ('within-band-null','layout-null'):
                            for band in g.bands:values[band]=values[band][rng.permutation(len(band))]
                            # A perfectly regular geometry covariate is present but NOT admitted as label evidence.
                            layout_phase=np.arange(n)%5;assert len(layout_phase)==n
                        elif scenario=='length-fake':
                            fake=[];real=set(phrases)
                            for j in range(n):
                                for attempt in range(1000):
                                    ws=tuple(str(rng.choice(pools[len(w)])) for w in phrases[int(values[j]-1)])
                                    if ws not in real:break
                                else:raise RuntimeError('fake generation failed before scoring')
                                fake.append(list(ws))
                            values=-np.arange(2,n+2)
                        elif scenario=='wrong-unit':
                            try:g.score(values,target[:-1])
                            except a.NotAdmitted:pass
                            else:raise AssertionError('wrong-unit adapter accepted incompatible cardinality')
                            row=dict(route=route,geometry=lengths,reading=reading,scenario=scenario,trial=trial,p=None,flag=False,rejected=True);rows.append(row);details.append(row);continue
                        maskrng=np.random.default_rng(seed(82507,'mask',lengths,route,reading,scenario,trial));mask=maskrng.random(n)<noise;values[mask]=-1
                        # Readable values pass through source encoding, unique tokenization, original decoder,
                        # whole-span adapter and exact-number parser. Metadata IDs remain synthetic/open.
                        source_labels=([None if mask[j] else fake[j] for j in range(n)] if scenario=='length-fake' else [list(phrases[int(i-1)]) if i>0 else None for i in values]) if route=='known-text-order' else [[str(i)] if i>0 else None for i in values]
                        if route=='numeral':
                            records=[]
                            for j,ws in enumerate(source_labels):records.append(dict(id=f'num{j}',folio='synthetic-control',reading=reading,words=[None] if ws is None else [decode_word_source(ws[0],number_book,number_key)]))
                            for j,v in enumerate(values):
                                text=a.decode_span(records,[[f'num{j}',0]],number_key,h.decode_word)
                                assert (text is None and v<0) or a.exact_number(text)==int(v)
                                assert a.numeric_check([text],'sum',str(v))==(v>0)
                            ORACLES['exact_numeric_labels']+=n
                        else:
                            # Same multi-token labels, explicitly preserving word boundaries and unknown slots.
                            l=[list(phrases[i]) for i in range(n)];r=[ws if ws is not None else [None]*3 for ws in source_labels]
                            assert e2_oracle(l,r,reading,text_key,text_books)==int((values==target).sum())
                        rng=np.random.default_rng(seed(82507,'null',lengths,route,reading,scenario,trial))
                        null_values=g.shuffle(values,rng);obs=g.oracle(values,target);null=g.score(null_values,target);assert g.oracle(null_values[0],target)==int(null[0]);p=pvalue(obs,null)
                        row=dict(route=route,geometry=lengths,reading=reading,scenario=scenario,trial=trial,success=obs,n=n,p=p,flag=p<=ALPHA,null_max=int(null.max()),null_min=int(null.min()));rows.append(row);details.append(row)
                    cell=f'{route}:{lengths}:{reading}:{scenario}';out[cell]=summarize(rows,positive=scenario=='positive');print(cell,out[cell],flush=True);save('ORDER-TRIALS.json',details);save('RUN-STATE.json',dict(phase='order',cell=cell,complete=len(details)))
    return out

def main():
    begin=time.time();source=load(PLAN['inputs']['known_text']);cut=len(source)//2;train=source[:cut];held=source[cut:]
    pools=defaultdict(set)
    for chapter in train:
        for w in chapter['words']:
            if w and all(c in 'abcdefghijklmnopqrstuvwxyz' for c in w):pools[len(w)].add(w)
    pools={n:sorted(ws) for n,ws in pools.items()};phrases=[];seen=set()
    for chapter in held:
        words=chapter['words']
        for start in range(0,len(words)-2,3):
            phrase=tuple(words[start:start+3])
            if phrase not in seen and all(w and all(c in 'abcdefghijklmnopqrstuvwxyz' for c in w) and len(w) in pools for w in phrase):seen.add(phrase);phrases.append(phrase)
    assert len(phrases)>=24
    key,books=cipher('abcdefghijklmnopqrstuvwxyz',True);nk,nb=cipher('0123456789')
    # Independent fast-path checks before control outcomes; no data-dependent tuning.
    rng=np.random.default_rng(PLAN['seeds']['verification'])
    for lengths in PLAN['numerals_and_order']['geometries']:
        g=Geometry(lengths)
        for _ in range(20):g.oracle(rng.integers(-1,g.n+1,size=g.n),np.arange(1,g.n+1))
    save('INPUTS.json',dict(source_units=len(source),train_units=[c['unit'] for c in train],held_units=[c['unit'] for c in held],phrase_count=len(phrases),phrase_sha256=h.digest(phrases),read_allowlist=READS,geometry='SYNTHETIC ONLY',noise_assumptions={'H':.10,'F':.20},key_complexity_bits=h.complexity(key)))
    kb=key_banks(phrases,key,books);save('KEY-SUMMARY.json',kb);print('KEY BANKS',kb,flush=True)
    e2=text_trials(phrases,pools,key,books);save('E2-SUMMARY.json',e2)
    order=order_trials(phrases,pools,key,books,nk,nb[0]);save('ORDER-SUMMARY.json',order)
    gates={**{'E2:'+k:v['gate'] for k,v in e2.items()},**{k:v['gate'] for k,v in order.items()},**{'wrong-key:'+k:v['gate'] for k,v in kb['negative'].items()},**{'true-key:'+k:v for k,v in kb['true_key_gates'].items()}}
    result=dict(status='QUALIFIED_ON_DECLARED_ADAPTER_CONTROL_SCOPE' if all(gates.values()) else 'NOT_QUALIFIED_ON_ALL_DECLARED_CELLS',gates=gates,failed=[k for k,v in gates.items() if not v],key_summary=kb,E2=e2,order=order,oracles=dict(ORACLES),data_reads=READS,baseline_write_calls=0,vault='CLOSED',full_B_C_qualification=False,remaining=PLAN['not_qualified_here'],seconds=time.time()-begin)
    save('QUALIFICATION.json',result);save('RUN-STATE.json',dict(phase='complete',status=result['status']));print(json.dumps(dict(status=result['status'],failed=result['failed'],oracles=result['oracles'],seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
