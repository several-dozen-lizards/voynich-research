<!-- editorial-guide: 2026-11-07 -->

# Catching an incompatible specification before running it

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Checked whether the requested single-target study could be executed unchanged by the referenced scoring engines.

## What we found

Preflight found a mismatch between the requested strata and the qualified engine, plus target leakage in a proposed predictive comparison. All manuscript cells stayed not run.

## What remains unresolved

Not run is different from unsupported, underpowered, or negative. Executing the study required an explicit revised specification rather than silently changing its question.

## What is in this folder

- [FREEZE.json](../../research/sh-qok-single-target-preflight/FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](../../research/sh-qok-single-target-preflight/PROTOCOL.json): the rules, intended scope, or pinned setup.
- [REPORT.md](../../research/sh-qok-single-target-preflight/REPORT.md): explanation, outcome, or dated checkpoint.
- [ORIGINAL-SPEC.txt](../../research/sh-qok-single-target-preflight/ORIGINAL-SPEC.txt): the rules, intended scope, or pinned setup.
- [PANELS-METADATA-ONLY.json](../../research/sh-qok-single-target-preflight/PANELS-METADATA-ONLY.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [preflight.py](../../research/sh-qok-single-target-preflight/preflight.py): implementation or checking code.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [sh-qok-single-target-preflight/REPORT.md](../../research/sh-qok-single-target-preflight/REPORT.md)

[Full study file catalogue](../../catalog/studies/sh-qok-single-target-preflight.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
