# Phase 8 audit addendum: key-sharing and coverage sensitivity

Date: 2026-10-27. Post-outcome diagnostic documentation, not a new registration.

**Status remains FAIL / STOPPED_CALIBRATION_FAILED. Voynich remains CLOSED.** No new fits, graph construction, null draws, scoring runs, retuning, replacement controls or registration were performed. This addendum qualifies interpretation of the original report; it does not overwrite its protocol, scores, cell decisions, manifests or completion receipt.

## Distinguishing the findings

| Finding | Classification | What the existing results establish |
|---|---|---|
| 19/32 separation cells passed; 27/40 different-plaintext/two-key datasets were classified as shared plaintext | Method qualification failure | The frozen graph/frequency score and classifier failed the declared discrimination requirement on this bank. This does not establish that every alignment method must fail. |
| Four Italian physical negative-control cells failed the rejection bound | Physical-control design confound | Conjugate leaves always share a key, whereas the within-quire shuffle does not preserve that structure. These cells do not provide an unconfounded estimate of content-specific false-positive rates. The registered failures remain recorded. |
| Coverage contributes 89.0% of the paired Q loss | Score-design sensitivity and descriptive accounting | The classifier responds strongly to a score whose noise decline is predominantly a coverage effect. This is not a causal ablation or a percentage attribution of classification changes. |
| All 360 datasets completed without scorer exceptions | Implementation status | No stored scorer failure explains the FAIL. FAQ remains approximate; lack of exceptions or iteration-cap endpoints does not prove global optimization. |
| Some intermediate mappings were not saved | Receipt limitation | See RUN_DEVIATIONS.md. This audit does not reconstruct missing intermediates or infer their values. |

## Conjugate key-sharing embedded in the controls

The inherited A/B map has 94 known-label leaves and 46 complete conjugate pairs: **26 AA, 20 BB, zero AB**. I carried this map into the fixed two-key controls without recognizing that it made conjugate key-sharing perfect. Calling the independent-content arms physical negative controls did not make them neutral with respect to key identity.

| Support | Observed same-label pairs | Within-quire shuffled expectation |
|---|---:|---:|
| Single-label quires | 27/27 | 27/27 |
| Mixed-label quires | 19/19 | 9/19 |
| All complete pairs | **46/46 = 100%** | **36/46 = 78.2609%** |

The excess is 21.7391 percentage points. The expectation is analytic, with no new random permutations: for quire q with n observed known-label leaves, a A leaves, b B leaves and m complete-pair slots, its expected same-label count is m*[a*(a-1)+b*(b-1)]/[n*(n-1)]. All observed leaves, including unpaired leaves, remain in the shuffle support. The pair-weighted book total is the sum across quires, not an unweighted average of quire proportions.

Mixed-quire detail:

| Quire | A leaves | B leaves | Complete pairs | Observed same-label | Expected same-label |
|---|---:|---:|---:|---:|---:|
| 4 | 6 | 2 | 4 | 4 | 2.285714 |
| 5 | 4 | 4 | 4 | 4 | 1.714286 |
| 6 | 4 | 4 | 4 | 4 | 1.714286 |
| 7 | 6 | 2 | 4 | 4 | 2.285714 |
| 8 | 1 | 2 | 1 | 1 | 0.333333 |
| 17 | 2 | 2 | 2 | 2 | 0.666667 |

Orientation 0 assigns alpha to A and beta1 to B; orientation 1 reverses them. Single-key arms use the orientation's A key throughout. Every complete pair in each two-key arm therefore shares a key. Orientation 0 has 26 alpha/alpha and 20 beta1/beta1 pairs; orientation 1 has 26 beta1/beta1 and 20 alpha/alpha pairs.

