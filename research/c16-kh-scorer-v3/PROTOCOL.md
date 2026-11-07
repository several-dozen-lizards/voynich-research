# V3 qualification — distinct scorer, decoder and search decisions

V2 is preserved byte-for-byte with a write-once archive/manifest. ZL and actual C11 remain CLOSED throughout this qualification. No new manuscript runner is provided. Actual C11 cannot provide an independent null because its alphagrams preserve Voynich words. All source/work assumptions, original failed runs and uncertainty remain visible.

## Fixed repair

The only production algorithm change from v2 is ctx[(a,b)] = sum_c trigram_count[(a,b,c)]. Build context counts from actual emitted trigram prefixes, excluding the spurious final (word,EOS) pair. Keep single UNKNOWN training sentence, canonical OOV events, deleted-interpolation ties, normalized missing-context fallback, exact candidate emission, Viterbi EOS, word-slot rank excluding EOS, lexical normalization, 24 variants and all search budgets/weights unchanged. Independently verify normalization even after EOS and prove equality to v2 on all nonterminal contexts. This repair does not promise better valid-sentence scores: v2's observed sentences never traversed post-EOS histories.

## Freshness and data lock

Use the exact old corpus train/test split; never retrain on test. Exclude EVERY original test-segment ID selected in v2 calibration or confirmation, not merely its selected words. Each remaining segment of >=4 words contributes at most one contiguous window: length=min(32,segment_length), offset fixed by SHA256(candidate,arm,parent). Never pad or repeat words. Exclude exact v2 selected strings, exact complete training-segment strings, and duplicate v3 window strings. These are fresh qualification windows/source positions, not unseen editions or pristine data: v1 aggregate held-out LM means and same-work/common-phrase exposure are acknowledged. No score-based selection, no retries, no full work-independence claim.

Select 640 distinct eligible parents per arm by new SHA256 namespace, 320 calibration and320 confirmation; group8 windows into40 documents per bank. No parent or selected source position is shared between banks or with v2. Windows may introduce artificial line boundaries; document grouping is not continuous prose. Freeze IDs, offsets, texts and hashes BEFORE any qualification scores. All matched nulls derive only from this fresh bank with new deterministic seeds.

Fresh nulls: within-line word shuffle; ceil(25% per line) UNKNOWN replacement; all UNKNOWN at identical lengths; uniform wrong injective Hebrew-letter key. Within-word shuffling is an equality control, never a distinguishable negative. Every negative receives its OWN maximum over the identical24 variants. No null is compared only in baseline direction. No post-hoc coverage or minimum-length filter.

External diagnostics: select40 C1 pages (>=8 nonempty lines, first8 lines), excluding ALL40 pages used in v2. Acknowledge their v1 aggregate exposure; they are fresh v2-qualification pages, not pristine Latin. Generate40 new C9 documents from the frozen legacy schematic grille with new seeds, matching fresh Hebrew document word-slot geometry; fixed stride7, no historical-replication claim. Fit clean versions independently and derive noise with the old frozen noise rates and new seeds; noise reuses clean keys. These fitted-null diagnostics involve search and cannot determine the SCORER status.

All38 C17 documents/writers were exposed in v2. User confirms no unused source or additional writers. Fresh C17 is UNAVAILABLE; no noise draw, text split, bootstrap, relabeling, reuse or synthetic surrogate may be counted as new human evidence. Old C17 stays preserved/read-only and is not rescored. This blocks broad qualification for the original four-null C16-KH task regardless of any narrower passes.

## Statistics fixed before scores

Document statistic: maximum over24 variants of mean top3 distinct line identities (or all if fewer). Also report linewise maximum/top3 envelope. For raw SCORER tests retain each known gold surface word attached to its slot while traversing order; within-word LTR/RTL represent the same already-resolved gold token. This is a gold-word scorer oracle, not de-anagramming. For DECODER and SEARCH tests use actual ciphertext words and unchanged exact alphagram Viterbi. Keep all variant/source tables, selected unknown fractions and word lengths. Signed word-order comparisons use ties half for the success gate; exact sign tails omit ties, with Wilson intervals reported as descriptive finite-bank intervals.

## Separate required decisions (both arms, no pooling away failures)

MATH: finite event probability sums within1e-10 of1, positive and<=1, at100 fixed seen/unseen/BOS/UNK/terminal contexts. ctx equals independently accumulated outgoing-trigram counts for all contexts; UNKNOWN count1; OOV alias equality. V2/V3 interpolation weights and log probabilities equal on every observed nonterminal event (tolerance1e-12); after-EOS normalized fallback is tested explicitly. Exhaustive synthetic Viterbi and24 slot-conservation checks pass.

SCORER-CORRUPTION: gold Hebrew beats length-matched all-UNKNOWN and25%-UNKNOWN on>=95% of320 confirmation lines; zero all-UNKNOWN document wins and zero all-UNKNOWN top3 envelope items when competing against the same originals/corruptions. Report length1/2/3 prefix tests separately.

SCORER-ORDER: gold-surface natural Hebrew document maxima beat separately maximized word-shuffle nulls in>=32/40 confirmation documents, ties half. Within-word direction invariance is exact. This gate contains NO key fitting or dictionary decoding.

SCORER-NULL: using raw known-word scorer only, threshold=max across word-shuffle, wrong-key, quarter-UNKNOWN and all-UNKNOWN families' nearest-rank95th-percentile CALIBRATION maxima. At this locked threshold confirmation sensitivity>=32/40 and false positives<=2/40 for EACH family. Report threshold, AUC, exact sample sizes and Wilson intervals. Do not choose a threshold on positives/confirmation. This operating-point gate may fail despite high AUC; do not lower it afterward.

SCORER status = MATH + CORRUPTION + ORDER + NULL only. It must not inherit search or decoder failures or successes.

DECODER: with correct letter key, exact alphagram Viterbi recovers>=90% of in-vocabulary gold tokens and>=80% of all confirmation tokens; within-word-shuffle candidate/output/score equality for all24 variants. This separate status measures ambiguity/decoding, not scorer or search recovery.

OBJECTIVE: first6 confirmation documents encrypted with known random22-letter substitution and within-word shuffle; true-key combined objective exceeds>=99/100 frozen wrong injective keys per case. Report both word/character combined objective and correct-key decoder ceilings. Never call this blind recovery.

SEARCH: unchanged blind fitter (beam3,12 rounds, top24 per n,top3 proposals, no restarts) on those6 ciphertexts. Median alphagram recovery>=90%, minimum>=75%. Record character accuracy and fitted vs true-key objective. Objective prefers true key but search misses it => search failure, not evidence against the scorer. OBJECTIVE + SEARCH define search qualification; keep separate from DECODER and SCORER.

EXTERNAL-FRESHNESS: C1/C9 diagnostics are separate, with provenance/geometry/size limitations. Fresh original-family C17 evidence is unavailable. No full original-task qualification or manuscript unlock until this required evidence is supplied and qualified under a separate freeze. Actual C11 remains closed.

G0: every preserved v2/v1 file, archive and registered v3 input/code/protocol hash matches; all scheduled cells accounted for. ANY invalid required cell is a failure, never retried silently. Execute this candidate once, preserve all negatives, no within-candidate retuning. Full status requires SCORER, DECODER, OBJECTIVE/SEARCH and external required evidence; otherwise NOT_QUALIFIED or required-evidence UNAVAILABLE, with ZL/C11 CLOSED. Freeze a prospective rerun separately if all requirements ever pass. No rating, Hebrew identification, semantic or translation claim.
