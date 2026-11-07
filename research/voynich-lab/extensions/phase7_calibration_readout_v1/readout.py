"""User-requested retrospective readout only. No registration, rescue or target run."""
from pathlib import Path
import sys,os
AUDIT=Path(__file__).resolve().parent;FAILED=AUDIT.parent/'phase7_conventions_v1';MAIN=AUDIT.parent/'phase7_two_table_v1'
sys.dont_write_bytecode=True;sys.path.insert(0,str(FAILED))
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
from common import read,table,dump,sha,gzread,sid,SEEDS
from features import transform
from mixture import model
from physical_tests import run as physical_run,leaf_labels,TESTS
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits
import pickle,json,multiprocessing as mp,statistics
def snapshot():
    return {str(p.resolve()):sha(p) for root in [FAILED,MAIN] for p in root.rglob('*') if p.is_file()}
def negative_readout(rows):
    cells=[];seeds=[]
    for family in ['C1','C2']:
        for k in [2,4]:
            for view in ['clean','noise']:
                rs=sorted([x for x in rows if x['family']==family and int(x['true_k'])==k and x['view']==view and x['schedule']=='independent_leaf'],key=lambda x:int(x['seed']))
                assert len(rs)==5
                for row in rs:
                    ph=json.loads((FAILED/'calibration'/row['id']/'PHYSICAL.json').read_text());rec=dict(dataset=row['id'],family=family,true_k=k,view=view,seed=int(row['seed']),selected_k=int(row['selected_k']))
                    for test in TESTS:
                        item=ph['tests'][test];rejected=item['Holm_p'] is not None and item['Holm_p']<=.05;assert rejected==json.loads(row['rejections'])[test]
                        rec.update({test+'_rejected':rejected,test+'_raw_p':item['p'],test+'_Holm_p':item['Holm_p'],test+'_status':item['status']})
                    seeds.append(rec)
                counts={test:sum(json.loads(x['rejections'])[test] for x in rs) for test in TESTS}
                cells.append(dict(family=family,true_k=k,view=view,selected_k_in_seed_order=','.join(x['selected_k'] for x in rs),**{test+'_positive':v for test,v in counts.items()},cell_pass=all(v<=1 for v in counts.values()),denominator=5))
    table(AUDIT/'independent_leaf_cells.csv',cells);table(AUDIT/'independent_leaf_per_seed.csv',seeds)
    byk=[]
    for k in sorted({x['selected_k'] for x in seeds}):
        ss=[x for x in seeds if x['selected_k']==k];byk.append(dict(selected_k=k,datasets=len(ss),**{test+'_positive':sum(x[test+'_rejected'] for x in ss) for test in TESTS}))
    table(AUDIT/'independent_leaf_by_selected_k.csv',byk)
    return dict(cells=cells,pooled={test:sum(x[test+'_rejected'] for x in seeds) for test in TESTS},datasets=40,gate_pass=all(x['cell_pass'] for x in cells),seed_order=SEEDS)
def fixed_worker(row):
    folder=AUDIT/'fixed_true_k'/row['id'];out=folder/'RESULT.json'
    if out.exists():return json.loads(out.read_text())
    original=FAILED/'calibration'/row['id'];seed=int(row['seed']);k=int(row['true_k'])
    with threadpool_limits(limits=1):
        raw=gzread(original/'raw_features.json.gz')
        with (original/'full_model.pkl').open('rb') as f:basis=pickle.load(f)['basis']
        x,_=transform(raw,basis);m=model(k,seed);m.fit(x)
        if not m.converged_:
            result=dict(dataset=row['id'],family=row['family'],true_k=k,schedule=row['schedule'],view=row['view'],seed=seed,status='NONCONVERGED');dump(out,result);return result
        post=m.predict_proba(x);labels=[dict(page=r['page'],leaf=r['leaf'],cluster=int(p.argmax()),posterior=json.dumps(p.tolist())) for r,p in zip(raw,post)];table(folder/'page_labels.csv',labels)
        ph=physical_run(leaf_labels(labels),sid(seed,'physical')%(2**32),folder/'PHYSICAL.json');truth=json.loads((FAILED/'controls'/row['id']/'truth.json').read_text())['leaf_labels'];ari=float(adjusted_rand_score([truth[str(r['leaf'])] for r in labels],[r['cluster'] for r in labels]))
        original_ph=json.loads((original/'PHYSICAL.json').read_text())
        result=dict(dataset=row['id'],family=row['family'],true_k=k,original_selected_k=int(row['selected_k']),schedule=row['schedule'],view=row['view'],seed=seed,status='COMPLETE',iterations=int(m.n_iter_),ARI=ari,tests=ph['tests'],original_selected_tests=original_ph['tests'],feature_basis_reused_sha256=sha(original/'full_model.pkl'),raw_features_sha256=sha(original/'raw_features.json.gz'))
        with (folder/'fixed_model.pkl').open('wb') as f:pickle.dump(m,f)
        dump(out,result);return result
