# Voynich handoff — 6 Nov 2026 (RD series)

Written by Reed for Re; corrected against saved receipts. Covers RD-v1, RD-C2 and RD-v2 Phase0. Calibration only: no real-ring text has been scored. Radial text is HELD; the inventory maximum is8 words, and short radial direction did not qualify in ZL or Latin.

Specs are preserved at `extensions/ringdir_v1/SPEC_USER_DRAFT.md` and `extensions/ringdir_v2/registration/SPEC_WORKING_DRAFT.md`, with executable amendments in their registration folders. Earlier runs remain unchanged.

## Run outcomes

- RD-v1: STOP_FAILED_GATE at the direction batch because radial gates failed. ZL circular word direction qualified only at41–80 (83%); Latin qualified from11–20.
- RD-C2: circular41–80 scope chosen after RD-v1 and disclosed. Unit mirror100%; any-boundary localization93.5%, end-to-end87.5%. Unique line origin FAIL_UNSUPPORTED (n=0), because eligible single lines do not reach41 words. Its result locates any retained line boundary, not a unique historical ring start or a seam count.
- Original inventory:84 circular loci, bins1–2:1;3–5:3;6–10:7;11–20:12;21–40:48;41–80:13. Ten of the13 long loci have uncertainty annotations; clean long loci are f72r3.14, fRos.20 and fRos.62.
- RD-v2's general eligibility rules exclude f57v.3, f57v.5 and f70r1.1. Remaining81 loci include12 long (3 clean,9 uncertain). At6–80 there are **78 eligible loci:26 clean and52 uncertain**, still unscored and subject to later authorization/target testing.
- RD-v2 clean S-glyph direction passes6–10,11–20,21–40,41–80, at84.0%,85.5%,97.5%,97.5%. Uncertainty-inclusive rates are **83.0%,84.0%,95.5%,98.5%**, with the same passing bins. Both instruments test word-order direction: S-glyph uses cross-word junction features; S-dir-word uses whole-word bigrams.
- RD-v2 ZL whole-word direction fails all bins;41–80 gives77.5%, clustered95% CI64.4–87.3%. Pooled direction does not qualify in any ZL chain; limited family-level power remains a material constraint.
- Isolated, known-direction S-p1 paragraph-origin passes21–40:98 complete paragraphs;57.1% hits vs16.9% mean chance; excess95% CI31.0–48.8 percentage points. Word-directed end-to-end hits38.8% (descriptive). At41–80 isolated hits41.7%, below the50% threshold. S-pos origin does not qualify.
- Seam count is FAIL_UNSUPPORTED: ZL k=1 has3 examples from1 family at21–40 and0 at41–80. No single-vs-multiple-unit calibration claim follows.
- Stem collapse, S-m and the specified combination are NOT_RUN_MISSING_SOURCE; exact Oct22 sources were not replaced. Arm T is registered for a later descriptive comparison only.
- A Windows path-label error affected aggregate report assembly after all calibration chains completed. A separately hash-bound report-only finalizer completed it; no calibration was rerun.

## Descriptive direction fingerprint

| System | Whole-word L_min | Junction-feature L_min |
|---|---:|---:|
| Latin |6|41|
| G2 abbreviated Latin |11|41|
| G3 notation/shorthand mix |11|41|
| G4 verbose cipher |21|FAIL|
| Naibbe |FAIL|FAIL|
| ZL |FAIL|6|

The table describes recovery of known word-order reversals by two feature sets. In these fixed realizations, ZL is recovered more effectively from junction features; Latin and G2–G4 qualify whole-word recovery, while Naibbe qualifies neither. “Weak word order” should not be read as absence of word-order structure: S-glyph itself measures an order asymmetry. The fixed generator settings and differing native unit representations limit cross-system generalization. None of these four tested generator realizations reproduces ZL's qualification pattern; this is not mechanism identification or decipherment.

Cross-word sandhi, non-plaintext spaces and untested generation mechanisms remain candidates. Agreement with an Oct22 junction-rule result is pending source reconciliation, not an established replication claim.

## Next work and permissions

1. Register a prospective rotated-crop visual annotation procedure before any real-ring model output: crop/rotation rules, annotation criteria and unblinding must be frozen. This is a **new proposal**, not an already registered “option c.” Re reports no retained recall of inventory details; record actual use of start hints rather than automatically declaring her annotation non-blind.
2. Any later Phase1 proposal concerns per-locus S-glyph direction at the qualified6–80 bins,78 eligible loci split26 clean/52 uncertain, with BH q=.05. Pooled calls are unavailable. No Phase1 authorization is implied by this handoff.
3. Register G5/G6 fingerprint extension. For G5 use the **pinned published Timm–Schinner implementation**, not the built-in v5 copy-modify surrogate. G6 is the existing v5 table/grille engineering implementation. Report their fixed configurations and fidelity limits.
4. New registration: end-to-end S-p1 paragraph-origin calibration using **S-glyph-inferred direction**, rather than assuming the known orientation or reusing the word-directed38.8% result as its outcome.
5. Seek exact Oct22 `ending_consistency.py`, `abbrev_function.py`, `am_replaces.py` and table provenance, possibly on the ChatGPT-handoff side. Unbound signals stay NOT_RUN.
6. If seam count is revisited, paragraph-unit count needs a new calibration design; do not manufacture unsupported long single lines.

Prior result paths: `results/ringdir/{phase0_v1,circular_v2,preflight,v2}/`. Canonical RD-v2 summary and verification are `results/ringdir/v2/summary.csv` and `VERIFICATION.json`.
