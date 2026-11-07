# Phase 9: later month annotations — registered calibration

**Calibration PASS: 32/32 registered cells passed.** All 160 positive datasets recovered the generating mapping/codebook and rejected the full max-over-families/languages shuffled null (each p=0.01). Negative controls rejected 0/160 times (p range 0.13–1.00). All 320 datasets completed without scorer/search exceptions. These are finite, paired control-bank outcomes, not independent language-corpus trials.

**Native-script herbal and zodiac tracks remain CLOSED. No later-annotation target fit was run. Phase 8 remains FAIL and unchanged.** This run stops at the explicitly requested registration/calibration stage, including on PASS. The annotation gate is qualified pending a separate target manifest, not an executed target result.

## Receipt defect preserved

**The strict full registration-manifest check FAILS for mutable RUN_STATE.json only.** I mistakenly included the progress/status file in the frozen-file list. The registered calibration code updates that file after fitting and writing the qualification decision. Every immutable registered code/source/name/assignment file remains byte-identical. No registered code or manifest was edited, no completion state was restored to hide the change, and no scientific fit or qualification threshold was rerun/changed.

RECEIPT_DEVIATION.json records the original and current hashes. RUN_STATE.registered_snapshot.json is an explicitly reconstructed before-state copy whose bytes match the original registered hash (including Windows newlines); it does not replace RUN_STATE.json. The first strict-audit failure is preserved. The independent post-outcome audit separately checks immutable hashes, that registered before-state hash, every saved model witness/max score, p-value, recovery criterion and gate decision. Its arithmetic/witness result is PASS with the receipt defect documented; it does not relabel the strict all-file manifest PASS. The registered report.py, which calls the same strict verifier, was not executed; this report is reporting-only output from already saved results.

## Calibration summary

| Family | Positive recovery + rejection | Negative rejections | Cells passing |
|---|---:|---:|---:|
| Monoalphabetic | 20/20 | 0/20 | 4/4 |
| Positional B/M/E | 20/20 | 0/20 | 4/4 |
| Six fixed published Naibbe tables | 120/120 | 0/120 | 24/24 |

Every cell required at least 4/5 positives jointly recovering the true identifiable mapping and rejecting the maximum null, no more than 1/5 negative rejections, and completion of all ten datasets. All cells actually achieved 5/5 and 0/5. No pooled override or post-outcome lexicon/model change.

| Language | Generator | Mapping recovered /5 | Recovery + max-test rejection /5 | Negative rejections /5 | Pass |
|---|---|---:|---:|---:|---|
| Latin | mono | 5 | 5 | 0 | True |
| Latin | position | 5 | 5 | 0 | True |
| Latin | naibbe_alpha | 5 | 5 | 0 | True |
| Latin | naibbe_beta1 | 5 | 5 | 0 | True |
| Latin | naibbe_beta2 | 5 | 5 | 0 | True |
| Latin | naibbe_beta3 | 5 | 5 | 0 | True |
| Latin | naibbe_gamma1 | 5 | 5 | 0 | True |
| Latin | naibbe_gamma2 | 5 | 5 | 0 | True |
| Italian | mono | 5 | 5 | 0 | True |
| Italian | position | 5 | 5 | 0 | True |
| Italian | naibbe_alpha | 5 | 5 | 0 | True |
| Italian | naibbe_beta1 | 5 | 5 | 0 | True |
| Italian | naibbe_beta2 | 5 | 5 | 0 | True |
| Italian | naibbe_beta3 | 5 | 5 | 0 | True |
| Italian | naibbe_gamma1 | 5 | 5 | 0 | True |
| Italian | naibbe_gamma2 | 5 | 5 | 0 | True |
| German | mono | 5 | 5 | 0 | True |
| German | position | 5 | 5 | 0 | True |
| German | naibbe_alpha | 5 | 5 | 0 | True |
| German | naibbe_beta1 | 5 | 5 | 0 | True |
| German | naibbe_beta2 | 5 | 5 | 0 | True |
| German | naibbe_beta3 | 5 | 5 | 0 | True |
| German | naibbe_gamma1 | 5 | 5 | 0 | True |
| German | naibbe_gamma2 | 5 | 5 | 0 | True |
| Occitan | mono | 5 | 5 | 0 | True |
| Occitan | position | 5 | 5 | 0 | True |
| Occitan | naibbe_alpha | 5 | 5 | 0 | True |
| Occitan | naibbe_beta1 | 5 | 5 | 0 | True |
| Occitan | naibbe_beta2 | 5 | 5 | 0 | True |
| Occitan | naibbe_beta3 | 5 | 5 | 0 | True |
| Occitan | naibbe_gamma1 | 5 | 5 | 0 | True |
| Occitan | naibbe_gamma2 | 5 | 5 | 0 | True |

## Completed cited period-name list

One cited form per language/month was frozen before control generation or scoring. This is a bounded candidate list, not an exhaustive historical lexicon. Exact locators, source URLs, normalized strings and evidence qualifications are in PERIOD_NAMES.json and NORMALIZED_NAMES.json.

