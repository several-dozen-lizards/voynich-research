# JX: testing the word-junction direction effect — corrected draft R1

Date: 2026-11-06. **Status: review draft prepared for freezing; NOT REGISTERED; NOTHING RUN.** This replaces ambiguities in the supplied JX draft for review, not in any RD registration. The source draft remains unchanged in `../sources/`. Re's approval of the candidate list and a hash-bound executable manifest must precede the first JX calibration result. The separate character-mapping PDF supplies no assumptions, mappings, rules or evidence to JX.

## Purpose and limits

RD-v2 and RD-FO3 provide prior, result-motivated evidence: on known-order pseudo-circles from held-out ZL paragraphs, junction features recovered word-order reversals more effectively than whole-word bigrams. This is a difference in feature performance, not absence of word-order structure, a demonstrated phonological mechanism, or an identified language. Old passes are not new JX passes. Source windows are held out within the fixed RD partition, not historically unseen by the lab.

JX asks whether that performance advantage is specific to particular word positions, robust to available readings and ambiguous spacing, and supported across annotated strata. Later measurements ask what neighbor-conditioned unit statistics and spacing-reference profiles remain. **Statistical unit conditioning is not, by itself, sandhi; a distributional spacing score does not identify plaintext word boundaries.** Sandhi and non-plaintext spacing remain hypotheses, not the names of the output classes.

Predictions retained for prospective freezing: K1 specificity passes; K2 passes every supported, documented independent alternate and both spacing variants; I1 shows regressive conditioning; I2 is closer to the real-space references under its calibrated comparison. These are predictions, not admission requirements for interpreting a negative outcome. No translation, letter values, word meanings or resident instruments are involved.

## Stages and stop rules

1. Approve/freeze the candidate list and symbolic priors before any JX result. Their detailed language-specific predictions remain NP unless separately source-bound before results; see the corrected register.
2. Register protocol, exact inputs, executable generators/scorers, environment, sample counts and seed namespaces **before Phase 0 generation, fitting or scoring**. “Phase 0 must pass before anything runs” is removed: Phase 0 runs after registration; target K tests run only after their calibration gates pass.
3. Phase 0 uses synthetic known-mechanism controls and empirical reference corpora. Source support and null calibration are gates, not opportunities to retune. Failures stop only the dependent analysis chain and are fully reported.
4. Paragraph-target K1/K2 open only for calibrated chains. K1 or K2 FAIL or UNSUPPORTED keeps the dependent I-phase closed. K1 failure means *specificity not demonstrated by this test*; K2 failure means *robustness not demonstrated*. Neither proves absence of structure or a transcription artifact.
5. K3 defines where subsequent claims may apply. No aggregate pass is inherited by an unsupported stratum. I1 and I2 need their own Phase 0 qualification in addition to K1/K2; one failed interpretation instrument cannot be replaced with the other.
6. **Real-ring scoring stays CLOSED throughout JX**, including metadata/image agreement. Radial text remains HELD. A later RD Phase 1 needs separate authorization and a registered prospective annotation procedure.

This review authorizes none of these stages. Draft hashes/checksums are provenance, not registration or permission to execute.

## Inputs, units and eligibility

