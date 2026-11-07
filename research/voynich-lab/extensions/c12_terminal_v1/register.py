from common import *
from src.train import prepare
P=R.parent/'c12_partial_v1'
def main():
    assert not (R/'REGISTRATION.json').exists()
    ready=json.loads((R/'DATA_READY.json').read_text());assert all(sha(R/p)==h for p,h in ready['files'].items())
    cfg=json.loads((I/'configs/phase4.json').read_text());split=json.loads((I/'configs/page_split.json').read_text());cache={};admitted=[]
    # Prior partial preparation identities already cover every exact .65 endpoint.
    for row in read(P/'DATA_IDENTITIES.csv'):
        for pos in [False,True]:
            for seed in cfg['seeds']:
                f=P/'instrument/runs'/f"{row['setting']}-{row['version']}-p{int(pos)}-s{seed}"/'metrics.json'
                assert f.exists()
                cache[row['tensor_sha256'],pos,seed]=f
    plan=[];owners={};datasets=[]
    for s in settings():
        for version in ['clean','noise']:
            p=prepare('C1_'+version,'T1',cfg,rows=typed(read(R/'data'/s['setting']/f'{version}.csv')),split=split);fp=tensor_fingerprint(p,cfg)
            if s['role']=='comparison':
                name=s['setting']+'_'+version
                for pos in [False,True]:
                    for seed in cfg['seeds']:
                        folder=(LAB/'runs/phase4-de886963575d'/f'{name}-T1-lstm-p{int(pos)}-s{seed}') if s['setting']=='C9' else (R.parent/'prior_work_v1/runs/models'/f'{name}-T1-lstm-p{int(pos)}-s{seed}')
                        if not (folder/'metrics.json').exists():continue
                        spec=json.loads((folder/'config.json').read_text());metric=json.loads((folder/'metrics.json').read_text())
                        assert spec['training']==cfg and spec['page_split']==split and spec['vocabulary']==p['vocabulary'] and spec['architecture']=='lstm' and spec['tokenization']=='T1' and spec['seed']==seed and spec['with_position']==pos
                        assert metric['device']=='cuda' and metric['torch_version']=='2.9.1+cu128'
                        cache[fp,pos,seed]=folder/'metrics.json';admitted.append(dict(source=str((folder/'metrics.json').relative_to(LAB)),sha256=sha(folder/'metrics.json'),config_sha256=sha(folder/'config.json'),tensor_sha256=fp))
            if s['role']=='terminal' and s['aggressiveness']==.65:
                assert all((fp,pos,seed) in cache for pos in [False,True] for seed in cfg['seeds']),'Endpoint identity failure'
            datasets.append(dict(setting=s['setting'],version=version,tensor_sha256=fp,role=s['role']))
            for pos in [False,True]:
                for seed in cfg['seeds']:
                    job=f"{s['setting']}-{version}-p{int(pos)}-s{seed}";key=(fp,pos,seed)
                    if key in cache:status='REUSED_PRIOR';source=os.path.relpath(cache[key],R)
                    elif key in owners:status='REUSED_IDENTICAL';source=owners[key]
                    else:status='TRAIN';source=None;owners[key]=job
                    plan.append(dict(job=job,setting=s['setting'],version=version,with_position=pos,seed=seed,tensor_sha256=fp,status=status,source=source))
            del p
            print('registered identity',s['setting'],version,flush=True)
    dump(R/'JOB_PLAN.json',plan);table(R/'DATA_IDENTITIES.csv',datasets);dump(R/'CACHE_ADMISSION.json',dict(status='IDENTITY_PASS_PENDING_REPLAY',comparator_checks=admitted,partial_registration_sha256=sha(P/'REGISTRATION.json'),partial_replay_sha256=sha(P/'REPLAY_VERIFICATION.json')))
    paths=list(R.glob('*.py'))+[R/'PROTOCOL.md',R/'INPUT_SNAPSHOT.json',R/'JOB_PLAN.json',R/'DATA_IDENTITIES.csv',R/'DATA_MANIFEST.csv',R/'ENGINEERING.json',R/'CACHE_ADMISSION.json',R/'HISTORICAL_SETTINGS.json',R/'SOURCES.md']
    frozen={str(p.relative_to(R)):sha(p) for p in paths};frozen.update(ready['files']);frozen.update(json.loads((R/'INPUT_SNAPSHOT.json').read_text())['reference_hashes'])
    # Freeze all reused results too, including files outside the new extension.
    for j in plan:
        if j['status']=='REUSED_PRIOR':frozen[j['source']]=sha(R/j['source'])
    import torch
    dump(R/'REGISTRATION.json',dict(status='FROZEN_BEFORE_TERMINAL_METRICS_AND_NEURAL_TRAINING',files=frozen,settings=16,terminal_version_cells=32,comparison_version_cells=14,historical_version_cells=26,nominal_model_jobs=len(plan),job_counts={k:sum(j['status']==k for j in plan) for k in ['TRAIN','REUSED_PRIOR','REUSED_IDENTICAL']},torch=torch.__version__,new_ZL_models=0,C16_holds='UNCHANGED',family_terminal=True))
    dump(R/'FAMILY_TERMINAL.json',dict(status='CLOSED_AFTER_THIS_REGISTERED_GRID',no_further_shorthand_family_sweeps=True,registration_sha256=sha(R/'REGISTRATION.json'),exceptions='none; corrections may only restore the registered grid'))
    print(json.dumps(json.loads((R/'REGISTRATION.json').read_text())['job_counts']))
if __name__=='__main__':main()
