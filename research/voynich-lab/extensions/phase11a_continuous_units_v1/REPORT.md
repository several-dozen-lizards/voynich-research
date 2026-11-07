# Phase 11a — declared continuous-stream amendment

**CALIBRATION_FAILED**. Voynich **CLOSED**; conditional secondary **CLOSED**.

All 840 registered evaluations completed using the saved Phase11 training-selected models: 300 natural, 240 positive, 300 negative. **Zero refits.** Every replay exactly reproduced its original within-word metrics; positive boundary counts also reproduced exactly. The amended natural region was frozen before amended positive/negative evaluation. Original Phase11 scientific files remain byte-identical. This is a control-informed amendment on the same banks, not independent confirmation.

## Read-only prerequisite: merge failure, not spaces alone

Saved Phase11 T-N positive failures against the corresponding pre/post pipeline bands (80 runs each):

| Coordinate | Pre below | Pre above | Post below | Post above |
|---|---:|---:|---:|---:|
| inventory | 0 | 80 | 80 | 0 |
| h1 | 0 | 80 | 80 | 0 |
| h2 | 0 | 80 | 80 | 0 |
| ratio | 80 | 0 | 22 | 50 |
| slope | 0 | 80 | 79 | 1 |
| word_length | 80 | 0 | 80 | 0 |
| positional_entropy | 0 | 80 | 80 | 0 |

Inventory/h1/h2 fail in every saved T-N positive before and after merging, changing from too high to too low. Inventory falls from 318–345 chunks to 2–18 post-merge units. **The merge stage is the primary diagnosed problem.** Space-dependent metrics and the old marginal-coverage gate were additional limitations. This amendment changes evaluation/coverage only and deliberately leaves the failing merge stage intact.

## Joint region and binomial reference

Five continuous-stream coordinates: inventory, h1=H(U), h2=H(next U | U), h2/h1, and rank-frequency slope. Transitions ignore ciphertext spaces within each source group, without bridging separate source documents or held-out gaps. Word length and positional entropy are descriptive only. There is no literal-letter anchor. Each tokenizer/stage has one standardized Mahalanobis region with frozen .05 covariance shrinkage and empirical 95th percentile (`higher`, inclusive).

| Tokenizer | Pre self-coverage | Post self-coverage | Post cutoff d² |
|---|---:|---:|---:|
| T-Z | 96% | 96% | 7.3120 |
| T-N | 96% | 96% | 6.3914 |
| T-MDL | 96% | 96% | 5.7866 |

For perfect boundary recovery and independent .95 band acceptance, X~Binomial(20,.95): **E[X]=19/20; P(X≥16)=99.742606%; P(X<16)=0.257394%.** Actual-coverage references are in BAND.json. This is a hypothetical benchmark: in-sample natural self-coverage does not establish predictive positive coverage, and fixed-source/noise replicates are dependent. Source-wise natural coverage/distances are retained in BAND.json.

## Positive calibration

A cell requires ≥16/20 joint boundary-F1≥.8 and post-merge-region successes. All four language/deck cells must pass for a tokenizer to become eligible.

| Source | Deck | Tokenizer | Boundary passes | Post-region hits | Joint successes | Cell |
|---|---:|---|---:|---:|---:|---|
| C1 | 52 | T-Z | 0/20 | 0/20 | 0/20 | FAIL |
| C1 | 52 | T-N | 20/20 | 0/20 | 0/20 | FAIL |
| C1 | 52 | T-MDL | 0/20 | 10/20 | 0/20 | FAIL |
| C1 | 78 | T-Z | 0/20 | 0/20 | 0/20 | FAIL |
| C1 | 78 | T-N | 20/20 | 0/20 | 0/20 | FAIL |
| C1 | 78 | T-MDL | 0/20 | 13/20 | 0/20 | FAIL |
| C2 | 52 | T-Z | 0/20 | 0/20 | 0/20 | FAIL |
| C2 | 52 | T-N | 20/20 | 0/20 | 0/20 | FAIL |
| C2 | 52 | T-MDL | 0/20 | 17/20 | 0/20 | FAIL |
| C2 | 78 | T-Z | 0/20 | 0/20 | 0/20 | FAIL |
| C2 | 78 | T-N | 20/20 | 0/20 | 0/20 | FAIL |
| C2 | 78 | T-MDL | 0/20 | 17/20 | 0/20 | FAIL |

Eligible tokenizers: none.

## Negative numerical counts; interpretation is conditional

Specificity status: **NOT_INTERPRETABLE_POSITIVE_CALIBRATION_FAILED**.

| Family | Any-tokenizer post-region hits | Rate | Numerical ≥20% trigger |
|---|---:|---:|---|
| C7 | 20/20 | 100% | yes |
| C8 | 0/20 | 0% | no |
| C9 | 0/20 | 0% | no |
| C11 | 0/20 | 0% | no |
| C17 | 0/20 | 0% | no |

These are raw diagnostic counts, **not interpretable specificity success or failure**, because positive calibration failed. Preserve every numerical STOP trigger; none authorizes target scoring.

## Limits and deliverables

The old training-only MDL tokenizer/merge rules, source sizes, 20 seeds, noise channel, positive boundary truth, four Naibbe source/deck cells and five negative families are unchanged. The T-MDL 64-merge path remains a bounded search. Naibbe/Zattera inventories are non-blind; modern Occitan, OCR, genre, smaller C13/C17, manuscript-dependent negatives and reused control outcomes limit interpretation. The context merge was not retrained on continuous contexts. Joint-region self-coverage is in-sample; it is not an unseen-text false-positive guarantee.

See METRICS.csv for all five coordinates pre/post and descriptive word/position measures, READ_ONLY_AUDIT.json for the initial saved-data diagnosis, BAND.json for all frozen natural vectors/regions, QUALIFICATION.json for all control cells, and VERIFICATION.json for preservation and gate reconstruction. Original citations and licenses remain in [Phase11 SOURCES](../phase11_plaintext_units_v1/SOURCES.md), including Zattera, Greshko, Lindemann & Bowern and Gaskell & Bowern.

No letter values, language claims, translation, manuscript A/B scoring, or two-table secondary scoring. The failed control instrument does not answer whether another segmentation of Voynich could work. No automatic merge repair or further sweep was run.
