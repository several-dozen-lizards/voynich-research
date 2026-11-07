# C16-KH scoring diagnosis and qualification

**NOT_QUALIFIED — ZL and actual C11 remain CLOSED.** New ZL scores: 0. No failed-run file was overwritten; no human rating or translation claim.

The failed implementation used hapax mass where the published base solver adds one singleton UNKNOWN training sentence. It gave each unseen string the aggregate unknown mass, failed to canonicalize unknown histories, lost higher-order probability mass in missing contexts, and averaged EOS as another ranking slot. The defective word score also affected fitted keys. A ranking-only repair would therefore be insufficient. Source: [Hauer et al. 2014, section 3](https://aclanthology.org/C14-1218/).

The frozen correction uses one observed UNKNOWN event, canonical OOV contexts/predictions, normalized fallback distributions and a word-slot ranking denominator excluding EOS. Candidate lists, beam/search limits, normalization and all 24 variants remain unchanged. No penalties or filters were selected after qualification outcomes. [PROTOCOL.md](PROTOCOL.md) and [REGISTRATION.json](REGISTRATION.json) preserve the rules and hashes.

| Arm | G1 mathematics | G2 held-out/oracle | G3 order/invariance | G4 actual-null maxima | G5 fitted cipher |
|---|---|---|---|---|---|
| tanakh | FAIL | FAIL | FAIL | FAIL | FAIL |
| medieval | FAIL | PASS | FAIL | FAIL | FAIL |

## tanakh

Probability normalization maximum error: 0.18; UNKNOWN count: 1; exhaustive Viterbi and traversal conservation: True/True.

Held-out oracle decoding: 87.69% of in-vocabulary tokens and 78.80% of all tokens recovered. Original beats quarter-UNKNOWN on 313/320 lines; all-UNKNOWN on 320/320. All-UNKNOWN envelope selections: 0; all-UNKNOWN document wins: 0.

Natural-order maxima beat independently maximized word shuffles: 24.5/40; within-word shuffle invariance: True. Neither character-shuffle equality nor unknown agreement is evidence of semantics.

| Null | Version | Positive exceed /40 | Null exceed /n | Null 95% Wilson interval | AUC |
|---|---|---:|---:|---|---:|
| C1 | clean | 0 | 0/20 | 0.0%–16.1% | 0.998 |
| C9 | clean | 0 | 0/20 | 0.0%–16.1% | 1.000 |
| C17 (short C17) | clean | 0 | 0/19 | 0.0%–16.8% | 0.983 |
| C1 | noise | 0 | 0/20 | 0.0%–16.1% | 0.998 |
| C9 | noise | 0 | 0/20 | 0.0%–16.1% | 1.000 |
| C17 (short C17) | noise | 0 | 0/19 | 0.0%–16.8% | 0.986 |

Blind search on 6 known-key ciphertexts: median alphagram recovery 38.92%, minimum 19.75%. Individual recoveries: 43.82%, 34.02%, 92.17%, 19.75%, 31.73%, 52.21%. True-key-vs-100-wrong-key counts: 100, 100, 100, 100, 100, 100. Search limits were not increased after failures.

## medieval

Probability normalization maximum error: 0.2; UNKNOWN count: 1; exhaustive Viterbi and traversal conservation: True/True.

Held-out oracle decoding: 91.18% of in-vocabulary tokens and 86.28% of all tokens recovered. Original beats quarter-UNKNOWN on 319/320 lines; all-UNKNOWN on 320/320. All-UNKNOWN envelope selections: 0; all-UNKNOWN document wins: 0.

Natural-order maxima beat independently maximized word shuffles: 31.0/40; within-word shuffle invariance: True. Neither character-shuffle equality nor unknown agreement is evidence of semantics.

| Null | Version | Positive exceed /40 | Null exceed /n | Null 95% Wilson interval | AUC |
|---|---|---:|---:|---|---:|
| C1 | clean | 1 | 0/20 | 0.0%–16.1% | 1.000 |
| C9 | clean | 1 | 0/20 | 0.0%–16.1% | 1.000 |
| C17 (short C17) | clean | 1 | 0/19 | 0.0%–16.8% | 0.963 |
| C1 | noise | 1 | 0/20 | 0.0%–16.1% | 1.000 |
| C9 | noise | 1 | 0/20 | 0.0%–16.1% | 1.000 |
| C17 (short C17) | noise | 1 | 0/19 | 0.0%–16.8% | 0.968 |

Blind search on 6 known-key ciphertexts: median alphagram recovery 63.46%, minimum 47.85%. Individual recoveries: 47.85%, 87.13%, 66.45%, 64.67%, 51.85%, 62.25%. True-key-vs-100-wrong-key counts: 100, 100, 100, 100, 100, 100. Search limits were not increased after failures.

## Preservation and limits

G0 preservation: True. Archived 2042 original files; archive SHA256 `dcec42499860cf234e75050a8b6d172f8d8f158a0178f7f94b6142cab452a8e0`. Original sealed key was not opened. No new ZL or actual C11 data entered this scorer. Actual C11 is held because its alphagrams preserve Voynich content; Hebrew-only C11-style controls test the required equality without circumventing the hold.

Each arm has 40 calibration and 40 confirmation Hebrew documents of 8 distinct held-out lines. Exact training-segment duplicates and exact test duplicates were excluded. Prior v1 aggregate exposure, same-work overlap, corpus editions and ordinary phrase overlap remain limitations. Nulls retain 20 calibration/20 confirmation C1/C9 pages and 19/19 C17 writers, without padding; noise uses clean fitted keys. These small finite banks cannot establish a population false-positive bound of 5%. Their confidence intervals and maximum-over-variant results remain visible. The confirmation bank is now exposed and must not be reused as fresh evidence after tuning.

Scorer mechanics, held-out discrimination and cipher search are separate gates. A mathematical repair alone does not authorize a manuscript rerun. All failed cells remain failures, without pooling or replacement. Stop. Preserve failed gates. A new candidate requires separate registration and disjoint confirmation data.

Artifacts: DIAGNOSIS.json; QUALIFICATION.json; results/<arm>/RESULT.json; complete variant-source.csv, Hebrew-maxima.csv and null-maxima.csv; individual known-cipher gold/fitted keys and recovery receipts; preservation/FAILED_RUN_MANIFEST.json and failed-c16-kh.zip. Reproduction: register.py is write-once; run qualify.py once for each arm, then finalize.py. Do not overwrite exposed banks.

## Independent post-run audit

The remaining normalization failure is confined to histories ending in EOS: context denominators count terminal pairs with no outgoing trigrams. Valid sentence scoring terminates at EOS and does not traverse those histories. Rebuilding that denominator from actual trigram-prefix counts would leave all valid sentence scores and deleted-interpolation weights unchanged; this is an analytic witness, not an activated or qualified revision. The registered G1 remains FAIL. This terminal-boundary failure is separate from the failed discrimination and search gates.

The original G3 `sign_tail` calculation treated half-ties as a binomial count. That is not an exact sign test when ties exist. The audit omits ties for the exact one-sided sign test below; the pre-registered win-count gate and every qualification decision remain unchanged.

| Arm | Wins / losses / ties | Exact sign tail | Reachable-context probability sums |
|---|---|---:|---|
| tanakh | 24 / 15 / 1 | 0.0997954 | PASS |
| medieval | 31 / 9 / 0 | 0.000339774 | PASS |

The null-threshold gate also exposes small-bank upper-tail instability. With 19 C17 calibration writers, a nearest-rank 95th percentile is the largest writer score. The frozen pooled upper-tail threshold can reject nearly all positives even when pairwise AUC is high. It was not lowered after seeing this failure. Driver-family receipts are in INDEPENDENT_AUDIT.json.

All 12 cipher-recovery receipts were independently recomputed using letter-count vectors and unchanged fitted keys. The published-rule mismatch, repaired unknown-collapse symptom, terminal-count defect, weak maximum-over-variant order discrimination, threshold sensitivity and limited key search are distinct findings. No manuscript was scored, no original run file changed, and no semantic conclusion follows.
