"""Six runnable sandbox mechanisms; historical fidelity is separately gated."""
from collections import deque
import random

FAMILIES = ('G1', 'G2', 'G3', 'G4', 'G5', 'G6')

def source_units(words):
    return [list(word) for word in words]

def abbreviate(words, rng, probability):
    # Engineering rules ONLY, pending a sourced diplomatic/Cappelli inventory.
    result = []
    for word in words:
        units = list(word)
        for ending, mark in (('que', '<QUE>'), ('rum', '<RUM>'), ('us', '<US>'), ('um', '<UM>')):
            if word.endswith(ending) and len(word) > len(ending) and rng.random() < probability:
                units = list(word[:-len(ending)]) + [mark]
                break
        result.append(units)
    return result

def generate(family, params, seed, source=None, line_lengths=(8,) * 100):
    """Return unit words per line, plus genealogy. Fixture != qualified family."""
    if family not in FAMILIES:
        raise ValueError(family)
    if not line_lengths or min(line_lengths) < 1:
        raise ValueError('positive line lengths required')
    rng = random.Random(seed)
    count = sum(line_lengths)
    lineage = []
    if family in ('G1', 'G2', 'G3', 'G4'):
        if not source:
            raise ValueError('natural-language source required')
        offset = rng.randrange(len(source))
        words = [source[(offset + i) % len(source)] for i in range(count)]
        output = abbreviate(words, rng, params.get('abbreviation_probability', .5)) if family in ('G2', 'G3') else source_units(words)
        if family == 'G3':
            symbols = params.get('symbols', {'et': '<AND>', 'recipe': '<TAKE>', 'eius': '<OF_IT>'})
            for i, word in enumerate(words):
                if word in symbols and rng.random() < params.get('symbol_probability', .5):
                    # Explicit context variant; no semantics inferred in generated EVA.
                    variant = ':after-vowel' if i and words[i-1][-1] in 'aeiou' else ':other'
                    output[i] = [symbols[word] + (variant if params.get('context_variants', True) else '')]
        if family == 'G4':
            groups = {c: [f'{c}:{j}' for j in range(rng.randint(1, params.get('max_expansion', 3)))] for c in sorted(set(''.join(words)))}
            output = []
            for word in words:
                units = []
                for i, c in enumerate(word):
                    cls = 'I' if i == 0 else 'F' if i == len(word)-1 else 'M'
                    units.extend(g + (':' + cls if params.get('position_variants', True) else '') for g in groups[c])
                    if rng.random() < params.get('null_probability', .05):
                        units.append('<NULL>')
                output.append(units)
        lines, start = [], 0
        for length in line_lengths:
            lines.append(output[start:start+length])
            start += length
        return dict(lines=lines, lineage=lineage, source_offset=offset, source_wraps=(offset+count-1)//len(source),
                    fixture_only=family in ('G2', 'G3'), layout='supplied engineering geometry')
    if family == 'G5':
        # Transparent surrogate, NOT the published Timm-Schinner algorithm.
        window = int(params.get('window_lines', 3))
        if window < 1:
            raise ValueError('window_lines must be positive')
        recent = deque(maxlen=window)
        seeds = params.get('seed_words', ['chedy', 'qokedy', 'daiin', 'ol'])
        alphabet = params.get('alphabet', 'adeikloqrsty')
        lines = []
        for li, length in enumerate(line_lengths):
            candidates = [(pi, wi, w) for pi, line in recent for wi, w in enumerate(line)]
            line = []
            for wi in range(length):
                if candidates:
                    pi, pj, parent = rng.choice(candidates)
                else:
                    pi, pj, parent = None, None, rng.choice(seeds)
                word = list(parent)
                if rng.random() < params.get('mutation_probability', .6):
                    action = rng.choice(('insert', 'delete', 'replace'))
                    at = rng.randrange(len(word))
                    if action == 'insert': word.insert(at, rng.choice(alphabet))
                    elif action == 'delete' and len(word) > 1: word.pop(at)
                    else: word[at] = rng.choice(alphabet)
                child = ''.join(word)
                line.append(child)
                lineage.append(dict(line=li, word=wi, parent_line=pi, parent_word=pj, parent=parent, child=child))
            lines.append(line)
            recent.append((li, line))
        return dict(lines=[[list(w) for w in line] for line in lines], lineage=lineage, fixture_only=True,
                    fidelity='copy-modify surrogate; published implementation not yet integrated')
    # Parametric three-column grille with offsets; not independent slot draws.
    prefix = params.get('prefix', ['', 'qo', 'ch', 'sh'])
    middle = params.get('middle', ['e', 'ee', 'ok', 'ai'])
    suffix = params.get('suffix', ['y', 'dy', 'in', 'ol'])
    tables = [prefix, middle, suffix]
    if any(not column for column in tables):
        raise ValueError('empty grille column')
    offsets = params.get('grille_offsets', [0, 1, 2])
    if len(offsets) != 3:
        raise ValueError('three grille holes required')
    size = max(map(len, tables))
    row = rng.randrange(size)
    lines = []
    for length in line_lengths:
        line = []
        for _ in range(length):
            row = (row + rng.randint(1, params.get('max_step', 3))) % size
            word = ''.join(column[(row+delta) % len(column)] for column, delta in zip(tables, offsets))
            if not word:
                raise ValueError('grille produced empty word')
            line.append(list(word))
        lines.append(line)
    return dict(lines=lines, lineage=[], fixture_only=True, fidelity='three-column grille prototype; table priors pending')
