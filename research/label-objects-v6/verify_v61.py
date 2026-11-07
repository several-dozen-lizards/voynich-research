"""Audit stored results and current closed gates; does not rerun or reseed controls."""
from common import *
from collections import Counter,defaultdict
import numpy as np,zipfile,subprocess,tempfile
import workflow,t1

checks={};freeze=load(ROOT/'FREEZE.json')
assert freeze['tier']=='CLAIM_PROTOCOL_V6_1'
assert all(sha(ROOT/p)==h for p,h in freeze['hashes'].items())
old=ROOT/'history/infrastructure-v6.0';oldfreeze=load(old/'FREEZE.json')
assert all(sha(old/p)==h for p,h in oldfreeze['hashes'].items())
checks['current_claim_seal_and_exact_prior_checkpoint']=True
features=read_csv(ROOT/'FEATURES.csv');inv=read_csv(ROOT/'LABEL-INVENTORY.csv');meta={r['task_id']:r for r in inv}
_,source_rows=source();raw={(r['locus'],r['reading']):r for r in source_rows}
assert len(inv)==1062 and len(features)==1076
assert all(r['page'] not in RESERVED for r in inv)
for r in features:
    words=raw[r['locus'],r['reading']]['words'];eligible=bool(words) and all(words)
    assert (r['eligible']=='True')==eligible
    if eligible:
        w=''.join(words);assert json.loads(r['features'])==feature_dict(w) and r['word_shape_template_class']==shape(w)
pharma=[r for r in features if meta[r['task_id']]['section']=='Recipes']
assert sum(r['reading']=='H' for r in pharma)==230 and sum(r['reading']=='F' for r in pharma)==2
assert sum(r['reading']=='F' and r['eligible']=='True' for r in pharma)==1
checks['source_features_HF_separation_reserved_pages_and_pharma_limit']=True
plan=load(ROOT/'CONTROL-PLAN.json');banks={}
for K in [2,3]:
    for reading in ['H','F']:
        for regime in ['balanced','section']:
            stem=f'BANK-{K}-{reading}-{regime}';path=ROOT/'controls'/(stem+'.npz');receipt=load(path.with_suffix('.json'))
            assert receipt['permutations']==5000 and receipt['output_sha256']==sha(path)
            data=np.load(path);assert all(len(data[k])==5001 and np.isfinite(data[k]).all() for k in data.files)
            banks[K,reading,regime]=data['gain'][1:]
checks['eight_complete_5000_permutation_banks']=True
records=load(ROOT/'controls/TRIALS.json');assert len(records)==1200
by=defaultdict(list)
for r in records:
    regime='balanced' if r['regime']=='positive' else 'section';null=banks[r['classes'],r['reading'],regime]
    p=(1+sum(null>=r['gain']-1e-12))/5001
    assert abs(p-r['p_raw'])<1e-14
    counts=Counter(r['truth']);assert min(counts.values())>=30
    perpage=12 if r['classes']==2 else 15
    for k in range(r['classes']):assert sum(k in r['truth'][i:i+perpage] for i in range(0,len(r['truth']),perpage))>=6
    by[r['classes'],r['regime'],r['reading'],r['trial']].append(r)
for rr in by.values():
    ordered=sorted(rr,key=lambda r:r['p_raw']);prior=0
    for j,r in enumerate(ordered):
        prior=max(prior,min(1.,(len(rr)-j)*r['p_raw']))
        assert abs(prior-r['p_holm'])<1e-14 and r['passed']==(prior<=.05 and r['gain']>0)
flags={(K,reading):sum(any(r['passed'] for r in by[K,'section_only',reading,t]) for t in range(100)) for K in [2,3] for reading in ['H','F']}
assert flags=={(2,'H'):6,(2,'F'):7,(3,'H'):5,(3,'F'):5}
assert all(any(r['passed'] for r in by[K,'positive',reading,t]) for K in [2,3] for reading in ['H','F'] for t in range(100))
checks['all_1200_p_values_support_Holm_and_decisions_recomputed']=True
summary=load(ROOT/'controls/SUMMARY.json')
assert summary['status']=='FAIL' and all(r['n']==1 for r in summary['results'] if r['regime']=='page_only')
correction=load(ROOT/'controls/REPORTING-CORRECTION.json')
assert correction['original_sha256']==sha(ROOT/'controls/SUMMARY-generated.json')
assert load(ROOT/'QUALIFICATION.json')['scientific_gate_passed'] is False
checks['qualification_failure_and_page_proof_reporting_correction_preserved']=True
for report in ['registration-pilot/AUDIT.json','registration-pilot-v2/AUDIT.json']:
    assert load(ROOT/report)['accepted']==0
