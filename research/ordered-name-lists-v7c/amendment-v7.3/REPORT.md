# v7.3 implementation and R2 opener check

The user-authored amendment is frozen and hashed before new scoring. The new label reading is R2=K (Karl Kluge) for Part C and Part B. A separate pharma choice, R2_PHARMA=V (John Grove), is frozen for new v6 T1/T2 runs. Paragraph tests retain H/F.

R2=K reproduces ok as the maximum-ratio opener under the unchanged C2 rule. C-MRK remains conditional; C-SUF is dropped with no replacement. C-FULL and C-STEM continue unchanged. The C pool now has three eligible arms. No C3 alignment, published-key score, v6 T1/T2 score or vault test was run.

## Amendment and preservation

AMENDMENT.md is a Markdown-normalized copy of the user’s v7.3 instruction. AMENDMENT-FREEZE.json seals it before coverage selection or the new C2 look. Its SHA256 is 62af33d874378ae0dcf51f82100c487bbff470a9b5b935c58746ac93f0a8af01.

The original C2 delivery files and five-look ledger, all original source-set files, v7.2 qualification, published-key intake files, BUDGET.json and the declaration receipts remain unchanged. The new reading check supplements the historical H/F result; it does not rewrite that result from NOT ESTIMABLE to a pass. Verification checks all 34 earlier C2 sealed files and all 100 C1 sealed files, as well as the preserved intake and administrative files.

## Outcome-blind reading choice

COVERAGE-PLAN.json and PROVENANCE-POLICY.json were frozen before counting. The counting stage emits only record identifiers, codes, stratum membership and a readability boolean. No spelling, opener, ending, dictionary hit or alignment score enters the selection.

The archive has no precomputed per-record readability field. A syntax-only byte pass therefore derives a one-bit validity flag from the existing C2 uncertainty/boundary rule, without decoding or emitting the EVA letter strings. This distinction is explicit: headers alone cannot establish readability. The selector reads the emitted flags, not payloads. A letter-identity-invariance check confirms that changing the lowercase letter identities leaves each validity decision unchanged.

Counts use the existing open zodiac ring units and astronomical/pharma comparator definitions; the five extra-top Gemini labels are not counted as a ring. Reserved signs are rejected before flagging, and no reserved readability flags are computed. The pharma-specific choice uses existing v6 source-only INCLUDE units in the Recipes section, not object ratings or T1/T2 outcomes. These slightly differ from the C2 comparator units.

| Code | Readable open ring records | Readable C2 pharma records | Readable v6 pharma records |
|---|---:|---:|---:|
| H | 170 | 219 | 216 |
| K | 110 | 87 | 84 |
| U | 58 | 134 | 134 |
| C | 41 | 26 | 26 |
| X | 28 | 0 | 0 |
| V | 14 | 206 | 204 |
| L | 0 | 74 | 71 |
| F | 0 | 1 | 1 |

The full table, including low-coverage and excluded second-choice codes, is in COVERAGE-COUNTS.json. The choice ranks readable records, not header totals: V has 173 open ring headers, but only 14 pass the frozen syntactic readability rule. No normalization was changed to increase its coverage. Raw-readable pharma counts are not the final physical-label sample sizes; unresolved multiline grouping is subsequently excluded by the unchanged C2 adapter.

K wins the zodiac-first ranking with 110/170 = 64.7% of H’s ring coverage, exceeding the 50% gate. V wins the separately frozen v6 pharma ranking with 204/216 = 94.4% of H’s readable pharma records. Both choices were frozen in R2-CHOICE-FREEZE.json before any new selected-reading payload decoding.

The source credits Kluge’s Petersen-copy work, dated 1992 in the archive introduction, separately from Takahashi’s 1998 transcription. V is separately credited to Grove, with unit comments describing his contributions and postings. No inspected source documents either selected code as derived from H. Full editorial independence is not established: shared archive conversion, label reordering and corrections remain limitations. Other archive codes unfolded from alternatives (D/G/I/Q/M) are not treated as distinct transcribers. Historical alternate-reading inventories already exist, so this is not a claim that these readings have never previously been viewed.

## C2 look 6: opener only

The original five C2 looks are untouched. The new plan schedules one opener table only, charged as look 6 against the same cap of ten. No ending-family or suffix search was run, and four looks remain unused. COMBINED-C2-LOOK-LOG.json preserves the original five entries verbatim and adds the checkpointed sixth.

