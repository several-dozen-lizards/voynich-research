# RD-v1 Phase 0

| Gate | Result |
|---|---|
| ZL_circular_direction | PASS |
| ZL_circular_shuffle_null | PASS |
| ZL_radial_direction | FAIL |
| ZL_radial_shuffle_null | PASS |
| Latin_circular_direction | PASS |
| Latin_circular_shuffle_null | PASS |
| Latin_radial_direction | FAIL |
| Latin_radial_shuffle_null | PASS |

| Corpus | Geometry | Length | n | Distinct windows | Source clusters | Accuracy | Cluster 95% CI | Ties | Powered |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| ZL | circular | 1–2 | 200 | 200 | 42 | 0.000 | 0.000–0.000 | 200 | False |
| ZL | circular | 3–5 | 200 | 200 | 43 | 0.205 | 0.145–0.280 | 140 | False |
| ZL | circular | 6–10 | 200 | 200 | 37 | 0.480 | 0.423–0.535 | 67 | False |
| ZL | circular | 11–20 | 200 | 200 | 35 | 0.505 | 0.431–0.568 | 44 | False |
| ZL | circular | 21–40 | 200 | 200 | 30 | 0.720 | 0.638–0.796 | 13 | False |
| ZL | circular | 41–80 | 200 | 200 | 19 | 0.830 | 0.726–0.896 | 4 | True |
| ZL | radial | 1–2 | 200 | 200 | 40 | 0.030 | 0.009–0.057 | 190 | False |
| ZL | radial | 3–5 | 200 | 200 | 40 | 0.160 | 0.118–0.205 | 148 | False |
| ZL | radial | 6–10 | 200 | 200 | 37 | 0.340 | 0.239–0.439 | 93 | False |
| Latin | circular | 1–2 | 200 | 27 | 27 | 0.000 | 0.000–0.000 | 200 | False |
| Latin | circular | 3–5 | 200 | 54 | 27 | 0.455 | 0.295–0.621 | 82 | False |
| Latin | circular | 6–10 | 200 | 108 | 27 | 0.795 | 0.675–0.899 | 25 | False |
| Latin | circular | 11–20 | 200 | 124 | 27 | 0.940 | 0.847–1.000 | 12 | True |
| Latin | circular | 21–40 | 200 | 196 | 27 | 1.000 | 1.000–1.000 | 0 | True |
| Latin | circular | 41–80 | 200 | 142 | 27 | 1.000 | 1.000–1.000 | 0 | True |
| Latin | radial | 1–2 | 200 | 54 | 27 | 0.080 | 0.020–0.159 | 180 | False |
| Latin | radial | 3–5 | 200 | 81 | 27 | 0.335 | 0.175–0.510 | 121 | False |
| Latin | radial | 6–10 | 200 | 81 | 27 | 0.690 | 0.527–0.834 | 44 | False |

| Corpus | Geometry | Shuffled non-ties | Null accuracy | Cluster 95% CI | Accepted |
|---|---|---:|---:|---|---|
| ZL | circular | 681 | 0.49045521292217326 | 0.4612794612794613–0.5184590690208668 | True |
| ZL | radial | 150 | 0.49333333333333335 | 0.391304347826087–0.5819672131147541 | True |
| Latin | circular | 855 | 0.4982456140350877 | 0.46882217090069284–0.5282167042889391 | True |
| Latin | radial | 246 | 0.5609756097560976 | 0.5–0.62 | True |

**STOP_FAILED_GATE**. Stop stage: direction.

Only passing supported bins qualify; L_min is not permission for calls at every longer length. Nonpassing bins remain underpowered. Overlapping/repeated windows are not independent trials: intervals resample source-folio families (Latin: contiguous source-span blocks). These are marginal intervals, not simultaneous confidence bands.

A calibration failure concerns this instrument and available source support. It does not determine whether manuscript rings are forward, reversed, line-like or have a unique start. No real ring text was scored; no later phase or corrected-order export ran.

Protocol and input/instrument hashes: `extensions/ringdir_v1/registration_v1/REGISTRATION.json`. Key sealing and score-before-key receipts: `events.jsonl`. All failures and untouched later-stage stimuli are retained; no retuning or retry.

The complete matching/fallback and exclusion ledgers accompany this report. Latin source blocks are not historical sections; source layout is artificial. Positions are transcription locus proxies, and fixed EVA units do not prove glyph identities. Re visual annotation remains pending.