- Primary is the existing source-hash-verified ZL ordinary paragraph data and RD family split. Keep folio sides/panels in one family; group fRos/f85/f86 as before; all ring-containing families stay excluded as in RD. Retain P0/P1/Pc/Pr/Pt, and preserve explicit paragraph/line markers. Use the existing drawing-interruption, missing-span, uncertainty and spurious-locus exclusions for the strict clean baseline. Never remove an unknown word and bridge its neighbors.
- Training and held-out source families stay separate for all fitted scores, category maps and source selection. Use paired evaluation windows for every feature comparison. RD-v2's trained coefficients or gate outcomes do not stand in for a fresh JX fit and gate.
- Units are exactly `ch sh cth ckh cph cfh ii iii in iin aiin qo ee`, longest match then single codepoints. They are transcription units, not established glyphs or sounds. Record raw codepoint and clustered-unit sensitivity; any added parser is a new registered variant, not a silent repair.
- Source intake lists **all** transcriber IDs, coverage, selection rules and documented ancestry before feature scoring. The local LSI introduction identifies H=Takahashi, U=Stolfi, V=Grove; it explicitly marks D/G/I/Q/M as unfolded alternate choices. Those branches are not independent readers. The archive also includes edited/combined historical readings, so IDs alone do not prove independence. H/U/V are mandatory inventory entries, not a declaration that they are three independent full-corpus replications.
- Build an ancestry/coverage ledger with `independent_reading_documented`, `derived`, or `unresolved`. Independent here means separately produced readings, not independent manuscripts or image sources. Unknown ancestry cannot satisfy an independent-reading gate. Do not silently omit a supported adverse reading. Partial readings without enough families are UNSUPPORTED, not failed phonological systems.
- Keep Currier **language varieties A/B**, historical Currier hand labels, and Davis scribe numbers distinct. Do not import ZL scribe identities into LSI without a separately frozen alignment. Missing labels stay missing.

### Ambiguous spacing

The clean primary baseline preserves RD's declared dot/comma split. Register two paired sensitivity parses of the **same raw, source-selected ZL loci**: split commas and join commas. Dot boundaries remain; drawing breaks and unknown/missing spans remain barriers. Removing a comma joins its two literal neighboring segments only; apply the frozen first-alternative rule before parsing; never join across a locus, missing span or illustration. Mark the resulting source-offset mapping.

Both variants must use exactly the same candidate source-locus panel selected without inspecting feature scores. Their word counts may differ. Evaluate matched source spans and additionally their own declared length-bin panels; report both so a changed length distribution cannot masquerade as a spacing effect. Lines excluded from the strict baseline solely because their raw ambiguity is being studied belong to a separately labeled spacing-sensitivity arm with all other eligibility rules fixed; do not claim they were in the clean baseline. If the paired panel lacks power, mark UNSUPPORTED rather than substituting a favorable panel. The split variant overlapping the baseline is not a new independent replication.

## Phase 0: controls and empirical references

Every pure synthetic control has a frozen generator, planted-relationship labels, seed family, source split and matched training/heldout token budget. Preserve every generated stream and transformation. Each control's role is narrower than a claim about all natural language.

| ID | Construction / role | What is actually known |
|---|---|---|
| C-lat | Existing C1 normalized Latin, losslessly inverse-relabelled; real editorial spaces | A natural-language reference. **No guarantee of zero cross-word dependence or a particular feature ranking.** Artificial RD layout is not authentic scribal lineation. |
| C-junc | Random lexical interiors and ordering, with a frozen planted final-to-next-initial unit relationship | The added mechanism is at that junction. Whole-word identities contain these units too; “whole-word information absent” is not a known answer. Test a finite-budget advantage, not exclusivity. |
| C-order | Frozen lexical-state order grammar with terminal units randomized independently of grammar state | An added word-order mechanism, no added junction rule. Emergent feature correlations must still be measured. |
| C-SS / C-EE | Matched position-only planted rules, respectively first→first and last→last | Specificity negative controls: the instrument must not always label J as the winning position pair. |
| C-zero | Factor-independent matched unit/word generator, plus exchangeability-preserving sham datasets | Operating false-positive rate for the *actual tested statistic*. These replace an assumed zero effect in Latin. |
| C-sandhi | C-lat plus a fully enumerated synthetic final-rewrite rule at probability .8, and a paired unchanged/sham copy | A specific added regressive rewrite, **not an authenticated historical Latin sandhi system**. Freeze input/output unit maps, order, eligible contexts, RNG, collision handling and change labels before generation. |
| C-prog | Matched synthetic progressive initial-rewrite control, with sham | Tests whether the I1 instrument can detect the other registered direction. A regressive-only positive cannot qualify progressive interpretation. |
| C-respace | The same Latin source character stream with original spaces removed and frozen Naibbe-style respacing applied | Imposed boundaries are known to differ from source editorial spaces; coincidences must be measured, not assumed absent. Preserve original and imposed boundary maps. |
| C-naibbe | Pinned author source, glyph table and fixed settings | A generated-cipher reference with known respacing procedure; “no measurable sandhi-like statistics” is **not** known. |

