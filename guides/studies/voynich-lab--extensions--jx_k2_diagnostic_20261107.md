<!-- editorial-guide: 2026-11-07 -->

# Checking what the paragraph adapter's markers mean

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Registered semantic fixtures and source-fidelity checks before decomposing the reading-robustness failure.

## What we found

The associated K2D run stopped when both required semantic fixtures failed: layout locators had been treated as certified paragraph starts. Later diagnostic chains were not run.

## What remains unresolved

This exposed a source-interpretation defect rather than repairing the earlier result. A separately registered correction was needed.

## What is in this folder

- [EXECUTION.md](../../research/voynich-lab/extensions/jx_k2_diagnostic_20261107/EXECUTION.md): the rules, intended scope, or pinned setup.
- [authority.json](../../research/voynich-lab/extensions/jx_k2_diagnostic_20261107/authority.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [diagnostic.py](../../research/voynich-lab/extensions/jx_k2_diagnostic_20261107/diagnostic.py): implementation or checking code.
- [test_engineering.py](../../research/voynich-lab/extensions/jx_k2_diagnostic_20261107/test_engineering.py): checks or qualification evidence; read the scope of the gate.
- [registration/](../../research/voynich-lab/extensions/jx_k2_diagnostic_20261107/registration) (5 archived files): Study rules, source/geometry registration, or pinned inputs. Read the timing and amendment receipts before assuming a stage was complete.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/results/jx/JX-20261107-K2D-1/report.md](../../research/voynich-lab/results/jx/JX-20261107-K2D-1/report.md)

[Full study file catalogue](../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
