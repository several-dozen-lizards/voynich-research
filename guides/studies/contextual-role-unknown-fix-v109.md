<!-- editorial-guide: 2026-11-07 -->

# Treating unseen context as missing evidence

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Changed the supervised scorer so that globally unseen features contribute no evidence and completely unsupported cases remain undecided.

## What we found

The repair improved several development measures and the evidence-bearing subset, but also produced explicit abstentions. Counting abstentions as misses gives a different, less favorable result than assigning them half-credit.

## What remains unresolved

No supported full comparison reached the recovery target. This repaired diagnostic did not qualify blind role discovery or establish any Voynich meanings.

## What is in this folder

- [FREEZE.json](../../research/contextual-role-unknown-fix-v109/FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](../../research/contextual-role-unknown-fix-v109/PROTOCOL.json): the rules, intended scope, or pinned setup.
- [REPORT.txt](../../research/contextual-role-unknown-fix-v109/REPORT.txt): explanation, outcome, or dated checkpoint.
- [RESULTS.json](../../research/contextual-role-unknown-fix-v109/RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [VERIFICATION.json](../../research/contextual-role-unknown-fix-v109/VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [verify.mjs](../../research/contextual-role-unknown-fix-v109/verify.mjs): checks or qualification evidence; read the scope of the gate.
- [BOOTSTRAP-DRAWS.json.gz](../../research/contextual-role-unknown-fix-v109/BOOTSTRAP-DRAWS.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [CONTROL-TRIALS.jsonl.gz](../../research/contextual-role-unknown-fix-v109/CONTROL-TRIALS.jsonl.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [DEVELOPMENT-SCORER.json](../../research/contextual-role-unknown-fix-v109/DEVELOPMENT-SCORER.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [FIXTURES.json](../../research/contextual-role-unknown-fix-v109/FIXTURES.json): saved data or supporting evidence; field definitions come from the protocol/report.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [contextual-role-unknown-fix-v109/REPORT.txt](../../research/contextual-role-unknown-fix-v109/REPORT.txt)
- [contextual-role-unknown-fix-v109/RESULTS.json](../../research/contextual-role-unknown-fix-v109/RESULTS.json)

[Full study file catalogue](../../catalog/studies/contextual-role-unknown-fix-v109.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
