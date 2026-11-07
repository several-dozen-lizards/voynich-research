"""Cache independent control jobs using the sealed instrument, never target data.

An orchestration helper only: no selection/evaluation formulas live here.
The sequential registered controls command verifies and aggregates these files.
Assign families ahead of that command to avoid duplicate work.
"""
import sys
import json
import uuid
from concurrent.futures import ProcessPoolExecutor
import run as p

def cache_dump(path,data):
    # Distinct temporary names avoid collision with the sequential aggregator.
    tmp=path.with_suffix('.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    tmp.replace(path)

def family_job(arg):
    kind,code,deck=arg
    p.verify()
    out=p.HERE/'results'
    if kind!='natural':
        assert (p.HERE/'BAND.json').exists(), 'Band must be frozen first'
    base=None if kind=='positive' else p.source(code)
    for seed in p.SEEDS:
        if kind=='positive': rows,encoding=p.positive(code,deck,seed)
        else: rows=base; encoding=None
        train,test,truth,split=p.split_noise(rows,seed)
        for method in p.METHODS:
            name=f'{kind}-{code}-'+(f'{deck}-' if kind=='positive' else '')+f'{seed}-{method}.json'
            path=out/name
            if path.exists(): continue
            result=dict(family=code,seed=seed,method=method,split=split,
                        **p.fit_evaluate(train,test,method,truth if kind=='positive' else None))
            if kind=='positive': result.update(deck=deck,encoding=encoding)
            cache_dump(path,result)
        print(kind,code,deck,seed,flush=True)

if __name__=='__main__':
    # Explicit finite task list, no new replicates or parameter choices.
    jobs=[tuple(s.split(':')) for s in sys.argv[1:]]
    jobs=[(kind,code,int(deck) if deck!='none' else None) for kind,code,deck in jobs]
    with ProcessPoolExecutor(max_workers=min(3,len(jobs))) as pool:
        list(pool.map(family_job,jobs))
