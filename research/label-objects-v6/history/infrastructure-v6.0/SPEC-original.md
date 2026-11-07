# Voynich spec v6: label-to-object dataset (shortest route to a meaning anchor)

**For:** a fresh session, or a loop worker.
**Written:** 24 Oct 2026 (Reed, for Re).
**Tier:** building the dataset is **infrastructure**. The two tests in §5 are **claim tier**: frozen before any label–object join.

---

## 0. Idea

Labels are short, sit next to drawings, and number in the hundreds. If the **written form** of a label predicts **what kind of thing it labels**, beyond what section and page already explain, then words carry reference. That gives an anchor class, the first foothold into meaning. Object classes are judged blind from images, so this is genuinely new evidence on exposed text.

## 1. Units

- **Every label locus** in the EVT: L, L1…Ln, S-type star labels, and other short inscription types as the transcription defines them. Readings H and F are kept separately.
- **Excluded:** the reserved zodiac folios (Virgo, Libra, Scorpio, Sagittarius), and paragraph text.
- **Pre-check:** list every label type code and its count per section. Freeze the included type list.

## 2. Registration (geometry only, outcome-blind)

- A registrar locates each label locus on its page image as a bounding box, matching by locus order and position. It uses the v4 registration machinery and rules (§4 of v4, plus v4.1).
- **The registrar never sees object categories or any analysis.**
- Labels that can't be located confidently are UNREGISTERED. Drop them and list them.

## 3. Object attachment (blind raters)

**Raters:** two raters (A, B), plus C for adjudication.

- **Model raters run as plain API calls: one image crop and the manual, no tools, no agent harness.** That settles the access-boundary problem from v4.
- One rater should ideally be human. If not, use two different model families.

**Input per label:** a crop of the page around the label with the label's box outlined, plus a low-resolution whole-page thumbnail. **No transcription.**

**The manual asks:** "What drawn thing is this marked writing attached to or placed beside? Choose one."

| Code | Class |
|---|---|
| STAR | star or star-like mark |
| SUN-MOON | sun, moon, face in a circle |
| PL-WHOLE | whole plant |
| PL-ROOT | root or underground part |
| PL-UPPER | leaf, flower, stem or seed head |
| VESSEL | jar, container, flask |
| FIGURE | human figure |
| WATER | tub, pool, pipe, tube |
| ROSETTE | rosette, circle, wheel |
| ANIMAL | animal (non-zodiac pages only) |
| OTHER | something else drawn |
| NONE | nothing nearby |
| UNCLEAR | can't tell |

**Gate:** Cohen's κ ≥ 0.60 between A and B on the full class set, and separately on a 4-way collapse (CELESTIAL / PLANT / VESSEL / FIGURE-WATER), before adjudication.

- If the full-class κ fails and the collapse passes, use the collapse.
- If both fail, the result is NOT RELIABLE. Stop and report.

**Output:** `LABEL-OBJECTS.csv` (locus, reading-independent object class, rater votes, adjudication).

## 4. Features (fixed before the join)

From each label's EVA form, per reading:

- length;
- opener class (q/qo, ch, sh, ot, ok, d, other);
- ending family;
- the presence of each glyph;
- character 1–3-grams;
- word-shape template class (the project's existing templates).

**Known exploratory findings may be listed as features, not hypotheses:** ot/ok openers are enriched in labels (stars 17%, plant jars 16.5%, rosettes 14%).

## 5. Tests (claim tier; freeze both before the join)

### T1: within-section reference

> Within a section, do label word features predict the object class better than chance, beyond page identity?

- **Where:** sections with at least 2 object classes, each having at least 30 labels across at least 6 folios. Pharma (VESSEL vs PL-ROOT vs PL-UPPER) is the main expected one. Others count only if they meet the threshold.
- **Model:** L2-regularised multinomial logistic regression on §4 features. Hyperparameters are tuned only by **inner** folio-grouped CV.
- **Evaluation:** outer folio-grouped CV with log-loss and balanced accuracy. Compare against a **page-prior baseline** that predicts each folio's object-class mix from its other labels.
- **Null:** permute object classes **among labels within each folio** (this keeps the folio's class mix), with at least 5,000 permutations, rerunning the whole CV pipeline each time.
- **Inference:** one-sided (better than null), per section × reading, Holm over the estimable sections within each reading.
- **Headline:** H and F both pass in the same section.

### T2: pharma ↔ herbal cross-reference

> Is a pharma label word that also appears (exact match, or edit distance ≤ 1 for words of at least 5 glyphs) on a herbal page attached to a drawing judged more similar to that herbal plant than to unmatched herbal plants?

- **Matching:** do it **before** any image judgment, with a frozen rule. List all matched pairs. The project's nine earlier pairs are flagged as previously seen, and the rest are fresh.
- **Judgment:** blind raters see a pharma drawing crop plus two herbal plant crops (one matched, one a random herbal plant from the same scribe), in randomised order, **with all writing masked out**. They pick which herbal plant is more similar, or say "neither / can't tell".
- **Statistic:** the share of matched picks among decided trials, against 0.5. One-sided exact binomial test, with fresh pairs only as the primary analysis.
- **Gate:** at least 15 fresh decided pairs. Otherwise, NOT ESTIMABLE.

## 6. Controls

- **T1:**
  - a synthetic positive, with object classes planted from feature rules at realistic label counts (power must be ≥ 0.80);
  - a page-confound null, where classes depend only on the page (must flag ≤ 5%);
  - a section-only null.
- **T2:** a shuffled-match control, re-running with randomly paired words.

## 7. Deliverables

`PROTOCOL.json` · `LABEL-REGISTRATION.json` · `MANUAL.md` · `RATER-A/B/C.csv` · `AGREEMENT.json` · `LABEL-OBJECTS.csv` · `FEATURES.csv` · `T1.json` · `T2.json` · `QUALIFICATION.json` · `REPORT.md` · `VERIFICATION.json`

## 8. What it can and cannot say

- **T1 pass:** label forms carry information about object class within a section. That's reference, and it's an **anchor class**: for example, "VESSEL labels in pharma share features X". It doesn't tell you what any word means or sounds like.
- **T2 pass:** pharma and herbal pages cross-reference the same plants by the same written form. That's an anchor pair, the kind of foothold a crib needs.
- **Fails:** labels at this resolution don't track object class, which is evidence against simple naming labels. **Not estimable** is not a negative.