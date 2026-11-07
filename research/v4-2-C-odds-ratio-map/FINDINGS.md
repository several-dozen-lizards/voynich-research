# v4.2-C findings

**RETROSPECTIVE / DESCRIPTIVE. H and F remain separate alternate readings.**

The smaller Currier-A percentage-point difference does not translate into a proportionately smaller adjusted odds ratio. The main available-only comparisons are:

| Context | H MH OR [pointwise folio-bootstrap 95% CI] | F MH OR [pointwise folio-bootstrap 95% CI] |
|---|---|---|
| Scribe 1, pooled Currier A botanical + recipes | 1.73 [1.09, 2.74] | 1.75 [1.09, 2.75] |
| Scribe 2, bath | 1.90 [1.42, 2.64] | 1.78 [1.33, 2.42] |
| Scribe 3, starred | 2.15 [1.64, 2.86] | 2.08 [1.58, 2.77] |

The individual A contexts remain visible: botanical OR 1.96 H / 1.71 F; recipes 1.51 H / 1.81 F. Their intervals are broad. The pooled A reference overlaps these contexts and is not independent evidence in addition to them.

These estimates are compatible with broadly similar relative associations across the main A/B panels. No equality/equivalence test or predictive common-versus-context-specific model comparison was frozen, so this does not establish a single strength across the book. Bootstrap intervals are pointwise descriptive intervals, not simultaneous corrections across the map.

## Requested descriptive heterogeneity summary

REML across exactly C1-C5, **B contexts only**, gives available-only tau-squared(log OR) 0.0000 H and 0.0144 F. The working-model Q-profile intervals are [0, 0.3431] H and [0, 0.1856] F. The low point estimates leave meaningful heterogeneity unresolved. They do not test equality with Currier A, which is outside this fit. B-Q2 remains unqualified; there is no new inferential heterogeneity p-value.

## Undefined resamples retained

The frozen rule withholds an OR interval if any of the 4,999 resamples has an undefined zero/zero MH ratio. No such draws were removed or replaced. Available-only affected rows:

| Context / reading | Undefined draws / 4,999 |
|---|---|
| C3 Rosettes / F | 63 |
| C5 scribe-3 botanical / F | 13 |
| C8-4 scribe-4 astronomy / H | 90 |
| C8-4 scribe-4 astronomy / F | 109 |
| C8-5 scribe-5 botanical / H | 9 |
| C8-5 scribe-5 botanical / F | 4 |

The point estimates remain defined. Infinite/zero OR draws are also retained; full counts are in RESULTS.json. A defined normal-working-model REML fit does not restore these withheld bootstrap intervals.

## Verification and scope

Arithmetic qualification passed before the outcome join: 600 rational-table fixtures, arm reversal, cluster derivatives, expanded bootstrap and analytic REML cases. An independent Fraction-based audit verified all 40 OR/RD rows from exported stratum tables. Existing risk-difference points replayed unchanged. All 20 frozen original source/control files stayed byte-identical. No raw EVT, images or vault subsets were opened. The PNG forest plot was visually reviewed for readable labels and correct inclusion of sparse rows.

This was an explicitly authorized manual analysis. The autonomous loop remains STAGED, with no new alpha spend, cycle or claim promotion.

Files: [full map](REPORT.md), [forest plot](available-only-forest.png), [machine-readable results](RESULTS.json), [verification](VERIFICATION.json), [frozen protocol](PROTOCOL.json).
