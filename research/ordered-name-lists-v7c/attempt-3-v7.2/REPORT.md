# v7.2 attempt 3 — dual-bank requalification

25 October 2026. **QUALIFIED_V7.2_ON_DECLARED_SCOPE**.

The approved v7.2 amendment retains original C3 and requires a supplementary context-role-preserving bank. It fixes source-first controls and tests the actual dictionary trap on a preregistered, jointly native-readable H/F cohort. Earlier failed attempts remain unchanged.

## Outcomes

| Case | v7.2 verdict | Original coherence bits | Role-bank coherence bits | Same evaluations above 99th in both |
|---|---|---:|---:|---|
| CLEAN | PASS | 25247.657 | 25229.186 | E1, E4 |
| CORRUPT | PASS | 7807.635 | 7903.708 | E1, E4 |
| NOISY-H | PASS | 23983.775 | 23972.804 | E1, E4 |
| NOISY-F | PASS | 24095.216 | 24071.314 | E1, E4 |
| TRAP-H | FAIL | -2549.927 | -2417.016 | none |
| TRAP-F | FAIL | -2507.292 | -2373.007 | none |

| Fresh proposal cohort | n | Verdict counts | PASS rate | Exact one-sided 95% upper PASS bound | Gate |
|---|---:|---|---:|---:|---|
| original | 200 | {'FAIL': 200} | 0.00% | 1.4867% | PASS |
| role | 200 | {'FAIL': 200} | 0.00% | 1.4867% | PASS |

All qualification gates are reported individually in [QUALIFICATION.json](QUALIFICATION.json). PARTIAL rates are reported rather than gated. The two negative cohorts are kept separate; their error bounds are not pooled. The 20%-corrupted key remains a reported near miss, with no requirement that it FAIL. Its PASS does not establish exact key recovery.

## The trap is now scored completely

The fixed source-support rule selected the first 40jointly present, native-readable H/F paragraph lines in the same eight training and eight held pages used by attempt 2. Eighteen native-uncertainty exclusions remain in [TRAP-COVERAGE.json](TRAP-COVERAGE.json), together with all other nonadmitted lines and reasons. No key-dependent deletion or source repair was performed. Source selection and its input seal preceded trap fitting.

Both fitted negative keys have finite E3/E4 and zero undecodable held slots. Their scores, controls and random-key banks are complete. Their literal FAILs therefore do not depend on the two native uncertain slots that blocked attempt 2. H/F are separate negative fits on paired source lines, not independent manuscript populations or a semantic cross-reading decoding result.

| Trap reading | E1 original-bank upper tail | E1 role-bank upper tail | E3 order gain bits/char | E4 target negative-loss value | Undecodable tokens |
|---|---:|---:|---:|---:|---:|
| H | 0.001998 | 0.051948 | -0.027726 | -4.498282 | 0 |
| F | 0.000999 | 0.048951 | -0.005855 | -4.514881 | 0 |

## What changed, and what did not

The [preceding diagnosis](../trap-diagnosis-v7.1/REPORT.md) located the old PARTIAL edge in five character-fallback spelling coincidences per reading. The memorized dictionary entries had exactly the same match count in every original C3 draw. Inactive whole-word x defaults dominated the original global permutation's fallback slots. That permutation followed its stated global frequency rule; the new supplementary comparison conditions on the already-declared use roles without deleting the original test.

The new sampler derives role strata solely from the KEY's rule-condition structure. It preserves unit inventory, context slots/conditions, all global and within-role value multisets and K. It uses no WORD-prefix heuristic, decoded forms, held values or desired outcomes to define strata. Each bank has1,000 random draws. Key hashes and distinct-key counts are retained.

A PASS must pass coherence and matched controls in each bank and have at least two of the SAME E1–E5 above the 99th-percentile criterion in both. A non-PASS becomes PARTIAL only if the SAME component reaches 99.8th in both. Otherwise it is FAIL. The strict trap FAIL gate remains intact. The original E1–E6 functions, K, reserved rejection and all historical outcomes were preserved.

C1a/C1b now shuffle registered raw source before retokenizing with the fixed key. The validated builder checks immutable inputs, raw/tokenized agreement, word geometry, endpoint classes, unknown barriers and duplicate/reserved IDs. It reproduces the earlier character-key controls exactly and can also disrupt opaque whole-word units.

The accelerated worker preserves the raw scores exactly in reference comparisons against the untouched original implementation. It caches word decoding, lexicon queries and LM probabilities; it does not change the scoring definition or add a new uncertainty penalty.

## Noise, generators and provenance

The new synthetic H/F held readings have 280/7099 differing source-character sites (3.944217%), using seed3712 and the previously measured nonzodiac disagreement rate. Disjoint corruption masks are saved; each raw reading is retokenized consistently. Training stays clean. This is substitution-noise qualification and does not model native transcription boundary errors.

All six v5 generator outputs are the unchanged, sealed outputs already produced through the qualified development entrypoint in attempt 2. Their owner/source provenance and file hash are retained in V5-C2-PROVENANCE.json. No generator fitting, new v5 reserve access, model selection or claim recovery occurred here. Published G5 retains native geometry and seed-line exclusion. Actual-trap controls are tokenized with that trap's unchanged whole-word/fallback tokenizer and appropriate section metadata. Each C2 percentile is calculated separately in both banks, across the same corresponding 1,000 keys.

Original known/corrupt banks are reused only after exact equality of the scoring projection and all key hashes is asserted. New noise/trap/control banks are evaluated afresh. Every new bank has an input checksum in its checkpoint header. Reuse references, key hashes and checkpoints remain inspectable; source/tokenizer metadata is not silently ignored when determining whether scored words match.

## Scope

This is an infrastructure qualification on declared fixtures, not a decipherment or universal error guarantee. The positive uses an already-exposed edited Latin herbal with artificial 12-word lines; the fresh negative draws are from its declared key family. Two actual overfit negatives test one dictionary-fit recipe. The source-first adapter currently supports the two stated fixture tokenizer modes. E2/v6 multi-token object/pair adapters and detailed E5/numeral arithmetic qualification remain to be completed before those capabilities are claimed. Native-uncertain whole-corpus language losses remain fail-closed; the readable qualification cohort does not certify a new missing-data policy.

The amendment and known-fixture reuse followed an exposed diagnosis and human approval. This is method development, not an independent historical validation. A future fixed key still needs provenance, a valid unbuilt-on test set, the appropriate adapters and controls, and its own frozen evaluation.

Part B/C requirements are unchanged. LISTS is still a source draft; no C2 structural look, ordered-name alignment or vault test ran. The separately administered alpha reservation and vault locks were not altered. The user's v7.2 approval authorized this qualification only.

[VERIFICATION.json](VERIFICATION.json) and [TEST-LOG.txt](TEST-LOG.txt) record independent arithmetic, source/control, key-bank, confidence-bound and preservation checks. All keys, selected/excluded source receipts, noisy inputs, null banks and failed controls are retained. Attempts1/2 are historical records, not overwritten by this result.
