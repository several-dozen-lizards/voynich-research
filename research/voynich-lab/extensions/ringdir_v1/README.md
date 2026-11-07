<!-- editorial-guide: 2026-11-07 -->

# Design and initial calibration for ring direction

> Plain-English reading guide to the archived snapshot. The linked reports contain the full rules, results, and qualifications. This guide is editorial material added after the original archive.

## What we tested

Reviewed whether proposed direction and start statistics could identify what they claimed, then bound an amended calibration.

## What we found

The preflight exposed rotation-invariant and non-unique-origin problems. The subsequent first calibration passed some circular direction gates but failed radial direction, triggering its stop rule.

## What remains unresolved

The source inventory is not a set of adjudicated independent rings. No corrected manuscript order or real-ring score followed.

## What is in this folder

- [verify_preflight.py](verify_preflight.py): checks or qualification evidence; read the scope of the gate.
- [verify_rd_phase0.py](verify_rd_phase0.py): checks or qualification evidence; read the scope of the gate.
- [DESIGN_REVIEW.md](DESIGN_REVIEW.md): saved data or supporting evidence; field definitions come from the protocol/report.
- [RD_AMENDED.md](RD_AMENDED.md): saved data or supporting evidence; field definitions come from the protocol/report.
- [SPEC_USER_DRAFT.md](SPEC_USER_DRAFT.md): the rules, intended scope, or pinned setup.
- [preflight.py](preflight.py): implementation or checking code.
- [rd_phase0.py](rd_phase0.py): implementation or checking code.
- [test_rd_phase0.py](test_rd_phase0.py): implementation or checking code.
- [registration_v1/](registration_v1) (5 archived files): Study rules, source/geometry registration, or pinned inputs. Read the timing and amendment receipts before assuming a stage was complete.

File formats: JSON stores structured values or settings; JSONL stores one event/trial record per line; CSV/TSV stores tables. Python and JavaScript files are code. Compressed `.gz`/`.xz` files retain the original bytes; the repository restoration helper can unpack them. HTML reports may require a local browser rather than GitHub’s file viewer.

## Read the evidence

- [voynich-lab/results/ringdir/preflight/report.md](../../results/ringdir/preflight/report.md)
- [voynich-lab/results/ringdir/phase0_v1/report.md](../../results/ringdir/phase0_v1/report.md)

[Full study file catalogue](../../../../catalog/studies/voynich-lab.md) · [All plain-English guides](../../../../GUIDES.md) · [Terms used in the reports](../../../../GLOSSARY.md)
