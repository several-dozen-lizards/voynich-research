"""Read-only arithmetic/provenance audit. No graph construction, fitting or scoring."""
from common import *

def load(name):
    return json.loads((R/name).read_text(encoding='utf8'))

def close(a,b):
    assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12),(a,b)

def predict(clf,q,d):
    x=[(v-m)/s for v,m,s in zip([q,d],clf['mean'],clf['sd'])]
    return min(clf['centroids'],key=lambda k:(sum((a-b)**2 for a,b in zip(x,clf['centroids'][k])),k))

def main():
    verify();ready=load('DATA_READY.json');reg=load('REGISTRATION.json')
    assert all(sha(R/p)==h for p,h in ready['files'].items())
    assert len(ready['jobs'])==360
    before=load('PRESERVATION_BEFORE.json')
    assert all(Path(p).is_file() and sha(Path(p))==h for p,h in before.items())
    old_roots=[R.parent/n for n in ['phase7_two_table_v1','phase7_conventions_v1','phase7_calibration_readout_v1','c12_partial_v1','c12_terminal_v1']]
    extras=[str(p.resolve()) for root in old_roots for p in root.rglob('*') if p.is_file() and str(p.resolve()) not in before]
    assert not extras,extras
    for job in ready['jobs']:
        truth=load('data/'+job['id']+'/truth.json')
        two=job['condition'].endswith('TWO')
        assert truth['keys_distinct']==two
        assert (truth['A_key']!=truth['B_key'])==two
        assert len(truth['key_token_counts'])==(2 if two else 1)
    dev=load('DEVELOPMENT_RESULTS.json');frozen=load('CLASSIFIER_FROZEN.json');clf=frozen['classifier']
    assert len(dev)==160 and all(r['status']=='COMPLETE' for r in dev)
    assert frozen['registration_sha256']==sha(R/'REGISTRATION.json')
    assert frozen['development_sha256']==sha(R/'DEVELOPMENT_RESULTS.json')
    mean=[statistics.mean(r[k] for r in dev) for k in ['Q','D']]
    sd=[statistics.pstdev(r[k] for r in dev) or 1. for k in ['Q','D']]
    for a,b in zip(mean,clf['mean']):close(a,b)
    for a,b in zip(sd,clf['sd']):close(a,b)
    for label in clf['centroids']:
        chosen=[r for r in dev if category(r['condition'])==label]
        for i,k in enumerate(['Q','D']):close(statistics.mean((r[k]-mean[i])/sd[i] for r in chosen),clf['centroids'][label][i])
    results=load('QUALIFICATION_RESULTS.json');qualification=load('QUALIFICATION.json');state=load('RUN_STATE.json')
    assert len(results)==200 and {r['id'] for r in results}=={j['id'] for j in ready['jobs'] if j['stage']=='qualification'}
    stages=Counter();null_invariant=Counter();optimizer=Counter();confusion=Counter()
    for result in results:
        folder=R/'results'/result['id']
        if result['status']!='COMPLETE':stages[result['active_stage']]+=1
        if (folder/'ALIGNMENT.json').exists():
            aligned=json.loads((folder/'ALIGNMENT.json').read_text())
            close(aligned['Q'],statistics.mean(f['Q'] for f in aligned['folds']))
            close(aligned['D'],statistics.mean(f['D'] for f in aligned['folds']))
            for mapping in aligned['mappings']:
                assert sorted(mapping['permutation'])==list(range(48))
                for receipt in mapping['optimizer']:
                    optimizer['observed_runs']+=1;optimizer['budget_endpoints']+=receipt['budget_endpoint']
        if (folder/'PAGE_NULLS.json').exists():
            null=json.loads((folder/'PAGE_NULLS.json').read_text());assert len(null['null_scores'])==99
            assert len(null['assignments'])==99
            for key in ['Q','D']:
                saved=null['statistics'][key];values=[x[key] for x in null['null_scores']]
                expected=(1+sum(v>=saved['observed'] for v in values))/100 if min(values)!=max(values) else None
                assert expected==saved['p'];null_invariant['page_'+key]+=expected is None
        if (folder/'WITHIN_QUIRE_CONJUGACY.json').exists():
            physical=json.loads((folder/'WITHIN_QUIRE_CONJUGACY.json').read_text());assert len(physical['nulls'])==1999
            values=physical['nulls'];expected=(1+sum(v>=physical['statistic'] for v in values))/2000 if min(values)!=max(values) else None
            assert expected==physical['p'];null_invariant['physical']+=expected is None
        if result['status']=='COMPLETE' and not result['fixture']:
            assert predict(clf,result['Q'],result['D'])==result['predicted']
            assert result['correct']==(result['predicted']==category(result['condition']))
            confusion[result['condition']+' -> '+result['predicted']]+=1
    for cell in qualification['separation_cells']:
        rs=[r for r in results if not r['fixture'] and all(r[k]==cell[k] for k in ['base','orientation','view','condition'])]
        valid=[r for r in rs if r['status']=='COMPLETE'];assert len(rs)==5
        correct=sum(r['correct'] for r in valid);false=sum(r['predicted']=='SAME_TWO_KEYS' for r in valid) if cell['condition']!='SAME_TWO' else None
        dp=sum(r['D_null_p'] is not None and r['D_null_p']<=.05 for r in valid)
        expected=len(valid)==5 and correct>=4 and (false is None or false<=1) and (cell['condition']!='SAME_TWO' or dp>=4) and (cell['condition']!='SAME_ONE' or dp<=1)
        assert (len(valid),correct,false,dp,expected)==(cell['valid'],cell['correct'],cell['false_same_two_keys'],cell['D_null_positives'],cell['cell_pass'])
    for cell in qualification['physical_cells']:
        rs=[r for r in results if r['fixture']==cell['positive_fixture'] and all(r[k]==cell[k] for k in ['base','orientation','view']) and (r['fixture'] or r['condition']==cell['condition'])]
        valid=[r for r in rs if r['status']=='COMPLETE'];assert len(rs)==5
        pos=sum(r['physical']['p'] is not None and r['physical']['p']<=.05 for r in valid)
        expected=len(valid)==5 and (pos>=4 if cell['positive_fixture'] else pos<=1)
        assert (len(valid),pos,expected)==(cell['valid'],cell['positive'],cell['cell_pass'])
    passed=all(c['cell_pass'] for c in qualification['separation_cells']+qualification['physical_cells'])
    assert qualification['status']==('PASS' if passed else 'FAIL')
    if not passed:
        assert state['Voynich_gate']=='CLOSED' and not state['target_features_read']
        assert not (R/'targets').exists() and not (R/'TARGET_MANIFEST.json').exists()
    result=dict(status='PASS',scope='Read-only receipt arithmetic; no new fits or scoring',registration_sha256=sha(R/'REGISTRATION.json'),classifier_sha256=sha(R/'CLASSIFIER_FROZEN.json'),qualification_sha256=sha(R/'QUALIFICATION.json'),preserved_files=len(before),extra_files_in_prior_runs=extras,data_hashes_checked=len(ready['files']),score_failure_stages=dict(stages),null_invariant=dict(null_invariant),observed_alignment_optimizer=dict(optimizer),qualification_confusion=dict(confusion),gate_recomputed=qualification['status'],target_closed_on_failure=not passed)
    dump(R/'INDEPENDENT_AUDIT.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