def main():
    assert json.loads((FAILED/'QUALIFICATION.json').read_text())['status']=='FAIL';assert not (FAILED/'targets').exists()
    snapfile=AUDIT/'PRESERVATION_BEFORE.json'
    if not snapfile.exists():dump(snapfile,snapshot())
    before=json.loads(snapfile.read_text());assert all(Path(p).exists() and sha(Path(p))==h for p,h in before.items())
    dump(AUDIT/'SCOPE.json',dict(type='USER_REQUESTED_RETROSPECTIVE_DIAGNOSTIC_NOT_A_NEW_REGISTERED_DESIGN',original_qualification='FAIL_UNCHANGED',part1='Read existing INFERRED-label physical results at selected k',part2='80 structured-control full fits fixed at their known true k, existing full-data basis/raw features/model hyperparameters/seeds/nulls/Holm rule unchanged',part3='Read saved main Phase7 results',new_controls=False,new_features=False,new_Voynich_analysis=False,original_files_read_only=True,future_design_registration=False))
    rows=read(FAILED/'CALIBRATION_RESULTS.csv');negative=negative_readout(rows);dump(AUDIT/'INDEPENDENT_LEAF_GATE.json',negative)
    jobs=[r for r in rows if r['schedule'] in ['bifolio_cycle','quire_block'] and int(r['true_k']) in [2,4]];assert len(jobs)==80;results=[]
    with mp.Pool(3) as pool:
        for result in pool.imap_unordered(fixed_worker,jobs,chunksize=1):
            results.append(result);dump(AUDIT/'PROGRESS.json',dict(completed=len(results),scheduled=80));print('fixed-k retrospective diagnostic',len(results),'/80',result['dataset'],result['status'],flush=True)
    summary=[]
    for family in ['C1','C2']:
        for k in [2,4]:
            for schedule in ['bifolio_cycle','quire_block']:
                for view in ['clean','noise']:
                    rr=[x for x in results if (x['family'],x['true_k'],x['schedule'],x['view'])==(family,k,schedule,view)];assert len(rr)==5
                    expected=['conjugacy_within_quire','conjugacy_book'] if schedule=='bifolio_cycle' else ['conjugacy_book','coherence_leaf_shuffle','coherence_bifolio_shuffle']
                    row=dict(family=family,true_k=k,schedule=schedule,view=view,denominator=5,converged=sum(x['status']=='COMPLETE' for x in rr),ARI_mean=statistics.mean(x['ARI'] for x in rr if x['status']=='COMPLETE'))
                    for test in TESTS:
                        row[test+'_positive']=sum(x['status']=='COMPLETE' and x['tests'][test]['Holm_p'] is not None and x['tests'][test]['Holm_p']<=.05 for x in rr);row[test+'_invariant']=sum(x['status']=='COMPLETE' and x['tests'][test]['status']=='NULL_INVARIANT' for x in rr)
                    row['all_expected_positive_seeds']=sum(x['status']=='COMPLETE' and all(x['tests'][t]['Holm_p'] is not None and x['tests'][t]['Holm_p']<=.05 for t in expected) for x in rr);summary.append(row)
    table(AUDIT/'fixed_true_k_summary.csv',summary);dump(AUDIT/'FIXED_TRUE_K_RESULTS.json',results)
    table(AUDIT/'main_phase7_probe_summary.csv',read(MAIN/'PROBE_SUMMARY.csv'));dump(AUDIT/'MAIN_PHASE7_STATUS.json',json.loads((MAIN/'STATUS.json').read_text()))
    drift=[p for p,h in before.items() if not Path(p).exists() or sha(Path(p))!=h];new_original=[str(p.resolve()) for root in [FAILED,MAIN] for p in root.rglob('*') if p.is_file() and str(p.resolve()) not in before];assert not drift and not new_original
    dump(AUDIT/'VERIFICATION.json',dict(status='PASS',failed_and_main_phase7_files_checked=len(before),changed_original_files=drift,new_files_inside_original_runs=new_original,negative_control_gate=negative['gate_pass'],new_design_registered=False,diagnostic_fixed_fits=80,converged_fixed_fits=sum(x['status']=='COMPLETE' for x in results),new_controls=False,new_target_analysis=False,original_qualification='FAIL_UNCHANGED'))
    print('DONE',json.dumps(dict(negative_gate=negative['gate_pass'],pooled=negative['pooled'],fixed_fits=80,original_files_unchanged=len(before))))
if __name__=='__main__':main()
