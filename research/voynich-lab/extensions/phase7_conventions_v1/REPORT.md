# Phase7 add-on: convention-count qualification

Calibration: **FAIL**, 0/28 cells passed the registered operating criteria.140 datasets, five seeds per cell, both plaintexts and clean/noisy views.

The primary analysis is order-agnostic: physical conjugacy and quire coherence. Reading-order proposals are secondary, source-dependent sensitivities. Quire sizes are fixed under the coherence null, while leaf/bifolio labels move across quire slots; shuffling labels within each quire would preserve coherence exactly.

| Plaintext | True k | Schedule | View | Passing seeds /5 | Selected k counts | Cell pass |
|---|---:|---|---|---:|---|---|
| C1 | 1 | single | clean | 0 | {"2": 5} | False |
| C1 | 1 | single | noise | 0 | {"2": 4, "3": 1} | False |
| C1 | 2 | bifolio_cycle | clean | 0 | {"11": 1, "5": 2, "6": 2} | False |
| C1 | 2 | bifolio_cycle | noise | 0 | {"4": 3, "5": 2} | False |
| C1 | 2 | quire_block | clean | 0 | {"5": 1, "7": 3, "8": 1} | False |
| C1 | 2 | quire_block | noise | 0 | {"4": 5} | False |
| C1 | 2 | independent_leaf | clean | 0 | {"5": 1, "6": 1, "7": 1, "8": 1, "9": 1} | False |
| C1 | 2 | independent_leaf | noise | 0 | {"4": 2, "5": 1, "6": 2} | False |
| C1 | 4 | bifolio_cycle | clean | 0 | {"10": 3, "11": 1, "12": 1} | False |
| C1 | 4 | bifolio_cycle | noise | 0 | {"11": 1, "12": 1, "8": 1, "9": 2} | False |
| C1 | 4 | quire_block | clean | 0 | {"10": 1, "7": 3, "9": 1} | False |
| C1 | 4 | quire_block | noise | 0 | {"6": 1, "7": 3, "8": 1} | False |
| C1 | 4 | independent_leaf | clean | 0 | {"10": 1, "11": 2, "12": 1, "9": 1} | False |
| C1 | 4 | independent_leaf | noise | 0 | {"10": 2, "9": 3} | False |
| C2 | 1 | single | clean | 0 | {"2": 5} | False |
| C2 | 1 | single | noise | 0 | {"2": 5} | False |
| C2 | 2 | bifolio_cycle | clean | 0 | {"4": 2, "5": 1, "6": 1, "8": 1} | False |
| C2 | 2 | bifolio_cycle | noise | 0 | {"4": 2, "5": 3} | False |
| C2 | 2 | quire_block | clean | 0 | {"4": 3, "5": 1, "6": 1} | False |
| C2 | 2 | quire_block | noise | 0 | {"4": 5} | False |
| C2 | 2 | independent_leaf | clean | 0 | {"4": 2, "6": 2, "7": 1} | False |
| C2 | 2 | independent_leaf | noise | 0 | {"4": 3, "5": 1, "7": 1} | False |
| C2 | 4 | bifolio_cycle | clean | 0 | {"10": 1, "11": 2, "12": 1, "9": 1} | False |
| C2 | 4 | bifolio_cycle | noise | 0 | {"11": 1, "12": 1, "8": 2, "9": 1} | False |
| C2 | 4 | quire_block | clean | 0 | {"12": 1, "7": 1, "8": 3} | False |
| C2 | 4 | quire_block | noise | 0 | {"6": 2, "7": 2, "8": 1} | False |
| C2 | 4 | independent_leaf | clean | 0 | {"10": 2, "9": 3} | False |
| C2 | 4 | independent_leaf | noise | 0 | {"10": 4, "9": 1} | False |

**STOP. The calibration gate failed. No ZL/H text fingerprints, manuscript mixture fits, best k, nesting/metadata associations, physical-test outcomes or sequence results were computed.** The requested manuscript analysis remains unqualified; this is a method/control failure, not evidence about how many conventions the manuscript has. No feature/covariance/profile/threshold rescue was attempted.

