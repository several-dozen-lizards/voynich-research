"""Process orchestration for independent registered replay families only."""
import sys
import uuid
import json
from concurrent.futures import ProcessPoolExecutor
import run as a

def atomic(path,data):
    tmp=path.with_suffix('.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    tmp.replace(path)

def job(args):
    a.verify()
    kind,code,deck=args
    assert kind in ['natural','positive','negative']
    a.dump=atomic
    a.replay_family(kind,code,None if deck=='none' else int(deck))

if __name__=='__main__':
    jobs=[tuple(s.split(':')) for s in sys.argv[1:]]
    with ProcessPoolExecutor(max_workers=min(3,len(jobs))) as pool: list(pool.map(job,jobs))
