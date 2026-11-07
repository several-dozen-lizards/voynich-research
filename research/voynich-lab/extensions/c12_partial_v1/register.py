from common import *
from src.train import prepare
def main():
    assert not (R/'REGISTRATION.json').exists();ready=json.loads((R/'DATA_READY.json').read_text());assert all(sha(R/p)==h for p,h in ready['files'].items())
    config=json.loads((I/'configs/phase4.json').read_text());split=json.loads((I/'configs/page_split.json').read_text());oldmap={};oldchecks=[]
    for code in ['SW04']+[f'SW{i:02d}' for i in range(9,18)]:
        for version in ['clean','noise']:
            p=prepare('C1_'+version,'T1',config,rows=typed(read(R/'reference'/code/f'{version}.csv')),split=split);fp=tensor_fingerprint(p,config)
            for pos in [False,True]:
                for seed in config['seeds']:
                    folder=R/'reference/jobs'/f'{code}-{version}-p{int(pos)}-s{seed}';spec=json.loads((folder/'config.json').read_text());metric=json.loads((folder/'metrics.json').read_text())
                    assert spec['training']==config and spec['vocabulary']==p['vocabulary'] and spec['page_split']==split and spec['architecture']=='lstm' and spec['tokenization']=='T1' and spec['with_position']==pos and spec['seed']==seed
                    assert metric['torch_version']=='2.9.1+cu128' and metric['device']=='cuda'
                    oldmap.setdefault((fp,pos,seed),str((folder/'metrics.json').relative_to(R)))
            oldchecks.append(dict(reference=code,version=version,tensor_sha256=fp,checks='PASS'));del p
    plan=[];owners={};datasets=[]
    for s in settings():
        for version in ['clean','noise']:
            rows=typed(read(R/'data'/s['setting']/f'{version}.csv'));p=prepare('C1_'+version,'T1',config,rows=rows,split=split);fp=tensor_fingerprint(p,config);datasets.append(dict(setting=s['setting'],version=version,tensor_sha256=fp))
            for pos in [False,True]:
                for seed in config['seeds']:
                    job=f"{s['setting']}-{version}-p{int(pos)}-s{seed}";key=(fp,pos,seed)
                    if key in oldmap:status='REUSED_PRIOR';source=oldmap[key]
                    elif key in owners:status='REUSED_IDENTICAL';source=owners[key]
                    else:status='TRAIN';source=None;owners[key]=job
                    plan.append(dict(job=job,setting=s['setting'],version=version,with_position=pos,seed=seed,tensor_sha256=fp,status=status,source=source))
            del p
            print('prepared job identity',s['setting'],version,flush=True)
    import torch
    assert torch.__version__=='2.9.1+cu128' and torch.cuda.is_available()
    dump(R/'JOB_PLAN.json',plan);table(R/'DATA_IDENTITIES.csv',datasets);dump(R/'CACHE_ADMISSION.json',dict(status='IDENTITY_PASS_PENDING_REPLAY',old_checks=oldchecks,prior_unique_model_jobs=len(oldmap),replay_reference='SW04-clean-p0/p1-s1729'))
    sourcepaths=[p for p in R.glob('*.py')]+[R/'PROTOCOL.md',R/'INPUT_SNAPSHOT.json',R/'JOB_PLAN.json',R/'DATA_IDENTITIES.csv',R/'DATA_MANIFEST.csv',R/'ENGINEERING.json',R/'CACHE_ADMISSION.json']
    frozen={str(p.relative_to(R)):sha(p) for p in sourcepaths};frozen.update(ready['files']);frozen.update(json.loads((R/'INPUT_SNAPSHOT.json').read_text())['reference_hashes'])
    dump(R/'REGISTRATION.json',dict(status='FROZEN_BEFORE_METRICS_AND_NEURAL_TRAINING',files=frozen,settings=47,version_cells=94,nominal_model_jobs=len(plan),job_counts={k:sum(p['status']==k for p in plan) for k in ['TRAIN','REUSED_PRIOR','REUSED_IDENTICAL']},runtime=dict(torch=torch.__version__,cuda=True,gpu=torch.cuda.get_device_name(0)),new_ZL_models=0,C16_holds='UNCHANGED'))
    print(json.dumps(json.loads((R/'REGISTRATION.json').read_text())['job_counts']))
if __name__=='__main__':main()
