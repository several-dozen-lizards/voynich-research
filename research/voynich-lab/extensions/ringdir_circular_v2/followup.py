"""RD-C2 scoped continuation; original run is immutable and never resumed."""
import argparse
import importlib.util
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PRIOR = LAB/'results/ringdir/phase0_v1'
PRIOR_REG = LAB/'extensions/ringdir_v1/registration_v1'
REG = HERE/'registration'
OUT = LAB/'results/ringdir/circular_v2'
SEED = 2026110602
spec = importlib.util.spec_from_file_location('rd_frozen_v1', PRIOR_REG/'rd_phase0.py')
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)
# The immutable snapshot lives one directory deeper than the original module.
# Restore its data root explicitly; do not edit the frozen snapshot.
rd.LAB=LAB


def registered_paths():
    paths = set(p for p in PRIOR.rglob('*') if p.is_file())
    paths.update(p for p in PRIOR_REG.rglob('*') if p.is_file())
    old = json.loads((PRIOR_REG/'REGISTRATION.json').read_text(encoding='utf-8'))
    paths.update(LAB/p for p in old['sha256'])
    paths.update(HERE/p for p in ['PROTOCOL.md','followup.py','verify.py'])
    return sorted(paths)


def register():
    assert not OUT.exists()
    for name, expected in json.loads((PRIOR_REG/'REGISTRATION.json').read_text())['sha256'].items():
        assert rd.sha(LAB/name)==expected, name
    for name, expected in json.loads((PRIOR/'ARTIFACT_MANIFEST.json').read_text())['sha256'].items():
        assert rd.sha(PRIOR/name)==expected, name
    assert json.loads((PRIOR/'STATUS.json').read_text())['status']=='STOP_FAILED_GATE'
    assert json.loads((PRIOR/'VERIFICATION.json').read_text())['status']=='PASS'
    REG.mkdir()
    rd.dump(REG/'REGISTRATION.json', dict(id='RD-C2', utc=datetime.now(timezone.utc).isoformat(),
        seed=SEED, scope='circular 41–80 only; remaining calibration gates; stop first failure',
        sha256={str(p.relative_to(LAB)):rd.sha(p) for p in registered_paths()}, python=sys.version))
    for name in ['PROTOCOL.md','followup.py','verify.py']:
        (REG/name).write_bytes((HERE/name).read_bytes())
    print('REGISTERED RD-C2 before new generation/fitting/scoring',flush=True)


def check_registered():
    registration = json.loads((REG/'REGISTRATION.json').read_text(encoding='utf-8'))
    for name, expected in registration['sha256'].items():
        assert rd.sha(LAB/name)==expected, name


def original_words(stimulus, key):
    words, rotation = stimulus['words'][:], key['rotate']
    if rotation:
        words = words[-rotation:]+words[:-rotation]
    if key['reverse']:
        words.reverse()
    return words


def prepare():
    oldkey = json.loads((PRIOR/'sealed/keys.json').read_text(encoding='utf-8'))
    oldstimuli = {s['id']:s for s in rd.loadlines(PRIOR/'stimuli.jsonl')}
    oldunique = {s['id']:s for s in rd.loadlines(PRIOR/'unique_stimuli.jsonl')}
    rng = random.Random(SEED)
    stimuli, keys, mirrors, mirrorkeys, unique, uniquekeys, provenance = [],[],[],[],[],[],[]
    for k in oldkey['direction']:
        if k['corpus']!='ZL' or k['kind']!='circular' or not 41<=k['n']<=80:
            continue
        words = original_words(oldstimuli[k['id']],k)
        # Undo old transformed boundary coordinates before a fresh transform.
        bounds = [(b+k['rotate'])%k['n'] for b in k['boundaries']]
        if k['reverse']:
            bounds = [(k['n']-b)%k['n'] for b in bounds]
        candidate = dict(words=words, boundaries=bounds, source=k['source'],family=k['family'])
        s, nk = rd.make_case(candidate, 'C2-'+k['id'], 'circular','ZL',rng)
        stimuli.append(s)
        keys.append(nk)
        mu = [rd.units(w) for w in s['words']]
        flipped = rng.random()<.5
        mirrors.append(dict(**s,mirror_words=[list(reversed(u)) for u in mu] if flipped else mu))
        mirrorkeys.append(dict(**nk,mirrored=flipped))
        provenance.append(dict(new_id=s['id'],old_id=k['id'],source=k['source'],n=k['n'],family=k['family']))
    for k in oldkey['unique']:
        if not 41<=k['n']<=80:
            continue
        words = original_words(oldunique[k['id']],k)
        candidate = dict(words=words,boundaries=[0],source=k['source'],family=k['family'])
        s,nk = rd.make_case(candidate,'C2-'+k['id'],'circular','ZL',rng,True)
        unique.append(s)
        uniquekeys.append(nk)
    assert len(stimuli)==200
    assert len({(k['source'],k['n']) for k in keys})==200
    rd.jsonlines(OUT/'stimuli.jsonl',stimuli)
    rd.jsonlines(OUT/'mirror_stimuli.jsonl',mirrors)
    rd.jsonlines(OUT/'unique_stimuli.jsonl',unique)
    rd.table(OUT/'source_provenance.csv',provenance)
    (OUT/'sealed').mkdir()
    rd.dump(OUT/'sealed/keys.json',dict(direction=keys,mirror=mirrorkeys,unique=uniquekeys))
    rd.event('KEY_SEALED',sha256=rd.sha(OUT/'sealed/keys.json'),cases=len(keys),unique_cases=len(uniquekeys))


