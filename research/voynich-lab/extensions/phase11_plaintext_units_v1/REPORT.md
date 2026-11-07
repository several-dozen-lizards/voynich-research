# Phase 11 — plaintext-unit search

Requested identical-pipeline rule: **CALIBRATION_FAILED**. Sealed extra-anchor rule: **CALIBRATION_FAILED**.

Pipeline-only positive calibration: FAIL. Pipeline-only full-search specificity: PASS. Voynich: **CLOSED**. Two-table secondary: **CLOSED**.

All 840 registered fits completed: 300 natural-band fits, 240 positive fits, 300 negative fits. Twenty split/noise replicates per frozen source; these are not independent texts. Registration preceded fitting; the natural band was sealed before positive/negative fitting. No target A/B feature computation, segmentation or scoring was performed by this instrument.

**Protocol limitation:** I added a literal-letter anchor beyond the requested identical-pipeline band. The frozen bands have disjoint ranges in {'T-Z': [], 'T-N': ['inventory'], 'T-MDL': ['word_length']}, making those combined gates impossible to pass. That is an implementation-design error, not a scientific failure of tokenization. Both rules are reported; REQUESTED_RULE_AUDIT.json applies the user-stated pipeline band without the extra anchor to exactly the same saved results, without refits, revised intervals, or winner selection. The sealed protocol and original qualification remain unchanged.

## Positive calibration

A pipeline joint success requires boundary F1 >= .8 and post-merge membership in the identical-pipeline band in the same replicate. The sealed extra-anchor joint success additionally requires literal-letter membership. A branch needs >=16/20 successes in every language/deck cell.

| Source | Deck | Tokenizer | Pipeline joint successes | Extra-anchor joint successes | Median boundary F1 | Pipeline-only hits | Literal-letter hits |
|---|---:|---|---:|---:|---:|---:|---:|
| C1 | 52 | T-Z | 0/20 | 0/20 | 0.317 | 0/20 | 0/20 |
| C1 | 52 | T-N | 0/20 | 0/20 | 0.819 | 0/20 | 0/20 |
| C1 | 52 | T-MDL | 0/20 | 0/20 | 0.570 | 0/20 | 0/20 |
| C1 | 78 | T-Z | 0/20 | 0/20 | 0.316 | 0/20 | 0/20 |
| C1 | 78 | T-N | 0/20 | 0/20 | 0.819 | 0/20 | 0/20 |
| C1 | 78 | T-MDL | 0/20 | 0/20 | 0.543 | 0/20 | 0/20 |
| C2 | 52 | T-Z | 0/20 | 0/20 | 0.318 | 0/20 | 0/20 |
| C2 | 52 | T-N | 0/20 | 0/20 | 0.822 | 0/20 | 0/20 |
| C2 | 52 | T-MDL | 0/20 | 0/20 | 0.514 | 0/20 | 0/20 |
| C2 | 78 | T-Z | 0/20 | 0/20 | 0.316 | 0/20 | 0/20 |
| C2 | 78 | T-N | 0/20 | 0/20 | 0.822 | 0/20 | 0/20 |
| C2 | 78 | T-MDL | 0/20 | 0/20 | 0.511 | 0/20 | 0/20 |

Eligible tokenizer branches under requested rule: none.

## Specificity

Pipeline-only family union counts follow; the extra-anchor counts remain in QUALIFICATION.json.

| Negative | Any-tokenizer pipeline hits | Rate | Descriptive Wilson 95% interval | >=20% stop rule |
|---|---:|---:|---:|---|
| C7 | 0/20 | 0% | 0.0%–16.1% | not triggered |
| C8 | 0/20 | 0% | 0.0%–16.1% | not triggered |
| C9 | 0/20 | 0% | 0.0%–16.1% | not triggered |
| C11 | 0/20 | 0% | 0.0%–16.1% | not triggered |
| C17 | 0/20 | 0% | 0.0%–16.1% | not triggered |

The denominator is fixed at 20 for each family. Wilson intervals are descriptive only: these dependent fixed-source/noise replicates do not justify independent-trial population inference. C13 and C17 retain their shorter real source size. C8 is the real pinned Timm–Schinner output; its generator seed was not resampled. C11 retains its manuscript dependence. Passing this finite negative bank is not a general proof that gibberish cannot reach natural statistics.

## Band and selection checks

h1=H(U), h2=H(next U | U), no spaces and no cross-word transitions. Seven marginal 95% ranges are intersected, so overall acceptance coverage is not 95%. Post-merge acceptance additionally requires the frozen raw-letter reference. No metric is used to choose tokenizer length or context inventory; training description lengths select those quantities.

| Tokenizer | Pre-merge natural self-coverage | Post-merge natural self-coverage |
|---|---:|---:|
| T-Z | 76% | 76% |
| T-N | 81% | 83% |
| T-MDL | 75% | 77% |

## Descriptive failure diagnosis (not a new gate)

| Positive tokenizer | F1 >= .8 | Post-merge vectors in pipeline band | Post-merge vectors in literal-letter band |
|---|---:|---:|---:|
| T-Z | 0/80 | 0/80 | 0/80 |
| T-N | 80/80 | 0/80 | 0/80 |
| T-MDL | 0/80 | 0/80 | 0/80 |

The literal-letter mean word-length reference is [4.301242701769375, 5.675162558823884] units per observed word. Naibbe standard respacing discards original plaintext word boundaries and creates one/two-letter groups. Correct chunk recovery therefore does not imply ordinary plaintext word lengths under ciphertext spaces. This is a calibration-design limitation, not evidence against language in the manuscript. Context-only homophone merging can also erase distinctions; inspect saved maps and inventory counts. DIAGNOSTICS.json records coordinate failure counts without changing the frozen rules.


Full pre/post vectors, word counts, OOV units and MDL endpoint flags: METRICS.csv. BAND.json contains all intervals; results/*.json contain split receipts, tokenizer paths, maps, context-merge objectives and boundary counts. Low reference self-coverage limits the test; it is not repaired after the scores.

## Interpretation and relation to prior work

This is a bounded operational search, not an exhaustive theorem about possible segmentations. T-MDL has a frozen 64-merge BPE-path cap. Tokenizers are independently fitted on training halves; context merges are distributional and selected by training MDL. Published Naibbe and Zattera inventories are non-blind. Noise/boundary survival, OCR, genre, short-source bias, and original-space conventions limit interpretation.

[Zattera](https://ceur-ws.org/Vol-3313/paper10.pdf) supplies the published alphabet proposal, used with explicit lossless fallback. [Greshko](https://doi.org/10.1080/01611194.2025.2566408) supplies the published Naibbe encoder/inventory and known-boundary positive controls. [Lindemann & Bowern](https://arxiv.org/abs/2010.14697) motivate segmentation-sensitive entropy comparisons and supply the cited modern Occitan sample. [Gaskell & Bowern](https://ceur-ws.org/Vol-3313/paper4.pdf) motivate testing specificity against structured human gibberish. This experiment does not reproduce all methods or numerical results in those papers.

No letter values, language claims or translations. Earlier phase results and gates remain unchanged. The two-table secondary was not run because the required primary gates were not reached.
