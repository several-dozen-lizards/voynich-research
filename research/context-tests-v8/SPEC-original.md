# Voynich spec v8: context tests (function vs content words, plant parts, entry formula)

**For:** a fresh session, or a loop worker.
**Written:** 25 Oct 2026 (Reed, for Re).
**Status:** frozen design. **T1 must be frozen before the v4 ratings are joined to any text.** T2 and T3 are independent and can run in parallel.
**Tier:** retrospective in text (v100/v102). T1 and T2 are **prospective in the image variable only.** T3 uses an **internal discovery/confirmation split** that is fixed now.

---

## 0. Context you won't have

- **The sh→qok rule** (an sh-opening word followed by a qok-opening word) has roughly **constant strength** across scribes 1–3, Currier A and B, and the sections, at an MH OR of about 1.7–2.2. A common-OR model **out-predicts** context-specific ORs on held-out folios (v4.2-C and the predictive comparison).
- **What varies with context is word *frequency*:** qok follows only about 3% of origins on scribe 1's herbal pages, against about 30% in bath. Earlier: *qo-* goes with recipe-type text, and *ot-/ok-* are enriched in labels across all subjects.
- **Working idea:** the script has a context-invariant structural layer and a context-sensitive vocabulary layer. Separating **function-like** from **content-like** word classes is a standard early decipherment step. The pictures give an independent context variable, so it can be done here.
- **v4 has registered 1,145 shared lines** (168 pages) with blind geometry, and image ratings are underway (v4, v4.1 gates G6/G2, v4.2). v8 T1 reuses those labels.

## 1. House rules

1. Freeze → outcome-blind support → controls at real support → outcomes. Hash each phase.
2. H and F are separate readings, scored separately, never pooled. Headline results need both.
3. Keep every failure and abstention. "Not estimable" is not a negative.
4. Reserved zodiac folios stay excluded, the same as everywhere else.
5. No meanings, no sound values, no plant IDs.
6. **Error budget:** the global ledger isn't built yet. Each test family below uses α = .05 (Holm within the family) unless Re authorises otherwise. That's recorded in `BUDGET.json` as separate from α_V.

---

## T1: which word classes track the pictures? (function vs content)

### T1.1 Data

- **Lines:** v4's registered lines, P-units only, with the v4 line-context labels (PL / VE / FG / CE / OT / NO). They're usable only if the v4.1 gates pass: G6 for the multi-class analyses, G2 for PL vs not-PL.
- **Word slots:** every readable word in a registered line **except the line-initial word** (line-start effects are known). Unknown slots are excluded and counted.

### T1.2 Word classes (frozen)

- **Openers:** qok, qo (but not qok), ot, ok, d, ch, sh, other-gallows (k / t / p / f initial), y, o (but not ot/ok/qo), a, s, other.
- **Ending families:** -aiin / -ain / -air / -ar / -al (a-family); -edy / -eey / -ey / -y (y-family); -ol / -or; other.

Total: **13 opener classes + 4 ending groups = 17 classes.**

### T1.3 Primary (directional, one test per reading)

> **T1-P:** within folio, the qok-opener rate per word slot is **higher** in lines labelled FG or VE than in lines labelled PL or NO.

- **Statistic:** MH log rate ratio over the strata, one-sided.
- **Strata:** folio × length bin (short/normal, from the v4 wrap flag).
- **Null:** permute line labels **among lines within each folio**, keeping each line's words together. Use at least 10,000 permutations.
- **Folios used:** those with at least one FG/VE line **and** at least one PL/NO line, each side having at least 30 word slots.
- **Gate:** at least 8 such folios, with no folio over 25% of the weight. Otherwise, NOT ESTIMABLE.
- **Headline:** H and F both have p < .05.

### T1.4 Class scan (secondary family)

- **For each of the 17 classes:** a within-folio heterogeneity test of class frequency across the labels present on each folio. Use a CMH-type statistic over folio × length-bin strata, with the same within-folio label permutation.
- Two-sided. **Holm over the 17 classes** within each reading.
- **Classification, descriptive and declared now:**

  | Class label | Criterion |
  |---|---|
  | **context-sensitive** | Holm-pass in both readings |
  | **context-invariant** | No pass in either reading, **and** the 95% folio-bootstrap CI of the largest label-vs-label log rate ratio lies within ±0.25 |
  | **unresolved** | everything else |

### T1.5 Controls (at real geometry; 200+ trials per scenario)

- a null with labels independent of words;
- a **wrap null**, where frequency depends only on the length bin and labels correlate with wrap as in the real data;
- a **position null**, where frequency depends on position in the line and paragraph;
- a **folio-latent null**;
- a positive (one class at 1.5× rate in FG/VE lines).

**Gates:** null upper Wilson-95 ≤ .05; positive power ≥ .80, otherwise the cell is UNDERPOWERED.

---

## T2: does herbal vocabulary track the drawn plant parts?

### T2.1 New rating item (blind; added to the v4/v6 rater manual as a separate pass)

- **For each herbal page's main plant drawing,** rate the **prominence** of four parts on 0 / 1 / 2 (absent or minimal / normal / emphasised or enlarged):
  - ROOT;
  - STEM–LEAF;
  - FLOWER;
  - SEED–FRUIT.
- **Raters:** two, from **different model families**, or a human. Plain no-tools calls: one image and the manual, no transcription.
- **Gate:** quadratic-weighted κ ≥ 0.60 for **ROOT**, which is the primary. The other parts are reported, and each is used only if it clears its own κ.