def finish(gates,stopped):
    check_registered()
    stages=['unit_mirror','any_boundary','unique_origin','boundary_pairing_null']
    status=dict(status='STOP_FAILED_GATE' if stopped else 'REMAINING_CIRCULAR_GATES_PASS',
        registered='RD-C2',stopped_at=stopped,gates=gates,
        phase_stages={s:'EVALUATED' if any(g['name']==s for g in gates) else 'NOT_RUN' for s in stages},
        scope=dict(type='circular',min_words=41,max_words=80),radial='HELD',prior_run='PRESERVED_STOP_FAILED_GATE',
        prior_run_hashes_unchanged=True,real_ring_scores_computed=False,phases_1_to_4_run=False,
        corrected_order_generated=False)
    rd.dump(OUT/'STATUS.json',status)
    text=['# RD-C2 circular-only calibration continuation','',
          '| Gate | Result |','|---|---|']
    text += [f"| {g['name']} | {'PASS' if g['passed'] else 'FAIL'} |" for g in gates]
    text += [f"| {s} | NOT_RUN |" for s in stages if status['phase_stages'][s]=='NOT_RUN']
    text += ['',f"**{status['status']}**; stop stage: {stopped or 'none'}.",'',
        'Scope is circular 41–80-word calibration only. Radial text remains HELD. '
        'RD-v1 remains STOP_FAILED_GATE, with every registered prior-run byte unchanged. '
        'This is a separately authorized follow-up, not a retroactive pass of RD-v1.','',
        'Direction evidence is inherited: ZL 41–80 recovery 83%, cluster 95% CI 72.6–89.6%; '
        'Latin circular direction passed at this bin. The earlier circular shuffle-null '
        'checks were pooled over lengths, not separately requalified within this bin.','']
    for g in gates:
        text += ['```json',json.dumps(g,indent=2),'```','']
    text += ['New nuisance transforms/mirror flags were sealed before new scores. All 200 '
        'scope-eligible windows were used in the dedicated mirror set, replacing an undersized '
        '10% subset by a predeclared sample-size amendment. Signals, source windows and thresholds '
        'were not tuned. Trial-level CSV/JSON and event receipts accompany the report.','',
        'Any-boundary localization and unique original-line-origin recovery remain separate. '
        'Absent complete 41–80-word single-line support is an unsupported gate, not a reason '
        'to manufacture long lines or extrapolate shorter-line results.','',
        'Calibration failure concerns the instrument/source support; it makes no finding about '
        'manuscript circle direction, starts, meanings or ring kind. No real rings were scored, '
        'no Phases 1–4 ran and no corrected transcription layer was created.','']
    (OUT/'report.md').write_text('\n'.join(text),encoding='utf-8')
    rd.event('STOP' if stopped else 'COMPLETE',stage=stopped,prior_hashes_unchanged=True)
    rd.dump(OUT/'ARTIFACT_MANIFEST.json',dict(sha256={str(p.relative_to(OUT)):rd.sha(p)
        for p in sorted(OUT.rglob('*')) if p.is_file()}))
    print(status['status'],stopped,flush=True)


def run():
    check_registered()
    OUT.mkdir()
    rd.OUT=OUT
    rd.event('RUN_STARTED',registration_sha256=rd.sha(REG/'REGISTRATION.json'))
    prepare()
    _,lines,runs,_,_,_=rd.load_sources()
    trainlines=[l for l in lines if l['split']=='train']
    models=dict(ZL=Counter_from_csv(PRIOR/'ZL_direction_model.csv'))
    rd.event('TRAINING_REUSED',lines=len(trainlines),direction_model_sha256=rd.sha(PRIOR/'ZL_direction_model.csv'))
    powered={'ZL_circular':[5]}
    gates=[]
    for stage,work in [
        ('unit_mirror',lambda:rd.score_mirror(trainlines)),
        ('any_boundary',lambda:rd.score_boundaries(trainlines,models,powered)),
        ('unique_origin',lambda:rd.score_boundaries(trainlines,models,powered,True)),
        ('boundary_pairing_null',lambda:rd.boundary_pairing_null(trainlines,powered))]:
        g=work()
        gates.append(g)
        if not g['passed']:
            finish(gates,stage)
            return
    finish(gates,None)


def Counter_from_csv(path):
    from collections import Counter
    return Counter({(r['a'],r['b']):int(r['count']) for r in rd.readcsv(path)})


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['register','run'])
    action=parser.parse_args().action
    register() if action=='register' else run()
