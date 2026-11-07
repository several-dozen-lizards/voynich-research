"""Resumable full 5-seed x architecture x position x tokenization model matrix."""
from src.train import *
import argparse,statistics

def config_hash(config):return hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:12]

def all_names():
    return ['ZL_running','LSI_H_running']+[f'C{i}_{v}' for i in range(1,14) for v in ['clean','noise']]

def aggregate(results):
    results=list(results)
    for r in results[:]:
        for lang,d in r.get('currier_test',{}).items():
            results.append({**r,'corpus':r['corpus']+'_'+lang,'test_bpt':d['bpt'],
                'test_tokens':d['tokens'],'test_unknown_rate':d['unknown']/d['tokens'],
                'test_bpc_with_escape':d['bpc_with_escape']})
    groups=defaultdict(list)
    for r in results:groups[r['corpus'],r['tokenization'],r['architecture'],r['with_position']].append(r)
    summary=[];gains=[]
    for (corpus,scheme,arch,pos),rs in groups.items():
        summary.append(dict(corpus=corpus,tokenization=scheme,architecture=arch,with_position=pos,seeds=len(rs),
            test_bpt_mean=statistics.mean(r['test_bpt'] for r in rs),
            test_bpt_sd=statistics.stdev(r['test_bpt'] for r in rs) if len(rs)>1 else None,
            validation_bpc_mean=statistics.mean(r['validation_bpc_with_escape'] for r in rs),
            test_bpc_mean=statistics.mean(r['test_bpc_with_escape'] for r in rs),
            unknown_rate_mean=statistics.mean(r['test_unknown_rate'] for r in rs),
            endpoint_selected_fraction=statistics.mean(r['still_improving_at_budget'] for r in rs),
            parameter_count=rs[0]['parameter_count'],effective_epochs_mean=statistics.mean(r['effective_token_epochs'] for r in rs)))
    for corpus,scheme,arch,pos in groups:
        if pos:continue
        baseline={r['seed']:r for r in groups[corpus,scheme,arch,False]}
        positioned={r['seed']:r for r in groups.get((corpus,scheme,arch,True),[])}
        matched=sorted(set(baseline)&set(positioned))
        if not matched:continue
        values=[baseline[s]['test_bpt']-positioned[s]['test_bpt'] for s in matched]
        gains.append(dict(corpus=corpus,tokenization=scheme,architecture=arch,seeds=len(values),
            gain_mean=statistics.mean(values),gain_sd=statistics.stdev(values) if len(values)>1 else None))
    for r in gains:
        z=next((g for g in gains if g['corpus']=='ZL_running' and g['tokenization']==r['tokenization'] and g['architecture']==r['architecture']),None)
        h=next((g for g in gains if g['corpus']=='LSI_H_running' and g['tokenization']==r['tokenization'] and g['architecture']==r['architecture']),None)
        floor=abs(z['gain_mean']-h['gain_mean']) if z and h else None
        r['transcription_gain_sensitivity']=floor
        r['interpretation']='no difference' if abs(r['gain_mean'])<=max(r['gain_sd'] or 0,floor or 0) else 'exceeds descriptive seed/transcription band; not a significance claim'
    table(ROOT/'report/model_summary.csv',summary);table(ROOT/'report/line_position_gain.csv',gains)
    return summary,gains

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--corpus');parser.add_argument('--max-jobs',type=int)
    args=parser.parse_args()
    config=json.loads((ROOT/'configs/phase4.json').read_text())
    if not torch.cuda.is_available():raise RuntimeError('CUDA GPU required for the registered full local matrix; do not silently switch to CPU.')
    experiment=ROOT/'runs'/('phase4-'+config_hash(config));experiment.mkdir(exist_ok=True)
    if not (experiment/'FREEZE.json').exists():
        paths=[*ROOT.glob('configs/*.json'),*ROOT.glob('src/*.py'),*ROOT.glob('src/encoders/*.py'),ROOT/'DECISIONS.md']
        dump(experiment/'FREEZE.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
        dump(experiment/'config.json',config)
    results=[];jobs=0;names=[args.corpus] if args.corpus else all_names()
    total=28*3*2*2*len(config['seeds'])
    for name in names:
        for scheme in ['T1','T2','T3']:
            prepared=None
            for arch in ['lstm','transformer']:
                for pos in [False,True]:
                    for seed in config['seeds']:
                        job=experiment/f'{name}-{scheme}-{arch}-p{int(pos)}-s{seed}'
                        if (job/'metrics.json').exists():
                            results.append(json.loads((job/'metrics.json').read_text()));continue
                        if prepared is None:prepared=prepare(name,scheme,config)
                        try:
                            model,result=fit(prepared,arch,pos,seed,config,job,save_weights=seed==config['seeds'][0])
                            results.append(result);del model
                        except Exception as error:
                            dump(job/'FAILED.json',dict(error=repr(error)))
                            raise
                        jobs+=1
                        completed=len(list(experiment.glob('*/metrics.json')))
                        dump(ROOT/'report/phase4_progress.json',dict(status='RUNNING',completed=completed,total=total,
                            last_job=job.name,last_seconds=result['seconds'],experiment=str(experiment),
                            last_test_bpt=result['test_bpt']))
                        print(f"{completed}/{total} {job.name}: {result['test_bpt']:.4f} bpt, {result['seconds']:.2f}s",flush=True)
                        if args.max_jobs and jobs>=args.max_jobs:return
            del prepared
    # Include receipts from all already completed jobs even for a filtered resume.
    results=[json.loads(p.read_text()) for p in experiment.glob('*/metrics.json')]
    table(ROOT/'report/model_runs.csv',[{k:v for k,v in r.items() if k!='curve'} for r in results])
    summary,gains=aggregate(results)
    status='PHASE_4_COMPLETE' if len(results)==total else 'PHASE_4_PARTIAL'
    dump(ROOT/'report/phase4_progress.json',dict(status=status,completed=len(results),total=total,experiment=str(experiment)))
    dump(experiment/'status.json',dict(status=status,completed=len(results),total=total))

if __name__=='__main__':main()
