# C16-KH: replication and extension — Phase 6

**Status: automatic run completed; coherence selection FAILED.** All 200 selected primary-arm items contain only `<UNK>`. The hapax-based unknown-token mass gives these lines high LM scores; this ranking does not measure useful coherence. The failed panel, outputs and frozen rules are preserved without post-result retuning. This is not an exact reproduction of the 2016 executable or published numerical results. No translation claims. No decoded lines were rated by the assistant.

## What was implemented

Frequency-initialized, decomposition-pattern constrained substitution search on word alphagrams, followed by exact trigram Viterbi decoding with deleted interpolation. The original full letter mapping and exact Tanach edition are not specified in the paper. The author software site was unavailable in logged retrievals, so the mapping was re-derived. Every numerical search choice, source substitution, EVA/Currier difference, alphabet mismatch and sensitivity policy is recorded in [DECISIONS.md](DECISIONS.md) and [PRE_SCORING_AMENDMENTS.md](PRE_SCORING_AMENDMENTS.md). These differences prevent a claim of exact replication.

The frozen 24 reading variants are the Cartesian product of within-word direction, word order, line order and row/approximate-column/boustrophedon traversal. Identical variants were applied to every source in each lexicon arm. Within-word reversal must disappear under alphagramming; its equality checks passed. Line order often has no effect because the decoder restarts at line boundaries. Duplicate variants are retained in the full table. Columnar reconstruction uses word slots, without x-coordinates.

Each clean page/document has its own fitted substitution key. Noise versions reuse their clean key. Scores use the same training LM that decodes candidate sequences, so they are optimization scores, not independent coherence validation. Top-line selection can favor short, repeated or unknown-containing outputs. No human interpretation was used to pick results.

## Coverage and source accounting

| Source | Version | Loci/lines | Words | Documents/pages | Size mismatch |
|---|---|---:|---:|---:|---|
| ZL | clean | 5,385 | 39,026 | 227 | All loci |
| C1 | clean | 3,996 | 34,509 | 204 | Controls cover running layout only |
| C1 | noise | 3,996 | 33,691 | 204 | Controls cover running layout only |
| C9 | clean | 3,996 | 34,509 | 204 | Controls cover running layout only |
| C9 | noise | 3,996 | 33,663 | 204 | Controls cover running layout only |
| C11 | clean | 3,996 | 34,509 | 204 | Controls cover running layout only |
| C11 | noise | 3,996 | 33,689 | 204 | Controls cover running layout only |
| C17 | clean | 1,617 | 10,075 | 38 | YES: C17 is short; no padding |
| C17 | noise | 1,617 | 9,856 | 38 | YES: C17 is short; no padding |

All 5,385 corrected ZL loci were processed, including labels, other diagram loci and flagged readings. Existing canonical parsing and first-alternative choices were inherited; raw transcription bytes were preserved. Null C1/C9/C11 layout covers 3,996 running loci, not ZL labels/other diagrams. Label-specific null comparisons are therefore unavailable, not zero. Section tables preserve this coverage distinction.

C17 contains 38 supplied documents, not 42 recovered volunteer documents; the repository metadata also identifies experimenter material. Per-document IDs, group metadata, file hashes, injective maps and noise operations are retained. Missing archive documents are not reconstructed. C17 has 10,075 clean words, substantially fewer than ZL. All C17 comparison tables explicitly flag this mismatch. Its inherited page labels are arbitrary, assigned before scoring; unsupported sections remain unsupported.

| Lexicon arm | Admitted works | Training words | Held-out words | Training word types |
|---|---:|---:|---:|---:|
| tanakh | 39 | 246,168 | 60,704 | 34,978 |
| medieval | 79 | 588,464 | 150,755 | 44,775 |

The Tanakh arm substitutes public-domain `Tanach with Text Only` for the unspecified published edition. Medieval Hebrew uses public-domain Torat Emet Mishneh Torah volumes. All 123 selected files were retrieved after 13 logged network retries; five versions with `unknown` licenses were excluded. The medieval arm is therefore 79 admitted volumes, not a claim of complete Mishneh Torah coverage. First 80% of segments per work train the models; last 20% remain held out. Hebrew combining marks and final forms are normalized automatically and identically; no spelling correction, affix stripping or manual word adjustment.

## Dictionary coverage and ambiguity

Baseline is LTR within words, LTR word order, top-to-bottom rows. Token hit means at least one exact alphagram candidate. Candidate mean includes zero-hit words. Type hit is presence in at least one page-specific key context. These are dictionary availability rates, never translation accuracy.

