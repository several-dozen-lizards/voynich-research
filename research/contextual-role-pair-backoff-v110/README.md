<!-- editorial-guide: 2026-11-07 -->

# Does backing off from rare word pairs help?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Suppressed singleton context-pair evidence while retaining the component words already present in the repaired scorer.

## What we found

The fixed rule changed very few decisions, produced negligible recovery improvement, and added no coverage. Simply falling back from an unseen pair was already equivalent to the baseline unless evidence was counted twice.

## What remains unresolved

This particular rule was not adopted. Other ways of sharing or combining evidence were not established by this test.

## What is in this folder

- [DECISION.json](DECISION.json): explanation, outcome, or dated checkpoint.
- [FREEZE.json](FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](PROTOCOL.json): the rules, intended scope, or pinned setup.
- [REPORT.txt](REPORT.txt): explanation, outcome, or dated checkpoint.
- [RESULTS.json](RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [VERIFICATION.json](VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [verify.mjs](verify.mjs): checks or qualification evidence; read the scope of the gate.
- [BOOTSTRAP-DRAWS.json.gz](BOOTSTRAP-DRAWS.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [CONTROL-TRIALS.jsonl.gz](CONTROL-TRIALS.jsonl.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [FIXTURES.json](FIXTURES.json): saved data or supporting evidence; field definitions come from the protocol/report.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [contextual-role-pair-backoff-v110/REPORT.txt](REPORT.txt)
- [contextual-role-pair-backoff-v110/DECISION.json](DECISION.json)

[Full study file catalogue](../../catalog/studies/contextual-role-pair-backoff-v110.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
