# Voynich Lab — Spec JX-K2R: Transcription Robustness Against the Original Stolfi H Archive
**Date:** 2026-11-07
**Status:** Draft for registration. A new registration. **Not a rerun, repair or replacement of K2.**
- JX-20261107-K123-1: K2 = FAIL_ROBUSTNESS, preserved.
- JX-20261107-LSIB-1: STOP_FAIL_SOURCE_FIDELITY, preserved.
- This is a result-motivated follow-up on laboratory-exposed material, and it is labeled that way in every output.

**Lab rules (unchanged):** identical pipeline for every corpus; calibrate on known-answer data before touching Voynich; register before running; preserve failed calibrations, don't rescue them; report negatives in full.

---

## Why this exists

K2 compared ZL against the LSI edition of Takahashi's H reading. The LSI adapter later failed validation (JX-20261107-LSIB-1). Collation of LSI against the original Stolfi 1.6e6 interlinear (sha256 `309e717d…02f0`) **using exact locus IDs, without a reviewed crosswalk**, found:
- 335 loci with differences (330 involving both the glyph stream and word-boundary positions);
- 395 unresolved identities.

**These counts are not an estimate of altered spacing.** If renumbering pairs two different manuscript lines under one ID, the glyph stream and the boundary positions both disagree. Misalignment and editorial change produce the same signature. "0 unparsed H records" establishes syntactic parsing only, not physical alignment, completeness or manuscript fidelity. The original Stolfi H is itself an edited archival rendering of Takahashi; it avoids the later conversion layer and nothing more.

**Defensible position:** K2 failed as registered. Whether that failure reflects the readings, the panel or the source correspondence is **unresolved**, and the shortfall can't be attributed to spacing. K2-R qualifies source identity and spans first, then (conditionally) asks the robustness question against original H.

---

## Stage 1 — Source qualification (gate; nothing is scored before it passes)

1. **Parser:** read the original Stolfi 1.6e6 interlinear directly (no LSI). Bind format documentation and authored engineering fixtures, covering: locus IDs, transcriber codes, word-break markers (definite and uncertain), paragraph and line markers, alternates, and illegible glyphs.
2. **Reading inventory:** list every transcriber code present, with:
   - coverage of ZL-eligible paragraph words, overall and in held-out families per bin;
   - independence status, assigned **only from documented provenance** (published descriptions of how the reading was produced, the archive documentation). Each status carries a cited source. Transcriber codes alone never establish independence. Undocumented means **unknown**, and unknown readings don't count as independent.
3. **Locus crosswalk (ZL ↔ interlinear), reviewed and frozen before any comparison of glyph content:**
   - Build it from **content-blind evidence only**: folio, panel, line order within a locus, locus type, line counts, and documented renumbering or locus-convention tables from either archive's documentation.
   - **Glyph-stream similarity may not be used to choose pairings.** That would build agreement into the comparison.
   - Every pairing gets a confidence label (documented / structural / ambiguous). Ambiguous pairings are **held, not guessed**.
   - The crosswalk is reviewed (by Re or a designated reviewer), hashed and frozen. Only then are any glyph streams compared.
3b. **Span validation:** on crosswalked pairs, report the glyph-stream agreement rate as a **diagnostic of crosswalk quality**. If a documented or structural pairing shows near-total glyph disagreement, it's flagged as a probable misalignment and moved to held. That rule is registered now and applied mechanically.
4. **Uncertain spaces:** each reading's own uncertain-space marker is run joined and split, matching the ZL convention.
5. **Gate:** **H** must map cleanly on ≥ 30 distinct evaluation windows and ≥ 8 held-out families in **each** of the 11–20 and 21–40 bins. Other readings are eligible as **secondary** readings only if they clear the same support. Readings that don't clear it are inventoried, not scored.

If H fails the gate: STOP_FAIL_SOURCE, preserve everything and report coverage. No fallback to LSI.

---

## Stage 2 — Robustness test

### Design (frozen)

