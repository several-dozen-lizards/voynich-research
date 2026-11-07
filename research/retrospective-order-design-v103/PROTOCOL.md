# v103: retrospective residual opening order, exact-tail full-family correction

Status: **DESIGN FROZEN; full method and actual-layout power NOT QUALIFIED; manuscript scoring CLOSED.** This is a new candidate procedure after preserved v96–v99 failures. It does not reopen v98, certify fresh text, or turn v99 target-only powers into acceptance evidence. The source has been extensively explored. Even a later pass would be a model-conditional retrospective finding, not independent confirmation.

## Question and immutable scope

Does `sh` before `qok`, with exactly one intervening readable source word, occur more than the specified adjacent-transition conditional model predicts? Reverse cases are part of the same two-sided family. A residual means more than its conditional expectation, not necessarily merely a positive raw forward-minus-reverse count.

Use the same four actual panel definitions as v96/v98: Bath hand2/B/rawP H and F, and Starred hand3/B/rawP H and F, on the same shared source loci. Never pool hand, section, Currier variety, format, reading, or unknown spans. H/F are dependent alternate readings. No other-hand success is inferred. Sparse/unscored herbal and ambiguous-hand panels remain part of the historical correction budget; they are not silently promoted to tests or discarded to lower correction.

Statistic for every original opening-class pair (A,B):

`D_AB = count(A_i and B_(i+2)) - count(B_i and A_(i+2))`.

Retain both original middle definitions: any readable middle; middle that starts with neither sh nor qok. The latter restriction is the SAME focal sh/qok/other rule for every search column, as in v98; do not redefine it separately for a better-looking pair. Unknowns break spans, source line boundaries are never crossed, and no circular wraparound is inferred. A/B may overlap; contributions cancel when both directions apply. Literal spellings and word boundaries stay unchanged.

Keep EVERY original v75 family label and unordered pair in each panel, including zero/constant columns, both signs, forced classes and their overlap. Read the saved label manifest, not a new frequency screen. The four panel column counts must match 4005,4371,9730,9316 in original panel order. Both signs are handled by a two-sided tail; there is no post-hoc one-sided conversion. Retain the unchanged **x28** reading/stratum/view budget (14 historical reading/stratum panels x two middle views). Do not replace it with x8 because only eight views receive new qualification. No new lag, middle type, section, hand subset, ending group or rare-word selection is included.

## Conditional null: specify exactly what local means

S = word starts sh; Q = word starts qok; N = other readable word. Independently within each original readable span, preserve literal first/last words, the entire literal word multiset and all nine directed S/Q/N adjacent-transition counts. Condition on source unknown barriers. Sample uniformly over the distinct compatible literal orders. Every originally constant or one-path span stays in the analysis. No nearest-neighbour model fit, MCMC approximation, or cross-line token move.

This conditions on adjacent class order; it cannot test the aggregate adjacent sh/qok count that is fixed by that condition. It does not preserve every literal-word bigram, character junction or exact interior ordinal. A pass may reflect positional conventions, extended collocation, copying, notation or other higher-order structure. Do not claim all boundary mechanisms excluded, grammar established, or meanings recovered. Heterogeneous within-span position-dependent transitions are outside this null.

## New candidate correction: exact marginal tails, then full-family minP

v98 used pilot-standardized count contrasts. This design retains the null, statistic, family and budget but changes the extremeness scale to an exact conditional marginal tail. This is a separately labelled method change, not a repair to v98 results. It may have no power advantage.

For each span and A/B pair, group interior words by signature `(S/Q/N, A-membership bit, B-membership bit)`. There are at most twelve signatures. Keep signature counts, pinned endpoint signatures and all nine S/Q/N edges. Dynamic programming tracks the previous two signatures, remaining interior signature counts and remaining edges, accumulating the exact D histogram. Within-signature literal assignment multiplicity is constant across signature orders, so it cancels in probabilities. All literal inventories still remain fixed; overlapping memberships are represented by both bits, not forced into exclusive A/B classes.

Convolve span histograms to obtain full-panel exact integer weights `w_j(d)`. With `T_j=sum w_j` and `M_j=sum d*w_j(d)`, define the exact two-sided mean-distance tail

`p_j(d) = sum_{x: |x*T_j-M_j| >= |d*T_j-M_j|} w_j(x) / T_j`.

Use integer/rational comparisons, conservative ties and p=1 for a constant column. Cache ONLY identical complete null signatures; do not merge columns because their historical effects look similar. Resource limits: 250000 memo states per span/column/view; the unchanged v98 sampler cap of 20000 class paths per span. Any cap or counting failure blocks the whole affected panel, not just the troublesome column; keep its failure and finish independent diagnostic panels. No tail approximation, normal extrapolation, column drop or reduced precision fallback.

For each panel/view and bank, draw **4096** independent full layouts using the qualified v98 uniform class-path plus within-class literal assignment sampler. Compute every original family column and `m_b=min_j p_j(D_bj)`. The prospective adjusted target tail is

`p_adj(d) = min(1, 28*(1 + count_b[m_b <= p_target(d)]) / 4097)`.

No pilot or fitted standardization is needed. This is not the v75 finite-row marginal-rank minP: every marginal p comes from an exact conditional distribution. Monte Carlo joint calibration remains finite and variable. No zero Monte Carlo p-values. Bank seeds are the first eight SHA256 bytes, big-endian, of UTF-8 `v103/exact-tail-minP/bank/{1|2|3}/panel/{original_panel_index}`. Never redraw a failed bank.

Inferential guarantee is for the fully specified joint conditional null: all column statistics are deterministic summaries of exchangeable conditional layouts. Do not claim general strong FWER control for arbitrary mixtures of unrelated true and false individual nulls without an additional valid closure/subset argument. Full search correction also does not erase all historical researcher choices or the selection of this new method after v98/v99.

