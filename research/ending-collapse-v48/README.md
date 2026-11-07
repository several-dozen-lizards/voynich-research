<!-- editorial-guide: 2026-11-07 -->

# When is it useful to pool word endings?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested a predictor on known text with planted redundant endings, informative endings, and layout-driven endings.

## What we found

The predictor separated the planted redundant and informative cases, but also accepted every layout-driven control. That prevents interpreting acceptance as proof of meaningless filler.

## What remains unresolved

The exact natural-ending families and manuscript collapse were not qualified or run. Prediction improvement alone cannot decide what an ending does.

## What is in this folder

- [FREEZE.json](FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](PROTOCOL.json): the rules, intended scope, or pinned setup.
- [RESULTS.json](RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [report.html](report.html): explanation, outcome, or dated checkpoint.
- [report.py](report.py): explanation, outcome, or dated checkpoint.
- [SHA256SUMS.json](SHA256SUMS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [qualify.py](qualify.py): implementation or checking code.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [ending-collapse-v48/report.html](report.html)
- [ending-collapse-v48/RESULTS.json](RESULTS.json)

[Full study file catalogue](../../catalog/studies/ending-collapse-v48.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
