# Voynich handoff — 6 Nov 2026 (RD series)

**Revision:** REV2. Saved separately from the registered handoff; receipts remain authoritative.

**Written:** by Reed for Re. Revised the evening of 6 Nov to match Codex's receipt-corrected handoff (`voynich-lab/report/HANDOFF_RD_2026-11-06.md`) and to add RD-FO3. **Where this file and the receipts disagree, the receipts win.**
**Status:** calibration only. **No real-ring text has been scored.** Radial text is HELD: the inventory maximum is 8 words, and short radial direction qualified in neither ZL nor Latin.
**Specs (drafts):** `voynich-spec-ring-direction-2026-11-06.md`, `voynich-spec-rd-v2-circular-2026-11-06.md`, `voynich-spec-jx-junction-2026-11-06.md`. The executable registrations live in the lab's registration folders. **The draft specs aren't registrations.**
**Candidate register:** `voynich-candidate-languages-freeze-2026-11-06.md` (draft; freeze before JX).

---

## 1. Run outcomes

**RD-v1.** STOP_FAILED_GATE (the radial gates failed). ZL circular word direction qualified only at 41–80 (83%); Latin qualified from 11–20.

**RD-C2.** Circular 41–80 only; the scope was chosen after RD-v1 and disclosed.
- Unit mirror: 100%.
- Any-boundary localization: 93.5%; end-to-end 87.5%. This locates *some* retained line boundary. It does not locate a unique ring start, and it does not count seams.
- Unique line origin: FAIL_UNSUPPORTED (n = 0).

**Inventory and eligibility.**
- 84 circular loci. By word count:

  | 1–2 | 3–5 | 6–10 | 11–20 | 21–40 | 41–80 |
  |---:|---:|---:|---:|---:|---:|
  | 1 | 3 | 7 | 12 | 48 | 13 |

- RD-v2's rules excluded f57v.3, f57v.5 and f70r1.1, leaving 81 loci. Of those, 12 are long (3 clean, 9 uncertain).
- **At 6–80 words: 78 eligible loci, 26 clean and 52 uncertain**, all unscored.
- The clean long loci are f72r3.14, fRos.20 and fRos.62.

**RD-v2 Phase 0.**
- ZL S-glyph direction passes 6–10, 11–20, 21–40 and 41–80:
  - clean: 84.0 / 85.5 / 97.5 / 97.5%;
  - uncertainty-inclusive: 83.0 / 84.0 / 95.5 / 98.5%.
- ZL whole-word direction fails every bin (41–80: 77.5%, CI 64.4–87.3).
- Pooled direction doesn't qualify in any ZL chain. Limited family-level power is a material constraint.
- Isolated (known-direction) S-p1 origin passes at 21–40: 98 paragraphs, 57.1% vs 16.9% chance.
  - Word-directed end-to-end: 38.8% (descriptive).
  - 41–80 isolated: 41.7%, which fails.
  - S-pos origin fails.
- Seam count: FAIL_UNSUPPORTED.
- Stem collapse, S-m and the combination: NOT_RUN_MISSING_SOURCE.
- Arm T is registered as descriptive only.
- A Windows path-label error hit report assembly. It was completed by a hash-bound report-only finalizer, with no calibration rerun.

**RD-FO3 (new registered follow-up).**
- **G5, the pinned published Timm–Schinner Java implementation:** whole-word FAIL, junction-feature FAIL. Its published rules and initialization are retained; the literal seed line is excluded.
- **G6, a fixed simplified table/grille:** whole-word FAIL, junction-feature FAIL.
- **S-glyph-directed S-p1 origin, end-to-end:**

  | Corpus | Bin | n | Hit | Chance | Excess CI | Result |
  |---|---|---:|---:|---:|---|---|
  | ZL | 21–40 | 98 | 50.0% | 16.9% | .218–.436 | **PASS, exactly at the 50% performance threshold** |
  | ZL | 41–80 | 36 | 44.4% | 9.7% | .185–.479 | FAIL |
  | Latin | 21–40 | 177 | 16.4% | 16.6% | −.058–.066 | FAIL; artificial layout |
  | Latin | 41–80 | 85 | 14.1% | 9.7% | −.017–.109 | FAIL; artificial layout |

- "Marginal" refers to meeting the performance cutoff exactly; the excess-over-chance interval excludes zero.
- The Latin control has no useful paragraph-first p/f enrichment: fitted rates are 16.377% on first lines versus 16.352% elsewhere. This is a measured control limitation, not a claim that Latin lacks p/f letters.
- Verification: 4,000 direction trials and 396 origin trials, including G5 provenance and preservation of prior runs.
- This calibrates paragraph origin, not ring starts. Paragraph-to-ring transfer is untested.

## 2. Descriptive direction fingerprint

| System | Whole-word L_min | Junction-feature L_min |
|---|---:|---:|
| Latin | 6 | 41 |
| G2 abbreviated Latin | 11 | 41 |
| G3 notation/shorthand mix | 11 | 41 |
| G4 verbose cipher | 21 | FAIL |
| Naibbe | FAIL | FAIL |
| G5 published copy-and-modify | FAIL | FAIL |
| G6 table/grille | FAIL | FAIL |
| **ZL** | **FAIL** | **6** |

**Correct framing.** Both feature sets measure recovery of known *word-order* reversals:
- In ZL, word order is recovered far better from **junction features** (word-final unit → next word-initial unit) than from **whole-word identity**.
- Latin and G2–G4 show the reverse: whole-word recovery qualifies first.
- None of the tested generator realizations reproduces ZL's combination of qualified junction-feature recovery and unqualified whole-word recovery.

"Weak word order" is the wrong phrase. The order structure is present, carried at the boundaries.

**Limits.** These are fixed generator realizations with differing native unit representations, so this is not mechanism identification. G5 is a single published realization, and G6 is simplified.

**Live candidates:** cross-word sandhi, spaces that aren't plaintext word boundaries, and untested generation mechanisms. **Agreement with the Oct 22 junction-rule result is pending source reconciliation**; it is not an established replication.

## 3. Next work (no authorization implied)

1. **Freeze the candidate-language register** (Re's review), hashed before any JX result.
2. **Register JX:** Phase 0 plus the K-phase kill tests (junction specificity, robustness across transcriptions and spacing, strata).
3. **Propose and register the rotated-crop visual annotation procedure** before any real-ring model output. Freeze crop and rotation rules, annotation criteria and unblinding. Record which start hints Re actually used, rather than declaring her non-blind by default.
4. **A later Phase 1 proposal:**
   - per-locus S-glyph direction at 6–80 on the 78 eligible loci (26 clean / 52 uncertain), BH q = .05;
   - junction-directed S-p1 origin at 21–40, labeled marginal and paragraph-transfer-assumed.
   - Pooled calls are unavailable.
5. **Optional:** a G5 parameter sweep, for a family-level rather than single-realization result.
6. **Find the exact Oct 22 sources** (`ending_consistency.py`, `abbrev_function.py`, `am_replaces.py` and table provenance), possibly on the ChatGPT-handoff side. Unbound signals stay NOT_RUN.
7. Seam count: if it's revisited, design a paragraph-unit count. Don't manufacture long single lines.

**Paths (Re's machine):** `voynich-lab/results/ringdir/{phase0_v1, circular_v2, preflight, v2, followup_v3}/`