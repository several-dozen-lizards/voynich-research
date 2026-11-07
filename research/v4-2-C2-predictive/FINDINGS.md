# Predictive comparison: findings

**Retrospective, descriptive, H/F separate.**

The common-OR predictor outperformed the fixed context-varying predictor in the primary partition and all four additional fixed partition checks, in both readings. The primary common-model gain was 3.5288 nats total for H and 4.1885 for F. Per 1,000 eligible origins, this is 0.6526 H [conditional score-bootstrap interval 0.0872, 1.2355] and 0.7921 F [0.2307, 1.3908]. These intervals condition on trained fits/partition and omit training-refit variability.

This is measured predictive support for using the simpler predictor at this support and under the frozen penalties. It is not an equivalence test or proof that the real odds ratios are constant.

The controls explain the limit: the varying predictor won 20/20 strong-heterogeneity datasets per reading, but only 8/20 H and 9/20 F with genuine modest OR variation (1.5 versus 2.5). Real modest variation can therefore coexist with a common-model predictive win. Every control dataset is retained.

The likelihood conditions on the held-out folio-by-ending qok totals and sh/ch counts. It tests allocation across sh/ch without fitting held-out folio baselines. It does not predict section-level qok frequency. Recto/verso and panels remain together; all Rosettes f85/f86 material is one group.

![Predictive comparison and controls](predictive-comparison.png)

Independent verification: 14,330 scalar log-likelihood calculations, maximum disagreement 1.78e-14; 230 unseen-context fallback checks; all 160 fixed control datasets and all held-out rows reconciled. Original v4.2-C files remained unchanged.

The fuller v4.2-C section4.3/5 source remains missing. No post-result plant meta-regression or formal scale-artifact classification was silently substituted.

The autonomous loop remains STAGED. No vault subset, private image rating or live model was opened for this analysis. The alpha_V=0.005 reservation is separate staged budget accounting, not a significance allocation for this descriptive comparison.

See [full report](REPORT.md), [frozen protocol](PROTOCOL.json), [verification](VERIFICATION.json) and [saved results](RESULTS.json).
