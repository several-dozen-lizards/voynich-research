"""Rebuild local Phase 0 tables/report from frozen, hash-checked downloads."""
import csv
import hashlib
import itertools
import json
import platform
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from parse_ivtff import parse, edit_distance, UNK

ROOT = Path(__file__).resolve().parents[1]

def write_csv(path, rows):
    if not rows:
        raise ValueError(f'No rows for {path}')
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def summary(rows):
    words = [w for r in rows for w in r['text_eva'].split()]
    return dict(lines=len(rows), pages=len({r['folio'] for r in rows}),
                words=len(words), characters=sum(map(len, words)), vocabulary=len(set(words)))

def main():
    if sys.version_info < (3, 11):
        raise RuntimeError('Use Python 3.11+ (bundled Python is available).')
    config = json.loads((ROOT/'configs/phase0.json').read_text())
    run_id = datetime.now(timezone.utc).strftime('phase0-%Y%m%dT%H%M%S%fZ')
    run = ROOT/'runs'/run_id
    run.mkdir()
    (run/'config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    (run/'environment.json').write_text(json.dumps(dict(python=sys.version,
        executable=sys.executable, platform=platform.platform(), seed=config['seed']), indent=2))
    manifest, all_rows, totals, sections, missing = [], [], [], [], []
    for source in config['sources']:
        path = ROOT/'data/raw'/source['filename']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source['sha256']:
            raise ValueError(f'Source hash changed: {path}; log and review before updating config.')
        manifest.append({**source, 'sha256': digest, 'bytes': path.stat().st_size})
        rows = parse(path, source['id'])
        write_csv(ROOT/'data/voynich'/f"{source['id']}_lines.csv", rows)
        all_rows.extend(rows)
        for t in sorted({r['transcriber'] for r in rows}):
            selected = [r for r in rows if r['transcriber'] == t]
            totals.append(dict(corpus=source['id'], transcriber=t, **summary(selected)))
            for section in sorted({r['section'] or 'unknown' for r in selected}):
                group = [r for r in selected if (r['section'] or 'unknown') == section]
                sections.append(dict(corpus=source['id'], transcriber=t, section=section, **summary(group)))
        for field in ['section','currier_lang','hand_scribe','currier_hand','line_index_in_paragraph','is_para_start','is_para_end']:
            missing.append(dict(corpus=source['id'], field=field, missing=sum(r[field] is None for r in rows), total=len(rows)))
    write_csv(ROOT/'report/corpus_summary.csv', totals)
    write_csv(ROOT/'report/section_summary.csv', sections)
    write_csv(ROOT/'report/missing_metadata.csv', missing)
    groups = defaultdict(list)
    for r in all_rows:
        if r['corpus'] == 'LSI':
            groups[r['line_id']].append(r)
    pairs, coverage = [], Counter()
    for locus, rows in groups.items():
        if len(rows) > 1:
            coverage['multi_transcriber_loci'] += 1
        for a, b in itertools.combinations(sorted(rows, key=lambda r: r['transcriber']), 2):
            coverage['candidate_pairs'] += 1
            reason = ('alternate_branch' if a['is_alternate_branch'] or b['is_alternate_branch'] else
                      'missing_span' if a['has_missing_span'] or b['has_missing_span'] else
                      'spurious' if a['is_spurious'] or b['is_spurious'] else '')
            x, y = a['text_eva'], b['text_eva']
            # UNK must never earn a character match in the noise-floor estimate.
            x, y = x.replace(UNK, '\ue000'), y.replace(UNK, '\ue001')
            if not x or not y:
                reason = reason or 'empty'
            n = max(len(x), len(y))
            distance = edit_distance(x, y)
            coverage['excluded_'+reason if reason else 'included_pairs'] += 1
            pairs.append(dict(line_id=locus, transcriber_a=a['transcriber'], transcriber_b=b['transcriber'],
                denominator=n, distance=distance, agreement=1-distance/n if n else None,
                included=not bool(reason), exclusion=reason))
    write_csv(ROOT/'report/agreement_lines.csv', pairs)
    by_pair = defaultdict(list)
    for p in pairs:
        if p['included']:
            by_pair[(p['transcriber_a'], p['transcriber_b'])].append(p)
    agreement = []
    for (a,b), ps in sorted(by_pair.items()):
        den, dist = sum(p['denominator'] for p in ps), sum(p['distance'] for p in ps)
        agreement.append(dict(transcriber_a=a, transcriber_b=b, pairs=len(ps), denominator=den,
                              distance=dist, agreement=1-dist/den, disagreement=dist/den))
    write_csv(ROOT/'report/agreement_by_pair.csv', agreement)
    included = [p for p in pairs if p['included']]
    den = sum(p['denominator'] for p in included)
    dist = sum(p['distance'] for p in included)
    metrics = dict(status='PHASE_0_COMPLETE_STOP', run_id=run_id, seed=config['seed'],
        summary=totals, agreement=dict(weighted_agreement=1-dist/den, weighted_disagreement=dist/den,
        denominator=den, distance=dist, **coverage), source_manifest=manifest)
    (run/'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    # Code receipts allow reproduction even as future phases add modules.
    receipts = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in ['src','configs','tests'] for p in (ROOT/folder).glob('*.py' if folder != 'configs' else '*.json')}
    receipts.update({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (ROOT/'report').glob('*.csv')})
    (run/'hashes.json').write_text(json.dumps(receipts, indent=2), encoding='utf-8')
    source_lines = ['# Sources', '', 'Downloaded 2026-10-26; raw bytes preserved unchanged. No cloud models or training.', '']
    for m in manifest:
        source_lines += [f"- [{m['filename']}]({m['url']}): {m['bytes']:,} bytes; SHA-256 `{m['sha256']}`."]
    source_lines += ['', 'Catalog: https://www.voynich.nu/transcr.html',
        'Format: https://www.voynich.nu/software/ivtt/IVTFF_format.pdf', '',
        'LSI is the catalog-linked beta IVTFF 1.5 conversion (0d), not an IT-only substitute.',
        'The files are publicly downloadable; no public-domain or redistribution license is inferred. Keep local pending license review for any release.']
    (ROOT/'SOURCES.md').write_text('\n'.join(source_lines)+'\n', encoding='utf-8')
    report = ['# Voynich pattern-model lab — Phase 0', '',
        '**STOP: Phase 0 complete. Phases 1–5 have not run.**', '',
        f"Run: `{run_id}`; Python {platform.python_version()}; deterministic intake, seed {config['seed']} (no sampling).", '',
        '## Transcriber disagreement: operational noise floor', '',
        f"LSI pair-weighted character agreement: **{1-dist/den:.2%}**; disagreement: **{dist/den:.2%}**.",
        f"{len(included):,} included line-pairs; {coverage['multi_transcriber_loci']:,} loci have multiple recorded versions.", '',
        'Agreement = 1 − exact Levenshtein distance / maximum cleaned line length, pooled by summing distances and denominators. Includes normalized word spaces; unknown symbols never match. See agreement_by_pair.csv for H/F and every other pair separately.', '',
        'This is an operational transcription-sensitivity estimate, not a universal statistical floor or a quantity in bits/token. Historical readings share ancestry, coverage and alphabet conversion; pair counts are dependent. No corpus-wide accuracy or full-coverage agreement is inferred. Locus alignment is within LSI only; ZL/LSI locus IDs are not assumed physically interchangeable.', '',
        f"Exclusions: {dict(coverage)}. All candidate pairs and reasons are retained in agreement_lines.csv.", '',
        '## Intake counts', '',
        'Characters exclude spaces; words split both certain and uncertain spaces. Vocabulary includes UNK-bearing words. These are EVA code-point counts, not manuscript glyph counts. Each row is one IVTFF locus/version; split line segments and labels are not merged into physical lines. LSI rows must not be pooled as a single corpus.', '',
        '| Source | Transcriber | Loci | Pages | Words | EVA characters | Vocabulary |',
        '|---|---|---:|---:|---:|---:|---:|']
    for r in totals:
        report.append(f"| {r['corpus']} | {r['transcriber']} | {r['lines']:,} | {r['pages']} | {r['words']:,} | {r['characters']:,} | {r['vocabulary']:,} |")
    report += ['', '## Per-section counts', '', '| Source | Transcriber | Section | Loci | Words | Characters |', '|---|---|---|---:|---:|---:|']
    for r in sections:
        report.append(f"| {r['corpus']} | {r['transcriber']} | {r['section']} | {r['lines']} | {r['words']} | {r['characters']} |")
    report += ['', '## Missing metadata', '', '| Source | Field | Missing | Total |', '|---|---|---:|---:|']
    report += [f"| {r['corpus']} | {r['field']} | {r['missing']} | {r['total']} |" for r in missing]
    report += ['', 'See DECISIONS.md for null/paragraph/hand/markup policies; SOURCES.md for byte hashes and provenance.', '',
        '## What this does NOT show', '',
        'No controls have been prepared and no generator, language, shorthand, cipher, entropy or semantic inference has been tested. No model has been trained. Intake counts and disagreement describe these files only; they do not identify how Voynich text was generated and do not constitute decipherment or translation.', '',
        'The next stage is Phase 1 controls, then Phase 2 tokenization and Phase 3 paired measurements, with another mandatory stop.']
    (ROOT/'report/REPORT.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print(json.dumps(dict(run_id=run_id, agreement=metrics['agreement'], zl=totals[-1]), indent=2))

if __name__ == '__main__':
    main()
