"""Prepare v4.1 before ratings. No tokenization, outcomes, ratings, or inference."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

R = Path(__file__).resolve().parent
P = R.parent
ATTACHMENT = Path(r'C:\Users\lewis\.codex\attachments\802b844e-37f0-4b82-868d-858133cc30ab\Pasted text.txt')
RESERVED = {'f72v1', 'f72v2', 'f73r', 'f73v'}
HEADER = 'PROSPECTIVE IN IMAGE VARIABLE ONLY — text events exposed (v100/v102).'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    p = R / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def seal(phase, names):
    path = R/'PHASES.jsonl'
    previous = sha(path) if path.exists() else None
    item = dict(phase=phase, utc=datetime.now(timezone.utc).isoformat(), previous_log_sha256=previous,
                files={n:sha(R/n) for n in names})
    with path.open('a', encoding='utf-8') as f: f.write(json.dumps(item, ensure_ascii=False)+'\n')

def prepare():
    if (R/'PROTOCOL.json').exists(): raise SystemExit('Already prepared; preserve freezes.')
    original = ATTACHMENT.read_bytes()
    (R/'ORIGINAL-SPEC.txt').write_bytes(original)
    spec = original.decode('utf-8-sig')
    amendment = (R/'AMENDMENT-v4.1.txt').read_text(encoding='utf-8')
    prior = json.loads((P/'sh-qok-context-map-v3/PROTOCOL.json').read_text(encoding='utf-8'))
    save('PROTOCOL.json', dict(status='DESIGN PRESERVED; PRE-RATING PREPARATION ONLY',
        spec=spec, amendment=amendment, original_sha256=sha(R/'ORIGINAL-SPEC.txt'),
        amendment_sha256=sha(R/'AMENDMENT-v4.1.txt'),
        source_hashes=prior['sources'], reserved_folios=sorted(RESERVED),
        phase_order=['protocol_and_amendment', 'amended_manual', 'independent_shared_line_registration',
                     'blind_picture_rating', 'derived_label_agreement_and_adjudication',
                     'outcome_blind_support', 'synthetic_qualification', 'outcome_join', 'tests'],
        phase_order_reason='v4.1 shared registered lines are required to compute agreement; registrar never sees picture boxes.',
        gates=dict(G6='Six-way kappa >= .60, before merge and adjudication; governs H-IMG',
                   G2='PL vs non-PL kappa >= .60, before adjudication; governs H-PLANT'),
        no_adjudication_rescue=True, manual_released=False,
        implementation_status='No rating or scientific scoring code executed. Remaining operational decisions in PREFLIGHT.json.'))
    seal('protocol_and_amendment', ['ORIGINAL-SPEC.txt','AMENDMENT-v4.1.txt','PROTOCOL.json'])
    manual = spec.split('## 3. Coding manual (give the raters this section and nothing else)',1)[1].split('\n## 4.',1)[0]
    manual = manual.rsplit('\n---',1)[0].strip()+'\n'
    old = '2. Draw a box around every **block of writing** and around **each line of writing** inside it. Number the lines top to bottom within each block.'
    assert old in manual
    manual = manual.replace(old, "2. You don't need to mark the writing.")
    # The old return-line sentence conflicts with the explicit abolition of rater line boxing.
    # Preserve it verbatim as requested; flag the conflict before distribution.
    (R/'MANUAL.md').write_text(manual, encoding='utf-8')
    seal('amended_manual_prepared_not_released', ['MANUAL.md'])
    for p,h in prior['sources'].items(): assert sha(Path(p)) == h, p
    meta_path = next(Path(p) for p in prior['sources'] if 'Davis-hands' in p)
    evt_path = next(Path(p) for p in prior['sources'] if 'text16e6' in p)
    metadata = {r['Folio']:r for r in csv.DictReader(meta_path.open(encoding='utf-8-sig'))}
    # Match locus headers only; never tokenize or inspect the captured writing body.
    lines = {}
    for raw in evt_path.open(encoding='latin1'):
        m = re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([HF])>', raw)
        if not m: continue
        pg,unit,num,reading = m.groups()
        if pg in RESERVED or not unit.startswith('P') or metadata.get(pg,{}).get('Scribe') not in ('1','2','3'): continue
        key = f'{pg}.{unit}.{num}'
        row = lines.setdefault(key, dict(folio=pg,unit=unit,line_number=num,locus=key,readings=[],status='UNREGISTERED'))
        assert reading not in row['readings'], (key,reading)
        row['readings'].append(reading)
    save('private/LINE-REGISTRATION-QUEUE.json', list(lines.values()))
    pages = sorted({r['folio'] for r in lines.values()})
    manifest_path = P/'g-ending-audit-v89/YALE-MANIFEST.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    bylabel = {}
    for c in manifest['items']:
        label = next(iter(c['label'].values()))[0]
        bylabel.setdefault(label, []).append(c)
    tasks, held = [], []
    for page in pages:
        choices = bylabel.get(page[1:], [])
        if len(choices) != 1:
            held.append(dict(folio=page, reason='No unique exact single-folio canvas; panel registration required.'))
            continue
        c = choices[0]
        body = c['items'][0]['items'][0]['body']
        tid = 'I'+hashlib.sha256(('v4.1/'+page).encode()).hexdigest()[:16]
        tasks.append(dict(task_id=tid,folio=page,canvas_id=c['id'],native_width=c['width'],native_height=c['height'],
                          image='images/'+tid+'.jpg',url=body['service'][0]['@id']+'/full/!1800,1800/0/default.jpg'))
    save('private/IMAGE-QUEUE.json',dict(tasks=tasks,withheld=held,manifest_sha256=sha(manifest_path)))
    issues = [
        dict(id='manual_return_sentence', status='CLARIFICATION_NEEDED',
             detail='v4.1 says nothing else changes, but the manual final sentence still requests one row per writing line. It conflicts with no writing boxes. Manual preserved with this conflict and not released.'),
        dict(id='line_registration',status='PENDING', detail='Independent outcome-blind registrar must supply line AND block boxes, exact EVT crosswalk, H/F count discrepancies and dropped blocks. Existing tool accepts annotations but does not produce an automatic crosswalk.'),
        dict(id='Q_definition',status='NOT_IMPLEMENTED', detail='Specify exact between-label weights, cluster variance, covariance handling, undefined-permutation policy and seeds before scoring. v3 uses inverse folio-cluster variance; v4 does not explicitly select that formula.'),
        dict(id='adjudication_geometry',status='NOT_IMPLEMENTED', detail='Third rater returns picture boxes on whole disagreement pages; retain third-rater labels for disputed lines only. Separate final six-way and binary-majority labels are required.'),
        dict(id='position_claim',status='QUALIFICATION_REQUIRED', detail='Strata include length bin but not position. Within-folio label permutations do not preserve label-position association. The wrap/position null must qualify this; a pass cannot by itself establish adjustment for every position variable.'),
        dict(id='support_scope',status='NOT_IMPLEMENTED', detail='Specify label-support and multi-label-folio selection order, total-V denominator, and whether qualifying support is recomputed under each shuffle before scoring. Support uses prefix counts, not qok outcomes.'),
        dict(id='synthetic_generators',status='NOT_IMPLEMENTED', detail='Freeze baselines, position functions, folio effects, dependence assumptions, rejection alpha and seeds for all six scenarios. 200 trials are binding; do not tune after seeing failures.'),
        dict(id='rater_isolation',status='PENDING', detail='No raters invoked. An ordinary analyst fork with inherited history is ineligible; no restricted fresh vision-session interface has been established here.'),
    ]
    save('PREFLIGHT.json',dict(status='PRE-RATING; NO SCIENTIFIC RESULT',issues=issues,
        cohort_folios=len(pages),physical_source_loci=len(lines),exact_single_folio_images=len(tasks),withheld_panels=len(held),
        cohort_rule='All scribe1/2/3 H/F P-unit locus headers, reserved folios excluded; not selected using old event presence or outcomes.',
        legacy_packet='Incompatible categories; not reused. Legacy receipts had 0 ready images.',
        network_probe='Sandbox DNS failed; escalated public Yale image request succeeded: HTTP 200 image/jpeg.'))
    (R/'REPORT.md').write_text(HEADER+'\n\n'+
        '\n'.join(f'H-IMG scribe{s}-{r}: PENDING — Q unavailable, Holm p unavailable' for s in (1,2,3) for r in ('H','F'))+
        '\n\nPre-rating preparation only. PENDING is a workflow state, not a scientific result from the specified result vocabulary. '
        'No agreement, support, controls, joins or tests have run. v4.1 is preserved and hashed before any manual release. '
        'The manual is withheld pending resolution of its remaining line-return instruction. See PREFLIGHT.json.\n',encoding='utf-8')
    seal('preflight_and_private_source_inventory', ['PREFLIGHT.json','private/LINE-REGISTRATION-QUEUE.json','private/IMAGE-QUEUE.json','REPORT.md'])

def fetch():
    from PIL import Image
    queue = json.loads((R/'private/IMAGE-QUEUE.json').read_text(encoding='utf-8'))
    (R/'private/images').mkdir(exist_ok=True)
    def one(t):
        p = R/'private'/t['image']
        try:
            if not p.exists():
                with urllib.request.urlopen(t['url'], timeout=40) as response: data = response.read()
                temp = p.with_suffix('.partial')
                temp.write_bytes(data)
                with Image.open(temp) as im: im.verify()
                temp.replace(p)
            with Image.open(p) as im:
                im.verify()
            return dict(task_id=t['task_id'],status='READY',sha256=sha(p),bytes=p.stat().st_size)
        except Exception as exc: return dict(task_id=t['task_id'],status='FETCH_FAILED',error=str(exc))
    receipts = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for item in pool.map(one,queue['tasks']):
            receipts.append(item)
            if len(receipts)%20 == 0: print('Retrieved',len(receipts),'of',len(queue['tasks']),flush=True)
    save('private/IMAGE-RECEIPTS.json',receipts)
    seal('private_image_retrieval_no_ratings', ['private/IMAGE-RECEIPTS.json'])
    print(json.dumps(dict(ready=sum(r['status']=='READY' for r in receipts),failed=sum(r['status']!='READY' for r in receipts),withheld=len(queue['withheld']))))

def verify():
    phases = [json.loads(s) for s in (R/'PHASES.jsonl').read_text(encoding='utf-8').splitlines()]
    checks = {}
    previous = b''
    for raw,phase in zip((R/'PHASES.jsonl').read_bytes().splitlines(keepends=True),phases):
        assert phase['previous_log_sha256'] == (hashlib.sha256(previous).hexdigest() if previous else None)
        for n,h in phase['files'].items():
            archived = R/'private/hash-history'/h
            assert sha(R/n)==h or (archived.exists() and sha(archived)==h),n
        previous += raw
    checks['phase_chain_and_files'] = True
    assert (R/'ORIGINAL-SPEC.txt').read_bytes()==ATTACHMENT.read_bytes()
    checks['original_byte_identical'] = True
    assert (R/'REPORT.md').read_text(encoding='utf-8').splitlines()[0] == HEADER
    checks['mandatory_report_first_line'] = True
    q = json.loads((R/'private/IMAGE-QUEUE.json').read_text(encoding='utf-8'))
    assert not RESERVED.intersection(t['folio'] for t in q['tasks'])
    assert not any((R/n).exists() for n in ['RATER-A.csv','RATER-B.csv','AGREEMENT.json','SUPPORT.json','EVENTS.csv','H-IMG.json','H-PLANT.json'])
    checks['reserved_images_excluded_and_no_fabricated_results'] = True
    save('VERIFICATION.json',dict(status='PASS_PREPARATION_ONLY',checks=checks,scientific_validation=False,
        hashes={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and p.name!='VERIFICATION.json'}))
    print(json.dumps(checks))

def finish():
    # Preserve the first manual bytes before correcting CRLF duplication introduced
    # by decoding attachment bytes and writing in Windows text mode. Wording stays identical.
    p = R/'MANUAL.md'
    data = p.read_bytes()
    normalized = data.replace(b'\r\r\n',b'\r\n')
    if data != normalized:
        archive = R/'private/hash-history'
        archive.mkdir(exist_ok=True)
        (archive/sha(p)).write_bytes(data)
        p.write_bytes(normalized)
        seal('manual_newline_serialization_repair_no_wording_change', ['MANUAL.md'])
    receipts = json.loads((R/'private/IMAGE-RECEIPTS.json').read_text(encoding='utf-8'))
    preflight = json.loads((R/'PREFLIGHT.json').read_text(encoding='utf-8'))
    save('DELIVERY.json',dict(status='PREPARED; INDEPENDENT REGISTRATION AND RATINGS PENDING',
        ready_images=sum(r['status']=='READY' for r in receipts),failed_images=sum(r['status']!='READY' for r in receipts),
        withheld_panels=preflight['withheld_panels'],cohort_folios=preflight['cohort_folios'],
        source_loci=preflight['physical_source_loci'],manual_released=False,ratings_collected=0,
        scientific_results=None,next_step='Resolve manual final sentence; establish independent blinded registration and restricted fresh picture-rater sessions.',
        limitation='Available tools do not establish a fresh vision-model session restricted to only images and manual. This analyst has seen outcomes and cannot substitute as a blind rater or registrar.'))
    seal('preparation_delivery', ['DELIVERY.json','REGISTRAR-CONTRACT.json','prepare.py'])
    verify()

if __name__ == '__main__':
    {'prepare':prepare,'fetch':fetch,'verify':verify,'finish':finish}[sys.argv[1]]()
