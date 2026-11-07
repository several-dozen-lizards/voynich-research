"""Prepare a separate blind packet; never run ratings or mutate initial evidence."""
from pathlib import Path
import collections, csv, hashlib, html, json, random, shutil, zipfile
from datetime import datetime, timezone

V = Path(__file__).resolve().parent
R = V / 'ratings'
D = V / 'adjudication-prep'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, obj): p.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def verify_initial():
    seal = load(R/'AGREEMENT-FINAL-SEAL.json')
    count = 0
    for section in ['files', 'data']:
        for name, expected in seal[section].items():
            assert sha(R/name) == expected, name
            count += 1
    for name, expected in load(R/'AGREEMENT-CLARIFICATION-SEAL.json').items():
        assert sha(R/name) == expected, name
        count += 1
    assert sha(V/'registration/SHARED-LINE-GEOMETRY.json') == seal['geometry_sha256']
    return count

def main():
    checked = verify_initial()
    assert not D.exists(), 'Refusing to replace an existing preparation'
    geom = load(V/'registration/SHARED-LINE-GEOMETRY.json')['lines']
    tasks = {t['task_id']:t for t in load(V/'rater-only/TASKS.json')}
    labels = {}
    for role in ['A','B']:
        with (R/f'LINE-CONTEXT-{role}.csv').open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        labels[role] = {r['shared_line_id']:r['label'] for r in rows}
        assert len(labels[role]) == len(rows)
    queue = []
    breakdown = collections.Counter()
    for line in geom:
        lid = line['shared_line_id']; a = labels['A'].get(lid); b = labels['B'].get(lid)
        if a is not None and b is not None and a == b: continue
        reason = ('DISAGREEMENT' if a is not None and b is not None else
                  'MISSING_BOTH' if a is None and b is None else
                  'MISSING_A' if a is None else 'MISSING_B')
        binary = a is not None and b is not None and ((a=='PL') != (b=='PL'))
        queue.append(dict(shared_line_id=lid, original_task_id=line['task_id'],
                          reason=reason, original_A=a or '', original_B=b or '',
                          G2_disagreement=binary))
        breakdown[reason] += 1
    assert len(geom)==1145 and breakdown['DISAGREEMENT']==194
    assert len(queue)==427 and sum(r['G2_disagreement'] for r in queue)==118
    selected = sorted({r['original_task_id'] for r in queue})
    seed = 'v4.1-v4.2-third-picture-preparation-2026-10-25'
    random.Random(seed).shuffle(selected)
    packet = D/'rater-only'; (packet/'images').mkdir(parents=True)
    public = []; crosswalk = []
    for tid in selected:
        t = tasks[tid]
        cid = 'P'+hashlib.sha256((seed+tid).encode()).hexdigest()[:16]
        src = V/'rater-only'/t['image']; dst = packet/'images'/f'{cid}.jpg'
        shutil.copyfile(src,dst)
        assert sha(src)==sha(dst)
        public.append(dict(task_id=cid,image=f'images/{cid}.jpg',
                           native_width=t['native_width'],native_height=t['native_height']))
        crosswalk.append(dict(third_task_id=cid, original_task_id=tid,
                              image_sha256=sha(src)))
    manual = (V/'MANUAL.md').read_text(encoding='utf-8-sig')
    shutil.copyfile(V/'MANUAL.md', packet/'MANUAL.md')
    # Identical coordinate-only operational appendix for isolated model calls.
    shutil.copyfile(R/'MANUAL-RATER.md', packet/'MANUAL-MODEL.md')
    save(packet/'TASKS.json',public)
    template = (V/'picture-tool-template.html').read_text(encoding='utf-8-sig')
    page = template.replace('__MANUAL__',html.escape(manual)).replace('__TASKS__',json.dumps(public))
    (packet/'index.html').write_text(page,encoding='utf-8')
    save(D/'PRIVATE-CROSSWALK.json',dict(seed=seed,pages=crosswalk))
    with (D/'PRIVATE-TARGET-LINES.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(queue[0]));writer.writeheader();writer.writerows(queue)
    failures=[]
    for role in ['A','B']:
        for tid in selected:
            if (R/'responses'/role/f'{tid}.json').exists():continue
            p=R/'attempts'/role/f'{tid}.json'; rec=load(p) if p.exists() else {}
            failures.append(dict(role=role,original_task_id=tid,original_attempt=str(p.relative_to(V)),
                                 original_attempt_sha256=sha(p) if p.exists() else None,
                                 status=rec.get('status'),failure=rec.get('failure')))
    save(D/'PRIVATE-MISSING-ANNOTATIONS.json',failures)
    initial=load(R/'AGREEMENT.json')
    protocol=dict(status='PREPARED ONLY; NO THIRD RATINGS OR ADJUDICATION RUN',
        created_utc=datetime.now(timezone.utc).isoformat(),authority='User requested preparation of blind adjudication for disagreements and 233 unpaired lines.',
        target_lines=len(queue),reason_counts=dict(breakdown),G2_disagreements=118,
        full_pages=len(public),registered_physical_lines=len(geom),
        selection='Union of six-way disagreements and missing A/B pairs. Whole source pages; all pictures independently annotated. No target-line cues.',
        rater='Fresh uninformed human or isolated model; never Re, analyst, initial rater context or registrar context.',
        model_route='One isolated call per page, only that image and MANUAL-MODEL.md; no tools, file/project access, previous responses or memory. Record model version and session provenance. No calls made by preparation.',
        registration='Frozen geometry and original assign/validate_response functions in ratings/agreement.py, unchanged. Apply separately after C collection; never expose geometry to rater.',
        proposed_resolution_policy={
            'status':'DRAFT; NOT APPLIED. Explicitly preserve unresolved cases.',
            'initial_agreement':'Retain A/B label. C observations on same page kept separately.',
            'initial_disagreement':'C matching A or B gives two-of-three consensus; three distinct valid labels remains unresolved.',
            'one_initial_missing':'If C agrees with sole original, mark two-observation agreement; otherwise unresolved. Original missing slot stays missing.',
            'both_initial_missing':'C-only supplemental observation, not consensus or repaired A/B pair.',
            'missing_invalid_C':'Unresolved; never replace with NO.',
            'initial_checks':'Never recompute/replace initial G6/G2 as post-adjudication gates or claim accuracy qualification.'},
        original_agreement={k:initial[k] for k in ['paired_physical_lines','G6','G2']},
        timing_exception=initial['timing_exception'],coordinate_control_limit=initial['coordinate_control_limit'],
        retained='Original responses, invalid boxes, runtime failures, recovery provenance, G6/G2 and all dropped registration blocks remain in their original sealed records.',
        held=['third-rater execution','adjudication application','OT merge','support','scientific controls','outcome joins','H-IMG/H-PLANT tests','geometry changes'],v103='PARKED')
    save(D/'PREPARATION.json',protocol)
    (D/'README.txt').write_text(
        'Blind adjudication preparation only; no third ratings collected.\n'
        f'{len(queue)} target physical lines: 194 six-way disagreements (118 also binary), 233 unpaired.\n'
        f'Whole-page picture annotation queue: {len(public)} pages.\n'
        f'Unpaired breakdown: {dict(breakdown)}\n'
        'Give a fresh rater ONLY rater-only/ or rater-only.zip. All other files are analyst-private.\n'
        'The rater annotates every picture on each selected full page; no writing or dispute locations.\n'
        'For a model, supply only MANUAL-MODEL.md plus one image per isolated call; TASKS and UI are for dispatch, not model prompt additions.\n'
        'Initial G6=.7005823251 and G2=.7358105189 are agreement checks on 912 pairs only.\n'
        'Original full-coverage gate remains NOT ESTIMABLE; C cannot reconstruct original A/B coverage.\n'
        'Resolution policy is a draft in PREPARATION.json; no decisions applied.\n'
        'TIMING EXCEPTION: v4.2 was not frozen before initial registration; retained 45-line exception persists.\n'
        'Synthetic coordinate failures remain; agreement does not establish coordinate accuracy.\n'
        'All dropped blocks and original evidence retained. v103 PARKED.\n',encoding='utf-8')
    with zipfile.ZipFile(D/'rater-only.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(packet.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(packet))
    allowed={'MANUAL.md','MANUAL-MODEL.md','TASKS.json','index.html'} | {t['image'] for t in public}
    actual={p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file()}
    assert actual==allowed
    assert all(set(t)=={'task_id','image','native_width','native_height'} for t in public)
    assert len(set(t['task_id'] for t in public))==len(public)
    # No private labels, original task IDs, source locators or geometry in text payloads.
    for p in packet.iterdir():
        if p.is_file():
            text=p.read_text(encoding='utf-8')
            assert all(tid not in text for tid in tasks)
            assert all(l['shared_line_id'] not in text for l in geom)
    assert verify_initial()==checked
    save(D/'VERIFICATION.json',dict(status='PASS: PACKET PREPARATION ONLY',
        original_sealed_files_verified=checked,original_geometry_unchanged=True,
        original_ratings_and_checks_unchanged=True,target_union_verified=True,
        packet_allowlist_verified=True,images_byte_identical=True,
        original_task_and_line_ids_absent_from_packet_text=True,
        blinding_limit='Source page pixels naturally retain manuscript writing and visual identifiers; selected page subset may reveal selection occurred. No transcription or analyst annotations added.',
        new_model_calls=0,third_ratings=0,adjudication_applied=False,
        timing_exception=initial['timing_exception'],v103='PARKED'))
    shutil.copyfile(Path(__file__),D/'prepare_adjudication.py')
    save(D/'PREPARATION-SEAL.json',{p.relative_to(D).as_posix():sha(p)
         for p in sorted(D.rglob('*')) if p.is_file()})
    print(json.dumps(dict(target_lines=len(queue),reason_counts=dict(breakdown),
                         pages=len(public),original_files_verified=checked,status='PREPARED; NOT RUN')))

if __name__=='__main__':main()