| Failed Italian SAME_TWO cell | Rejections /5 | Rejecting seeds | Same-key pairs in every rejecting seed |
|---|---:|---|---:|
| Orientation 0, clean | 4/5 | 1729, 1733, 1741, 1777 | 46/46 |
| Orientation 0, noise | 2/5 | 1733, 1741 | 46/46 |
| Orientation 1, clean | 3/5 | 1733, 1741, 1777 | 46/46 |
| Orientation 1, noise | 2/5 | 1741, 1777 | 46/46 |

All 11 rejecting seed/cell observations have 100% same-key conjugacy versus the 78.2609% shuffled expectation. All nine nonrejecting observations in these four cells also have 46/46 same-key pairs. The enrichment is fixed by the schedule; it is not a seed-specific difference and the repeated schedules are not independent structural observations.

The physical shuffle permutes complete leaf profiles within each quire, retaining the outside-trained coordinate system. It partially breaks the association between conjugacy and key identity. Any residual key signature after approximate mapping can therefore contribute to a rejection. The audit does not establish how much of an individual rejection arose from key-sharing rather than other profile differences: there are no observed mixed-key conjugate pairs in this support, and no new ablation was performed. These were intended negatives for cloned content, but they were not negatives for all graph association with conjugacy. The physical tests can fail their registered gate without demonstrating an intrinsic content-specific method failure.

## Coverage-driven score and classification changes

All 80 main qualification clean/noisy seed pairs are included, with five matched held-out folds each (400 fold pairs). No physical positive fixtures enter this decomposition. Saved fold scores obey Q=C*(G+F)/2, where C=sqrt(A_token_coverage*B_token_coverage), G is normalized mapped graph similarity, and F is normalized mapped frequency similarity. These are word-core token coverages, not edge coverages.

For this post-outcome accounting, let delta X=X_clean-X_noisy and bar X=(X_clean+X_noisy)/2. Use the exact symmetric decomposition:

- Coverage contribution: delta C*(bar G+bar F)/2.
- Graph contribution: bar C*delta G/2.
- Frequency contribution: bar C*delta F/2.

These sum exactly to Q_clean-Q_noisy, splitting each coverage/similarity interaction equally. This is a descriptive allocation convention, not a newly registered estimand or revised scorer. Calculate it within each fold before averaging across folds and seeds; multiplying pooled component means would not be equivalent.

| Pooled saved term | Clean | Noisy |
|---|---:|---:|
| C | 0.688378 | 0.541712 |
| G | 0.790426 | 0.744243 |
| F | 0.971891 | 0.966917 |

Mean Q loss is 0.143057: coverage contributes 0.127322 (89.001%), graph similarity 0.014206 (9.930%), and frequency similarity 0.001529 (1.069%).

| Base | Orientation | Actual control | Q loss | Coverage | Graph | Frequency |
|---|---:|---|---:|---:|---:|---:|
| Latin | 0 | Same plaintext, one key | 0.157838 | 0.136286 | 0.020644 | 0.000908 |
| Latin | 0 | Same plaintext, two keys | 0.148855 | 0.126083 | 0.021014 | 0.001758 |
| Latin | 0 | Different plaintexts, one key | 0.145310 | 0.129115 | 0.016038 | 0.000157 |
| Latin | 0 | Different plaintexts, two keys | 0.139428 | 0.127801 | 0.011720 | -0.000092 |
| Latin | 1 | Same plaintext, one key | 0.140790 | 0.124646 | 0.015578 | 0.000567 |
| Latin | 1 | Same plaintext, two keys | 0.147253 | 0.127539 | 0.017579 | 0.002135 |
| Latin | 1 | Different plaintexts, one key | 0.133789 | 0.122228 | 0.010752 | 0.000809 |
| Latin | 1 | Different plaintexts, two keys | 0.140659 | 0.123904 | 0.014646 | 0.002109 |
| Italian | 0 | Same plaintext, one key | 0.150179 | 0.133805 | 0.015668 | 0.000706 |
| Italian | 0 | Same plaintext, two keys | 0.141624 | 0.126814 | 0.012753 | 0.002057 |
| Italian | 0 | Different plaintexts, one key | 0.149824 | 0.127609 | 0.018677 | 0.003538 |
| Italian | 0 | Different plaintexts, two keys | 0.144126 | 0.122386 | 0.017319 | 0.004421 |
| Italian | 1 | Same plaintext, one key | 0.143487 | 0.131502 | 0.011789 | 0.000197 |
| Italian | 1 | Same plaintext, two keys | 0.134106 | 0.128209 | 0.004658 | 0.001240 |
| Italian | 1 | Different plaintexts, one key | 0.133744 | 0.122111 | 0.008722 | 0.002911 |
| Italian | 1 | Different plaintexts, two keys | 0.137899 | 0.127109 | 0.009739 | 0.001052 |

