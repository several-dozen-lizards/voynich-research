"""Run safe, repeatable S_fit-only development and provenance audit."""
from pathlib import Path
from collections import Counter
import argparse
import json
import platform
import re
import shutil
import sys
import time
import unittest
import xml.etree.ElementTree as ET
import numpy as np
from core import load_evt, panels, save, sha, canonical_hash, bootstrap_fit, fit_summary, rank_mapping
from GENERATORS import generate, FAMILIES

ROOT = Path(__file__).resolve().parent
DATA = Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a15c3d-56da-7f02-bc15-2522dc396abd\voynich-layout\data')
KNOWN = Path(r'C:\Users\lewis\.codex\visualizations\2026\10\21\01a160c2-56f0-7303-b3bf-ed8594c6ec40\voynich-abbreviation-v33\claude-abbrev-2026-10-22\sources')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bootstrap', type=int, default=100)
    args = parser.parse_args()
    if args.bootstrap < 2: raise ValueError('at least two bootstrap draws')
    if (ROOT/'FREEZE.json').exists():
        raise RuntimeError('sandbox closed after claim freeze; use a new experiment directory')
    started = time.time()
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern='test_sandbox.py')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError('sandbox engineering checks failed')
    rows, source_manifest = load_evt(DATA/'text16e6.original.evt', DATA/'Davis-hands.original.csv')
    save(ROOT/'DATA-MANIFEST.json', source_manifest)
    cells = []
    targets = {}
    for i, (key, cell) in enumerate(sorted(panels(rows).items())):
        cell_id = '-'.join(key)
        n_pages = len(set(row['folio'] for row in cell))
        targets[cell_id] = bootstrap_fit(cell, args.bootstrap, 52024+i) if n_pages >= 2 else {'status': 'INSUFFICIENT_PAGES'}
        cells.append(dict(currier=key[0], scribe=key[1], reading=key[2], lines=len(cell), pages=n_pages,
                          known_words=sum(w is not None for r in cell for w in r['tokens']),
                          unknown_slots=sum(w is None for r in cell for w in r['tokens']),
                          sections=dict(Counter(r['section'] for r in cell))))
    save(ROOT/'S-FIT-TARGETS.json', targets)
    save(ROOT/'CELLS.json', cells)
    sources = {}
    for language in ('Latin', 'German'):
        path = KNOWN/(language+'.xml')
        if path.exists():
            document = ET.parse(path)
            segments = [re.findall('[a-z]+', ''.join(node.itertext()).lower()) for node in document.iter('seg')]
            words = [w for segment in segments for w in segment]
            sources[language] = dict(path=str(path), sha256=sha(path), words=len(words),
                                     provenance='previous project source; Bible, not medieval medical/diplomatic',
                                     claim_ready=False)
    # Human-authored tiny Latin fixture. Not an inferential corpus or a Latin source claim.
    fixture = 'recipe herba et eius sucus bonus est cum aqua et oleum'.split()
    smoke = []
    mapping_trials = []
    samples = ROOT/'SANDBOX-SAMPLES'
    samples.mkdir(exist_ok=True)
    for i, family in enumerate(FAMILIES):
        generated = generate(family, {}, 53024+i, source=fixture, line_lengths=(8,)*100)
        save(samples/(family+'.json'), generated)
        # Raw generator units are not converted to characters by stringifying marks.
        smoke.append(dict(family=family, runs=True, seed=53024+i, lines=100, words=800,
                          raw_units=sum(len(w) for line in generated['lines'] for w in line),
                          historical_qualification=False, lineage_records=len(generated['lineage']),
                          output_sha256=sha(samples/(family+'.json'))))
        if family in ('G1', 'G2', 'G3', 'G4'):
            unit_words = [word for line in generated['lines'] for word in line]
            for key, cell in sorted(panels(rows).items()):
                target_words = [list(w) for r in cell for w in r['tokens'] if w]
                try:
                    mapping = rank_mapping(unit_words, target_words)
                    mapping_trials.append(dict(family=family, cell='-'.join(key), status='DRAFT_MAP_EXISTS', receipt=mapping))
                except ValueError as error:
                    mapping_trials.append(dict(family=family, cell='-'.join(key), status='CAPACITY_ABSTENTION', reason=str(error)))
    save(ROOT/'MAPPING-PREFLIGHT.json', mapping_trials)
    save(ROOT/'SOURCE-INVENTORY.json', sources)
    save(ROOT/'SANDBOX-SMOKE.json', smoke)
    manifest = ROOT/'SOURCES'/'timm-schinner-manifest.json'
    upstream = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else None
    published_ok = upstream is not None and all(sha(ROOT/r['path']) == r['sha256'] for r in upstream['files'])
    verification = dict(status='SANDBOX_ENGINEERING_PASS', claim_ready=False, claim_freeze_exists=False,
                        engineering_tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                        held_statistics_computed_on_generator_output=False, held_statistics_computed_on_manuscript=False,
                        source_hashes_checked=True, exclusions_checked=True, H_F_pooled=False, Currier_A_B_pooled=False,
                        cells=len(cells), generated_fixture_words=4800, bootstrap_repeats_per_panel=args.bootstrap,
                        published_source_files_verified=len(upstream['files']) if published_ok else 0,
                        manuscript_fit_performed=False, inference_performed=False,
                        python=platform.python_version(), numpy=np.__version__, elapsed_seconds=time.time()-started,
                        data_manifest_sha256=sha(ROOT/'DATA-MANIFEST.json'),
                        code_hashes={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'core.py',ROOT/'held.py',ROOT/'GENERATORS/__init__.py',ROOT/'test_sandbox.py',Path(__file__)]})
    save(ROOT/'VERIFICATION.json', verification)
    print(json.dumps(dict(status=verification['status'], tests=result.testsRun, cells=len(cells),
                          mapping_abstentions=sum(r['status']=='CAPACITY_ABSTENTION' for r in mapping_trials),
                          published_source_verified=published_ok, held_scoring=False, elapsed_seconds=round(time.time()-started, 1))))

if __name__ == '__main__':
    main()