`C-shuf` from the original draft is moved out of source-only Phase 0. It is a **target-derived word-order randomization reference**, opened only after source/synthetic qualification. Shuffling without replacement within source lines preserves vocabulary, line composition and some dependence constraints; it does not guarantee all sequential statistics are zero. Do not open held-out Voynich words to rescue a failed source calibration.

Apply the same unit/scoring/test pipeline to every corpus. Native encodings, source lineation and symbol inventories differ; log these differences. C-lat, C-respace and C-sandhi comparisons must be paired to the same underlying Latin source, alphabet and token-budget policy. Match usable token counts to frozen ZL paragraph geometry; stop short-source controls without recycling. No generated relation is inferred from its label: independently verify planted effects and shams from generator receipts.

Synthetic unit sequences must round-trip through the actual frozen rendering/parser. Concatenation can merge adjacent proposed units into a longer EVA cluster; a failed round-trip is a generator qualification failure, not permission to score an idealized unit list while claiming it is the rendered text. Freeze generator code and verify its intended relationships before the held-out calibration draw; never repair it after a scored failure.

## K1: position specificity

For positions P,Q in {initial,final}, fit counts `c_PQ(u_P(a),u_Q(b))` from forward adjacent training words. Score a test edge with

`log((c_PQ(u_P(a),u_Q(b))+.5)/(c_PQ(u_P(b),u_Q(a))+.5))`.

This compares reversing **word order**, keeping each word's spelling fixed. It is not the log ratio obtained by merely transposing the two unit roles. Use J=(final,initial), SS=(initial,initial), EE=(final,final), SE=(initial,final). Average over the same cycle edges; score ties<=1e-12 are wrong, never automatically forward. Closing an artificial loop adds a declared artificial edge; do not use that edge as evidence about real paragraph endpoints.

Run raw and matched-category versions. For the latter learn initial and final category maps from **training words only**, reused across all pairings. Let `k=min(11, number_of_distinct_initial_units−1, number_of_distinct_final_units−1)`; retain the top k units at each position, tie by codepoint sequence, map the nonempty tail and OOVs to OTHER. This yields the same observed class count on both sides when supported. It controls category count, **not entropy, tail mass or all information-capacity differences**. Report these quantities. If k<1, the matched-category control is unsupported; do not create empty pseudo-classes to pretend there are12 categories.

Freeze matched known-order pseudo-circles at11–20 and21–40 words, fresh reversals/rotations and exact RD window/exclusion/support rules: >=30 distinct windows and>=8 held-out families per bin. All four pairings and both variants use the same sealed flags and source windows. Report accuracies, ties, coverage and paired source-family bootstrap differences.

Calibration uses a predeclared finite-budget criterion: C-junc must meet the same J-minus-each margin used for the target; C-order must not produce an unsupported claim of J specificity; C-SS/C-EE must recover the deliberately planted alternative advantage. No benchmark is forced to have “no order.” Source/sham false-specificity control must qualify before a manuscript-specificity claim. A failing control stops K1; preserve the unfavorable output.

Target K1 requires, in **both** length bins and **both** feature variants, J accuracy at least .10 above each alternative and the paired lower95% family-bootstrap bound of each difference>0. Report all12 contrasts, including the best alternative. This is a conjunction; do not advertise a selected favorable contrast as the whole K1 pass. Separate per-contrast or per-stratum claims need the multiplicity policy frozen in the executable manifest. Repeating correlated windows does not multiply source families.