Positive contributions indicate Q loss; a negative term offsets the loss. Displayed sums can differ by rounding. Base identifies the common source in SAME arms and the A-side source in DIFF arms (the B side then uses the other language).

| Actual control, 20 paired seeds per arm | Clean to noisy classification |
|---|---|
| Same plaintext, one key | All 20 stay correctly ONE_KEY |
| Same plaintext, two keys | 13 stay correctly SAME_TWO_KEYS; 7 become incorrectly DIFFERENT |
| Different plaintexts, one key | All 20 move from incorrect ONE_KEY to correct DIFFERENT |
| Different plaintexts, two keys | 13 move from incorrect SAME_TWO_KEYS to correct DIFFERENT; 7 remain incorrect |

Pooled correct classification rises from 40/80 clean to 66/80 noisy: 33 corrections and seven new errors. This aggregate does not override any cell gate. In clean data all 20 different-source/two-key cases were called shared plaintext.

The frozen classifier uses Q and D=Q-Q0, not Q0 as a separate feature. In same-source/one-key controls, Q0 largely tracks the Q decline, leaving D nearly unchanged. In two-key arms, Q0 is already near zero and most Q loss passes into D. Arithmetic decomposition of the frozen squared-distance margins shows that both Q and D changes favor DIFFERENT in all 20 two-key classification switches (seven false negatives and 13 corrections). For all 20 different-source/one-key switches, Q movement favors DIFFERENT while D movement opposes that switch. These are calculations from saved scores and centroids, not refitting.

The 89.0% figure describes allocation of Q loss, not the fraction of decisions causally explained by coverage. Clean and noisy arms originally learned their own vocabularies and mappings under the frozen pipeline, and noise can also change tokenization and core membership. This audit holds none of those factors fixed. It establishes strong coverage sensitivity in the existing score and corresponding decision movement, without establishing that noise restores reliable plaintext discrimination or identifying the unique causal contribution of each component.

## Preserved disposition and provenance

**FAIL remains FAIL: 19/32 separation cells and 20/24 physical cells passed; all were required.** The physical-control confound qualifies interpretation of four failed physical cells; it does not erase them or rescue the independently failed source-discrimination requirement. No Phase 8 ZL/H text graphs or results were produced. No revised design, new null, new bank, sweep, fit, threshold, mapping, classifier or registration is introduced. Naibbe tables remain explicitly non-blind to Voynich statistics. No translation or historical-mechanism claim follows.

Readout sources are the existing AB_LEAVES.json, PHYSICAL.json, QUALIFICATION_RESULTS.json, QUALIFICATION.json, CLASSIFIER_FROZEN.json, saved main-control ALIGNMENT.json fold receipts, failed-cell truth.json and WITHIN_QUIRE_CONJUGACY.json receipts. RUN_DEVIATIONS.md continues to document missing intermediate null/physical mappings; they remain unavailable and were not recreated.

AUDIT_ADDENDUM_DATA.json contains the computed metadata expectations, failed-cell seed details, saved-score pair transitions, fold decomposition and cell summaries. AUDIT_ADDENDUM_RECEIPT.json anchors this addendum to the unchanged original manifests and completion receipt and verifies preservation of every pre-existing Phase 8 file. It is a post-outcome audit receipt, not a registration. Existing manifests were not rewritten to absorb the addendum.
