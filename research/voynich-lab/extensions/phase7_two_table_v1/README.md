<!-- editorial-guide: 2026-11-07 -->

# Can two fitted cipher tables reproduce the A/B contrast?

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Selected table settings using training data, then compared fixed two-table and one-table arms on separate evaluation material.

## What we found

The selector chose the same setting for both A and B, making the selected two-table arms exact aliases of their one-table controls. The resulting probes did not reproduce the manuscript's A/B separation.

## What remains unresolved

This bounded selector did not instantiate distinct chosen tables. It does not reject unrestricted pairs of codebooks, and the published tables were developed with Voynich statistics rather than being blind controls.

## What is in this folder

- [DECISIONS.md](DECISIONS.md): explanation, outcome, or dated checkpoint.
- [PLAINTEXT_SOURCES.json](PLAINTEXT_SOURCES.json): source attribution, access history, or rights context.
- [PROBE_REPLAY_QUALIFICATION.json](PROBE_REPLAY_QUALIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [PROTOCOL.md](PROTOCOL.md): the rules, intended scope, or pinned setup.
- [REPORT.md](REPORT.md): explanation, outcome, or dated checkpoint.
- [SOURCES.md](SOURCES.md): source attribution, access history, or rights context.
- [STATUS.json](STATUS.json): explanation, outcome, or dated checkpoint.
- [VERIFICATION.json](VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report_verify.py](report_verify.py): explanation, outcome, or dated checkpoint.
- [A_B_differences.csv](A_B_differences.csv): saved data or supporting evidence; field definitions come from the protocol/report.
- [author/](author) (4 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [data/](data) (30 archived files): Published inputs, derived tables, or source records. The archive ledger explains omitted raw or protected material.
- [fit_cache/](fit_cache) (234 archived files): Environment, dependency, or cache-related material retained in this snapshot; it is not a separate research result.
- [instrument/](instrument) (87 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [plaintext/](plaintext) (2 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/extensions/phase7_two_table_v1/REPORT.md](REPORT.md)
- [voynich-lab/extensions/phase7_two_table_v1/STATUS.json](STATUS.json)

[Full study file catalogue](../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../GUIDES.md) · [Terms used in the reports](../../../../GLOSSARY.md)
