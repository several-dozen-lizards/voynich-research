<!-- editorial-guide: 2026-11-07 -->

# Why did the picture-label scan produce too many alarms?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Traced the failed scan through its exact readable exposures, permutation assumptions, sparse cells, and a separately frozen repair diagnostic.

## What we found

The audit identified a mismatch between fixed label-specific readable exposure and the shuffled reference, with a particularly influential singleton cell. Position confounding and support failures were separate problems. The saved repair cell reduced alarms but still failed its scan gate.

## What remains unresolved

The retained repair summary is limited and does not certify a complete replacement. No real word/image outcome join or protected scoring followed from the audit.

## What is in this folder

- [AUDIT-FREEZE.json](AUDIT-FREEZE.json): the rules, intended scope, or pinned setup.
- [REPAIR-FREEZE.json](REPAIR-FREEZE.json): the rules, intended scope, or pinned setup.
- [verify.py](verify.py): checks or qualification evidence; read the scope of the gate.
- [AUDIT-CODE-SEAL.json](AUDIT-CODE-SEAL.json): checks or qualification evidence; read the scope of the gate.
- [AUDIT-DIAGNOSTIC-EXTENSION.json](AUDIT-DIAGNOSTIC-EXTENSION.json): checks or qualification evidence; read the scope of the gate.
- [CAUSE.json](CAUSE.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [DIAGNOSTICS.json](DIAGNOSTICS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [EXPOSURE-DIAGNOSTIC.json](EXPOSURE-DIAGNOSTIC.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [FIXED-DESIGN-CODE-SEAL.json](FIXED-DESIGN-CODE-SEAL.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [FIXED-DESIGN-DIAGNOSTICS.json](FIXED-DESIGN-DIAGNOSTICS.json): saved data or supporting evidence; field definitions come from the protocol/report.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [t1-scan-calibration-audit-2026-10-26/CAUSE.json](CAUSE.json)
- [t1-scan-calibration-audit-2026-10-26/REPAIRED-SUMMARY.json](REPAIRED-SUMMARY.json)

[Full study file catalogue](../../catalog/studies/t1-scan-calibration-audit-2026-10-26.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