- **Signal:** RD-v2 S-glyph direction, with the instrument unchanged. Units are the RD-v1 S-int inventory (13 clusters, longest match, then single codepoints), in raw and rank-matched (12-class) variants.
- **Family split:** RD-v1 folio-family split unchanged.
- **Identical spans:** evaluation windows are defined on **locus identity**, as complete loci. A window enters only if both readings fall in the same length bin by their own word counts. Windows are built once and shared by every reading.
- **Two training regimes per reading:**
  - **Common-training (primary):** fit only on training loci present in both readings, with ZL restricted equally.
  - **Native-training (secondary):** fit on all eligible training text in that reading.
- **Panel-restriction comparison (descriptive):** ZL scored on its full baseline panel vs on the common-locus panel. This isolates how much difficulty comes from the panel itself.
- Sealed reversal keys, fresh seed, scores saved and hashed before any key is opened.

### Thresholds (unchanged from K2)

Per reading, per bin, raw and matched:
- accuracy ≥ .80;
- lower family-bootstrap 95% bound ≥ .65 (with the K3 adjustment as registered in K123-1);
- support ≥ 30 distinct windows and ≥ 8 families.

### Primary gate

**K2R-PASS** if **H under common-training** meets every threshold in both bins, in both raw and matched variants.

The secondary readings and native-training results are reported in full. They don't gate, and they can't rescue a primary failure.

### Paired analysis (descriptive)

- Per-trial agreement between ZL and each reading.
- **Paired accuracy difference** (ZL minus reading), with a family-bootstrap 95% CI.
- Labeled **"comparable"** if the CI lies within ±5 points. This is a label, not an equivalence gate.

### Strata

- Currier A, Currier B and the supported scribes run as **separate chains**, exactly as in K3.
- Per-stratum results are descriptive. **No A–B difference claim is made here.** That needs its own registered contrast test.

---

## Stage 3 — Boundary-disagreement diagnostic (runs only if Stage 1 passes; independent of the Stage 2 outcome)

1. On common loci, align ZL and H **unit streams with spaces removed**, using a minimum-edit alignment with fixed costs (registered).
2. Classify every junction as:
   - **agreed** (a space in both);
   - **ZL-only**;
   - **H-only**.
3. For held-out windows, compute each junction's S-glyph D-contribution under the common-training model.
4. **Report:**
   - the share of total direction evidence carried by agreed vs disputed junctions;
   - mean |D| per class, with family-clustered CIs;
   - direction accuracy recomputed on agreed junctions only.

**Interpretation, registered now:** if direction evidence concentrates at disputed junctions, that **supports an association** between the effect and transcription decisions. It does not by itself show that transcribers created the effect, since manuscript ambiguity could produce both the disagreements and the junction differences. If accuracy on agreed junctions alone stays above threshold, that argues against a spacing-decision explanation.

---

## Registered predictions (Reed, first stated 2026-11-07 ~00:46 ET, before any K2-R result; frozen with this registration's hash before Stage 2 scoring)

1. Under identical spans and common training, **H comes within ~2 points of ZL** at 11–20.
2. ZL's drop from the baseline panel to the common-locus panel **tracks the Currier A share** of the panel. Reported descriptively: A share and per-stratum accuracy for each panel.
3. **K2R-PASS** in aggregate.
4. **Stage 3:** accuracy on **agreed** junctions alone stays ≥ .80 at 21–40.

If prediction 1 fails (H stays well below ZL, matched for training and spans), the transcription explanation is back on the table. That gets reported plainly.

---

## Outputs

- `results/jx/K2R/` with source inventory, collation and mapping ledgers, fixture results, sealed keys, trial-level scores, metrics, `report.md`, `STATUS.json` and `VERIFICATION.json`, all exclusive-create.
- **Summary table:** rows = reading × training regime × stratum. Columns per bin and variant: accuracy, lower bound, support, pass.
- Plus the paired-difference table and the Stage 3 junction-class table.

## Out of scope

The I-phase (conditioning) and any spacing interpretation remain CLOSED. Also out of scope: I2v2 target use, real-ring scoring and radial text (HELD), language ranking (all 36 frozen rows stay NP), translation, and using Kay or another persona as an instrument.