| Arm | Source | Dictionary token hit | Candidates/token | Ambiguous token rate |
|---|---|---:|---:|---:|
| tanakh | ZL | 22.68% | 0.575 | 14.98% |
| tanakh | C1 | 30.87% | 0.802 | 23.61% |
| tanakh | C9 | 30.34% | 0.735 | 18.96% |
| tanakh | C11 | 22.26% | 0.566 | 14.85% |
| tanakh | C17 (short C17) | 24.21% | 0.592 | 16.84% |
| medieval | ZL | 24.86% | 0.543 | 13.85% |
| medieval | C1 | 33.84% | 0.734 | 21.72% |
| medieval | C9 | 29.67% | 0.651 | 17.75% |
| medieval | C11 | 24.09% | 0.528 | 13.45% |
| medieval | C17 (short C17) | 30.93% | 0.610 | 15.89% |

Full clean/noise, section, running/label/other and C17 writer tables are in `results/<arm>/variant-source-section.csv`. Candidate lists and selected outputs are in compressed token ledgers. Cross-context pair agreement (excluding pairs within the same physical line), known-only agreement, cross-page agreement and within-key agreement are in `cross-context-consistency.csv`. Equal outputs may arise mechanically from the same key and language model; unknown-inclusive agreement may be inflated by repeated `<UNK>`.

| Arm | Source | Known-only context agreement | Cross-page incl. unknowns | Within-key incl. unknowns |
|---|---|---:|---:|---:|
| tanakh | ZL | 10.82% | 58.28% | 99.40% |
| tanakh | C1 | 21.88% | 24.95% | 93.32% |
| tanakh | C9 | 0.84% | 53.89% | 99.39% |
| tanakh | C11 | 17.30% | 36.69% | 98.65% |
| tanakh | C17 (short C17; writer-scoped) | 94.72% | n.a. | 98.08% |
| medieval | ZL | 7.32% | 57.19% | 99.47% |
| medieval | C1 | 15.10% | 17.64% | 99.46% |
| medieval | C9 | 1.08% | 54.79% | 99.54% |
| medieval | C11 | 9.04% | 14.45% | 99.06% |
| medieval | C17 (short C17; writer-scoped) | 99.03% | n.a. | 99.32% |

C17 word identities are scoped by anonymous writer because each document has its own injective symbol inventory. Cross-writer collisions of relabeled strings do not establish the same original word. Use C17-writer-context-consistency.csv and C17-context-consistency-scoped.csv; the unscoped C17 agreement rows in the raw per-arm tables are retained only as an auditable reporting error and must not be interpreted. This correction changes no fit, decoding, ranking or blind selection.

## Maximum-over-variants comparison

The table gives each source its own best global variant. The registered linewise maximum envelope, used for the blind selection, is also reported separately in `linewise-max-scores.csv`; it may combine different variants across lines. Both are retained rather than choosing whichever comparison looks better. Primary requested source maxima are top-100 for ZL and top-25 for each null; an equal-25 sensitivity follows. These finite control-family maxima are descriptive; there is no calibrated p-value.

| Arm | Null | ZL best score | Null best score | ZL − null | Equal-25 difference |
|---|---|---:|---:|---:|---:|
| tanakh | C1 | -3.3078 | -3.3078 | +0.0001 | +0.0016 |
| tanakh | C9 | -3.3078 | -3.3075 | -0.0003 | +0.0012 |
| tanakh | C11 | -3.3078 | -3.3062 | -0.0015 | -0.0000 |
| tanakh | C17 (short C17) | -3.3078 | -3.3087 | +0.0009 | +0.0024 |
| medieval | C1 | -4.2123 | -4.1979 | -0.0144 | +0.0145 |
| medieval | C9 | -4.2123 | -4.2052 | -0.0071 | +0.0218 |
| medieval | C11 | -4.2123 | -4.1978 | -0.0145 | +0.0144 |
| medieval | C17 (short C17) | -4.2123 | -4.2181 | +0.0058 | +0.0347 |

**These maxima failed as coherence statistics.** The selected Tanakh envelope has 100% unknown tokens for ZL and every null; the medieval ZL envelope has 98.31% unknown tokens. Tanakh unknown unigram mass is 0.07016 and its interpolation weight is 0.52495, giving about 0.03683 unknown-token probability without higher-order support. This aggregate unknown state can outrank individual dictionary words. End-marker and length effects drive tiny maximum-score differences. These are not useful coherence advantages. No penalty, coverage filter, alternate LM or new variant was introduced after this failure. Best variant IDs, unknown fractions and lengths remain in the tables.

