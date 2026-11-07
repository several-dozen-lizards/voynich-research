"""Content-blind source metadata and reviewer packet only. No glyph comparisons."""
import sys
sys.dont_write_bytecode=True
import argparse,csv,hashlib,importlib.util,json,re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent;LAB=HERE.parents[1];WORK=LAB.parent
ID='JX-20261107-K2R-1';SEED=2026110704
REG=HERE/'registration';OUT=LAB/'results/jx/K2R'/ID
SOURCE=LAB/'extensions/jx_lsi_boundary_20261107/sources/text16e6.evt'
ZL=LAB/'data/raw/ZL3b-n.txt'
PREV=LAB/'extensions/jx_lsi_boundary_20261107/registration/REGISTRATION.json'
PREVOUT=LAB/'results/jx/JX-20261107-LSIB-1'
def now():return datetime.now(timezone.utc).isoformat()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False)
def table(p,rows):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def readtable(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def family(f):
    if f=='fRos' or re.match(r'^f(?:85|86)[rv]',f):return 'rosettes'
    return re.match(r'^f(\d+)',f)[1]
def split(f):return 'train' if int(hashlib.sha256(('RD-v1-split|'+family(f)).encode()).hexdigest()[:8],16)/2**32<.60 else 'heldout'

ORIGINAL=re.compile(r'^<(?P<folio>f[^.>]+)\.(?P<unit>[^.>]+)\.(?P<num>\d+[a-z]?);(?P<reader>[A-Z])>$')
ZL_LOCUS=re.compile(r'^<(?P<folio>f[^.>]+)\.(?P<num>\d+[a-z]?),?(?P<code>[^;>]+)>$')
def original_kind(unit):
    if re.fullmatch(r'P\d*',unit):return 'body'
    if re.fullmatch(r'T\d*',unit):return 'title'
    return 'unresolved_type'
def original_header(header):
    m=ORIGINAL.fullmatch(header)
    if not m:raise ValueError('Unparsed original record header: '+header)
    d=m.groupdict();d['kind']=original_kind(d['unit']);d['source_id']=f"{d['folio']}.{d['unit']}.{d['num']}"
    return d

def original_metadata(path):
    physical={};readers=Counter();unparsed=[]
    for n,line in enumerate(Path(path).read_text(encoding='latin-1').splitlines(),1):
        if not line.startswith('<') or ';' not in line.split('>',1)[0]:continue
        # Only header bytes reach the parser; text after > cannot influence mapping.
        header=line.split('>',1)[0]+'>'
        try:d=original_header(header)
        except ValueError:unparsed.append(dict(source_line=n,header=header));continue
        readers[d['reader']]+=1
        row=physical.setdefault(d['source_id'],dict(folio=d['folio'],unit=d['unit'],num=d['num'],source_id=d['source_id'],kind=d['kind'],source_order=len(physical),first_source_line=n,readers=[]))
        if d['reader'] in row['readers']:raise ValueError('Duplicate reader at original full locus '+header)
        row['readers'].append(d['reader'])
    return list(physical.values()),dict(readers),unparsed

def zl_metadata(path):
    out=[]
    for n,line in enumerate(Path(path).read_text(encoding='latin-1').splitlines(),1):
        if not line.startswith('<f') or '.' not in line.split('>',1)[0]:continue
        head=line.split('>',1)[0]+'>'
        m=re.fullmatch(r'<(f[^.>]+)\.(\d+[a-z]?),([^;>]+)>',head)
        if not m:raise ValueError('Unparsed ZL header '+head)
        folio,num,code=m.groups();t=code[1:]
        if t not in {'P0','P1','Pc','Pr','Pt'}:continue
        out.append(dict(folio=folio,zl_id=folio+'.'+num,zl_code=code,kind='title' if t=='Pt' else 'body',source_line=n,order=len(out)))
    return out

def match_metadata(original,zl,banned):
    # This function receives metadata ONLY. It cannot read files or text fields.
    assert all('raw' not in r and 'text' not in r and 'words' not in r for r in original+zl)
    og=defaultdict(list);zg=defaultdict(list);held=[]
    for r in original:
        if family(r['folio']) in banned:continue
        if r['kind']=='unresolved_type':
            held.append(dict(folio=r['folio'],kind=r['kind'],source_id=r['source_id'],reason='TYPE_UNRESOLVED_NOT_PRIMARY'));continue
        og[r['folio'],r['kind']].append(r)
    for r in zl:
        if family(r['folio']) not in banned:zg[r['folio'],r['kind']].append(r)
    pairs=[];groups=[]
    for folio,kind in sorted(set(og)|set(zg)):
        aa=og[folio,kind];bb=zg[folio,kind];equal=bool(aa and len(aa)==len(bb))
        groups.append(dict(folio=folio,family=family(folio),split=split(folio),kind=kind,original_loci=len(aa),ZL_loci=len(bb),status='STRUCTURAL_REVIEW_REQUIRED' if equal else 'AMBIGUOUS_COUNT_MISMATCH'))
        if not equal:
            held.append(dict(folio=folio,kind=kind,source_ids=';'.join(r['source_id'] for r in aa),zl_ids=';'.join(r['zl_id'] for r in bb),reason='AMBIGUOUS_COUNT_MISMATCH'));continue
        for i,(a,b) in enumerate(zip(aa,bb),1):
            pairs.append(dict(pair_id=f'{folio}:{kind}:{i:03d}',folio=folio,family=family(folio),split=split(folio),kind=kind,ordinal=i,
                ZL_id=b['zl_id'],ZL_source_line=b['source_line'],ZL_type=b['zl_code'],original_id=a['source_id'],original_unit=a['unit'],original_num=a['num'],original_first_source_line=a['first_source_line'],
                original_readers=';'.join(sorted(a['readers'])),H_present='H' in a['readers'],confidence='STRUCTURAL_REVIEW_REQUIRED',
                basis='Exact folio/panel + source-documented body/title class + equal complete line counts + file order; no glyph/word-count comparison',
                review_status='PENDING_RE',ZL_metadata_label='NOT_LOADED_FOR_PAIRING'))
    return pairs,held,groups

def engineering():
    results=[]
    def check(name,value):results.append(dict(name=name,passed=bool(value)))
    check('original_alpha_locus',original_header('<f112v.P2.44a;H>')['source_id']=='f112v.P2.44a')
    check('original_reader_codes',original_header('<f1r.P1.1;V>')['reader']=='V')
    check('unknown_unit_is_not_inferred',original_kind('Q')=='unresolved_type')
    spec=importlib.util.spec_from_file_location('frozen_canonical',LAB/'extensions/jx_lsi_boundary_20261107/adapter.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    a=mod.canonical('ab!.cd,ef- {plant}',True)
    check('word_breaks_padding_comments',a['literal']=='ab.cd,ef' and a['boundaries']==[[2,'.'],[4,',']])
    check('paragraph_vs_line_marker',mod.canonical('ab.cd=',True)['paragraph_end'] and not a['paragraph_end'])
    check('alternates_and_illegible_held',mod.canonical('[ab|cd].ef-',True)['held'] and mod.canonical('ab.*f-',True)['held'])
    aa=[dict(folio='f1r',kind='body',source_id='f1r.P.9',unit='P',num='9',first_source_line=2,readers=['H'])]
    bb=[dict(folio='f1r',kind='body',zl_id='f1r.1',source_line=3,zl_code='@P0')]
    pairs,held,groups=match_metadata(aa,bb,set())
    check('structural_order_not_numeric_id',len(pairs)==1 and pairs[0]['original_num']=='9' and pairs[0]['confidence']=='STRUCTURAL_REVIEW_REQUIRED')
    p,h,g=match_metadata(aa,bb+bb,set());check('count_mismatch_held',not p and h[0]['reason']=='AMBIGUOUS_COUNT_MISMATCH')
    return results

def register():
    assert not OUT.exists();REG.mkdir()
    prior=load(PREV);paths={WORK/p for p in prior['hashes']}
    for p,h in prior['hashes'].items():assert sha(WORK/p)==h,p
    for p,h in load(PREVOUT/'ARTIFACT_MANIFEST.json')['hashes'].items():assert sha(PREVOUT/p)==h,p
    paths.update(p for p in PREVOUT.rglob('*') if p.is_file());paths.add(PREV)
    paths.update(p for p in HERE.iterdir() if p.is_file())
    save(REG/'REGISTRATION.json',dict(id=ID,utc=now(),seed=SEED,python=sys.version,
        authority='User requested K2R; crosswalk review explicitly required by supplied Stage1.3',
        phase='SOURCE_INTAKE_REGISTERED; full conditional protocol frozen; crosswalk review and target executable bindings pending',
        hashes={(p.relative_to(WORK).as_posix() if p.is_relative_to(WORK) else str(p)):sha(p) for p in sorted(paths)},
        reviewer='Re or reviewer explicitly designated by Re; no designation currently supplied',
        source_thresholds=dict(distinct_windows=30,families=8,bins=[[11,20],[21,40]],near_total_agreement_below=.20),
        performance_thresholds=dict(accuracy=.80,lower_95_bound=.65),
        crosswalk_review='PENDING',target_executable='NOT_BOUND_PENDING_REVIEW',I_phase='CLOSED',spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD'))
    for name in ['SPEC_SUPPLIED.md','EXECUTION.md','stage1.py']:
        with (REG/name).open('xb') as f:f.write((HERE/name).read_bytes())
    print('REGISTERED',ID,'source intake and conditional protocol; no comparisons or fits',flush=True)

def check():
    for p,h in load(REG/'REGISTRATION.json')['hashes'].items():assert sha(WORK/p)==h,p

def prepare():
    check();OUT.mkdir(parents=True)
    save(OUT/'START.json',dict(utc=now(),registration_sha256=sha(REG/'REGISTRATION.json')))
    fs=engineering();save(OUT/'fixtures.json',fs)
    if not all(r['passed'] for r in fs):
        save(OUT/'STATUS.json',dict(status='STOP_FAIL_SOURCE_PARSER_ENGINEERING'));return
    original,counts,unparsed=original_metadata(SOURCE);zl=zl_metadata(ZL)
    save(OUT/'unparsed_headers.json',unparsed)
    if unparsed:
        save(OUT/'STATUS.json',dict(status='STOP_FAIL_SOURCE_PARSER',unparsed=len(unparsed)));return
    banned={family(r['folio']) for r in readtable(LAB/'results/ringdir/preflight/ring_inventory.csv')}
    pairs,held,groups=match_metadata(original,zl,banned)
    table(OUT/'crosswalk_candidates.csv',pairs);table(OUT/'held_metadata.csv',held);table(OUT/'folio_type_counts.csv',groups)
    inventory=[]
    for code,n in sorted(counts.items()):
        ps=[p for p in pairs if code in p['original_readers'].split(';')]
        status='DOCUMENTED_INDEPENDENT_READING' if code=='H' else ('DERIVED_ALTERNATE' if code in 'DGIQM' else 'UNKNOWN_LOCUS_LEVEL_INDEPENDENCE')
        inventory.append(dict(code=code,original_records=n,proposed_mapped_paragraph_loci=len(ps),heldout_families=len({p['family'] for p in ps if p['split']=='heldout'}),
            independence=status,provenance='Original archive introduction f0.K; separately manuscript-produced, retained in edited archive' if code=='H' else 'Original archive transcriber-code list; named identity/composite label does not establish independent locus-level contribution',
            provenance_source_sha256=sha(SOURCE),word_coverage='NOT_RUN_PENDING_CROSSWALK_REVIEW',bin_11_20_support='NOT_RUN_PENDING_CROSSWALK_REVIEW',bin_21_40_support='NOT_RUN_PENDING_CROSSWALK_REVIEW'))
    table(OUT/'reading_inventory.csv',inventory)
    summary=dict(proposed_pairs=len(pairs),H_present=sum(p['H_present'] for p in pairs),H_missing=sum(not p['H_present'] for p in pairs),
        structural_folio_type_groups=sum(g['status']=='STRUCTURAL_REVIEW_REQUIRED' for g in groups),ambiguous_folio_type_groups=sum(g['status']=='AMBIGUOUS_COUNT_MISMATCH' for g in groups),
        unresolved_type_original_rows=sum(h['reason']=='TYPE_UNRESOLVED_NOT_PRIMARY' for h in held),
        proposed_H_heldout_families=len({p['family'] for p in pairs if p['H_present'] and p['split']=='heldout'}),
        glyph_content_used_for_pairing=False,glyph_comparisons=0,models_fitted=0,scores_computed=0)
    save(OUT/'review_summary.json',summary)
    review=['# K2R content-blind crosswalk — review required','',
        'This packet proposes structural identities only. No glyph strings, paired agreement, scores or direction calls were used. Equal folio/type line counts and ordinal position are the entire pairing rule. They require review and do not establish identity by themselves.','',
        'Original P/Pn units are body; T/Tn units are title. Other unit types are held. ZL Pt is title; P0/P1/Pc/Pr are body. Whole folio/type groups with unequal counts are held, without shifts or partial matching. Numeric IDs may differ.','',
        '## Counts','', '```json',json.dumps(summary,indent=2),'```','',
        '## Files to review','',
        '- crosswalk_candidates.csv: every proposed pair, reader coverage, source positions and confidence.','- folio_type_counts.csv: the complete count-equality basis by folio/type.','- held_metadata.csv: all count-mismatch groups and unresolved original types.','- reading_inventory.csv: all reader codes, provenance status and provisional metadata coverage.','',
        '## Sample proposals (metadata only)','', '| ZL | Original | Type | H present | Confidence |','|---|---|---|---|---|']
    examples=[p for p in pairs if p['ZL_id'].rsplit('.',1)[-1]!=p['original_num']][:12] or pairs[:12]
    for p in examples:review.append(f"| {p['ZL_id']} | {p['original_id']} | {p['kind']} | {p['H_present']} | structural, pending review |")
    review+=['','Review decision requested from Re: approve these exact structural candidates with all listed ambiguous/unknown groups held, or identify metadata-supported corrections. Approval binds the exact CSV hashes; it does not certify glyph agreement or performance. No glyph-based corrections are allowed.','',
        'The supplied spec Stage1.3 requires this review before any glyph streams are compared. Stage1 span/support qualification and Stages2/3 remain NOT_RUN_PENDING_REVIEW. Thresholds remain .80 accuracy/.65 lower95% bound, with the inherited family support and stratum adjustment. No I-phase or real-ring scoring opens.']
    with (OUT/'CROSSWALK_REVIEW.md').open('x',encoding='utf-8') as f:f.write('\n'.join(review)+'\n')
    save(OUT/'REVIEW_BINDING.json',dict(status='CANDIDATE_NOT_APPROVED',registration_sha256=sha(REG/'REGISTRATION.json'),
        source_sha256=sha(SOURCE),ZL_sha256=sha(ZL),hashes={n:sha(OUT/n) for n in ['crosswalk_candidates.csv','folio_type_counts.csv','held_metadata.csv','reading_inventory.csv']},reviewer=None))
    for name in ['span_validation','robustness','boundary']:
        save(OUT/name/'STATUS.json',dict(status='NOT_RUN_PENDING_CROSSWALK_REVIEW',target_executable='NOT_BOUND_PENDING_REVIEW' if name!='span_validation' else 'Pending reviewed crosswalk and executable binding'))
    save(OUT/'STATUS.json',dict(id=ID,status='AWAITING_CROSSWALK_REVIEW',source_parser_fixtures='PASS',crosswalk='CANDIDATE_NOT_APPROVED',
        source_identity='NOT_QUALIFIED_PENDING_REVIEW',span_validation='NOT_RUN',robustness='NOT_RUN',boundary='NOT_RUN',
        target_executable='NOT_BOUND_PENDING_REVIEW',I_phase='CLOSED',spacing_interpretation='CLOSED',real_ring_scoring='CLOSED',radial='HELD',prior_gates='UNCHANGED'))
    check()
    save(OUT/'ARTIFACT_MANIFEST.json',dict(id=ID,hashes={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print(json.dumps(summary,indent=2));print('AWAITING_CROSSWALK_REVIEW',flush=True)

def verify():
    check()
    for p,h in load(OUT/'ARTIFACT_MANIFEST.json')['hashes'].items():assert sha(OUT/p)==h,p
    pairs=readtable(OUT/'crosswalk_candidates.csv');groups=readtable(OUT/'folio_type_counts.csv')
    basis={(g['folio'],g['kind']):g for g in groups}
    for p in pairs:
        g=basis[p['folio'],p['kind']];assert g['original_loci']==g['ZL_loci'] and g['status']=='STRUCTURAL_REVIEW_REQUIRED'
        assert p['confidence']=='STRUCTURAL_REVIEW_REQUIRED' and p['review_status']=='PENDING_RE'
    assert len({p['ZL_id'] for p in pairs})==len(pairs)==len({p['original_id'] for p in pairs})
    assert load(REG/'REGISTRATION.json')['utc']<load(OUT/'START.json')['utc']
    assert load(OUT/'REVIEW_BINDING.json')['reviewer'] is None
    assert not list(OUT.rglob('scores.jsonl')) and not list(OUT.rglob('models.json'))
    for name in ['span_validation','robustness','boundary']:assert load(OUT/name/'STATUS.json')['status']=='NOT_RUN_PENDING_CROSSWALK_REVIEW'
    save(OUT/'VERIFICATION.json',dict(status='PASS_METADATA_PACKET_AUDIT_ONLY',prior_runs_unchanged=True,
        registration_before_preparation=True,one_to_one_proposals=True,no_glyph_comparisons=True,no_target_scores=True,review_approved=False,utc=now()))
    print('PASS_METADATA_PACKET_AUDIT_ONLY',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['register','prepare','verify']);a=p.parse_args()
    try:{'register':register,'prepare':prepare,'verify':verify}[a.stage]()
    except Exception as e:
        if a.stage=='prepare' and OUT.exists():save(OUT/'TECHNICAL_FAILURE.json',dict(status='STOP_TECHNICAL_FAILURE',error=repr(e),utc=now()))
        raise
