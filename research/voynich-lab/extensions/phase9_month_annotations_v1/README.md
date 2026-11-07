<!-- editorial-guide: 2026-11-07 -->

# Qualifying a matcher for the later month annotations

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested mapping recovery and the complete language/family search on planted month-label datasets and shuffled negatives.

## What we found

All thirty-two calibration cells passed. A separate strict receipt check failed because a mutable progress file had mistakenly been included in the frozen manifest; that defect was disclosed while immutable inputs remained unchanged.

## What remains unresolved

No annotation target fit ran in this calibration folder. The later Latin-script annotations are a separate track from the native Voynich text, and the finite controls do not identify its language.

## What is in this folder

- [DECISIONS.md](DECISIONS.md): explanation, outcome, or dated checkpoint.
- [PROTOCOL.md](PROTOCOL.md): the rules, intended scope, or pinned setup.
- [QUALIFICATION.json](QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [REPORT.md](REPORT.md): explanation, outcome, or dated checkpoint.
- [RESULTS.json](RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [RESULT_HASHES.json](RESULT_HASHES.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [SOURCES.json](SOURCES.json): source attribution, access history, or rights context.
- [SOURCE_RETRIEVAL.json](SOURCE_RETRIEVAL.json): source attribution, access history, or rights context.
- [SOURCE_RETRIEVAL_2.json](SOURCE_RETRIEVAL_2.json): source attribution, access history, or rights context.
- [SOURCE_RETRIEVAL_3.json](SOURCE_RETRIEVAL_3.json): source attribution, access history, or rights context.
- [author/](author) (3 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [data/](data) (320 archived files): Published inputs, derived tables, or source records. The archive ledger explains omitted raw or protected material.
- [results/](results) (640 archived files): Reports, saved outputs, or run records. A saved output can document a pass, a failure, or an unfinished run.
- [targets/](targets) (22 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/extensions/phase9_month_annotations_v1/REPORT.md](REPORT.md)
- [voynich-lab/extensions/phase9_month_annotations_v1/DECISIONS.md](DECISIONS.md)

[Full study file catalogue](../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../GUIDES.md) · [Terms used in the reports](../../../../GLOSSARY.md)
