"""Sandbox primitives. No manuscript or output is read at import time."""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import hashlib
import json
import math
import random
import re
import numpy as np

RESERVED = frozenset(('f72v1', 'f72v2', 'f73r', 'f73v'))
EXPECTED_EVT = '309e717d0dcc13115eace006eb40ece6c0ac89faab48f1569dcb9732d26b02f0'
EXPECTED_HANDS = 'af08e1dedecc791ba8dafe8b556133172e8b7acfdfdfcd2d1ef38708a680914f'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()).hexdigest()

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')

def tokens(text):
    # Attempt C policy. Unknown original slots remain barriers.
    text = re.sub(r'\{[^}]*\}', '', text.split('#')[0])
    text = re.sub(r'[!\s]', '', text)
    return [w if re.fullmatch('[a-z]+', w) else None for w in re.split(r'[.,=\-]', text) if w]

def load_evt(source, metadata, verify_hashes=True):
    if verify_hashes and (sha(source) != EXPECTED_EVT or sha(metadata) != EXPECTED_HANDS):
        raise ValueError('source version mismatch; a new robustness run is required')
    with Path(metadata).open(encoding='utf-8-sig', newline='') as stream:
        hands = {row['Folio']: row for row in csv.DictReader(stream)}
    rows, excluded, rejected, seen = [], Counter(), Counter(), set()
    for raw in Path(source).read_text(encoding='latin1').splitlines():
        match = re.match(r'^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>\s*(.*)', raw)
        if not match:
            continue
        page, place, number, reading, text = match.groups()
        # Exclude before tokenization, metadata join, or any statistical extraction.
        if page in RESERVED:
            excluded[reading] += 1
            continue
        if reading not in ('H', 'F') or not place.startswith('P'):
            continue
        key = (reading, page, place, number)
        if key in seen:
            raise ValueError(('duplicate source locus', key))
        seen.add(key)
        info = hands.get(page, {})
        if info.get('Language') not in ('A', 'B') or info.get('Scribe') not in ('1', '2', '3', '4', '5'):
            rejected[(reading, info.get('Language', '?'), info.get('Scribe', '?'))] += 1
            continue
        rows.append(dict(reading=reading, folio=page, locus=f'{page}.{place}.{number}',
                         place=place, number=number, currier=info['Language'], scribe=info['Scribe'],
                         section=info['Section'], tokens=tokens(text),
                         paragraph_end='=' in text.split('#')[0]))
    if any(row['folio'] in RESERVED for row in rows):
        raise AssertionError('reserved folio escaped exclusion')
    policy = dict(reserved=sorted(RESERVED), scope='H/F separate; P loci; exact A/B and scribe1..5; attempt-C tokenizer')
    manifest = dict(source_sha256=sha(source), metadata_sha256=sha(metadata), policy=policy,
                    policy_sha256=canonical_hash(policy), retained_rows_sha256=canonical_hash(rows),
                    excluded_reserved_rows_by_reading=dict(excluded),
                    rejected_metadata_rows={str(k): v for k, v in rejected.items()},
                    no_reserved_rows_retained=True)
    return rows, manifest

def panels(rows):
    result = defaultdict(list)
    for row in rows:
        result[(row['currier'], row['scribe'], row['reading'])].append(row)
    return dict(result)

def position(index, length):
    # Singletons are free, never silently counted twice as initial and final.
    return 'free' if length == 1 else 'initial' if index == 0 else 'final' if index == length - 1 else 'medial'

def unit_profile(words):
    counts = Counter()
    locations = defaultdict(Counter)
    for word in words:
        for i, unit in enumerate(word):
            counts[unit] += 1
            locations[unit][position(i, len(word))] += 1
    classes = {}
    for unit, distribution in locations.items():
        top = max(distribution, key=lambda p: (distribution[p], p))
        classes[unit] = top if distribution[top] / counts[unit] >= .95 else 'free'
    return counts, locations, classes

