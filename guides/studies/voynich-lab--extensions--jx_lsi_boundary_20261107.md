<!-- editorial-guide: 2026-11-07 -->

# Correcting paragraph handling before source comparison

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Separated layout markers from paragraph-start evidence and registered source collation before any boundary diagnostic.

## What we found

The associated run passed fifteen adapter fixtures, then failed source fidelity because differences and unresolved identities remained. The boundary diagnostic was not run.

## What remains unresolved

A conversion mismatch is not automatically proof that either editorial representation is wrong. The earlier failures were not overwritten or rescued.

## What is in this folder

- [EXECUTION.md](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/EXECUTION.md): the rules, intended scope, or pinned setup.
- [adapter.py](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/adapter.py): implementation or checking code.
- [authority.json](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/authority.json): saved data or supporting evidence; field definitions come from the protocol/report.
- [fixtures.py](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/fixtures.py): implementation or checking code.
- [run.py](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/run.py): implementation or checking code.
- [test_syntax.py](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/test_syntax.py): implementation or checking code.
- [registration/](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/registration) (7 archived files): Study rules, source/geometry registration, or pinned inputs. Read the timing and amendment receipts before assuming a stage was complete.
- [sources/](../../research/voynich-lab/extensions/jx_lsi_boundary_20261107/sources) (3 archived files): Published inputs, derived tables, or source records. The archive ledger explains omitted raw or protected material.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/results/jx/JX-20261107-LSIB-1/report.md](../../research/voynich-lab/results/jx/JX-20261107-LSIB-1/report.md)

[Full study file catalogue](../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../GUIDES.md) · [Terms used in the reports](../../GLOSSARY.md)
