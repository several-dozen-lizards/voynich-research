from pathlib import Path
import json,datetime
P=Path(__file__).parent
read=lambda name:json.loads((P/name).read_text(encoding='utf-8'))
support=read('SUPPORT.json');q=read('QUALIFICATION.json');v=read('VERIFICATION.json');rr=read('REFERENCE-NULL-REPLAY.json');rc=read('REFERENCE-COMPLETE-NULL-REPLAY.json');diag=read('RATER-ONLY-SUPPORT-DIAGNOSTIC.json');hold=read('JOIN-HOLD.json')
lines=[]
lines.append('RETROSPECTIVE IN TEXT; T1 PROSPECTIVE IN IMAGE VARIABLE ONLY.')
lines.append('T1 FINAL LABEL RESOLUTION, OUTCOME-BLIND SUPPORT AND REAL-SUPPORT CONTROLS')
lines.append('Result: NOT QUALIFIED ON THE DECLARED REAL SUPPORT. Real word-class outcome join and vault remain CLOSED.\n')
lines.append('1. FINAL LABEL RULE, FROZEN BEFORE SUPPORT')
lines.append('An exact A/B image-category agreement supplies the T1 label. Any disagreement stays UNRESOLVED and is excluded from T1 estimation. No rater/model priority, NO imputation, OT merge, category edits or analyst adjudication. All1,145 lines remain in the completed full-population G6/G2 receipts; those gates were not recomputed on a smaller population. The T1 consensus population is a separately declared analysis population.')
lines.append('There are912 consensus physical lines and233 image-category disagreements. These are not missing ratings. The numerical equality to the earlier912 paired-line diagnostic subset is coincidental; the old paired subset and the new exact-consensus set are different sets. All1,145 lines have both ratings.')
lines.append('LABEL-RESOLUTION-FREEZE.json pins the original executable T1 methods, completed ratings, blind geometry/wrap and reading maps. It explicitly records that this label-resolution freeze occurs after rating completion but before the label/readability-mask join; no original freeze is backdated.\n')
lines.append('2. OUTCOME-BLIND SUPPORT')
lines.append('A separate source process inherited the exact original-slot tokenizer. It inspected only registered H/F P-locus bodies after header admission; no reserved or unregistered body was tokenized. It had no image-label input and exported only original-slot readability booleans/metadata, never words or real class counts. Support then joined image labels, fixed geometry and these masks. Physical source slot0 is excluded even when unreadable; the first readable word is never promoted into that exclusion.')
for reading in ('H','F'):
 s=support['readings'][reading];a=s['audit'];lines.append(f'{reading}: consensus source lines={a["consensus_lines"]}; readable noninitial slots={a["readable_noninitial_slots"]}; unknown noninitial slots={a["unknown_noninitial_slots"]}; unavailable reading-map/source lines={a.get("unavailable_reading_lines",0)}; primary informative eligible folios={s["primary"]["informative_folios"]}; scan design upper bound={s["scan_design_upper_bound_folios"]} folios.')
lines.append('Primary T1 requires30 readable noninitial slots in EACH of FG/VE and PL/NO on the same folio, >=8 informative folios and no folio >25% weight. Neither reading has even one folio satisfying the30-per-side exposure gate. Thus primary T1 is NOT ESTIMABLE before any real word-class count is computed. FG/VE versus PL/NO largely separates folios instead of furnishing supported contrasts within folios.')
lines.append('A post-freeze exposure diagnostic did not change the rule: A alone gives0 eligible folios, B alone4, in both readings. B also falls below the frozen8-folio gate. This is not a post-result alternative analysis or a rescue.')
lines.append('The scan has at most14 informative folios, but its event-dependent support must be checked using synthetic counts. All15 pairwise equivalence-design gates fail; OT has no consensus lines. No unsupported bootstrap, invariant-class declaration or claim that nonsignificance establishes invariance is made.\n')
lines.append('3. REAL-SUPPORT SYNTHETIC CONTROLS')
lines.append('All2,000 declared datasets completed:200 independent datasets per scenario x5 scenarios x2 readings. Scenarios: independent null, wrap-only null, original word/block-line-position null, folio-latent null, and exact1.5x qok rate in FG/VE positive. H/F are dependent alternate readings of the same fixed geometry, not independent replications.')
lines.append('Actual label/readability/position support was fixed; all17 class counts were SYNTHETIC. Baseline opener probabilities were1/13 and ending-group probabilities1/4. No real class prevalence was read or fitted. The conclusions concern this declared synthetic profile at real support, not an estimate of manuscript effect sizes or false positives.')
lines.append('One fixed10,000-draw unrestricted within-folio line-label permutation bank per reading was reused across independent generated datasets. Finite p-values used every draw. An observed or permuted support failure caused NOT ESTIMABLE; no failed permutation was removed or redrawn. The generalized-CMH statistic, support gates, Holm17 and one-sided primary method were unchanged.')
lines.append('Every primary control was NOT ESTIMABLE from the real exposure failure. Undefined controls are not validated zero false positives. Scan-family flags below include only computed class p-values; complete-family counts expose the many abstentions.')
lines.append('\nScenario | H flags among defined classes / complete-family flags / complete families | F same; denominators200')
for scenario in ('independent-null','wrap-null','position-null','folio-latent-null','positive-1.5x'):
 cells=[]
 for reading in ('H','F'):
  d=v['control_diagnostics'][reading+':'+scenario];cells.append(f'{d["family_flags_any_defined_classes"]} / {d["flags_in_complete_families"]} / {d["complete_families"]}')
 lines.append(scenario+' | '+' | '.join(cells))
