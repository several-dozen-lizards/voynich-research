"""Independent arithmetic, completeness and preservation audit after reporting."""
from common import *
from collections import Counter
import math,statistics
from scipy.stats import wasserstein_distance
def main():
    results=read(R/'sweep_results.csv');ranked=read(R/'ranked_all_cells.csv');models=read(R/'model_runs.csv');plan=json.loads((R/'JOB_PLAN.json').read_text());reg=json.loads((R/'REGISTRATION.json').read_text());snap=json.loads((R/'INPUT_SNAPSHOT.json').read_text())
    drift=[p for p,h in reg['files'].items() if sha(R/p)!=h]
    original_drift=[p for group in ['original_lab_hashes','previous_partial_hashes','comparison_source_hashes'] for p,h in snap[group].items() if sha(LAB/p)!=h]
    assert not drift and not original_drift
    assert len(plan)==len(models)==720 and len(results)==72 and len(ranked)==184
    expected={(s['setting'],v,pos,seed) for s in settings() for v in ['clean','noise'] for pos in [False,True] for seed in [1729,1733,1741,1753,1777]}
    actual={(m['setting'],m['version'],m['with_position']=='True',int(m['seed'])) for m in models};assert actual==expected
    assert Counter(r['origin'] for r in ranked)==dict(original=18,partial=94,terminal=32,comparison=14,historical=26)
    ref=json.loads((R/'reference/growth_and_lengths_extended.json').read_text());zh=ref['ZL_running:T1']['word_length_distribution'];xs=[int(k) for k in zh];weights=list(zh.values());checks=[]
    metrics=read(R/'reference/master_metrics_extended.csv');z=next(float(r['h2']) for r in metrics if r['corpus']=='ZL_running' and r['tokenization']=='T1')
    gains=read(R/'reference/line_position_gain.csv');zg=next(float(r['gain_mean']) for r in gains if (r['corpus'],r['tokenization'],r['architecture'])==('ZL_running','T1','lstm'))
    for row in results:
        lengths=Counter(len(w) for line in read(R/'data'/row['setting']/f"{row['version']}.csv") for w in line['text_eva'].split())
        independently=wasserstein_distance(xs,list(lengths),weights,list(lengths.values()));assert math.isclose(independently,float(row['word_length_W1']),rel_tol=1e-12,abs_tol=1e-12)
        ms=[m for m in models if (m['setting'],m['version'])==(row['setting'],row['version'])];values=[]
        for seed in [1729,1733,1741,1753,1777]:values.append(next(float(m['test_bpt']) for m in ms if int(m['seed'])==seed and m['with_position']=='False')-next(float(m['test_bpt']) for m in ms if int(m['seed'])==seed and m['with_position']=='True'))
        assert statistics.mean(values)==float(row['position_gain_mean']) and statistics.stdev(values)==float(row['position_gain_sd'])
        checks.append(dict(setting=row['setting'],version=row['version'],W1_scipy=independently,gain_check='PASS'))
    for key in ['word_length_W1','h2_distance','gain_distance']:
        order=sorted({float(r[key]) for r in ranked})
        assert all(int(r['rank_'+key])==order.index(float(r[key]))+1 for r in ranked)
        sorted_rows=read(R/f'ranked_by_{key}.csv');assert len(sorted_rows)==184 and [float(r[key]) for r in sorted_rows]==sorted(float(r[key]) for r in sorted_rows)
    for row in ranked:
        assert abs(float(row['h2'])-z)==float(row['h2_distance']) and abs(float(row['position_gain_mean'])-zg)==float(row['gain_distance'])
    replay=json.loads((R/'REPLAY_VERIFICATION.json').read_text());assert replay['status']=='PASS' and all(c['exact'] for c in replay['checks'])
    dump(R/'VERIFICATION.json',dict(status='PASS',ranked_rows=184,nominal_jobs=720,complete_job_cross=True,independent_W1_checks=checks,gain_checks=72,dense_rank_checks=3,registration_drift=drift,original_and_previous_partial_drift=original_drift,exact_cache_replays=2,new_ZL_H_C11_scoring=False,family_terminal=True))
    dump(R/'OUTPUT_HASHES.json',{str(p.relative_to(R)):sha(p) for p in R.iterdir() if p.is_file() and p.name!='OUTPUT_HASHES.json'})
    print('PASS: all184 ranked rows;720 jobs; independent W1/gain/rank arithmetic; preserved originals.')
if __name__=='__main__':main()
