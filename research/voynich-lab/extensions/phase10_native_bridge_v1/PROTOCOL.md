# Phase 10 — internal native-name bridge: pharma ↔ herbal

Registered 2026-10-27 before source-list freeze, synthetic generation, calibration or target scoring. Question: do labels adjacent to published pharmaceutical plant redraws recur on the corresponding herbal page above a stratified label-shuffle baseline? No meaning or botanical identity is inferred.

## Sequential gates

1. Source-only audit: do not open local Voynich transcriptions, token tables, concordances, target scores or target images containing legible native text. Compile published picture correspondences. Bibliographic pages may incidentally contain native-script examples; these are not extracted or used. Log such exposure. This is not a claim that the investigator has never seen Voynich text in earlier phases.
2. Freeze the complete retrieved candidate list and source evidence, including tentative and contested proposals. Count unique pharma-item/herbal-page pairs classified confident. Fewer than 15 confident pairs means STOP immediately: no calibration, target extraction or target scoring. Do not relax confidence, add self-proposed matches or count duplicate citations as additional pairs.
3. Only if the source gate passes, bind all calibration dependencies and executable code in a second pre-generation hash manifest. Missing C2 entry boundaries/name sources, ZL error profile or published Naibbe tables is a preflight failure, not permission to improvise. Calibration must PASS before target text opens. Any failed calibration cell means STOP with no parameter rescue.

## Source inclusion and confidence (frozen before collation)

Published means an attributable public scholarly publication, author's research website or dated research-forum contribution, with exact retrievable source locator. This is broader than peer reviewed; record the source kind. A botanical species identification is not itself an internal picture match.

Confident: source explicitly identifies the drawings as the same plant/drawing, a copy/redraw, or an unqualified strong/clear match, and an identifiable pharmaceutical item and herbal folio are given. Tentative: possible, similar, partial-feature or qualified resemblance; a list without item-level confidence is tentative. Contested: explicit substantive disagreement about that same pairing in the inspected sources, or unresolved competing herbal destinations. Contested overrides confident. Mere generic caution about copying is not item-level disagreement. Confidence is a source-evidence classification, not a new visual adjudication. Preserve source wording separately and never promote through citation multiplicity. Scope of the final count is the audited published sources, not every proposal that might exist.

Use Petersen item IDs and page/row/item coordinates where supplied; preserve differing foldout foliation as aliases. Do not infer alias equivalence from text similarity. One primary record per unique item/page pair. Repeated herbal destinations remain visible, with dependency diagnostics; they are not claimed independent plants.

## Data and label assignment (conditional on gates)

ZL primary, LSI H alternate; never pool. Freeze exact version/hash and metadata before extraction. Retain readable diplomatic word boundaries in each transcription; lowercase EVA only, no stemming, spelling repair, anagrams, phonetic merger, or fitted normalization. Uncertain/unreadable tokens are excluded and counted, without jumping over a missing paragraph-initial token to create a replacement opener.

Prefer a cited item-to-label assignment. Otherwise use a pre-text geometric annotation: select the label block with smallest Euclidean gap between its bounding box and the matched item's bounding box, within the same pharmaceutical row/panel; ties sort top coordinate, then left coordinate. Geometry is frozen before transcription is attached. If no unambiguous item/row/label geometry is available, record unavailable; do not choose by lexical outcome. A multi-label item carries all equally assigned blocks as an intact bundle. Each complete readable whitespace-delimited label word is a candidate; do not join words. All candidates receive equal search freedom in observed and shuffled data. Multiple words/blocks never inflate the pair denominator.

Herbal side: all readable running-text word tokens on the cited page, with paragraph ID, line ID, ordinal and paragraph-initial flag. Exclude marginalia and picture labels. S2 covers the first word of every paragraph, not just the first paragraph. Keep unavailable pairs in the source ledger; bind a text-availability manifest without inspecting overlaps before scoring. Report source and available denominators separately; if fewer than 15 confident scorable pairs remain, STOP rather than silently changing the sample.

## Statistics and null (conditional)

