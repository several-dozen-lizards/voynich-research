<!-- editorial-guide: 2026-11-07 -->

# Can structural alignment distinguish shared from different plaintext?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Used genuinely different fixed substitution tables and tested graph alignment on same-source and different-source known controls.

## What we found

Required qualification failed. Many different-source/two-key datasets were incorrectly classified as shared-source/two-key cases, despite significant mapping gains.

## What remains unresolved

Mapping gain under this comparison did not establish shared plaintext. No manuscript graph alignment or learned mapping was computed.

## What is in this folder

- [DECISIONS.md](DECISIONS.md): explanation, outcome, or dated checkpoint.
- [DEVELOPMENT_RESULTS.json](DEVELOPMENT_RESULTS.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [PLAINTEXT_SOURCES.json](PLAINTEXT_SOURCES.json): source attribution, access history, or rights context.
- [PROTOCOL.md](PROTOCOL.md): the rules, intended scope, or pinned setup.
- [QUALIFICATION.json](QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [QUALIFICATION_PROGRESS.json](QUALIFICATION_PROGRESS.json): checks or qualification evidence; read the scope of the gate.
- [QUALIFICATION_RESULTS.json](QUALIFICATION_RESULTS.json): checks or qualification evidence; read the scope of the gate.
- [QUALIFICATION_SUMMARY.csv](QUALIFICATION_SUMMARY.csv): checks or qualification evidence; read the scope of the gate.
- [REPORT.generated.md](REPORT.generated.md): explanation, outcome, or dated checkpoint.
- [REPORT.md](REPORT.md): explanation, outcome, or dated checkpoint.
- [author/](author) (3 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [data/](data) (720 archived files): Published inputs, derived tables, or source records. The archive ledger explains omitted raw or protected material.
- [plaintext/](plaintext) (4 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [results/](results) (1,040 archived files): Reports, saved outputs, or run records. A saved output can document a pass, a failure, or an unfinished run.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/extensions/phase8_alignment_v1/REPORT.md](REPORT.md)
- [voynich-lab/extensions/phase8_alignment_v1/DECISIONS.md](DECISIONS.md)

[Full study file catalogue](../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../GUIDES.md) · [Terms used in the reports](../../../../GLOSSARY.md)
