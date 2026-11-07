# Phase 7: two-table verbose cipher A/B test

Training-only fitting and chosen-table freeze preceded this held-out evaluation. This is a registered retrospective extension: the historical held-out corpus had been examined in earlier phases. Naibbe tables were developed using Voynich statistics and are NOT blind controls. No translation or historical identification claim.

**Outcome:** the registered training selector chose the same setting for A, B and pooled, independently in Latin and Italian: weights `[40,8,8,8,4,4]` over alpha/beta1/beta2/beta3/gamma1/gamma2 (72 cards), respacing 22/36. Thus both selected Naibbe two-table arms are exact content aliases of their single-table nulls. Their per-seed probe readings match exactly. No distinct Naibbe A/B table contrast was instantiated by this selector. The fitting optimum is at the registered alpha-weight multiplier and respacing bounds; no expansion was performed.

A/B probe accuracy is 61.63% for Latin and 60.82% for Italian, versus 94.02% ZL. C9 is 63.37% with two arrangements and 63.59% with one. Section scores 46.52%-50.80% are below the 61.50% majority baseline, rather than reproducing the ZL 62.30% reading. These are descriptive outcomes of this bounded weight/respacing family; they do not rule out unrestricted pairs of distinct codebooks. No table adjustment followed held-out results.

## Selected table settings

| Plaintext/control | A setting | B setting | Single/unknown setting | Same A/B? |
|---|---|---|---|---|
| C1 | D52_alpha_double_R22 | D52_alpha_double_R22 | D52_alpha_double_R22 | True |
| C2 | D52_alpha_double_R22 | D52_alpha_double_R22 | D52_alpha_double_R22 | True |
| C9 | G30 | G57 | G30 | False |

D52/D78 identify the author base weight vector, followed by the one-table weight adjustment and respacing numerator /36. Exact six-table weights and totals are in CHOSEN_TABLES.json; adjusted decks need not contain 52/78 cards. G IDs identify original C9 shuffled cyclic-table arrangements. Encoder fitting used h2, W1, exact repetition and edit1 repetition, scaled by training candidate variation. Probes and vocabulary overlap did not select tables.

## Test fingerprints, mean across five paired seeds

| Corpus | Subset | h2 | abs delta h2 | W1 | Exact repetition | Edit1 repetition |
|---|---|---:|---:|---:|---:|---:|
| ZL | A | 1.728274 | 0.000000 | 0.000000 | 0.884% | 4.798% |
| ZL | B | 1.524449 | 0.000000 | 0.000000 | 0.873% | 4.101% |
| C1_two | A | 1.535155 | 0.193119 | 0.418321 | 0.303% | 2.008% |
| C1_two | B | 1.523329 | 0.014021 | 0.181962 | 0.524% | 2.042% |
| C1_single | A | 1.535155 | 0.193119 | 0.418321 | 0.303% | 2.008% |
| C1_single | B | 1.523329 | 0.014021 | 0.181962 | 0.524% | 2.042% |
| C2_two | A | 1.546698 | 0.181576 | 0.390294 | 0.492% | 2.626% |
| C2_two | B | 1.529689 | 0.011802 | 0.190981 | 0.628% | 2.565% |
| C2_single | A | 1.546698 | 0.181576 | 0.390294 | 0.492% | 2.626% |
| C2_single | B | 1.529689 | 0.011802 | 0.190981 | 0.628% | 2.565% |
| C9_two | A | 1.856373 | 0.128099 | 1.007306 | 0.000% | 2.146% |
| C9_two | B | 1.847531 | 0.323082 | 1.123734 | 0.000% | 1.955% |
| C9_single | A | 1.856373 | 0.128099 | 1.007306 | 0.000% | 2.146% |
| C9_single | B | 1.848705 | 0.324256 | 1.125158 | 0.000% | 2.112% |

ZL is one fixed target and one cached 1729 model; its displayed seed SD is 0, not an estimate of target uncertainty. The abs delta h2 column averages per-seed absolute distances; it is not the absolute difference of the displayed mean h2 from target. Full per-seed values, SDs, signed repetition differences, supports and A/B differences are in fingerprints.csv, TEST_FINGERPRINT_SUMMARY.csv and A_B_differences.csv. W1 compares each generated subset only with its matching held-out ZL subset.