## Page-topic probe

The authored exact-form botanical/astronomical lists were frozen before scoring. `topic-section-comparisons.csv` reports selected-output and any-candidate rates, denominators and differences in each supported matching running-text section for every variant and both lexicons. All ZL label/other rates remain in the full section table. This narrow probe does not resolve inflection, ambiguity, general vocabulary or semantics; it is not a topic classifier. C17 labels are artificial and have incomplete section support. No words were added after results, and no decoded meanings were inspected to improve the probe.

Baseline running-text focal-section rates (selected outputs; n.a. means no support):

| Arm | Section / probe | ZL | C1 | C9 | C11 | C17 (short) |
|---|---|---:|---:|---:|---:|---:|
| tanakh | herbal / botanical | 0.03% | 0.06% | 0.15% | 0.03% | 0.13% |
| tanakh | astronomical / astronomical | 0.00% | 0.00% | 0.00% | 0.00% | n.a. |
| tanakh | zodiac / astronomical | n.a. | n.a. | n.a. | n.a. | n.a. |
| medieval | herbal / botanical | 0.03% | 0.04% | 0.15% | 0.04% | 0.00% |
| medieval | astronomical / astronomical | 0.00% | 0.00% | 0.00% | 0.00% | n.a. |
| medieval | zodiac / astronomical | n.a. | n.a. | n.a. | n.a. | n.a. |

## Blind coherence packet

**Preserved failed export, not a usable coherence experiment:** 200 source- and variant-stripped items (100 Voynich, 25 each C1/C9/C11/C17), with every selected token `<UNK>`. Selection follows the registered clean Tanakh linewise maximum/top-N rule; no replacement items were chosen. OS entropy supplies shuffling and opaque IDs. The separate key is procedurally sealed and SHA256 committed, not encrypted. Do not give the key, ledgers or this source-count report to raters. Rating fields and comments are blank. There is no reason to expend human rating effort on this degenerate panel.

- Duplicate decoded strings in the 200-item panel: 179 (retained).
- Key SHA256: `e7cb4f595566163cf66ade851ba4983034c0c0d14399eb16cc0bd61a597584a4`.
- Rater packet: `blind/rater-only.zip` (CSV, XLSX, instructions).
- Separate key: `sealed/key.zip`. The assistant did not open the sealed archive or self-rate outputs.

## Verification and limits

Synthetic unit tests passed (5). 20 final accounting/invariance checks passed; the broader lab-byte snapshot detected concurrent changes to 5 Phase 5 files. The pipeline wrote only within c16-kh and did not overwrite them. Before/after hashes are in CONCURRENT_CHANGE_RECEIPT.json. Frozen consumed inputs and algorithm hashes match. Independent verification checked 18,000 candidate records using count vectors, every key's injectivity, and context-pair arithmetic. C11 preserves all 34,509 matched source-word multisets. Under a fixed key its dictionary candidates must match ZL at those slots. Separate full-ZL fitting can differ because extra labels/diagram words enter the fit; such differences do not challenge the invariant.

No exact original software reproduction, validated key recovery on manuscript text, Hebrew identification, grammatical reading or translation has been established. The requested top-line coherence comparison failed under the registered scorer, rather than merely awaiting ratings. All failures, unknowns, surplus alphabet targets, search limits, duplicate variants and source exclusions remain visible. Work stops here.

## Sources and reproducibility

- Hauer, Bradley & Grzegorz Kondrak (2016). [Decoding Anagrammed Texts Written in an Unknown Language and Script](https://aclanthology.org/Q16-1006/). TACL 4:75–86. DOI:10.1162/tacl_a_00084.
- Gaskell, Daniel E. & Claire L. Bowern (2022). [Gibberish after all?](https://github.com/danielgaskell/voynich). CEUR Workshop Proceedings, International Conference on the Voynich Manuscript 2022, University of Malta. Modified MIT license preserved in `sources/C17-LICENSE-README.md`.
- [Sefaria export](https://github.com/Sefaria/Sefaria-Export) and per-version license metadata. Full receipts and hashes: [SOURCES.md](SOURCES.md).

Run `python test_core.py`, `python prepare.py` only for a new pre-score preparation, then `python run.py tanakh` and `python run.py medieval`; completed page/source checkpoints resume without extra starts. `python finalize.py`, the workbook builder and `python report.py` aggregate/export. Do not regenerate preparation over a scored registration. The recorded source bytes and algorithms are frozen locally.