## Calibration outcome and failure separation

| Known page-level table settings | Datasets | Selected k range | Exact-count recoveries | Median page-label ARI |
|---:|---:|---:|---:|---:|
| 1 | 20 | 2-3 | 0/20 | 0.0000 |
| 2 | 60 | 4-11 | 0/60 | 0.5028 |
| 4 | 60 | 6-12 | 0/60 | 0.6133 |

All 8,400 fold/k fits converged and all 140 searches completed. Independent summation of the saved held-out likelihoods reproduces every selected k. This is convention-count over-splitting under the registered working likelihood, not a numerical/convergence/search-completeness failure. The count of predictive mixture components is not calibrated to recover the number of known page-level encoder settings at this operating point.

All 80 structured-schedule cases show the expected positive primary physical tests under both the oracle truth labels and the inferred leaf labels. Thus the physical association tests recovered those control signals even though the mixture count was wrong. That narrower result does not satisfy the registered conjunction of count recovery, label recovery and structural recovery; the manuscript gate stays closed. Independent-leaf null behavior and all four test/null receipts remain in each calibration dataset folder.

The target runner was explicitly guard-tested AFTER failure: it rejected before target manifest creation or text-feature extraction. TARGET_GUARD_TEST.json records the expected rejection. No target k, transcription stability,2x2 nesting, metadata alignment or target physical/order results exist.

## Registered method and controls

All declared scalar/ngram/word-length/affix/slot-grammar feature families enter a train-fold transform. Regularized tied-covariance Gaussian mixtures k = 1..12 are selected by leaf-grouped held-out log likelihood, not metadata or visual clustering. PCA with 20 axes plus a shared residual density is an explicit working likelihood; it does not identify literal languages or writing conventions. Full curves, convergence failures, retained variance and per-page features are retained. Controls use known 2/4-table mixtures, three physical switching schedules, single-table references, identical page/leaf/bifolio/quire geometry, fixed seeds and the original noise model. True labels enter only after unsupervised k selection.

Naibbe published glyph tables and slot grammar were developed using Voynich material and are NOT blind controls. C1 Latin and C2 Italian share paired versions and schedules; clean/noisy views are not independent manuscripts. Five seeds do not establish population-wide calibration.

## Codicology and order-source limits

Physical collation and missing leaves follow [Zandbergen's published layout](https://www.voynich.nu/layout.html) and individual quire descriptions. Foldout panels are pooled to leaf sides; all panels and both sides stay in one leaf fold. Coverage, fixed folds and physical sheet/conjugate links are frozen in COMMON_PAGES.json, FOLDS.json and PHYSICAL.json. No original reading order is assumed.

ORDER_REGISTRY.json lists current binding, the Bunn/Pelling Q20 center fragment, Pelling Q20 subgroup/adjacency suggestions, Pelling2006 Q13, Layfield/Davis2026 singulions/Q13 variant, the Q9 refolding suggestion and VoynichViews2015 Q13. Ambiguous, source-unavailable or insufficient fragments are explicitly not assigned a guessed total order. The [Layfield/Davis publisher page](https://doi.org/10.4000/16k0a) served a bot challenge; the [image resource](https://quantumlynxresearch.com/resources/singulion_images) names sheets by present nesting position, not a uniquely verified original total order. Current order and proposals would be reported separately only after qualification; no source is ranked or chosen by clusters.

## Receipts and preservation

REGISTRATION.json predates control generation/model fitting. CONTROL_DATA_READY.json freezes every generated text/truth file before model fitting. Each dataset retains held-out likelihoods, any convergence failures, selected k, ARI, page labels, full model and primary null distributions. QUALIFICATION.json and RUN_STATE.json record the gate. Original Phase7/C12 artifacts and C16 hold files remain hash-identical. No new C12 sweep, C16 scoring or translation claim.
