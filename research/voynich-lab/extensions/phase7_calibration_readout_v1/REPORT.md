# Phase7 requested readout: no rescue or new registration

**Item (1) FAILS. No fixed-k hypothesis-test design has been registered.** This report preserves the accepted failed calibration unchanged. Item2 is an explicitly user-requested retrospective structured-control diagnostic, written outside the failed run. It is not a new qualification or replacement of the original results.

## 1. Independent-leaf controls: inferred labels at selected k

Positive means the original per-dataset Holm-adjusted p<=0.05 across the four physical tests. All 40 negative-control tests per null were estimable (no invariant/null-excluded cases). Each seed uses its original selected k. C1=Latin, C2=Italian. Seed order 1729,1733,1741,1753,1777. Fractions are positive rejections /5. The gate is <=1/5 for EACH test in EACH family x true-k x view cell; pooled rates do not replace that gate.

| Family | True k | View | Selected k in seed order | Conjugacy: within quire | Conjugacy: book | Coherence: leaf null | Coherence: bifolio null | Cell gate |
|---|---:|---|---|---:|---:|---:|---:|---|
| C1 | 2 | clean | 7,8,5,9,6 | 1/5 | 3/5 | 5/5 | 5/5 | False |
| C1 | 2 | noise | 5,6,6,4,4 | 1/5 | 4/5 | 5/5 | 5/5 | False |
| C1 | 4 | clean | 11,12,9,10,11 | 0/5 | 1/5 | 5/5 | 5/5 | False |
| C1 | 4 | noise | 10,9,10,9,9 | 0/5 | 1/5 | 4/5 | 4/5 | False |
| C2 | 2 | clean | 4,6,7,4,6 | 0/5 | 3/5 | 5/5 | 5/5 | False |
| C2 | 2 | noise | 7,4,4,4,5 | 0/5 | 3/5 | 5/5 | 5/5 | False |
| C2 | 4 | clean | 10,10,9,9,9 | 0/5 | 2/5 | 5/5 | 5/5 | False |
| C2 | 4 | noise | 10,10,10,10,9 | 0/5 | 2/5 | 5/5 | 5/5 | False |

| Pooled descriptive count | Conjugacy: within quire | Conjugacy: book | Coherence: leaf null | Coherence: bifolio null |
|---|---:|---:|---:|---:|
| Positives /40 | 2/40 | 19/40 | 39/40 | 39/40 |
| Percent | 5.0% | 47.5% | 97.5% | 97.5% |

All 8 cells fail the combined negative-control gate. Within-quire conjugacy alone meets the per-cell bound; book-wide conjugacy exceeds it in 6/8 cells; each coherence null exceeds it in 8/8. The previously reported 80/80 structured positives establish neither specificity nor qualification. Clean/noisy versions are paired; these pooled fractions are not population error-rate estimates.

### Breakdown by actual selected k

| Selected k | N | Conjugacy: within quire | Conjugacy: book | Coherence: leaf null | Coherence: bifolio null |
|---:|---:|---:|---:|---:|---:|
| 4 | 7 | 1/7 | 3/7 | 7/7 | 7/7 |
| 5 | 3 | 0/3 | 2/3 | 3/3 | 3/3 |
| 6 | 5 | 1/5 | 4/5 | 5/5 | 5/5 |
| 7 | 3 | 0/3 | 3/3 | 3/3 | 3/3 |
| 8 | 1 | 0/1 | 0/1 | 1/1 | 1/1 |
| 9 | 9 | 0/9 | 3/9 | 9/9 | 9/9 |
| 10 | 9 | 0/9 | 4/9 | 8/9 | 8/9 |
| 11 | 2 | 0/2 | 0/2 | 2/2 | 2/2 |
| 12 | 1 | 0/1 | 0/1 | 1/1 | 1/1 |

Per-seed selected k, raw p, Holm p, statuses and rejections: independent_leaf_per_seed.csv. Per-cell gate counts: independent_leaf_cells.csv.

## 2. Structured schedules with k fixed at the true value

