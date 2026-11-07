# Voynich Lab — Spec RD-v2: Circular Text, Pooled Direction, Seam Count, Paragraph Origin
**Date:** 2026-11-06
**Status:** Working draft for registration; exposure wording revised per Re. Not registered or run. See INTAKE.md for eligibility audit and execution details still to freeze. A new registration, not a patch. RD-v1 (STOP_FAILED_GATE) and RD-C2 (STOP_FAILED_GATE at unique_origin) are preserved unchanged and cited as prior evidence only.
**Lab rules (unchanged):** identical pipeline for every corpus; calibrate on known-answer data before touching Voynich; register before running; preserve failed calibrations, don't rescue them; report negatives in full.
**Scope:** circular loci only. Radial text is **HELD**: every radial locus is ≤10 words (≤8 in the inventory), and Latin also failed radial direction at that length. There is no RD-v2 radial arm.

---

## What carries forward

- **RD-v1:** the ZL circular direction bin at 41–80 passed (0.83, CI .726–.896). Latin circular was powered from 11–20. Every other ZL circular bin failed.
- **RD-C2:** unit mirror passed (1.00). Any-boundary localization passed at 41–80 (hit .935; end-to-end .875; null centered on 0). Unique origin **FAIL_UNSUPPORTED (n = 0)**: no held-out single paragraph lines reach 41 words.
- **Disclosed:** RD-C2's scope was chosen after RD-v1 results were seen. RD-v2's design choices below are motivated by those results, and that is labeled throughout. **No RD-v2 gate reuses an RD-v1 or RD-C2 pass as its own pass.**
- **Inventory (read-only, preflight):** 84 circular loci. By length: 1–2: 1; 3–5: 3; 6–10: 7; 11–20: 12; 21–40: 48; 41–80: 13; 81+: 0. Of the 13 long loci, 10 carry uncertainty annotations. The 3 clean ones are f72r3.14, fRos.20 and fRos.62.

---

## Exposure record (registered before anything runs)

Re reports no retained recall of the inventory details. Prior availability of transcriber metadata is recorded as provenance; it does not establish recollection or use of particular start positions. We do not automatically declare Re's annotation non-blind from availability alone.

For prospective visual annotation, record whether source start hints are consulted during annotation, and freeze the annotation before text-derived model outputs are viewed. An independent annotator is an optional stronger control. Describe the actual procedure without claiming historical never-exposed blindness.

No real-ring model scores have been computed in RD. The agent read raw transcription excerpts/comments during source intake. Re reports no retained recall of the inventory details.

---

## Target eligibility (frozen before any calibration is generated)

1. **Non-word-text exclusion:** exclude a locus if EVA codepoints per word < 2.0, or unknown words / words > 0.20. This catches f57v.3 (68 words, 72 codepoints, 16 unknown), the single-glyph ring. Log every excluded locus. The rule is stated generally and applied to all loci, not to f57v.3 by name.
2. **Uncertainty strata:**
   - **Clean:** `has_uncertainty = False`.
   - **Uncertain:** `has_uncertainty = True`. Eligible only if Arm U (below) passes.
3. Alternate branches and spurious loci are excluded. Missing spans make a locus ineligible for seam tests but keep it eligible for direction.
4. Loci are proxies for physical rings. Where several loci sit on one ring (`+Cc` continuation codes), Codex reports the grouping from the source. Physical-ring grouping is descriptive only and does not change eligibility.

---

## Signals

All signals are fit on training paragraph words only, using the RD-v1 folio-family split unchanged.

- **S-dir-word:** RD-v1 S-dir, unchanged.
- **S-dir-stem:** S-dir computed on collapsed words, keeping opening + core + ending *family* and dropping the near-free ending variant. The collapse uses the segmentation frozen in the Oct 22 scripts (`ending_consistency.py` / `abbrev_function.py`), imported by hash. If those scripts can't be bound by hash, S-dir-stem is NOT_RUN. **Latin gets the analogous collapse:** stem + inflection class, with the specific inflection dropped.
- **S-glyph:** a cross-boundary unit transition score. D over (last unit of word *i*, first unit of word *i+1*) pairs, using the RD-v1 S-int unit inventory, with the same smoothing as S-dir. This signal is robust to spaces that aren't plaintext word boundaries.
- **S-pos:** RD-v1, unchanged.
- **S-p1:** p/f gallows concentration on paragraph-first lines. A candidate unique-origin signal only.
- **S-m:** a line-final-form score for words ending in *-am / -om / -im / -m* and the line-final *-y / -dy* shift, from the Oct 22 frozen ending tables. A candidate seam and origin signal only.

**Registered predictions:**
- If endings are near-free decoration, **S-dir-stem lowers Voynich L_min relative to S-dir-word, while raising Latin's L_min**. That asymmetry is this spec's test of the endings hypothesis.
- S-glyph ≥ S-dir-word on Voynich at matched length.

---

