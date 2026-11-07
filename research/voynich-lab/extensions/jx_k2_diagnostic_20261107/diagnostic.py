"""Exclusive JX K2 diagnostic, source validation before conditional target scoring."""
import sys
sys.dont_write_bytecode=True
import ast, hashlib, json, random
from pathlib import Path
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent;LAB=HERE.parents[1];WORK=LAB.parent
sys.path.insert(0,str(LAB/'extensions/jx_k123_20261107'))
import run_k123 as old
ID='JX-20261107-K2D-1';MASTER=2026110702
PREVIOUS=LAB/'results/jx/JX-20261107-K123-1'
REG=HERE/'registration';OUT=LAB/'results/jx'/ID
save=old.save;load=old.load;sha=old.sha
def now():return datetime.now(timezone.utc).isoformat()
def event(name,**kw):old.j.event(OUT,name,**kw)
def seed(name):return MASTER+int(hashlib.sha256(name.encode()).hexdigest()[:12],16)

def register():
    assert not OUT.exists();REG.mkdir()
    prior=load(old.REG/'REGISTRATION.json');paths={WORK/p for p in prior['hashes']}
    for p,h in prior['hashes'].items():assert sha(WORK/p)==h,p
    for p,h in load(PREVIOUS/'ARTIFACT_MANIFEST.json')['hashes'].items():assert sha(PREVIOUS/p)==h,p
    paths.update(p for p in PREVIOUS.rglob('*') if p.is_file())
    paths.update(p for p in old.REG.rglob('*') if p.is_file())
    paths.update([HERE/'diagnostic.py',HERE/'EXECUTION.md',HERE/'authority.json',HERE/'test_engineering.py'])
    save(REG/'REGISTRATION.json',dict(id=ID,utc=now(),master_seed=MASTER,python=sys.version,numpy=old.j.np.__version__,
        authority='User authorized adapter-first K2 diagnostic, decomposition conditional on passed prerequisites.',
        exposure='Prior K2 results and primary-source semantics inspected before registration; anticipated adapter issue disclosed.',
        original_input_collation_receipt=None,spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',
        hashes={(p.relative_to(WORK).as_posix() if p.is_relative_to(WORK) else str(p)):sha(p) for p in sorted(paths)}))
    for name in ['diagnostic.py','EXECUTION.md','authority.json','test_engineering.py']:(REG/name).write_bytes((HERE/name).read_bytes())
    print('REGISTERED',ID,'before validation execution or new target scoring',flush=True)

def preservation():
    for p,h in load(REG/'REGISTRATION.json')['hashes'].items():assert sha(WORK/p)==h,p
    assert load(LAB/'results/jx/JX-20261106-P0-1/specificity/STATUS.json')['status']=='PASS'
    assert load(PREVIOUS/'aggregate/K2/STATUS.json')['status']=='FAIL_ROBUSTNESS'

def paragraph_program():
    """Extract original state machine, not a rewritten surrogate to test itself."""
    tree=ast.parse((old.HERE/'run_k123.py').read_text(encoding='utf-8'))
    intake=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='intake')
    outer=next(n for n in intake.body if isinstance(n,ast.For))
    loop=next(n for n in outer.body if isinstance(n,ast.For))
    body=[]
    for n in loop.body:
        body.append(n)
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='previous_p' for t in n.targets):break
    tail=loop.body[-1]
    assert isinstance(tail,ast.If) and 'is_para_end' in ast.unparse(tail)
    for n in body:assert not any(isinstance(x,(ast.Call,ast.Import,ast.ImportFrom)) for x in ast.walk(n))
    a=ast.fix_missing_locations(ast.Module(body=body,type_ignores=[]))
    b=ast.fix_missing_locations(ast.Module(body=[tail],type_ignores=[]))
    return compile(a,'<registered original intake paragraph state>','exec'),compile(b,'<registered original end reset>','exec'),ast.unparse(a)+'\n'+ast.unparse(b)