For each pair and candidate label: S1 is 1 if its exact string occurs anywhere in running text, else 0; S2 is 1 if it exactly matches any paragraph-initial word, else 0; S3 is the largest 1 − Levenshtein(label, word)/max(length(label), length(word)) over page words (empty candidate set: unavailable). Best over the frozen candidate bundle is applied separately to each statistic. Across pairs use arithmetic means. No extra spelling variants are added. The supplied 4.27% noise figure motivates calibration, not a declaration that edit similarity corrects all transcription error or identifies homophony.

Shuffle whole label bundles across available matched-pair slots within herbal Currier A/B × herbal section strata, 999 permutations, seed 101027001 (NumPy PCG64, recorded version). All assignments, including identity/duplicate permutations, retained. Unknown Currier/section metadata is unavailable, not reassigned or merged into a convenient stratum. Singleton strata are fixed and reported; an invariant orbit cannot support rejection. Preserve duplicate page dependencies and report distinct pages, items, strata and exchangeable slots. No post-result pooling or alternate null.

Use a permutation-rank maximum so the binary and continuous statistics have comparable scales. Include observed row 0 and 999 shuffled rows. For each S column, calculate upper-tail rank p_j(r) = count[S_j(q) >= S_j(r)]/1000 over all rows q. T(r) = max_j(1 − p_j(r)). Global p = count[T(q) >= T(0)]/1000, with exact ties conservative. This applies the complete S1–S3 search identically to observed and nulls. ZL has the primary test at .05; H is a separately reported alternate, not an additional route to declare primary success. Tentative pairs are a separate descriptive secondary set; never pooled and never used to rescue primary failure.

Report all tied exact and best-edit matches, their positions, page token/type lengths, paragraph count, matched-word page count, and matched-word corpus/page frequency once access is allowed. Diagnostics do not change the statistic, sample, or null.

## Calibration (only after source PASS and dependency/code freeze)

Use cited C2 Mattioli plant-entry text and names, with the name inserted as paragraph-initial word in a synthetic illustrated-herbal layout. Synthetic slot count, repeated-page structure and strata mirror the frozen available source geometry, using source metadata only. Freeze C2 entry IDs, name forms, tokenization, all bank seeds, error operations, tables and encoder settings before generation. Do not learn a noise profile from Phase 10 target text.

Four rates p in {0,.1,.25,.5}, three conditions (clean; ZL-profile noise; published Naibbe tables + the same noise), 50 replicates per cell = 600 datasets. Independent seeded Bernoulli(p) true-name assignments per slot; other labels sampled independently from the frozen name pool, preserving accidental matches in the p=0 baseline. Names are not sampled by desired test result. Noise on page and label observations is independently generated from the bound prior ZL error profile. Naibbe encodes names and body text using the published-table implementation with settings frozen before generation; source noise-profile limitations and any previous Voynich-informed table construction remain explicit. No freshly invented uniform typo process may substitute for the specified profile.

Each dataset uses the identical complete statistic, bundle maximum and 999 stratified null permutations. For EACH condition require at least 40/50 rejections at p=.25 and at p=.5; at p=0 at most 2/50 rejections (the largest integer count satisfying ≤5%). p=.1 is descriptive only. No cross-cell averaging, discarded failures, seed replacement, parameter rescue or manuscript access on FAIL. Report binomial uncertainty as descriptive; the gate uses the requested empirical proportions. Any unbound dependency prevents generation and is reported as NOT RUN, never PASS.

## Outputs and inference boundary

Save cited source ledger, confidence/exclusion reasons, frozen list/hash, registration/hash, status, and verification. If admitted later, save the full calibration cell/trial tables, complete null assignments and scores, and per-pair target match/position/statistic table with ZL and H separate. On source STOP, label/match/score columns remain explicitly NOT LOADED/NOT RUN; do not fabricate the requested target table.

Relation to prior work is assessed as replicate/extend/contradict only within the work actually completed. Published internal-picture matching precedes this experiment. A source audit has no textual result to replicate or contradict. A successful calibrated target test would establish candidate native name loci only, with no meanings, botanical species, language or decipherment inferred.
