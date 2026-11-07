# Amendment v7.1: harness verdict controls and qualification gates

**For:** the v7 session. Freeze this before the second Part A qualification attempt. The first attempt's failed verdict is **preserved unchanged**. This amendment governs attempt 2 onward. **Supersedes:** v7 Part A §A6 condition 3, the definition of PARTIAL, and the §A8 negative gate.

## Why (authored-spec errors exposed by attempt 1)

1. **A6 condition 3 compared E3 (the word-order gain) against the C1 glyph-shuffle control.** Glyph shuffling within words preserves word order, so that control keeps what E3 measures. The true key's real-vs-control E3 difference was therefore uninformative: 0.0378 real vs 0.0466 glyph-shuffled bits per character.
2. **PARTIAL was defined as "any of E1–E5 at or above the 99th percentile of C3", with no multiplicity correction.** Random keys then reach PARTIAL about 5% of the time by construction (attempt 1: 7/100). So the A8 requirement of at least 99% FAIL was unattainable.

## Changes

1. **Matched controls (replaces A6.3).** Each evaluation is compared against the control that destroys the structure it measures:
   | Evaluation               | Must exceed the gain under                                                                     | Why                                             |
   | ------------------------ | ---------------------------------------------------------------------------------------------- | ----------------------------------------------- |
   | E3 (order)               | **C1a: word order shuffled within line** (glyphs intact), **and** C2                           | Destroys word order and keeps words             |
   | E4 (target-language fit) | **C1b: glyphs shuffled within word**, keeping position classes (word order intact), **and** C2 | Destroys word-internal spelling and keeps order |
   | E1, E2 (reference)       | C1b **and** C2                                                                                 | Destroys spelling and keeps placement           |
   | E5 (numbers)             | the Part B within-band permutation null                                                        | Destroys sequence and keeps forms               |
   "Exceed" means the real-text value is above the 95th percentile of that control's distribution, computed across the C3 random keys applied to the control text. That removes the single-point comparison.
2. **PARTIAL with multiplicity.** PARTIAL now requires at least one of E1–E5 to be at or above the **99.8th percentile** of C3, which is Bonferroni over five evaluations at 0.01.
3. **A8 negative gate:** at least 99% of random proposals are **not PASS**, with the upper 95% Clopper–Pearson bound on the PASS rate at or below 3%. Use at least 200 proposals. PARTIAL rates are **reported**, not gated, with an expected rate of about 1% under the corrected definition.
4. **The A8 positive gate is unchanged:** the true key must PASS. Add a **noisy dual-reading positive**: the same key on two synthetic "readings" with transcription disagreement at the observed H/F rate. It must PASS in both.
5. **The coherence score stays necessary but not sufficient.** Attempt 1's corrupted key showing positive coherence (7,807 bits) is expected behaviour, not a defect. Record it in the report as a known property.

## Not changed

E1–E6 definitions, K, the C3 bank, the reserved-folio rejection, the flexible-key trap requirement and every Part B/C rule.

## Re-qualification order

Preserve attempt 1, freeze this amendment, then run:

1. the true key;
2. the corrupted key (20%) and the noisy dual-reading positive;
3. at least 200 random proposals;
4. the actual Voynich flexible-key trap;
5. the generator controls (C2), once v5 generators are available, using the qualified v5 entrypoint.
