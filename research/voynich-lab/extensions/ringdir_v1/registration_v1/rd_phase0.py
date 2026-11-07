"""Registered RD-v1 calibration. No real C/R text is loaded or scored."""
import argparse
import csv
import hashlib
import json
import math
import platform
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
REG = HERE / 'registration_v1'
OUT = LAB / 'results' / 'ringdir' / 'phase0_v1'
SEED = 2026110601
BINS = [(1, 2), (3, 5), (6, 10), (11, 20), (21, 40), (41, 80), (81, 160), (161, 1000000)]
CLUSTERS = sorted('ch sh cth ckh cph cfh ii iii in iin aiin qo ee'.split(), key=lambda x: (-len(x), x))
INPUTS = ['data/voynich/ZL_lines_corrected.csv', 'data/raw/ZL3b-n.txt',
          'data/raw/LSI_ivtff_0d.txt', 'data/controls/C1/clean.csv',
          'data/controls/C1/metadata.json', 'configs/phase0.json',
          'results/ringdir/preflight/ring_inventory.csv']
INSTRUMENTS = ['RD_AMENDED.md', 'rd_phase0.py', 'test_rd_phase0.py', 'verify_rd_phase0.py']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def readcsv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def table(path, rows):
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def jsonlines(path, rows):
    with path.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def loadlines(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]


def event(kind, **details):
    value = dict(event=kind, utc=datetime.now(timezone.utc).isoformat(), **details)
    with (OUT / 'events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(value) + '\n')


def stable(value):
    return int(hashlib.sha256(value.encode()).hexdigest()[:8], 16)


def family(folio):
    if folio == 'fRos' or re.match(r'^f(?:85|86)[rv]', folio):
        return 'rosettes'
    return re.match(r'^f(\d+)', folio)[1]


def binof(n):
    return next(i for i, (a, b) in enumerate(BINS) if a <= n <= b)


def units(word):
    result, i = [], 0
    while i < len(word):
        unit = next((x for x in CLUSTERS if word.startswith(x, i)), word[i])
        result.append(unit)
        i += len(unit)
    return result


def mirror(word):
    return ''.join(reversed(units(word)))


def fit_dir(runs):
    counts = Counter()
    for run in runs:
        words = [w for line in run for w in line['words']]
        counts.update(zip(words, words[1:]))
    return counts


def direction(words, counts, kind):
    pairs = list(zip(words, words[1:]))
    if kind == 'circular' and len(words) > 1:
        pairs.append((words[-1], words[0]))
    if not pairs:
        return 0., 0.
    score = sum(math.log((counts[a, b] + .5) / (counts[b, a] + .5)) for a, b in pairs) / len(pairs)
    return score, sum(bool(counts[a, b] or counts[b, a]) for a, b in pairs) / len(pairs)


def sign(x):
    return 0 if abs(x) <= 1e-12 else (1 if x > 0 else -1)


def features(word):
    text = '^' + word + '$'
    f = Counter('g' + str(n) + ':' + text[i:i+n]
                for n in (1, 2, 3) for i in range(len(text)-n+1))
    f.update(['length:' + str(len(word)), 'initial:' + word[0], 'final:' + word[-1]])
    return f


def fit_pos(lines):
    counts, totals, classes, positions = [Counter() for _ in range(3)], [0]*3, [0]*3, [0.]*3
    vocab = set()
    for line in lines:
        words = line['words']
        if len(words) < 3:
            continue
        for i, w in enumerate(words):
            c = 0 if i == 0 else (2 if i == len(words)-1 else 1)
            f = features(w)
            counts[c].update(f)
            totals[c] += sum(f.values())
            classes[c] += 1
            positions[c] += i / (len(words)-1)
            vocab.update(f)
    assert all(classes), 'Position training lacks required classes'
    return dict(counts=counts, totals=totals, classes=classes, vocab=vocab,
                means=[positions[i]/classes[i] for i in range(3)])


def predict_pos(word, model):
    f, v = features(word), len(model['vocab'])
    scores = [math.log(model['classes'][c]/sum(model['classes'])) +
              sum(n * math.log((model['counts'][c][k]+.5)/(model['totals'][c]+.5*v))
                  for k, n in f.items() if k in model['vocab']) for c in range(3)]
    p = [math.exp(x-max(scores)) for x in scores]
    p = [x/sum(p) for x in p]
    return p, sum(a*b for a, b in zip(p, model['means']))


def fit_internal(lines):
    counts = [Counter() for _ in range(3)]
    vocab = set()
    for line in lines:
        for word in line['words']:
            u = units(word)
            if len(u) < 2:
                continue
            for i, x in enumerate(u):
                counts[0 if i == 0 else (2 if i == len(u)-1 else 1)][x] += 1
                vocab.add(x)
    return counts, vocab


def internal(words, model):
    counts, vocab = model
    values = []
    for word in words:
        u = word if isinstance(word, list) else units(word)
        if len(u) < 2:
            continue
        values.append(sum(math.log((counts[c][x]+.5)/(sum(counts[c].values())+.5*len(vocab)))
                          for i, x in enumerate(u)
                          for c in [0 if i == 0 else (2 if i == len(u)-1 else 1)]) / len(u))
    return sum(values)/len(values) if values else 0.


def bootstrap(rows, field, seed):
    groups = defaultdict(list)
    for r in rows:
        groups[r['family']].append(r[field])
    if not groups:
        return [None, None]
    values = list(groups.values())
    rng = random.Random(seed)
    samples = []
    for _ in range(2000):
        selected = [values[rng.randrange(len(values))] for _ in values]
        samples.append(sum(map(sum, selected))/sum(map(len, selected)))
    samples.sort()
    return [samples[49], samples[1949]]


def wilson(k, n):
    if not n:
        return [None, None]
    p, z = k/n, 1.959963984540054
    center = (p+z*z/(2*n))/(1+z*z/n)
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [center-half, center+half]


def binomial_p(k, n):
    return min(1., 2*sum(math.exp(math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)-n*math.log(2))
                        for i in range(min(k, n-k)+1))) if n else None


