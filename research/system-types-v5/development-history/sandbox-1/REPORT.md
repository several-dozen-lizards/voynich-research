SANDBOX ONLY — NO MODEL ELIMINATION OR SURVIVAL RESULT. CLAIM RUN INCOMPLETE.

# Voynich system types v5: development report

Recorded 24 October 2026, America/New_York. The original request is preserved byte-for-byte in `SPEC-v5.md`. This is a development cut, not the final simulate-and-compare experiment.

## What exists and was verified

The EVT and Davis metadata match their expected source hashes. Reserved Virgo/Libra/Scorpio/Sagittarius folios (`f72v1`, `f72v2`, `f73r`, `f73v`) are excluded before tokenization. Original unknown slots remain barriers. H/F alternate readings and Currier A/B stay in separate cells. `DATA-MANIFEST.json` hashes the exclusion policy and all retained rows.

`core.py` implements the five S_fit blocks and whole-page bootstrap scaling. `S-FIT-TARGETS.json` contains those basic targets only, not H1–H8 outcomes. Zero-variance bootstrap dimensions cannot be rescued with a small denominator: a mismatch gives infinite distance.

`GENERATORS/` contains reproducible runnable mechanisms for all six families. These are development fixtures: G2/G3 use unsourced illustrative rules, G5 is a copy-modify surrogate, G6 is a coupled three-column grille prototype. G1/G4 mechanics run but still lack a full source and mapping specification. No fixture is a historically qualified family implementation. Six 800-word fixtures, raw source-unit marks and G5 genealogy are saved under `SANDBOX-SAMPLES/`.

