# H1/H2 log-odds reference arithmetic: synthetic qualification

This is an arithmetic reference tested only on hand-written and seeded synthetic integer tables. It does not implement scientific H1/H2 event extraction or recompute their targets. **H3 remains unresolved. No manuscript, real-source or G1–G6 output counts were used. Fresh reserves remain unparsed and held-out scoring stays locked.**

## What is implemented

For each stratum, the table is `[[a,b],[c,d]]`: exposure/reference rows and outcome yes/no columns. The reference calculates the natural logarithm of the Mantel–Haenszel pooled odds ratio:

`beta = log[(sum a*d/n) / (sum b*c/n)]`, with `n = a+b+c+d`.

It pools weighted cross-products rather than averaging stratum log odds or collapsing the tables first. The point-estimate formula was checked against the [official statsmodels implementation](https://www.statsmodels.org/stable/_modules/statsmodels/stats/contingency_tables.html#StratifiedTable.oddsratio_pooled). The installed Python environment has no statsmodels package; no statsmodels execution is claimed and no package was installed.

The API accepts immutable, explicitly synthetic tables. It has no word, corpus, availability-classifier or generator adapters. `held.py` is byte-for-byte unchanged; its score calls still refuse to execute without a complete claim freeze.

## Zero and support rules in the reference

- Empty tables and tables without exposure contrast or outcome variation contribute no information. Their full counts and exclusion reasons remain in the ledger.
- A zero cell alone does not force abstention: opposing separated strata can still produce a finite pooled estimate.
- Zero pooled denominator or numerator produces an explicit positive/negative-infinity status; neither becomes a finite estimate through half-counts or clipping. If both sums are zero, the result is `NO_INFORMATION`.
- Exact integer/rational sums preserve an odds ratio of exactly one. Near-one effects use a stable logarithm; effects outside floating-point range remain `NUMERIC_RANGE`, with the exact ratio retained. No arbitrary near-zero threshold is used.

These are qualified arithmetic behaviors, not an adopted scientific support policy. Finite-input rules for predictive intervals and elimination must still be fixed before claim scoring.

## H2 must use the approved log-odds scale explicitly

The user's decision to use log odds is retained. The literal reading of the spec's “H1 effect among available followers divided by aggregate effect,” with H1 on that approved scale, is `beta_available / beta_all`. The reference implements this as a **candidate scientific definition**, with componentwise-subset validation of available counts. The approved scale is not being reopened; the event and uncertainty protocol has not yet been frozen.

| Synthetic example | Overall OR | Available OR | Ratio of log effects | Ratio of ORs |
|---|---:|---:|---:|---:|
| Counts `[[10,10],[5,10]]`; subset `[[4,1],[1,2]]` |2|8|3|4|

If the overall OR is exactly one, its log effect is zero and this ratio is undefined, including the 0/0 case. The reference returns no H2 point value. It records the log-effect difference separately for diagnosis; **that difference has not replaced H2**. Direction reversal remains explicit. Small finite denominators are not clipped into apparent stability.

Uncertainty remains unqualified: a denominator distribution crossing zero can make a ratio interval unbounded, and event dependence prevents assuming an iid-table standard error is appropriate. Bootstrap/resampling units, near-null interval behavior and simultaneous predictive support still need a fixed protocol. The old 1.16–1.32 risk-difference ratios have not been imported as log-odds targets.

## Verification and remaining work

**16/16 synthetic engineering tests pass**, covering hand calculations, a stratification reversal, orientation/scaling invariance, support failures, separation, near-null numerical precision, subset constraints and the distinct ratio definitions. **250/250 seeded cases agree with a separate 80-digit Decimal implementation**, which uses no Fraction code from the reference. Maximum absolute log-effect error is reported in `RESULTS.json` (about 5.8e-15). This qualifies arithmetic, not uncertainty coverage or mechanism recovery.

Still pending: exact opener/context/ending selection and tie rules; within-page event construction; follower availability; H/F, hand and section strata; uncertainty/resampling; H5's between-section variance estimator; and a complete claim freeze. H3, H6–H8 method issues, layout conditioning and source/register limits remain as recorded. No definitions were inferred from fresh-reserve outcomes.

The preceding source-cut2 report and 1,158-file delivery audit are preserved under `previous-cut2/`; the source-cut2 report, 50 tests, 60 mapping checks and 22 generation checks remain a separate qualification. Reproduce this phase with `python system-types-v5/held-definition-development/qualify_arithmetic.py`, then `python system-types-v5/prepare.py`.