The original functions for token parsing, glyph grouping, feature extraction, pair counts, baseline probabilities, exact ratios and candidate selection are unchanged by AST comparison. Only the reading-role wrapper is parameterized to accept R2; the underlying source code K remains recorded on every admitted row. H’s earlier result is reused unchanged, not rescored.

| Quantity | H, preserved result | R2=K, look 6 |
|---|---:|---:|
| Admitted ring labels | 170 | 110 |
| Labels beginning ok | 41 (24.1%) | 30 (27.3%) |
| Within-ring ok pairs | 176/1,774 (9.92%) | 134/1,102 (12.16%) |
| Different-ring ok pairs, same zodiac section | 1,464/26,956 (5.43%) | 736/10,888 (6.76%) |
| Available nonzodiac-label ok pairs | 3,192/137,270 (2.33%) | 90/6,972 (1.29%) |
| Frozen constancy ratio | 4.27 | 9.42 |
| Maximum eligible opener | ok | ok |

The fixed literal removal operation matches in H and R2: prefix ok, conditional on the opener classifier equalling ok. Nothing is stripped in this pre-test. No sound value, language, angelic morpheme or source-name pairing is inferred.

K’s admitted data comprise 110 ring labels, five extra-top labels outside the pair statistic, and 84 pharma comparator labels. Its ring coverage is Pisces 28, Aries 15+14, Taurus 14+15, Gemini 24; Cancer and Leo have no K label rows. K has no astronomical or rosette comparator labels. Its available comparison pool is therefore pharma-only, while H uses 371 available astronomical/pharma labels. This coverage imbalance, source-defined band registration and unverified exact figure ownership remain limits on the descriptive replication. They must carry into C3 design and qualification; no missing stratum is imputed.

## Arm disposition and allocation

ARM-DISPOSITION-FREEZE.json records:

- C-SUF: dropped by v7.3; kal and its two-label sparse result remain preserved. No replacement suffix is selected.
- C-MRK: retained conditionally because K also selects ok under the frozen rule. A complete C3 freeze, qualifying controls and all vault locks still apply.
- C-FULL and C-STEM: continue unchanged.

The total vault family envelope remains 0.005. B keeps 0.0025. The unchanged C pool of 0.0025 is divided across FULL, STEM and MRK: 0.0008333333333333334 per arm (1/1200). This is an explicit v7.3 within-C redistribution, not a refund to the global budget, a change to BUDGET.json or permission to execute. The later loss of an arm at qualification must not rescue the remaining arms by changing this frozen divisor.

Carry-forward descriptive note: H does not support the strong theophoric form requiring a near-constant marker on every name. The ok opener covers about a quarter of H ring labels, and the selected kal suffix was sparse. FULL and STEM do not assume such a marker. The C-MRK distribution check is not a semantic result.

## Published-key and v6 policies

PUBLISHED-TIER-POLICY.json defines RETROSPECTIVE-PUBLISHED for future mechanically complete, image-verified keys. SOURCE.md must freeze every cited example/derivation locus; admissible evaluation text excludes those loci and sealed material. Both unchanged v7.2 banks, all gates, source-first controls and complexity requirements remain. FAIL applies to that faithfully implemented fixed key as published. PASS/PARTIAL can motivate a prospective follow-up only and never become a claim. Prior NOT_TESTABLE intake records are preserved; incomplete or unverified mappings still cannot be scored. No published key was reevaluated here.

V6-LABEL-READING-POLICY.json freezes H/V for new v6 pharma T1/T2 work, with the original geometry, rating, support, controls and score gates retained. V must not be replaced after seeing poor T2 herbal-pair coverage. Existing H/F results stay historical. Versioned policy pointers were added to the v6 directory and the published-key intake directory; legacy sealed runners and results were not edited. Future runs must explicitly consume these overlays and prepare/qualify the required adapters; no new v6 score or V payload decode occurred in this continuation.

## Verification and vault

VERIFICATION.json passes 271 checks: coverage recounts and rankings, lexical-invariance validity checks, exact-function preservation, independent direct pair enumeration, candidate selection, allocation arithmetic and all preservation receipts. A completed-run check returned the existing look 6 result without changing the result, row, or combined-look hashes.

Only the chosen K payloads in allowed open/comparator units were decoded after the choice freeze. All 327 reserved-record headers in the monolithic EVT were rejected before payload decoding. Reserved signs were not displayed, aligned or scored. The vault remains closed, with no execution authorization or test count change.
