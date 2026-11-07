# Phase 11a — declared control-informed amendment

2026-10-27. User-authorized amendment; Phase 11 is immutable. No Voynich A/B scoring has occurred in this experiment. This amendment is informed by the earlier synthetic/control outcomes and is NOT an independent replication or a blind new control bank. No letter values, language claims, or translation.

## Read-only prerequisite and diagnosis

Before this amendment's scoring, audit saved Phase11 DIAGNOSTICS.json, METRICS.csv and BAND.json, without fitting anything. Report T-N positive coordinate failures separately pre/post against their corresponding pipeline bands; keep the extra literal-letter reference separate. Inventory, h1 and h2 each fail 80/80 pre-merge (above) AND post-merge (below). Inventory changes from 318–345 pre to 2–18 post. The merge stage is the primary diagnosed problem, not merely the band or ciphertext spaces. This amendment does NOT repair or tune the merge algorithm. Persist the audit and hashes in READ_ONLY_AUDIT.json. Earlier statements suggesting a spaces-only explanation are not supported by this audit.

## Preserved selection, data and calibration

Reuse the EXACT frozen Phase11 tokenizer states, selected BPE prefixes, chunk probabilities, MDL context-merge maps, sources, twenty seeds 11001..11020, 50/50 source-group splits, noise channel, Naibbe encoder/decks/truth and all negative families. No refits are necessary: these models were selected on training halves using the unchanged MDL rules. Reconstruct held-out streams by replaying saved tokenizer states and merge maps. Check reproduced within-word metrics and positive boundary counts against the saved Phase11 values; any discrepancy is an execution error and closes scoring. No parameter or inventory selection may use new metrics. This specifically isolates the amended evaluation/band from changes to fitting. No future claim of new positive/negative fitting is permitted. All Phase11 scientific artifacts and their hashes are sealed in this amendment before new scoring and checked again on completion.

Natural sources remain C1, C2, C3, C13 and cited modern Occitan (20 equally weighted vectors per source); controls remain Naibbe C1/C2 x52/78 decks and C7, real published C8, C9, C11, C17. Existing source-size, OCR, genre, non-blind published-inventory, manuscript-dependent negative and fixed-source replicate limitations carry over. References remain the exact Phase11 SOURCES.md. No new downloads, raw-source changes, replacement corpus, fresh noise bank, or method sweep.

## Continuous metrics

For held-out pre/post unit streams measure inventory, h1=H(U), h2=H(U_next|U), h2/h1 and OLS log-rank/log-frequency slope over all observed types. Ignore ciphertext spaces when counting transitions, including transitions between observed words and original lines within one held-out source group. Do NOT bridge separate source documents, held-out gaps or artificial 200-source-word group boundaries. Pool counts across groups; no extra boundary symbols. This removes ciphertext-space conditioning without inventing transitions between unrelated held-out fragments. Fitted segmentation and context maps still follow Phase11; they are not retrained with continuous contexts.

Word length and word-positional entropy remain descriptive only, copied/reproduced from Phase11. No literal-letter anchor, word-length coordinate or positional coordinate enters the gate. Unknown held-out chunks remain distinct unmerged symbols under the original UNKNOWN escape rule. Any missing/nonfinite metric, fewer than two types, zero h1 or no adjacent pair is NOT_ESTIMABLE and cannot pass.

## One joint region per tokenizer and stage

Natural stage ONLY, before any amended positive/negative evaluation: collect the 100 natural held-out five-coordinate vectors for each tokenizer and pre/post stage. Standardize each coordinate by its natural-bank mean and population SD; replace zero SD by 1, retaining this fact in the band receipt. Compute the standardized population covariance S; use fixed shrinkage R=.95*S+.05*I and its matrix inverse. Joint distance is d²=zᵀR⁻¹z. Threshold is the empirical 95th percentile of these 100 distances using quantile method `higher`; acceptance is inclusive d²<=threshold. Assert empirical natural self-coverage >=.95 for EVERY tokenizer/stage region; otherwise BAND_FAILED and stop. Save all vectors, source identity, normalization/covariance/inverse, distances, threshold, actual coverage and band hashes in BAND.json. No changing shrinkage, dimensions or cutoff after seeing positives. No independent marginal-coordinate gates.

This is >=95% **in-sample natural self-coverage**, not evidence of 95% predictive coverage for unseen languages/texts. Paired source/noise versions are dependent. Report this limitation, source-wise natural coverage and source-wise distance distributions. Only post-merge joint membership is primary; pre-merge metrics/membership are diagnostic. No pooled candidate region or best-of-region choice.

## Positive gate and binomial expectation

As Phase11, each language x deck x tokenizer cell requires at least16/20 replicates jointly meeting observable chunk-boundary F1>=.8 AND post-merge membership. A tokenizer is eligible only if all four of its cells pass; global positive calibration requires at least one eligible tokenizer. Require natural self-coverage >=95% before applying that rule. Report all12 cells; no subset rescue or newly chosen tokenizer. Boundary truth and scoring are unchanged and reproduced exactly.

For an ideal positive with perfect boundary recovery and nominal .95 independent band acceptance, X~Binomial(20,.95): report E[X]=19 and P(X>=16), plus P(X<16). Also calculate this reference at each band's actual empirical coverage. This is a hypothetical independent-trial reference, not a valid sampling model for these dependent replicates, and self-coverage is not the unknown positive acceptance probability.

## Specificity, STOP and target access

Evaluate the complete unchanged negative bank after BAND.json is frozen, using the identical replay/continuous scoring. Per negative family, a replicate is a hit if ANY of all three tokenizer post-merge vectors is inside its own natural joint region. At least4/20 hits in ANY family is the unchanged >=20% non-discriminating STOP rule. Preserve raw branch/family counts even if positives fail. **Specificity is interpretable only if positive calibration passes.** If positives fail, mark specificity NOT_INTERPRETABLE_POSITIVE_CALIBRATION_FAILED; do not call zero negative hits specificity success. If both a positive failure and a numerical negative STOP trigger occur, preserve both flags while the overall result remains unqualified.

Voynich remains CLOSED unless positive calibration AND specificity both PASS. No target-reader or A/B scoring is implemented in this amendment's control command. Conditional two-table analysis remains CLOSED; any later authorized target stage requires the unchanged Phase11 prospective target receipt and both-primary gates. No further amendment, tuning or search is automatically authorized by failure.

## Freeze and validation order

1. Save the read-only audit; report its merge diagnosis to the user.
2. Run engineering tests on invented data only. Seal protocol, implementation, tests, source/model hashes, audit and environment in REGISTRATION.json.
3. Replay natural models and seal BAND.json. All100 vectors per region required; assert self-coverage before proceeding.
4. Replay positive/negative models; freeze complete QUALIFICATION.json, metrics and factual report. Reconstruct saved joins and all gates; verify every original Phase11 artifact remains byte-identical. No Phase11 artifacts are modified to make verification pass.
