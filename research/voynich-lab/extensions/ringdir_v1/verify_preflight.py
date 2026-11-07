"""Independent raw-record/count checks and preflight artifact verification."""
import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
OUT = LAB / 'results' / 'ringdir' / 'preflight'


def read_csv(name):
    with (OUT / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def verify():
    status = json.loads((OUT / 'STATUS.json').read_text(encoding='utf-8'))
    manifest = json.loads((OUT / 'PREFLIGHT_MANIFEST.json').read_text(encoding='utf-8'))
    for name, sha in manifest['sha256'].items():
        assert hashlib.sha256((LAB / name).read_bytes()).hexdigest() == sha, name
    primary, alternates = read_csv('ring_inventory.csv'), read_csv('alternate_inventory.csv')
    for corpus, rows, filename in [('ZL', primary, 'ZL3b-n.txt'),
                                   ('LSI', alternates, 'LSI_ivtff_0d.txt')]:
        raw = (LAB / 'data' / 'raw' / filename).read_bytes().decode('latin-1')
        # Independent physical record header extraction; continuation lines have no header.
        expected = set()
        for m in re.finditer(r'^<(f[^.>]+)\.(\d+[a-z]?),([^;>]+)(?:;([^>]+))?>', raw, re.M):
            folio, num, code, reading = m.groups()
            if code[1:] in {'Cc', 'Ca', 'Ri', 'Ro'}:
                expected.add((folio + '.' + num, reading or 'ZL', code))
        actual = {(r['locus_id'], r['transcriber'], r['locus_code']) for r in rows}
        assert actual == expected, (corpus, len(actual), len(expected))
        assert len(actual) == len(rows)
    assert len(primary) == status['primary_loci'] == 226
    assert all(r['direction_call'] == 'NOT_RUN' and r['seam_offset'] == ''
               and r['underpowered'] == '' and r['glyph_count'] == '' for r in primary + alternates)
    marks = read_csv('physical_marks_BLANK.csv')
    assert len(marks) == len(primary)
    assert all(r['annotation_status'] == 'NOT_ANNOTATED' and not r['absolute_clock']
               and not r['word_boundary_index'] for r in marks)
    assert not any(k in marks[0] for k in ['source_comments', 'transcription_start_clock'])
    assert status['registered'] is False and status['phase0_calibration_run'] is False
    assert status['real_ring_scores_computed'] is False and status['phases_1_to_4_run'] is False
    toy = json.loads((OUT / 'synthetic_checks.json').read_text())
    assert all(toy['checks'].values())
    assert len(set(toy['maxima_under_rotations'])) == 1
    # Independent scalar boundary calculation in a twelve-slot perfect classifier.
    values = [int(i % 4 == 0) + int((i-1) % 4 == 3) for i in range(12)]
    assert [i for i, v in enumerate(values) if v == max(values)] == [0, 4, 8]
    return {'status': 'PASS', 'primary_loci': len(primary),
            'alternate_reading_rows': len(alternates),
            'verified': ['preflight artifact hashes', 'independent raw source locus coverage',
                         'unique reading keys', 'empty result/glyph columns',
                         'unfilled visual worksheet without source hints',
                         'no registration/calibration/target scoring', 'authored algebraic counterexamples'],
            'scope': 'Preflight verification only; does not qualify any RD signal.'}


if __name__ == '__main__':
    result = verify()
    (OUT / 'VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
