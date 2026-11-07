<!-- editorial-guide: 2026-11-07 -->

# Testing the point where a planted effect is just possible

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Constructed supported layouts near the sh follower-availability boundary, retaining accepted and rejected candidate layouts.

## What we found

The specified null and positive checks passed at that particular boundary. The positive was deliberately strong among the few available followers, which can make it easier to detect.

## What remains unresolved

The ch boundary and the joint boundary were not qualified by this experiment. A pass here is not universal sensitivity across availability patterns.

## What is in this folder

- [FREEZE.json](FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](PROTOCOL.json): the rules, intended scope, or pinned setup.
- [VERIFICATION.json](VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report.html](report.html): explanation, outcome, or dated checkpoint.
- [report.py](report.py): explanation, outcome, or dated checkpoint.
- [ATTEMPTS.json](ATTEMPTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [DESIGNS.json.gz](DESIGNS.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [SUMMARY.json](SUMMARY.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [TRIALS.json](TRIALS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [run.py](run.py): implementation or checking code.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [sh-qok-feasibility-boundary/report.html](report.html)

[Full study file catalogue](../../catalog/studies/sh-qok-feasibility-boundary.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
