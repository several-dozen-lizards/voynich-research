"""Declared evaluation-only amendment: replay frozen Phase11 models, no refits."""
import csv
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'phase11_plaintext_units_v1'
spec=importlib.util.spec_from_file_location('phase11_frozen',PRIOR/'run.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
np=p.np
KEYS=['inventory','h1','h2','ratio','slope']
NATURAL=['C1','C2','C3','C13','Occitan']
NEGATIVE=['C7','C8','C9','C11','C17']

def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def dump(path,data): p.dump(path,data)
def original_files():
    return sorted(f for f in PRIOR.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
def prior_hashes(): return {str(f.relative_to(p.ROOT)):p.sha(f) for f in original_files()}

def audit():
    assert not (HERE/'REGISTRATION.json').exists(), 'Read-only audit precedes registration'
    rows=list(csv.DictReader((PRIOR/'METRICS.csv').open(encoding='utf-8',newline='')))
    bands=read(PRIOR/'BAND.json'); diag=read(PRIOR/'DIAGNOSTICS.json')
    result={}
    for stage in ['pre','post']:
        selected=[r for r in rows if r['kind']=='positive' and r['method']=='T-N' and r['stage']==stage]
        assert len(selected)==80
        result[stage]={}
        for k in p.KEYS:
            lo,hi=bands['T-N'][stage]['intervals'][k]; vals=[float(r[k]) for r in selected]
            result[stage][k]=dict(n=80,below=sum(v<lo for v in vals),above=sum(v>hi for v in vals),
                                  observed_range=[min(vals),max(vals)],band=[lo,hi])
            if stage=='post':
                assert {z:result[stage][k][z] for z in ['below','above']}==diag['pipeline_coordinate_failures']['T-N'][k]
    dump(HERE/'READ_ONLY_AUDIT.json',dict(status='READ_ONLY_NO_REFITS',pipeline_band=result,
         diagnosis='Inventory/h1/h2 fail every pre and post vector. Merge stage is primary problem, not band/spaces alone.',
         files={name:p.sha(PRIOR/name) for name in ['DIAGNOSTICS.json','METRICS.csv','BAND.json']},
         reported_before_amendment_scoring=True))

def restore(method,state):
    tok=p.Tokenizer.__new__(p.Tokenizer)
    tok.method=method; tok.meta=state; tok.alphabet=[]
    tok.pairs,tok.chunks=p.published(); tok.merges=[]
    if method=='T-N':
        first=defaultdict(list)
        for t in state['inventory']: first[t[0]].append(t)
        tok.byfirst={k:sorted(v,key=lambda t:(-len(t),t)) for k,v in first.items()}
        tok.cost=state['costs']; tok.escape=state['escape']
    elif method=='T-MDL': tok.merges=[tuple(pair) for pair in state['full_path'][:state['selected_prefix']]]
    return tok

def continuous(groups):
    c=Counter(t for g in groups for t in g)
    pairs=Counter(pair for g in groups for pair in zip(g,g[1:])); left=Counter()
    for (a,b),n in pairs.items(): left[a]+=n
    h1=p.entropy(c.values())
    h2=sum(-n*math.log2(n/left[a]) for (a,b),n in pairs.items())/sum(pairs.values()) if pairs else None
    slope=float(np.polyfit(np.log(np.arange(1,len(c)+1)),np.log(sorted(c.values(),reverse=True)),1)[0]) if len(c)>1 else None
    r=dict(inventory=len(c),h1=h1,h2=h2,ratio=h2/h1 if h1 and h2 is not None else None,slope=slope,
           units=sum(c.values()),adjacent_pairs=sum(pairs.values()),groups=len(groups))
    r['valid']=len(c)>1 and h1>0 and all(r[k] is not None and math.isfinite(r[k]) for k in KEYS)
    return r

def evaluate(rows,seed,method,saved,positive=False):
    train,test,truth,split=p.split_noise(rows,seed)
    assert split==saved['split']
    tok=restore(method,saved['tokenizer'])
    word_units=[tok.word(w) for w in test]
    for w,ts in zip(test,word_units): assert ''.join(ts)==w
    merged_words=[tuple(saved['merge_map'].get(t,'UNKNOWN:'+t) for t in w) for w in word_units]
    # Reproduction must pass before the new metrics are trusted.
    for label,words in [('pre',word_units),('post',merged_words)]:
        old=p.metrics(words)
        assert old==saved[label], (seed,method,label,'Phase11 metric replay mismatch')
    if positive:
        assert p.boundary(test,truth,tok)==saved['boundary']
    # Replay only row noise to retain source boundaries and held-out gaps.
    groups=defaultdict(list); position=0
    for i,row in enumerate(rows):
        if row['group'] not in set(split['test_groups']): continue
        words,labs=p.noise(row['text_eva'],row.get('labels',list(range(len(row['text_eva'])))),p.rng(seed,'noise:'+str(i)))
        for word in words:
            assert test[position]==word
            groups[row['group']].extend(word_units[position]); position+=1
    assert position==len(test)
    pre=list(groups.values())
    post=[[saved['merge_map'].get(t,'UNKNOWN:'+t) for t in g] for g in pre]
    result=dict(method=method,seed=seed,pre=continuous(pre),post=continuous(post),split=split,
                descriptive={stage:{k:saved[stage][k] for k in ['word_length','positional_entropy']} for stage in ['pre','post']},
                reproduction='EXACT',prior_model_sha256=saved['_sha'],
                boundary=saved.get('boundary'),selected_K=saved['merge']['selected_K'],
                mdl_cap=saved['tokenizer'].get('cap_reached'))
    tok.word.cache_clear()
    return result

def joint_band(vectors):
    assert len(vectors)==100 and all(r['valid'] for r in vectors), 'BAND_FAILED: natural bank not estimable'
    x=np.array([[r[k] for k in KEYS] for r in vectors],dtype=float)
    mean=x.mean(axis=0); sd=x.std(axis=0); zero=sd==0; sd[zero]=1
    z=(x-mean)/sd; cov=z.T@z/len(x)
    shrunk=.95*cov+.05*np.eye(len(KEYS)); inverse=np.linalg.inv(shrunk)
    d=np.einsum('ij,jk,ik->i',z,inverse,z)
    threshold=float(np.quantile(d,.95,method='higher'))
    coverage=float(np.mean(d<=threshold))
    assert coverage>=.95,'BAND_FAILED: self-coverage below .95'
    return dict(keys=KEYS,mean=mean.tolist(),sd=sd.tolist(),zero_sd=zero.tolist(),covariance=cov.tolist(),
                shrinkage=.05,inverse=inverse.tolist(),threshold=threshold,self_coverage=coverage,
                natural_distances=d.tolist(),n=100)

def distance(r,b):
    if not r['valid']: return None
    z=(np.array([r[k] for k in KEYS])-np.array(b['mean']))/np.array(b['sd'])
    return float(z@np.array(b['inverse'])@z)
def inside(r,b):
    d=distance(r,b)
    return d is not None and d<=b['threshold']
def expectation(probability):
    success=sum(math.comb(20,k)*probability**k*(1-probability)**(20-k) for k in range(16,21))
    return dict(p=probability,expected_successes=20*probability,probability_at_least_16=success,
                probability_below_16=max(0.,1-success),assumption='Hypothetical independent Bernoulli acceptance and perfect boundaries; not inferred from self-coverage')

def register():
    assert not (HERE/'REGISTRATION.json').exists()
    p.verify()
    assert (HERE/'READ_ONLY_AUDIT.json').exists()
    files=[HERE/n for n in ['PROTOCOL.md','run.py','test_instrument.py','READ_ONLY_AUDIT.json']]
    dump(HERE/'REGISTRATION.json',dict(phase='11a',status='REGISTERED_BEFORE_AMENDED_SCORES',
         time=datetime.now(timezone.utc).isoformat(),python=sys.version,numpy=np.__version__,scipy=p.scipy.__version__,
         files={str(f.relative_to(p.ROOT)):p.sha(f) for f in files},phase11=prior_hashes(),
         evaluation_only=True,refits=0,seeds=p.SEEDS,methods=p.METHODS,metrics=KEYS,
         band=dict(kind='standardized shrinkage Mahalanobis',shrinkage=.05,quantile=.95,method='higher'),
         nominal_binomial=expectation(.95),voynich='CLOSED'))

def verify():
    reg=read(HERE/'REGISTRATION.json'); p.verify()
    for f,h in {**reg['files'],**reg['phase11']}.items(): assert p.sha(p.ROOT/f)==h, f
    assert reg['phase11']==prior_hashes(), 'Phase11 scientific artifact set changed'
    assert reg['python']==sys.version and reg['numpy']==np.__version__ and reg['scipy']==p.scipy.__version__
    return reg

def replay_family(kind,code,deck=None):
    if kind!='natural': assert (HERE/'BAND.json').exists(), 'Band freeze must precede amended control evaluation'
    result=[]; base=None if kind=='positive' else p.source(code)
    for seed in p.SEEDS:
        if kind=='positive': rows,encoding=p.positive(code,deck,seed)
        else: rows=base; encoding=None
        for method in p.METHODS:
            name=f'{kind}-{code}-'+(str(deck)+'-' if deck else '')+f'{seed}-{method}.json'
            saved=read(PRIOR/'results'/name); saved['_sha']=p.sha(PRIOR/'results'/name)
            path=HERE/'results'/name
            if path.exists(): r=read(path); assert r['prior_model_sha256']==saved['_sha']
            else:
                r=dict(kind=kind,family=code,deck=deck,**evaluate(rows,seed,method,saved,kind=='positive'))
                if encoding is not None: assert encoding==saved['encoding']
                dump(path,r)
            result.append(r)
        print(kind,code,deck,seed,flush=True)
    return result

def natural():
    verify(); (HERE/'results').mkdir(exist_ok=True)
    assert not (HERE/'BAND.json').exists(), 'Band is immutable'
    rows=[]
    for code in NATURAL: rows.extend(replay_family('natural',code))
    bands={}
    for method in p.METHODS:
        bands[method]={}
        for stage in ['pre','post']:
            selected=[r for r in rows if r['method']==method]
            b=joint_band([r[stage] for r in selected])
            b['natural_rows']=[dict(family=r['family'],seed=r['seed'],metrics=r[stage]) for r in selected]
            b['by_source']={code:dict(self_coverage=sum(inside(r[stage],b) for r in selected if r['family']==code)/20,
                distances=[distance(r[stage],b) for r in selected if r['family']==code]) for code in NATURAL}
            b['binomial_reference']=expectation(b['self_coverage'])
            bands[method][stage]=b
    dump(HERE/'BAND.json',dict(registration_sha256=p.sha(HERE/'REGISTRATION.json'),regions=bands,
                               nominal_binomial=expectation(.95),positive_negative_amended_evaluations_started=False))

def summarize(rows,bands):
    cells=[]
    for code in ['C1','C2']:
        for deck in [52,78]:
            for method in p.METHODS:
                selected=[r for r in rows if r['kind']=='positive' and r['family']==code and r['deck']==deck and r['method']==method]
                assert len(selected)==20
                detail=[dict(seed=r['seed'],f1=r['boundary']['f1'],band=inside(r['post'],bands[method]['post']),
                             distance=distance(r['post'],bands[method]['post'])) for r in selected]
                successes=sum(r['band'] and r['f1'] is not None and r['f1']>=.8 for r in detail)
                cells.append(dict(family=code,deck=deck,method=method,successes=successes,passed=successes>=16,detail=detail))
    eligible=[m for m in p.METHODS if all(c['passed'] for c in cells if c['method']==m)]
    negatives=[]
    for code in NEGATIVE:
        selected=[r for r in rows if r['kind']=='negative' and r['family']==code]; assert len(selected)==60
        detail=[dict(seed=seed,branches={m:inside(next(r['post'] for r in selected if r['method']==m and r['seed']==seed),bands[m]['post']) for m in p.METHODS}) for seed in p.SEEDS]
        hits=sum(any(r['branches'].values()) for r in detail)
        negatives.append(dict(family=code,hits=hits,rate=hits/20,stop_threshold_triggered=hits>=4,detail=detail))
    triggers=any(r['stop_threshold_triggered'] for r in negatives)
    return dict(status='PASS' if eligible and not triggers else 'CALIBRATION_FAILED' if not eligible else 'NON_DISCRIMINATING',
         calibration_pass=bool(eligible),eligible_tokenizers=eligible,positive_cells=cells,negatives=negatives,
         negative_stop_triggered=triggers,
         specificity='NOT_INTERPRETABLE_POSITIVE_CALIBRATION_FAILED' if not eligible else 'FAIL' if triggers else 'PASS',
         voynich='ELIGIBLE_FOR_SEPARATE_TARGET_SEAL' if eligible and not triggers else 'CLOSED',secondary='CLOSED')

def controls():
    verify(); assert not (HERE/'QUALIFICATION.json').exists()
    band=read(HERE/'BAND.json'); assert band['registration_sha256']==p.sha(HERE/'REGISTRATION.json')
    assert all(band['regions'][m][s]['self_coverage']>=.95 for m in p.METHODS for s in ['pre','post'])
    rows=[]
    for code in ['C1','C2']:
        for deck in [52,78]: rows.extend(replay_family('positive',code,deck))
    for code in NEGATIVE: rows.extend(replay_family('negative',code))
    q=summarize(rows,band['regions'])
    dump(HERE/'QUALIFICATION.json',dict(**q,band_sha256=p.sha(HERE/'BAND.json'),registration_sha256=p.sha(HERE/'REGISTRATION.json'),
         completed=datetime.now(timezone.utc).isoformat(),refits=0,nominal_binomial=expectation(.95)))
    print(q['status'],q['specificity'],flush=True)

if __name__=='__main__':
    {'audit':audit,'register':register,'verify':verify,'natural':natural,'controls':controls}[sys.argv[1]]()
