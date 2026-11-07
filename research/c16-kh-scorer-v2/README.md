<!-- editorial-guide: 2026-11-07 -->

# Diagnosing the unknown-word scoring failure

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Separated and repaired several ways the earlier language model handled unknown words, sentence endings, and missing contexts, then tested the repair on known-answer controls.

## What we found

The repair still failed required qualification checks in both source arms. Some individual tests improved, but neither arm qualified as a whole.

## What remains unresolved

Correcting a ranking formula alone could not repair keys already fitted with a defective objective. New manuscript scoring stayed closed.

## What is in this folder

- [C17-LICENSE-README.md](C17-LICENSE-README.md): explanation, outcome, or dated checkpoint.
- [PROTOCOL.md](PROTOCOL.md): the rules, intended scope, or pinned setup.
- [QUALIFICATION.json](QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [REPORT.md](REPORT.md): explanation, outcome, or dated checkpoint.
- [DIAGNOSIS.json](DIAGNOSIS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [INDEPENDENT_AUDIT.json](INDEPENDENT_AUDIT.json): checks or qualification evidence; read the scope of the gate.
- [REGISTRATION.json](REGISTRATION.json): the rules, intended scope, or pinned setup.
- [audit.py](audit.py): checks or qualification evidence; read the scope of the gate.
- [corrected.py](corrected.py): implementation or checking code.
- [diagnose.py](diagnose.py): implementation or checking code.
- [inputs/](inputs) (11 archived files): Published inputs, derived tables, or source records. The archive ledger explains omitted raw or protected material.
- [preservation/](preservation) (1 archived files): Earlier versions, failed attempts, or preserved checkpoints. Their status belongs to their own date.
- [results/](results) (256 archived files): Reports, saved outputs, or run records. A saved output can document a pass, a failure, or an unfinished run.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [c16-kh-scorer-v2/REPORT.md](REPORT.md)
- [c16-kh-scorer-v2/QUALIFICATION.json](QUALIFICATION.json)

[Full study file catalogue](../../catalog/studies/c16-kh-scorer-v2.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
