<!-- editorial-guide: 2026-11-07 -->

# Using shared evidence only when local evidence is absent

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested a fixed positional-first fallback intended to retain sharing's extra coverage while reducing its confidence problems.

## What we found

The fallback kept the extra decisions but lost most of the earlier recovery gain. Confidence quality improved relative to additive sharing, yet did not meet the requested no-worse comparison with the repaired baseline.

## What remains unresolved

This was a partial tradeoff rather than a complete solution. The exposed development results do not independently qualify the method.

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

- [contextual-role-shared-fallback-v112/REPORT.txt](REPORT.txt)
- [contextual-role-shared-fallback-v112/DECISION.json](DECISION.json)

[Full study file catalogue](../../catalog/studies/contextual-role-shared-fallback-v112.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
