import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
import sys,json,hashlib,time,importlib.util,concurrent.futures,math
P=Path(__file__).resolve().parent
OLD=P.parent/'zodiac-qualification-v85'
spec=importlib.util.spec_from_file_location('v85',OLD/'run.py')
v85=importlib.util.module_from_spec(spec); spec.loader.exec_module(v85)
np=v85.np
REGIMES=v85.REGIMES
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,o): (P/n).write_text(json.dumps(o,indent=2),encoding='utf-8')
def verify():
    f=json.loads((P/'FREEZE.json').read_text())
    for n,h in f['files'].items(): assert sha(P/n)==h,n
    old=json.loads((OLD/'FREEZE.json').read_text())
    for n,h in old['sha256'].items(): assert sha(OLD/n)==h,n
def init():
    global X,KEYS,IDS
    X=np.load(P/'templates.npy'); KEYS=json.loads((P/'keys.json').read_text())
    IDS=np.array([i for i,k in enumerate(KEYS) if k[7]=='457'])
def trial(job):
    regime,j,seed=job; rng=np.random.default_rng(seed)
    if 'signal' in regime:
        k=int(rng.choice(IDS)); y=X[k].astype(float)
        if regime=='noisy_masked_signal':
            flip=rng.random(120)<.1; y[flip]=1-y[flip]; y[rng.random(120)<.15]=np.nan
    else: y,k=v85.make_y(regime,rng,X)
    result=v85.score_engine(X,y,np.random.default_rng(seed+10000000))
    result.update(regime=regime,replicate=j,seed=seed,true_template=k,true_key=None if k is None else KEYS[k],observed=int(np.isfinite(y).sum()),values=[None if not np.isfinite(v) else int(v) for v in y])
    return result
def wilson(k,n,z=1.6448536269514722):
    c=(k/n+z*z/(2*n))/(1+z*z/n); h=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n)
    return [max(0,c-h),min(1,c+h)]
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='freeze':
        assert not (P/'FREEZE.json').exists()
        X,keys=v85.templates(); np.save(P/'templates.npy',X); dump('keys.json',keys)
        jobs=[[r,j,8600000+ri*10000+j] for ri,r in enumerate(REGIMES) for j in range(200 if 'signal' in r else 100)]
        dump('JOBS.json',jobs)
        dump('PROTOCOL.json',{'scope':'Separate section457 synthetic qualification; no manuscript feature scoring or held-out sign inspection.', 'scoring':'Import and call byte-verified v85.score_engine unchanged. Full18424-template family includes457 AND458;199 ring shifts,1e-7 tie tolerance,absolute block-centered correlation,Bonferroni2 retained. No restricted457-only null.', 'positive_sampling':'Uniform among unique457 templates;200 fresh clean and200 fresh10%flip15%missing signals. Both use120 synthetic slots from existing four development geometries. No empirical image labels or ambiguity masks.', 'negative_sampling':'100 fresh trials for each of the five unchanged v85 nuisance generators;500 total.', 'gates':'Every regime required. One-sided95% Wilson lower bound >=.90 clean, >=.80 noisy/masked; upper bound <=.10 for EACH negative. These are per-regime bounds, not simultaneous family confidence intervals. Detection threshold remains adjustedp<=.05. No optional stopping, replacement seeds or gate relaxation.', 'precision':'200 positive trials reduce worst-case two-sided95% binomial margin to about6.9points, around4.2points near90% detection.100 negative trials support an explicit upper-bound gate. Not exact rule recovery or universal nuisance immunity.', 'seeds':'8600000+10000*regime_index+replicate; permutation seed +10000000. Disjoint from v85.', 'source':'Unchanged v85 TABLES and original source caveats; sex classes are historical table categories, not claimed figure sex.', 'ambiguities':'v84 inventory frozen unchanged; Pisces29 and uncertain Leo excluded; garments/enclosures retain unknowns, all pigment unresolved, label adjacency provisional.', 'heldout':'Virgo Libra Scorpio Sagittarius unscored; no development manuscript score either.', 'execution':'Four local worker processes call original scoring code. Completion order may vary; all900 jobs retained. No subagents.'})
        dump('FREEZE.json',{'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':{n:sha(P/n) for n in ['run_suite.py','templates.npy','keys.json','JOBS.json','PROTOCOL.json']},'inherited':{str(Path('..')/'zodiac-qualification-v85'/n):sha(OLD/n) for n in ['run.py','TABLES.json','PROTOCOL.json','FREEZE.json']},'inventory_sha256':sha(P.parent/'zodiac-mapping-v84/ANNOTATIONS.json')})
        print('Frozen900 fresh trials;457 templates:',sum(k[7]=='457' for k in keys),flush=True)
    elif mode=='run':
        verify(); jobs=json.loads((P/'JOBS.json').read_text()); started=time.time()
        with (P/'replicates.jsonl').open('x',encoding='utf-8') as f, concurrent.futures.ProcessPoolExecutor(max_workers=4,initializer=init) as pool:
            futures=[pool.submit(trial,j) for j in jobs]
            for i,future in enumerate(concurrent.futures.as_completed(futures),1):
                result=future.result(); f.write(json.dumps(result)+'\n'); f.flush()
                if i%25==0: print(i,'/900',round(time.time()-started),'seconds',flush=True)
        verify(); print('COMPLETE',flush=True)
