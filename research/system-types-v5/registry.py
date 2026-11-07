"""Candidate entry point: G5 always means the unmodified published implementation.

GENERATORS.generate('G5') is retained ONLY as the archived-development surrogate.
This registry never selects it. Layout conventions still require a claim freeze.
"""
import re
from core import group_rank_mapping, render_groups, canonical_hash
from GENERATORS import generate
from published_g5 import run_published

def produce(family,params,seed,source_words=None,inventory=None,line_lengths=None,line_count=100):
    if family=='G5':
        if line_lengths is not None:
            raise ValueError('published G5 uses native character-count layout; do not force target token counts')
        name='registry-'+canonical_hash(dict(params=params,seed=seed,lines=line_count))[:20]
        upstream=run_published(name,seed=seed,lines=line_count,overrides=params)
        lines=[line.split() for line in upstream['raw'].splitlines() if line.strip() and not line.startswith('#')]
        if len(lines)!=line_count or not all(re.fullmatch('[a-z]+',w) for line in lines for w in line):
            raise ValueError('published output parser failed')
        return dict(family=family,lines=lines[1:],initial_seed_line=lines[0],seed_line_excluded=True,
                    requested_native_lines=line_count,layout='published native character-count',published_source=True,source_output=upstream['path'])
    if line_lengths is None:raise ValueError('explicit development geometry required for G1–G4/G6')
    if family in ('G1','G2','G3','G4'):
        if source_words is None or sum(line_lengths)>len(source_words):
            raise ValueError('SOURCE_TOO_SHORT: original-slot budget exceeds source, before generator invocation')
        if params.get('allow_source_wrap',False):raise ValueError('source wrapping is forbidden in the candidate registry')
        params=dict(params,allow_source_wrap=False)
    g=generate(family,params,seed,source=source_words,line_lengths=line_lengths)
    if family=='G6':
        return dict(family=family,lines=[[''.join(w) for w in line] for line in g['lines']],
                    mechanism=g,layout='supplied development token counts')
    if inventory is None:raise ValueError('registered EVA-group inventory required')
    words=[w for line in g['lines'] for w in line]
    receipt=group_rank_mapping(words,inventory,max_width=g['max_expansion'] if family=='G4' else 3)
    rendered=render_groups(words,receipt)
    lines=[];cursor=0
    for length in line_lengths:
        lines.append(rendered['words'][cursor:cursor+length]);cursor+=length
    return dict(family=family,lines=lines,mapping=receipt,source_unit_groups=words,source_offset=g['source_offset'],source_wraps=g['source_wraps'],
                mapped_unit_groups=rendered['mapped_unit_groups'],layout='supplied development token counts')