assert all(r['status']!='REGISTERED' and r['bbox'] is None for r in load(ROOT/'LABEL-REGISTRATION.json')['rows'])
assert len(read_csv(ROOT/'DROPPED-LABELS.csv'))==1062
assert all(not read_csv(ROOT/f'RATER-{who}.csv') for who in ['A','B','C'])
assert not read_csv(ROOT/'LABEL-OBJECTS.csv') and not (ROOT/'OUTCOME-JOIN.json').exists()
for call in [workflow.join,t1.run]:
    try:call()
    except ValueError as error:assert 'qualification' in str(error).lower() or 'controls' in str(error).lower()
    else:raise AssertionError('Failed scientific gate allowed execution')
checks['zero_geometry_zero_real_ratings_and_closed_join_inference_gates']=True
for folder in ['registration-pilot','registration-pilot-v2']:
    for path in (ROOT/folder).rglob('request-receipt.json'):
        r=load(path);assert r['message_count']==1 and r['tools_supplied'] is False and r['agent_harness'] is False and r['stateless'] is True
        assert all(token not in r['manual'] for token in ['PL-ROOT','SUN-MOON','ng1:','opener:'])
        assert r['image_sha256']==sha(r['image_path'])
checks['registrar_calls_stateless_source_only_and_pixels_hashed']=True
schedule=read_csv(ROOT/'T2-TEXT-SCHEDULE.csv');assert len(schedule)==37 and all(r['reading']=='H' for r in schedule)
assert len({r['pharma_locus'] for r in schedule})==len({r['pharma_word'] for r in schedule})==37
used=[p for r in schedule for p in [r['herbal_page'],r['distractor_page']]];assert len(used)==len(set(used))
assert sha(ROOT/'T2-TEXT-SCHEDULE.csv')==load(ROOT/'T2-SCHEDULE-FREEZE.json')['schedule_sha256']
checks['T2_schedule_separate_reading_nonreuse_and_seal']=True
with zipfile.ZipFile(ROOT/'human-registration-only.zip') as z:
    assert z.testzip() is None and set(z.namelist())=={'index.html','SOURCE-MANIFEST.json','page-1.jpg','page-2.jpg'}
    manifest=json.loads(z.read('SOURCE-MANIFEST.json'));assert manifest['completed_registrars']==0
    for name,h in manifest['images'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
html=(ROOT/'human-registration/index.html').read_text(encoding='utf-8');js=html.split('<script>',1)[1].split('</script>',1)[0]
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'tool.js';path.write_text(js,encoding='utf-8');subprocess.run(['node','--check',str(path)],check=True,capture_output=True)
    # Execute the actual exported UI coordinate function against known CSS/native scales.
    point=js.split('function point(e){',1)[1].split('\n',1)[0]
    test='let c={width:3000,height:4000,getBoundingClientRect:()=>({left:20,top:40,width:750,height:1000})};function point(e){'+point+'\n'
    test+="if(JSON.stringify(point({clientX:395,clientY:540}))!=='[1500,2000]')throw Error('native scale');if(JSON.stringify(point({clientX:-5,clientY:5000}))!=='[0,4000]')throw Error('bounds');"
    path.write_text(test,encoding='utf-8');subprocess.run(['node',str(path)],check=True,capture_output=True)
checks['clean_human_zip_native_hashes_JS_syntax_and_coordinate_execution']=True
save(ROOT/'VERIFICATION.json',dict(status='PASS_REPRODUCIBILITY_AND_BOUNDARIES',checks=checks,
    scientific_qualification='FAIL',no_manuscript_claim_test=True,accepted_label_geometry=0,real_raters=0,
    human_UI_visual_review='NOT_PERFORMED',note='Audit pass does not override any failed qualification or missing independent observation.'))
print(json.dumps(load(ROOT/'VERIFICATION.json'),indent=2))
