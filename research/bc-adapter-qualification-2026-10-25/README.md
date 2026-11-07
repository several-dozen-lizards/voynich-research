<!-- editorial-guide: 2026-11-07 -->

# Can the proposed B/C scoring adapters recover known answers?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested the adapters on constructed examples with known numerical and phrase-order relationships, including several arrangements of item counts.

## What we found

Most arrangements worked, but three groups of four items failed positive recovery. An exact counting argument showed that this arrangement could not meet the frozen significance threshold, even with a perfect match.

## What remains unresolved

The adapters did not qualify across every required condition. Success on other arrangements does not authorize use on real B/C data.

## What is in this folder

- [CODE-FREEZE.json](CODE-FREEZE.json): the rules, intended scope, or pinned setup.
- [STATUS.json](STATUS.json): explanation, outcome, or dated checkpoint.
- [BASELINE-BEFORE.json](BASELINE-BEFORE.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [FAILURE.json](FAILURE.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [PLAN.json](PLAN.json): the rules, intended scope, or pinned setup.
- [PRE-OUTCOME-IMPLEMENTATION.json](PRE-OUTCOME-IMPLEMENTATION.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [RUN.log](RUN.log): saved data or supporting evidence; field definitions come from the protocol/report.
- [run.py](run.py): implementation or checking code.
- [snapshot.mjs](snapshot.mjs): implementation or checking code.
- [attempt-2/](attempt-2) (25 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [bc-adapter-qualification-2026-10-25/STATUS.json](STATUS.json)
- [bc-adapter-qualification-2026-10-25/attempt-2/REPORT.txt](attempt-2/REPORT.txt)

[Full study file catalogue](../../catalog/studies/bc-adapter-qualification-2026-10-25.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