def support(rows):
    return len({(r['source'], r['n']) for r in rows}), len({r['family'] for r in rows})


def load_sources():
    inv = readcsv(LAB / INPUTS[-1])
    banned = {family(r['folio']) for r in inv}
    raw = readcsv(LAB / INPUTS[0])
    ledger, lines = [], []
    for r in raw:
        if r['locus_code'][1:] not in {'P0', 'P1', 'Pc', 'Pr', 'Pt'}:
            continue
        fam = family(r['folio'])
        reasons = []
        if fam in banned:
            reasons.append('target_folio_family')
        for field in ['is_spurious', 'has_missing_span', 'has_uncertainty']:
            if r[field] == 'True':
                reasons.append(field)
        words = r['text_eva'].split()
        if not words or any(not re.fullmatch('[a-zA-Z]+', w) for w in words):
            reasons.append('empty_or_unknown_word')
        if '<->' in r['text_raw'] or '<~>' in r['text_raw']:
            reasons.append('drawing_interruption')
        if not r['line_index_in_paragraph']:
            reasons.append('missing_paragraph_index')
        split = 'train' if stable('RD-v1-split|' + fam)/2**32 < .60 else 'heldout'
        ledger.append(dict(locus_id=r['line_id'], folio=r['folio'], family=fam, split=split,
                           eligible=not reasons, reasons=';'.join(reasons), n=len(words)))
        if not reasons:
            lines.append(dict(id=r['line_id'], folio=r['folio'], family=fam, split=split,
                              index=int(r['line_index_in_paragraph']), start=r['is_para_start']=='True',
                              words=words, scribe=r['hand_scribe'], section=r['section']))
    runs = []
    for line in lines:
        if (not runs or line['folio'] != runs[-1][-1]['folio'] or line['start'] or
                line['index'] != runs[-1][-1]['index']+1):
            runs.append([])
        runs[-1].append(line)
    latin_rows = readcsv(LAB / 'data/controls/C1/clean.csv')
    latin, offset = [], 0
    for r in latin_rows:
        assert int(r['source_word_start']) == offset
        words = r['text_eva'].split()
        assert int(r['source_word_end'])-offset == len(words)
        offset += len(words)
        latin.extend(words)
    cut = int(len(latin)*.60)
    train_latin = [[dict(words=latin[:cut])]]
    latin_runs = []
    for a in range(cut+128, len(latin), 512):
        latin_runs.append([dict(id=f'C1:{a}', folio=f'C1:{a}', family=f'C1block:{a}',
                                words=latin[a:a+512], scribe='', section='', index=0)])
    return inv, lines, runs, ledger, train_latin, latin_runs


