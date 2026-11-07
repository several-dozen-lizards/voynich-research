P1-H: PASS — +5.895 pts [+0.557, +11.554]; Holm p 0.04126709892078925
P1-F: PASS — +6.414 pts [+1.513, +11.285]; Holm p 0.04126709892078925
P2-H: NOT ESTIMABLE — +10.346 pts [+4.733, +17.827]; Holm p not computed
P2-F: NOT ESTIMABLE — +4.298 pts [-0.506, +15.126]; Holm p not computed

Attempt C was frozen before support and all outcome computations. H/F remain separate alternate readings, not independent samples. This is a single-target RETEST on previously searched botanical material, not untouched confirmation. Effects and folio-bootstrap intervals are descriptive when support or qualification fails.

## Primary support and qualification

| Cell | sh / ch | V | Supported pages | Largest page share | H1 null gate | +15 pt power gate |
|---|---:|---:|---:|---:|---|---|
| P1-H | 279 / 488 | 139.291 | 26 | 10.60% | True | True |
| P1-F | 258 / 460 | 133.041 | 24 | 11.12% | True | True |
| P2-H | 90 / 193 | 49.529 | 9 | 37.85% | True | False |
| P2-F | 60 / 146 | 33.322 | 7 | 55.00% | False | False |

Primary two-reading confirmation: PASS. A support failure is not evidence against the dependency; failed null qualification blocks inference. Underpowered cells cannot exclude smaller effects.

## Leakage-free H2

The target is next-qok. P includes prefix main effects; J adds only origin-end/previous-end features and their prefix interactions. No follower or future token appears in either feature map. This is a newly defined prediction question, not unchanged replication of attempt B’s prefix-prediction gain.

- P1-H: NO PASS; gain 0.003482519056045072 bits; Holm p 1.0; qualification PASS_LIMITED_SCOPE.
- P1-F: QUALIFICATION FAILED; gain unavailable bits; Holm p None; qualification FAIL_NULL_QUALIFICATION.
- P2-H: NOT ESTIMABLE; gain unavailable bits; Holm p None; qualification NOT_RUN_SUPPORT_FAILED.
- P2-F: NOT ESTIMABLE; gain unavailable bits; Holm p None; qualification NOT_RUN_SUPPORT_FAILED.

## Descriptive discovery panels

No P0 hypothesis test or p-value was computed. Bath hand2 and starred hand3 are kept separate.

- P0-2-H (Balneological): +9.800 points; 95% folio-bootstrap CI [4.978662029510392, 15.460116500419696]; n=1322.
- P0-2-F (Balneological): +8.734 points; 95% folio-bootstrap CI [4.1714189115415925, 13.972766578720293]; n=1313.
- P0-3-H (Starred paragraphs): +10.469 points; 95% folio-bootstrap CI [6.674855054130543, 14.443598033334938]; n=2158.
- P0-3-F (Starred paragraphs): +9.853 points; 95% folio-bootstrap CI [6.380114557379392, 13.426888919001854]; n=2167.

## Full freshness audit

Membership comes from historical source rules and metadata. Prior numerical outcome tables were not opened. “Previously not passed” is inherited from the supplied spec, not newly verified. v49/v50 tested word-part section contrasts, not sh→qok adjacency. v75/v77 used the forced sh/qok comparison in their search. v94/context-transfer/nuisance were discovery-only; v98/v99 used discovery layouts for qualification/diagnostics without new original-arrangement inferential scoring. Preflight incidental historical-index exposure is recorded in PROTOCOL.json.

