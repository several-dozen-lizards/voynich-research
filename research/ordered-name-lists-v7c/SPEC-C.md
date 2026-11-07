# Voynich spec v7, Part C: ordered name lists (angels, decans, mansions, degree names) as cribs

**For:** the v7 session (the harness from Part A is required).
**Written:** 25 Oct 2026 (Reed, for Re).
**Tier:** list assembly and the C2 pre-test are **sandbox / descriptive** on the open signs. C3 is **claim tier**, and its vault run needs Re's written OK. **The C3 vault use is declared together with Part B** (α split in §C6).

---

## C0. Idea

Medieval astral-magical lists are **ordered**: 7 planetary angels, 12 sign angels, 24 hour angels, 28 lunar mansions, 36 decans, 72 quinances, and named or imaged degrees (30 per sign). The zodiac and cosmological diagrams have rings of labels in matching counts. **An ordered list aligned to an ordered ring gives every name–label pairing at once**, up to start point and direction. That's a far stronger crib than the unordered plant-name sets that v79/v80 showed to be underpowered.

## C1. Frozen list set (assemble FIRST; no Voynich data opened while assembling)

- **Date rule:** use only sources whose earliest surviving witness or securely dated tradition is **≤ 1440**. Record the earliest-witness date and the edition/manuscript used for every list. Lists known only from later sources (Agrippa 1533, Trithemius 1508, the Lemegeton) go in a separate **LATE** set. That set can be reported descriptively but is excluded from claims.
- **Candidate traditions** (verify the dates; don't assume them):
  - Picatrix (Latin) mansion spirits and degree images;
  - Liber Razielis and other Alfonsine material;
  - Liber Juratus (Sworn Book of Honorius);
  - Ars Notoria;
  - the Heptameron tradition (planetary and hour angels; check how early its manuscripts are);
  - the Alfonsine lapidary (a stone per degree);
  - decan names (Greek, Latin and Arabic transmissions);
  - lunar mansion names (Arabic and Latin forms).
- **For every entry:** keep every attested spelling variant, the list order, which unit it attaches to (sign, degree, mansion…), and its morphology. Mark the theophoric suffix explicitly (*-el / -iel / -ael / -uel / -yel*) and any prefix.
- **Freeze** `LISTS.json` and hash it. **The number of lists × variants is the search size, and it is charged in every null** (§C5).

## C2. Structural pre-test (descriptive, open signs only, no mapping)

On the **open** zodiac sign-pages (Pisces, Aries ×2, Taurus ×2, Gemini, Cancer, Leo) and, separately, on the other label sets (star labels on f68/f67, plant-jar labels, rosette labels):

1. **Ending concentration:** for each ending family and for the final 1–3 glyphs, the share of ring labels carrying it, against its share in the other label sets and in paragraph text.
2. **Opener concentration:** the same for openers, with ot / ok / qo / ch / sh / d / other.
3. **Within-ring constancy:** the probability that two labels in the same ring share an ending (or an opener), against two labels from different rings in the same section, and against two labels from non-zodiac label sets.

**Interpretation, decided now:** if angel or theophoric names sit in the rings, **some component should be near-constant within rings**, well above the other label sets.

- The candidate **suffix-sign** S\* is the ending with the highest within-ring constancy ratio.
- The candidate **marker** M\* is the opener with the highest ratio.
- **If neither ratio exceeds 2× the other-label baseline,** record `NO MARKER` and skip arms C-SUF and C-MRK.

This is a sandbox step: at most 10 logged looks.

## C3. Alignment arms (claim tier: freeze all four together before any alignment)

Each arm aligns ring labels (in cyclic order, searching all rotations × 2 directions × band orders) to one frozen list, using a **constrained sound mapping** fitted on the open signs.

| Arm | List side | Voynich side |
|---|---|---|
| **C-FULL** | Full names with the suffix | Labels intact |
| **C-STEM** | The suffix removed from every name | Labels intact |
| **C-SUF** | The suffix removed | **S\*** stripped from labels (the suffix is assumed written as S\*) |
| **C-MRK** | The suffix removed | **M\*** stripped from labels (the name-class marker is assumed to stand in for the theophoric element) |

**Mapping constraints:** the mapping is a v7 Part A `KEY.json`. Glyph or group values are fitted on the open signs only. Every context rule must be stated. **Complexity K is recorded.** Maximum key size is declared at freeze.

**Prediction:** for each **reserved** sign (Virgo, Libra, Scorpio, Sagittarius), the frozen key + list + alignment rule predicts the label forms in figure order. The score is the mean normalised edit distance between predicted and observed labels, under the best alignment.

## C4. Qualification (before any vault run)

- **Positive:** encode a real ordered list into synthetic labels with a known key of declared complexity, add transcription noise at the observed H/F rate, and use the real reserved geometry. Detection ≥ 0.80 for each arm.
- **Flexible-key trap:** fit keys of the same maximum complexity to the open signs against **fake angel lists** (below). The real-list result must beat that distribution.
- **Equal-complexity random keys** (v7 A4 C3): at least 1,000.

## C5. Nulls (all four charged with the full list × variant × arm search size)

1. **Shuffled list order** (same names, wrong order).
2. **Fake angel lists:** names generated from the real lists' morphology. Same length distribution, same suffix rates, and a syllable model trained on the real stems, with no real names. **If fakes fit as well as reals, the "hit" is morphology, not reference.** This is the key null.
3. **Wrong-unit lists:** for example, mansion names aligned to a degree ring.
4. **Shuffled Voynich ring order,** with each ring's label multiset kept.

## C6. Error budget and vault (declared together with Part B)

- Part B (numerals) and Part C (lists) both use the reserved signs. **Both are declared before either vault run.** Each reserved subset is used once per hypothesis.
- **α split:** Part B gets half. Part C gets the other half, split equally across the arms that survive C2. If C2 returns NO MARKER, only C-FULL and C-STEM run.
- **PASS** (per arm): the reserved-sign prediction beats every null in §C5 at the arm's α, in **both** readings, and the coherence score (v7 A5) is > 0.

## C7. What it can and cannot say

- **A PASS on C-SUF or C-MRK** is the most informative outcome. It would mean a fixed Voynich component behaves as the written form of a theophoric element **and** an ordered name list predicts unseen labels. That's a crib with structure behind it.
- **A PASS on C-FULL or C-STEM alone** is weaker. It needs the fake-list null to have been beaten decisively, because morphology fits are the classic failure.
- **NO MARKER plus a fail on every arm:** the zodiac rings aren't spelled lists of this kind, at least for the frozen lists. Record it and close the branch.
- **It cannot** confirm a language or a reading outside the matched labels. Any key that passes then goes through the full v7 Part A harness on paragraph text.

## Deliverables

`LISTS.json` (+ sources and dates) · `LISTS-LATE.json` · `C2-PRETEST.json` · `C3-FREEZE.json` · `KEYS/C-*/KEY.json` · `FAKE-LISTS.json` · `QUALIFICATION.json` · `NULLS.json` · `VAULT-RESULT.json` (if authorised) · `REPORT.md` · `VERIFICATION.json`