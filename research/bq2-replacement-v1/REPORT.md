RETROSPECTIVE — all material exposed or uncertified (v100/v102).

Both readings failed the frozen nominal-calibration gate. All practical-null bounds cleared the separate5% tolerance; this does not override the nominal-size condition. No manuscript heterogeneity statistic, p, τ² or I² was computed.

| Blocking control | Reading | Flags/N | Rejection rate | Simultaneous exact interval | Nominal target |
|---|---|---|---|---|---|
| section_baseline_homogeneous | H | 182/5000 | 3.640% | [2.914%, 4.479%] | 2.5% |
| section_baseline_homogeneous | F | 166/5000 | 3.320% | [2.628%, 4.126%] | 2.5% |

In this control the expected effect is+.08 in every context, while context baseline probabilities differ. The lower bounds exceed2.5% in both readings, establishing a calibration problem at the predeclared nominal level for this candidate on this geometry. The problem is not a residual undefined statistic. No replacement rule, extra trials, altered baseline or guarded-flag fallback was used after seeing it.

Planted+.12 power was only47.9%–51.6% across the four positive-control cells. Power was descriptive by design; it reinforces why a no-detection result would not establish a uniform rule. Here both manuscript readings remain unscored. The scientific heterogeneity question remains unresolved.

The14 simultaneous intervals in the main table cover10 point-flag null rates and4 point-flag power rates. Supplementary guarded-power intervals in JSON are per-proportion descriptive intervals and are not included in that14-interval simultaneous family.

Separate B-Q2 replacement R1. Original attempts and the original unqualified B-Q2 remain unchanged. The replacement retains raw folio×ending MH effects, uses positive Jeffreys-stabilized binomial working variances, and centers heterogeneity within each scribe. Qualification, not merely mathematical finiteness, gates scoring.

| Reading | Supported folios | Context folios C1–C5 | Qualification | Manuscript result | Adjusted p |
|---|---|---|---|---|---|
| H | 76 | [19, 20, 6, 22, 9] | NOT QUALIFIED | BLOCKED: QUALIFICATION | None |
| F | 72 | [19, 20, 4, 22, 7] | NOT QUALIFIED | BLOCKED: QUALIFICATION | None |

A blocked reading has no new manuscript statistic, p, REML or I². H/F were never pooled. No failed permutation or synthetic trial was dropped; scoreable zero empirical variance uses the frozen positive working variance, and all-tie scores remain degenerate rather than negative evidence.

| Reading | Scenario | Flags/N | Simultaneous exact interval | Decision | Nominal alarm | Guarded flags |
|---|---|---|---|---|---|---|
| H | homogeneous_null | 129/5000 | [1.974%, 3.302%] | CERTIFIED BELOW TOLERANCE | False | 109 |
| H | homogeneous_positive | 133/5000 | [2.044%, 3.392%] | CERTIFIED BELOW TOLERANCE | False | 116 |
| H | scribe_baseline_homogeneous | 128/5000 | [1.956%, 3.280%] | CERTIFIED BELOW TOLERANCE | False | 113 |
| H | section_baseline_homogeneous | 182/5000 | [2.914%, 4.479%] | CERTIFIED BELOW TOLERANCE | True | 161 |
| H | available_homogeneous | 92/5000 | [1.334%, 2.464%] | CERTIFIED BELOW TOLERANCE | False | 84 |
| H | heterogeneous_positive | 516/1000 | [46.947%, 56.234%] | DESCRIPTIVE POWER | False | 495 |
| H | available_heterogeneous_positive | 492/1000 | [44.560%, 53.850%] | DESCRIPTIVE POWER | False | 465 |
| F | homogeneous_null | 142/5000 | [2.202%, 3.593%] | CERTIFIED BELOW TOLERANCE | False | 119 |
| F | homogeneous_positive | 143/5000 | [2.220%, 3.615%] | CERTIFIED BELOW TOLERANCE | False | 128 |
| F | scribe_baseline_homogeneous | 157/5000 | [2.468%, 3.927%] | CERTIFIED BELOW TOLERANCE | False | 142 |
| F | section_baseline_homogeneous | 166/5000 | [2.628%, 4.126%] | CERTIFIED BELOW TOLERANCE | True | 148 |
| F | available_homogeneous | 88/5000 | [1.266%, 2.372%] | CERTIFIED BELOW TOLERANCE | False | 78 |
| F | heterogeneous_positive | 486/1000 | [43.964%, 53.252%] | DESCRIPTIVE POWER | False | 459 |
| F | available_heterogeneous_positive | 479/1000 | [43.271%, 52.554%] | DESCRIPTIVE POWER | False | 455 |

Fixed run:5,000 trials per five required nulls and1,000 per two positives per supported reading (54,000 if both support), each with its own fresh independent10,000-shuffle bank. Point-p flags use p≤.025. Fourteen simultaneous exact Clopper–Pearson intervals quantify outer simulation uncertainty; qualification requires all practical-null upper bounds≤5%, no lower bound>.025 nominal alarm, and no numeric failures. Power has no qualification gate and is descriptive; guarded flags additionally require the inner-MC interval to clear the manuscript cutoff. No extension or retuning occurred.

A no-detection result does not establish a constant-strength rule, especially if planted-positive power is weak or τ² intervals are broad. Monte Carlo boundary results remain inconclusive without adding permutations. If qualification fails, the manuscript stays unscored for that reading. Selection of C1/C4 for large earlier effects remains a retrospective bias. No new scribe2-only sensitivities were inferentially scored: their smaller geometries were not independently qualified.

The five calibration nulls distinguish identical baseline, common+.08 effect, between-scribe baseline changes, between-section baseline changes at equal effect, and a physically availability-preserving common aggregate+.08 effect. The latter uses precomputed MH-weighted available fractions; its probabilities were frozen at support time. The two positives plant+.12 only in C1 with either abstract Bernoulli outcomes or availability-preserving outcomes. The abstract controls do not reproduce every token dependency; this is qualification for authored controls on actual geometry, not universal calibration.

The working-variance half-count is a fixed Jeffreys construction, not an outcome-tuned numerical floor. Raw observations/effects are unchanged. Studentized permutation tests need care under equal-parameter but nonidentical-distribution nulls; this candidate is not asserted to inherit finite-sample exactness. [Chung and Romano’s primary research](https://statistics.stanford.edu/technical-reports/exact-and-asymptotically-robust-permutation-tests) motivates that distinction. [Astropy’s documentation](https://docs.astropy.org/en/stable/api/astropy.stats.binom_conf_interval.html) describes the Beta(1/2,1/2) construction; [NumPy](https://numpy.org/doc/2.0/reference/random/generated/numpy.random.Generator.permuted.html) documents independent row permutations, and [NIST](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm) documents exact binomial bounds.

All prior non-cache files were hash-preserved. Engineering includes a complete small permutation orbit, independent scalar scoring, deterministic all-zero/all-one/perfect-prefix fixtures and finite replacement scores on all six prior zero-variance synthetic assignments. POSTRUN-AUDIT.json records independent scalar probes for every fresh null false flag and trial0 per scenario. All outcomes/banks are reproducible from recorded coordinates and hashes. No reserved zodiac material or raw EVT was opened; no meanings, grammar or mechanisms are claimed.
