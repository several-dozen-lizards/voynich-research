<!-- editorial-guide: 2026-11-07 -->

# Would considering every interior position solve sparse matching?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Allowed all interior positions as candidate matches while preserving line composition, exact word bodies, and position controls.

## What we found

The constructed positive cases still failed the required detection gates, and no dataset reached the earlier usable-support requirement. Some zero false-alarm counts came from cases that could not be estimated at all.

## What remains unresolved

The limitation was too few usable comparisons, not evidence against an association. No manuscript data were opened or scored.

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

- [sh-qok-all-interior/report.html](report.html)

[Full study file catalogue](../../catalog/studies/sh-qok-all-interior.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
