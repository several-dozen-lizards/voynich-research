<!-- editorial-guide: 2026-11-07 -->

# Does training frequency provide better evidence weights?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Weighted local and shared word evidence according to their training occurrence counts, alongside fixed comparison arms.

## What we found

This weighting rule did not improve expected recovery or probability-score quality over the repaired baseline. It retained extra coverage but lost to an equal-weight mixture on recovery in every adequately supported development panel.

## What remains unresolved

Training counts are not automatically measures of reliability or independent evidence. No alternative weighting was selected after seeing the failure.

## What is in this folder

- [DECISION.json](../../research/contextual-role-support-weighting-v113/DECISION.json): explanation, outcome, or dated checkpoint.
- [FREEZE.json](../../research/contextual-role-support-weighting-v113/FREEZE.json): the rules, intended scope, or pinned setup.
- [PROTOCOL.json](../../research/contextual-role-support-weighting-v113/PROTOCOL.json): the rules, intended scope, or pinned setup.
- [REPORT.txt](../../research/contextual-role-support-weighting-v113/REPORT.txt): explanation, outcome, or dated checkpoint.
- [RESULTS.json](../../research/contextual-role-support-weighting-v113/RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [VERIFICATION.json](../../research/contextual-role-support-weighting-v113/VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [verify.mjs](../../research/contextual-role-support-weighting-v113/verify.mjs): checks or qualification evidence; read the scope of the gate.
- [BOOTSTRAP-DRAWS.json.gz](../../research/contextual-role-support-weighting-v113/BOOTSTRAP-DRAWS.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [CONTROL-TRIALS.jsonl.gz](../../research/contextual-role-support-weighting-v113/CONTROL-TRIALS.jsonl.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [FIXTURES.json](../../research/contextual-role-support-weighting-v113/FIXTURES.json): saved data or supporting evidence; field definitions come from the protocol/report.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [contextual-role-support-weighting-v113/REPORT.txt](../../research/contextual-role-support-weighting-v113/REPORT.txt)
- [contextual-role-support-weighting-v113/DECISION.json](../../research/contextual-role-support-weighting-v113/DECISION.json)

[Full study file catalogue](../../catalog/studies/contextual-role-support-weighting-v113.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
