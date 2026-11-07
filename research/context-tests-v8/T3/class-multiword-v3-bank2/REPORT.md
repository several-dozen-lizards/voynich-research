RETROSPECTIVE IN TEXT; T1/T2 PROSPECTIVE IN IMAGE VARIABLE ONLY; T3 INTERNAL SPLIT.

Class-based T3 passes LIMITED CONTROL QUALIFICATION on the fresh isolated-worker bank: all 1,200 trials are valid, with zero full passes; all four reused Latin positive cells pass; independent audit and final verification both pass. BANK-PROTOCOL.json and TRIAL-PLAN.json froze the bank before generation. No new manuscript discovery or H/F confirmation score is part of this qualification-only run.

The method is an exact byte copy of T3-class-multiword-v3-attempt1: fixed52 spelling classes from the existing13 opener categories crossed with4 ending families. An anchor class, a variable gap of1–3 classes and a second anchor class must lie wholly within original word positions2–15. Unknown slots remain barriers, and paragraph-first words are excluded. Discovery thresholds are >=8folios, >=50%paragraph presence, concentration>=2, top16 class variants covering>=80%, and at least2 variants each on>=2folios. Ranking, lexical ties and the class codebook are unchanged.

Confirmation transfers the exact frame and variants. It requires>=8folios, >=50%presence, concentration>=1.5, >=70%frozen coverage, <=4new variants, and2recurrent frozen variants. NO CANDIDATE is terminal; a candidate failing predictions is a full failure with no permutation p-value. A structurally passing candidate receives exactly10,000 first-word-fixed withinparagraph shuffles including unknown slots. The literal joint-pass fraction and add-one sensitivity are retained. Holm2 operates over the two scribe inventories separately within G2 and G3 for Latin and over paired synthetic scribe panels for the mechanism family check.

The fresh bank changes only the registered seed block, synthetic folio ID prefix and execution model. Seeds use872600000 + family offset(G5:0/G6:1000000) + geometry offset(Latin:0/scribe1:10000/scribe2:20000) + trial0..199. Synthetic IDs start CMW3B2 and are salted deterministically to the old hash-parity arm before native words are generated. There are200 trials in each of six mechanism/geometry cells,1,200 total. Seeds are disjoint from the earlier exact-word and failed class-based banks. No result is pooled across banks, no seed is replaced and no failed trial is retried.

Every trial starts in its own isolated Python process, serially, to bound memory use from the outset. G5 runs the pinned published native Java curveline implementation with its existing -Xmx64m setting, the initial seed line excluded and fixed native line budget ceil(originalslots/4)+2. Unused tail output is retained; shortage fails without wrapping or padding. G6 uses the same native v5 default table/grille generator. Original geometry and masks are unchanged: Latin17/19 folios, scribe1 54/43, scribe2 12/8. Manuscript-sized profiles derive only from previously cached H discovery, never real confirmation text/layout. The wrapper/controller do not alter native source parameters or scoring.

The prior bank remains NOT QUALIFIED, with1,190 valid trials and10 retained invalid trials(9MemoryError cases plus1interrupted case), four failed synthetic candidates, its exact receipts and its post-process seal. It is not repaired or replaced by this new bank. PRESERVATION.json verifies19,798 earlier files: the failed class bank's10,067 sealed files plus its two delivery receipts and9,729 older files, including the exact-word negative and source/diagnostic failures. New files live only in this bank's directory and new routing pointers.

The unchanged Latin pipeline was rerun end to end with the original mapped inputs,17/19hash split, selection rules, gold and permutation seeds. It reproduces all four passes. Frames and class variants are frozen before Latin confirmation processing. This reuses one exposed36-entry Circa instans A block from the Paris1582 print, with old G2/G3-EVA maps unchanged and no refitting; four transformations and repeated computation do not create independent source replication or a power estimate.

| Latin cell | Discovery presence | Confirmation presence | Frozen coverage in confirmation | Gold precision discovery / confirmation | Joint shuffled passes |
|---|---:|---:|---:|---:|---:|
| G2-s1 | 14/17 | 13/19 | 13/14 | 14/14;13/14 | 0/10,000 |
| G2-s2 | 14/17 | 13/19 | 11/14 | 14/16;13/14 | 0/10,000 |
| G3-s1 | 14/17 | 13/19 | 13/14 | 14/14;13/14 | 0/10,000 |
| G3-s2 | 14/17 | 14/19 | 13/16 | 14/16;13/16 | 0/10,000 |

