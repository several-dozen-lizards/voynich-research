"""Replay saved tokenizers; keep synthetic truth out of learner arguments."""
import importlib.util,json,re
from collections import defaultdict
from pathlib import Path
import hmm as h
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'phase11_plaintext_units_v1'
AMEND=HERE.parent/'phase11a_continuous_units_v1'
spec=importlib.util.spec_from_file_location('phase11a_frozen',AMEND/'run.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
p=a.p
np=h.np

def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def dump(path,data): p.dump(path,data)

def naibbe(code,deck,seed):
    mod=p.author_module(seed); events=[]
    class Capture(dict):
        def get(self,key,default=None):
            glyph=super().get(key,default); events.append((key,glyph)); return glyph
    plain=mod.clean_line(' '.join(r['text_eva'] for r in p.source(code)))
    encoded=mod.encrypt_naibbe(plain,mod.naibbe_tables,Capture(mod.placeholder_to_glyph),use_78=deck==78)
    accepted=[]; i=0
    while i<len(events):
        key,glyph=events[i]; i+=1
        if key.startswith('unigram_'): accepted.append([(glyph,ord(key[-1])-97)])
        else:
            k2,g2=events[i]; i+=1
            assert key.startswith('prefix_') and k2.startswith('suffix_')
            if glyph+g2 not in mod.unigram_glyphs:
                accepted.append([(glyph,ord(key[-1])-97),(g2,ord(k2[-1])-97)])
    assert [''.join(g for g,l in w) for w in accepted]==encoded
    letters=''.join(chr(l+97) for w in accepted for g,l in w)
    assert letters==plain.replace(' ','')
    rows=[]; truth={}; inst=0
    for start in range(0,34509,200):
        chars=[]; ids=[]
        for j,chunks in enumerate(accepted[start:min(start+200,34509)]):
            if j: chars.append(' '); ids.append(None)
            for glyph,label in chunks:
                truth[inst]=label; chars.extend(glyph); ids.extend([inst]*len(glyph)); inst+=1
        rows.append(dict(text_eva=''.join(chars),labels=ids,group=str(start//200)))
    original,metadata=p.positive(code,deck,seed)
    assert [r['text_eva'] for r in rows]==[r['text_eva'] for r in original]
    return rows,truth

def c7():
    rows=p.source('C7'); words=[w for r in p.source('C1') for w in r['text_eva'].split()]
    source_map=read(p.ROOT/'data/controls/C1/metadata.json')['symbol_mapping']
    inverse={v:k for k,v in source_map.items()}; assert len(inverse)==len(source_map)
    words=[''.join(inverse[c] for c in w) for w in words]
    meta=read(p.ROOT/'data/controls/C7/metadata.json')
    code={c:''.join(meta['symbol_mapping'][g] for g in glyph) for c,glyph in meta['codebook'].items()}
    result=[]; truth={}; inst=0; wi=0
    for row in rows:
        chars=[]; ids=[]
        for j,cipherword in enumerate(row['text_eva'].split()):
            word=words[wi]; wi+=1
            assert ''.join(code[c] for c in word)==cipherword
            if j: chars.append(' '); ids.append(None)
            for c in word:
                glyph=code[c]; truth[inst]=ord(c)-97
                chars.extend(glyph); ids.extend([inst]*len(glyph)); inst+=1
        result.append(dict(text_eva=''.join(chars),labels=ids,group=row['group']))
    assert wi==34509
    return result,truth

def truncate(rows,fraction):
    n=int(sum(len(r['text_eva'].split()) for r in rows)*fraction); out=[]; remain=n
    for r in rows:
        matches=list(re.finditer(r'\S+',r['text_eva']))
        if not remain: break
        end=matches[min(remain,len(matches))-1].end(); remain-=min(remain,len(matches))
        out.append({**r,'text_eva':r['text_eva'][:end],**({'labels':r['labels'][:end]} if 'labels' in r else {})})
    assert remain==0
    return out,n

def dataset(kind,code,deck,seed,method,fraction):
    if kind=='naibbe': rows,truth=naibbe(code,deck,seed); oldkind='positive'
    elif kind=='c7': rows,truth=c7(); oldkind='negative'
    else: rows=p.source(code); truth={}; oldkind='negative'
    name=f'{oldkind}-{code}-'+(str(deck)+'-' if deck else '')+f'{seed}-{method}.json'
    saved=read(OLD/'results'/name); tok=a.restore(method,saved['tokenizer'])
    rows,nwords=truncate(rows,fraction)
    groups={r['group'] for r in rows}
    training=set(saved['split']['train_groups'])&groups
    heldout=sorted(groups-training,key=lambda g:p.rng(seed,'hmm_validation:'+g).random())
    validation=set(heldout[:len(heldout)//2]); evaluation=set(heldout[len(heldout)//2:])
    assert training and validation and evaluation
    assert not(training&validation or training&evaluation or validation&evaluation)
    roles={}; records={role:[] for role in ['train','validation','evaluation']}; true_ids={role:set() for role in records}
    for i,row in enumerate(rows):
        role='train' if row['group'] in training else 'validation' if row['group'] in validation else 'evaluation'
        roles[row['group']]=role
        labels=row.get('labels',list(range(len(row['text_eva']))))
        words,labs=p.noise(row['text_eva'],labels,p.rng(seed,'noise:'+str(i)))
        if truth: true_ids[role].update(v for v in labels if isinstance(v,int))
        for word,ids in zip(words,labs):
            chunks=tok.word(word); assert ''.join(chunks)==word
            pos=0
            for chunk in chunks:
                span=ids[pos:pos+len(chunk)]; pos+=len(chunk)
                origins=[v if isinstance(v,int) and v in truth else -1 for v in span] if truth else []
                records[role].append((row['group'],chunk,origins))
    vocab=sorted({t for g,t,ids in records['train']}); vi={t:i for i,t in enumerate(vocab)}; V=len(vocab)+1
    result={}; oracle={}
    for role,current in records.items():
        x=np.array([vi.get(t,V-1) for g,t,ids in current],dtype=np.int64)
        starts=np.array([i==0 or current[i-1][0]!=g for i,(g,t,ids) in enumerate(current)],dtype=np.bool_)
        result[role]=(x,starts)
        if truth:
            unit=[]; instance=[]
            for idx,(g,t,ids) in enumerate(current):
                unit.extend([idx]*len(ids)); instance.extend(ids)
            keys=sorted(true_ids[role]); mapping={v:i for i,v in enumerate(keys)}
            oracle[role]=dict(unit=np.array(unit,dtype=np.int64),
                  instance=np.array([mapping.get(v,-1) for v in instance],dtype=np.int64),
                  true=np.array([truth[v] for v in keys],dtype=np.int64))
    tok.word.cache_clear()
    metadata=dict(kind=kind,family=code,deck=deck,seed=seed,tokenizer=method,fraction=fraction,
         words_before_noise=nwords,units={r:len(x) for r,(x,s) in result.items()},
         groups={r:sum(v==r for v in roles.values()) for r in records},
         group_assignment=roles,emission_inventory=V,training_chunk_types=V-1,
         true_alphabet_size=len(set(truth[v] for role in true_ids for v in true_ids[role])) if truth else None,
         oov={r:int(np.sum(x==V-1)) for r,(x,s) in result.items()},
         tokenizer_source=str((OLD/'results'/name).relative_to(p.ROOT)),tokenizer_source_sha256=p.sha(OLD/'results'/name),
         tokenizer_refits=0,short_length_tokenizer='full-length Phase11 tokenizer retained')
    return result,oracle,metadata

def recovery(z,oracle,K):
    from sklearn.metrics import v_measure_score
    votes=np.zeros((len(oracle['true']),K),dtype=np.int64)
    mask=oracle['instance']>=0
    np.add.at(votes,(oracle['instance'][mask],z[oracle['unit'][mask]]),1)
    missing=votes.sum(axis=1)==0
    state=votes.argmax(axis=1); state[missing]=K
    contingency=np.zeros((K,26),dtype=np.int64)
    for s,t in zip(state,oracle['true']):
        if s<K: contingency[s,t]+=1
    return dict(many_to_one_accuracy=float(contingency.max(axis=1).sum()/len(state)),
         v_measure=float(v_measure_score(oracle['true'],state)),letter_instances=len(state),
         deleted_instances=int(missing.sum()),surviving_fraction=float(1-missing.mean()),
         evaluation='one vote per observed glyph, majority state per plaintext-letter instance; deleted instances incorrect; no label map exported')