lines.append('\nThese are diagnostic flag frequencies, NOT a validated full-family false-positive estimate with undefined tests counted as negatives. Even counting only flags from fully estimable independent-null families, the lower-bound flag counts are:')
for reading in ('H','F'):
 d=v['control_diagnostics'][reading+':independent-null'];lines.append(f'{reading}: {d["flags_in_complete_families"]}/200 ({100*d["complete_flag_fraction_all_trials"]:.1f}%).')
lines.append('The primary support gate and scan calibration/estimability gates fail. Synthetic qok Holm detection for the1.5x positive:')
for reading in ('H','F'):
 d=q['cells'][reading+':positive-1.5x'];lines.append(f'{reading}: {d["scan_qok_flags"]}/200 ({100*d["scan_unconditional_qok_detection"]:.1f}%) versus required80%; primary remains not estimable.')
lines.append('\n4. REFERENCE REPLAY AND INTEGRITY')
lines.append('Sparse/batched algebra precomputed geometry and support only; it did not change the test. Balanced engineering fixtures compared all17 classes, observed and permuted statistics, and exact frozen shuffle order. Real-support boundary/reference checks cover first/last datasets in every cell, and numerical tie neighborhoods were replayed through the untouched method.')
lines.append(f'The first independent-null family flag was replayed across all10,000 stored permutations with the frozen engine: {rr["feature"]}, trial{rr["trial"]}, p={rr["reference_p"]}, exactly matching the accelerated result. A second replay from the first fully estimable flagged family also matched exactly: {rc["feature"]}, trial{rc["trial"]}, p={rc["reference_p"]}. Pure-label folios have exact zero contribution for every permutation; full/reduced zero-contribution checks passed. These flags are not numerical acceleration artifacts.')
lines.append('A pre-execution code correction name-keyed folio-latent seeds so H/F share the same latent value even when one reading lacks a folio. It was recorded before any control outcome; both source versions remain. No statistic, threshold, label rule, permutation restriction or undefined-draw rule was changed after results.')
lines.append('VERIFICATION.json checks source/input/code freezes, exact consensus, complete original rating population, H/F map exclusions, mask-only extraction, physical-first-slot exclusion, no reserved tokenization, support arithmetic, all200 trials per cell, Monte Carlo p resolution, independent Holm decisions and both full reference replays. Original T1 method files and previous qualification failures remain unchanged.\n')
lines.append('5. DECISION AND NEXT WORK')
lines.append('Do not open the T1 word-class outcome join. This is a support/qualification result, not evidence that manuscript word classes do or do not track pictures. No real qok/opener/ending association, primary effect, scan or classification was computed.')
lines.append('Next effort belongs in a count/image-only feasibility design for more within-folio mixed-context registration, and an independently frozen audit/repair of scan calibration at fixed layout/positions. Label exchangeability and sparse/unequal exposure are questions to investigate, not diagnoses established by this run. Preserve current thresholds and failures; any new null, stratum or comparison set must be separately declared and requalified before outcomes. The full-label invariance arm currently has no design support.')
lines.append('The vault, outcome join and alpha_V remain untouched. No external model calls were made in this continuation.')
(P/'REPORT.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('report_written')
