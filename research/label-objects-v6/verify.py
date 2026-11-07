"""Independent engineering checks. Synthetic fixtures never enter scientific files."""
from common import *
from collections import Counter
import math
import numpy as np
import workflow, t1

def rejected(call):
    try: call()
    except (ValueError,RuntimeError): return True
    raise AssertionError('Invalid input accepted')

def main():
    checks={}
    inventory=read_csv(ROOT/'LABEL-INVENTORY.csv');features=read_csv(ROOT/'FEATURES.csv')
    units,raw=source()
    selected={r['unit'] for r in read_csv(ROOT/'UNIT-TYPE-AUDIT.csv') if r['status']=='INCLUDE' and r['reserved']=='False'}
    expected={(r['locus'],r['reading']):r for r in raw if r['unit'] in selected and r['reading'] in ['H','F']}
    assert set(expected)=={(r['locus'],r['reading']) for r in features}
    assert len(inventory)==len({r['locus'] for r in inventory})==len({r['task_id'] for r in inventory})
    assert all(r['page'] not in RESERVED for r in inventory)
    assert all(not r['code'].startswith('P') for r in inventory)
    checks['source_inventory_reconciled']=True
    assert tokens('qokain.chol=')==['qokain','chol']
    assert tokens('qokain,chol=')==[None,None]
    assert tokens('qok!ain.chol=')==['qokain','chol']
    assert tokens('qok***.chol=')==[None,'chol']
    assert tokens('olrodar={was <f102v2.P.2;F>}')==['olrodar']
    assert tokens('chol,')==[None]
    checks['uncertainty_and_padding_fixtures']=6
    for r in features:
        words=expected[r['locus'],r['reading']]['words']
        assert (r['eligible']=='True')==(bool(words) and all(words))
        if r['eligible']=='True': assert json.loads(r['features'])==feature_dict(''.join(words))
    checks['all_feature_rows_recomputed']=len(features)
    assert kappa(['a','a','b','b'],['a','a','b','b'])==1
    assert kappa(['a','a','b','b'],['b','b','a','a'])==-1
    assert kappa(['a'],['a']) is None and kappa([],[]) is None
    checks['agreement_oracles']=4
    good=dict(task_id='T',**{'class':'STAR'},rater_id='R',family='FAMILY_A',response_sha256='engineering-fixture')
    assert workflow.validate_votes([good],{'T'})['T']['class']=='STAR'
    checks['vote_rejections']=[rejected(lambda: workflow.validate_votes(rows,{'T'})) for rows in
        [[],[good,good],[dict(good,task_id='BAD')],[dict(good,**{'class':'GUESS'})],[dict(good,rater_id='')]]]
    assert workflow.box_ok([1,2,3,4],20,20)
    for bad in [[-1,0,3,4],[0,0,0,4],[0,0,21,4],[0,0,float('nan'),4],[True,0,1,1]]:
        assert not workflow.box_ok(bad,20,20)
    checks['native_geometry_boundary_rejections']=5
    from build import distance_one
    assert distance_one('abcde','abcde') and distance_one('abcde','abxde') and distance_one('abcde','abcdef')
    assert not distance_one('abcde','axcxe') and not distance_one('abcde','abc')
    pairs=read_csv(ROOT/'T2-MATCHED-PAIRS.csv')
    for p in pairs:
        if p['match']=='EXACT': assert p['pharma_word']==p['herbal_word']
        else: assert min(len(p['pharma_word']),len(p['herbal_word']))>=5 and distance_one(p['pharma_word'],p['herbal_word'])
    checks['all_T2_match_rules_recomputed']=len(pairs)
    # Positive transfer: lexical feature generalises to unseen physical folios.
    groups=np.repeat([f'f{i}' for i in range(1,13)],8)
    pages=groups.tolist(); y=np.tile(['A','B']*4,12)
    X=[{'signal:'+v:1,'page:'+g:1,'length':5} for v,g in zip(y,groups)]
    positive=t1.evaluate(X,y,groups,pages)
    assert positive['gain']>0 and positive['balanced_accuracy']==1
    checks['nested_CV_positive_fixture']={k:v for k,v in positive.items() if k!='tuning'}
    # Page-only fixture: page mix almost determines class, but no lexical transfer.
    ypage=np.repeat(['A','B']*6,8)
    Xpage=[{'page:'+g:1,'constant':1} for g in groups]
    page_result=t1.evaluate(Xpage,ypage,groups,pages)
    assert page_result['gain']<0
    for seed in range(20):
        perm=t1.permute(ypage,pages,np.random.default_rng(seed));assert np.array_equal(perm,ypage)
    checks['page_only_null_fixture']={k:v for k,v in page_result.items() if k!='tuning'}
    for train,test in t1.folds(groups,5): assert not set(groups[train])&set(groups[test])
    assert np.allclose(t1.holm([.01,.04,.03]),[.03,.06,.06])
    baseline=t1.page_prior(np.array(['A','B']),['p','p'],np.array(['A','B']))
    assert np.allclose(baseline,[[.25,.75],[.75,.25]])
    checks['physical_folio_isolation_holm_peer_baseline']=True
    reg=load(ROOT/'LABEL-REGISTRATION.json')
    assert all(r['status']!='REGISTERED' and r['bbox'] is None for r in reg['rows'])
    assert all(not read_csv(ROOT/f'RATER-{r}.csv') for r in ['A','B','C'])
    assert not read_csv(ROOT/'LABEL-OBJECTS.csv')
    assert not (ROOT/'OUTCOME-JOIN.json').exists()
    assert load(ROOT/'PROTOCOL.json')['claim_freeze_status']=='INCOMPLETE'
    assert rejected(workflow.join) and rejected(t1.run)
    checks['missing_data_not_fabricated_and_claim_gates_closed']=True
    locators=load(ROOT/'registrar-only/LOCI.json')
    allowed={'task_id','locus','page','unit','line','status','reading_presence'}
    assert all(set(r)==allowed for r in locators)
    assert all(r['page'] not in RESERVED for r in load(ROOT/'registrar-only/PAGES.json'))
    manifest=load(ROOT/'SOURCE-MANIFEST.json')
    assert all(sha(p)==h for p,h in manifest['sources'].items())
    assert all(sha(ROOT/p)==h for p,h in load(ROOT/'FREEZE.json')['hashes'].items())
    checks['source_hashes_infrastructure_seal_and_registrar_allowlist']=True
    result=dict(status='PASS_ENGINEERING_ONLY',checks=checks,
        scientific_controls_qualified=False,independent_registrar_completed=False,raters_completed=0,
        manuscript_inference_run=False,claim_freeze_completed=False,
        warning='Two deterministic fixtures are software checks, not measured power or a false-positive study.')
    save(ROOT/'VERIFICATION.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