def candidates(runs, n):
    values = []
    for run in runs:
        for j, first in enumerate(run):
            words, bounds, offset = [], [], 0
            for line in run[j:]:
                if offset > 0:
                    bounds.append(offset)
                words.extend(line['words'])
                offset += len(line['words'])
                if offset >= n:
                    if offset == n:
                        bounds.insert(0, 0)
                    break
            if len(words) >= n:
                values.append(dict(words=words[:n], boundaries=[b for b in bounds if b < n],
                                   source=first['id'], family=first['family'],
                                   scribe=first['scribe'], section=first['section']))
    return values


def make_case(candidate, case_id, kind, corpus, rng, unique=False):
    words = candidate['words'][:]
    n = len(words)
    reverse, rotate = rng.random() < .5, rng.randrange(n) if kind == 'circular' else 0
    bounds = [0] if unique else candidate['boundaries']
    if reverse:
        words.reverse()
        bounds = [(n-b) % n for b in bounds]
    words = words[rotate:] + words[:rotate]
    bounds = sorted((b-rotate) % n for b in bounds)
    stimulus = dict(id=case_id, kind=kind, corpus=corpus, words=words)
    key = dict(id=case_id, kind=kind, corpus=corpus, n=n, bin=binof(n), reverse=reverse,
               rotate=rotate, boundaries=bounds, source=candidate['source'],
               family=candidate['family'], unique=unique)
    return stimulus, key


def generate(inv, heldout, latin_runs):
    rng = random.Random(SEED)
    stimuli, keys, matches = [], [], []
    cache, use = {}, Counter()
    for corpus, runs in [('ZL', heldout), ('Latin', latin_runs)]:
        for kind in ['circular', 'radial']:
            targets = [r for r in inv if r['type'] == kind]
            for b in sorted({binof(int(r['word_count'])) for r in targets}):
                rows = [r for r in targets if binof(int(r['word_count'])) == b]
                order = []
                while len(order) < 200:
                    copy = rows[:]
                    rng.shuffle(copy)
                    order.extend(copy)
                for i, target in enumerate(order[:200]):
                    n = int(target['word_count'])
                    ck = corpus, n
                    if ck not in cache:
                        cache[ck] = candidates(runs, n)
                    pool, match = cache[ck], 'all_source_families'
                    if corpus == 'ZL':
                        for label, predicate in [
                            ('scribe+section', lambda c: c['scribe'] == target['scribe'] and c['section'] == target['section']),
                            ('scribe', lambda c: c['scribe'] == target['scribe'])]:
                            sub = [c for c in pool if predicate(c)]
                            if len({c['family'] for c in sub}) >= 8:
                                pool, match = sub, label
                                break
                    else:
                        match = 'not_applicable_Latin_source_span'
                    cid = f'{corpus}-{kind}-b{b}-{i:03d}'
                    if not pool:
                        matches.append(dict(id=cid, corpus=corpus, kind=kind, bin=b, n=n,
                                            target=target['locus_id'], match='UNAVAILABLE'))
                        continue
                    smallest = min(use[corpus, kind, c['source'], n] for c in pool)
                    c = rng.choice([c for c in pool if use[corpus, kind, c['source'], n] == smallest])
                    use[corpus, kind, c['source'], n] += 1
                    stimulus, key = make_case(c, cid, kind, corpus, rng)
                    stimuli.append(stimulus)
                    keys.append(key)
                    matches.append(dict(id=cid, corpus=corpus, kind=kind, bin=b, n=n,
                                        target=target['locus_id'], match=match,
                                        source=c['source'], family=c['family']))
    unique_stimuli, unique_keys = [], []
    occupied = {binof(int(r['word_count'])) for r in inv if r['type']=='circular'}
    complete_lines = [line for run in heldout for line in run
                      if len(line['words']) >= 6 and binof(len(line['words'])) in occupied]
    rng.shuffle(complete_lines)
    for i, line in enumerate(complete_lines):
        c = dict(words=line['words'], boundaries=[0], source=line['id'], family=line['family'])
        s, k = make_case(c, f'unique-{i:04d}', 'circular', 'ZL', rng, True)
        unique_stimuli.append(s)
        unique_keys.append(k)
    mirrored, mirror_keys = [], []
    for s, k in zip(stimuli, keys):
        if s['corpus'] == 'ZL' and rng.random() < .10:
            flipped = rng.random() < .5
            word_units = [units(w) for w in s['words']]
            mirrored.append(dict(**s, mirror_words=[list(reversed(u)) for u in word_units] if flipped else word_units))
            mirror_keys.append(dict(**k, mirrored=flipped))
    jsonlines(OUT / 'stimuli.jsonl', stimuli)
    jsonlines(OUT / 'unique_stimuli.jsonl', unique_stimuli)
    jsonlines(OUT / 'mirror_stimuli.jsonl', mirrored)
    table(OUT / 'matching_ledger.csv', matches)
    (OUT / 'sealed').mkdir()
    dump(OUT / 'sealed/keys.json', dict(direction=keys, unique=unique_keys, mirror=mirror_keys))
    event('KEY_SEALED', sha256=sha(OUT/'sealed/keys.json'), cases=len(keys), unique_cases=len(unique_keys))


