# C16-KH v3: EOS repair and separated qualification

**Full qualification: NOT QUALIFIED. ZL and actual C11 remain CLOSED.** No new manuscript scores. Fresh C17 evidence is unavailable: the user confirms no unused source or additional writers. Noise, splitting, resampling or relabeling old writers does not supply new human evidence.

## Preservation and frozen repair

V2 preserved: True; archived 288 files, SHA256 `943fa164c4e80261c8dbcfcfd6c2f547310ec74ee227b3fffc6b39c07652ce1e`. V1 preserved: True. Registered v3 code/input/protocol drift: 0. Both failed runs and sealed keys remain untouched.

The sole production algorithm change builds ctx(a,b) from actual emitted trigram prefixes. The extra terminal (word,EOS) pair is excluded. The same repair applies to word and alphagram LMs. The tests compare all observed nonterminal event probabilities and interpolation weights to v2: this repairs terminal normalization, not the earlier weak discrimination or limited key search. Search budgets, candidate lists, normalization, all24 variants and word-slot rank are unchanged.

Scorer tests use gold surface words and matched fresh nulls, with NO decoder or key fitting. Decoder accuracy uses the true mapping separately. OBJECTIVE checks whether the combined key objective prefers the true key; SEARCH checks whether the unchanged blind search finds it. Fitted external-null maxima involve search and are diagnostic only; they never decide the SCORER status.

| Arm | Math | Corruption | Order | Null operating point | SCORER | DECODER | OBJECTIVE | SEARCH |
|---|---|---|---|---|---|---|---|---|
| tanakh | PASS | PASS | FAIL | FAIL | FAIL | FAIL | PASS | FAIL |
| medieval | PASS | PASS | PASS | FAIL | FAIL | PASS | PASS | FAIL |

## tanakh

Fresh parents/windows: 640; v2 parent overlap: 0; calibration/confirmation parent overlap: 0. Forty calibration and forty confirmation documents, eight windows per document.

word LM: ctx exactly equals outgoing counts=True; normalized distribution max error=1.11e-16; 215,528 nonterminal events checked against v2, max log-probability difference=0.

alphagram LM: ctx exactly equals outgoing counts=True; normalized distribution max error=1.11e-16; 213,876 nonterminal events checked against v2, max log-probability difference=0.

Gold-word scorer: original beats quarter-UNKNOWN 318/320, all-UNKNOWN 320/320; all-UNKNOWN top3 selections=0, document wins=0.

Order discrimination: 26 wins, 13 losses, 1 ties, gate count 26.5/40; exact sign tail with ties omitted=0.026626. Within-word gold-token invariance=True.

| Raw matched null | Positive exceed /40 | Null exceed /40 | Null 95% Wilson interval | AUC |
|---|---:|---:|---|---:|
| word_shuffle | 2 | 2 | 1.4%–16.5% | 0.602 |
| wrong_key | 2 | 0 | 0.0%–8.8% | 1.000 |
| quarter_UNKNOWN | 2 | 2 | 1.4%–16.5% | 0.667 |
| all_UNKNOWN | 2 | 0 | 0.0%–8.8% | 1.000 |

Separate known-key decoder: IV word accuracy=85.61%, all-token accuracy=77.50%, within-word candidate/output/score invariance=True.

Separate blind search: median alphagram recovery=45.11%, minimum=23.53%. Individual recoveries: 44.96%, 44.17%, 45.26%, 68.32%, 97.58%, 23.53%. True-key-vs-100-wrong-key wins: 100, 100, 100, 100, 100, 100.

When the true-key objective wins but fitted keys have poor recovery and lower objective, the residual is a search failure. It cannot be counted as a scorer failure or fixed by quietly adding search starts. Actual C1/C9 fitted-null score tables explicitly mark search involvement.

## medieval

Fresh parents/windows: 640; v2 parent overlap: 0; calibration/confirmation parent overlap: 0. Forty calibration and forty confirmation documents, eight windows per document.

word LM: ctx exactly equals outgoing counts=True; normalized distribution max error=1.11e-16; 502,235 nonterminal events checked against v2, max log-probability difference=0.

alphagram LM: ctx exactly equals outgoing counts=True; normalized distribution max error=0; 500,463 nonterminal events checked against v2, max log-probability difference=0.

Gold-word scorer: original beats quarter-UNKNOWN 320/320, all-UNKNOWN 320/320; all-UNKNOWN top3 selections=0, document wins=0.