## K2: reading and spacing robustness

Refit the same J score on each admitted reading's training families; use the same family split and common source-locus panels wherever coverage permits. Also report each reading's complete eligible panel as sensitivity. For each required supported independent alternate and both comma variants, require accuracy>=.80 and lower clustered95% bound>=.65 at11–20 and21–40, with the same >=30-window/>=8-family support rules. Transcriber variants are repeated measurements of one manuscript, not independent biological or historical samples.

Primary ZL, at least one documented independent alternate, and both spacing variants must qualify. Every additional supported independent alternate admitted by the pre-score inventory must qualify too. A required unsupported/unresolved reading leaves K2 UNSUPPORTED and I closed; a supported failure gives K2 FAIL and I closed. Derived readings are reported as sensitivity but cannot substitute for the alternate requirement. A missing/unsupported reading is not evidence of an artifact. No scope can be called “independent of transcription” merely because two related versions agree.

## K3: annotated scope

Report K1/K2 separately in A/B varieties and in each supported annotated scribe; do not call A/B hands. Require the same source-family support and paired reading coverage within each stratum. Freeze the family of stratum claims and its adjustment before execution. Aggregate K qualification does not automatically qualify any stratum; unsupported strata are explicit.

Use “both supported Currier varieties in this paragraph sample” or name the passing strata. Remove “manuscript-wide”: A/B coverage cannot establish every folio, scribe, section or circular-text type. K3 does not erase an aggregate result, but I analyses are confirmatory only in independently qualified scope strata. If none qualify, I is UNSUPPORTED; no fallback to a convenient aggregate interpretation.

## I1: neighbor-conditioned unit statistics

Open only after K1/K2 and the corresponding synthetic/statistical calibration pass for the named scope. Primary outputs are **regressive-unit-conditioning**, **progressive-unit-conditioning**, **both**, or **not detected at calibrated sensitivity**. These are conditional associations, not phonetic, causal or language diagnoses.

Use common pairs whose two words each have at least two frozen units; no invented penultimate/second-unit values. Define regressive gain as `H(final_i | penultimate_i) − H(final_i | penultimate_i,initial_next)` and progressive gain as `H(initial_next | second_next) − H(initial_next | second_next,final_i)`. Retain signed finite-sample estimates; do not clip negatives to zero. Specify Miller–Madow conditional entropy as the weighted sum of per-context estimates `H_ML(Y|x)+(observed_categories_x−1)/(2*n_x*ln2)` on the same eligible sample for each contrast. Publish context counts, occupancy and uncorrected estimates as diagnostics; correction does not guarantee unbiased estimates in sparse cells.

Conditional randomization must preserve each tested conditioning variable. Regressive: permute neighbor initials within `(source page, penultimate unit)` cells. Progressive: permute preceding finals within `(source page, second unit)` cells. Cells with no possible change remain fixed and their mass is reported. Freeze informative-cell support, a minimum effect detectable in synthetic controls, source-family aggregation, >=1000 permutations, zero/tie handling and multiplicity across two directions/scopes before execution. “Family-clustered p-values” must be replaced by an exact executable statistic and resampling design; it is not an estimator by itself. Report finite Monte Carlo resolution.

C-sandhi's **added** gain must be recovered against its paired original/sham, and C-prog must qualify progressive sensitivity. C-zero/sham operating false-positive rates, not p>.05 in one Latin sample, qualify the null. C-lat/C-naibbe and target shuffles are empirical reference outcomes; a positive association there is not automatically an instrument error or a license to call them sandhi. A null/generator mismatch stops the corresponding I1 chain.

I1-full remains NOT_RUN_MISSING_SOURCE unless exact Oct22 ending definitions and provenance are hash-bound **before any JX result**. No newly fitted suffix family replaces them. If a later discovery follows results, it belongs to a separately labeled, prospectively registered follow-up.

