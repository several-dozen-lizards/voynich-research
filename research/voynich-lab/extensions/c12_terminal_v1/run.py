from common import *
import multiprocessing as mp,time,gc
from collections import Counter
from src.train import prepare,fit
from src.metrics import measure
def initialize_worker():
    import torch
    torch.set_num_threads(2)
def jobpath(job):return I/'runs'/job
def replay():
    import torch
    cfg=json.loads((I/'configs/phase4.json').read_text());split=json.loads((I/'configs/page_split.json').read_text());p=prepare('C1_clean','T1',cfg,rows=typed(read(R/'reference/SW04/clean.csv')),split=split);p['name']='SW04_clean';checks=[]
    for pos in [False,True]:
        folder=I/'replay'/f'SW04-clean-p{int(pos)}-s1729';model,result=fit(p,'lstm',pos,1729,cfg,folder);del model
        old=json.loads((R/'reference/jobs'/folder.name/'metrics.json').read_text());fields=['validation_bpt','test_bpt','test_tokens','test_unknown_rate','validation_bpc_with_escape','test_bpc_with_escape','training_tokens_seen','effective_token_epochs','selected_step','parameter_count']
        diff={k:dict(old=old[k],new=result[k]) for k in fields if old[k]!=result[k]};checks.append(dict(position=pos,exact=not diff,differences=diff));assert not diff,diff
    dump(R/'REPLAY_VERIFICATION.json',dict(status='PASS',checks=checks,cache_admitted=True));del p;torch.cuda.empty_cache()
def model_free():
    if (R/'model_free.csv').exists():return
    cfg=json.loads((I/'configs/phase3.json').read_text());manifest={(r['setting'],r['version']):r for r in read(R/'DATA_MANIFEST.csv')};rows=[];detail={}
    for s in settings():
        for version in ['clean','noise']:
            rs=typed(read(R/'data'/s['setting']/f'{version}.csv'));metric,d=measure(rs,'T1',cfg['clusters'],None);rows.append({**manifest[s['setting'],version],**metric});detail[s['setting']+':'+version]=d
        print('model-free',s['setting'],flush=True)
    table(R/'model_free.csv',rows);dump(R/'growth_and_lengths.json',detail)
def train_cell(task):
    setting,version,jobs=task;cfg=json.loads((I/'configs/phase4.json').read_text());split=json.loads((I/'configs/page_split.json').read_text());p=prepare('C1_'+version,'T1',cfg,rows=typed(read(R/'data'/setting/f'{version}.csv')),split=split);p['name']=setting+'_'+version
    fp=tensor_fingerprint(p,cfg);assert all(j['tensor_sha256']==fp for j in jobs)
    done=0
    for j in jobs:
        folder=jobpath(j['job'])
        if (folder/'metrics.json').exists():
            r=json.loads((folder/'metrics.json').read_text());assert r['corpus']==p['name'] and r['seed']==j['seed'] and r['with_position']==j['with_position']
        else:
            model,r=fit(p,'lstm',j['with_position'],j['seed'],cfg,folder);del model;done+=1
        dump(folder/'ACCOUNTING.json',dict(status='TRAINED',tensor_sha256=fp,registration_sha256=sha(R/'REGISTRATION.json')))
    del p;gc.collect();return dict(setting=setting,version=version,new_jobs=done,total_jobs=len(jobs))
def main():
    reg=json.loads((R/'REGISTRATION.json').read_text());assert all(sha(R/p)==h for p,h in reg['files'].items()),'Freeze drift'
    if not (R/'REPLAY_VERIFICATION.json').exists():replay()
    model_free();plan=json.loads((R/'JOB_PLAN.json').read_text());groups={}
    for j in plan:
        if j['status']=='TRAIN':groups.setdefault((j['setting'],j['version']),[]).append(j)
    tasks=[(s,v,jobs) for (s,v),jobs in groups.items()];completed=0;events=[]
    with mp.Pool(2,initializer=initialize_worker) as pool:
        for result in pool.imap_unordered(train_cell,tasks,chunksize=1):
            completed+=result['total_jobs'];events.append(result);dump(R/'PROGRESS.json',dict(status='RUNNING',completed_unique_new_jobs=completed,scheduled_unique_new_jobs=sum(len(j) for j in groups.values()),cells=events));print('neural progress',completed,'/',sum(len(j) for j in groups.values()),result['setting'],result['version'],flush=True)
    results=[]
    for j in plan:
        folder=jobpath(j['job']);mode=j['status']
        if mode=='TRAIN':r=json.loads((folder/'metrics.json').read_text());mode='TRAINED'
        else:
            source=(R/j['source']) if mode=='REUSED_PRIOR' else jobpath(j['source'])/'metrics.json';r=json.loads(source.read_text());r=dict(r,corpus=j['setting']+'_'+j['version'],run_dir=str(folder.relative_to(I)),reuse_source=str(source.relative_to(R)),reuse_source_sha256=sha(source));dump(folder/'metrics.json',r);dump(folder/'REUSE.json',dict(status=mode,source=str(source.relative_to(R)),source_sha256=sha(source),tensor_sha256=j['tensor_sha256'],not_an_independent_replication=True))
        results.append({k:v for k,v in r.items() if k!='curve'}|dict(job=j['job'],setting=j['setting'],version=j['version'],status=mode,tensor_sha256=j['tensor_sha256']))
    table(R/'model_runs.csv',results);dump(R/'PROGRESS.json',dict(status='COMPLETE',nominal_jobs=len(results),status_counts=dict(Counter(r['status'] for r in results)),new_ZL_models=0))
    print(json.dumps(dict(status='COMPLETE',nominal_jobs=len(results),status_counts=dict(Counter(r['status'] for r in results)))))
if __name__=='__main__':main()
