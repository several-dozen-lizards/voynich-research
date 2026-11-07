<!-- editorial-guide: 2026-11-07 -->

# Preserving a qualification run that failed to execute

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Attempted the registered first-stage full-family controls for the new conditional order statistic.

## What we found

The attempt stopped with a memory error while constructing the comparison family. The failed implementation, traceback, and frozen inputs were retained.

## What remains unresolved

An execution failure is not a failed scientific prediction or a negative manuscript finding. A repair required a separately named and frozen attempt.

## What is in this folder

- [FREEZE.json](FREEZE.json): the rules, intended scope, or pinned setup.
- [README.md](README.md): explanation, outcome, or dated checkpoint.
- [freeze.py](freeze.py): the rules, intended scope, or pinned setup.
- [report.html](report.html): explanation, outcome, or dated checkpoint.
- [report.py](report.py): explanation, outcome, or dated checkpoint.
- [verify.py](verify.py): checks or qualification evidence; read the scope of the gate.
- [CONTROL-PLAN.json](CONTROL-PLAN.json): the rules, intended scope, or pinned setup.
- [DELIVERY-HASHES.json](DELIVERY-HASHES.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [EXECUTION-FAILURE.json](EXECUTION-FAILURE.json): the rules, intended scope, or pinned setup.
- [FAMILY.json](FAMILY.json): saved data or supporting evidence; field definitions come from the protocol/report.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [v103-qualification-v104/report.html](report.html)
- [v103-qualification-v104/README.md](README.md)

[Full study file catalogue](../../catalog/studies/v103-qualification-v104.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
