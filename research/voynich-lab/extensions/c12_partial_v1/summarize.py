from common import *
from collections import Counter,defaultdict
import statistics,math
def w1(a,b):
    na=sum(a.values());nb=sum(b.values());ca=cb=0.;terms=[]
    for k in range(max(max(a),max(b))+1):ca+=a.get(k,0)/na;cb+=b.get(k,0)/nb;terms.append(abs(ca-cb))
    return math.fsum(terms)
def main():
    progress=json.loads((R/'PROGRESS.json').read_text());assert progress['status']=='COMPLETE'
    free=read(R/'model_free.csv');models=read(R/'model_runs.csv');details=json.loads((R/'growth_and_lengths.json').read_text());ref=json.loads((R/'reference/growth_and_lengths_extended.json').read_text());hist=lambda d:{int(k):v for k,v in d['word_length_distribution'].items()};zh=hist(ref['ZL_running:T1']);hh=hist(ref['LSI_H_running:T1'])
    metrics=read(R/'reference/master_metrics_extended.csv');gains=read(R/'reference/line_position_gain.csv');z=next(r for r in metrics if r['corpus']=='ZL_running' and r['tokenization']=='T1');h=next(r for r in metrics if r['corpus']=='LSI_H_running' and r['tokenization']=='T1');zg=next(r for r in gains if r['corpus']=='ZL_running' and r['tokenization']=='T1' and r['architecture']=='lstm');hg=next(r for r in gains if r['corpus']=='LSI_H_running' and r['tokenization']=='T1' and r['architecture']=='lstm')
    hband=abs(float(z['h2'])-float(h['h2']));lband=w1(zh,hh);gb_trans=abs(float(zg['gain_mean'])-float(hg['gain_mean']));output=[];seedrows=[]
    for f in free:
        rs=[r for r in models if r['setting']==f['setting'] and r['version']==f['version']];ss=[]
        for seed in [1729,1733,1741,1753,1777]:
            a=next(r for r in rs if int(r['seed'])==seed and r['with_position']=='False');b=next(r for r in rs if int(r['seed'])==seed and r['with_position']=='True');gain=float(a['test_bpt'])-float(b['test_bpt']);ss.append(gain);seedrows.append(dict(setting=f['setting'],version=f['version'],seed=seed,baseline_bpt=float(a['test_bpt']),position_bpt=float(b['test_bpt']),gain=gain,baseline_status=a['status'],position_status=b['status']))
        mean=statistics.mean(ss);sd=statistics.stdev(ss);gb=max(gb_trans,sd,float(zg['gain_sd']));ld=w1(zh,hist(details[f['setting']+':'+f['version']]));hd=abs(float(f['h2'])-float(z['h2']));gd=abs(mean-float(zg['gain_mean']))
        output.append(dict(**f,position_gain_mean=mean,position_gain_sd=sd,h2_distance=hd,h2_band=hband,word_length_W1=ld,word_length_band=lband,gain_distance=gd,gain_band=gb,h2_within=hd<=hband,length_within=ld<=lband,gain_within=gd<=gb,all_three_within=hd<=hband and ld<=lband and gd<=gb,tensor_sha256=next(r['tensor_sha256'] for r in rs)))
    table(R/'sweep_results.csv',output);table(R/'position_gains_by_seed.csv',seedrows)
    snapshot=json.loads((R/'INPUT_SNAPSHOT.json').read_text());drift=[p for p,h in snapshot['original_lab_hashes'].items() if sha(LAB/p)!=h];reg=json.loads((R/'REGISTRATION.json').read_text());frozen_drift=[p for p,h in reg['files'].items() if sha(R/p)!=h];assert not frozen_drift
    within=[r for r in output if r['all_three_within']];unique=len({r['tensor_sha256'] for r in output});matchedunique=len({r['tensor_sha256'] for r in within})
    status=dict(status='COMPLETE',settings=47,version_cells=len(output),unique_prepared_inputs=unique,nominal_model_jobs=len(models),job_status_counts=dict(Counter(r['status'] for r in models)),exact_cache_replays=2,all_three_within_nominal=len(within),all_three_within_unique_inputs=matchedunique,original_lab_files_unchanged=not drift,original_lab_drift=drift,frozen_extension_drift=frozen_drift,new_ZL_models_or_scores=0,C16_holds='UNCHANGED',formal_equivalence_test=False,semantic_claims=False)
    dump(R/'STATUS.json',status)
    os.environ['MPLCONFIGDIR']=str(R/'.mplcache');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    colors=dict(paired_zero='#555555',C5_external='#111111',sigla_only='#9c4a83',subset25='#2882a3',subset50='#c48122',subset75='#49884c',full='#a34538');fig,axes=plt.subplots(1,3,figsize=(15,5),layout='constrained')
    for ax,key,label,target,band in zip(axes,['h2','word_length_W1','position_gain_mean'],['h2 (bits/character, spaces included)','Word-length W1 to cached ZL','Position gain (bits/token)'],[float(z['h2']),0,float(zg['gain_mean'])],[hband,lband,max(gb_trans,float(zg['gain_sd']))]):
        for mode,color in colors.items():
            for version,marker in [('clean','o'),('noise','x')]:
                rs=[r for r in output if r['mode']==mode and r['version']==version];x=[float(r['occurrence_fraction']) for r in rs];y=[float(r[key]) for r in rs];ax.scatter(x,y,c=color,marker=marker,s=27,alpha=.8,label=f'{mode} {version}')
        ax.axhline(target,color='black',lw=1);ax.axhspan(max(0,target-band) if key=='word_length_W1' else target-band,target+band,color='gray',alpha=.14);ax.set_xlabel('Fraction of base sign occurrences expanded');ax.set_ylabel(label);ax.grid(alpha=.15)
    axes[0].legend(fontsize=6,ncol=2);fig.suptitle('C12 partial decomposition: fixed grid; overlapping points and aliases retained\nGray = cached transcription sensitivity; gain comparisons also use each control seed SD',fontsize=11);fig.savefig(R/'partial_sweep.png',dpi=160);plt.close(fig)
    rows=['# C12 partial decomposition sweep','',f"Completed {len(output)} nominal clean/noise cells across47 settings, with {unique} unique prepared inputs. {len(within)} nominal cells ({matchedunique} unique inputs) lie inside all three frozen descriptive bands. These are not formal equivalence tests or evidence of a reading.",'','## Design and checks','',
    'Both requested arms ran: sigla-only and nested deterministic25/50/75% sign-type subsets, across L2/3/4 and rigidity0/.5/1. Full C12, paired zero and standalone C5 references are included. All paired arms use the same C12-internal C5 base. Standalone C5 uses its original different RNG and remains a separate reference. Selected types form a disjoint stroke alphabet from retained atomic types, making mixed-width codes prefix-free. Every clean word reverses exactly to its base.','',
    'A pre-metric full-endpoint check caught a missing stroke-alphabet shuffle in the extension. Failed attempt1 is preserved; no metric/neural result used it. The corrected data reproduce all18 full-C12 clean/noise endpoints and both standalone-C5 endpoints. All slot-cardinality, prefix, word-count and expansion-accounting checks passed before metrics and training.','',
    'All original neural measuring code/config/splits were copied and hash-checked. Two exact baseline/position replays admitted old endpoint jobs. The full five-seed T1 LSTM grid uses96 steps with validation-only checkpoint selection. Fixed-budget/continuing-learning limitations remain. Identical tensor inputs are explicitly reused; duplicates such as L2 rigidity0/.5 are not independent repetitions.','',
    '| Job accounting | Count |','|---|---:|']
    for k,v in status['job_status_counts'].items():rows.append(f'| {k} | {v} |')
    rows+=['| Cache-admission training replays, additional | 2 |','','## Results','',
    '| Mode | Version | Nominal cells | h2 within | Length within | Gain within | All three |','|---|---|---:|---:|---:|---:|---:|']
    for mode in colors:
        for version in ['clean','noise']:
            rr=[r for r in output if r['mode']==mode and r['version']==version];rows.append(f"| {mode} | {version} | {len(rr)} | {sum(r['h2_within'] for r in rr)} | {sum(r['length_within'] for r in rr)} | {sum(r['gain_within'] for r in rr)} | {sum(r['all_three_within'] for r in rr)} |")
    rows+=['','![Partial decomposition grid](partial_sweep.png)','','Type fractions are not occurrence fractions. Exact selected counts, occurrence fractions, source/expanded character sizes, actual noise sizes, all h0/h1/h2 metrics, W1 distances, five seed gains and per-cell bands are in sweep_results.csv and position_gains_by_seed.csv. The old full-decomposition limitation is tested explicitly here; a negative result would concern this fixed codebook family/grid, not partial decomposition generally.','',
    '### Cells within all three descriptive bands','', '| Setting | Mode | Version | L | Rigidity | Types fraction | Occurrences fraction | h2 | W1 | Gain mean ± SD |','|---|---|---|---:|---:|---:|---:|---:|---:|---|']
    for r in within:rows.append(f"| {r['setting']} | {r['mode']} | {r['version']} | {r['sequence_length']} | {r['slot_rigidity']} | {float(r['type_fraction']):.1%} | {float(r['occurrence_fraction']):.1%} | {float(r['h2']):.4f} | {r['word_length_W1']:.4f} | {r['position_gain_mean']:.4f} ± {r['position_gain_sd']:.4f} |")
    if not within:rows+=['','None.']
    rows+=['','## Limits and preservation','',
    'Bands reuse only cached ZL/H measurements and histograms. No new ZL, H or actual C11 scoring/training occurred; C16-KH holds remain unchanged. h2 and length bands are empirical transcription sensitivity, and gain bands widen by the larger primary/control seed SD; none is a formal equivalence margin. One fixed encoder seed was used, and five neural seeds measure only model variation. Generated controls share C1 ancestry and borrowed layout. Partial codebooks are synthetic and do not identify a historical abbreviation system. No interpolation, parameter rescue, model selection on test, alpha spending or semantic/translation claim.','',f"Original lab source/config/report/C5/C12 byte snapshot unchanged: {not drift}. Concurrent/shared drift if any: {drift}. Registered extension drift: {frozen_drift}.",'',
    'Key artifacts: PROTOCOL.md, REGISTRATION.json, ENGINEERING.json, REPLAY_VERIFICATION.json, JOB_PLAN.json, DATA_MANIFEST.csv, DATA_IDENTITIES.csv, model_free.csv, model_runs.csv, sweep_results.csv, position_gains_by_seed.csv and full encoder/noise receipts. Code and data from the failed preflight are retained separately.']
    (R/'REPORT.md').write_text('\n'.join(rows)+'\n',encoding='utf8');print(json.dumps(status,indent=2))
if __name__=='__main__':main()