def score_direction(models):
    rng = random.Random(SEED+1)
    scores = []
    for s in loadlines(OUT/'stimuli.jsonl'):
        val, coverage = direction(s['words'], models[s['corpus']], s['kind'])
        null = s['words'][:]
        rng.shuffle(null)
        nv, nc = direction(null, models[s['corpus']], s['kind'])
        scores.append(dict(id=s['id'], score=val, pair_coverage=coverage,
                           null_score=nv, null_pair_coverage=nc))
    jsonlines(OUT/'direction_scores.jsonl', scores)
    event('SCORES_SAVED', stage='direction', sha256=sha(OUT/'direction_scores.jsonl'))


def open_key(stage):
    event('KEY_OPENED', stage=stage, sha256=sha(OUT/'sealed/keys.json'))
    return json.loads((OUT/'sealed/keys.json').read_text(encoding='utf-8'))


def evaluate_direction():
    key = open_key('direction')['direction']
    scored = {r['id']: r for r in loadlines(OUT/'direction_scores.jsonl')}
    rows, cells, nullcells, gates, powered = [], [], [], [], {}
    for k in key:
        s = scored[k['id']]
        target = -1 if k['reverse'] else 1
        rows.append(dict(**k, **{x: y for x, y in s.items() if x!='id'},
                         correct=int(sign(s['score']) == target),
                         null_correct=int(sign(s['null_score']) == target),
                         tie=int(sign(s['score']) == 0), null_tie=int(sign(s['null_score']) == 0)))
    table(OUT/'direction_trials.csv', rows)
    for corpus in ['ZL', 'Latin']:
        for kind in ['circular', 'radial']:
            group = [r for r in rows if r['corpus']==corpus and r['kind']==kind]
            passing = []
            for b in sorted({r['bin'] for r in group}):
                sub = [r for r in group if r['bin']==b]
                distinct, families = support(sub)
                accuracy = sum(r['correct'] for r in sub)/len(sub)
                ci = bootstrap(sub, 'correct', SEED+stable(f'{corpus}{kind}{b}'))
                passed = distinct >= 30 and families >= 8 and accuracy >= .80 and ci[0] >= .65
                if passed:
                    passing.append(b)
                cells.append(dict(corpus=corpus, kind=kind, bin=b, length_min=BINS[b][0],
                    length_max=BINS[b][1], n=len(sub), distinct_windows=distinct, families=families,
                    accuracy=accuracy, ci_lower=ci[0], ci_upper=ci[1],
                    wilson_lower=wilson(sum(r['correct'] for r in sub), len(sub))[0],
                    ties=sum(r['tie'] for r in sub),
                    mean_pair_coverage=sum(r['pair_coverage'] for r in sub)/len(sub),
                    passed=passed, underpowered=not passed))
            informative = [r for r in group if not r['null_tie'] and
                           r['n'] >= (3 if kind=='circular' else 2)]
            nc = bootstrap(informative, 'null_correct', SEED+stable(corpus+kind+'null'))
            nf = len({r['family'] for r in informative})
            na = sum(r['null_correct'] for r in informative)/len(informative) if informative else None
            npass = (len(informative)>=100 and nf>=8 and .40 <= na <= .60 and
                     nc[0]>=.35 and nc[1]<=.65)
            nullcells.append(dict(corpus=corpus, kind=kind, non_tied_n=len(informative),
                                 families=nf, accuracy=na, ci_lower=nc[0], ci_upper=nc[1],
                                 ties_excluded=sum(r['null_tie'] for r in group),
                                 binomial_p=binomial_p(sum(r['null_correct'] for r in informative), len(informative)),
                                 passed=npass))
            powered[corpus+'_'+kind] = passing
            gates.append(dict(name=corpus+'_'+kind+'_direction', passed=bool(passing),
                              L_min=BINS[min(passing)][0] if passing else None,
                              eligible_bins=passing))
            gates.append(dict(name=corpus+'_'+kind+'_shuffle_null', passed=npass))
    table(OUT/'direction_bins.csv', cells)
    table(OUT/'direction_nulls.csv', nullcells)
    dump(OUT/'direction_gates.json', gates)
    return gates, powered


