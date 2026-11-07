"""Resumable Phase 5 analyses; strict stop after completed report/verification."""
from src.train import *
sys.path.insert(0,str(ROOT/'.analysis-runtime'))
from src.phase4 import config_hash,all_names
from src.probes import read_model_runs
from src.extend_phase3 import read,typed
import argparse

def experiment_path(config,p5):
    return ROOT/'runs'/('phase5-'+config_hash(dict(phase4=config,phase5=p5)))

def label_measurements(experiment,reference,labels_by_name):
    from src.metrics import measure
    p3=json.loads((ROOT/'configs/phase3.json').read_text());bpe=json.loads((ROOT/'configs/control_bpe_extended.json').read_text())
    results=[];scores=[]
    for name,rows in labels_by_name.items():
        for scheme in ['T1','T2','T3']:
            m,_=measure(rows,scheme,p3['clusters'],bpe.get(name.split('_')[0]))
            results.append(dict(corpus=name,tokenization=scheme,role='actual_labels' if not name.startswith('C') else 'matched_pseudo_labels',**m))
        for pos in [False,True]:
            values=read(experiment/f'reference_{name}_p{int(pos)}_labels.csv')
            bits=sum(float(r['bits']) for r in values);characters=sum(float(r['characters']) for r in values)
            scores.append(dict(corpus=name,with_position=pos,words=len(values),characters=characters,
                heldout_lexical_bpc=bits/characters,unknown_tokens=sum(float(r['unknown_tokens']) for r in values),
                context='independent line from BOS; cross-fitted T1 LSTM running-text model'))
    table(ROOT/'report/labels_model_free.csv',results);table(ROOT/'report/labels_model_scores.csv',scores)
    return results,scores

