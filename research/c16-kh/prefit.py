"""Scheduling-only acceleration: unchanged frozen fit(), disjoint page checkpoints.

No new variants, objective, candidates, parameters, or restarts.
"""
import multiprocessing as mp,sys,os,time,json,hashlib
from collections import defaultdict
from core import Model,fit,alpha
from prepare import R,read,dump,sha
M=None;ARM=None
def init(arm):
    global M,ARM;ARM=arm
    M=Model(json.loads((R/'prepared'/f'{arm}.json').read_text())['train'])
def work(task):
    source,page,seqs=task;kp=R/'results'/ARM/'keys'/f'{source}-clean-{page}.json'
    if kp.exists():return source,page,'cached'
    M.alm.cache.clear()
    if len(M.charcache)>200000:M.charcache.clear()
    start=time.monotonic();key,f=fit(seqs,M);f=dict(f,seconds=time.monotonic()-start)
    ident=hashlib.sha256(json.dumps([[alpha(w) for w in s] for s in seqs],ensure_ascii=True).encode()).hexdigest()
    result=dict(key=key,fit=f,canonical_sha256=ident,registration_sha256=sha(R/'REGISTRATION.json'),schedule='prefit unchanged fit')
    tmp=kp.with_suffix(f'.{os.getpid()}.tmp');dump(tmp,result);tmp.replace(kp)
    return source,page,f['evaluations']
if __name__=='__main__':
    arm=sys.argv[1];tasks=[]
    for source in ['C1','C9','C17']:
        pages=defaultdict(list)
        for r in read(R/'prepared'/f'{source}-clean.csv'):pages[r['folio']].append(r['text_eva'].split())
        tasks.extend((source,page,seqs) for page,seqs in pages.items())
    with mp.Pool(3,initializer=init,initargs=(arm,)) as pool:
        for i,res in enumerate(pool.imap_unordered(work,tasks,chunksize=1)):
            if i%25==0:print(arm,'PREFIT',i+1,'/',len(tasks),res,flush=True)