def execute_fixture(records):
    head,tail,source=paragraph_program()
    env=dict(code='H',current=None,idx=None,para=-1,previous_p=False,TYPES=old.TYPES)
    states=[]
    for r in records:
        env['r']=r;exec(head,{'__builtins__':{}},env)
        states.append(dict(index=env['index'],paragraph_group=env['para'],start=r['locus_code'][0] in '@*',folio=r['folio']))
        exec(tail,{'__builtins__':{}},env)
    return states,source

def mirror(records):
    states=[];current=None;idx=None;para=-1;previous_p=False
    for r in records:
        p=r['locus_code'][1:] in old.TYPES
        if r['folio']!=current:idx=None;current=r['folio'];para=-1;previous_p=False
        if p and r['locus_code'][0] in '@*':idx=0;para+=1
        elif p and idx is not None and previous_p:idx+=1
        else:idx=None
        previous_p=p
        states.append(dict(index=idx,paragraph_group=para,start=r['locus_code'][0] in '@*',folio=r['folio']))
        if r['is_para_end']:idx=None
    return states

def fixtures():
    def r(code,end=False,folio='f1r'):return dict(locus_code=code,is_para_end=end,folio=folio)
    return [
        dict(id='layout_star_is_not_a_certified_paragraph_start',mandatory=True,
            records=[r('@P0'),r('=Pt'),r('*P0')],expected_last=dict(start=False,paragraph_group=0),
            rationale='Author-created single paragraph: title-like same-line item followed by a left-margin next line. A layout locator alone cannot certify a new paragraph.'),
        dict(id='layout_at_is_not_a_certified_paragraph_start',mandatory=True,
            records=[r('@P0'),r('@P0')],expected_last=dict(start=False,paragraph_group=0),
            rationale='Known continuing authored paragraph with second locus of unspecified relative position. @ supplies layout uncertainty, not an explicit paragraph-start marker.'),
        dict(id='explicit_end_followed_by_plus_context_loss',mandatory=False,
            records=[r('@P0',True),r('+P0')],expected_last=dict(index=None,start=False),
            rationale='Characterizes the original conservative exclusion. It is not a requirement to infer or repair a subsequent paragraph start.'),
        dict(id='page_change_does_not_continue_context',mandatory=False,
            records=[r('@P0'),r('+P0',folio='f1v')],expected_last=dict(index=None),
            rationale='Retain unknown context after page transition without an asserted start.'),
    ]

def gate_adapter():
    folder=OUT/'adapter';folder.mkdir()
    authority=load(HERE/'authority.json')
    assert len(authority['sources'])==2
    results=[];engineering=True
    for f in fixtures():
        states,source=execute_fixture(f['records']);agrees=states==mirror(f['records']);engineering &= agrees
        ok=all(states[-1][key]==value for key,value in f['expected_last'].items())
        results.append(dict(**f,actual_states=states,extraction_matches_mirror=agrees,passed=ok))
    (folder/'extracted_original_state_machine.py.txt').write_text(source+'\n',encoding='utf-8')
    save(folder/'fixtures.json',results)
    status='FAIL_VALIDATION_ENGINEERING' if not engineering else ('PASS' if all(r['passed'] for r in results if r['mandatory']) else 'FAIL_ADAPTER_SEMANTICS')
    save(folder/'STATUS.json',dict(status=status,mandatory_pass=sum(r['passed'] for r in results if r['mandatory']),mandatory_total=2,
        source_issue='Publisher beta-conversion warning; not tested by this semantic fixture gate',target_features_scored=False))
    return status

def whole_spans(lines):
    cases=[]
    for run in old.make_runs([l for l in lines['ZL'] if l['split']=='heldout']):
        for i,first in enumerate(run):
            words=[];locs=[]
            for line in run[i:]:
                words+=line['words'];locs.append(line['id'])
                if len(words)>40:break
                if len(words)>=11:
                    cases.append(dict(source=first['id'],source_loci=locs[:],family=first['family'],scribe=first['scribe'],variety=first['variety'],
                        n=len(words),bin=old.RD.binof(len(words)),streams={'ZL':words[:]},words=words[:]))
    return cases

