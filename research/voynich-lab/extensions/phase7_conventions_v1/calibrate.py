from common import *
import os
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
import importlib.util,multiprocessing as mp
import numpy as np
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits
from features import raw_features
from mixture import analyze
from physical_tests import run as physical_run,leaf_labels,TESTS
def plan():
    jobs=[]
    for family in ['C1','C2']:
        for k,schedule in [(1,'single')]+[(k,s) for k in [2,4] for s in ['bifolio_cycle','quire_block','independent_leaf']]:
            for seed in SEEDS:
                for view in ['clean','noise']:jobs.append(dict(id=f'{family}_K{k}_{schedule}_s{seed}_{view}',family=family,true_k=k,schedule=schedule,seed=seed,view=view))
    assert len(jobs)==140;return jobs
def backend():
    spec=importlib.util.spec_from_file_location('frozen_phase7_backend',OLD/'common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def generate():
    if (R/'CONTROL_DATA_READY.json').exists():return
    be=backend();phy=physical();common=set(json.loads((R/'COMMON_PAGES.json').read_text()));leaves=sorted({leaf(p) for p in common});rates=json.loads((R/'noise_model.json').read_text())['rates'];alltypes=['alpha','beta1','beta2','beta3','gamma1','gamma2'];profiles=[]
    for i,name in enumerate(['alpha','beta1','beta2','gamma1']):profiles.append(dict(id=f'CONTROL_{name}',weights={t:40 if t==name else 1 for t in alltypes},respacing=17))
    dump(R/'CONTROL_PROFILES.json',profiles)
    from src.noise import inject
    alphabet=set(''.join(r['glyphs'] for r in be.read(OLD/'author/naibbe_tables.csv')))
    jobs=plan();by=defaultdict(list)
    for j in jobs:by[j['family'],j['seed']].append(j)
    for (family,seed),js in by.items():
        data={p['id']:be.generated(family,p,seed)[0] for p in profiles};indexed={key:{r['line_id']:r for r in rs} for key,rs in data.items()};template=next(iter(data.values()))
        for j in js:
            k=j['true_k'];schedule=j['schedule'];truth={}
            if schedule=='independent_leaf':
                values=[i%k for i in range(len(leaves))];random.Random(sid(seed,family,k,'leaf_schedule')).shuffle(values);truth=dict(zip(leaves,values))
            else:
                for l in leaves:
                    p=phy[str(l)];truth[l]=(p['sheet_index'] if schedule=='bifolio_cycle' else p['quire_index'] if schedule=='quire_block' else 0)%k
            rows=[];ops=Counter()
            for r in template:
                pg=page(r['folio'])
                if pg not in common:continue
                li=leaf(pg);tid=profiles[truth[li]]['id'];row=indexed[tid][r['line_id']];text=row['text_eva']
                if j['view']=='noise':
                    rng=random.Random(sid(seed,family,k,schedule,r['line_id'],'noise'));text,changes,_=inject(text,rates,alphabet,rng);ops.update(changes)
                rows.append(dict(folio=pg,line_id=r['line_id'],text_eva=text,is_para_start=None))
            folder=R/'controls'/j['id'];table(folder/'text.csv',rows);dump(folder/'truth.json',dict(leaf_labels=truth,noise_operations=dict(ops),job=j))
        print('generated control bank',family,seed,flush=True)
    dump(R/'CONTROL_DATA_READY.json',dict(status='FROZEN_CONTROLS_BEFORE_MIXTURE_FITTING',files={str(p.relative_to(R)):sha(p) for p in (R/'controls').rglob('*') if p.is_file()},jobs=jobs,source='no target text'))
def worker(j):
    folder=R/'calibration'/j['id'];done=folder/'RESULT.json'
    if done.exists():return json.loads(done.read_text())
    with threadpool_limits(limits=1):
        path=folder/'raw_features.json.gz'
        if path.exists():raws=gzread(path)
        else:
            rs=read(R/'controls'/j['id']/'text.csv');raws=[raw_features(p) for p in pages(rs)];gzwrite(path,raws)
        result=analyze(raws,j['seed'],folder)
        # Truth is read only AFTER all k likelihoods and k selection for this dataset.
        truth=json.loads((R/'controls'/j['id']/'truth.json').read_text())['leaf_labels'];truth={int(k):int(v) for k,v in truth.items()};oracle=physical_run(truth,sid(j['seed'],'physical')%(2**32),folder/'ORACLE_PHYSICAL.json')
        if result['status']=='COMPLETE':
            labels=read(folder/'page_labels.csv');ari=float(adjusted_rand_score([truth[int(r['leaf'])] for r in labels],[int(r['cluster']) for r in labels]));observed=physical_run(leaf_labels(labels),sid(j['seed'],'physical')%(2**32),folder/'PHYSICAL.json');recovered=result['best_k']==j['true_k'] and ari>=.8
        else:ari=None;observed=None;recovered=False
        positives=['conjugacy_within_quire','conjugacy_book'] if j['schedule']=='bifolio_cycle' else ['conjugacy_book','coherence_leaf_shuffle','coherence_bifolio_shuffle'] if j['schedule']=='quire_block' else []
        oracle_pass=all(oracle['tests'][key]['Holm_p'] is not None and oracle['tests'][key]['Holm_p']<=.05 for key in positives)
        physical_pass=observed is not None and all(observed['tests'][key]['Holm_p'] is not None and observed['tests'][key]['Holm_p']<=.05 for key in positives)
        record=dict(**j,status=result['status'],selected_k=result.get('best_k'),ARI=ari,recovered_k_and_labels=recovered,expected_positive_tests=positives,oracle_signal_pass=oracle_pass,physical_signal_pass=physical_pass,seed_pass=recovered and physical_pass and oracle_pass,rejections={key:observed['tests'][key]['Holm_p'] is not None and observed['tests'][key]['Holm_p']<=.05 if observed else False for key in TESTS})
        dump(done,record);return record
def main():
    verify();assert not (R/'QUALIFICATION.json').exists();generate();ready=json.loads((R/'CONTROL_DATA_READY.json').read_text());assert all(sha(R/p)==h for p,h in ready['files'].items());results=[]
    with mp.Pool(3) as pool:
        for record in pool.imap_unordered(worker,ready['jobs'],chunksize=1):
            results.append(record);table(R/'CALIBRATION_RESULTS.csv',[{**r,'rejections':json.dumps(r['rejections']),'expected_positive_tests':json.dumps(r['expected_positive_tests'])} for r in results]);dump(R/'PROGRESS.json',dict(stage='CALIBRATION_ONLY',completed=len(results),scheduled=140,target_feature_extraction=False));print('CALIBRATION',len(results),'/140',record['id'],record['status'],record['selected_k'],record['ARI'],flush=True)
    cells=[]
    for family in ['C1','C2']:
        for k,schedule in [(1,'single')]+[(k,s) for k in [2,4] for s in ['bifolio_cycle','quire_block','independent_leaf']]:
            for view in ['clean','noise']:
                rs=[x for x in results if (x['family'],x['true_k'],x['schedule'],x['view'])==(family,k,schedule,view)];assert len(rs)==5
                n=sum(x['seed_pass'] for x in rs);false_counts={key:sum(x['rejections'][key] for x in rs) for key in TESTS};false_ok=schedule!='independent_leaf' or max(false_counts.values())<=1
                cells.append(dict(family=family,true_k=k,schedule=schedule,view=view,passing_seeds=n,required=4,false_rejection_counts=false_counts,cell_pass=n>=4 and false_ok,selected_k_counts=dict(Counter(str(x['selected_k']) for x in rs))))
    passed=all(x['cell_pass'] for x in cells);dump(R/'QUALIFICATION.json',dict(status='PASS' if passed else 'FAIL',cells=cells,datasets=140,registration_sha256=sha(R/'REGISTRATION.json'),target_feature_extraction=False,target_mixture_fits=0,no_target_results_on_failure=True))
    dump(R/'RUN_STATE.json',dict(status='QUALIFIED_PENDING_TARGET_MANIFEST' if passed else 'STOPPED_CALIBRATION_FAILED',Voynich_gate='OPEN_FOR_REGISTERED_RUN' if passed else 'CLOSED',target_features_read=False,manuscript_best_k=None))
    print('QUALIFICATION', 'PASS' if passed else 'FAIL',sum(x['cell_pass'] for x in cells),'/28 cells')
if __name__=='__main__':main()