def score_mirror(lines):
    model = fit_internal(lines)
    result = []
    for s in loadlines(OUT/'mirror_stimuli.jsonl'):
        a = internal(s['mirror_words'], model)
        b = internal([list(reversed(u)) for u in s['mirror_words']], model)
        result.append(dict(id=s['id'], forward=a, reversed=b))
    jsonlines(OUT/'mirror_scores.jsonl', result)
    event('SCORES_SAVED', stage='mirror', sha256=sha(OUT/'mirror_scores.jsonl'))
    keys = {k['id']: k for k in open_key('mirror')['mirror']}
    rows = [dict(**keys[r['id']], correct=int(sign(r['forward']-r['reversed']) ==
                                             (-1 if keys[r['id']]['mirrored'] else 1))) for r in result]
    distinct, families = support(rows)
    accuracy = sum(r['correct'] for r in rows)/len(rows) if rows else 0
    table(OUT/'mirror_trials.csv', rows)
    gate = dict(name='unit_mirror', n=len(rows), distinct_windows=distinct, families=families,
                accuracy=accuracy, passed=distinct>=30 and families>=8 and accuracy>=.90)
    dump(OUT/'mirror_gate.json', gate)
    return gate


def boundary_profile(words, model):
    p = [predict_pos(w, model)[0] for w in words]
    return [[p[i][0]+p[i-1][2] for i in range(len(p))],
            [p[i-1][0]+p[i][2] for i in range(len(p))]]


def argmax_tie(values, rng):
    peak = max(values)
    return rng.choice([i for i, x in enumerate(values) if abs(x-peak)<=1e-12])


def window_union(bounds, n):
    return {(b+d)%n for b in bounds for d in range(-2, 3)}


