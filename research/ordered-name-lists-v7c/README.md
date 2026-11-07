# v7 A/C work area

Start with [REPORT.md](REPORT.md). This is incomplete infrastructure plus a historical source draft. It contains no manuscript result.

Run20 focused checks with Python's unittest discovery in HARNESS. Run HARNESS/verify.py for artifact/integrity verification. HARNESS/qualify.py reproduces the frozen initial known-text experiment and takes several minutes. RapidFuzz3.14.1 is vendored locally; dependency metadata and license remain in HARNESS/vendor. Reproduction overwrites named result files; preserve the directory before a revised experiment.

C2_pretest.run checks the list, harness and budget gates before opening an input. They currently deny scoring. There is no vault runner.
