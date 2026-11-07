# Frozen nuisance-predictor repair: weak-score v2

The earlier weak-score v1 remains unchanged, including every failure. Its27-cell qualification found96/98/96 weak detections in three designs and all18 null cells passed. The16x48 strong cell failed: all100 scores were significant, but only87 nuisance predictions passed the constant+.01bits adequacy rule. The13 failures and their losses are preserved. This revision changes only the nuisance predictor, and is frozen before any fresh qualification or new manuscript scoring. No old manuscript outcomes are used to choose this repair.

The entire preceding weak-score v1 protocol is incorporated by hash. The score, honest learning/testing split, source extractor, H/F and section separation, unknown barriers, support, features, C=.25 raw logistic fits, interaction vocabulary/projection/direction, t statistic, factor4 primary/factor24 sensitivity, constant+.01bits adequacy rule, Wilson95 upper null<=.10, lower weak/strong power>=.80, exact paired improvement p<=.01, and all failure-stop conditions remain unchanged. No threshold is relaxed, and no failing design is dropped.

## Sole change: nuisance predictor

Instead of a single inner half-split with four sequential weights, obtain leave-one-learning-folio-out predictions for constant and the four unchanged raw models P,J,L,F. Each validation folio is wholly absent from that raw fit, including its vectorizer. Every learning event receives one OOF prediction per model. Testing folios never participate.

For each raw model m optimize one convex mixing weight with the OOF constant, using the unchanged derivative optimizer. The same candidate weight is fitted to all OOF learning events; there are no sequential mixtures. Compare its average natural-log loss gain with penalty [0.5log(n_learning)+log(4)]/n_learning. This is a prespecified one-parameter BIC/finite-choice-scale selection penalty, not a generalization guarantee or a manuscript adequacy threshold. Select the greatest penalized gain; ties follow P,J,L,F order. If no candidate has positive penalized gain, select constant. The inherited optimizer's1/n small-gain rejection cannot change an admitted candidate because this selection penalty is greater than1/n at allowed sample sizes.

Refit only the selected raw model on all learning folios, then use its frozen convex weight with the all-learning add-half constant on both learning and testing events. Save OOF assignments, probabilities, candidate weights/gains, selection penalty, chosen model, full raw probabilities and final nuisance probabilities. The learning residuals passed to the unchanged direction estimator use this same refitted mixture. Any benefit or harm to score calibration must pass the same full controls.

## Fresh qualification, unchanged controls and gates

Same three designs (16foliosx48events,10x100,12x96), nine regimes and100 independently seeded datasets per cell:2700 total. Same generators, including position/junction/phrase, distant proxies for local phrase/position, additive far effect without qok interaction, weak.65 and strong2.5 logit interactions, tiny.35 descriptive. Seeds1710000+design_index*100000+regime_index*1000+trial; disjoint from all prior weak-score seeds.

All18 null cells, all three weak cells, all three strong cells, and the existing exact paired ×24 improvement gate against context-transfer v2 on the first weak design must pass. Every unsupported or inadequate positive trial counts as a nondetection. Tiny and ×24 power remain fully reported, without new pass gates. Every required failure blocks ALL manuscript scoring. No post-failure narrowed scope or rescue.

For diagnosis only, also run the unchanged weak-score v1 on the same100 fresh strong16x48 datasets. Keep its adequacy, scores and flags beside the repair. This adds no new pass threshold and does not replace any existing gate. The old context-transfer v2 paired weak comparison retains its original gate and denominator.

Engineering: retain v1 parser, barrier, prefix-leak, generator replay, kernel dual/primal, scalar-score and zero-direction fixtures. Additionally check OOF allocations exclude validation and testing folios; independently replay model-choice weights, penalty and mixtures from saved predictions; confirm changing only testing labels cannot alter any nuisance probability or calibration allocation; and execute the real zero-direction fixture. Convergence errors or hash changes stop and remain recorded. Inherited fixtures are reused engineering, not fresh statistical evidence.

Only a full pass permits the original four-panel manuscript application. Save every event, honest split, OOF selection receipt, held-out probability/direction/score, per-folio mean, p4/p24, adequacy/support outcomes. Existing material is historically exposed; synthetic uniform layouts do not establish actual sparse-layout power. No grammar, meanings, causal spelling mechanism or language identification follows from this score.

Freeze hashes of this protocol, core.py and run.py; all imported v1 weak/core/context-transfer sources and protocols; preceding failure/qualification records; source atlas and manifest; and v94 definitions. Retain timestamps, all2700 fresh trial records, exact gates, independent audits, and the prior attempt. A failed repair remains a failure.
