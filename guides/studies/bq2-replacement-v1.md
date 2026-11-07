<!-- editorial-guide: 2026-11-07 -->

# A replacement test that failed calibration

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested a proposed replacement for comparing effect strength between contexts, using cases where the true answer was known.

## What we found

The replacement flagged differences too often in a required control with differing baseline rates. It failed the frozen calibration requirement, so the manuscript comparison was not run.

## What remains unresolved

Passing a separate practical-tolerance check did not cancel that failure. The historical question remained unanswered by this version.

## What is in this folder

- [PROTOCOL.json](../../research/bq2-replacement-v1/PROTOCOL.json): the rules, intended scope, or pinned setup.
- [QUALIFICATION-INTERPRETATION.json](../../research/bq2-replacement-v1/QUALIFICATION-INTERPRETATION.json): checks or qualification evidence; read the scope of the gate.
- [QUALIFICATION.json](../../research/bq2-replacement-v1/QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [REPORT.md](../../research/bq2-replacement-v1/REPORT.md): explanation, outcome, or dated checkpoint.
- [RESULTS.json](../../research/bq2-replacement-v1/RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [VERIFICATION.json](../../research/bq2-replacement-v1/VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [CONTROLS-COMPLETE.json](../../research/bq2-replacement-v1/CONTROLS-COMPLETE.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [ENGINEERING.json](../../research/bq2-replacement-v1/ENGINEERING.json): checks or qualification evidence; read the scope of the gate.
- [MASKED.json.gz](../../research/bq2-replacement-v1/MASKED.json.gz): saved data or supporting evidence; field definitions come from the protocol/report.
- [PHASES.jsonl](../../research/bq2-replacement-v1/PHASES.jsonl): saved data or supporting evidence; field definitions come from the protocol/report.
- [trials/](../../research/bq2-replacement-v1/trials) (1,080 archived files): Constructed cases, control outcomes, or generator records. The parent report defines their purpose and pass/fail rules.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [bq2-replacement-v1/REPORT.md](../../research/bq2-replacement-v1/REPORT.md)
- [bq2-replacement-v1/QUALIFICATION-INTERPRETATION.json](../../research/bq2-replacement-v1/QUALIFICATION-INTERPRETATION.json)

[Full study file catalogue](../../catalog/studies/bq2-replacement-v1.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