def score_boundaries(lines, models, powered, unique=False):
    stage = 'unique_origin' if unique else 'any_boundary'
    model = fit_pos(lines)
    # Out-of-fold diagnostics only once, after direction/mirror gates open.
    if not unique:
        diagnostic = []
        for fold in range(5):
            train = [r for r in lines if stable(r['family'])%5 != fold]
            test = [r for r in lines if stable(r['family'])%5 == fold and len(r['words'])>=3]
            fitted = fit_pos(train)
            for line in test:
                for i, w in enumerate(line['words']):
                    p, pos = predict_pos(w, fitted)
                    true = 0 if i==0 else (2 if i==len(line['words'])-1 else 1)
                    diagnostic.append(dict(fold=fold, family=line['family'], source=line['id'],
                                           true_class=true, predicted=max(range(3), key=lambda c:p[c]),
                                           relative_position=i/(len(line['words'])-1), predicted_position=pos))
        table(OUT/'position_training_cv.csv', diagnostic)
    rng = random.Random(SEED+(4 if unique else 3))
    stimuli = loadlines(OUT/('unique_stimuli.jsonl' if unique else 'stimuli.jsonl'))
    scores = []
    for s in stimuli:
        if s['corpus']!='ZL' or s['kind']!='circular' or binof(len(s['words'])) not in powered['ZL_circular']:
            continue
        profiles = boundary_profile(s['words'], model)
        nullwords = s['words'][:]
        rng.shuffle(nullwords)
        nullprofiles = boundary_profile(nullwords, model)
        ds, _ = direction(s['words'], models['ZL'], 'circular')
        scores.append(dict(id=s['id'], forward_peak=argmax_tie(profiles[0], rng),
                           reverse_peak=argmax_tie(profiles[1], rng),
                           null_forward_peak=argmax_tie(nullprofiles[0], rng),
                           null_reverse_peak=argmax_tie(nullprofiles[1], rng), inferred_reverse=ds < -1e-12))
    jsonlines(OUT/(stage+'_scores.jsonl'), scores)
    event('SCORES_SAVED', stage=stage, sha256=sha(OUT/(stage+'_scores.jsonl')))
    keys = {k['id']: k for k in open_key(stage)['unique' if unique else 'direction']}
    trials = []
    for r in scores:
        k = keys[r['id']]
        if not unique and len(k['boundaries']) < 2:
            continue
        acceptable = window_union(k['boundaries'], k['n'])
        chance = len(acceptable)/k['n']
        if chance >= 1:
            continue
        picked = r['reverse_peak'] if k['reverse'] else r['forward_peak']
        predicted = r['reverse_peak'] if r['inferred_reverse'] else r['forward_peak']
        npick = r['null_reverse_peak'] if k['reverse'] else r['null_forward_peak']
        hit, e2e, nhit = int(picked in acceptable), int(predicted in acceptable), int(npick in acceptable)
        trials.append(dict(**k, chance=chance, hit=hit, end_to_end_hit=e2e, excess=hit-chance,
                           end_to_end_excess=e2e-chance, null_excess=nhit-chance))
    table(OUT/(stage+'_trials.csv'), trials)
    gates = []
    for b in powered['ZL_circular']:
        sub = [r for r in trials if r['bin']==b]
        distinct, families = support(sub)
        ex = bootstrap(sub, 'excess', SEED+10+b)
        ee = bootstrap(sub, 'end_to_end_excess', SEED+20+b)
        nu = bootstrap(sub, 'null_excess', SEED+30+b)
        rate = sum(r['hit'] for r in sub)/len(sub) if sub else 0
        erate = sum(r['end_to_end_hit'] for r in sub)/len(sub) if sub else 0
        passed = (distinct>=30 and families>=8 and rate>=.5 and erate>=.5 and
                  ex[0]>0 and ee[0]>0 and -.15<=nu[0]<=0<=nu[1]<=.15)
        gates.append(dict(name=stage, bin=b, n=len(sub), distinct_windows=distinct, families=families,
                          hit_rate=rate, end_to_end_hit_rate=erate, excess_ci=ex,
                          end_to_end_excess_ci=ee, null_excess_ci=nu, passed=passed))
    dump(OUT/(stage+'_gates.json'), gates)
    # Supported length-specific calibration is allowed, no extrapolation.
    return dict(name=stage, passed=any(g['passed'] for g in gates), bins=gates)


def boundary_pairing_null(lines, powered):
    model = fit_pos(lines)
    keys = open_key('pairing_selection')['direction']
    eligible = {k['id'] for k in keys if k['corpus']=='ZL' and k['kind']=='circular'
                and k['bin'] in powered['ZL_circular'] and len(k['boundaries'])>=2}
    stimuli = [s for s in loadlines(OUT/'stimuli.jsonl') if s['id'] in eligible][:100]
    rng = random.Random(SEED+5)
    trials = []
    for s in stimuli:
        words = s['words'][:]
        rng.shuffle(words)
        observed = max(boundary_profile(words, model)[0])
        null = []
        for _ in range(199):
            rng.shuffle(words)
            null.append(max(boundary_profile(words, model)[0]))
        p = (1+sum(x>=observed-1e-12 for x in null))/200
        trials.append(dict(id=s['id'], p=p, false_positive=p<=.05, observed=observed, null=null))
    jsonlines(OUT/'pairing_null_trials.jsonl', trials)
    rate = sum(r['false_positive'] for r in trials)/len(trials) if trials else None
    gate = dict(name='boundary_pairing_null', n=len(trials), false_positive_rate=rate,
                passed=len(trials)>=100 and rate<=.10)
    dump(OUT/'pairing_null_gate.json', gate)
    return gate