All four meet the frozen>=80%gold requirement that a known quality/degree value occurs inside the gap in both arms. Broad class frames also match some nongold positions. The same one-word degree slot has three or four frozen class variants; this is a known-source control association, not a meaning assigned to manuscript classes. Literal Monte Carlo p=0 records zero observed joint passes, not zero true probability; add-one sensitivity is1/10001, Holm2 sensitivity2/10001.

The unchanged mechanism qualification gate requires no invalid trials in any cell, each cell's two-sided95%Wilson upper full-pass proportion<=5%, and both paired either-scribe Holm2 families meeting the same upper-bound gate. Bounds are per cell/family, not simultaneous confidence statements. Any invalid cell blocks overall qualification even if all valid outputs fail the full pipeline. An inactive internal Holm slot has bookkeeping value1 and is not a measured p-value.



| Fresh bank2 cell | Valid trials | Discovery candidates | Full passes | Invalid | Wilson95% upper | Frozen gate |
|---|---:|---:|---:|---:|---:|---|
| G5 Latin | 200 | 0 | 0 | 0 | 1.8845% | PASS |
| G5 scribe1 | 200 | 0 | 0 | 0 | 1.8845% | PASS |
| G5 scribe2 | 200 | 1 | 0 | 0 | 1.8845% | PASS |
| G6 Latin | 200 | 2 | 0 | 0 | 1.8845% | PASS |
| G6 scribe1 | 200 | 0 | 0 | 0 | 1.8845% | PASS |
| G6 scribe2 | 200 | 0 | 0 | 0 | 1.8845% | PASS |

Both paired either-scribe Holm2 mechanism families have0/200 flags, no invalid cases and the same1.8845%upper bound. The bank is complete with 1200 isolated workers, no retries and no generation failures. Of 1200 valid datasets, 1197 terminate at NO CANDIDATE; three selected frames fail their frozen confirmation predictions. Those failures retain exact candidate freezes and metrics, with no permutation p-value or synthetic permutation bank:

| Synthetic case, relative to bank2 | Confirmation presence | Concentration | Frozen coverage | New types | Recurrent frozen types |
|---|---:|---:|---:|---:|---:|
| G5-scribe2-146 | 5/22 | 0.7846 | 3/5 | 1 | 0 |
| G6-Latin-092 | 2/19 | 0.4651 | 1/2 | 1 | 0 |
| G6-Latin-093 | 5/19 | 1.4414 | 5/6 | 1 | 1 |

The repeated numerical trial index093 denotes a fresh seed873600093 and fresh bank2 IDs, not a retry of failed-bank seed863600093. Every bank2 seed is disjoint from both previous banks. Failed-bank observations remain separate and are never included in these200-trial denominators.

Independent implementation checks use the unchanged separate Python classifier and frame-selection/metric code, with exact source-gold and 400 seeded raw/class shuffle-hash checks. Native controls are independently reconstructed from all G5 prefixes and regenerated from all G6 seeds, with table/draw/mask comparisons. These are same-agent separate-code checks, not outside adjudication. Final verification replays the40,000Latin shuffles, checks every control input and candidate freeze, verifies fixed seeds/arms, and recomputes gates and preservation. Engineering checks are the same22authored tests; no test fixture changes the scientific rule.

Qualification is limited to the exposed Latin block and frozen default G5/G6 mechanisms/geometries. It does not establish independent herbal replication, manuscript-sized positive power, parameter-grid coverage, frequency-matched discrimination, a natural-language interpretation or a numeral/degree reading. A pass on this new bank would leave the failed earlier bank unchanged. No global alpha_V is allocated or spent. H/F manuscript confirmation remains CLOSED throughout this run, including after any limited qualification pass.

The completed separate-code audit verifies all 1,200 native cases:600 G5 prefixes and600 G6 full seed replays, with exact generated slots, unknown masks, tables/draws, class selections and confirmation metrics. All 1,200 cases are valid. The Latin source-gold audit and 400 seeded raw/class shuffle references reproduce exactly. The previous failed bank and all prior receipts remain unchanged.

Final verification passes 32,391 checks, including 40,000 Latin shuffle replays and 19,798 unchanged earlier files. QUALIFICATION.json records the limited pass and CUSTODY.json keeps manuscript H/F confirmation CLOSED. The prior failed bank remains failed; no outcomes are pooled and no old receipt is overwritten. DELIVERY-HASHES.json seals the completed artifact set, with a separate full rehash after the sealing process exits. New routing is ../CLASS-MULTIWORD-BANK2-LATEST.json; the old failed-bank pointer is retained unchanged.
