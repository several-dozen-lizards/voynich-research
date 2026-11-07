# Amendment v7.3: published-key tier, second transcription for label tests, Part C arm disposition

**For:** the v7 and v6 sessions. Freeze and hash this before any further published-key, Part C or v6 label scoring. **Preserved unchanged:** every prior result, including the C2 outputs (five looks used), the published-key NOT_TESTABLE intake records, v7.2 qualification, BUDGET.json and the vault locks.

## 1. Published keys: a retrospective tier (fixes the A1/A2 impossibility)

**Problem:** A1 treats everything not shown to be unused as built_on. Every published author had the whole manuscript, so no published key can ever have held-out text, and every one stops at NOT_TESTABLE.

**Change:** a published key whose map can be fully written as a KEY.json is scored under tier **RETROSPECTIVE-PUBLISHED**:

- **Evaluation text:** all admissible text **minus every locus the author cites as an example or derivation.** List the cited loci in SOURCE.md before scoring.
- **Harness:** the same v7.2 harness, both banks, all gates, with no relaxation.
- **Verdict meaning:**
  - **FAIL is decisive** for that key as published. It failed on text its author could have tuned to.
  - **PASS / PARTIAL is weak.** It can only motivate a prospective follow-up and is never a claim.
  - Label every result RETROSPECTIVE-PUBLISHED.
- **Transcription completeness** (glyph mapping verified against images) is still required. NOT_TESTABLE still applies to keys that can't be fully specified.

## 2. Label tests: the second independent transcription (fixes the F label gap)

**Problem:** reading F has essentially no label coverage: zero zodiac or astronomical labels, one pharma label. H+F agreement is therefore unattainable for C2, C3, v6 T1/T2 and Part B.

**Change:** for **label-based** tests only, the second reading is the **independent transcription with the largest label coverage** in the interlinear file, other than H. It's chosen **by outcome-blind coverage counts only**:

- count readable label records per transcription code in the relevant strata (zodiac rings, astronomical labels, pharma labels), **from record headers and readability flags only, without decoding payload content**;
- pick the code with the most zodiac-ring coverage; break ties on pharma coverage;
- **exclude any code documented as derived from H.** If derivation status is unknown, record it as a limitation.

Freeze the choice, call it **R2**, before decoding any R2 payload. **The headline rule for label tests becomes H and R2 agreeing.** Paragraph tests keep H and F.

If no code other than H gives at least 50% of H's zodiac-ring coverage, label tests are **H-only**, labelled SINGLE-TRANSCRIPTION, and cannot reach the both-readings headline.

## 3. Part C arm disposition (after C2)

- **C-SUF is dropped.** Its frozen selection produced S* = kal: 2/170 labels, both in one band, a ratio driven by a sparse comparator. The selection rule lacked a prevalence floor (an authoring error). Dropping an uninformative arm can't raise the false-positive rate. **Its α share returns to the C pool.** No replacement suffix is selected.
- **C-MRK is retained, conditional.** M* = ok (H: 24.1% of ring labels; within-ring pairs 9.9% vs 5.4% across rings in the same section). It proceeds only if R2 (§2) reproduces ok as M* under the same frozen C2 rule, with the remaining looks charged against the same 10-look cap. Otherwise C-MRK is dropped the same way.
- **C-FULL and C-STEM continue unchanged.**
- **α split for C** (per the joint declaration): divided across the arms still eligible after this amendment: 2 or 3.
- **A descriptive note to carry forward:** the strong theophoric form of the hypothesis (a near-constant marker on every name) is **not** supported in H, because no opener or ending is near-constant within rings. C-FULL and C-STEM test names without assuming such a marker.

## 4. Applies to v6 as well

v6 T1 (pharma) and T2 adopt the §2 rule for their second reading, chosen by the same outcome-blind coverage procedure, and frozen separately for the pharma stratum if needed.