## Held-out line probes

| Corpus | A/B accuracy mean +/- SD | A/B balanced accuracy | Section accuracy mean +/- SD | Section majority baseline | Section baseline using A/B alone |
|---|---:|---:|---:|---:|---:|
| ZL | 94.022% +/- 0.000% | 94.929% | 62.299% +/- 0.000% | 61.497% | 53.476% |
| C1_two | 61.630% +/- 1.159% | 69.746% | 46.524% +/- 3.152% | 61.497% | 53.476% |
| C1_single | 61.630% +/- 1.159% | 69.746% | 46.524% +/- 3.152% | 61.497% | 53.476% |
| C2_two | 60.815% +/- 2.082% | 68.833% | 47.861% +/- 1.310% | 61.497% | 53.476% |
| C2_single | 60.815% +/- 2.082% | 68.833% | 47.861% +/- 1.310% | 61.497% | 53.476% |
| C9_two | 63.370% +/- 2.203% | 70.668% | 48.984% +/- 1.420% | 61.497% | 53.476% |
| C9_single | 63.587% +/- 0.859% | 70.918% | 50.802% +/- 0.535% | 61.497% | 53.476% |

These are the same Transformer/T1 baseline 96-step representation and scaler/logistic instruments on all arms. Encoder/model seeds are paired, so their separate variability is not identifiable here. The primary 1729 cached ZL model reproduces the old 94.02% A/B and 62.30% section probe exactly; section majority baseline 61.50%. No approximately94% threshold was used to tune anything. Validation labels choose logistic C only; encoder settings use training pages only. Within-A/B section probes, class support and selected C are retained in probes.csv; rare/unseen sections and A/B-section confounding limit interpretation.

## Held-out A/B vocabulary overlap

| Corpus | Jaccard mean | A tokens covered by B vocabulary | B tokens covered by A vocabulary |
|---|---:|---:|---:|
| ZL | 12.171% | 47.819% | 50.316% |
| C1_two | 21.119% | 69.716% | 73.449% |
| C1_single | 21.119% | 69.716% | 73.449% |
| C2_two | 22.243% | 70.665% | 74.715% |
| C2_single | 22.243% | 70.665% | 74.715% |
| C9_two | 100.000% | 100.000% | 100.000% |
| C9_single | 100.000% | 100.000% | 100.000% |

## Scope and limitations

One sequential Latin stream and one Italian stream were used, with disjoint fixed character chunks per page and no plaintext repetition/padding. The paired two/single arms receive identical source chunks. Exact ciphertext word-slot layout is imposed and native Naibbe alphabets are shared across A/B. Word resegmentation and discarded suffixes mean this is not source syntax preservation. Unknown A/B pages receive pooled settings; all page labels are inherited metadata.

The C9 two-arrangement null keeps the same original 512-cell word inventory and changes shuffled cyclic order/offset; it has less lexical flexibility than the Naibbe family. Candidate search budget is matched but mechanism/expressivity is not. The primary clean-only experiment adds no synthetic transcription noise.

Both table settings, candidate losses, zero-scale fallbacks, source/code/input hashes, generation spans, five-seed metrics and paired two-minus-single probe differences are retained. Prior model/encoder failures are not erased. Ninety-six-step models are fixed-budget instruments and may still be learning. Descriptive point estimates and seed SDs are not equivalence or significance tests.

Original phases, C12 terminal files and C16 holds remain hash-identical. No new C12 sweep, C16 decode/score or ZL language-model training occurred. New target fingerprints/probes are confined to this explicitly requested Phase7 test. Stop; no parameter rescue or follow-up sweep is scheduled.

Supplemental audits: all nine training minima match the frozen selections; 60 training regeneration checks and ten Naibbe two/single content-alias checks pass. Filesystem chronology and hash-chain receipts confirm registration before fitting and selected-table freeze before generated held-out data. See SCIENTIFIC_OUTCOME.json and TRAINING_REGENERATION_AND_ALIAS_AUDIT.json. C9 source-offset fields are layout coordinates for generated words, not consumed Latin/Italian plaintext; C9 has no plaintext.

Fixed-budget diagnostic: 30/30 new control fits selected their final checkpoint. No convergence claim or budget extension.