### T2.2 Primary

> **T2-P:** page text features predict **ROOT prominence** on held-out herbal folios better than a baseline.

- **Unit:** the herbal folio, single main plant only (multi-plant pages excluded and listed).
- **Features:** the T1.2 class frequencies plus glyph 1–2-gram rates, computed on paragraph text excluding paragraph-first words.
- **Model:** ordinal logistic with ridge penalty. Tune it by inner leave-one-folio-out cross-validation.
- **Baseline:** scribe, plus page layout covariates (words on page, mean line length, share of wrapped lines). Large roots squeeze the text, and that's a confound.
- **Evaluation:** outer leave-one-folio-out log-loss, compared with the baseline.
- **Null:** permute ROOT ratings **across folios within scribe**, with at least 5,000 permutations, rerunning the full nested pipeline each time.
- One-sided. **Headline:** H and F both have p < .05.

### T2.3 Controls

- a layout-only null (ROOT tracks only the layout covariates);
- a positive (ROOT planted to depend on one class frequency at a realistic effect size);
- 200+ trials per scenario, with the same gates as T1.

---

## T3: the herbal entry formula (quality and degree)

### T3.0 Idea

Nearly every medieval herbal entry states the plant's **complexion**: hot / cold and dry / moist, in degree 1–4. Example: *calida et sicca in secundo gradu*. That's a closed, small set (at most 16 combinations, often fewer in practice), and it usually comes **early** in the entry. If Voynich herbal paragraphs are entries of that kind, possibly in abbreviated form, there should be an **early slot filled from a small variant set** that recurs across pages.

### T3.1 Data and split (fixed NOW)

- **Paragraphs:** herbal-section P-unit paragraphs (scribes 1 and 2, kept separate), all lines.
- **Split:** assign herbal folios to **DISCOVERY** or **CONFIRMATION** by `SHA256("v8-T3:" + folio) mod 2`. Record the lists before any text is read. **Confirmation folios are not opened for T3 until the freeze in T3.3.**

### T3.2 Discovery (sandbox on DISCOVERY folios only; at most 20 logged looks)

- **Unit:** the word **class** = opener + core, ignoring ending. The core is defined by the project's existing segmentation (state the version). The **variant** is the ending, or the whole word if the class is a single word.
- **Search:** each class C, and each window W of word positions 2–15 counted from the paragraph start (the paragraph-first word is excluded, being anomalous; H8).
- **Candidate criteria:**
  - **presence:** C occurs inside W in at least 50% of paragraphs;
  - **concentration:** C's rate inside W is at least 2× its rate elsewhere in the paragraph;
  - **closed variant set:** at least 80% of C's tokens inside W fall into 4–16 variant types.
- Keep the best candidate, by presence × concentration. If none meets all three criteria, record **NO CANDIDATE** and stop T3. That's a full result.

### T3.3 Freeze

Freeze one candidate: C, W, the variant definition, and the three criteria thresholds. Plus the predictions for CONFIRMATION:

- **(i) presence** at or above the discovery presence minus 15 points;
- **(ii) concentration** ≥ 1.5×;
- **(iii) closed variant set:** the same variant types cover at least 70% of tokens, with no more than 4 new types.

Hash it.

### T3.4 Confirmation test (both readings, separately)

- **Statistic:** the joint pass of (i)–(iii).
- **Null:** shuffle word order **within each paragraph**, keeping the first word fixed, and recompute (i)–(iii) for the frozen C and W. At least 10,000 shuffles. **The p-value is the share of shuffles meeting all three.**
- **Headline:** the frozen predictions hold, **and** null p < .05, in both readings.

### T3.5 Controls

- **Positive (essential):** a real Latin herbal **prose** text with complexion statements. *Circa instans* or a comparable prose herbal is preferred; verse such as Macer is less formulaic. Run it through the v5 G2/G3 abbreviation generator and EVA mapping, then through the identical discovery → freeze → confirmation pipeline with its own hash split. **The pipeline must recover the complexion formula** (presence ≥ 50%, a closed variant set). If it fails, T3 is NOT QUALIFIED and the Voynich result isn't interpreted.
- **Generator controls:** v5 G5 (copy-and-modify) and G6 (table and grille) output, formatted into pseudo-paragraphs of herbal size. Report how often the pipeline finds a "formula" in each. If either one routinely produces a passing slot, a Voynich pass doesn't distinguish meaning from mechanism. Report that plainly.

### T3.6 What it can and cannot say

- **A pass** means there's a recurring early slot with a small closed variant set, as an entry formula would produce. The variant set then becomes a **candidate numeral/quality set**: a target for the v7 harness's E5 check, and for cross-referencing pharma↔herbal (v6 T2), where the same plant should carry the same variant.
- **A pass cannot** say the slot means "hot in the second degree." It's structure that a complexion formula *predicts*, nothing more.
- **NO CANDIDATE / fail:** the herbal paragraphs don't contain a slot of this kind at this resolution.

---

## Deliverables

`PROTOCOL.json` · `T1/` (support, qualification, primary, scan, classification) · `T2/` (rating manual addendum, agreement, model, permutation results) · `T3/` (split lists, discovery log, freeze, confirmation, positive-control and generator reports) · `REPORT.md` · `VERIFICATION.json`

**`REPORT.md` line 1:** `RETROSPECTIVE IN TEXT; T1/T2 PROSPECTIVE IN IMAGE VARIABLE ONLY; T3 INTERNAL SPLIT.`