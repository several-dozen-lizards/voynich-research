"""Read-only audit of the registered result. Does not rerun calibration or fit models."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
OUT = LAB/'results/ringdir/phase0_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def readcsv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def lines(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]


def main():
    registration = load(HERE/'registration_v1/REGISTRATION.json')
    for name, expected in registration['sha256'].items():
        assert sha(LAB/name)==expected, name
    for name, expected in load(OUT/'ARTIFACT_MANIFEST.json')['sha256'].items():
        assert sha(OUT/name)==expected, name
    events = lines(OUT/'events.jsonl')
    sealed = next(i for i,e in enumerate(events) if e['event']=='KEY_SEALED')
    scored = next(i for i,e in enumerate(events) if e['event']=='SCORES_SAVED')
    opened = next(i for i,e in enumerate(events) if e['event']=='KEY_OPENED')
    assert sealed < scored < opened
    assert events[sealed]['sha256']==sha(OUT/'sealed/keys.json')
    assert events[scored]['sha256']==sha(OUT/'direction_scores.jsonl')
    assert registration['utc'] < events[0]['utc']
    key = {k['id']:k for k in load(OUT/'sealed/keys.json')['direction']}
    stimuli = {s['id']:s for s in lines(OUT/'stimuli.jsonl')}
    scores = {s['id']:s for s in lines(OUT/'direction_scores.jsonl')}
    assert set(key)==set(stimuli)==set(scores)
    ledger = readcsv(OUT/'paragraph_eligibility.csv')
    eligible = {r['locus_id']:r for r in ledger if r['eligible']=='True'}
    source = readcsv(LAB/'data/voynich/ZL_lines_corrected.csv')
    windows = {}
    bypage = defaultdict(list)
    for r in source:
        if r['line_id'] in eligible:
            bypage[r['folio']].append(r)
    for page, rows in bypage.items():
        for i,r in enumerate(rows):
            tail = r['text_eva'].split()
            previous = r
            for nxt in rows[i+1:]:
                if (nxt['is_para_start']=='True' or
                    int(nxt['line_index_in_paragraph']) != int(previous['line_index_in_paragraph'])+1):
                    break
                tail.extend(nxt['text_eva'].split())
                previous = nxt
            windows[r['line_id']] = tail
    latin = [w for r in readcsv(LAB/'data/controls/C1/clean.csv') for w in r['text_eva'].split()]
    models = {corpus:{(r['a'],r['b']):int(r['count']) for r in readcsv(OUT/(corpus+'_direction_model.csv'))}
              for corpus in ['ZL','Latin']}
    correct = {}
    for cid,k in key.items():
        s, score = stimuli[cid], scores[cid]
        assert len(s['words'])==k['n']
        if k['corpus']=='ZL':
            assert eligible[k['source']]['split']=='heldout'
            original = windows[k['source']][:k['n']]
        else:
            start = int(k['source'].split(':')[1])
            original = latin[start:start+k['n']]
        transformed = list(reversed(original)) if k['reverse'] else original[:]
        rot = k['rotate']
        assert (k['kind']=='circular' or rot==0)
        assert transformed[rot:]+transformed[:rot]==s['words'], cid
        w = s['words']
        pairs = list(zip(w,w[1:]))
        if k['kind']=='circular' and len(w)>1:
            pairs += [(w[-1],w[0])]
        model = models[k['corpus']]
        expected = (sum(math.log(model.get((a,b),0)+.5)-math.log(model.get((b,a),0)+.5)
                        for a,b in pairs)/len(pairs)) if pairs else 0.
        assert abs(expected-score['score'])<1e-10, cid
        predicted = 0 if abs(expected)<=1e-12 else (1 if expected>0 else -1)
        correct[cid] = int(predicted==(-1 if k['reverse'] else 1))
    for r in readcsv(OUT/'direction_bins.csv'):
        selected = [k for k in key.values() if k['corpus']==r['corpus'] and k['kind']==r['kind']
                    and str(k['bin'])==r['bin']]
        assert len(selected)==int(r['n'])
        assert abs(sum(correct[k['id']] for k in selected)/len(selected)-float(r['accuracy']))<1e-12
        passed = (int(r['distinct_windows'])>=30 and int(r['families'])>=8 and
                  float(r['accuracy'])>=.8 and float(r['ci_lower'])>=.65)
        assert passed==(r['passed']=='True')
    status = load(OUT/'STATUS.json')
    assert status['real_ring_scores_computed'] is False
    assert status['phases_1_to_4_run'] is False and status['corrected_order_generated'] is False
    if status['stopped_at']=='direction':
        assert any(not g['passed'] for g in status['gates'])
        assert all(status['phase_stages'][s]=='NOT_RUN' for s in
                   ['unit_mirror','any_boundary','unique_origin','boundary_pairing_null'])
        assert not any((OUT/(s+'_scores.jsonl')).exists() for s in
                       ['mirror','any_boundary','unique_origin'])
        assert events[-1]['event']=='STOP'
    result = dict(status='PASS', trials_verified=len(key),
                  checks=['registered instrument/input hashes', 'all final artifact hashes',
                          'registration before run and sealed-key/score-before-open chronology',
                          'independent reconstruction of every trial and reverse/rotation flag',
                          'independent direction arithmetic for every trial',
                          'bin accuracies/thresholds', 'stop-state/later-stage closure'])
    (OUT/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':
    main()
