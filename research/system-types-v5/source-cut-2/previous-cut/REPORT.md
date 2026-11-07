TRANSFER ABSTENTIONS DIAGNOSED; UNKNOWN-UNIT/SOURCE-LENGTH POLICIES SETTLED — H3 UNRESOLVED, CLAIM SCORING LOCKED.

# Voynich v5: frozen transfer and finite-source policy

This cut diagnoses the existing reserves and enforces development-only generation. **It fits no mapping, normalizer, inventory extension, abbreviation rate or model parameter to a reserve.** It does not run H1–H8, manuscript inference or full recovery.

## What caused the abstentions

The ten target EVA inventories have sufficient capacity. The source-side development codebooks lack a few literal units:

| Source | Full reserve slots | Newly unmappable slots | Unseen units |
|---|---:|---:|---|
| Latin | 1,884 | 0 | none |
| Italian | 7,380 | 5 | x, ä |
| German | 24,511 | 0 | none |
| Czech | 5,051 | 4 | w |
| Occitan | 25,149 | 17 | ç |
| Real_Latin_14c | 1,732 | 13 | DIGIT:U+0030, DIGIT:U+0031, DIGIT:U+0032, DIGIT:U+0033, DIGIT:U+0034, DIGIT:U+0036, DIGIT:U+0037, DIGIT:U+0038, MARK:U+0301 |

Italian's five affected words are `mäi`, `mäometto` twice, `portäi`, and `vexilla`. Czech's four contain literal `w`; Gascon's17 contain `ç`. These written forms are retained; no spelling substitution or foreign-word removal is applied. Real Latin has twelve numeric-token slots containing previously unseen digits and one token with U+0301. Labels identify literal transcription codepoints, not inferred meanings. Raw source-unit/line/slot provenance is saved in `UNSEEN-UNIT-DIAGNOSIS.json`.

This extends the earlier first1,000-word sample to complete reserves. It finds additional Italian and Czech gaps. Source gaps repeat identically across ten target inventories: they are not ten independent discoveries. Latin and German have no newly unseen units in their complete reserves. Across60 source/cell views,20 fully transfer and40 remain not estimable for full transfer.

Every transfer codebook exactly reproduces its previously frozen **development-only** baseline. Altering diagnostic reserve content changes coverage but not codebooks. Reserve frequencies were counted for the requested diagnosis; they did not choose mappings, mergers, expansions, rates or acceptance thresholds.

## Unknown-unit policy, now enforced

`UNKNOWN-AND-LENGTH-POLICY.json` fixes the contract:

- Development alone fits inventories, position classes and maps. Calibration/reserve inputs are rejected by the fitting API.
- A newly unmappable word becomes one `None` barrier **in its original slot**, with raw units/provenance retained. Known fragments are not substituted for the word; later words are not repacked or promoted to line start. No adjacency is created across a barrier.
- Original transcription unknowns remain the pre-existing missingness mask. They are distinct from new transfer loss; the qualified scope is registered observable text, not reconstructed missing letters.
- Any newly unmappable originally readable word leaves **full-transfer qualification not estimable**. Supported-slot diagnostics have their own explicit masks and do not certify full-source G2 survival. Conditional held scoring would require its own later frozen estimand and support gate.
- No accent stripping, digit completion, mark merger, silent expansion, reserve reranking or reserve-based alphabet extension is admitted. Any future inventory extension needs independently selected development evidence, a new cut and newly reserved evaluation material.

`transfer_policy.py` implements immutable codebooks and barrier views; `BARRIER-PRESERVING-RESERVE-VIEWS.json` retains every original slot. Sparse source coverage is not a rejected production mechanism.

## Source-length policy, now enforced

Primary fitting/generation uses **development material only**. A corpus must contain one consecutive within-work run long enough for the target's **original slot count, including unknown positions**. Counts pooled across works, missing sections or partitions cannot satisfy that requirement. Eligible start positions are sampled uniformly without inspecting reserve or generated outcomes.

The source-backed entrypoint is **`source_contract.produce_from_development`**. It loads hash-registered development source units into an immutable corpus, samples an admissible same-work window, and delegates to the existing generator registry. Source-start fitting and reserve/calibration generation inputs are rejected. The registry also rejects insufficient budgets and source-wrap overrides before invoking a generator. G1–G4 now use bounded source slices; legacy wrapping remains only in explicitly historical standalone sandbox fixtures, outside the primary entrypoint.

No cyclic reuse, padding, unrelated-work stitching, post-shortage partition pooling or family-specific size reduction is allowed. Naturally repeated words remain present. Independent Monte Carlo draws may reuse the fixed corpus, but do not count as independent corpora. G5's native copying and G6's table reuse are their generative mechanisms and are not external-source padding.

Seven of50 development-language/reading-cell combinations are unsupported:

| Development source | Largest consecutive run | Unsupported cells |
|---|---:|---|
| Latin/Macer |9,709 slots|A-1-F10,137; A-1-H10,352; B-2-H10,031; B-3-F10,912; B-3-H11,331|
| Old Gascon |10,624 slots|B-3-F10,912; B-3-H11,331|

The Gascon development aggregate was14,863 words, but it spans three works; those counts cannot be stitched into one manuscript. Across all150 partition/cell combinations,49 lack the required consecutive run. Complete candidate comparisons at unsupported sizes remain unqualified. A smaller common-size experiment must be separately specified/frozen, not used to rescue a failed cell.

## Verification

- **42/42 engineering tests pass**, including rejection before generator invocation, immutable codebooks, reserve perturbation invariance, gap/work boundaries, original-slot budgets, source-file drift, and retained native missingness.
- Actual-geometry source-entrypoint checks: **58 supported generations and22 correct pre-generator size rejections**,80 cases total. The22 rejections include multiple Latin-dependent families sharing the seven source/cell shortages; these are not22 mechanism eliminations.
- The full mechanism/mapping schedule was replayed using **development Macer chapters only, without wrapping**:200 mechanism trials,1,600 successful group maps, and five published-G5 repeat pairs. No reserve supplied those new mapping fits.
- Current source and transfer plan hashes are unchanged. No claim `FREEZE.json` exists; held and full-recovery locks remain closed.

`RECOVERY-PROTOCOL.json` now incorporates the policy hash, safe source entrypoint and unsupported-size treatment. Its full experiment remains defined but unrun.

## Exposure and preserved history

Earlier whole-reserve representation maps are **diagnostic-only**, not frozen transfer proof. Earlier Macer last40% mechanism controls overlap what later became calibration/reserve partitions; those historical mapping fits are quarantined and never initialize the current development-only transfer. `RESERVE-EXPOSURE-LEDGER.json` preserves this history. We do not call those sources historically untouched.

The previous policies, diagnostics and generator owners remain under `development-history/transfer-policy-start/`, `transfer-policy-v1/` and `group-qualification-3/`. The policy clarification separating pre-existing unknowns from newly lost readable words changed none of the current source-gap outcomes. Earlier source extraction, partition and mapping failures are still retained.

Current artifacts: `UNKNOWN-AND-LENGTH-POLICY.json`, `UNSEEN-UNIT-DIAGNOSIS.json`, `CONTIGUOUS-SOURCE-SUPPORT.json`, `TRANSFER-DIAGNOSTIC-RESULTS.json`, `SOURCE-ENTRYPOINT-VERIFICATION.json`, `STATUS.json`, `VERIFICATION.json`. Prior source/provenance report: `development-history/transfer-policy-start/REPORT.md`.

**H3 remains unresolved.** No replacement estimator, reduced-H3 run, reserve-trained repair or held-out scientific score has been introduced.