## Phase 0 — Calibration (each arm gated separately; a failure stops only its own chain)

### Arm D — Per-locus direction, by signal

RD-v1 pseudo-ring construction, bins, support rules and pass rule (accuracy ≥ .80, lower CI ≥ .65), with a fresh seed. Run every signal on ZL and Latin. Report the L_min curve per signal. Per-locus direction calls are eligible only in bins where that signal passes.

### Arm P — Pooled direction (the main event for the 48 loci at 21–40)

- **Construction:** pseudo-ring *sets* matching the eligible real inventory: the same number of loci per length bin and the same family structure (pseudo-rings drawn from distinct held-out families where support allows).
- **Conditions, sealed:**
  - (i) all forward;
  - (ii) all reversed;
  - (iii) mixed, with 50% of members reversed.
- **Statistic:** clustered sign-randomization over folio families, weighted (n per cycle) and unweighted.
- **Pass:**
  - Recovers the majority direction in (i)/(ii) at ≥ .90 of sets.
  - In (iii), returns "no majority" at ≥ .90 of sets (false-majority rate ≤ .10).
- Run for each signal. **Pooled calls are about the set, never about any single locus.**

### Arm U — Uncertainty calibration

Rebuild Arm D and Arm P calibration from paragraph lines *including* uncertainty-bearing lines. Use the first alternative reading, and treat uncertain codepoints as a dedicated unseen token. If Arm U passes in the same bins, uncertain targets become eligible. If it fails, the uncertain stratum stays out. The clean stratum alone is descriptive: n = 3 at 41–80, so no calls.

### Arm K — Seam count (one vs several)

- Pseudo-rings built from exactly k complete lines, with k ∈ {1, 2, 3, 4, 5} sealed, length-matched to 21–80.
- **Estimator:** the number of S-pos seam peaks exceeding a per-ring threshold set from that ring's own within-ring word shuffles (99th percentile of the shuffled peak distribution), with peaks ≥ 3 words apart.
- **Pass:**
  - The k = 1 vs k ≥ 2 distinction has accuracy ≥ .80 and lower CI ≥ .65 in at least one bin.
  - Exact-k accuracy is reported, not gated.
- **This arm is required before any real-ring claim of the form "this ring is one unit" or "this ring is built from line-sized pieces."**

### Arm O — Unique origin on whole paragraphs

- **Units:** complete held-out paragraphs of 21–80 words, looped, rotated and reversed under a sealed key. The paragraph start is the unique origin. Internal line breaks remain as distractor boundaries.
- **Candidate signals, each tested separately, then one registered combination:**
  - S-pos start+end;
  - S-p1;
  - S-m (paragraph-final word);
  - combination = the sum of standardized per-signal scores, with equal weights fixed now.
- **Pass, per signal and for the combination:** hit within ±2 words of the paragraph start ≥ .50, lower clustered excess CI over chance > 0, shuffled-null excess interval inside [−.15, .15] and containing 0. Same support thresholds as RD-v1.
- **Important:** a signal passing here shows it finds *paragraph* starts. Applying it to rings assumes a ring was written as a paragraph-like unit. That assumption is reported, not tested, unless Arm K says k = 1 for that ring.

### Arm T — Transcriber-start baseline (descriptive calibration)

No calibration analog exists, since this is metadata. The registration fixes the later comparison: the agreement between the text-derived seam and `transcription_start_clock`, using ±2 words converted by the equal-spacing proxy, against a null of random offsets.

### Arm F — System-type fingerprint (descriptive, not gated)

Run the Arm D direction curves (all signals) on v5 generator outputs G2 (abbreviated Latin), G3 (notation/shorthand mix), G4 (verbose cipher), plus Naibbe, all at matched token counts. Report where Voynich's L_min curve sits among them. If the v5 generators aren't built and hash-bound, Arm F is NOT_RUN. **No decipherment claim follows from this arm.**

---

## Phase 1+ (closed until authorized after Phase 0)

When authorized, real-ring scoring uses only the arms and bins that passed:
- per-locus direction (Arm D bins);
- pooled direction (Arm P);
- seam count (Arm K);
- origin (Arm O signals that passed);
- transcriber-start and visual-mark agreement (Arm T, plus the exposure option chosen above).

BH q = .05 within each named outcome family. Rosettes (fRos, f85/f86) are reported as their own stratum alongside the pooled results. **The rosette feeder hypothesis is not tested here.**

## Outputs

- `results/ringdir/v2/<arm>/` with trial-level files, metrics, `report.md` and `STATUS.json`, all exclusive-create.
- **Summary table:** rows = signal × corpus. Columns:
  - L_min (Arm D);
  - pooled pass (Arm P);
  - Arm U pass;
  - Arm K pass;
  - Arm O pass per signal;
  - Arm F position.
- **Flag immediately** any null that passes a test it should fail.

## Out of scope

Radial text; decipherment, letter values or meaning; re-running other specs on corrected order; using Kay or another persona as an instrument.