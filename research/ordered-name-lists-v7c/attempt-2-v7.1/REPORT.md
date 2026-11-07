# v7.1 attempt 2 — requalification

25 October 2026. **NOT_QUALIFIED.** Attempt 1 remains unchanged.

The amendment fixes the clean-positive control failure. The true key and both noisy readings pass the amended rules with all six actual v5 C2 families. The random-proposal gate passes. The unchanged actual-flexible-key requirement is unmet: both trap readings are PARTIAL, not FAIL. This attempt therefore does not authorize real proposed-key evaluation or any Part B/C scoring.

| Evaluation | Final verdict | Coherence bits |
|---|---|---:|
| True key | PASS | 25247.657 |
| 20% corrupted key | PASS | 7807.635 |
| Noisy synthetic H | PASS | 24046.335 |
| Noisy synthetic F | PASS | 24040.062 |

The 20%-corrupted key also passes. Its coherence is the same 7,807.635 bits retained from attempt 1. Positive coherence is a known property of a key retaining substantial information; it is necessary but insufficient, and the near-miss gate does not require a FAIL. This result does not establish exact key recovery.

## Correct controls and multiplicity

[AMENDMENT-v7.1.md](AMENDMENT-v7.1.md), [PLAN.json](PLAN.json) and their seals preceded attempt-2 scoring. The original E1–E6 raw-score implementation and K were preserved. Clean and corrupted real-text C3 banks were reused with identical key hashes; new control/noisy banks used the same declared random-key families. Each real/control bank has 1,000 keys.

E3 uses C1 word shuffling and each C2 family. E4, and supported E1/E2, use C1 glyph shuffling and each C2 family. E5 requires its within-band control if claimed; E5 was not claimed here. Real values must strictly exceed the control distribution's nearest-rank 95th percentile. PASS still requires positive coherence and at least two evaluations reaching the conservative 99th-percentile criterion. PARTIAL now uses the conservative 99.8th-percentile criterion, with ties counted in the upper tail.

## Noisy dual reading

The measured non-zodiac paragraph H/F disagreement is 4423/112084 = 3.94614753%, across 21,669 readable paired word slots. Entire folios f67–f73 were excluded. Unequal-boundary/slot-count lines and unknown pairs are counted separately in [HF-DISAGREEMENT.json](HF-DISAGREEMENT.json); disagreement is not adjudicated transcription error.

The fixed synthetic corruption uses 280/7099 differing glyph sites (3.94421750%), split between disjoint H/F masks. Both views preserve the known held-out word/line geometry and use the same clean training corpus and fixed key. This qualifies a substitution-noise positive on this fixture, not a general model of transcription boundary errors. Masks and both full input datasets are retained.

## Random proposals

200 independently drawn proposals: **{'FAIL': 198, 'PARTIAL': 2}**. PASS rate 0.00%; not-PASS rate 100.00%. The one-sided exact 95% Clopper–Pearson upper PASS bound is **1.4867%**, below the 3% cap. The two-sided-95%-interval upper endpoint, reported as sensitivity, is 1.8275%. PARTIAL is reported and is not a negative-gate failure.

These are conditional calibration results for this declared corpus/key family and fixed C3 bank, not a universal false-positive guarantee.

## Actual manuscript flexible-key trap

A fresh program fitted whole-word inventory/context values only to the preregistered training pages. The target Latin dictionary supplied values; held pages were never used to fit them. Unknown source slots stayed in place. The key tokenizer uses exact training whole-word units and character fallback for unseen words; hundreds of explicit section conditions are charged in K. This is a deliberate dictionary-hit maximizer, not a proposed reading.

| Reading | Verdict | K bits | Coherence bits | E1 held rate | C3 median | Upper-tail p |
|---|---|---:|---:|---:|---:|---:|
| H | PARTIAL | 2431.280 | -2431.012 | 43.4457% | 41.5730% | 0.000999 |
| F | PARTIAL | 2391.108 | -2390.836 | 41.5094% | 39.6226% | 0.000999 |

The small E1 excess reaches the corrected PARTIAL threshold, while the complexity cost overwhelms its gain. E3/E4 are NOT ESTIMABLE because each held reading contains two uncertain slots under the original fail-closed loss policy. Neither trap can PASS, but the specification still requires the literal verdict FAIL. That gate is preserved and remains unmet.

The trap's C2 results remain explicitly provisional. Completing C2 cannot remove a PARTIAL label determined by the real-text C3 rank, or make its negative coherence positive. The final real-generator controls were completed for the true key, corrupted key and both noisy positives.

A further adapter limitation is retained: C1 glyph shuffling presently acts on supplied key-unit arrays. For the trap's whole-word units, it cannot shuffle inside a single unit. A source-glyph shuffle followed by retokenization is needed to qualify that control for arbitrary word/group tokenizers. A source-first adapter for the two fixture tokenizer modes was built after this attempt and passes six authored engineering tests in diagnostics/. It has not been used to rescore the frozen attempt; that requires a new code freeze. No interpretation or fixed-key result has been promoted from this limitation. The literal PARTIAL result does not disappear merely by repairing the matched control.

## v5 generator controls

All G1–G6 were generated through the existing source_contract.produce_from_development entrypoint after its eight owning code hashes were checked against the qualified v5 seal. G1–G4 use the current cut-2 sealed Latin development source, with contiguous same-work windows and no wrapping. G5 uses the pinned unmodified published implementation, its native layout and seed-line exclusion. G6 uses the registered table/grille mechanism. Default parameters and seeds were fixed before execution.

Each family supplied 40 lines: G1–G4/G6 have 480 original word slots, and published G5 has 318 words in its native layout. Each final C2 distribution uses the 1,000 corresponding C3 keys. These are engineering mechanism controls; no v5 claim recovery, survivor selection, reserve-body read, or elimination ran. Full output and source/mapping receipts are in [V5-C2-DATA.json](V5-C2-DATA.json).

## Scope and continuation

The clean/noisy/negative changes are implemented and tested, but **Part A is not qualified for real keys**. Keep the failed strict trap gate and the missing loss/control-adapter coverage visible. Resolve those definitions and adapters under a fresh freeze before another attempt; do not relabel this attempt after seeing the outcomes.

Attempt 1's 130 original file contents remain preserved: 128 still match at their original paths, and two administrative files have byte-identical backups in the separate budget amendment directory. That external workflow superseded BUDGET.json and JOINT-DECLARATION-FREEZE.json during this run, recording a 0.005 nonrecycling reservation with zero vault tests and no execution authorization. This attempt did not allocate it or evaluate that amendment's statistical validity. See CONCURRENT-ADMINISTRATION.json for exact hashes and backup paths. Attempt 1's failed scientific verdict, corrupted-key coherence and all failures remain unchanged. C2 structural looks remain zero and historical LISTS remains a draft. No Part B/C score, vault result or vault authorization was created here.

[QUALIFICATION.json](QUALIFICATION.json) contains every gate and final score. [VERIFICATION.json](VERIFICATION.json) records method/artifact checks; [TEST-LOG.txt](TEST-LOG.txt) records the focused v7.1 tests. All intermediate provisional outcomes, both trap keys, data, masks and random-key banks are retained.
