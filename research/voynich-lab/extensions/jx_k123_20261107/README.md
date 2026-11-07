<!-- editorial-guide: 2026-11-07 -->

# Code and registration for paragraph junction tests

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Bound the paragraph specificity, reading-robustness, and annotated-subgroup comparisons before execution.

## What we found

The associated result records an aggregate specificity pass but failed reading robustness and mixed subgroup support. A later diagnostic then exposed an adapter/source-semantics limitation.

## What remains unresolved

Use the separately stored K123 and K2D result reports together. Numerical reproduction does not certify paragraph interpretation, language, or spacing meaning.

## What is in this folder

- [verify_k123.py](verify_k123.py): checks or qualification evidence; read the scope of the gate.
- [ENGINEERING.json](ENGINEERING.json): checks or qualification evidence; read the scope of the gate.
- [EXECUTION.md](EXECUTION.md): the rules, intended scope, or pinned setup.
- [run_k123.py](run_k123.py): implementation or checking code.
- [test_k123.py](test_k123.py): implementation or checking code.
- [intake/](intake) (7 archived files): A preserved sub-study or supporting work package; follow its local report, protocol, and status records.
- [registration/](registration) (5 archived files): Study rules, source/geometry registration, or pinned inputs. Read the timing and amendment receipts before assuming a stage was complete.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/results/jx/JX-20261107-K123-1/report.md](../../results/jx/JX-20261107-K123-1/report.md)
- [voynich-lab/results/jx/JX-20261107-K2D-1/report.md](../../results/jx/JX-20261107-K2D-1/report.md)

[Full study file catalogue](../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../GUIDES.md) · [Terms used in the reports](../../../../GLOSSARY.md)