def register():
    assert not OUT.exists(), 'Run already exists'
    sources = json.loads((LAB/'configs/phase0.json').read_text())['sources']
    for source in sources:
        assert sha(LAB/'data/raw'/source['filename']) == source['sha256'], 'Raw source drift'
    REG.mkdir()  # exclusive; never replace a registration
    paths = [LAB/p for p in INPUTS] + [HERE/p for p in INSTRUMENTS]
    hashes = {str(p.relative_to(LAB)): sha(p) for p in paths}
    dump(REG/'REGISTRATION.json', dict(id='RD-v1', utc=datetime.now(timezone.utc).isoformat(),
         scope='Phase 0 only; stop first failed required gate', seed=SEED, sha256=hashes,
         python=sys.version, platform=platform.platform(),
         prior_exposure='Preflight transcript/comment exposure; no ring scores. Not historically blind.'))
    for name in INSTRUMENTS:
        (REG/name).write_bytes((HERE/name).read_bytes())
    print('REGISTERED RD-v1 before generation/fitting/scoring', flush=True)


def plots():
    sys.path.insert(0, str(LAB/'.runtime'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = readcsv(OUT/'direction_bins.csv')
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharey=True)
    for ax, (corpus, kind) in zip(axes.flat, [(c,k) for c in ['ZL','Latin'] for k in ['circular','radial']]):
        sub = [r for r in rows if r['corpus']==corpus and r['kind']==kind]
        ys = [float(r['accuracy']) for r in sub]
        lo = [float(r['ci_lower']) for r in sub]
        hi = [float(r['ci_upper']) for r in sub]
        ax.errorbar(range(len(sub)), ys, yerr=[[max(0,y-l) for y,l in zip(ys,lo)],
                                              [max(0,h-y) for y,h in zip(ys,hi)]], fmt='o', capsize=3)
        ax.axhline(.8, color='green', linestyle='--', linewidth=1)
        ax.axhline(.5, color='gray', linestyle=':', linewidth=1)
        ax.set_xticks(range(len(sub)), [r['length_min']+'–'+r['length_max'] for r in sub], rotation=30)
        ax.set_title(corpus+' '+kind)
        ax.set_ylim(-.03, 1.03)
        ax.set_ylabel('Recovery accuracy (ties wrong)')
        ax.set_xlabel('Word length bin')
    fig.suptitle('RD-v1 Phase 0 — direction calibration; 95% source-cluster bootstrap intervals')
    fig.tight_layout()
    fig.savefig(OUT/'direction_calibration.png', dpi=150)
    plt.close(fig)


def finish(gates, stopped):
    phases = ['direction', 'unit_mirror', 'any_boundary', 'unique_origin', 'boundary_pairing_null']
    status = dict(status='STOP_FAILED_GATE' if stopped else 'PHASE0_PASS',
                  stopped_at=stopped, registered='RD-v1', gates=gates,
                  phase_stages={p: ('EVALUATED' if any(g['name'].startswith(p) or
                    (p=='direction' and ('direction' in g['name'] or 'shuffle_null' in g['name'])) for g in gates)
                    else 'NOT_RUN') for p in phases}, real_ring_scores_computed=False,
                  phases_1_to_4_run=False, corrected_order_generated=False)
    dump(OUT/'STATUS.json', status)
    plots()
    text = ['# RD-v1 Phase 0', '', '| Gate | Result |', '|---|---|']
    text += [f"| {g['name']} | {'PASS' if g['passed'] else 'FAIL'} |" for g in gates]
    text += ['', '| Corpus | Geometry | Length | n | Distinct windows | Source clusters | Accuracy | Cluster 95% CI | Ties | Powered |',
             '|---|---|---|---:|---:|---:|---:|---|---:|---|']
    for r in readcsv(OUT/'direction_bins.csv'):
        text.append('| '+ ' | '.join([r['corpus'], r['kind'], r['length_min']+'–'+r['length_max'],
            r['n'],r['distinct_windows'],r['families'], f"{float(r['accuracy']):.3f}",
            f"{float(r['ci_lower']):.3f}–{float(r['ci_upper']):.3f}",r['ties'],r['passed']])+' |')
    text += ['', '| Corpus | Geometry | Shuffled non-ties | Null accuracy | Cluster 95% CI | Accepted |',
             '|---|---|---:|---:|---|---|']
    for r in readcsv(OUT/'direction_nulls.csv'):
        text.append(f"| {r['corpus']} | {r['kind']} | {r['non_tied_n']} | {r['accuracy']} | "
                    f"{r['ci_lower']}–{r['ci_upper']} | {r['passed']} |")
    text += ['', f"**{status['status']}**. Stop stage: {stopped or 'none'}.", '',
             'Only passing supported bins qualify; L_min is not permission for calls at every longer length. '
             'Nonpassing bins remain underpowered. Overlapping/repeated windows are not independent '
             'trials: intervals resample source-folio families (Latin: contiguous source-span blocks). '
             'These are marginal intervals, not simultaneous confidence bands.', '',
             'A calibration failure concerns this instrument and available source support. It does not '
             'determine whether manuscript rings are forward, reversed, line-like or have a unique start. '
             'No real ring text was scored; no later phase or corrected-order export ran.', '',
             'Protocol and input/instrument hashes: `extensions/ringdir_v1/registration_v1/REGISTRATION.json`. '
             'Key sealing and score-before-key receipts: `events.jsonl`. All failures and '
             'untouched later-stage stimuli are retained; no retuning or retry.', '',
             'The complete matching/fallback and exclusion ledgers accompany this report. Latin source '
             'blocks are not historical sections; source layout is artificial. Positions are transcription '
             'locus proxies, and fixed EVA units do not prove glyph identities. Re visual annotation remains pending.', '']
    (OUT/'report.md').write_text('\n'.join(text), encoding='utf-8')
    event('STOP' if stopped else 'COMPLETE', stage=stopped)
    manifest = {str(p.relative_to(OUT)): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
    dump(OUT/'ARTIFACT_MANIFEST.json', dict(sha256=manifest))
    print(status['status'], stopped, flush=True)


def run():
    registration = json.loads((REG/'REGISTRATION.json').read_text(encoding='utf-8'))
    for name, expected in registration['sha256'].items():
        assert sha(LAB/name)==expected, 'Registered dependency changed: '+name
    OUT.mkdir()  # exclusive; failed runs are never overwritten
    event('RUN_STARTED', registration_sha256=sha(REG/'REGISTRATION.json'))
    inv, lines, runs, ledger, train_latin, latin_runs = load_sources()
    table(OUT/'paragraph_eligibility.csv', ledger)
    table(OUT/'family_split.csv', [dict(family=f, split=s) for f,s in sorted({(l['family'],l['split']) for l in lines})])
    train = [r for r in runs if r[0]['split']=='train']
    heldout = [r for r in runs if r[0]['split']=='heldout']
    trainlines = [l for run in train for l in run]
    event('INPUT_PREPARED', train_lines=len(trainlines), heldout_lines=sum(map(len,heldout)),
          excluded=sum(not r['eligible'] for r in ledger))
    generate(inv, heldout, latin_runs)
    models = dict(ZL=fit_dir(train), Latin=fit_dir(train_latin))
    for corpus, model in models.items():
        table(OUT/(corpus+'_direction_model.csv'), [dict(a=a,b=b,count=n) for (a,b),n in sorted(model.items())])
    event('MODELS_FROZEN', ZL_sha256=sha(OUT/'ZL_direction_model.csv'),
          Latin_sha256=sha(OUT/'Latin_direction_model.csv'))
    score_direction(models)
    gates, powered = evaluate_direction()
    if not all(g['passed'] for g in gates):
        finish(gates, 'direction')
        return
    for stage, work in [
        ('unit_mirror', lambda: score_mirror(trainlines)),
        ('any_boundary', lambda: score_boundaries(trainlines, models, powered)),
        ('unique_origin', lambda: score_boundaries(trainlines, models, powered, True)),
        ('boundary_pairing_null', lambda: boundary_pairing_null(trainlines, powered))]:
        gate = work()
        gates.append(gate)
        if not gate['passed']:
            finish(gates, stage)
            return
    finish(gates, None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register','run'])
    args = parser.parse_args()
    register() if args.action=='register' else run()
