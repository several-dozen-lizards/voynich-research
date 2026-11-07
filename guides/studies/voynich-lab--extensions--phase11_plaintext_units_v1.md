<!-- editorial-guide: 2026-11-07 -->

# Can a unit-finding pipeline recover known plaintext structure?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested alternative segmentation/merge pipelines on natural text, planted encodings, and negative controls before manuscript use.

## What we found

Positive calibration failed, including under the requested identical-pipeline rule. An extra literal-letter anchor also introduced an acknowledged impossible combined gate, preserved as a design error rather than hidden.

## What remains unresolved

The audit did not repair the failed merge method or identify manuscript units. No target segmentation, letter values, or meaning was scored.

## What is in this folder

- [PROTOCOL.md](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/PROTOCOL.md): the rules, intended scope, or pinned setup.
- [QUALIFICATION.json](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [REPORT.md](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/REPORT.md): explanation, outcome, or dated checkpoint.
- [SOURCES.md](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/SOURCES.md): source attribution, access history, or rights context.
- [VERIFICATION.json](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report.py](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/report.py): explanation, outcome, or dated checkpoint.
- [BAND.json](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/BAND.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [DIAGNOSTICS.json](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/DIAGNOSTICS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [EXECUTION_NOTES.md](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/EXECUTION_NOTES.md): the rules, intended scope, or pinned setup.
- [METRICS.csv](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/METRICS.csv): saved data or supporting evidence; field definitions come from the protocol/report.
- [results/](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/results) (840 archived files): Reports, saved outputs, or run records. A saved output can document a pass, a failure, or an unfinished run.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/extensions/phase11_plaintext_units_v1/REPORT.md](../../research/voynich-lab/extensions/phase11_plaintext_units_v1/REPORT.md)

[Full study file catalogue](../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
