<!-- editorial-guide: 2026-11-07 -->

# Would evaluating a continuous stream repair the unit test?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Re-evaluated the saved models under a declared continuous-stream amendment without refitting or altering the original failed results.

## What we found

Calibration still failed. The saved positives showed a merge-stage collapse from many chunks to very few units; removing dependence on spaces alone did not fix that problem.

## What remains unresolved

This reused the same control banks and was not independent confirmation. Manuscript and conditional secondary scoring remained closed.

## What is in this folder

- [PROTOCOL.md](PROTOCOL.md): the rules, intended scope, or pinned setup.
- [QUALIFICATION.json](QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [REPORT.md](REPORT.md): explanation, outcome, or dated checkpoint.
- [VERIFICATION.json](VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report.py](report.py): explanation, outcome, or dated checkpoint.
- [BAND.json](BAND.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [METRICS.csv](METRICS.csv): saved data or supporting evidence; field definitions come from the protocol/report.
- [READ_ONLY_AUDIT.json](READ_ONLY_AUDIT.json): checks or qualification evidence; read the scope of the gate.
- [REGISTRATION.json](REGISTRATION.json): the rules, intended scope, or pinned setup.
- [replay_jobs.py](replay_jobs.py): implementation or checking code.
- [results/](results) (840 archived files): Reports, saved outputs, or run records. A saved output can document a pass, a failure, or an unfinished run.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/extensions/phase11a_continuous_units_v1/REPORT.md](REPORT.md)

[Full study file catalogue](../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../GUIDES.md) · [Terms used in the reports](../../../../GLOSSARY.md)
