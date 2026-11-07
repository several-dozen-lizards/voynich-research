<!-- editorial-guide: 2026-11-07 -->

# Why did contextual-role recovery fail?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Examined the saved errors and score components from the preceding role-recovery experiment without fitting a new model.

## What we found

Exact context features were sparse, clusters often followed local boundaries or collocations, and unseen features introduced a concrete scoring bias. The audit did not show that the representation had exhausted all useful information.

## What remains unresolved

Wider context was a possible future experiment, not an established cure. Retrospective error explanations are not prospective recovery improvements.

## What is in this folder

- [FREEZE.json](../../research/contextual-role-error-audit-v108/FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](../../research/contextual-role-error-audit-v108/PROTOCOL.json): the rules, intended scope, or pinned setup.
- [REPORT.txt](../../research/contextual-role-error-audit-v108/REPORT.txt): explanation, outcome, or dated checkpoint.
- [SCORE-AUDIT-FREEZE.json](../../research/contextual-role-error-audit-v108/SCORE-AUDIT-FREEZE.json): the rules, intended scope, or pinned setup.
- [VERIFICATION.json](../../research/contextual-role-error-audit-v108/VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [verify.py](../../research/contextual-role-error-audit-v108/verify.py): checks or qualification evidence; read the scope of the gate.
- [CLUSTER-BOUNDARY-AUDIT.json](../../research/contextual-role-error-audit-v108/CLUSTER-BOUNDARY-AUDIT.json): checks or qualification evidence; read the scope of the gate.
- [CONTEXT-COLLISIONS.json](../../research/contextual-role-error-audit-v108/CONTEXT-COLLISIONS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [CONTEXT-SUPPORT.json](../../research/contextual-role-error-audit-v108/CONTEXT-SUPPORT.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [EXAMPLES.json](../../research/contextual-role-error-audit-v108/EXAMPLES.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [history/](../../research/contextual-role-error-audit-v108/history) (3 archived files): Earlier versions, failed attempts, or preserved checkpoints. Their status belongs to their own date.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [contextual-role-error-audit-v108/REPORT.txt](../../research/contextual-role-error-audit-v108/REPORT.txt)

[Full study file catalogue](../../catalog/studies/contextual-role-error-audit-v108.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
