# v4.2-C2 common versus context-varying odds ratio

**RETROSPECTIVE / DESCRIPTIVE. H/F kept separate; no vault access or autonomous-loop activation.**

The comparison conditions on each held-out folio × ending stratum’s fixed sh/ch counts and total qok count. It predicts the allocation of qok across sh/ch, not the unconditional frequency of qok. No held-out folio baseline is fitted.

Both models use the same normal-prior penalty on a shared log OR (SD 2.5). The varying model adds context deviations (SD 1), learned only on training folds. An unseen context uses the training shared effect. Recto/verso and all panels of a numbered folio stay together; all f85/f86 material is one Rosettes foldout group.

Positive Δ means the varying model predicted better. Primary score is held-out conditional log-likelihood, normalized by eligible origins. All models are scored without their training penalty.

| Reading | Common LL | Varying LL | Δ LL, nats | Δ nats/origin [conditional score-bootstrap interval] |
|---|---:|---:|---:|---|
| H | -267.9191 | -271.4479 | -3.5288 | -0.0006526 [-0.0012355, -0.0000872] |
| F | -266.0816 | -270.2701 | -4.1885 | -0.0007921 [-0.0013908, -0.0002307] |

The 4,999-draw paired physical-group bootstrap conditions on the fitted training sets and chosen primary partition. It omits training-refit variability; it is not an inferential model-selection test.

## Fixed partition sensitivities

| Reading | Partition | Δ nats/origin |
|---|---|---:|
| H | v4.2-C2-partition-1 | -0.0021206 |
| H | v4.2-C2-partition-2 | -0.0009699 |
| H | v4.2-C2-partition-3 | -0.0007319 |
| H | v4.2-C2-partition-4 | -0.0008177 |
| F | v4.2-C2-partition-1 | -0.0015181 |
| F | v4.2-C2-partition-2 | -0.0012155 |
| F | v4.2-C2-partition-3 | -0.0010575 |
| F | v4.2-C2-partition-4 | -0.0008308 |

## Fixed simulation controls at observed margins

| Reading | Scenario | Varying wins/N | Mean Δ nats/origin |
|---|---|---:|---:|
| H | common_OR1 | 1/20 | -0.0010383 |
| H | common_OR2 | 2/20 | -0.0005948 |
| H | modest_heterogeneous | 8/20 | -0.0003637 |
| H | strong_heterogeneous | 20/20 | +0.0024627 |
| F | common_OR1 | 1/20 | -0.0007567 |
| F | common_OR2 | 4/20 | -0.0004688 |
| F | modest_heterogeneous | 9/20 | -0.0002438 |
| F | strong_heterogeneous | 20/20 | +0.0021250 |

## Context contributions in the primary partition

| Context | H Δ nats/origin | F Δ nats/origin |
|---|---:|---:|
| C1 | -0.0013963 | -0.0014796 |
| C2 | -0.0000495 | -0.0007634 |
| C3 | +0.0005141 | +0.0004390 |
| C4 | -0.0003148 | -0.0001893 |
| C5 | +0.0002665 | -0.0002687 |
| C6 | -0.0005710 | -0.0003981 |
| C7 | -0.0000631 | -0.0006597 |
| C8-4 | +0.0004598 | -0.0055438 |
| C8-5 | -0.0099078 | -0.0092772 |

## Limits and provenance

- This is a comparison of these two fixed penalized predictors, not proof of constant strength, a single mechanism, grammar or sound values. No equivalence margin or “scale artifact likely” classification rule was supplied/frozen.
- The main 5-fold partition was fixed before fitting. Four additional fixed partitions are sensitivities, not extra independent replications; none replaces the primary.
- Sparse contexts may provide little information, and an entirely held-out context cannot teach its own deviation. In particular Rosettes has only one conservative physical foldout group.
- Controls preserve the observed qok totals. They test this conditional prediction problem and do not validate an unconditional generator of section frequencies.
- All saved strata, failed controls and partition outcomes are retained. H/F are alternate readings, not independent datasets.
- Original v4.2-C results and source text were not changed. This run uses only saved count tables; no raw EVT, images, ratings or vault subsets were read.
