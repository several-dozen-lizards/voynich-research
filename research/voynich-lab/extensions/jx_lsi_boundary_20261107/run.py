"""Registered adapter/source gates and conditional locus-local boundary census."""
import sys
sys.dont_write_bytecode=True
import csv,gzip,hashlib,json,re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from adapter import adapt,canonical,boundary_comparison
import fixtures

HERE=Path(__file__).resolve().parent;LAB=HERE.parents[1];WORK=LAB.parent
sys.path.insert(0,str(LAB/'src'))
import parse_ivtff as iv
ID='JX-20261107-LSIB-1';SEED=2026110703
REG=HERE/'registration';OUT=LAB/'results/jx'/ID
PREV=LAB/'extensions/jx_k2_diagnostic_20261107/registration/REGISTRATION.json'
PREVOUT=LAB/'results/jx/JX-20261107-K2D-1'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False)
def jsonlines(p,xs):
    with Path(p).open('x',encoding='utf-8') as f:
        for x in xs:f.write(json.dumps(x,ensure_ascii=False)+'\n')
def readlines(p):return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines()]
def event(name,**kw):
    with (OUT/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(event=name,utc=now(),**kw))+'\n')
def family(f):
    if f=='fRos' or re.match(r'^f(?:85|86)[rv]',f):return 'rosettes'
    return re.match(r'^f(\d+)',f)[1]
