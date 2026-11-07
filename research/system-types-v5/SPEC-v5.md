# Voynich spec v5: what kind of system is it? (simulate-and-compare)

**For:** a fresh session, or a loop worker (see the ORCHESTRATOR spec).
**Written:** 24 Oct 2026 (Reed, for Re).
**Tier:** generator development is **sandbox**. The final comparison run is **claim tier**: frozen before it runs.

---

## 0. Idea

Each hypothesis about the Voynich is a hypothesis about **how the text was produced**. So: build a generator for each candidate kind of system, tune it to match the manuscript's *basic* statistics, then check whether it **also** reproduces the findings it was **not** tuned on. A system type that can't reproduce the qualified findings is eliminated. Every result the project has already earned becomes a filter at no extra cost.

## 1. Data

- **Transcription:** `text16e6.original.evt`, readings H and F separately. Swap to a newer IVTFF transcription later, as a robustness rerun.
- **Currier A and Currier B are fitted separately.** Report scribe as a stratum.
- **Exclude** the reserved zodiac folios (Virgo, Libra, Scorpio, Sagittarius) at load time and verify the exclusion by hash.

## 2. Candidate families (each is a parameterised generator)

| ID | Family | Notes |
|---|---|---|
| G1 | **Plain natural language**, letter-for-letter | Latin, Italian, German, Czech and Occitan corpora (herbal/medical genre where possible). No tuning beyond the mapping in §3. |
| G2 | **Abbreviated Latin** | Preferred: a diplomatic transcription of a heavily abbreviated 14th–15th c. Latin medical/herbal manuscript, with suspension and contraction marks kept as **separate tokens**. Fallback: a Latin herbal with Cappelli-style abbreviation rules applied, with the rule probabilities as parameters. |
| G3 | **Notation / shorthand mix** (Re's hypothesis) | G2, plus frequent words or concepts (planets, signs, humours, units, "take", "of it") replaced by symbol tokens with probability *p*, and the symbols allowed context-dependent variants. |
| G4 | **Verbose cipher** | Latin letters → 1–3-glyph groups, with position-dependent variants (initial/medial/final forms) and optional nulls. |
| G5 | **Copy-and-modify** (Timm & Schinner) | Each word copied from a recent word (window *w* lines) and modified by mutation rules. Parameters as in their published algorithm. |
| G6 | **Table and grille** (Rugg) | Prefix/mid/suffix tables plus a grille, with the table and grille parameters free. |

Families can be added later. Each addition is a new frozen run.

## 3. Mapping into EVA

G5 and G6 produce EVA-like tokens directly. For G1–G4, use a **frozen mapping procedure** with no free choices after the freeze:

- Assign each source unit (a letter, abbreviation mark, symbol or cipher group) a **position class** (initial / medial / final / free), from its own distribution.
- Map units to EVA glyphs or glyph groups **by frequency rank within position class**.
- Ties are broken by a fixed seed.

The mapping is part of the generator. It's applied identically to every parameter draw.

## 4. Statistics

### S_fit: the generators are tuned on these

- word length distribution;
- glyph unigram distribution and bigram conditional entropy;
- the type–token growth curve;
- words per line distribution;
- the share of each glyph class in initial, medial and final position.

### S_held: never used for tuning (the project's earned findings)

| # | Statistic | Voynich target |
|---|---|---|
| H1 | **Adjacent opener dependency:** for the pair of word-openers that differ by one glyph and share the most contexts (in Voynich: sh vs ch), the within-page, within-ending MH log-OR for the next word opening with the most frequent 3-glyph opener (Voynich: qok) | v3/v4.2-C estimates, by scribe |
| H2 | **Availability strengthening:** the H1 effect among available followers ÷ the aggregate effect | about 1.16–1.32 |
| H3 | **Ending-variant freedom:** noise-relative information about the ending variant from the stem, and from ±48 signs of context (ending_lm v2 method) | stem ≈ 0.06–0.11 bits; context ≈ 0 |
| H4 | **Position rigidity:** share of glyph types with ≥ 95% use in one position class | Voynich value (q, i, e, n…) |
| H5 | **Ratio stability across sections:** τ² of log-OR(H1) across sections within scribe | v4.2-C estimate |
| H6 | **Copying locality:** mean max edit-similarity of each word to the words in the previous 1, 3 and 10 lines, vs same-page random lines and vs other pages | computed fresh on the Voynich in this run |
| H7 | **Line-initial effects:** extra p-type use at line start (p/r line-position rule) | v1-era held-out result |
| H8 | **Paragraph-initial anomaly:** template-breaking rate in paragraph-first words vs body words | 15.5% vs 3.4% |

H6 is the **direct test of copy-and-modify.** G5 predicts strong locality, and it predicts sh→qok pairs will concentrate in near-copies of recent words. Report H6 both overall and restricted to sh/ch→qok pairs.

## 5. Procedure

1. **Sandbox phase (not frozen).** Implement the generators, check that each one runs and produces plausible output, and set prior ranges. No S_held statistic may be computed on generator output during sandbox. Enforce this in code: S_held functions refuse to run until `FREEZE.json` exists.
2. **Freeze:** families, priors, S_fit, S_held definitions, distance, ABC settings and elimination rule. Hash them.
3. **ABC-SMC per family × scribe × reading.**
   - Distance: Euclidean on S_fit standardised by the Voynich-bootstrap SD.
   - At least 2,000 accepted parameter sets per family.
   - Report the S_fit fit quality. A family that can't match S_fit within tolerance is "**cannot mimic basics**" and is reported as such.
4. **Posterior predictive on S_held.** For each accepted parameter set, generate a manuscript-sized text and compute H1–H8. Report each Voynich value's percentile in the family's posterior predictive.
5. **Model choice:** ABC random forest (Pudlo et al. 2016), run on S_fit ∪ S_held, reporting posterior model probabilities. Descriptive alongside the elimination rule.

## 6. Elimination rule (frozen)

A family is **eliminated** for a scribe × reading if the Voynich value falls outside its central 95% posterior predictive interval on **at least 2 of H1, H2, H3, H6**. Those four are the most specific statistics.

- **Result counts** only when **both** H and F agree.
- A family **survives** if it is not eliminated and matches S_fit.
- The headline is the **list of surviving families per scribe.**
- If zero families survive, that's a result too: none of the candidate mechanisms reproduces the manuscript. Report it.

## 7. Controls

- **Recovery:** for each family, generate a pseudo-manuscript from known parameters, treat it as the "Voynich", and run the whole pipeline. That family must survive and its parameters must be recovered roughly. **Most other families should be eliminated.** Report the confusion matrix.
  - Gate: at least 80% correct-family survival.
  - If the gate fails, the family set can't be told apart at this text size. Report that and don't interpret.
- **Known text:** run real abbreviated Latin (if G2 uses a real source, hold out part of it) through as a "Voynich". G2 must survive.

## 8. Deliverables

`PROTOCOL.json` · `FREEZE.json` · `GENERATORS/` (code, with hashes) · `MAPPING.json` · `ABC-POSTERIORS/` · `PPC.csv` (every family × statistic × scribe × reading, with percentiles) · `ELIMINATION.json` · `RECOVERY-CONFUSION.json` · `ABC-RF.json` · `REPORT.md` · `VERIFICATION.json`

## 9. What it can and cannot say

- **It can:** eliminate production mechanisms, rank survivors, and say which earned findings each family can't produce.
- **It cannot:** read anything, or prove a surviving family is the true one. A survivor is only "**consistent with everything measured**".
- The family set is finite. A true mechanism outside it would show up as "**everything eliminated**" or "**everything poor**".