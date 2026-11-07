# C16-KH scorer v2: qualification registration

Scope: correct and qualify before any new ZL fitting, decoding, scoring or ranking. Preserve the failed run and key. Actual C11 is CLOSED too: its Voynich-derived alphagrams would bypass the ZL hold. C11-style invariance is tested on held-out Hebrew.

## Fixed candidate (before qualification scores)

Hauer, Hayward & Kondrak (2014), section 3, https://aclanthology.org/C14-1218/, appends one UNKNOWN sentence to train word models. V1 instead assigned every unseen string hapax mass and left unseen contexts uncanonicalized. Both key fitting and final ranking were affected.

V2 appends exactly one singleton UNKNOWN sentence to each word/alphagram LM; all OOV predictions and contexts canonicalize to that event; BOS remains context-only. Retain deleted-interpolation leave-one-out winner counts, unigram-first tie rule. Missing bigram contexts use unigram distributions; missing trigram contexts use bigram distributions. This explicit normalized fallback is an engineering clarification. No added probability floor or hapax allocation. Check finite-support sums.

Replace BOTH LMs used by the fitter/decoder. Keep exact alphagram candidate sets, Viterbi path EOS, normalization, beam=3, rounds=12, top24 source ngrams per order, top3 proposals, and equal mean character/word key objective unchanged. The latter remains a published-method replication limitation. Final line rank is mean conditional word-slot log probability, excluding EOS from numerator and denominator. Empty lines are ineligible; no minimum length or coverage filter. No dictionary additions, spelling correction, parser, new variants, weight optimization or restarts.

Keep all prior 24 direction/traversal variants. Each document statistic is its own maximum over variants of mean top3 unique lines (all lines when fewer than3), plus a separately reported linewise maximum/top3 envelope. Preserve every variant table, coverage and length. No ratings or semantic review.

## Frozen input selection and exposure

Use the exact two old corpus train/test splits and automatic normalization. Old test segments were exposed to v1 aggregate LM means; do not claim pristine/work-independent external evidence. Remove exact test duplicates and exact segment matches to training; keep ordinary lexical/phrase overlap. Select 640 unique held-out 4–32-word segments per arm by seeded SHA256 order. Groups of8 produce 40 calibration and40 confirmation documents, with no exact-segment overlap. Grouping does not imply continuous original prose across lines. Models restart at lines. No parameters are tuned on either bank. Calibration only sets the null threshold below.

Per Hebrew document generate independently seeded: word shuffle within each line; replace ceil(25% words) per line by UNKNOWN; all UNKNOWN at identical lengths; within-word character shuffle (INVARIANCE, not distinguishable negative). Every family gets its own maximum over the SAME24 variants. Seeds derive from candidate/arm/bank/document/family SHA256 and are never retried.

Actual nulls are copied C1/C9/C17 clean and existing-noise files only. C1/C9 select40 eligible pages (>=8 nonempty lines) by page-ID hash:20 calibration,20 confirmation. Fit/score first8 nonempty lines. C17 uses all38 anonymous writers and complete documents:19 calibration,19 confirmation, no padding/repetition. Keep per-writer IDs; flag C17 size/geometry mismatch everywhere. Fit each clean document independently; noise reuses its clean key and selected line IDs. Previous v1 exposure and small writer/page sample precision remain limitations.

## All required gates, each arm separately

G0: archive and all failed-run file hashes unchanged; registered qualification code/input/protocol hashes match; no ZL or actual C11 input admitted.

G1: probability sums within1e-10 of1 over finite support at100 fixed seen/unseen/BOS/UNK contexts; probabilities positive and<=1; UNKNOWN count=1; canonical OOV equality; length1 unknown rank excludes EOS exactly. Exhaustive synthetic Viterbi reference and all24 slot-conservation checks pass.

G2: original Hebrew scores above same-length all-UNKNOWN and 25%-UNKNOWN versions in >=95% of320 confirmation lines. Prefix lengths1/2/3 are separately reported length-artifact audits, not short-phrase coherence claims. Known-key alphagram Viterbi recovers >=90% of in-vocabulary gold tokens and>=80% of ALL gold tokens. Zero all-UNKNOWN top3 envelope items when originals and corruptions compete; zero all-UNKNOWN document maxima beat paired positives.

G3: natural Hebrew oracle-decoded best-variant top3 beats independently maximized word-shuffle null in>=32/40 confirmation documents (ties half; sign tail/Wilson interval reported). Within-word shuffle must have identical candidates, decoding and scores for every variant; never treat that equality as a false positive.

G4: per arm, clean/noise separately, threshold=max of the three families' nearest-rank95th-percentile calibration document maxima. At that fixed threshold, confirmation Hebrew sensitivity>=32/40, and at most1 confirmation null document per family exceeds threshold (1/20 pages or1/19 C17 writers). Report denominators and Wilson intervals: this finite-bank gate is NOT a population<=5% false-positive guarantee. Report AUC and source maxima/coverage. No threshold chosen on positives or confirmation; insufficient support fails.

G5: first6 confirmation Hebrew documents per arm get a known random22-letter substitution and independent within-word shuffle. Blind fitter gets ciphertext only. Gold key is used afterwards for recovery receipts. Require median alphagram word recovery>=90%, minimum>=75%, and true-key objective above99/100 frozen random wrong keys per case. Separate known-key decoder and search recovery. No extra restarts/search budget after failure.

Terminal: ANY invalid job, hash drift, insufficient cell or failed gate => NOT_QUALIFIED; ZL/actual C11 remain CLOSED. Preserve all failures; stop without within-candidate retuning. A later revision requires new registration and disjoint confirmation bank. If ALL gates pass, write narrow qualification and freeze prospective C16-KH rerun rules/hashes BEFORE any manuscript run. This task contains no ZL runner. No identification, translation or semantic conclusion follows from a pass.