The old run stored full-data labels only at selected k, so fixed-true-k results did not previously exist. For this requested diagnostic, refit ONLY the 80 existing structured-control datasets at their known k = 2 or 4, reusing the exact saved full-data feature basis/raw features, model settings and seeds. Same 1999 permutations, leaf aggregation, four tests and Holm rule. No new controls/features/target analysis and no changes to the failed run. All 80 fixed-k fits converged. This is retrospective and does not qualify a future design.

| Fixed true k | Schedule | N | Conjugacy: within quire | Conjugacy: book | Coherence: leaf null | Coherence: bifolio null | Mean page ARI |
|---:|---|---:|---:|---:|---:|---:|---:|
| 2 | bifolio_cycle | 20 | 10/20 | 20/20 | 10/20 | 10/20 | 0.4978 |
| 2 | quire_block | 20 | 0/20 | 20/20 | 20/20 | 20/20 | 0.2234 |
| 4 | bifolio_cycle | 20 | 20/20 | 20/20 | 14/20 | 5/20 | 0.4880 |
| 4 | quire_block | 20 | 0/20 | 20/20 | 20/20 | 20/20 | 0.5022 |

Quire-block schedules do not predict an additional within-quire conjugacy effect after conditioning on quire. Their within-quire null is invariant in 12/20 fixed-k2 cases and13/20 fixed-k4 cases; no p-value is assigned to invariant nulls. The fixed-k2 bifolio-cycle group also has 5/20 invariant within-quire nulls. Invariant cases are shown in the total-case denominator above, never counted as positive.

Pooled positives are not a substitute for the original five-seed cell criterion. The within-quire conjugacy counts for fixed-k2 bifolio-cycle controls are C1 clean3/5, C1 noise2/5, C2 clean4/5, C2 noise1/5. All fixed-k4 bifolio-cycle cells give5/5 for both conjugacy tests; all quire-block cells give5/5 for the book-wide and both coherence tests. These detections can coexist with low agreement to true schedule labels (ARI column). They do not resolve the independent-leaf rejection problem.

Full 16-cell table with invariant counts and ARI: fixed_true_k_summary.csv. Full per-seed outputs/p-values are in FIXED_TRUE_K_RESULTS.json and fixed_true_k/<dataset>/PHYSICAL.json.

## 3. Main Phase7 two-table A/B test

Status: COMPLETE, registered before fitting, chosen settings frozen before held-out evaluation. This separate main experiment WAS run. Its original ZL probe replay was exact. In both C1 and C2, the A, B and pooled Naibbe settings all selected D52_alpha_double_R22: weights [40,8,8,8,4,4], 72 cards, respacing 22/36. The nominal two-table and single-table arms are identical in content and per-seed probes. No distinct Naibbe A/B contrast was instantiated. C9 selected G30 for A, G57 for B, pooled G30.

| Corpus/arm | A/B accuracy mean +/- SD | Section accuracy mean +/- SD |
|---|---:|---:|
| ZL | 94.02% +/- 0.00 pp | 62.30% +/- 0.00 pp |
| C1_two | 61.63% +/- 1.16 pp | 46.52% +/- 3.15 pp |
| C1_single | 61.63% +/- 1.16 pp | 46.52% +/- 3.15 pp |
| C2_two | 60.82% +/- 2.08 pp | 47.86% +/- 1.31 pp |
| C2_single | 60.82% +/- 2.08 pp | 47.86% +/- 1.31 pp |
| C9_two | 63.37% +/- 2.20 pp | 48.98% +/- 1.42 pp |
| C9_single | 63.59% +/- 0.86 pp | 50.80% +/- 0.53 pp |

Section majority baseline 61.50%; A/B training-majority test baseline 32.07%. ZL is one saved 1729 reference; its 0 seed SD is not an uncertainty estimate. Control SDs describe five paired encoder/model seeds. Full main Phase7 h2/W1/repetition, vocabulary overlap and probe details remain in ../phase7_two_table_v1/REPORT.md and its CSVs. Naibbe glyph tables were designed using Voynich statistics and are NOT blind controls.

## Preservation and stop

All 1,925 pre-existing files in the failed calibration and main Phase7 trees, including their existing caches, are byte-identical; no files were added inside either original run. The original calibration FAIL and closed manuscript gate are unchanged. No new registration, replacement calibration, rescue, parameter sweep or manuscript analysis occurred. Item (1) fails, so the condition for registering the proposed separate fixed-k design is not met. STOP.
