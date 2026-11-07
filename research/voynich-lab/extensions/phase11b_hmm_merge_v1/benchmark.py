"""Runtime qualification on invented streams only; no empirical control fits."""
import json,time
from pathlib import Path
import hmm as h
from numba import set_num_threads
set_num_threads(8)
r=h.np.random.default_rng(4201)
x=r.integers(0,350,30000,dtype=h.np.int64)
start=h.np.zeros(len(x),dtype=h.np.bool_); start[::300]=True
results={}
for algorithm in ['EM','GIBBS']:
    fn=h.em if algorithm=='EM' else h.gibbs
    # Compile outside timed qualification.
    fn(x[:200],start[:200],26,350,123,20)
    t=time.perf_counter()
    if algorithm=='EM': value=fn(x,start,26,350,123,20)
    else: value=fn(x,start,26,350,123,20,10,10)
    results[algorithm]=dict(seconds=time.perf_counter()-t,steps=int(value[-2]),N=30000,K=26,V=350)
print(json.dumps(results),flush=True)
(Path(__file__).resolve().parent/'ENGINEERING_BENCHMARK.json').write_text(json.dumps(dict(invented_only=True,results=results),indent=2),encoding='utf-8')
