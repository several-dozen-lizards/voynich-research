<!-- editorial-guide: 2026-11-07 -->

# The adapter-semantic diagnostic stop

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Tested the original adapter's meaning of layout locators before downstream source and reading decompositions.

## What we found

Both mandatory semantic fixtures failed because layout markers were treated as paragraph-start evidence. The run stopped and downstream diagnostics remained unrun.

## What remains unresolved

The earlier numerical results were preserved, but their reproducibility did not certify source semantics. No repair was substituted into this failed run.

## What is in this folder

- [STATUS.json](STATUS.json): explanation, outcome, or dated checkpoint.
- [VERIFICATION.json](VERIFICATION.json): checks or qualification evidence; read the scope of the gate.
- [report.md](report.md): explanation, outcome, or dated checkpoint.
- [ARTIFACT_MANIFEST.json](ARTIFACT_MANIFEST.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [events.jsonl](events.jsonl): saved data or supporting evidence; field definitions come from the protocol/report.
- [D-panel/](D-panel) (1 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [D-reading/](D-reading) (1 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [D-training/](D-training) (1 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [adapter/](adapter) (3 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [source_fidelity/](source_fidelity) (1 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/results/jx/JX-20261107-K2D-1/report.md](report.md)
- [voynich-lab/results/jx/JX-20261107-K2D-1/STATUS.json](STATUS.json)

[Full study file catalogue](../../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../../GUIDES.md) · [Terms used in the reports](../../../../../GLOSSARY.md)
