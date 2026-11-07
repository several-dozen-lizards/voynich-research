# Later month annotation target: frozen-rule result

The maximum is **5/12 exact item matches (41.7%)**, using the Occitan candidate list and positional substitution. Each of the five frozen 99-shuffle banks gives **p = .01** for the full language/family/table maximum. This is a result for the later Latin-script annotations only; it does not identify the annotator's language or interpret native-script text.

The target manifest was sealed before target optimization at 2026-10-27T14:45:19.045008+00:00. Its SHA256 is `d36fd9c0c345656d2679d8507bf147d03a8888edc4cf48b42d80170a165dc8c8`. Original rules, period names, normalization, annotation alternatives, codebooks, and shuffle assignments were unchanged. The observed target was fitted once with all 32 frozen models; each shuffle was refitted with the same full search.

## All language by family scores

Scores count whole exact matched items out of 12. Naibbe is the maximum over the six frozen published tables.

| Candidate language | Monoalphabetic | Naibbe verbose | Positional substitution |
|---|---:|---:|---:|
| Latin | 0/12 | 0/12 | 1/12 |
| Italian | 2/12 | 0/12 | 2/12 |
| German | 1/12 | 0/12 | 1/12 |
| Occitan | 4/12 | 0/12 | 5/12 |

Every Naibbe submodel is retained below (exact item counts):

| Candidate language | alpha | beta1 | beta2 | beta3 | gamma1 | gamma2 |
|---|---:|---:|---:|---:|---:|---:|
| Latin | 0 | 0 | 0 | 0 | 0 | 0 |
| Italian | 0 | 0 | 0 | 0 | 0 | 0 |
| German | 0 | 0 | 0 | 0 | 0 | 0 |
| Occitan | 0 | 0 | 0 | 0 | 0 | 0 |

## Max-statistic shuffle null

For every shuffled assignment, the statistic is the maximum over all four languages and all three families, including all six Naibbe tables. Labels are shuffled among the twelve zodiac panels within section. Each bank uses its original 99 frozen assignments. The p-value is `(1 + count(null >= observed)) / 100`.

| Frozen seed | Draws | Null range | Mean | Null >= 5 | p | Histogram (score: count) |
|---|---:|---|---:|---:|---:|---|
| 9011 | 99 | 0–3 | 1.4343 | 0 | 0.01 | 0: 2, 1: 59, 2: 31, 3: 7 |
| 9013 | 99 | 0–4 | 1.3232 | 0 | 0.01 | 0: 1, 1: 69, 2: 26, 3: 2, 4: 1 |
| 9019 | 99 | 0–4 | 1.4949 | 0 | 0.01 | 0: 2, 1: 59, 2: 27, 3: 9, 4: 2 |
| 9029 | 99 | 0–3 | 1.3737 | 0 | 0.01 | 0: 4, 1: 57, 2: 35, 3: 3 |
| 9041 | 99 | 0–4 | 1.4848 | 0 | 0.01 | 0: 4, 1: 55, 2: 30, 3: 8, 4: 2 |

All five banks are reported separately, without selecting a seed, pooling p-values, or adding a decision gate. They measure Monte Carlo variation on the same target and are not independent manuscript replications. The value .01 is the resolution floor of each 99-shuffle test.

## Saved optimal witness

The selected model uses separate injective beginning/interior/end maps, each consistent across all items. Its five matched items are March (`Mars` -> `mars`, f70v2), May (`Mai` -> `may`, f71v and f72r1), June (`Junh` -> `jong`, f72r2), and August (`Agost` -> `augst`, f72v3), with the frozen automatic normalization applied. The two May panels count twice under the registered item statistic; these are five panel matches spanning four distinct months. The twelve-panel target spans ten distinct month identities.

The Occitan positional model is the only language/family/table submodel attaining five; this does not establish a unique optimal character mapping. The full saved mapping is in OBSERVED.json and RESULT.json. This fit demonstrates compatibility with the frozen exact-match rule, not a historical cipher reconstruction.

## Scope, provenance, and preserved failures

Annotation readings and panel assignments come from the frozen source table at [Voynich.nu, Writing](https://www.voynich.nu/writing.html). Parenthesized source letters are included or omitted automatically by the frozen rule; no manual spelling corrections or newly restored letters were added. Candidate spellings and their period citations remain in the original PERIOD_NAMES.json and SOURCES.md. Historical forms span different witnesses, dates, and regions; French is outside the registered candidate set. Length, repeated-character constraints, spelling choices, abbreviation alternatives, and the duplicated panels all affect this exact-match statistic. Zero scores do not exclude a language or all verbose cipher systems. The six tested Naibbe tables are a fixed published subfamily and are not blind to Voynich statistics.

The saved-witness audit checked 15,872 model witnesses and 495 null records, with no new fitting. It verified the mappings/segmentation witnesses, score arithmetic, full maxima, shuffle assignments, p-values, and preservation hashes. All 1,353 pre-existing calibration files and 1,837 earlier preserved files remain byte-identical.

**Native tracks remain CLOSED. Phase 8 remains FAIL.** The original calibration registration still fails its strict full-manifest check solely because mutable RUN_STATE.json was included in it and later changed during calibration. That receipt defect and its documented initial-state reconstruction remain preserved; the target audit does not relabel the original strict receipt as PASS. The original calibration RUN_STATE.json is unchanged by this target run; TARGET_RUN_STATE.json records the separate authorized target completion.

Machine-readable evidence: TARGET_MANIFEST.json in the parent calibration directory; local RESULT.json, OBSERVED.json, LANGUAGE_FAMILY_SCORES.json, NULLS_s*.jsonl.gz, AUDIT.json, OUTPUT_HASHES.json, and COMPLETION_RECEIPT.json. No translation claims are made. Work stops here.
