"""Expose only previously used v2 synthetic cases; never access manuscript rows."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json
import core
R=Path(__file__).resolve().parent
def job(regime,t):
    ri=('position','junction','phrase','distant_strong','distant_small').index(regime);seed=1220000+ri*1000+t
    return dict(regime=regime,trial=t,seed=seed,result=core.score(core.a.generate(regime,seed)))
if __name__=='__main__':
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        tasks=[pool.submit(job,regime,t) for regime in ('position','junction','phrase','distant_small') for t in range(12)]
        for task in as_completed(tasks):rows.append(task.result())
    summary=[]
    for regime in ('position','junction','phrase','distant_small'):
        rr=[r['result'] for r in rows if r['regime']==regime];summary.append(dict(regime=regime,n=len(rr),flag4=sum(r.get('flag4',False) for r in rr),flag24=sum(r.get('flag24',False) for r in rr),adequate=sum(r.get('adequate',False) for r in rr)))
    (R/'DEVELOPMENT.json').write_text(json.dumps(dict(scope='OLD EXPOSED SYNTHETIC DATA ONLY. Not qualification.',records=rows,summary=summary),indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