The published Timm–Schinner source is pinned at commit `a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`; all **40** downloaded source/license/documentation files match their manifest hashes. They have not been executed or silently replaced by the surrogate. The published code has page/position source selection, several mutation operations, follow constraints and suggestion logic. Source: [Timm–Schinner repository](https://github.com/TorstenTimm/SelfCitationTextgenerator).

`abc_smc.py` implements bounded uniform-prior ABC-SMC with proper importance weights, recorded seeds, distances and ESS. A planted scalar location and an independent density calculation verify the sampler mechanics. That is not the six-family recovery gate. No manuscript fitting was performed. Required particle count remains at least 2,000 per qualified family/cell.

`abc_rf.py` implements classification plus OOB allocation-error regression for a selected-model probability approximation. It explicitly distinguishes forest votes from posterior probabilities and does not invent probabilities for all other models. Source: [Pudlo et al., Reliable ABC model choice via random forests](https://arxiv.org/abs/1406.6288).

**13 engineering tests passed.** Tests cover tokenizer/barriers, exclusion before tokenization, source-hash mismatch, all generators' reproducibility, separate abbreviation units, verbose expansion, causal/windowed parent receipts, mapping injection/abstention, hand-calculated fit statistics, zero bootstrap variance, freeze absence/incompleteness/tampering, ABC weights/recovery and RF behavior. The initial development test-file indentation failure was repaired before this successful run; no scientific result was produced by the failed invocation.

`held.py` refuses H1–H8 scoring without a valid complete `FREEZE.json` and matching source-owner hashes; its actual statistic dispatch is still unimplemented. No FREEZE has been created. Neither generator nor manuscript H1–H8 values were computed in this cut.

## Population retained

| Currier | Scribe | Reading | Pages | Lines | Known words | Unknown slots |
|---|---|---|---:|---:|---:|---:|
| A | 1 | F | 112 | 1453 | 10023 | 114 |
| A | 1 | H | 112 | 1456 | 10301 | 51 |
| B | 2 | F | 44 | 1097 | 9541 | 55 |
| B | 2 | H | 45 | 1140 | 10018 | 13 |
| B | 3 | F | 29 | 1116 | 10826 | 86 |
| B | 3 | H | 31 | 1160 | 11321 | 10 |
| B | 4 | F | 8 | 43 | 343 | 8 |
| B | 4 | H | 8 | 43 | 353 | 0 |
| B | 5 | F | 6 | 62 | 558 | 10 |
| B | 5 | H | 6 | 62 | 579 | 1 |

P-locus and metadata eligibility are explicit draft choices. Other formats and missing/ambiguous Currier/scribe assignments are excluded and counted in the data manifest. No missing cell is interpreted as a failed mechanism.

## User decision and recovered history

Re selected **log odds ratio; recompute targets** for H1/H2. The historical 1.16–1.32 availability-strengthening interval is from a risk-difference estimand and is not reused as a log-OR target.

At Re's request, earlier Voynich conversations, attachments and saved experiment owners were searched. The original p/r matched-remainder layout result was recovered: 12/12 eligible line-start forms used p, versus9/45 elsewhere; that is not the share of all line-start words containing p. The exact `ending_lm v2` method was not recovered. The saved v65 template method concerns line-first words and explicitly does not establish the paragraph-first H8 method or its quoted15.5%/3.4% targets. `HISTORY-SEARCH.json` records scope and limits; this is not a claim that the missing work never existed.

## Mapping preflight

The strict single-character rank-map draft produced **40/40 capacity abstentions** across four source-unit fixtures × ten manuscript panels. This shows the draft mapping cannot represent those source inventories within the selected position classes. It does not eliminate G1–G4, establish a fit failure, or demonstrate anything about the manuscript mechanism. The spec permits EVA groups, but their inventory, segmentation, class rules, reuse/overflow and unseen-unit behavior must be made explicit. No many-to-one fallback was inserted.

## Work remaining before a claim freeze

- **H3 — NEEDS_ORIGINAL_METHOD:** ending_lm v2 exact estimator, noise correction, ending inventory and ±48-sign construction not recovered in earlier chats or local artifacts. No replacement estimator has been substituted.

- **MAPPING — IMPLEMENTATION_DESIGN_REQUIRED:** Single-EVA-character, 95%-class, injective rank-map draft abstains in every G1–G4 × panel fixture. Need a declared glyph/group inventory, position-class rule, overflow and unseen-unit policy before freezing. This is not inability to mimic basics.

- **SOURCES — INCOMPLETE:** Latin/German Bible sources located; not medical/diplomatic. Italian/Czech/Occitan sources and source license/provenance manifests missing. No real heavily abbreviated Latin control yet.

- **G2_G3 — ENGINEERING_FIXTURES_ONLY:** Illustrative suspension/contraction and symbol rules run; historical diplomatic/Cappelli rule inventories and probabilities not qualified.

- **G5 — PUBLISHED_SOURCE_PINNED_NOT_INTEGRATED:** 40 published source/license/docs files pinned and hash-verified. Java/java compiler/Maven not found on PATH. Python copy-modify fixture is explicitly a surrogate and cannot eliminate Timm–Schinner.

- **G6 — PROTOTYPE_ONLY:** Three-column tables with explicit coupled grille offsets run. Published mechanism fidelity, table priors and movement law still need qualification.

- **H1_H2_H5 — NEW_SCALE_APPROVED_DEFINITIONS_PENDING:** User selected MH log OR and recomputed targets. Old 1.16–1.32 is RD strengthening, not an OR target. Freeze zero-cell/no-support policy, opener/context selection, availability and section heterogeneity estimator before recomputation.

- **H4 — OVERLAPS_S_FIT:** H4 is a function of glyph position shares already fitted. Keep as a declared diagnostic; do not call it independent held-out evidence.

- **H6 — DEFINITION_TO_FREEZE:** Normalized edit-distance convention, page boundaries, eligible candidate windows, equal-size random baselines, pair restriction and vector-to-one-failure rule need explicit definitions. Zero-support cases must be missing, not zero.

- **H7_H8 — LEGACY_METHOD_MISMATCH:** Original p/r result recovered: matched remainders, 12/12 versus9/45, not generic p frequency. v65 is line-first template surprise and explicitly excludes paragraph-start inference. Exact method underlying paragraph15.5% vs3.4% not recovered.

- **RECOVERY — NOT_RUN:** Correct-family survival alone does not establish discrimination. G2/G3/G4 contain G1-like boundaries; G3 contains G2 at p=0. Preserve expected non-identifiability rather than require arbitrary wrong-family elimination. Freeze number of pseudo-manuscripts, parameter-recovery tolerance and off-diagonal gate.

- **CLAIM_EXECUTION — NOT_READY:** No qualified full generators, frozen prior ranges/tolerance schedule, simulation budget, PPC multicomponent rule or recovery matrix yet. No manuscript ABC/PPC/RF or elimination was run.

These gaps are not inferential failures. The code and evidence are reviewable, but this experiment has not reached the requested claim tier. `PROTOCOL.json`, `MAPPING.json` and `PRIORS-DRAFT.json` are explicitly drafts. The following requested result artifacts are absent because their computations have not run: `FREEZE.json`, `ABC-POSTERIORS/`, `PPC.csv`, `ELIMINATION.json`, `RECOVERY-CONFUSION.json`, `ABC-RF.json`.

The finite family/parameter/source choices define what could be excluded. Even a qualified exclusion would concern that implementation and prior support, not every conceivable natural-language, abbreviation, cipher or copying mechanism. A survivor would remain compatible with the measured features, not a decipherment.

## Reproduce this sandbox cut

From the project folder:

```powershell
python system-types-v5/sandbox.py --bootstrap 100
python system-types-v5/prepare.py
```

No live services, other research branches or reserved-folio content were modified. `VERIFICATION.json` records the environment, engineering checks and code hashes; `DELIVERY-HASHES.json` inventories this development cut without calling it a claim freeze.