def rank_mapping(source_words, target_words, seed=51024):
    """Draft rank map; strict injection. Insufficient target class capacity abstains."""
    sc, _, sx = unit_profile(source_words)
    tc, _, tx = unit_profile(target_words)
    tie = lambda x: hashlib.sha256(f'{seed}:{x}'.encode()).hexdigest()
    mapping = {}
    for cls in ('initial', 'medial', 'final', 'free'):
        source = sorted((u for u in sc if sx[u] == cls), key=lambda u: (-sc[u], tie(u)))
        target = sorted((u for u in tc if tx[u] == cls), key=lambda u: (-tc[u], tie(u)))
        if len(source) > len(target):
            raise ValueError(f'mapping class {cls}: {len(source)} source units, {len(target)} target units; group inventory unresolved')
        mapping.update(zip(source, target))
    return dict(mapping=mapping, seed=seed, threshold=.95, source_classes=sx, target_classes=tx,
                collision_free=len(set(mapping.values())) == len(mapping))

def apply_mapping(words, receipt):
    return [''.join(receipt['mapping'][unit] for unit in word) for word in words]

def fit_summary(lines, alphabet=None, max_word_length=30, max_line_words=40):
    """Only S_fit. Word-internal bigrams; length/line tails kept in overflow bins."""
    words = [w for line in lines for w in line if w]
    if not words:
        raise ValueError('empty panel')
    alphabet = tuple(sorted(set(''.join(words)))) if alphabet is None else tuple(alphabet)
    extra = set(''.join(words)) - set(alphabet)
    if extra:
        raise ValueError(('unregistered glyphs', sorted(extra)))
    n = len(words)
    glyphs = Counter(''.join(words))
    lengths = Counter(min(len(w), max_word_length + 1) for w in words)
    line_lengths = Counter(min(len(line), max_line_words + 1) for line in lines)
    bigrams = Counter(pair for word in words for pair in zip(word, word[1:]))
    lefts = Counter()
    for (a, b), count in bigrams.items():
        lefts[a] += count
    total_bigrams = sum(bigrams.values())
    entropy = -sum(count / total_bigrams * math.log2(count / lefts[a]) for (a, b), count in bigrams.items()) if total_bigrams else 0.
    _, loc, _ = unit_profile(words)
    out = {f'word_length:{i}': lengths[i] / n for i in range(1, max_word_length + 2)}
    out.update({f'glyph:{c}': glyphs[c] / sum(glyphs.values()) for c in alphabet})
    out['bigram_conditional_entropy'] = entropy
    for fraction in (.1, .25, .5, .75, 1.):
        stop = max(1, int(n * fraction))
        out[f'type_growth:{fraction}'] = len(set(words[:stop])) / stop
    out.update({f'line_words:{i}': line_lengths[i] / len(lines) for i in range(max_line_words + 2)})
    for c in alphabet:
        for cls in ('initial', 'medial', 'final', 'free'):
            out[f'position:{c}:{cls}'] = loc[c][cls] / glyphs[c] if glyphs[c] else 0.
    return out

def bootstrap_fit(rows, repeats=100, seed=52024):
    pages = defaultdict(list)
    for row in rows:
        pages[row['folio']].append(row['tokens'])
    if len(pages) < 2:
        raise ValueError('need at least two pages for bootstrap scaling')
    names = sorted(pages)
    lines = [row['tokens'] for row in rows]
    target = fit_summary(lines)
    alphabet = sorted(set(''.join(w for line in lines for w in line if w)))
    rng = random.Random(seed)
    draws = []
    for _ in range(repeats):
        sample = [line for name in rng.choices(names, k=len(names)) for line in pages[name]]
        draws.append(list(fit_summary(sample, alphabet).values()))
    sd = np.std(np.asarray(draws), axis=0, ddof=1)
    return dict(target=target, bootstrap_sd=dict(zip(target, map(float, sd))), pages=len(pages),
                repeats=repeats, seed=seed, zero_sd=[k for k, s in zip(target, sd) if s == 0])

def fit_distance(observed, reference):
    target, sd = reference['target'], reference['bootstrap_sd']
    if observed.keys() != target.keys():
        raise ValueError('summary schema mismatch')
    distance = 0.
    for key in target:
        delta = observed[key] - target[key]
        if sd[key] == 0:
            if abs(delta) > 1e-12:
                return math.inf
        else:
            distance += (delta / sd[key]) ** 2
    return math.sqrt(distance)
