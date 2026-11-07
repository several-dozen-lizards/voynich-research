from common import *
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
from alignment import evaluate,nulls
from conjugacy import run as conjugacy
from threadpoolctl import threadpool_limits
import numpy as np,multiprocessing as mp
def worker(job):
    folder=R/'results'/job['id'];done=folder/'RESULT.json'
    if done.exists():return json.loads(done.read_text())
    with threadpool_limits(limits=1):
        rows=read(R/'data'/job['id']/'text.csv');labels=known_labels();seed=job['seed']
        result=dict(**job,status='COMPLETE',active_stage='initialization')
        try:
            if not job['fixture']:
                result['active_stage']='held_out_alignment'
                observed=evaluate(rows,labels,seed,folder/'ALIGNMENT.json');result.update(Q=observed['Q'],Q0=observed['Q0'],D=observed['D'])
                if job['stage']=='qualification':
                    result['active_stage']='refitted_page_nulls'
                    stats=nulls(rows,labels,seed,observed,folder/'PAGE_NULLS.json');result.update(D_null_p=stats['D']['p'],Q_null_p=stats['Q']['p']);clf=json.loads((R/'CLASSIFIER_FROZEN.json').read_text())['classifier'];result['predicted']=predict(clf,result['Q'],result['D']);result['truth_category']=category(job['condition']);result['correct']=result['predicted']==result['truth_category']
            if job['stage']=='qualification':result['active_stage']='within_quire_conjugacy';result['physical']=conjugacy(rows,labels,seed,folder/'WITHIN_QUIRE_CONJUGACY.json')
            result['active_stage']='complete'
        except Exception as e:result.update(status='FAILED',error=repr(e))
        dump(done,result);return result
def predict(clf,Q,D):
    x=(np.array([Q,D])-np.array(clf['mean']))/np.array(clf['sd']);return min(clf['centroids'],key=lambda k:(float(np.sum((x-np.array(clf['centroids'][k]))**2)),k))
def stage(jobs,name):
    out=[]
    with mp.Pool(3) as pool:
        for result in pool.imap_unordered(worker,jobs,chunksize=1):out.append(result);dump(R/f'{name}_PROGRESS.json',dict(completed=len(out),scheduled=len(jobs),target_open=False));print(name,len(out),'/',len(jobs),result['id'],result['status'],flush=True)
    dump(R/f'{name}_RESULTS.json',out);return out
def main():
    verify();assert not (R/'QUALIFICATION.json').exists()
    ready=json.loads((R/'DATA_READY.json').read_text());assert all(sha(R/p)==h for p,h in ready['files'].items());development=stage([j for j in ready['jobs'] if j['stage']=='development'],'DEVELOPMENT')
    if any(x['status']!='COMPLETE' for x in development):
        dump(R/'QUALIFICATION.json',dict(status='FAIL',reason='DEVELOPMENT_SCORE_FAILURE',target_open=False));dump(R/'RUN_STATE.json',dict(status='STOPPED_CALIBRATION_FAILED',Voynich_gate='CLOSED',target_features_read=False));return
    values=np.array([[r['Q'],r['D']] for r in development]);mean=values.mean(0);sd=values.std(0);sd=np.where(sd==0,1.,sd);centroids={label:((np.array([[r['Q'],r['D']] for r in development if category(r['condition'])==label])-mean)/sd).mean(0).tolist() for label in ['ONE_KEY','SAME_TWO_KEYS','DIFFERENT']};clf=dict(mean=mean.tolist(),sd=sd.tolist(),centroids=centroids)
    dump(R/'CLASSIFIER_FROZEN.json',dict(status='FROZEN_BEFORE_QUALIFICATION_SCORING',registration_sha256=sha(R/'REGISTRATION.json'),development_sha256=sha(R/'DEVELOPMENT_RESULTS.json'),classifier=clf,development_predictions=[dict(id=r['id'],truth=category(r['condition']),predicted=predict(clf,r['Q'],r['D'])) for r in development]))
    results=stage([j for j in ready['jobs'] if j['stage']=='qualification'],'QUALIFICATION');cells=[];physical_cells=[]
    for base in ['C1','C2']:
        for orientation in [0,1]:
            for view in ['clean','noise']:
                for condition in ['SAME_ONE','SAME_TWO','DIFF_ONE','DIFF_TWO']:
                    rs=[r for r in results if not r['fixture'] and (r['base'],r['orientation'],r['view'],r['condition'])==(base,orientation,view,condition)];assert len(rs)==5;valid=[r for r in rs if r['status']=='COMPLETE'];correct=sum(r['correct'] for r in valid);false=sum(r['predicted']=='SAME_TWO_KEYS' for r in valid) if condition!='SAME_TWO' else None;dp=sum(r['D_null_p'] is not None and r['D_null_p']<=.05 for r in valid);passed=len(valid)==5 and correct>=4 and (false is None or false<=1) and (condition!='SAME_TWO' or dp>=4) and (condition!='SAME_ONE' or dp<=1)
                    cells.append(dict(base=base,orientation=orientation,view=view,condition=condition,valid=len(valid),correct=correct,false_same_two_keys=false,D_null_positives=dp,cell_pass=passed))
                    if condition in ['SAME_ONE','SAME_TWO']:
                        pos=sum(r['physical']['p'] is not None and r['physical']['p']<=.05 for r in valid);physical_cells.append(dict(base=base,orientation=orientation,view=view,condition=condition,positive_fixture=False,valid=len(valid),positive=pos,cell_pass=len(valid)==5 and pos<=1))
                fixture=[r for r in results if r['fixture'] and (r['base'],r['orientation'],r['view'])==(base,orientation,view)];valid=[r for r in fixture if r['status']=='COMPLETE'];pos=sum(r['physical']['p'] is not None and r['physical']['p']<=.05 for r in valid);physical_cells.append(dict(base=base,orientation=orientation,view=view,condition='CLONED_CONJUGATES',positive_fixture=True,valid=len(valid),positive=pos,cell_pass=len(valid)==5 and pos>=4))
    passed=all(c['cell_pass'] for c in cells+physical_cells);dump(R/'QUALIFICATION.json',dict(status='PASS' if passed else 'FAIL',separation_cells=cells,physical_cells=physical_cells,source_development_qualification_disjoint=True,classifier_freeze_sha256=sha(R/'CLASSIFIER_FROZEN.json'),target_open=False));dump(R/'RUN_STATE.json',dict(status='QUALIFIED_PENDING_TARGET_MANIFEST' if passed else 'STOPPED_CALIBRATION_FAILED',Voynich_gate='OPEN_FOR_REGISTERED_PHASE8_RUN' if passed else 'CLOSED',target_features_read=False,new_retired_physical_tests=0))
    print('PHASE8 QUALIFICATION','PASS' if passed else 'FAIL',sum(c['cell_pass'] for c in cells),'/32 separation cells',sum(c['cell_pass'] for c in physical_cells),'/24 physical cells')
if __name__=='__main__':main()