Order discrimination: 39 wins, 1 losses, 0 ties, gate count 39.0/40; exact sign tail with ties omitted=3.72893e-11. Within-word gold-token invariance=True.

| Raw matched null | Positive exceed /40 | Null exceed /40 | Null 95% Wilson interval | AUC |
|---|---:|---:|---|---:|
| word_shuffle | 12 | 0 | 0.0%–8.8% | 0.941 |
| wrong_key | 12 | 0 | 0.0%–8.8% | 1.000 |
| quarter_UNKNOWN | 12 | 0 | 0.0%–8.8% | 0.996 |
| all_UNKNOWN | 12 | 0 | 0.0%–8.8% | 1.000 |

Separate known-key decoder: IV word accuracy=90.71%, all-token accuracy=86.70%, within-word candidate/output/score invariance=True.

Separate blind search: median alphagram recovery=81.78%, minimum=79.20%. Individual recoveries: 79.20%, 90.18%, 81.25%, 100.00%, 80.89%, 82.30%. True-key-vs-100-wrong-key wins: 100, 100, 100, 100, 100, 100.

When the true-key objective wins but fitted keys have poor recovery and lower objective, the residual is a search failure. It cannot be counted as a scorer failure or fixed by quietly adding search starts. Actual C1/C9 fitted-null score tables explicitly mark search involvement.

## Freshness limits and holds

Freshness means disjoint qualification source segments/positions and new null draws, not new corpus editions. V2-selected parents were excluded entirely before selecting one deterministic <=32-word contiguous window per remaining segment. Exact v2-window/training-segment matches and duplicate windows were excluded. V1 aggregate held-out means, same-work training, common-phrase overlap and artificial window boundaries remain disclosed limitations. No scoring influenced window selection.

C1 diagnostic pages exclude all40 used by v2, but had v1 aggregate exposure. C9 uses fresh seeded draws of the fixed legacy schematic grille, with fresh Hebrew word-slot geometry. Neither is a substitute for fresh human C17. No C17 document was rescored. Hebrew-only within-word shuffles test the C11 equality without admitting actual Voynich-derived C11.

The original-task hold cannot be lifted while required C17 evidence is unavailable, even if a narrower scorer or objective dimension passes. Other failed dimensions also remain failures. No new ZL runner was created or invoked. No threshold, candidate, variant, search budget or holdout was revised after these outcomes. The new confirmation bank is now exposed and cannot become fresh evidence for later tuning.

Frozen rules and inputs: PROTOCOL.md, REGISTRATION.json, inputs/banks.json. Detailed receipts: results/<arm>/RESULT.json, SCORER_DECODER.json, MATH.json, full variant-source.csv and separate raw-scorer/decoder/fitted-external-null tables, cipher cases and gold/fitted key objectives. Preservation: preservation/V2_MANIFEST.json and v2-failed-qualification.zip. No human ratings, Hebrew identification, semantic or translation claims.

## Independent source/selection audit

The independent audit reconstructed every selected Hebrew window from its original parent/offset, excluded all v2 parents, checked exact duplicate exclusions, and independently traversed and selected all 960 document-family maxima. This scorer audit instantiated only the word LM and called neither a decoder nor a fitter. It also reconstructed fresh C9 draws from frozen cell orders and independently recomputed all 12 cipher recoveries with count vectors. All checks passed.

| Arm | Gold scorer family | Mean selected line words | Singleton selected lines |
|---|---|---:|---:|
| tanakh | Hebrew | 4.92 | 43/120 |
| tanakh | word_shuffle | 2.72 | 46/120 |
| medieval | Hebrew | 30.07 | 0/120 |
| medieval | word_shuffle | 7.65 | 0/120 |

The full length table is raw-selected-length-audit.csv. These are diagnostics, not a post-hoc coverage filter or revised threshold. V2 and v3 use different qualification windows and geometry: changes in recovery rates cannot be attributed to the EOS repair, whose valid-sentence scores were proven unchanged. No added retry, larger search, new source or manuscript score was introduced.

## Direct objective-versus-search separation

Of 12 known-key cases, 11 have incomplete recovery even though the true key has a strictly BETTER combined objective than the fitted key. Those are demonstrated search misses under this budget. The remaining 1 case(s) recover all alphagrams. No case preferred an incorrect fitted key over the true key. This does not prove the objective globally correct: its frozen PASS gate compares only the true key against 100 random wrong keys. The separate gold-word scorer still fails its operating-point gate, independently of these search misses. Detailed gaps and classifications are in FAILURE_SEPARATION.json. No gate, threshold, search budget or result was changed.