## Qualification before scoring: three distinct stages

**Stage 0, authored implementation checks.** Before source-layout tables: enumerate all strings of lengths1..6 over the four fixed signatures `(S,1),(S,3),(Q,2),(N,0)`; group by endpoints, signature inventory and edges. The DP histogram must exactly match direct enumeration in BOTH middle views, including overlaps, constants and asymmetric tails. Check exact finite-orbit full-family minP rank bounds, tied outcomes, duplicate-column invariance and plus-one arithmetic. These are arithmetic checks only. Their pass does not qualify the full sampler, actual family or power.

**Stage 1, full engine/null qualification.** Implement a qualification-only runner with no source scoring entrypoint, and freeze its complete code, controls and inputs BEFORE running it. Reuse the existing exhaustive S/Q/N path oracle for lengths1..7 and Fisher–Yates multiplicity checks including repeated literal words; independently check arbitrary A/B signatures, all score columns, endpoints, multisets, edge counts and unknown seams. Verify two-source-line and all-unknown/short fixtures never create a cross-boundary gap. Enumerate each finite authored full-layout orbit and compare exact family minima/tails to independent direct counts; null rejection fractions must not exceed the exact nominal alpha, including .05/28 where attainable. Pinned/one-path/all-constant cases are not-estimable, never negative evidence; nonconstant positive fixtures must also exist. Validate sampler path and literal-order frequencies against their exact laws with a pre-frozen familywise CDF audit, not visual agreement.

Required nuisance-only controls: independent words, page-specific, line/span-specific and hand-specific first-order S/Q/N transition matrices with uniform within-class word assignment, conditioned on the fixed endpoints/inventories/edges. Explicitly verify constant product weight within every authored fiber, since this is why a homogeneous within-span Markov mechanism is removed. Within-span positional transitions, repeated long templates and boundary-context generators are mandatory adversarial scope diagnostics: they may violate this null. A rejection there is residual dependence, not automatically a calibration error or evidence for grammar. Preserve those failures of mechanism specificity; do not change the null afterward to rescue the claim. No semantic qualification is supplied by these controls.

The Stage1 runner must enumerate and freeze its concrete nuisance matrices, trial counts (if sampling is used), seeds, multiplicity-adjusted CDF thresholds, and all fixture arrays before any control outcomes. Until that implementation freeze exists, Stage1 is **NOT RUN**, not implicitly qualified by this document. No staged omission may be used to jump to source scoring. A necessary code repair requires a new named frozen attempt; preserve this prototype and its result.

**Stage 2, actual-layout computation and power.** Only after every required Stage1 gate passes, construct exact marginal tables for every family column in all four panels/two views, using only the same frozen span inventories/endpoints/transition margins. NEVER evaluate the original gap arrangement. Target marginal distributions must exactly reproduce the saved v96 distributions, and target partial-coverage ledgers must reproduce v97. Verify all full-family columns and invariants, not merely sh/qok. Constant/sparse views and resource failures remain visible.

Stage2A: one new calibration bank per panel, finish all four panels/eight views despite failures in another panel. For every panel/view require exact focal null rejection probability <=.05/28, minimum attainable target adjusted p<=.01, and sampler-vs-exact marginal CDF checks with family alpha .001 across planned three banks and every audited support point/column/view. Freeze the implementation's exact support-point family count before sampling; use Bonferroni for that audit. The plus-one minP conditional-layout rank argument and all full-family toy checks are also mandatory; focal null size alone is not empirical proof of full-family calibration.

Power uses the **unchanged v97 alternative family**, not fitted manuscript effects: per-D weight ratios 1.1,1.25,1.5,2,3,4, null1 and reciprocal reverse; all/half/quarter coverage using the same SHA256-ranked variable-span subsets. These are r^D tilts within the fixed transition fibers, not r times as many word pairs. Reuse and independently verify the exact rational selected+remaining convolutions. Keep every 312 effect/coverage/layout case per bank, correct-direction, wrong-direction and any rejection.

The unchanged full-coverage forward gates are **>=80% power at r=1.5 and >=90% at r=2 in EACH of the eight views**. Do not average H/F, hands, sections, views or banks. Low, partial and reverse effects are mandatory diagnostics, not scope-selection tools. No power equivalence is asserted for arbitrary grammar or other residual mechanisms.

Stage2B: banks2 and3 for this NEW candidate run only if ALL Stage2A required gates pass. Each bank must independently pass all gates. Any failure leaves later banks explicitly NOT RUN and scoring CLOSED. These are new candidate banks; v98's failed attempt and unrun banks remain untouched. More sampling is not a post-failure remedy here.

## Source-scoring lock and interpretation

No source scoring is performed as part of this design or qualification. Only after the complete three-bank method/control/power pass may a separately frozen retrospective scoring run be prepared, using the unchanged statistic, family and correction. Its source arrangement must remain unopened until that lock passes. Save every reverse case, folio exception, unknown/one-path span, unsupported panel and alternate-reading conflict. No token-level meaning, operation, timing, grammar or translation assignment follows from a pass.

A power failure means the candidate cannot exclude the frozen effects at the promised sensitivity. It is neither evidence that the manuscript lacks residual structure nor permission to reduce the family. If this design also fails, retain it and stop this scoring branch. Do not search methods until something passes and present the winner as confirmation.

## Method references

- Phipson and Smyth, 2010, corrected2011: https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf — finite Monte Carlo rank p-values and the danger of zero tails.
- Westfall and Troendle, 2008: https://pmc.ncbi.nlm.nih.gov/articles/PMC3117234/ — multiple-testing closure and the assumptions behind stronger familywise-error claims. This design does not borrow an unproved strong-control guarantee.