| Panel | Folio | Section | v49/v50 included | v75/v77 sh→qok searched | v94/v98/v99/A/B/repair included |
|---|---|---|---|---|---|
| P1 | f26r | Botanical | True | True | False |
| P1 | f26v | Botanical | True | True | False |
| P1 | f31r | Botanical | True | True | False |
| P1 | f31v | Botanical | True | True | False |
| P1 | f33r | Botanical | True | True | False |
| P1 | f33v | Botanical | True | True | False |
| P1 | f34r | Botanical | True | True | False |
| P1 | f34v | Botanical | True | True | False |
| P1 | f39r | Botanical | True | True | False |
| P1 | f39v | Botanical | True | True | False |
| P1 | f40r | Botanical | True | True | False |
| P1 | f40v | Botanical | True | True | False |
| P1 | f43r | Botanical | True | True | False |
| P1 | f43v | Botanical | True | True | False |
| P1 | f46r | Botanical | True | True | False |
| P1 | f46v | Botanical | True | True | False |
| P1 | f50r | Botanical | True | True | False |
| P1 | f50v | Botanical | True | True | False |
| P1 | f55r | Botanical | True | True | False |
| P1 | f55v | Botanical | True | True | False |
| P1 | f85r1 | Rose obverse | True | False | False |
| P1 | f85r2 | Rose obverse | False | False | False |
| P1 | f86v3 | Rose obverse | True | False | False |
| P1 | f86v4 | Rose obverse | True | False | False |
| P1 | f86v5 | Rose obverse | True | False | False |
| P1 | f86v6 | Rose obverse | True | False | False |
| P2 | f58r | Botanical | True | True | False |
| P2 | f58v | Botanical | False | False | False |
| P2 | f65r | Botanical | False | False | False |
| P2 | f65v | Botanical | False | False | False |
| P2 | f73r | Astronomy/Astrology | False | False | False |
| P2 | f73v | Astronomy/Astrology | False | False | False |
| P2 | f94r | Botanical | True | True | False |
| P2 | f94v | Botanical | True | True | False |
| P2 | f95r1 | Botanical | True | True | False |
| P2 | f95r2 | Botanical | True | True | False |
| P2 | f95v1 | Botanical | True | True | False |
| P2 | f95v2 | Botanical | True | True | False |

PANELS.json retains every declared folio, coverage, per-reading line counts, per-run membership and freshness label. Missing P-unit folios are preserved, not replaced.

## Controls, sensitivity and limits

QUALIFICATION.json gives every cell/scenario Wilson interval; SYNTHETIC-TRIALS.jsonl retains every trial with replay seed and outcome hash. H1 null rejection can reflect position/line or spelling confounding under the proposed exchangeability assumption. Such failures are preserved; no design was tuned to the results. H2 junction-only is a recovery diagnostic, not a null. H2 power uses a strong interaction and does not certify detection of a 15-point H1 effect.

SENSITIVITY.json applies the unchanged repaired predictor to its original sh/ch target, with its original support and adequacy gates. Transport to the new event population is explicitly exploratory and cannot rescue primary inference.

The new tokenizer follows literal comma-separator/comment-drop rules, with engineering fixtures; it intentionally differs from the older comma-masking atlas. All known paragraph loci in each reading are used, without forced shared-locus or Currier-B restriction. No signs were reserved/opened for zodiac scoring, no meanings were assigned, and no discovery-panel inferential test was run. Bootstrap CIs are descriptive and do not repair confounding or historical selection.

VERIFICATION.json independently reparses raw EVT, checks every event/exclusion/count/effect and frozen hashes; engineering oracles verify the exact test on enumerated assignments.

## Detailed control results

All rejection flags use the conservative first Holm threshold .05/4. Wilson gates use all attempted trials, including abstentions. A null gate qualifies the finite end-to-end procedure here; it does not show calibration conditional on receiving a nondegenerate score.

| Test | Cell | Scenario | Role | Flags / attempts | Wilson 95% | No p computed | Gate |
|---|---|---|---|---:|---|---:|---|
| H1 | P1-H | null_low | null | 3/200 | [0.00511, 0.04317] | 0 | True |
| H1 | P1-H | null_high | null | 2/200 | [0.00275, 0.03572] | 0 | True |
| H1 | P1-H | additive | null | 0/200 | [0.00000, 0.01885] | 0 | True |
| H1 | P1-H | junction_only | null | 2/200 | [0.00275, 0.03572] | 0 | True |
| H1 | P1-H | positive | power | 188/200 | [0.89807, 0.96535] | 0 | True |
| H1 | P1-F | null_low | null | 3/200 | [0.00511, 0.04317] | 0 | True |
| H1 | P1-F | null_high | null | 3/200 | [0.00511, 0.04317] | 0 | True |
| H1 | P1-F | additive | null | 0/200 | [0.00000, 0.01885] | 0 | True |
| H1 | P1-F | junction_only | null | 1/200 | [0.00088, 0.02777] | 0 | True |
| H1 | P1-F | positive | power | 184/200 | [0.87401, 0.95016] | 0 | True |
| H1 | P2-H | null_low | null | 1/200 | [0.00088, 0.02777] | 0 | True |
| H1 | P2-H | null_high | null | 0/200 | [0.00000, 0.01885] | 0 | True |
| H1 | P2-H | additive | null | 0/200 | [0.00000, 0.01885] | 0 | True |
| H1 | P2-H | junction_only | null | 1/200 | [0.00088, 0.02777] | 0 | True |
| H1 | P2-H | positive | power | 109/200 | [0.47579, 0.61252] | 0 | False |
| H1 | P2-F | null_low | null | 2/200 | [0.00275, 0.03572] | 0 | True |
| H1 | P2-F | null_high | null | 0/200 | [0.00000, 0.01885] | 0 | True |
| H1 | P2-F | additive | null | 0/200 | [0.00000, 0.01885] | 0 | True |
| H1 | P2-F | junction_only | null | 4/200 | [0.00780, 0.05029] | 0 | False |
| H1 | P2-F | positive | power | 71/200 | [0.29199, 0.42348] | 0 | False |
| H2 | P1-H | null_low | null | 0/100 | [0.00000, 0.03699] | 85 | True |
| H2 | P1-H | null_high | null | 0/100 | [0.00000, 0.03699] | 87 | True |
| H2 | P1-H | additive | null | 0/100 | [0.00000, 0.03699] | 85 | True |
| H2 | P1-H | junction_only | recovery_diagnostic | 0/100 | [0.00000, 0.03699] | 50 | diagnostic only |
| H2 | P1-H | positive | power | 100/100 | [0.96301, 1.00000] | 0 | True |
| H2 | P1-F | null_low | null | 0/100 | [0.00000, 0.03699] | 87 | True |
| H2 | P1-F | null_high | null | 0/100 | [0.00000, 0.03699] | 79 | True |
| H2 | P1-F | additive | null | 1/100 | [0.00177, 0.05449] | 75 | False |
| H2 | P1-F | junction_only | recovery_diagnostic | 0/100 | [0.00000, 0.03699] | 50 | diagnostic only |
| H2 | P1-F | positive | power | 100/100 | [0.96301, 1.00000] | 0 | True |

