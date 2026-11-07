"""Registered resumable HMM experiment. No manuscript reader or target stage."""
import os,sys,time,math,itertools,json,hashlib,traceback
from datetime import datetime,timezone
from pathlib import Path
import hmm as h
import data as d
from numba import set_num_threads
np=h.np
HERE=d.HERE
KEYS=['h1','h2','ratio','slope']

def cfg(): return d.read(HERE/'config.json')
def stamp(): return datetime.now(timezone.utc).isoformat()
def hashes(root):
    return {str(f.relative_to(d.p.ROOT)):d.p.sha(f) for f in sorted(root.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
def scientific(): return {**hashes(d.OLD),**hashes(d.AMEND)}
def four_band(source):
    x=np.array([[r['metrics'][k] for k in KEYS] for r in source['natural_rows']])
    mean=x.mean(axis=0); sd=x.std(axis=0); sd[sd==0]=1
    z=(x-mean)/sd; inverse=np.linalg.inv(.95*(z.T@z/len(x))+.05*np.eye(4))
    distances=np.einsum('ij,jk,ik->i',z,inverse,z); threshold=float(np.quantile(distances,.95,method='higher'))
    return dict(keys=KEYS,mean=mean.tolist(),sd=sd.tolist(),inverse=inverse.tolist(),threshold=threshold,
                self_coverage=float(np.mean(distances<=threshold)),distances=distances.tolist(),
                source='Phase11a same tokenizer post-merge natural vectors; inventory removed',source_vectors=source['natural_rows'])

def register():
    assert not(HERE/'REGISTRATION.json').exists()
    d.a.verify()
    prior=d.read(d.AMEND/'QUALIFICATION.json')
    c7=next(r for r in prior['negatives'] if r['family']=='C7')
    assert c7['hits']==20
    d.dump(HERE/'RECLASSIFICATION.json',dict(declared=True,refits=0,C7='meaningful C1 Latin through a verbose fixed cipher; supplemental positive',
         phase11a_band_successes=20,replicates=20,letter_recovery_claim=False,
         negatives=cfg()['negative_families'],original_labels_preserved=True,
         evidence={str(f.relative_to(d.p.ROOT)):d.p.sha(f) for f in [d.p.ROOT/'src/encoders/__init__.py',d.p.ROOT/'data/controls/C7/metadata.json',d.AMEND/'QUALIFICATION.json']}))
    oldband=d.read(d.AMEND/'BAND.json')
    d.dump(HERE/'BAND.json',dict(regions={m:four_band(oldband['regions'][m]['post']) for m in cfg()['tokenizers']},
         before_hmm_fitting=True,phase11a_band_sha256=d.p.sha(d.AMEND/'BAND.json')))
    import numba,llvmlite
    source=[f for f in HERE.iterdir() if f.suffix in ['.py','.md','.json'] and f.name!='REGISTRATION.json']
    d.dump(HERE/'REGISTRATION.json',dict(phase='11b',status='REGISTERED_BEFORE_HMM_CONTROL_FITS',time=stamp(),
         config=cfg(),files={str(f.relative_to(d.p.ROOT)):d.p.sha(f) for f in source},prior_scientific_files=scientific(),
         environment=dict(python=sys.version,numpy=np.__version__,numba=numba.__version__,llvmlite=llvmlite.__version__),
         restart_fits=408000,primary_curve_fits=288000,tokenizer_refits=0,voynich='CLOSED',secondary='CLOSED'))
    print('REGISTERED:408000 restart fits; target CLOSED',flush=True)

def verify():
    reg=d.read(HERE/'REGISTRATION.json')
    import numba,llvmlite
    assert reg['environment']==dict(python=sys.version,numpy=np.__version__,numba=numba.__version__,llvmlite=llvmlite.__version__)
    for f,sha in {**reg['files'],**reg['prior_scientific_files']}.items():
        assert d.p.sha(d.p.ROOT/f)==sha, f
    assert scientific()==reg['prior_scientific_files']
    assert reg['config']==cfg()
    return reg

def jobs():
    c=cfg(); result=[]
    for frac in c['fractions']:
        for code,deck,seed,method,alg in itertools.product(['C1','C2'],[52,78],c['seeds'],c['tokenizers'],c['algorithms']):
            result.append(dict(kind='naibbe',code=code,deck=deck,seed=seed,method=method,algorithm=alg,fraction=frac))
    for code in ['C7']+c['negative_families']:
        for seed,method,alg in itertools.product(c['seeds'],c['tokenizers'],c['algorithms']):
            result.append(dict(kind='c7' if code=='C7' else 'negative',code=code,deck=None,seed=seed,method=method,algorithm=alg,fraction=1.))
    return result

def key(job,algorithm=True):
    return '-'.join(str(job[k]) for k in ['kind','code','deck','seed','method','fraction']+(['algorithm'] if algorithm else []))

def save_npz(path,**arrays):
    tmp=path.with_suffix('.tmp')
    with tmp.open('wb') as f: np.savez_compressed(f,**arrays)
    tmp.replace(path)

def get_data(job):
    stem=HERE/'datasets'/key(job,False); path=stem.with_suffix(stem.suffix+'.npz'); meta_path=Path(str(stem)+'.json')
    if path.exists() and meta_path.exists():
        meta=d.read(meta_path); assert meta['arrays_sha256']==d.p.sha(path)
        with np.load(path) as z: arrays={k:z[k] for k in z.files}
    else:
        streams,oracle,meta=d.dataset(job['kind'],job['code'],job['deck'],job['seed'],job['method'],job['fraction'])
        arrays={}
        for role,(x,start) in streams.items(): arrays[role+'_x']=x; arrays[role+'_start']=start
        for role,truth in oracle.items():
            for name,value in truth.items(): arrays[role+'_oracle_'+name]=value
        save_npz(path,**arrays); meta['arrays_sha256']=d.p.sha(path); d.dump(meta_path,meta)
    return arrays,meta

def band_score(metrics,method):
    b=d.read(HERE/'BAND.json')['regions'][method]
    if not metrics['valid']: return dict(distance=None,inside=False)
    z=(np.array([metrics[k] for k in KEYS])-np.array(b['mean']))/np.array(b['sd'])
    distance=float(z@np.array(b['inverse'])@z)
    return dict(distance=distance,threshold=b['threshold'],inside=distance<=b['threshold'])

def safe_trace(array):
    return [[float(v) if np.isfinite(v) else None for v in row] for row in array]

def run_job(job):
    c=cfg(); jid=key(job); folder=HERE/'models'/jid; folder.mkdir(exist_ok=True)
    arrays,meta=get_data(job); x=arrays['train_x']; start=arrays['train_start']; V=meta['emission_inventory']
    vx=arrays['validation_x']; vs=arrays['validation_start']; ex=arrays['evaluation_x']; es=arrays['evaluation_start']
    summary=[]
    for K in c['K']:
        checkpoint=folder/f'K{K}.json'; model=folder/f'K{K}.npz'
        if checkpoint.exists():
            r=d.read(checkpoint); assert r['model_sha256']==d.p.sha(model); summary.append(r); continue
        seeds=np.array([int(hashlib.sha256(f'{jid}:{K}:{r}'.encode()).hexdigest()[:8],16) for r in range(c['restarts'])],dtype=np.int64)
        began=time.perf_counter()
        pis,As,Bs,lls,steps,traces=h.restarts(x,start,K,V,seeds,0 if job['algorithm']=='EM' else 1,c['em_max_iterations'])
        assert np.all(np.isfinite(lls)), 'Nonfinite restart; no failure conclusion authorized'
        best=int(np.argmax(lls)); pi,A,B=pis[best],As[best],Bs[best]
        validation_ll=float(h.forward(vx,vs,pi,A,B)[2]); assert math.isfinite(validation_ll)
        save_npz(model,pi=pi,A=A,B=B)
        finite_traces=[t[np.isfinite(t)] for t in traces]
        r=dict(job=job,K=K,best_restart=best,training_ll=float(lls[best]),validation_ll=validation_ll,
               restart_training_ll=lls.tolist(),restart_seeds=seeds.tolist(),steps=steps.tolist(),
               iteration_cap=[bool(n==c['em_max_iterations']) for n in steps],
               nonmonotonic_em=[bool(np.any(np.diff(t)<-1.e-7)) if job['algorithm']=='EM' else None for t in finite_traces],
               traces=safe_trace(traces),seconds=time.perf_counter()-began,
               model_sha256=d.p.sha(model),dataset_sha256=meta['arrays_sha256'],
               registration_sha256=d.p.sha(HERE/'REGISTRATION.json'))
        d.dump(checkpoint,r); summary.append(r)
        print('K_DONE',jid,K,'seconds',round(r['seconds'],2),flush=True)
        d.dump(HERE/'STATUS.json',dict(status='RUNNING',time=stamp(),pid=os.getpid(),job=job,last_completed_K=K,
             completed_replicate_branches=len(list((HERE/'results').glob('*.json'))),
             completed_K_fits=len(list((HERE/'models').glob('*/*.json'))),total_replicate_branches=len(jobs()),
             total_K_fits=len(jobs())*15,expected_restart_fits=408000,voynich='CLOSED',secondary='CLOSED'))
    selected=min(summary,key=lambda r:(-r['validation_ll'],r['K'])); K=selected['K']
    with np.load(folder/f'K{K}.npz') as z: pi,A,B=z['pi'],z['A'],z['B']
    z=h.viterbi(ex,es,pi,A,B)
    starts=np.flatnonzero(es); streams=[z[beg:end].tolist() for beg,end in zip(starts,list(starts[1:])+[len(z)])]
    metrics=d.a.continuous(streams); band=band_score(metrics,job['method'])
    baseline=np.bincount(x,minlength=V).astype(float); baseline=np.maximum(baseline,1.e-12); baseline/=baseline.sum()
    baseline_ll=float(np.log(baseline[ex]).sum()); ll=float(h.forward(ex,es,pi,A,B)[2])
    result=dict(job=job,metadata=meta,selected_K=K,true_alphabet_size=meta['true_alphabet_size'],
         validation_ll=selected['validation_ll'],training_ll=selected['training_ll'],
         evaluation_ll=ll,baseline_K1_ll=baseline_ll,gain_over_K1_nats=ll-baseline_ll,
         gain_over_K1_nats_per_unit=(ll-baseline_ll)/len(ex),metrics=metrics,band=band,
         selected_restart=selected['best_restart'],selected_model_sha256=selected['model_sha256'],
         all_K_selection=[dict(K=r['K'],validation_ll=r['validation_ll'],training_ll=r['training_ll']) for r in summary],
         selected_restart_at_cap=selected['iteration_cap'][selected['best_restart']],
         recovery=None,primary_pass=None,completed=stamp())
    if job['kind']!='negative':
        oracle={name:arrays['evaluation_oracle_'+name] for name in ['unit','instance','true']}
        rec=d.recovery(z,oracle,K); result['recovery']=rec
        result['primary_pass']=rec['many_to_one_accuracy']>=.8 and rec['v_measure']>=.7
    d.dump(HERE/'results'/f'{jid}.json',result)
    print('REPLICATE_DONE',jid,'K',K,'recovery',result['recovery'],flush=True)
    return result

def summarize(rows):
    c=cfg(); cells=[]; curves=[]
    for fraction in c['fractions']:
        for method,alg,code,deck in itertools.product(c['tokenizers'],c['algorithms'],['C1','C2'],[52,78]):
            selected=[r for r in rows if r['job']['kind']=='naibbe' and r['job']['fraction']==fraction and r['job']['method']==method and r['job']['algorithm']==alg and r['job']['code']==code and r['job']['deck']==deck]
            n=len(selected); successes=sum(bool(r['primary_pass']) for r in selected)
            cells.append(dict(fraction=fraction,method=method,algorithm=alg,source=code,deck=deck,completed=n,expected=20,successes=successes,
                  status='INCOMPLETE' if n!=20 else 'PASS' if successes>=16 else 'FAIL'))
        eligible=[]
        for method,alg in itertools.product(c['tokenizers'],c['algorithms']):
            relevant=[r for r in cells if r['fraction']==fraction and r['method']==method and r['algorithm']==alg]
            if all(r['status']=='PASS' for r in relevant): eligible.append([method,alg])
        relevant=[r for r in cells if r['fraction']==fraction]
        curves.append(dict(fraction=fraction,status='INCOMPLETE' if any(r['status']=='INCOMPLETE' for r in relevant) else 'PASS' if eligible else 'FAIL',eligible=eligible))
    full=next(r for r in curves if r['fraction']==1.)
    negatives=[]
    for family in c['negative_families']:
        selected=[r for r in rows if r['job']['kind']=='negative' and r['job']['code']==family]
        completed=[s for s in c['seeds'] if sum(r['job']['seed']==s for r in selected)==4]
        hits=sum(any(r['band']['inside'] for r in selected if r['job']['seed']==s) for s in completed)
        negatives.append(dict(family=family,complete_replicates=len(completed),hits=hits,denominator=20,
               numerical_stop_triggered=hits>=4,interpretable=full['status']=='PASS' and len(completed)==20))
    specificity='NOT_INTERPRETABLE_POSITIVE_CALIBRATION_INCOMPLETE' if full['status']=='INCOMPLETE' else 'NOT_INTERPRETABLE_POSITIVE_CALIBRATION_FAILED' if full['status']=='FAIL' else 'INCOMPLETE' if any(r['complete_replicates']!=20 for r in negatives) else 'FAIL' if any(r['numerical_stop_triggered'] for r in negatives) else 'PASS'
    return dict(primary_full_length=full['status'],length_curve=curves,cells=cells,specificity=specificity,negatives=negatives,
         completed_branches=len(rows),expected_branches=1360,restart_fits_required=408000,
         voynich='CLOSED',secondary='CLOSED',
         requested_failure_statement='Naibbe-class homophony is not recoverable language-free at this length by HMM.' if full['status']=='FAIL' else None,
         scope='Finite registered tokenizer/K/inference budgets; not an impossibility theorem; do not interpret unfinished banks as failure.')

def report():
    reg=verify(); rows=[d.read(f) for f in sorted((HERE/'results').glob('*.json'))]
    summary=summarize(rows); d.dump(HERE/'RESULTS_SUMMARY.json',summary)
    lines=['# Phase11b — HMM homophone merge','',f"Primary full-length status: **{summary['primary_full_length']}**. Specificity: **{summary['specificity']}**.",'',
        f"Completed replicate branches: {len(rows)}/1360. Required bank:408,000 restart fits. Every completed branch includes all15 K values and20 restarts per K; these counts are not interchangeable.",'',
        'C7 is reclassified as a meaningful-text verbose cipher and supplemental positive. Its Phase11a20/20 band hits are positive-control band successes, not letter recovery. Earlier artifacts remain unchanged.','',
        'Voynich and two-table secondary remain CLOSED. No letter values, language claims or translation.','',
        '| Length fraction | Primary gate | Eligible branches |','|---|---|---|']
    for r in summary['length_curve']: lines.append(f"| {r['fraction']} | {r['status']} | {r['eligible']} |")
    lines+=['','| Fraction | Tokenizer | Algorithm | Source | Deck | Complete | Recovery successes | Status |','|---|---|---|---|---:|---:|---:|---|']
    for r in summary['cells']: lines.append(f"| {r['fraction']} | {r['method']} | {r['algorithm']} | {r['source']} | {r['deck']} | {r['completed']}/20 | {r['successes']} | {r['status']} |")
    lines+=['','Every results/*.json reports selected K versus true alphabet size, accuracy, V-measure, likelihood gain over K=1, band membership, actual lengths and endpoint flags. models/*/K*.json preserve all restart training likelihoods, traces and K-validation likelihoods. K selection uses validation only; oracle evaluation follows selection.','',
        'Iterations/sweeps are capped at100; Gibbs burn-in50 and thinning10. Short-chain mixing and endpoint convergence are not established by model selection. Length curves retain full-length fitted tokenizers and are conditional on them. Four-coordinate secondary regions project saved Phase11a post-merge natural vectors; these are not newly HMM-fitted natural reference streams.','',
        'See [registration](REGISTRATION.json), [protocol](PROTOCOL.md), [bibliography](SOURCES.md), [reclassification](RECLASSIFICATION.json), [status](STATUS.json), and RESULTS_SUMMARY.json. Bibliography distinguishes language-model-assisted EM/sampling decipherment from this fully learned language-free HMM.','']
    if summary['requested_failure_statement']: lines += [summary['requested_failure_statement'],'','This sentence describes the registered finite experiment, not all possible HMMs or an impossibility proof.']
    (HERE/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    return summary

def run_all():
    verify(); c=cfg(); set_num_threads(c['numba_threads'])
    for name in ['models','results','datasets']: (HERE/name).mkdir(exist_ok=True)
    queue=jobs(); assert len(queue)==1360
    d.dump(HERE/'STATUS.json',dict(status='RUNNING',time=stamp(),pid=os.getpid(),total_branches=1360,total_restart_fits=408000,voynich='CLOSED',secondary='CLOSED'))
    try:
        for job in queue:
            path=HERE/'results'/f'{key(job)}.json'
            if path.exists(): continue
            run_job(job)
            if len(list((HERE/'results').glob('*.json')))%4==0: report()
        summary=report(); verify()
        files=list((HERE/'results').glob('*.json')); checkpoints=list((HERE/'models').glob('*/*.json'))
        assert len(files)==1360 and len(checkpoints)==20400
        for checkpoint in checkpoints:
            r=d.read(checkpoint)
            assert len(r['restart_training_ll'])==20 and r['model_sha256']==d.p.sha(checkpoint.with_suffix('.npz'))
        d.dump(HERE/'VERIFICATION.json',dict(status='PASS',complete_branches=1360,complete_K_searches=20400,restart_fits=408000,
            prior_scientific_files_unchanged=True,tokenizer_refits=0,registration_sha256=d.p.sha(HERE/'REGISTRATION.json'),
            primary_full_length=summary['primary_full_length'],specificity=summary['specificity'],
            selected_result_hashes={f.name:d.p.sha(f) for f in files},voynich='CLOSED',secondary='CLOSED'))
        d.dump(HERE/'STATUS.json',dict(status='COMPLETE',time=stamp(),pid=os.getpid(),completed_branches=1360,
                  primary_full_length=summary['primary_full_length'],specificity=summary['specificity'],voynich='CLOSED',secondary='CLOSED'))
    except BaseException as exc:
        d.dump(HERE/'STATUS.json',dict(status='EXECUTION_ERROR',time=stamp(),pid=os.getpid(),error=repr(exc),traceback=traceback.format_exc(),
                  completed_branches=len(list((HERE/'results').glob('*.json'))),voynich='CLOSED',secondary='CLOSED'))
        raise

if __name__=='__main__': {'register':register,'verify':verify,'run':run_all,'report':report}[sys.argv[1]]()