def confirmation(experiment,config,architecture,scheme):
    p5=json.loads((ROOT/'configs/phase5.json').read_text());results=[]
    for name in all_names():
        prepared=prepare(name,scheme,config)
        for pos in [False,True]:
            for seed in p5['dramatic_result_confirmation_seeds']:
                job=experiment/f'confirm-{name}-{scheme}-{architecture}-p{int(pos)}-s{seed}'
                if (job/'metrics.json').exists():r=json.loads((job/'metrics.json').read_text())
                else:
                    model,r=fit(prepared,architecture,pos,seed,config,job);del model
                    print(f'confirmation {job.name} complete',flush=True)
                results.append(r)
    table(ROOT/'report/confirmation_runs.csv',[{k:v for k,v in r.items() if k not in ['curve','currier_test']} for r in results])
    output=[]
    for name in all_names():
        pairs=[]
        for seed in p5['dramatic_result_confirmation_seeds']:
            a=next(r for r in results if r['corpus']==name and r['seed']==seed and not r['with_position'])
            b=next(r for r in results if r['corpus']==name and r['seed']==seed and r['with_position']);pairs.append(a['test_bpt']-b['test_bpt'])
        output.append(dict(corpus=name,architecture=architecture,tokenization=scheme,seeds=5,
            gain_mean=float(np.mean(pairs)),gain_sd=float(np.std(pairs,ddof=1))))
    table(ROOT/'report/confirmation_position_gain.csv',output)
    return output

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-sweeps-only',action='store_true');args=parser.parse_args()
    config=json.loads((ROOT/'configs/phase4.json').read_text());p5=json.loads((ROOT/'configs/phase5.json').read_text())
    experiment=experiment_path(config,p5);experiment.mkdir(exist_ok=True)
    from src.sweep import prepare_sweeps
    if args.prepare_sweeps_only:
        prepare_sweeps(experiment/'sweep');return
    progress=json.loads((ROOT/'report/phase4_progress.json').read_text())
    if progress['status']!='PHASE_4_COMPLETE':raise RuntimeError('Phase 4 matrix incomplete; do not run ahead with partial model comparisons.')
    freeze=[*ROOT.glob('configs/*.json'),*ROOT.glob('src/*.py'),*ROOT.glob('src/encoders/*.py'),ROOT/'DECISIONS.md']
    if not (experiment/'FREEZE.json').exists():dump(experiment/'FREEZE.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in freeze})
    dump(experiment/'config.json',dict(phase4=config,phase5=p5))
    def stage(name):
        dump(ROOT/'report/phase5_progress.json',dict(status='RUNNING',stage=name,experiment=str(experiment)))
        print('PHASE 5: '+name,flush=True)
    from src.fingerprint import full_fingerprint,classify
    stage('control-fitted corpus fingerprints');full_fingerprint()
    from src.surprise import crossfit,actual_labels,pseudo_labels,render_surprise
    stage('five-fold reference scoring, authentic labels and matched control pseudo-labels')
    references={};labels_by_name={};templates=actual_labels()
    for index,name in enumerate(all_names()):
        if name=='ZL_running':labels=templates
        elif name=='LSI_H_running':labels=typed(read(ROOT/'data/voynich/LSI_H_labels.csv'))
        else:labels=pseudo_labels(name,templates)
        labels_by_name[name]=labels
        table(experiment/f'labels_{name}.csv',labels)
        for pos in [False,True]:
            paths=[experiment/f'reference_{name}_p{int(pos)}_{suffix}.csv' for suffix in ['words','lines','labels']]
            if not all(p.exists() for p in paths):
                ws,ls,labs=crossfit(name,'lstm','T1',pos,config,experiment/'crossfit',f'{name}-T1-lstm-p{int(pos)}',labels=labels)
                for path,values in zip(paths,[ws,ls,labs]):table(path,values)
            references[name,pos]=paths[0]
        dump(ROOT/'report/phase5_progress.json',dict(status='RUNNING',stage='reference cross-fitting',completed_corpora=index+1,total_corpora=28,experiment=str(experiment)))
    stage('source-block-held-out classifier and separate A/B queries');classify(references)
    stage('labels versus running-text instruments');label_measurements(experiment,references,labels_by_name)
    stage('validation-selected best Voynich model, folio-cross-fitted surprise map')
    runs=read_model_runs();groups=defaultdict(list)
    for r in runs:
        if r['corpus']=='ZL_running':groups[r['architecture'],r['tokenization'],r['with_position']].append(r)
    best=min(groups,key=lambda k:np.mean([r['validation_bpc_with_escape'] for r in groups[k]]))
    dump(ROOT/'report/best_voynich_model.json',dict(architecture=best[0],tokenization=best[1],with_position=best[2],
        validation_bpc_with_escape=float(np.mean([r['validation_bpc_with_escape'] for r in groups[best]])),selection='validation only; mean over all five seeds'))
    running_ids={r['line_id'] for r in read_rows('ZL_running')};label_ids={r['line_id'] for r in templates}
    other=[{**r,'score_role':'other'} for r in typed(read(ROOT/'data/voynich/ZL_lines_corrected.csv')) if r['line_id'] not in running_ids|label_ids]
    ws,ls,labs=crossfit('ZL_running',best[0],best[1],best[2],config,experiment/'surprise','best-ZL',labels=templates+other,save_tokens=True)
    render_surprise(ws,labs)
    token_rows=[]
    for path in sorted((experiment/'surprise').glob('best-ZL-fold*/*tokens.csv')):token_rows.extend(read(path))
    table(ROOT/'report/best_model_token_surprise.csv',token_rows)
    stage('C4–C6 aggressiveness and C12 length/rigidity sweeps')
    from src.sweep import run as sweep_run
    sweep_run(experiment/'sweep',config)
    stage('held-out metadata probes and T3 embedding geometry')
    from src.probes import run as probe_run,geometry
    probe_run(experiment,config);geometry(config)
    stage('changed-seed confirmation of selected instrument on both transcriptions and EVERY control')
    confirmation(experiment/'confirmation',config,best[0],best[1])
    stage('report and final verification')
    from src.report_phase5 import render
    render(experiment,config,p5)
    from src.verify_phase5 import verify
    verify(experiment)
    dump(ROOT/'report/phase5_progress.json',dict(status='PHASE_5_COMPLETE_STOP',experiment=str(experiment)))
    dump(experiment/'status.json',dict(status='PHASE_5_COMPLETE_STOP'))
    for path in (ROOT/'report').glob('*'):
        if path.is_file() and path.suffix in ['.csv','.json','.md','.png']:(experiment/path.name).write_bytes(path.read_bytes())
    dump(experiment/'OUTPUT_HASHES.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'report').glob('*') if p.is_file()})
    print('PHASE 5 COMPLETE. STOP.',flush=True)

if __name__=='__main__':main()
