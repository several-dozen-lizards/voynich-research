from common import *
from summarize import w1
from collections import Counter
import statistics
def main():
    assert json.loads((R/'PROGRESS.json').read_text())['status']=='COMPLETE'
    free=read(R/'model_free.csv');models=read(R/'model_runs.csv');details=json.loads((R/'growth_and_lengths.json').read_text());ref=json.loads((R/'reference/growth_and_lengths_extended.json').read_text())
    hist=lambda d:{int(k):v for k,v in d['word_length_distribution'].items()};zh=hist(ref['ZL_running:T1']);hh=hist(ref['LSI_H_running:T1'])
    metrics=read(R/'reference/master_metrics_extended.csv');gains=read(R/'reference/line_position_gain.csv')
    z=next(r for r in metrics if r['corpus']=='ZL_running' and r['tokenization']=='T1');h=next(r for r in metrics if r['corpus']=='LSI_H_running' and r['tokenization']=='T1')
    zg=next(r for r in gains if (r['corpus'],r['tokenization'],r['architecture'])==('ZL_running','T1','lstm'));hg=next(r for r in gains if (r['corpus'],r['tokenization'],r['architecture'])==('LSI_H_running','T1','lstm'))
    hb=abs(float(z['h2'])-float(h['h2']));lb=w1(zh,hh);gb0=abs(float(zg['gain_mean'])-float(hg['gain_mean']));out=[];seedrows=[]
    for f in free:
        rs=[r for r in models if r['setting']==f['setting'] and r['version']==f['version']];ss=[]
        for seed in [1729,1733,1741,1753,1777]:
            a=next(r for r in rs if int(r['seed'])==seed and r['with_position']=='False');b=next(r for r in rs if int(r['seed'])==seed and r['with_position']=='True');gain=float(a['test_bpt'])-float(b['test_bpt']);ss.append(gain)
            seedrows.append(dict(setting=f['setting'],version=f['version'],seed=seed,baseline_bpt=a['test_bpt'],position_bpt=b['test_bpt'],gain=gain,baseline_status=a['status'],position_status=b['status']))
        mean=statistics.mean(ss);sd=statistics.stdev(ss);gb=max(gb0,sd,float(zg['gain_sd']));ld=w1(zh,hist(details[f['setting']+':'+f['version']]));hd=abs(float(f['h2'])-float(z['h2']));gd=abs(mean-float(zg['gain_mean']))
        out.append({**f,'position_gain_mean':mean,'position_gain_sd':sd,'h2_distance':hd,'h2_band':hb,'word_length_W1':ld,'word_length_band':lb,'gain_distance':gd,'gain_band':gb,'h2_within':hd<=hb,'length_within':ld<=lb,'gain_within':gd<=gb,'all_three_within':hd<=hb and ld<=lb and gd<=gb,'tensor_sha256':rs[0]['tensor_sha256']})
    table(R/'sweep_results.csv',out);table(R/'position_gains_by_seed.csv',seedrows)
    ranked=[]
    def add(row,origin,identity,role):
        ranked.append(dict(row_id=origin+':'+identity+':'+row['version'],origin=origin,setting=identity,role=role,version=row['version'],mode=row.get('mode',row.get('encoder','')),aggressiveness=row.get('aggressiveness',.65),sequence_length=row.get('sequence_length',''),slot_rigidity=row.get('slot_rigidity',''),word_length_W1=float(row['word_length_W1']),h2_distance=float(row['h2_distance']),gain_distance=float(row['gain_distance']),h2=float(row['h2']),position_gain_mean=float(row['position_gain_mean']),position_gain_sd=float(row['position_gain_sd'])))
    original=[r for r in read(R/'reference/shorthand_sweep.csv') if r['encoder']=='C12'];assert len(original)==18
    for row in original:add(row,'original',row['setting'],'C12')
    partial=read(R.parent/'c12_partial_v1/sweep_results.csv');assert len(partial)==94
    for row in partial:add(row,'partial',row['setting'],'C5_reference' if row['mode'] in ['paired_zero','C5_external'] else 'C12')
    for row in out:add(row,'terminal' if row['role']=='terminal' else ('historical' if row['role']=='historical' else 'comparison'),row['setting'],'C12' if row['role'] in ['terminal','historical'] else row['setting'].split('_')[0])
    assert len(ranked)==184 and len({r['row_id'] for r in ranked})==184
    for r in ranked:
        r['published_prior_word_length_W1']=r['word_length_W1'] if r['origin']=='original' else ''
        if r['origin']=='original':
            data=typed(read(R/'reference'/r['setting']/f"{r['version']}.csv"));lengths=Counter(len(w) for line in data for w in line['text_eva'].split());r['word_length_W1']=w1(zh,lengths)
        r['h2_distance']=abs(r['h2']-float(z['h2']));r['gain_distance']=abs(r['position_gain_mean']-float(zg['gain_mean']))
        r['word_length_band']=lb;r['h2_band']=hb;r['gain_band']=max(gb0,r['position_gain_sd'],float(zg['gain_sd']))
        r['h2_within']=r['h2_distance']<=hb;r['length_within']=r['word_length_W1']<=lb;r['gain_within']=r['gain_distance']<=r['gain_band'];r['all_three_within']=r['h2_within'] and r['length_within'] and r['gain_within']
    for key in ['word_length_W1','h2_distance','gain_distance']:
        values={v:i+1 for i,v in enumerate(sorted({r[key] for r in ranked}))}
        for row in ranked:row['rank_'+key]=values[row[key]]
    ranked.sort(key=lambda r:(r['word_length_W1'],r['h2_distance'],r['gain_distance'],r['row_id']));table(R/'ranked_all_cells.csv',ranked)
    for key in ['word_length_W1','h2_distance','gain_distance']:table(R/f'ranked_by_{key}.csv',sorted(ranked,key=lambda r:(r[key],r['row_id'])))
    lines=['# All cells: complete distance ranks','', 'Ascending dense ranks; exact ties share rank. Sorted by W1, h2, gain, ID for display; no composite score. Repeated endpoints are aliases, not replications. Same cached ZL target and T1 LSTM96 instrument. Units: characters, bits/character, bits/token respectively.','', '| Cell | W1 (rank) | abs delta h2 (rank) | Gain distance (rank) | All bands |','|---|---:|---:|---:|---|']
    for r in ranked:lines.append(f"| {r['row_id']} | {r['word_length_W1']:.9f} ({r['rank_word_length_W1']}) | {r['h2_distance']:.9f} ({r['rank_h2_distance']}) | {r['gain_distance']:.9f} ({r['rank_gain_distance']}) | {r['all_three_within']} |")
    (R/'RANKED_TABLE.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    snap=json.loads((R/'INPUT_SNAPSHOT.json').read_text());drift=[]
    for section in ['original_lab_hashes','previous_partial_hashes','comparison_source_hashes']:drift += [p for p,hash_ in snap[section].items() if sha(LAB/p)!=hash_]
    reg=json.loads((R/'REGISTRATION.json').read_text());frozen_drift=[p for p,hash_ in reg['files'].items() if sha(R/p)!=hash_];assert not drift and not frozen_drift,(drift,frozen_drift)
    term=[r for r in out if r['role']=='terminal'];counts={key:sum(r[key] for r in term) for key in ['h2_within','length_within','gain_within','all_three_within']}
    status=dict(status='COMPLETE',family_terminal=True,no_further_shorthand_family_sweeps=True,settings=16,terminal_version_cells=32,comparison_version_cells=14,historical_version_cells=26,ranked_rows=len(ranked),coverage=dict(original_C12=18,partial_including_C5_references=94,terminal=32,comparison=14,historical=26),terminal_bands=counts,job_status_counts=dict(Counter(r['status'] for r in models)),nominal_model_jobs=len(models),original_and_partial_drift=drift,frozen_drift=frozen_drift,new_ZL_H_actual_C11_scores_or_models=0,C16_holds='UNCHANGED',formal_equivalence=False,translation_claims=False)
    dump(R/'STATUS.json',status);best=min(term,key=lambda r:r['word_length_W1'])
    rows=['# C12 terminal sweep','',f"Completed16 settings /32 clean-noise cells. All-three descriptive-band matches: {counts['all_three_within']}/32. Length matches: {counts['length_within']}; h2 matches: {counts['h2_within']}; gain matches: {counts['gain_within']}.",'',f"Smallest terminal W1: {best['setting']} {best['version']}, {best['mode']}, aggressiveness {best['aggressiveness']}, rigidity {best['slot_rigidity']}: W1={best['word_length_W1']:.9f}; length band={lb:.9f}.",'','The complete184-row ranked table covers18 original C12 cells,94 prior partial cells including4 C5-reference cells,26 earlier registered mixed-codebook cells,32 terminal cells and14 comparator cells (all C15 Latin/Italian52/78, C9, C18 bigraph2/addB, clean/noise). All three distances and independent dense ranks are in RANKED_TABLE.md and ranked_all_cells.csv; each metric has its own complete sorted CSV. Aliases and repeated endpoints remain visible, not independent replications. Original Phase5 W1 values differ at floating-point roundoff; preserved separately while common histogram arithmetic supplies ranks.','', 'Same fixed96-step T1 LSTM instrument, five seeds, bands, data and noise rules; source/config/tensor identity and exact replays qualify reuse. Seed gains, job accounting, codebooks and hashes retained. No test-driven budget or parameter changes. Fixed-compute fits can still be learning; gain is an instrument reading, not convergence or significance.','',f"Job accounting: {status['job_status_counts']}; two additional cache-admission replay fits.",'','Bands are descriptive transcription/seed sensitivity, not equivalence or language identification. C15 author tables were developed against Voynich statistics; these are not blind controls. C18 is the fully specified table-transform extension, not an exact replication of every source experiment. Controls share ancestry/layout; closeness does not identify historical mechanisms.','', 'Earlier sources/configs/reports/controls and entire prior partial extension remain hash-identical. Only cached ZL/H metrics used; no manuscript text opened and no new ZL/H/actual C11 scoring or models. C16 holds unchanged. No translation claims.','', '**STOP: this shorthand encoder family is terminal. No further family sweeps after this registered grid.**','', 'Artifacts: PROTOCOL.md, REGISTRATION.json, FAMILY_TERMINAL.json, INPUT_SNAPSHOT.json, ENGINEERING.json, CACHE_ADMISSION.json, REPLAY_VERIFICATION.json, JOB_PLAN.json, DATA_MANIFEST.csv, DATA_IDENTITIES.csv, model_runs.csv, sweep_results.csv, position_gains_by_seed.csv, SOURCES.md, VERIFICATION.json.']
    (R/'REPORT.md').write_text('\n'.join(rows)+'\n',encoding='utf8');print(json.dumps(status,indent=2))
if __name__=='__main__':main()