def stable(s):return int(hashlib.sha256(s.encode()).hexdigest()[:8],16)
def csvrows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def register():
    assert not OUT.exists();REG.mkdir()
    prior=load(PREV)
    paths={WORK/p for p in prior['hashes']}
    for p,h in prior['hashes'].items():assert sha(WORK/p)==h,p
    for p,h in load(PREVOUT/'ARTIFACT_MANIFEST.json')['hashes'].items():assert sha(PREVOUT/p)==h,p
    paths.update(p for p in PREVOUT.rglob('*') if p.is_file())
    paths.update([PREV,LAB/'src/parse_ivtff.py'])
    paths.update(p for p in HERE.rglob('*') if p.is_file() and 'registration' not in p.relative_to(HERE).parts)
    save(REG/'REGISTRATION.json',dict(id=ID,utc=now(),seed=SEED,python=sys.version,authority='User authorized corrected LSI adapter, adapter/source gates, conditional descriptive boundary diagnostic.',
        prior_exposure='Prior outcomes and source syntax inspected; no source collation or boundary outcome before registration.',
        gates=['G0 preservation','G1 adapter and synthetic instrument fixtures','G2 original-source fidelity','G3 conditional boundary census'],
        hashes={(p.relative_to(WORK).as_posix() if p.is_relative_to(WORK) else str(p)):sha(p) for p in sorted(paths)},
        spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',PDF_used=False))
    for n in ['adapter.py','fixtures.py','run.py','EXECUTION.md','authority.json','test_syntax.py']:
        with (REG/n).open('xb') as f:f.write((HERE/n).read_bytes())
    print('REGISTERED',ID,'before gate execution',flush=True)

def preservation():
    for p,h in load(REG/'REGISTRATION.json')['hashes'].items():assert sha(WORK/p)==h,p
    assert load(PREVOUT/'STATUS.json')['status']=='STOP_FAIL_ADAPTER_SEMANTICS'
    assert load(LAB/'results/jx/JX-20261107-K123-1/aggregate/K2/STATUS.json')['status']=='FAIL_ROBUSTNESS'

def original_records():
    raw=(HERE/'sources/text16e6.evt').read_bytes()
    assert gzip.decompress((HERE/'sources/text16e6.evt.gz').read_bytes())==raw
    text=raw.decode('latin-1');assert 'Release 1.6e6' in text[:1200]
    pattern=re.compile(r'^<(?P<folio>f[^.>]+)\.(?P<unit>[^.>]+)\.(?P<num>\d+[a-z]?);(?P<reader>[^>]+)>(?P<raw>.*)$')
    records=defaultdict(list);unparsed=[]
    for line_no,line in enumerate(text.splitlines(),1):
        if ';H>' not in line or not line.startswith('<'):continue
        m=pattern.match(line)
        if not m:unparsed.append(dict(source_line=line_no,raw=line));continue
        d=m.groupdict()
        records[f"{d['folio']}.{d['num']}"].append(dict(source_line=line_no,unit=d['unit'],raw=d['raw'].strip(),folio=d['folio']))
    return records,unparsed

def source_gate():
    folder=OUT/'source';folder.mkdir()
    originals,unparsed=original_records()
    modern=iv.parse(LAB/'data/raw/LSI_ivtff_0d.txt','LSI')
    banned={family(r['folio']) for r in csvrows(LAB/'results/ringdir/preflight/ring_inventory.csv')}
    selected=[r for r in modern if r['transcriber']=='H' and r['locus_code'][1:] in {'P0','P1','Pc','Pr','Pt'} and family(r['folio']) not in banned]
    corrected=adapt([r for r in modern if r['transcriber']=='H' and family(r['folio']) not in banned]);jsonlines(folder/'corrected_adapter_records.jsonl',corrected)
    ledger=[]
    for r in selected:
        found=originals.get(r['line_id'],[])
        base=dict(locus=r['line_id'],family=family(r['folio']),modern_source_line=r['source_line'],modern_raw=r['text_raw'],modern_locus_code=r['locus_code'])
        if len(found)!=1:
            ledger.append(dict(**base,status='UNRESOLVED_IDENTITY',original_candidates=found));continue
        o=found[0];a=canonical(o['raw'],True);b=canonical(r['text_raw'])
        base.update(original_source_line=o['source_line'],original_unit=o['unit'],original_raw=o['raw'],original_canonical=a,modern_canonical=b)
        if a['held'] or b['held'] or r['is_spurious'] or r['has_missing_span'] or r['has_uncertainty']:
            ledger.append(dict(**base,status='HELD_SOURCE_SPAN'));continue
        issues=[]
        if a['stream']!=b['stream']:issues.append('glyph_stream')
        if a['boundaries']!=b['boundaries']:issues.append('word_boundary_offsets_or_types')
        if a['paragraph_end']!=b['paragraph_end']:issues.append('paragraph_end_conversion')
        ledger.append(dict(**base,status='FAIL_SOURCE_DIFFERENCE' if issues else 'MATCH',issues=issues))
    jsonlines(folder/'collation.jsonl',ledger);save(folder/'unparsed_original_H.json',unparsed)
    counts=Counter(r['status'] for r in ledger);clean=[r for r in ledger if r['status'] in {'MATCH','FAIL_SOURCE_DIFFERENCE'}]
    issues=Counter(s for r in ledger for s in r.get('issues',[]))
    if unparsed or counts['UNRESOLVED_IDENTITY'] or counts['FAIL_SOURCE_DIFFERENCE']:status='FAIL_SOURCE_FIDELITY'
    elif len(clean)<30 or len({r['family'] for r in clean})<8:status='UNSUPPORTED_SOURCE_FIDELITY'
    else:status='PASS_CLEAN_PARAGRAPH_SOURCE_FIDELITY'
    result=dict(status=status,selected_loci=len(selected),counts=dict(counts),difference_types=dict(issues),unparsed_original_H=len(unparsed),clean_compared=len(clean),clean_families=len({r['family'] for r in clean}),
        original_sha256=sha(HERE/'sources/text16e6.evt'),lsi_sha256=sha(LAB/'data/raw/LSI_ivtff_0d.txt'),
        unknown_start_records=sum(r['paragraph_start'] is None for r in corrected),
        scope='Non-ring ordinary paragraph H only; original publisher/editorial source, not manuscript truth')
    save(folder/'STATUS.json',result);return result

def diagnostic():
    folder=OUT/'boundary';folder.mkdir()
    banned={family(r['folio']) for r in csvrows(LAB/'results/ringdir/preflight/ring_inventory.csv')}
    zl=iv.parse(LAB/'data/raw/ZL3b-n.txt','ZL');hh=iv.parse(LAB/'data/raw/LSI_ivtff_0d.txt','LSI')
    hmap={r['line_id']:r for r in hh if r['transcriber']=='H' and r['locus_code'][1:] in {'P0','P1','Pc','Pr','Pt'}}
    ledger=[]
    for r in zl:
        if r['locus_code'][1:] not in {'P0','P1','Pc','Pr','Pt'}:continue
        f=family(r['folio'])
        if f in banned or stable('RD-v1-split|'+f)/2**32<.60:continue
        base=dict(locus=r['line_id'],family=f,variety=r['currier_lang'],scribe=r['hand_scribe'])
        h=hmap.get(r['line_id'])
        if h is None:ledger.append(dict(**base,status='MISSING_H'));continue
        if any(x['is_spurious'] or x['has_uncertainty'] or x['has_missing_span'] for x in [r,h]):
            ledger.append(dict(**base,status='HELD_SOURCE_UNCERTAINTY'));continue
        ledger.append(dict(**base,**boundary_comparison(canonical(r['text_raw']),canonical(h['text_raw']))))
    eligible=[r for r in ledger if r['status']=='ALIGNED'];jsonlines(folder/'locus_alignment.jsonl',ledger)
    if len(eligible)<30 or len({r['family'] for r in eligible})<8:
        result=dict(status='UNSUPPORTED_DIAGNOSTIC_SUPPORT',aligned_loci=len(eligible),families=len({r['family'] for r in eligible}))
    else:
        result=dict(status='DESCRIPTIVE_COMPLETE',counts=dict(Counter(r['status'] for r in ledger)),aligned_loci=len(eligible),families=len({r['family'] for r in eligible}),
            shared_boundaries=sum(len(r['shared']) for r in eligible),ZL_only=sum(len(r['ZL_only']) for r in eligible),H_only=sum(len(r['H_only']) for r in eligible),
            differing_boundary_types=sum(len(r['boundary_type_differences']) for r in eligible),
            differing_shared_junction_features=sum(v['different'] for r in eligible for v in r['shared_junction_features']),
            interpretation='Representation counts only; no causal, plaintext spacing, linguistic or robustness claim')
    save(folder/'STATUS.json',result);return result

def hold(name,reason):
    p=OUT/name;p.mkdir();save(p/'STATUS.json',dict(status='NOT_RUN_UPSTREAM_FAILURE',dependency=reason))

def run():
    OUT.mkdir();event('RUN_STARTED',registration_sha256=sha(REG/'REGISTRATION.json'))
    preservation();event('G0_PRESERVATION_PASS')
    p=OUT/'adapter';p.mkdir();fs=fixtures.execute();save(p/'fixtures.json',fs)
    good=all(x['passed'] for x in fs);adapter_status='PASS_ADAPTER_ENGINEERING' if good else 'FAIL_ADAPTER_ENGINEERING'
    save(p/'STATUS.json',dict(status=adapter_status,passed=sum(x['passed'] for x in fs),total=len(fs),scope='authored fixtures; not source fidelity'))
    event('G1_ADAPTER_COMPLETE',status=adapter_status)
    source=None;boundary=None
    if not good:hold('source',adapter_status);hold('boundary',adapter_status);status='STOP_'+adapter_status
    else:
        source=source_gate();event('G2_SOURCE_COMPLETE',status=source['status'])
        if source['status']!='PASS_CLEAN_PARAGRAPH_SOURCE_FIDELITY':hold('boundary',source['status']);status='STOP_'+source['status']
        else:boundary=diagnostic();status=boundary['status'];event('G3_BOUNDARY_COMPLETE',status=status)
    save(OUT/'STATUS.json',dict(id=ID,status=status,adapter=adapter_status,source=source['status'] if source else 'NOT_RUN_UPSTREAM_FAILURE',
        boundary=boundary['status'] if boundary else 'NOT_RUN_UPSTREAM_FAILURE',new_direction_fits=0,new_direction_scores=0,
        spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',prior_gate_labels='UNCHANGED',PDF_used=False))
    report=[f'# {ID} — corrected adapter and source gates','',f'**{status}**','',f'Adapter: {adapter_status}; {sum(x["passed"] for x in fs)}/{len(fs)} authored fixtures passed.','',
        'Layout locators no longer assert paragraph starts. Unknown starts remain null; locus-local text is retained. Safe fragments are not recovered paragraphs.']
    if source:
        report+=['','Source collation against the hash-bound original Stolfi1.6e6 archive:', '','```json',json.dumps(source,indent=2),'```','',
            'Every mismatch and held span is retained in source/collation.jsonl. A mismatch is an unresolved conversion difference, not automatically a demonstrated error in either editorial representation. No title-attachment or other exception was introduced after comparison.']
    report+=['',f'Boundary diagnostic: {boundary["status"] if boundary else "NOT_RUN_UPSTREAM_FAILURE"}.','',
        'Prior K1/K2 results, failed adapter run and all gate labels remain preserved. Numerical verification did not certify source semantics. No direction calibration or I-phase was rerun. Spacing interpretation and real-ring scoring CLOSED; radial HELD.']
    (OUT/'report.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    preservation();event('FINAL_PRESERVATION_PASS')
    save(OUT/'ARTIFACT_MANIFEST.json',dict(id=ID,hashes={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print(status,flush=True)

def verify():
    preservation()
    for p,h in load(OUT/'ARTIFACT_MANIFEST.json')['hashes'].items():assert sha(OUT/p)==h,p
    events=readlines(OUT/'events.jsonl');assert load(REG/'REGISTRATION.json')['utc']<events[0]['utc']
    fs=load(OUT/'adapter/fixtures.json');assert all(f['passed'] for f in fs)
    status=load(OUT/'STATUS.json');p=OUT/'source/collation.jsonl'
    if p.exists():
        rows=readlines(p);s=load(OUT/'source/STATUS.json')
        assert dict(Counter(r['status'] for r in rows))==s['counts']
        assert dict(Counter(x for r in rows for x in r.get('issues',[])))==s['difference_types']
        for r in rows:
            if r['status'] not in {'MATCH','FAIL_SOURCE_DIFFERENCE'}:continue
            a=r['original_canonical'];b=r['modern_canonical'];issues=[]
            if a['stream']!=b['stream']:issues.append('glyph_stream')
            if a['boundaries']!=b['boundaries']:issues.append('word_boundary_offsets_or_types')
            if a['paragraph_end']!=b['paragraph_end']:issues.append('paragraph_end_conversion')
            assert r['issues']==issues
    if status['source']!='PASS_CLEAN_PARAGRAPH_SOURCE_FIDELITY':
        assert load(OUT/'boundary/STATUS.json')['status']=='NOT_RUN_UPSTREAM_FAILURE'
        assert not (OUT/'boundary/locus_alignment.jsonl').exists()
    assert not list(OUT.rglob('models.json')) and not list(OUT.rglob('scores.jsonl'))
    save(OUT/'VERIFICATION.json',dict(status='PASS_AUDIT',prior_runs_unchanged=True,registration_precedes_gates=True,
        fixtures_passed=len(fs),source_ledger_arithmetic_verified=p.exists(),stop_graph_verified=True,
        source_gate=status['source'],boundary_gate=status['boundary'],spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',utc=now()))
    print('PASS_AUDIT',flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','run','verify']);a=p.parse_args()
    try:{'register':register,'run':run,'verify':verify}[a.stage]()
    except Exception as exc:
        if a.stage=='run' and OUT.exists():save(OUT/'TECHNICAL_FAILURE.json',dict(status='STOP_TECHNICAL_FAILURE',error=repr(exc),utc=now()))
        raise
