# Phase8: A/B structural alignment qualification

Qualification: **FAIL**. 19/32 separation cells and 20/24 within-quire physical cells passed their registered gates.

The original Phase7 count/rejection failures remain unchanged. This is a separately requested experiment. Fixed keys alpha/beta1 are genuinely different published substitution tables and are never fitted; both key orientations are included. Native glyphs are shared, collision outputs retained and the same source segmentation used across keys.

**STOP. No Voynich A/B text graphs, learned mappings, alignment statistics or physical-similarity results were computed.** The method did not pass the registered separation/physical-control gate. No rescue, retuning, replacement keys, modified score, new bank or parameter sweep followed the failure.

## Held-out control separation

| Control | Complete / total | Correct category | False SAME_TWO_KEYS | D-null positives | Mean Q | Mean D |
|---|---:|---:|---:|---:|---:|---:|
| SAME_ONE | 40/40 | 40 | 0 | 5 | 0.552723 | 0.005475 |
| SAME_TWO | 40/40 | 33 | None | 40 | 0.534410 | 0.527154 |
| DIFF_ONE | 40/40 | 20 | 0 | 40 | 0.526281 | 0.121704 |
| DIFF_TWO | 40/40 | 13 | 27 | 40 | 0.526469 | 0.519166 |

Q is held-out core-graph/frequency alignment, coverage-weighted. D subtracts native word-identity alignment. The fixed 48-word core and bijective matching are approximations; author table collisions can violate bijectivity. FAQ is a fixed-budget approximate optimizer. Frequencies/graphs/vocabularies and mapping are trained only on each held-out-sheet complement; ground-truth unit mappings are not input.

DEVELOPMENT and QUALIFICATION use disjoint normalized source characters and seeds. Equal-prior nearest centroids over development-standardized(Q,D) are frozen before qualification. Classifier categories are ONE_KEY (same source/single key), SAME_TWO_KEYS (same source/two keys), DIFFERENT (different sources under either key condition). They do not identify the language/meaning/historical generator of arbitrary text. Source/seed/noise variants are paired, not independent texts.

The graph null reassigns A/B among whole leaves within fixed sheet-fold/observed-side-count strata, preserving sizes. A mere page-order shuffle would leave aggregate graphs invariant. All 99 null assignments retrain vocabularies and mappings and score their held-out halves. Q and D nulls, supports, coverage, duplicate assignments and optimizer receipts are retained. These nulls assess the partition, not exclusively cipher causation.

## Within-quire mapped-graph conjugacy

| Base | Orientation | View | Control | Positive /5 | Cell pass |
|---|---:|---|---|---:|---|
| C1 | 0 | clean | SAME_ONE | 0/5 | True |
| C1 | 0 | clean | SAME_TWO | 0/5 | True |
| C1 | 0 | clean | CLONED_CONJUGATES | 5/5 | True |
| C1 | 0 | noise | SAME_ONE | 0/5 | True |
| C1 | 0 | noise | SAME_TWO | 0/5 | True |
| C1 | 0 | noise | CLONED_CONJUGATES | 5/5 | True |
| C1 | 1 | clean | SAME_ONE | 0/5 | True |
| C1 | 1 | clean | SAME_TWO | 0/5 | True |
| C1 | 1 | clean | CLONED_CONJUGATES | 5/5 | True |
| C1 | 1 | noise | SAME_ONE | 0/5 | True |
| C1 | 1 | noise | SAME_TWO | 0/5 | True |
| C1 | 1 | noise | CLONED_CONJUGATES | 5/5 | True |
| C2 | 0 | clean | SAME_ONE | 0/5 | True |
| C2 | 0 | clean | SAME_TWO | 4/5 | False |
| C2 | 0 | clean | CLONED_CONJUGATES | 5/5 | True |
| C2 | 0 | noise | SAME_ONE | 1/5 | True |
| C2 | 0 | noise | SAME_TWO | 2/5 | False |
| C2 | 0 | noise | CLONED_CONJUGATES | 5/5 | True |
| C2 | 1 | clean | SAME_ONE | 0/5 | True |
| C2 | 1 | clean | SAME_TWO | 3/5 | False |
| C2 | 1 | clean | CLONED_CONJUGATES | 5/5 | True |
| C2 | 1 | noise | SAME_ONE | 0/5 | True |
| C2 | 1 | noise | SAME_TWO | 2/5 | False |
| C2 | 1 | noise | CLONED_CONJUGATES | 5/5 | True |

Mappings/vocabularies for each tested quire are learned using all other quires; all tested leaves share that outside-trained coordinate system. Leaf profiles pool their sides/panels. Only conjugate-pair mapped graph/frequency similarity is compared with 1999 within-quire whole-leaf permutations. Quire coherence and book-wide conjugacy were retired and are not computed. Physical positives intentionally clone source-unit content only within a conjugate pair; their detectability is not a claim about natural plaintext or real bifolio content. Independent-content same-source controls test unwanted conjugacy detections from key/layout artifacts.

## Full cell receipts

See SEPARATION_CELLS.csv, PHYSICAL_CELLS.csv, QUALIFICATION_RESULTS.json, CLASSIFIER_FROZEN.json and each results/<dataset>/ folder. Failures retain the active stage and partial saved outputs, so score/optimizer/data-support failures are separate from unsuccessful control discrimination. Every control/key/source/noise specification and dataset/truth hash is frozen; no omitted failures.

Naibbe glyph tables were designed using Voynich statistics and are NOT blind controls. This finite Latin/Italian/table/core-vocabulary calibration is not universal. Source substrings, imposed line-word layout, conditioning on A/B, limited word nodes, approximate mapping/bijection and paired noise/source draws constrain interpretation. Earlier ZL/H held-out analyses were already seen; a later qualified target analysis would be a registered retrospective extension.

Preservation: 8173 pre-existing source/result/hold files are byte-identical. No earlier qualification file or gate was changed. No C12 sweep, C16 score, retired physical test or translation claim. Stop.
