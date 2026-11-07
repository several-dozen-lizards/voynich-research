Amendment v4.2: effect scale for H-IMG and H-PLANT (before any rating)

**For:** the v4 session. Freeze and hash this **before** any rating, registration or support computation. It supersedes v4 §6 and §8 where they conflict. v4.1 stands.

## Why

v3.2 found that qok base rates differ enormously between contexts. On scribe 1's botanical pages, qok follows 2–5% of origins; in bath it's around 25–30%. On a 3% base rate, a risk difference (RD) can't be large even when sh's *relative* pull toward qok is the same or stronger. Raw family rates show sh/ch ratios of roughly 2–3.6× in scribe 1 botanical, scribe 2 botanical, bath and starred alike, while the RDs run from about 1.8 to 10.5 points.

Image labels will correlate with qok base rate: plant lines are expected to be low-qok. If v4 stays on the RD scale, **H-PLANT could pass from base rate alone**, and H-IMG heterogeneity would be confounded the same way.

## Changes

1. **Primary effect scale: the Mantel–Haenszel log odds ratio** (sh vs ch → qok), using the same strata as v4 §5 (folio × ending × length bin). Strata with zero qok in both arms, or zero non-qok in both arms, contribute nothing to MH-OR. That's standard, and nothing is selected on outcome.
   - **H-IMG:** heterogeneity Q is computed on label-specific MH log-ORs. Use Robins–Breslow–Greenland variances for the descriptive Q; the inferential p-value still comes from the v4 within-folio label permutation.
   - **H-PLANT:** the statistic is log-OR(PL) − log-OR(non-PL). One-sided: PL < non-PL.
2. **Risk difference becomes secondary and descriptive.** Report it next to every OR. Where OR and RD disagree, report both and claim neither.
3. **Base-rate reporting.** For every label × scribe × reading, report the pooled qok rate after sh and after ch, so readers can see base-rate differences directly.
4. **Controls (v4 §8): add a base-rate null.** The qok base rate differs by label (PL lower, matching the real label mix), and the OR is the **same** across labels. Gate: upper Wilson-95 bound ≤ .05 for **both** H-IMG and H-PLANT on the OR scale. Also run it with the RD statistic, as a demonstration only, not a gate.
5. **Recalibrate the positive controls to the OR scale.**
   - H-IMG: OR 1 in one label, OR 2.5 in the others.
   - H-PLANT: OR 1.2 for PL, OR 2.5 for non-PL.
   Both use the real base rates per label. Gates are unchanged: lower bound ≥ .80, else UNDERPOWERED.
6. **Support gate (v4 §7):** add that each label needs at least **10 qok-follower events** in supported strata. MH-OR has no information when qok is very rare. This uses outcome counts, which v4's outcome-blind gate doesn't allow, so it is applied **after** the join, as an **abstain-only** rule. It can turn a cell into NOT ESTIMABLE but can never add one. Declared here.

## Optional retrospective companion (descriptive, separate session OK)

Recompute the v3 context map (C1–C8, all and available-only) as MH odds ratios with folio-bootstrap CIs, plus a REML τ² on log-OR across C1–C5. Label it retrospective and exploratory. The question it answers: **does the "weaker on plant pages" pattern disappear on the ratio scale?** It doesn't touch the v3 primaries.
