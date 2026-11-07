# Frozen sh/ch–qok context-transfer study

This protocol is written before synthetic outcomes, manuscript extraction, or fitted manuscript outputs. Earlier manuscript panels are exposed evidence. This is a new frozen retrospective comparison, not untouched confirmation.

## Question and identifiability

Does prediction of sh versus ch require more than position, a bounded written-junction model, and a bounded local lexical/phrase model? No text-only test can universally distinguish grammar from junction spelling or reusable templates: processes assigned those names can have identical observable distributions. An explicit equal-output grammar/template control will document this limit. A positive extended-context result means inadequacy of the specified local predictor, not grammar, semantics, or causality.

## Data and eligible events

Input: unchanged complete-atlas-v56/ROWS.json, whose parser retains uncertain tokens as barriers. Two panels: Balneological hand 2 / B / P and Starred paragraphs hand 3 / B / P. H and F use intersecting source-line locators within each panel but keep all tokenization, outcomes, fits, and exclusions separate. No spelling normalization, e-run collapse, or label/paragraph inference.

Origins start literally sh or ch and end in longest-match edy, eey, ey, y, in that order. Outcome is sh=1/ch=0. Following token must be readable; origins at a line end or followed by unknown are excluded. Context offsets do not cross a line or an unknown barrier. Missing context is a typed EDGE or UNKNOWN marker. Word body is the literal remainder after sh/ch. The following-qok indicator uses literal startswith(qok).

## Four nested predictors, fixed before fitting

P: exact body, ending, exact line length, exact forward/reverse ordinal, and their fixed body-position interactions.

J: P plus following first one/two/three EVA characters, preceding final one/two characters, and body/ending interactions with following first three characters. These are written characters, not established graphemes or phonemes. Explicit next-qok is included. This is a bounded junction model, not all junction models.

L: J plus exact neighboring words at -2,-1,+1,+2, left/right word pairs, body/immediate-neighbor interactions, immediate flank pair, and the complete masked five-word lexical frame. This captures reusable local sequences but is not every possible phrase model.

G: L plus words at -4,-3,+3,+4 and their interactions with following-qok and body. This is an extended-context predictor, not a grammatical parser. Far-context changes leave P/J/L features invariant by construction.

All models use training-only DictVectorizer and liblinear logistic regression, C=.25, L2, intercept, no class weights, tolerance 1e-7, max_iter 2000. No hyperparameter search or post-outcome repair. Failure to converge blocks scoring. Clip probabilities only for scoring to [1e-9,1-1e-9]. Constant predictor uses training add-half sh rate. Fold assignment: sort unique numbered folios by SHA256('sh-qok-context-transfer-v1|'+folio), then round-robin into five folds. All sides/lines of each folio stay together; shared H/F folios get the same folds.

## Frozen outcomes and correction

Three incremental gains in held-out log score (bits/origin): J-P, L-J, G-L. Report all losses, constant baseline, per-folio gains, failures, and reverse results. Primary view: all eligible held-out origins. Novel-frame sensitivity: score only held-out origins whose exact (previous word, body, next word) triple never occurs in that fold's training data. Unknown/edge markers remain explicit. No test-dependent feature or phrase selection. Both views reuse the same fitted models; they are not independent experiments.

Equal-weight mean across numbered folios. One-sided sign-randomization of folio gains: exhaustive 2^n signs when n<=18, otherwise 65,535 fixed random signs plus observed with plus-one tail. Bonferroni24 covers 3 contrasts x 2 views x 2 panels x 2 readings, even for missing comparisons. This sign procedure assumes approximately symmetric independent folio score differences; overlapping CV training sets weaken that assumption. Synthetic calibration checks the whole procedure under authored settings, not a universal exact test. No correction for the entire historical search is claimed.

Support: >=200 scored events, >=8 folios, >=30 of each prefix in a view; otherwise not estimable (with counts retained). Novel sensitivity has the same gates. Constant-baseline adequacy: for a claimed gain, its comparator must have aggregate loss no more than .01 bits worse than training-rate baseline. Report next-qok and other events separately descriptively; no subgroup significance search. A robust shared-reading extension requires G-L positive and adjusted p<=.05, comparator adequate, both views supported, in H and F in the same panel. H/F robustness is not independent replication.

## Qualification before manuscript extraction

Sixty independently seeded datasets per regime, 16 folios x48 events, seeds 1210000 + regime_index*1000 + trial. Each event is generated as a 9-word line with target at zero-based index4, four bodies, eight-valued nearby tokens and binary far cue at -3. A second fixed target position3 is used in alternating events to exercise position. Synthetic labels are sampled from logit models described in run.py; no real manuscript rows are opened during qualification.

Regimes: position/body only; next-qok junction; short lexical phrase (immediate neighbors); distant strong (+/-2.5 logit cue x next-qok); distant small (+/-.65 logit). All use the same complete fivefold fitting/scoring/correction. Null qualification: in each of the first three regimes, primary-view G-L adjusted flags must have Wilson95 upper rate <=.10. Strong distant primary-view G-L detection must have Wilson95 lower rate >=.80. Small distant power is mandatory to report but has no pass threshold: failure to detect manuscript effects cannot exclude effects of that size. Any required gate, invariance, parser, freeze, or convergence failure prohibits manuscript fitting in this attempt. All trials and failed gates saved. No retuning, new seeds, or narrowed family after outcomes.

Novel-frame power is reported independently; this study does not qualify small or sparse novel-frame power. Test generator intentionally supplies favorable repeated body and cue coverage; it cannot establish real-corpus power or historical authenticity. Strong-control passage counts do not constitute natural-language qualification.

## Integrity and failure retention

Freeze SHA256 of protocol, runner, source atlas, source manifest, and v94 protocol/runner before qualification. Preserve all files of older branches. Record chronological phase log, all synthetic predictions/gains, manuscript fold manifest/events/exclusions/probabilities if admitted, and final hashes. Never silently repair this frozen attempt. Any required implementation correction becomes a separately named attempt, preserves the original files, and requires a new freeze before new scoring.

Report whether each model generalizes, whether local-frame novelty changes the result, and what alternatives remain observationally indistinguishable. No glyph meanings, thing/action labels, language identities, grammatical categories, or causal prefix claims.
