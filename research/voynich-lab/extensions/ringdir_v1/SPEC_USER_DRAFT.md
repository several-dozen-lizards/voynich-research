# Voynich Lab — Spec RD: Reading Direction and Start Points in Circular Text
**Date:** 2026-11-06
**Status:** Draft for registration. Nothing in Phases 1–4 runs until Phase 0 passes and this spec is registered.
**Lab rules (unchanged):** identical pipeline for every corpus; calibrate on known-answer data before touching Voynich; register before running; preserve failed calibrations, don't rescue them; report negatives in full.
**Origin:** the defensible core of "spatial tracking inversion" (Deen, Zenodo 23931411), with the impairment story and Latin target removed. It connects to Re's hunch (26 Oct) that something from the rosettes feeds the system.
**Numbering:** "RD" is a side spec. v10 stays reserved for the cross-model label-alignment work named in v9.

---

## Purpose

Circular (ring) and radial (spoke) texts have no line breaks, so their transcribed direction and start point are the transcriber's choice. This spec asks three questions:

- **Q1 — Direction:** does ring text run in the transcribed direction, at the word-order level?
- **Q2 — Seam:** does each ring have a detectable *true start point*, and is it where the transcription starts?
- **Q3 — Kind:** does ring text behave like paragraph-line text at all, or like something else (label-like, list-like)?

**This spec does not attempt translation.** If it succeeds, its output is a corrected order and start point for ring loci, to be used by later specs.

**Registered predictions:**
- Q3: ring text carries a weaker but nonzero version of the line-position signature.
- Q1: the majority of rings run in the transcribed direction.
- Q2: no prediction.

Every outcome, including "no signal," gets reported and is informative.

---

## Hypotheses

| ID | Claim | Observable |
|---|---|---|
| H-word | Word *order* runs opposite to the transcription; glyphs inside words are normal | Pair-directionality score flips sign; word-internal signature unchanged |
| H-glyph | Glyph order *inside words* is reversed (mirror writing) | Word-internal positional signature flips (e.g. `q-`-type initials land word-final) |
| H-seam | The ring has a true start that differs from the transcription start | Line-start likelihood peaks at a non-zero offset, beyond the rotation null |
| H-null | Ring text has no directional or positional structure | All scores fall within shuffled-ring nulls |

H-glyph is expected to fail, since mirrored glyph shapes would have been visible to transcribers. It's included because it costs nothing and acts as an extra sanity check.

---

## Data

