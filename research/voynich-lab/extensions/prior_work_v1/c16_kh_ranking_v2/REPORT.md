# C16-KH ranking v2

Status: ranking-only amendment executed. Human coherence ratings remain pending and blank.

This declared post-failure amendment uses the **existing v1 decoded lines and original LM**, as explicitly selected by the user. It changes only ranking eligibility and scoring: omit `<UNK>` targets, retain their positions in LM history, require at least 60% known tokens, and average original-LM log probabilities over known word targets. BOS/EOS are excluded from that mean. Empty/all-unknown lines are ineligible. All 24 v1 variants, two lexicon arms and C1/C9/C11/C17 clean/noisy nulls are preserved. No key, lexicon, decoded line or model was refit. The separate scorer-repair project was not imported.

The mechanical qualification passes. The before/after v1 input audit has no drift, including the byte hash of the original sealed key, whose contents were not opened. These checks establish implementation and preservation, not Hebrew coherence or qualification of the original language model.

## Side-by-side results

v1 selected all-unknown items. v2 removes that specific ranking failure, but retains the original LM and decoding choices. Its selected lines are often short. The v1 and v2 scores have different definitions, so raw score magnitudes are not directly comparable. Equal-N comparisons against nulls are descriptive; calibrated p-values were not estimated.

| arm | source | eligible_identities | actual_n | mean_words | minimum_known_fraction | unknown_fraction | v1_unknown_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tanakh | C1 | 530 | 25 | 2.24 | 0.6153846153846154 | 0.19642857142857142 | 1.0 |
| tanakh | C9 | 637 | 25 | 3.08 | 0.6 | 0.23376623376623376 | 1.0 |
| tanakh | C11 | 373 | 25 | 2.24 | 0.6 | 0.21428571428571427 | 1.0 |
| tanakh | C17 | 145 | 25 | 3.08 | 0.6 | 0.2857142857142857 | 1.0 |
| tanakh | ZL | 774 | 100 | 1.9 | 0.6 | 0.1631578947368421 | 1.0 |
| medieval | C1 | 686 | 25 | 2.56 | 0.6 | 0.265625 | 0.7339449541284404 |
| medieval | C9 | 519 | 25 | 2.52 | 0.6 | 0.2222222222222222 | 0.9801324503311258 |
| medieval | C11 | 499 | 25 | 1.72 | 0.6 | 0.16279069767441862 | 0.9738372093023255 |
| medieval | C17 | 313 | 25 | 2.96 | 0.6 | 0.24324324324324326 | 0.9888475836431226 |
| medieval | ZL | 1039 | 100 | 2.61 | 0.6 | 0.16475095785440613 | 0.9831410825199645 |

Full clean/noisy results: [v1/v2 table](report/v1_v2_side_by_side.csv), [all variants](report/variant_source_scores_v2.csv), [held-out Hebrew calibration](report/heldout_Hebrew_calibration.csv), and [equal-N null comparison](report/max_statistic_comparisons_v2.csv).

## Blind export

The clean Tanakh-arm rater package contains 200 eligible items: 100 ZL and 25 each C1/C9/C11/C17. Source and variant labels are stripped. Every item meets the registered known-token threshold. There are **97 duplicate decoded strings**, limiting independent information in subsequent ratings. They were retained rather than replaced after inspecting this outcome.

All coherence, grammaticality and comment fields are blank. No self-ratings were supplied. Workbook layout was checked with synthetic replacement text only. The independent key is separately sealed and was not opened for QA. The rater package contains CSV, JSON, instructions and XLSX, with no key.

[Rater-only package](blind/rater-only.zip). [Mechanical/input verification](report/VERIFICATION.json). [Workbook/package receipt](report/WORKBOOK_PACKAGE_RECEIPT.json).

The original v1 failure remains untouched. This amendment does not establish decipherment, meaningful text, or a successful repair of the original scorer.