Report residual final-given-penultimate and initial-given-second entropies on matched samples as descriptive flexibility measures. They neither identify the historically changing side nor compare full stem-conditioned freedom unless full stem models have been separately qualified.

## I2: within-word/cross-boundary distributional comparison

Measure JSD in bits, base2, between normalized distributions of cross-space unit pairs and within-word adjacent unit pairs, using the union pair support **within each corpus**, retaining zero cells with the standard zero contribution. Report pair counts, alphabet size, length distribution and source-family uncertainty. No arbitrary unit-label mapping across languages is inferred from this scalar.

Use paired real-editorial-space / respaced / planted-rewrite Latin references and the generated Naibbe reference. Word length, morphology, alphabet and generator rules can alter JSD without identifying boundaries. C-sandhi and unmodified Latin are not guaranteed to lie above both respaced references; that is a calibration hypothesis that must pass on source-separated reference evaluation if a categorical comparison is to be used.

Remove the contradictory “nearest reference” and overlapping “within or below” rules. Primary output is the continuous JSD and predeclared family-bootstrap contrasts against each reference. A comparison is **higher-than-both-respaced-references** only if each lower95% contrast bound>0; **lower-than-both** only if each upper bound<0; otherwise **not-separated**. These are descriptive reference comparisons, not real/false-plaintext-space classifications. Categorical generalization across languages or encodings requires separately preregistered held-out language/source validation; it is NOT_QUALIFIED by a single Latin pair. Do not infer causality from nonoverlapping CIs.

If the source reference-ordering calibration fails, preserve it, stop categorical I2 interpretation, and report the measurements as descriptive only under the already frozen reporting plan. Do not replace failed references or thresholds after viewing Voynich outcomes.

## Joint reporting and candidate use

Combine I1's association label with I2's measured contrasts in a table. A positive I1 plus a high JSD is *compatible with several mechanisms*, including grammatical/lexical relations and encoding rules; it is not confirmation of real word boundaries plus sandhi. Conflicts and not-separated comparisons stay unresolved. Remove the forced joint classifications “real boundaries” and “spaces likely not plaintext boundaries.”

No language row is eliminated, assigned a posterior probability or promoted on these statistics alone. Symbolic candidate priors and any source-qualified operational prediction must be frozen before results; NP means no directional typology inference. Later language references, transformation searches and reading attempts require their own registered sources, held-out source families, search budgets and wrong-language controls. The36-row count is not the whole future multiplicity burden.

## Freeze checklist and artifacts

Before execution, attach a machine-readable manifest with: approved candidate-list revision/hash; protocol revision/hash; exact generator/rule code and empirical corpus spans; source/ancestry/coverage and comma-offset ledgers; supported strata determined without feature scoring; matched-case construction, counts, seeds, sealed-key access ordering; pure-synthetic calibration effect/false-positive criteria; bootstrap and permutation algorithms/draws; multiple-comparison families; phase dependency/stop graph; software versions; and exclusive-create output paths. A missing dependency is NOT_RUN/UNSUPPORTED, not permission to invent a substitute.

This is the remaining executable binding work, **not an inconsistency left to resolve after results**. Freeze all such choices before generation. Once registered, preserve failed calibrations and technical failures; no seed/threshold rescue. Re's requested review does not authorize registration or scoring.

Write `results/jx/<registered-study-id>/<phase>/` ledgers, all trial scores/null assignments, metrics, plots, STATUS/report, and final hashes. Summary rows are corpus×reading×scope with K1 margins, K2 qualification, K3 coverage, I1 signed gains, optional I1-full status, I2 continuous contrasts and literal joint description. Keep FAIL, UNSUPPORTED, NOT_RUN and no-detected-effect distinct. Record prior RD exposure/design motivation briefly; no claim that Re remembers prior details is inferred from their availability.
