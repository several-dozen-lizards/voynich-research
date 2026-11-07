"""RD metadata intake and synthetic identifiability checks ONLY; never fit/score text."""
import csv
import hashlib
import itertools
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB))
from src.parse_ivtff import parse

OUT = LAB / 'results' / 'ringdir' / 'preflight'
TYPES = {'Cc': ('circular', 'clockwise'), 'Ca': ('circular', 'anticlockwise'),
         'Ri': ('radial', 'inwards'), 'Ro': ('radial', 'outwards')}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def synthetic_checks():
    # No manuscript-derived words, features, probabilities or fitted models.
    start = [1., 0., 0., 1., 0., 0., 1., 0., 0.]
    end = [0., 0., 1., 0., 0., 1., 0., 0., 1.]
    scores = [start[i] + end[i-1] for i in range(9)]
    peaks = [i for i, x in enumerate(scores) if x == max(scores)]
    rotation_peaks = []
    for k in range(9):
        s, e = start[k:] + start[:k], end[k:] + end[:k]
        rotation_peaks.append(max(s[i] + e[i-1] for i in range(9)))
    # Every two-word cyclic score cancels for an antisymmetric D.
    d = {('a', 'b'): 2., ('b', 'a'): -2.}
    two_cycle = d['a', 'b'] + d['b', 'a']
    # Three indistinguishable line boundaries: no unique original-start information.
    # Reverse the EVA rendering of one grouped unit to show the encoding issue.
    checks = {
        'rotation_peak_invariant': len(set(rotation_peaks)) == 1,
        'multiple_perfect_line_boundary_peaks': peaks == [0, 3, 6],
        'two_word_closed_direction_zero': two_cycle == 0.,
        'one_word_has_no_direction_pair': True,
        'short_window_chance_exceeds_one_if_uncapped': 5 / 3 > 1,
        'literal_EVA_reversal_breaks_ch_unit': 'ch'[::-1] == 'hc',
    }
    assert all(checks.values())
    # Exact additive seam-max distribution over an authored four-slot example.
    authored = [(1., 0.), (0., 1.), (.2, .1), (.3, .4)]
    maxima = [max(p[i][0] + p[i-1][1] for i in range(4))
              for p in itertools.permutations(authored)]
    return {'scope': 'authored algebraic counterexamples; NOT Phase 0 calibration',
            'checks': checks, 'seam_scores': scores, 'equal_peak_offsets': peaks,
            'maxima_under_rotations': rotation_peaks,
            'two_word_cycle_score': two_cycle,
            'authored_shuffle_maximum_distribution': dict(Counter(map(str, maxima))),
            'interpretation': 'Rotation cannot calibrate a maximum over all rotations. '
            'Word shuffles can change this maximum, but do not identify a unique original boundary.'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    config = json.loads((LAB / 'configs' / 'phase0.json').read_text())
    inventory, counts, sources = [], [], []
    for source in config['sources']:
        path = LAB / 'data' / 'raw' / source['filename']
        assert digest(path) == source['sha256'], f'Source changed: {path}'
        rows = parse(path, source['id'])
        sources.append({'corpus': source['id'], 'path': str(path), 'sha256': digest(path),
                        'parsed_records': len(rows)})
        c = Counter((r['transcriber'], r['locus_code']) for r in rows)
        counts.extend(dict(corpus=source['id'], transcriber=t, locus_code=code, n=n)
                      for (t, code), n in sorted(c.items()))
        for r in rows:
            code = r['locus_code'][1:]
            if code not in TYPES:
                continue
            kind, direction = TYPES[code]
            words = r['text_eva'].split()
            # Preserve comments without making their contents blind annotations.
            comments = re.findall(r'<!([^>]*)>', r['text_raw'])
            clock = next((m.group(0) for x in comments
                          if (m := re.search(r'\b\d{2}:\d{2}\b', x))), '')
            inventory.append(dict(corpus=r['corpus'], transcriber=r['transcriber'],
                folio=r['folio'], locus_id=r['line_id'], locus_code=r['locus_code'],
                type=kind, word_count=len(words),
                eva_codepoint_count=sum(len(w) for w in words), glyph_count='',
                unknown_word_count=sum('\ufffd' in w for w in words),
                has_uncertainty=r['has_uncertainty'], has_missing_span=r['has_missing_span'],
                is_spurious=r['is_spurious'], is_alternate_branch=r['is_alternate_branch'],
                currier_hand=r['currier_hand'], scribe=r['hand_scribe'],
                section=r['section'], section_code=r['section_code'],
                is_rosettes_foldout=r['folio'] == 'fRos',
                transcription_direction=direction, transcription_start_clock=clock,
                source_comments=json.dumps(comments, ensure_ascii=False),
                source_line=r['source_line'], source_sha256=source['sha256'],
                direction_call='NOT_RUN', seam_offset='', underpowered='',
                status='INVENTORY_ONLY'))
    assert inventory
    primary = [r for r in inventory if r['corpus'] == 'ZL']
    assert len({r['locus_id'] for r in primary}) == len(primary)
    fields = list(inventory[0])
    write_csv(OUT / 'ring_inventory.csv', primary, fields)
    write_csv(OUT / 'alternate_inventory.csv', [r for r in inventory if r['corpus'] != 'ZL'], fields)
    write_csv(OUT / 'all_locus_code_counts.csv', counts,
              ['corpus', 'transcriber', 'locus_code', 'n'])
    selected_counts = Counter((r['corpus'], r['transcriber'], r['type'], r['locus_code']) for r in inventory)
    write_csv(OUT / 'selected_code_counts.csv',
              [dict(corpus=c, transcriber=t, type=k, locus_code=l, n=n)
               for (c, t, k, l), n in sorted(selected_counts.items())],
              ['corpus', 'transcriber', 'type', 'locus_code', 'n'])
    # One row per locus, with no source comments/clock hints or text features.
    write_csv(OUT / 'physical_marks_BLANK.csv',
        [dict(folio=r['folio'], locus_id=r['locus_id'], annotation_status='NOT_ANNOTATED',
              mark_id='', mark_kind='', absolute_clock='', word_boundary_index='',
              image_reference='', confidence='', prior_exposure='', notes='') for r in primary],
        ['folio', 'locus_id', 'annotation_status', 'mark_id', 'mark_kind', 'absolute_clock',
         'word_boundary_index', 'image_reference', 'confidence', 'prior_exposure', 'notes'])
    write_json(OUT / 'synthetic_checks.json', synthetic_checks())
    status = dict(status='STOP_PRE_REGISTRATION_DESIGN',
                  timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  registered=False, phase0_calibration_run=False,
                  real_ring_scores_computed=False, phases_1_to_4_run=False,
                  corrected_order_generated=False, primary_loci=len(primary),
                  primary_types=dict(Counter(r['type'] for r in primary)),
                  primary_codes=dict(Counter(r['locus_code'] for r in primary)),
                  primary_word_lengths=dict(sorted(Counter(r['word_count'] for r in primary).items())),
                  primary_missing_start_clock=sum(not r['transcription_start_clock'] for r in primary),
                  sources=sources,
                  exposure='Agent read raw transcription excerpts/comments and parsed text for counts; '
                  'not an investigator-blind claim. Re annotation exposure has not been established.',
                  format_reference='https://www.voynich.nu/software/ivtt/IVTFF_format.pdf; '
                  'issue 2.0.2, Table 9, pp.22-23; accessed 2026-11-06',
                  glyph_count_policy='Unknown: EVA codepoints are not adjudicated glyph units.',
                  stop_reasons=['Non-identifiable single original seam in concatenated multiline loops',
                                'Maximum seam score invariant under rotation null',
                                'Radial loci require open-path endpoint treatment',
                                'Execution details and unique-seam calibration target not frozen'])
    write_json(OUT / 'STATUS.json', status)
    table = ['# RD preflight — 2026-11-06', '',
             '| ZL locus type | Loci | One-word loci | Source start clock missing |',
             '|---|---:|---:|---:|']
    for kind in ['circular', 'radial']:
        subset = [r for r in primary if r['type'] == kind]
        table.append(f"| {kind} | {len(subset)} | "
                     f"{sum(r['word_count'] == 1 for r in subset)} | "
                     f"{sum(not r['transcription_start_clock'] for r in subset)} |")
    table += ['', '| Corpus | Reading | Code | Loci |', '|---|---|---|---:|']
    for (corpus, t, kind, code), n in sorted(selected_counts.items()):
        table.append(f'| {corpus} | {t} | {code} | {n} |')
    table += ['', '**STOP_PRE_REGISTRATION_DESIGN.** No empirical RD calibration, fitted '
              'signature, real-ring score, phase 1–4 result or corrected order exists.', '',
              'Authored counterexamples establish that a peak over all rotations is '
              'rotation-invariant, and that multiple equally strong original line '
              'boundaries need not identify a unique original start. These are design '
              'limitations, not manuscript findings. Radial paths need endpoint treatment.', '',
              'See [the design review](../../../extensions/ringdir_v1/DESIGN_REVIEW.md) '
              'for the proposed amendment and remaining execution choices. The user '
              'draft is preserved unchanged. v10 remains reserved.', '',
              'Counts are locus counts, not adjudicated complete independent rings. '
              'LSI readings remain separate. Codes and transcription direction follow '
              '[IVTFF Table 9](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf), '
              'issue 2.0.2, pp.22–23. No glyph segmentation or physical clock map is inferred.', '',
              'The visual-mark worksheet is blank and omits source clock/comment '
              'hints. Re annotation/exposure registration is still pending. Agent '
              'source-text exposure is disclosed in STATUS.json.', '']
    (OUT / 'report.md').write_text('\n'.join(table), encoding='utf-8')
    manifest = {str(p.relative_to(LAB)): digest(p) for p in sorted(OUT.iterdir())
                if p.is_file() and p.name != 'PREFLIGHT_MANIFEST.json'}
    for p in [HERE / 'preflight.py', HERE / 'SPEC_USER_DRAFT.md', HERE / 'DESIGN_REVIEW.md']:
        manifest[str(p.relative_to(LAB))] = digest(p)
    write_json(OUT / 'PREFLIGHT_MANIFEST.json',
               {'kind': 'preflight provenance, NOT executable registration', 'sha256': manifest})
    print(json.dumps({k: status[k] for k in ['status', 'primary_loci', 'primary_types',
                                            'primary_codes', 'primary_missing_start_clock']}))


if __name__ == '__main__':
    main()
