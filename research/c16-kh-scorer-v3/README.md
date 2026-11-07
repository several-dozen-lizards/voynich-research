<!-- editorial-guide: 2026-11-07 -->

# Separating scorer, decoder, objective, and search failures

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Made a narrower sentence-ending repair and tested probability arithmetic, discrimination, true-key decoding, the search objective, and blind key search separately.

## What we found

Probability arithmetic was repaired, but the full system remained unqualified. The separate checks exposed limits beyond that arithmetic bug, including weak discrimination and search performance.

## What remains unresolved

A mathematically valid scorer is not automatically an effective decoder. Fresh evidence from additional human writers was unavailable, and old material could not be made fresh by resampling.

## What is in this folder

- [C17-LICENSE-README.md](C17-LICENSE-README.md): explanation, outcome, or dated checkpoint.
- [PROTOCOL.md](PROTOCOL.md): the rules, intended scope, or pinned setup.
- [QUALIFICATION.json](QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [REPORT.md](REPORT.md): explanation, outcome, or dated checkpoint.
- [SOURCES.md](SOURCES.md): source attribution, access history, or rights context.
- [FAILURE_SEPARATION.json](FAILURE_SEPARATION.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [INDEPENDENT_AUDIT.json](INDEPENDENT_AUDIT.json): checks or qualification evidence; read the scope of the gate.
- [LENGTH_DIAGNOSTIC.json](LENGTH_DIAGNOSTIC.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [REGISTRATION.json](REGISTRATION.json): the rules, intended scope, or pinned setup.
- [audit.py](audit.py): checks or qualification evidence; read the scope of the gate.
- [inputs/](inputs) (10 archived files): Published inputs, derived tables, or source records. The archive ledger explains omitted raw or protected material.
- [preservation/](preservation) (1 archived files): Earlier versions, failed attempts, or preserved checkpoints. Their status belongs to their own date.
- [results/](results) (186 archived files): Reports, saved outputs, or run records. A saved output can document a pass, a failure, or an unfinished run.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [c16-kh-scorer-v3/REPORT.md](REPORT.md)
- [c16-kh-scorer-v3/QUALIFICATION.json](QUALIFICATION.json)

[Full study file catalogue](../../catalog/studies/c16-kh-scorer-v3.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