H2 P1-F failed the additive null: 1/100 flags, Wilson upper 0.054486 > 0.05. Its positive control passed, but that cannot rescue failed null qualification. H1 P2-F additionally failed junction-only qualification (4/200; upper 0.050287), and both P2 readings had inadequate +15-point power. These failures remain recorded even though the earlier support gate already blocks both P2 manuscript tests.

## Event exclusions

| Cell | Unknown origin slots | Origin at line end | Following unknown |
|---|---:|---:|---:|
| P1-H | 10 | 72 | 2 |
| P1-F | 21 | 57 | 3 |
| P2-H | 1 | 24 | 0 |
| P2-F | 9 | 18 | 1 |

Absent exclusion keys in SUPPORT.json mean zero, not missing measurement.

## Interpretation and execution receipts

H1 passes the frozen two-reading primary rule: H +5.895 points [0.557, 11.554], F +6.414 [1.513, 11.285]; exact raw p 0.01360434 / 0.01031677; Holm-over-four adjusted p 0.04126710 in each reading. The two readings are not independent replications. The result concerns the specified mixture of non-bathing hand-2 pages; no post-outcome botanical-only or unsearched-subset test was added.

P1 has 20 previously searched folios and six outside the listed sh→qok searches. P2 has seven previously searched folios and five outside those searches. P2 f65r/f73r/f73v have no P-unit coverage and remain in the declared lists. Neither combined panel is called untouched. No first-ever non-circular confirmation is claimed.

H2 H has gain +0.00348252 bits/event (equal-folio average), raw sign-flip p 0.28462219 and Holm p 1.0: NO PASS. H2 F was not inferentially scored. H2 groups exact physical-page Folio identifiers, including separate recto/verso pages; it does not hold out an entire numbered leaf jointly as the old context-transfer extractor did. This limits the comparison with attempt B and may retain dependence between related pages. No grammar-versus-junction conclusion follows.

The unchanged transported weak-score sensitivity produced no passing score in either P1 reading (raw p H 0.622867, F 0.685036; original factor-four p 1 in each). It tests the original far-context interaction with a sh/ch target, not H1’s adjacency effect or H2’s qok target, and cannot rescue either test.

The original worker disappeared after 4,576 durably saved trials. RESUME.json records the event and file hash; only the remaining 424 predeclared jobs were run. All 5,000 trial keys and seeds are unique. No code, seed, quota or acceptance threshold changed.

Independent verification passed: all 9,823 event/exclusion ledger rows; all primary/descriptive effects; primary bootstrap intervals; H2 fold separation and saved losses; exact H1 p-values recomputed using integer assignment counts; all 5,000 synthetic outcome hashes replayed; all 30 Wilson control gates recomputed; and all frozen hashes and phase order checked. See VERIFICATION.json, EXACT-INTEGER-AUDIT.json and QUALIFICATION-AUDIT.json.
