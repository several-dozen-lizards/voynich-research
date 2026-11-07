"""Six runnable sandbox mechanisms; historical fidelity is separately gated."""
from collections import deque
import random

FAMILIES = ('G1', 'G2', 'G3', 'G4', 'G5', 'G6')

def source_units(words):
    return [list(word) for word in words]

def abbreviate(words, rng, probability):
    # Sourced rule types; probabilities are model parameters, not historical rates.
    result = []
    for word in words:
        units = list(word)
        for ending, replacement in (('que', ['q', '<SEMICOLON>']), ('rum', ['<RUM>']), ('us', ['<SUP9>']), ('um', ['u', '<NASAL>']), ('em', ['e', '<NASAL>']), ('am', ['a', '<NASAL>'])):
            if word.endswith(ending) and len(word) > len(ending) and rng.random() < probability:
                units = list(word[:-len(ending)]) + replacement
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
            symbols = params.get('symbols', {'et': '<TIRONIAN_ET>'})
            for i, word in enumerate(words):
                if word in symbols and rng.random() < params.get('symbol_probability', .5):
                    # Explicit context variant; no semantics inferred in generated EVA.
                    variant = ':after-vowel' if i and words[i-1][-1] in 'aeiou' else ':other'
                    output[i] = [symbols[word] + (variant if params.get('context_variants', True) else '')]
        if family == 'G4':
            widths = {c:rng.randint(1, params.get('max_expansion', 3)) for c in sorted(set(''.join(words)))}
            cipher_widths = {}
            output = []
            for word in words:
                units = []
                for i, c in enumerate(word):
                    cls = 'I' if i == 0 else 'F' if i == len(word)-1 else 'M'
                    group = f'<CIPHER:{c}:{cls if params.get("position_variants", True) else "FREE"}>'
                    cipher_widths[group] = widths[c]
                    units.append(group)
                    if rng.random() < params.get('null_probability', .05):
                        units.append('<NULL>')
                        cipher_widths['<NULL>'] = 1
                output.append(units)
        lines, start = [], 0
        for length in line_lengths:
            lines.append(output[start:start+length])
            start += length
        return dict(lines=lines, lineage=lineage, source_offset=offset, source_wraps=(offset+count-1)//len(source),
                    cipher_widths=cipher_widths if family == 'G4' else {},
                    fixture_only=False, historical_source_qualified=False, layout='supplied engineering geometry')
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
    # Rugg-style repeated three-column blocks, shifted rows and an explicit grille.
    prefix = params.get('prefix', ['', 'qo', 'ch', 'sh'])
    middle = params.get('middle', ['e', 'ee', 'ok', 'ai'])
    suffix = params.get('suffix', ['y', 'dy', 'in', 'ol'])
    tables = [prefix, middle, suffix]
    if any(not column for column in tables):
        raise ValueError('empty grille column')
    offsets = params.get('grille_offsets', [0, 1, -1])
    if len(offsets) != 3:
        raise ValueError('three grille holes required')
    depth = int(params.get('table_rows', 40))
    blocks = int(params.get('table_blocks', 8))
    table = params.get('table')
    if table is None:
        table = [[rng.choice(column) for _ in range(blocks) for column in tables] for _ in range(depth)]
    depth = len(table)
    if not depth or len(table[0]) % 3 or any(len(r) != len(table[0]) for r in table):
        raise ValueError('rectangular table with repeated prefix/root/suffix triples required')
    blocks = len(table[0])//3
    lo, hi = -min(0, *offsets), depth-1-max(0,*offsets)
    if lo > hi: raise ValueError('grille cannot fit table')
    row = rng.randint(lo,hi)
    block = 0
    draws = []
    lines = []
    for length in line_lengths:
        line = []
        while len(line) < length:
            coordinates = [(row+delta,3*block+i) for i,delta in enumerate(offsets)]
            word = ''.join(table[r][c] for r,c in coordinates)
            draws.append(dict(row=row,block=block,coordinates=coordinates,word=word,emitted=bool(word)))
            if word: line.append(list(word))
            if len(draws) > sum(line_lengths)*100:
                raise ValueError('grille mostly empty; exhausted registered draw budget')
            block += 1
            if block == blocks:
                block = 0
                row = rng.randint(lo,hi)
            else:
                candidate = row+rng.choice(params.get('row_steps',[-2,-1,0,1,2]))
                row = candidate if lo<=candidate<=hi else rng.randint(lo,hi)
        lines.append(line)
    return dict(lines=lines, lineage=[], fixture_only=False, table=table, grille_offsets=offsets,draws=draws,
                fidelity='Rugg-style parametric repeated-column table/grille; movement policy explicit, not a unique historical reconstruction')