- **Transcription:** the lab's existing ZL / IVTFF files. Select loci by IVTFF locus type: circular and radial text. Codex should confirm the exact type codes in the files in use and log the codes and counts before any scoring.
- **Ring inventory:** a table with one row per locus. Columns: folio, locus ID, type (circular / radial), word count, glyph count, Currier hand (if annotated), scribe (if annotated), section, and the transcription start position as recorded in the source.
- **Paragraph reference:** all paragraph-type loci with line structure intact. Signatures are learned here.
- **Physical-mark annotation (Re, blind):** for each ring, mark any visible feature that could be a start (ornament, star, gap, size change, a figure's head) as a clock position relative to the transcription start. **Done and registered before Phase 2 output is viewed.** The exposure rule matches Phase 10's.

---

## Signals

All signals are learned on paragraph text only, and frozen before any ring is scored.

1. **Line-position signature (S-pos).** A classifier predicts a word's relative position in its line (first / interior / last, and continuous position 0–1) from word features. Features: glyph n-grams (1–3), length, initial glyph, final glyph. Trained with cross-validation grouped by folio. Output: P(line-start | word), P(line-end | word).
2. **Pair directionality (S-dir).** From paragraph word bigrams, compute D(a,b) = log P(a→b) − log P(b→a), smoothed. A sequence's direction score is the sum of D over adjacent pairs, normalized by pair count. Positive means it reads like forward text.
3. **Word-internal signature (S-int).** Glyph positional preferences inside words (initial / medial / final). A reversed-glyph check scores each word forward and mirrored.
4. **Paragraph-first-line signature (S-p1).** The p/f gallows concentration on paragraph first lines. This is used only as a descriptive check: do rings contain p/f, and where in the ring do they sit?

---

## Phase 0 — Calibration (must pass before anything else)

### 0.1 Pseudo-rings (known answer)

Build pseudo-rings from **held-out paragraph text** (folios excluded from signal training):

- Match the ring inventory's length distribution, and its hand and section where annotation allows.
- Concatenate consecutive lines into one word sequence and close it into a loop (drop line breaks).
- **Sealed key:** rotate each loop to a random start offset, and reverse word order in a random 50%. Codex writes the key to a sealed file before scoring and opens it only after scores are saved.
- Also build a **glyph-mirrored** subset (10%) to calibrate H-glyph.

### 0.2 Nulls

- **Within-ring word shuffle** of each real ring: keeps vocabulary, destroys order.
- **Shuffled pseudo-rings:** same treatment, for an expected-zero baseline at matched length.
- **Latin control:** the sectioned Latin control text built into loops the same way. This tests S-dir only, since Latin transcription line breaks carry no scribal line signature. It checks that S-dir detects word-order direction in a known natural language.

### 0.3 Power and pass criteria

- **Direction (S-dir):** accuracy recovering the sealed reverse flag on pseudo-rings, as a function of ring length. Define **L_min** as the shortest length bin with accuracy ≥ 0.80 and its lower 95% CI ≥ 0.65. Rings shorter than L_min are **underpowered**: they're reported, never called individually, and only enter pooled tests.
- **Seam (S-pos):** fraction of pseudo-rings where the estimated start falls within ±2 words of the true start. Pass if ≥ 0.50 at lengths ≥ L_min, against a chance rate of (5 / ring length). The ±2 window is registered now.
- **H-glyph:** mirrored subset detected at ≥ 0.90.
- **Nulls:** shuffled rings give direction accuracy within chance (binomial, p > 0.05) and no seam peak beyond the rotation null.
- **Latin control:** S-dir accuracy ≥ 0.80 at matched length.

If any criterion fails: stop, write up the failure, preserve all artifacts, and report back. Do not tune on real rings.

---

## Phase 1 — Q3: Do rings look like lines?

- Distribution of S-pos scores in ring words vs paragraph words, and vs label words (existing label annotations).
- A three-way probe (paragraph / ring / label) on spelling features, grouped by folio. Where do rings sit?
- Fraction of ring vocabulary attested in paragraphs vs labels.
- **Readout:** "line-like," "label-like," or "intermediate," using thresholds registered here. Line-like if ring–paragraph distance is less than half the ring–label distance on the probe's decision axis; label-like if the reverse holds; intermediate otherwise.

If rings come out label-like, Phases 2–3 still run but are flagged: a line-position signature may not apply to them.

---

## Phase 2 — Q1: Direction

- S-dir score per ring (forward as transcribed) and its permutation p-value against that ring's within-ring shuffles (≥ 1,000 shuffles).
- **Per-ring call** (only for length ≥ L_min): forward / reversed / undetermined, using Benjamini–Hochberg FDR at q = 0.05 across rings.
- **Pooled test:** a sign test on the S-dir scores of all rings, with length-weighted and unweighted versions reported.
- S-int forward vs mirrored for every ring (H-glyph).
- Split every result by locus type (circular vs radial), section (zodiac, cosmological, rosettes), and hand.
- **Radial loci:** report the inward-vs-outward reading the transcription implies, alongside the S-dir result.

---

## Phase 3 — Q2: Seam

For each ring at length ≥ L_min:

- At every rotation offset, compute seam likelihood: P(line-start) for the word at the offset plus P(line-end) for the word just before it, under the direction chosen in Phase 2 (transcribed direction if Phase 2 says "undetermined").
- **Seam statistic:** the peak value, against a null from the same ring's within-ring shuffles.
- **Report:** the peak offset, its significance (FDR across rings), and the offset in clock position.
- **Physical-mark check (confirmatory):** among rings with a significant seam, the fraction whose seam falls within ±2 words of a mark Re annotated, compared against a null of random offsets. This is the strongest possible result. Text-internal and visual evidence arriving at the same point independently is the "tripod" standard.

---

## Phase 4 — Descriptive: Rosette and zodiac pattern (no confirmatory claims)

- For rings with a called direction and a seam: tabulate direction and start position by folio. Is there one convention (for example, all clockwise, starting near the top), or several?
- **Rosettes foldout specifically:** do the circular and radial loci share direction conventions with the zodiac rings? Are seam words in the rosettes attested elsewhere in the manuscript, and where?
- Where p/f (S-p1) occur in rings, and their offset from the seam.

This phase is description to support Re's rosette hypothesis. Any test of that hypothesis needs its own registration.

---

## Outputs

- `results/ringdir/<phase>/` with metrics as CSV/JSON, plots, and `report.md` (tables first, prose second).
- `ring_inventory.csv` with every locus and its final calls (direction, seam offset, underpowered flag).
- **Corrected-order file:** ring loci reordered and rotated by the calls, as a *separate* transcription layer. The source transcription is never overwritten.
- **Single summary table:** rows = locus type × section. Columns:
  - n rings, n powered
  - share forward / reversed / undetermined
  - share with a significant seam
  - seam–mark agreement
  - Q3 class
- **Flag immediately (don't continue past)** any result where a null passes a test it should fail.

## Out of scope

- Any decipherment, letter values, or meaning claims
- Re-running other specs on the corrected order. That needs its own registration, after RD results are in.
- Using Kay or another persona as an instrument