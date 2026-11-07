<!-- editorial-guide: 2026-11-07 -->

# How many supplied names does the toy decoder need?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Expanded the name-recovery benchmark with new name strings, separate development and confirmation sets, and five fixed encodings.

## What we found

Full-letter and consonant-only versions first met the tested reliability rule at 36 supplied training names. The internal-vowel-omission version failed its confirmation gate, and the syllable-like schemes did not reach development qualification.

## What remains unresolved

Correct name pairs and boundaries were supplied. The number 36 is a benchmark-specific result, not a universal minimum or permission to fit uncertain Voynich labels.

## What is in this folder

- [FREEZE.json](FREEZE.json): the rules, intended scope, or pinned setup.
- [PRE-RUN-FREEZE.json](PRE-RUN-FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](PROTOCOL.json): the rules, intended scope, or pinned setup.
- [report.html](report.html): explanation, outcome, or dated checkpoint.
- [CONFIRMATION.json.gz](CONFIRMATION.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [COVERAGE-CEILING.json](COVERAGE-CEILING.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [CURVES.json](CURVES.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [DEVELOPMENT-TRIALS.json.gz](DEVELOPMENT-TRIALS.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [H-F-SLOTS.json](H-F-SLOTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [NAMES.json](NAMES.json): saved data or supporting evidence; field definitions come from the protocol/report.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [name-coverage-v80/report.html](report.html)

[Full study file catalogue](../../catalog/studies/name-coverage-v80.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