def select_spans(pool,name):
    result=[];r=random.Random(seed(name))
    for b in [3,4]:
        sub=[x for x in pool if x['bin']==b];r.shuffle(sub)
        for i,c in enumerate(sub[:200]):result.append(dict(c,id=f'b{b}-{i:03d}',requested_n=c['n'],length_fallback=False))
    return result

def decomposition():
    """Conditional executable; unreachable after a failed source prerequisite."""
    lines=load(old.PREP/'lines.json');pools=load(old.PREP/'pools.json')
    common=select_spans(pools['reading_complete'],'common-complete-spans');full=select_spans(whole_spans(lines),'full-complete-spans')
    common_ids={l['id'] for l in lines['ZL'] if l['split']=='train'} & {l['id'] for l in lines['H'] if l['split']=='train'}
    matched={reading:[l for l in ls if l['split']!='train' or l['id'] in common_ids] for reading,ls in lines.items()}
    old.MASTER=MASTER;old.j.MASTER=MASTER;old.OUT=OUT
    plans={
        'D-panel':[('full_ZL',full,{'ZL':('ZL','split')},lines),('common_ZL',common,{'ZL':('ZL','split')},lines)],
        'D-training':[('native',common,{'ZL':('ZL','split'),'H':('H','split')},lines),('common_training',common,{'ZL':('ZL','split'),'H':('H','split')},matched)],
        'D-reading':[('ZL',common,{'ZL':('ZL','split')},matched),('H',common,{'H':('H','split')},matched)]}
    results={}
    for chain,cells in plans.items():
        outcomes=[];stopped=False
        for name,cases,streams,data in cells:
            folder=OUT/chain/name
            if stopped:
                folder.mkdir(parents=True);save(folder/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE'));continue
            folder.parent.mkdir(exist_ok=True)
            save(folder.parent/(name+'_source_cases.json'),cases)
            status=old.evaluate(folder,cases,streams,data,'aggregate',ID+'/'+chain+'/'+name)
            outcomes.append(dict(cell=name,status=status));stopped=status!='PASS'
        results[chain]=outcomes
        save(OUT/chain/'STATUS.json',dict(status=outcomes[-1]['status'],cells=outcomes))
    return results

def hold_decomposition(reason):
    for name in ['source_fidelity','D-panel','D-training','D-reading']:
        folder=OUT/name;folder.mkdir();save(folder/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE',dependency=reason,target_features_scored=False))

def run():
    OUT.mkdir();event('RUN_STARTED',registration_sha256=sha(REG/'REGISTRATION.json'))
    try:preservation()
    except Exception as e:
        save(OUT/'STATUS.json',dict(status='FAIL_PRESERVATION',error=repr(e)));raise
    event('G0_PRESERVATION_PASS')
    adapter=gate_adapter();event('G1_ADAPTER_COMPLETE',status=adapter)
    if adapter!='PASS':hold_decomposition(adapter);state='STOP_'+adapter
    else:
        receipt=load(REG/'REGISTRATION.json')['original_input_collation_receipt']
        if receipt is None:
            folder=OUT/'source_fidelity';folder.mkdir();save(folder/'STATUS.json',dict(status='UNSUPPORTED_SOURCE_FIDELITY'))
            for name in ['D-panel','D-training','D-reading']:
                p=OUT/name;p.mkdir();save(p/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE',dependency='UNSUPPORTED_SOURCE_FIDELITY'))
            state='STOP_UNSUPPORTED_SOURCE_FIDELITY'
        else:
            # Any future execution path requires a receipt bound before registration, never late admission.
            registration=load(REG/'REGISTRATION.json')
            assert receipt in registration['hashes']
            fidelity=load(WORK/receipt)
            assert fidelity['status']=='PASS_SOURCE_FIDELITY' and fidelity['unresolved_differences']==0
            assert fidelity['lsi_sha256']==sha(LAB/'data/raw/LSI_ivtff_0d.txt')
            folder=OUT/'source_fidelity';folder.mkdir();save(folder/'STATUS.json',dict(status='PASS',receipt=receipt))
            decomposition();state='DECOMPOSITION_COMPLETE_WITH_GATED_CELLS'
    save(OUT/'STATUS.json',dict(status=state,id=ID,adapter=adapter,prior_K2='FAIL_ROBUSTNESS_UNCHANGED',
        spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',new_manuscript_fits=0,new_manuscript_scores=0))
    fixture_results=load(OUT/'adapter/fixtures.json')
    mandatory_failed=sum(not f['passed'] for f in fixture_results if f['mandatory'])
    (OUT/'report.md').write_text('# JX K2 diagnostic — adapter validation\n\n'+
        f'Registration: {ID}. Result: **{state}**.\n\n'+
        f'The frozen adapter treats layout locators @/* as certified paragraph starts. Mandatory authored semantic fixtures failed: {mandatory_failed}/2. See adapter/fixtures.json for expected/actual states and extraction-versus-mirror checks. No repair was made.\n\n'+
        'Source fidelity and all panel/training/reading decomposition chains are NOT_RUN_UPSTREAM_FAILURE. No new manuscript models or scores were produced. The publisher beta-source warning remains unresolved; it was not tested as a second gate after the first failed.\n\n'+
        'The earlier numerical K1/K2 results and verification remain preserved. Numerical reproducibility did not certify source semantics; the K2 reading-robustness result carries an adapter/source-selection qualification. Its FAIL is unchanged.\n\n'+
        'Spacing interpretation and real-ring scoring remain CLOSED; radial HELD. Any repair/source collation requires a separately registered follow-up, without changing this failed run.\n',encoding='utf-8')
    preservation();event('FINAL_PRESERVATION_PASS')
    save(OUT/'ARTIFACT_MANIFEST.json',dict(id=ID,hashes={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print(state,flush=True)

def verify():
    preservation();m=load(OUT/'ARTIFACT_MANIFEST.json')
    for p,h in m['hashes'].items():assert sha(OUT/p)==h,p
    r=load(REG/'REGISTRATION.json');events=[json.loads(x) for x in (OUT/'events.jsonl').read_text().splitlines()]
    assert r['utc']<events[0]['utc']
    fs=load(OUT/'adapter/fixtures.json');assert all(f['extraction_matches_mirror'] for f in fs)
    assert all(not f['passed'] for f in fs if f['mandatory'])
    assert load(OUT/'adapter/STATUS.json')['status']=='FAIL_ADAPTER_SEMANTICS'
    for chain in ['source_fidelity','D-panel','D-training','D-reading']:
        assert load(OUT/chain/'STATUS.json')['status']=='NOT_RUN_UPSTREAM_FAILURE'
        assert list((OUT/chain).iterdir())==[OUT/chain/'STATUS.json']
    assert not list(OUT.rglob('scores.jsonl')) and not list(OUT.rglob('models.json'))
    save(OUT/'VERIFICATION.json',dict(status='PASS_AUDIT_OF_FAILED_GATE',registered_before_execution=True,
        original_state_machine_matches_independent_mirror=True,mandatory_semantic_failures=2,
        prior_runs_unchanged=True,decomposition_not_run=True,new_manuscript_scores=0,utc=now()))
    print('PASS_AUDIT_OF_FAILED_GATE',flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','run','verify']);a=p.parse_args()
    try:{'register':register,'run':run,'verify':verify}[a.stage]()
    except Exception as e:
        if a.stage=='run' and OUT.exists():save(OUT/'TECHNICAL_FAILURE.json',dict(status='STOP_TECHNICAL_FAILURE',error=repr(e),utc=now()))
        raise
