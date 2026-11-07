# Verified v7.2 qualification

Start with [REPORT.md](REPORT.md) and [QUALIFICATION.json](QUALIFICATION.json). Status: QUALIFIED_V7.2_ON_DECLARED_SCOPE. All eleven declared gates pass.

The original C3 bank is retained; the additional context-role bank, source-first controls and native-readable trap cohort are the approved v7.2 changes. Prior attempts remain read-only.

run.py is the frozen qualification driver. Do not rerun it into this sealed directory or edit its methods after outcomes. A revised experiment needs a new directory and freeze. It reuses old banks only when all key hashes and scoring projections match, and checkpoints new banks against a saved input hash.

verify.py independently checks frozen code/inputs, all bank/control quantiles, both negative confidence bounds, native support and historical preservation. Six regression tests include exact comparisons against the original raw evaluator. The preceding trap diagnosis has twenty additional infrastructure tests.

Source-first tokenization currently supports the two declared fixture modes. E2/v6 multi-token adapters, detailed E5/numeral qualification and native-uncertain whole-corpus loss handling are outside this qualification's scope. No Part B/C or vault execution is enabled.