| Month | Latin | Italian | German | Occitan |
|---|---|---|---|---|
| 3 | Martius | Marzo | merze | Mars |
| 4 | Aprilis | Aprile | aberellen | Abril |
| 5 | Maius | Magio | Meye | Mai |
| 6 | Junius | Giugnio | Brachmanot | Junh |
| 7 | Julius | Luglio | huemaendes | Julh |
| 8 | Augustus | Agosto | augst | Agost |
| 9 | September | Septembre | öigstin | Setembre |
| 10 | October | Octobre | wynmaent | Octobre |
| 11 | November | Nouembre | wintermonat | Novembre |
| 12 | December | Decembre | wintermonat | Desembre |

- Latin: [Brandeis Hours catalogue transcript](https://www.manuscripts.org.uk/chd.dk/gui/Brandeis_gui.html), calendar folios 3–12, manuscript dated c1420–1430; corroborated by [The National Archives historical Latin reference](https://www.nationalarchives.gov.uk/latin/reference/dating-latin-documents/). This is scholarly catalogue/reference evidence, not new manuscript-facsimile adjudication.
- Italian: [Piero Crescentio de agricultura, Venice 1495](https://archive.org/details/pierocrescentiod00cres), Book XII chapters 3–12, scans n357–n362. All selected headings were read in the saved facsimiles. Magio, Giugnio, Septembre, Octobre, Nouembre and Decembre remain as printed; OCR misreadings were not adopted as historical spellings. This witness is later than the vellum date and does not date the added annotations.
- German: [Grotefend historical glossary](https://www.handschriftenzentren.de/materialien/grotefend/g_m.htm) and [Trier Middle High German lexical index](https://woerterbuchnetz.de/?lemid=FM00555&sigle=FindeB). Exact dated quotes (1421 aberellen, 1470 Meye, 1422 Brachmanot, 1367 huemaendes, 1467 augst, 1453 öigstin) are distinguished from undated historical lexical entries. The regional and grammatical forms are not claimed to represent one dialect or uniform case. Wintermonat is intentionally retained for both November and December, reflecting documented ambiguity; it is not an exclusive month identifier.
- Occitan: Raynouard, Lexique roman, selected historical entries and medieval calendar/troubadour quotations, with full volume/lemma/OCR-line locators in PERIOD_NAMES.json. [Volume III printed p31](https://archive.org/download/lexiqueromanoudi03raynuoft/page/n40.jpg) confirms Desembre where OCR is corrupt. These are edited historical lemmas, not diplomatic fifteenth-century local spellings. Raw texts and the checked page image are preserved.

The original annotation readings come from [Zandbergen’s MON table](https://www.voynich.nu/writing.html). Their Romance language is disputed. French is not one of the four tested languages; any later best-language result cannot establish the annotator’s language. Duplicate April/May panels and German November/December name ambiguity are retained rather than counted as independent month identities.

## Frozen method and limits

The objective is the largest number of full label/name matches under one global consistent model and one candidate language, denominator twelve. Every observed and each of 99 shuffled datasets reoptimizes and maximizes over monoalphabetic substitution, beginning/interior/end substitution, all six fixed Naibbe tables, and all four languages. The exact finite algorithms report matched items, mappings/table, integer bounds and search-node counts; no optimizer cutoff or best-found approximation is substituted for a maximum.

Plaintext names use the same author-derived 23-letter normalization across all families/languages; encoded symbols do not receive spelling substitutions. Source parentheses are finite optional literal groups; all alternatives move together under shuffles. There is no manual correction, arbitrary missing-letter restoration, edit distance, stemming, reversal or post-outcome candidate addition.

Synthetic data use the twelve source month slots, duplicate April/May identities, five seeds, and the declared parenthesis pattern. Positive mapping recovery is evaluated in the generating-language/family fit, without truth in fitting. Mono/position recovery covers only mapping entries observed in these labels. Naibbe recovery uniquely identifies the fixed generating table, not a stochastic deck schedule or necessarily a unique segmentation. Family selection itself may tie because positional substitution contains monoalphabetic substitution.

This is an in-sample exact-string crib calibration with wrong-pair/max-statistic controls, not held-out new-name generalization or handwriting recognition. The statistic can exploit name length and repeated-character patterns. Passing this finite bank does not prove phonetic content, historical generation, the correctness of an arbitrary botanical identification, or that every possible cipher would be recovered.

Naibbe: Michael A. Greshko (2025), [The Naibbe cipher](https://doi.org/10.1080/01611194.2025.2566408), author code commit 719f2f4c4d1eacf95fabf48381cd84fc6cd94279. Copyright/license/citation notices and all six published fixed tables are copied in author/. These tables were designed using Voynich statistics and are NOT blind controls. Stochastic mixed decks and fitted glyph tables are outside this declared subfamily.

## Saved receipts and stop

Independent read-only validation checked 1,024,000 saved model witnesses, 31,680 null records, all 320 p-values/recovery outcomes and all 32 cell decisions. It introduced no new fit, scoring run or permutation draw. Code and candidate/source immutability are verified separately from the preserved mutable-state manifest defect.

REGISTRATION.json froze sources, candidates, code, assignments and seeds before synthetic generation; DATA_READY.json froze the generated bank before fitting. Each observed fit and all 99 null assignments/model witnesses are retained in results/, with nulls in compressed JSONL. No missing intermediate mappings are silently claimed present.

Preservation: 1,837 pre-existing Phase 8 and Phase 9 source-audit files remain byte-identical. Original FAIL, source freezes and earlier registrations are unchanged. Native tracks stay closed and annotation-target fitting remains unrun. No new scientific registration, rescue bank, retuning or translation claim follows this calibration result.
