# Transition constraints versus search correction: frozen diagnostic v99

Status: diagnostic complete; v98 qualification remains **FAIL**. No manuscript score or p-value was calculated or rescored. Robustness banks 2 and 3 remain unrun. No gates, effects, family members or failed views were dropped.

Open `report.html` for the comparison. `PROTOCOL.json` and `FREEZE.json` were written before diagnostic computation; the latter records input, bank and analysis-script hashes. `COMPUTATION-QUALIFICATION.json` records the exact authored-data qualification before the layout calculations. `VERIFICATION.json` records replay of all 1,560 diagnostic cases, including exact agreement with all 312 original v98 powers.

Within the same strict transition-preserving alternative, full-coverage forward weight-1.5 targeted power is 86–95% across the eight reading/view layouts. Full opening-search and 28-panel/view correction reduces it to 3–16%. These easier thresholds are counterfactual diagnostics, not replacement acceptance screens. H and F remain dependent alternate readings, and Bath hand 2 and Starred hand 3 remain separate.

Preserving transitions retains 56–66% of the relaxed null score variance. This structural restriction cannot be read as a percentage of power lost. Relaxing the constraints changes the null and the own-base tilted alternatives. The model-mismatch comparison preserves substantial baseline rejection in some views: a relaxed test can respond to the local transition background without additional residual tilt.

`RESULTS.json` preserves every correction case, constraint/model-mismatch case and structural span ledger. `LOOSE-NULLS.json` preserves exact relaxed-null integer weights. `SUMMARY.json` is a compact numerical index. Power estimates are conditional on the saved first v98 pilot/calibration banks, fixed effect laws and coverage subsets. No causal allocation between constraints and multiplicity, semantic role or grammar claim follows.

Reproduction uses Python 3.10 with NumPy and SciPy: `run.py`, then `verify.py`, then `report.py`. Preserve the existing frozen outputs; a future independent rerun should use a new output directory and its own freeze. Browser visual review was not performed; the prior local-file policy block was respected.
