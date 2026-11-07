# C12 partial decomposition sweep

Completed 94 nominal clean/noise cells across 47 settings, with 84 unique prepared inputs. **0 nominal cells (0 unique inputs) lie inside all three frozen descriptive bands.** These are not formal equivalence tests or evidence of a reading.

## Design and checks

Both requested arms ran: sigla-only and nested deterministic 25/50/75% sign-type subsets, across lengths 2/3/4 and rigidity 0/.5/1. Full C12, paired zero and standalone C5 references are included. All paired arms use the same C12-internal C5 base. Standalone C5 uses its original different RNG and remains a separate reference. Selected types form a disjoint stroke alphabet from retained atomic types, making mixed-width codes prefix-free. Every clean word reverses exactly to its base.

A pre-metric full-endpoint check caught a missing stroke-alphabet shuffle in the extension. Failed attempt1 is preserved; no metric/neural result used it. The corrected data reproduce all18 full-C12 clean/noise endpoints and both standalone-C5 endpoints. All slot-cardinality, prefix, word-count and expansion-accounting checks passed before metrics and training.

All original neural measuring code/config/splits were copied and hash-checked. Two exact baseline/position replays admitted old endpoint jobs. The full five-seed T1 LSTM grid uses 96 steps with validation-only checkpoint selection. Fixed-budget/continuing-learning limitations remain. Identical tensor inputs are explicitly reused; duplicates such as length 2, rigidity 0/.5 are not independent repetitions. A result-table duplicate-field error was repaired without changing metrics or parameters; the original registration and implementation are preserved in EXECUTION_LOG.md and the table-fix receipts.

| Job accounting | Count |
|---|---:|
| TRAINED | 660 |
| REUSED_IDENTICAL | 80 |
| REUSED_PRIOR | 200 |
| Cache-admission training replays, additional | 2 |

## Results

| Mode | Version | Nominal cells | h2 within | Length within | Gain within | All three |
|---|---|---:|---:|---:|---:|---:|
| paired_zero | clean | 1 | 0 | 0 | 1 | 0 |
| paired_zero | noise | 1 | 0 | 0 | 1 | 0 |
| C5_external | clean | 1 | 0 | 0 | 1 | 0 |
| C5_external | noise | 1 | 0 | 0 | 1 | 0 |
| sigla_only | clean | 9 | 0 | 0 | 9 | 0 |
| sigla_only | noise | 9 | 0 | 0 | 9 | 0 |
| subset25 | clean | 9 | 0 | 0 | 5 | 0 |
| subset25 | noise | 9 | 0 | 0 | 9 | 0 |
| subset50 | clean | 9 | 0 | 0 | 8 | 0 |
| subset50 | noise | 9 | 1 | 0 | 8 | 0 |
| subset75 | clean | 9 | 0 | 0 | 6 | 0 |
| subset75 | noise | 9 | 0 | 0 | 8 | 0 |
| full | clean | 9 | 0 | 0 | 9 | 0 |
| full | noise | 9 | 0 | 0 | 9 | 0 |

![Partial decomposition grid](partial_sweep.png)

Type fractions are not occurrence fractions. Exact selected counts, occurrence fractions, source/expanded character sizes, actual noise sizes, all h0/h1/h2 metrics, W1 distances, five seed gains and per-cell bands are in sweep_results.csv and position_gains_by_seed.csv. This negative result concerns the fixed codebook family/grid, not partial decomposition generally.

**Word length is the universal mismatch:** 0/94 cells fall within its frozen band. The closest is clean sigla-only expansion, length 2, rigidity 0 (identical at .5): W1 **0.693819**, versus the cached ZL/H band **0.083187**. Only one cell falls within the h2 band; passing position gain alone does not establish a joint match.

### Cells within all three descriptive bands

None.

## Limits and preservation

Bands reuse only cached ZL/H measurements and histograms. No new ZL, H or actual C11 scoring/training occurred; C16-KH holds remain unchanged. h2 and length bands are empirical transcription sensitivity, and gain bands widen by the larger primary/control seed SD; none is a formal equivalence margin. One fixed encoder seed was used, and five neural seeds measure only model variation. Generated controls share C1 ancestry and borrowed layout. Partial codebooks are synthetic and do not identify a historical abbreviation system. No interpolation, parameter rescue, model selection on test, alpha spending or semantic/translation claim.

Original lab source/config/report/C5/C12 byte snapshot unchanged: True. Concurrent/shared drift if any: []. Registered extension drift: [].

Key artifacts: PROTOCOL.md, REGISTRATION.json, ENGINEERING.json, REPLAY_VERIFICATION.json, JOB_PLAN.json, DATA_MANIFEST.csv, DATA_IDENTITIES.csv, model_free.csv, model_runs.csv, sweep_results.csv, position_gains_by_seed.csv and full encoder/noise receipts. Code and data from the failed preflight are retained separately.
