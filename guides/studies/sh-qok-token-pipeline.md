<!-- editorial-guide: 2026-11-07 -->

# Testing the full path from raw tokens to a score

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Exercised token cleaning, eligibility, body matching, availability conditioning, support, and exact scoring together on constructed transcription.

## What we found

Dense designed cases passed, but sparse cases lost eligibility and were unsupported. The complete pipeline therefore did not receive broad qualification.

## What remains unresolved

Good performance on idealized group layouts cannot establish performance after realistic token and position losses. No manuscript scoring ran.

## What is in this folder

- [FREEZE.json](../../research/sh-qok-token-pipeline/FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](../../research/sh-qok-token-pipeline/PROTOCOL.json): the rules, intended scope, or pinned setup.
- [VERIFICATION.json](../../research/sh-qok-token-pipeline/VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report.html](../../research/sh-qok-token-pipeline/report.html): explanation, outcome, or dated checkpoint.
- [report.py](../../research/sh-qok-token-pipeline/report.py): explanation, outcome, or dated checkpoint.
- [DESIGNS.json.gz](../../research/sh-qok-token-pipeline/DESIGNS.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [SUMMARY.json](../../research/sh-qok-token-pipeline/SUMMARY.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [TRIALS.json](../../research/sh-qok-token-pipeline/TRIALS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [run.py](../../research/sh-qok-token-pipeline/run.py): implementation or checking code.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [sh-qok-token-pipeline/report.html](../../research/sh-qok-token-pipeline/report.html)

[Full study file catalogue](../../catalog/studies/sh-qok-token-pipeline.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
