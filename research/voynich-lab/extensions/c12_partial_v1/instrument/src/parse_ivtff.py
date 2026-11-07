"""Local Phase 0 IVTFF intake; no statistical or model phases run here."""
import re
from pathlib import Path

UNK = '\ufffd'
LOCUS = re.compile(r'^<(?P<page>f[^.>]+)\.(?P<num>\d+[a-z]?),(?P<code>[^;>]+)(?:;(?P<t>[^>]+))?>(?P<text>.*)$')
PAGE = re.compile(r'^<(f[^.>]+)>')
SECTIONS = dict(A='astronomical', B='biological', C='cosmological', H='herbal', P='pharmaceutical', S='stars', T='text_only', Z='zodiac')
BRANCHES = {'D', 'G', 'I', 'Q', 'M'}

def clean(raw):
    """First alternate; preserve ligature components; one UNK per unreadable run/code.

    Commas are split as uncertain word spaces. Legacy ! padding is removed;
    % missing stretches become UNK and are excluded from agreement separately.
    """
    s = re.sub(r'<[-~]>', '.', raw)
    s = re.sub(r'<[^>]*>', '', s)
    while '[' in s:
        s, n = re.subn(r'\[([^\[\]]*)\]', lambda m: re.split(r'[:|]', m[1])[0], s)
        if not n:
            raise ValueError(f'Unbalanced alternatives: {raw}')
    s = re.sub(r'@\d{3};', UNK, s)
    s = s.replace('{', '').replace('}', '').replace('!', '')
    s = re.sub(r'[?%]+', UNK, s)
    s = re.sub(r'[^a-zA-Z\ufffd.,\s]', UNK, s)
    # Physical whitespace in IVTFF is formatting, not manuscript word spacing.
    s = re.sub(r'\s+', '', s)
    return re.sub(r'[.,]+', ' ', s).strip()

def logical_lines(text):
    pending, start = '', 0
    for n, line in enumerate(text.splitlines(), 1):
        line = line.rstrip()
        if pending:
            if not line.startswith('/'):
                raise ValueError(f'Invalid continuation at {n}')
            pending += line[1:]
        elif line.endswith('/') and not line.startswith('#'):
            pending, start = line, n
        else:
            yield n, line
            continue
        if pending.endswith('/'):
            pending = pending[:-1]
        else:
            yield start, pending
            pending = ''
    if pending:
        raise ValueError('Unclosed continuation')

def parse(path, corpus):
    text = Path(path).read_bytes().decode('latin-1')
    if not text.startswith('#=IVTFF Eva-'):
        raise ValueError('Expected requested EVA IVTFF source')
    old_hand = corpus == 'LSI'
    meta, page, tags, rows, indices = {}, None, {}, [], {}
    seen = set()
    for n, line in logical_lines(text):
        if not line or line.startswith('#'):
            continue
        m = LOCUS.match(line)
        if not m:
            h = PAGE.match(line)
            if not h:
                raise ValueError(f'Unparsed record {path}:{n}: {line}')
            page, tags, indices = h[1], {}, {}
            meta = dict(re.findall(r'\$([A-Z])=([^\s>])', line))
            continue
        d = m.groupdict()
        if d['page'] != page:
            raise ValueError(f'Page mismatch at {n}')
        t = d['t'] or 'ZL'
        raw = d['text'].strip()
        # Tags in an interlinear source persist within each transcriber only.
        state = tags.setdefault(t, {})
        state.update(re.findall(r'<@([A-Z])=([^>])>', raw))
        effective = {**meta, **state}
        effective = {k: v for k, v in effective.items() if v != '@'}
        key = (page, d['num'], t)
        if key in seen:
            raise ValueError(f'Duplicate locus/transcriber {key}')
        seen.add(key)
        is_p = d['code'][1:2] == 'P'
        start, end = '<%>' in raw, '<$>' in raw
        if is_p and start:
            indices[t] = 0
        elif is_p and indices.get(t) is not None:
            indices[t] += 1
        idx = indices.get(t) if is_p else None
        rows.append(dict(corpus=corpus, folio=page, line_id=f"{page}.{d['num']}",
            transcriber=t, source_line=n, locus_code=d['code'], text_raw=raw,
            text_eva=clean(raw), section=SECTIONS.get(effective.get('I')),
            section_code=effective.get('I'), currier_lang=effective.get('L'),
            hand_scribe=None if old_hand else effective.get('H'),
            currier_hand=effective.get('H') if old_hand else effective.get('C'),
            is_label=d['code'][1:2] == 'L', line_index_in_paragraph=idx,
            is_para_start=(start if is_p and (start or idx is not None) else None),
            is_para_end=(end if is_p else None),
            has_missing_span='%' in re.sub(r'<[^>]*>', '', raw),
            is_alternate_branch=t in BRANCHES, is_spurious=d['code'].startswith('!'),
            page_metadata_raw=str(meta), has_uncertainty=bool(re.search(r'[?\[]', raw))))
        # Labels/diagram loci can interrupt the file order within a paragraph.
        # They must not erase the running paragraph's explicit start marker.
        if is_p and end:
            indices[t] = None
    return rows

def edit_distance(a, b):
    """Exact bit-vector Levenshtein distance (unit insertion/deletion/substitution)."""
    if not a:
        return len(b)
    masks = {}
    for i, c in enumerate(a):
        masks[c] = masks.get(c, 0) | (1 << i)
    vp, vn, score, top = ~0, 0, len(a), 1 << (len(a)-1)
    for c in b:
        eq = masks.get(c, 0)
        x = eq | vn
        d = (((eq & vp) + vp) ^ vp) | eq
        hp, hn = vn | ~(d | vp), vp & d
        score += bool(hp & top) - bool(hn & top)
        hp = (hp << 1) | 1
        hn <<= 1
        vp, vn = hn | ~(x | hp), x & hp
    return score
