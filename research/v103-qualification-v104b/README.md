# v103 qualification runner: Stage1 controls, attempt B

**PASS_STAGE1_CONTROLS_ONLY. Actual-layout power NOT RUN. Manuscript scoring CLOSED.** Original v103 design and prior failed gates are preserved. This deliverable implements and exercises the full-family Stage1 engine/control runner; it does not qualify manuscript-sized power or supply a manuscript scoring entrypoint.

All 56 panel/view/fixture cases met their required gates. All original 4,005 / 4,371 / 9,730 / 9,316 search columns remain, including constants and both signs via exact two-sided tails. Both middle definitions and x28 correction remain. Bath hand2 and Starred hand3, H/F separately, are never pooled. The fixtures are authored datasets instantiated under those four family manifests, not observations or independent replications of the manuscript.

The frozen code checks the signature DP against complete literal-order orbits and independent direct scores for every column, verifies paths against direct enumeration and the old v98 path routine, checks Fisher–Yates multiplicities, endpoints, inventories, edge counts, barriers and exact family rank bounds. Concrete independent/page/line/hand first-order nuisance weights are constant within each conditional fiber. The 4,096-draw sampler CDF audit uses a pre-sampling full-column support-point budget and a Hoeffding union bound. Small orbits and constant fixtures are retained and explicitly not claimed powered.

The deliberately planted 32-span positive is detected in every panel/view, with corrected target p=28/4097 (about .006834). This is an engineering positive, not an 80%/90% power result. Those unchanged actual-layout requirements and all three new-method banks remain mandatory before any retrospective manuscript scoring.

The scope diagnostics preserve a major limitation. Across the frozen views, exact target rejection probabilities are approximately 76–84% for position-dependent arrangements, 93–95% for repeated templates and 24–31% for literal-junction preferences. These generators violate the uniform class-transition conditional null. Their flags demonstrate residual dependence, not a calibrated false-positive rate or evidence of grammar. Every trial and exact mass is retained in `QUALIFICATION.json`; the report keeps all views separate.

## Preserved resource failures

Attempt A at `../v103-qualification-v104/` hit MemoryError during pre-sampling table construction. Its frozen code, trace and failure report remain unchanged. No random control draws had run. Attempt B separately froze the SAME fixtures, matrices, seed rule, counts, search family and gates, changing only memory management: stream table construction and full-column compressed output rather than retaining all tables/banks in RAM. `REPAIR.json` documents that change.

The original frozen replay helper `verify.py` then encountered MemoryError during ZIP reading amid host paging-file pressure. `VERIFICATION-RESOURCE-FAILURE.json` retains it. No controls were rerun. The separately frozen `verify_stream.py` uses only the Python standard library and row-wise ZIP reads. It independently reconstructs tail laws from direct literal permutations, not the tested signature DP. It replayed eight banks (54,844 column-views, 4,096 rows each), all minima/positive adjustments and 24 exact scope-diagnostic masses. `STREAM-VERIFY-FREEZE.json` and `VERIFICATION.json` contain the receipts.

Open `report.html`. `FREEZE.json`, `CONTROL-PLAN.json`, `FIXTURES.json`, `FAMILY.json`, `SUPPORT-PLAN.json`, `QUALIFICATION.json` and `VERIFICATION.json` distinguish frozen design, exact controls, numerical checks and unrun stages. The first attempt and original verifier remain available as failures; this pass does not erase them.

Do not rerun controls into this completed directory. `run.py` is one-shot and refuses an existing final qualification. To reproduce verification, use `verify_stream.py`; it makes no random draws or manuscript calculations. Browser appearance remains unreviewed. v98 stays FAIL and its banks2/3 remain unrun.
