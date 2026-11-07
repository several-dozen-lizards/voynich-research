<!-- editorial-guide: 2026-11-07 -->

# Expanding the set of legal comparison arrangements

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Built an exact conditional comparison over more prefix arrangements while retaining line, position, and literal-body controls.

## What we found

The revision improved detection in some constructed cases, but a required page-control gate and sparse positive cases still failed. Every result from the new and old methods on the same data was retained.

## What remains unresolved

A larger legal arrangement space is not automatically a fully qualified test. Sparse support and nuisance behavior still constrained manuscript use.

## What is in this folder

- [FREEZE.json](FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](PROTOCOL.json): the rules, intended scope, or pinned setup.
- [VERIFICATION.json](VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report.html](report.html): explanation, outcome, or dated checkpoint.
- [report.py](report.py): explanation, outcome, or dated checkpoint.
- [SUMMARY.json](SUMMARY.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [TRIALS.json](TRIALS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [run.py](run.py): implementation or checking code.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [sh-qok-expanded-null/report.html](report.html)

[Full study file catalogue](../../catalog/studies/sh-qok-expanded-null.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
