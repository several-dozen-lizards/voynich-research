# RD pre-registration design review — 2026-11-06

| Gate | Outcome |
|---|---|
| User draft preserved | `SPEC_USER_DRAFT.md`, byte-for-byte attachment copy |
| Source intake | Metadata and counts only; source hashes checked against existing Phase 0 freeze |
| Executable registration | NOT REGISTERED |
| RD Phase 0 empirical calibration | NOT RUN |
| Real ring feature scores / Phases 1–4 | NOT RUN |
| Corrected-order layer | NOT GENERATED |
| Design disposition | STOP before registration: seam target and null need amendment |

This is a preflight result, **not a failed empirical calibration and not evidence against reading direction or starts in the manuscript**. The original lab phases and their registrations are unchanged. RD remains a side spec; no v10 number is consumed. No external paper's mechanism or attribution was investigated; the draft's origin statement is preserved as supplied.

## Structural blockers

1. **Multiline loops do not identify one true start with S-pos.** Concatenating consecutive lines retains every original line-end→line-start junction. With three equal lines and a perfect first/interior/last classifier, all three junctions receive the same maximum. Rotating/reversing the loop does not make the first concatenated line uniquely recognizable. Recovering any line boundary and recovering the arbitrarily designated original start are different targets. This is a counterexample to unique identification by these signals, not a claim that every real paragraph has equal boundary strengths. Paragraph-first-line features could supply extra information, but the draft reserves S-p1 for description: promoting it would change the registered analysis.

2. **The maximum seam score cannot be tested against rotations of the same loop.** Let b(i)=s(w_i)+e(w_(i-1)). Rotating a loop only permutes the b(i) values, so max_i b(i) is unchanged. Under a tie-inclusive permutation test every rotation equals the observed maximum (p=1). A statistic tied to a fixed, independently supplied location can use a rotation null; a maximum over all locations cannot acquire peak significance that way. The Phase 3 word-shuffle null can change the maximum by changing adjacency, but it tests unusually strong boundary-feature pairing, not whether one recovered seam is the original start. Keep these claims separate.

3. **Radial text is an open path.** The official IVTFF specification defines Cc/Ca as clockwise/anticlockwise circumferential text and Ri/Ro as inward/outward radial text ([Table 9, pp.22–23](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf), issue 2.0.2, accessed 2026-11-06). A spoke has endpoints; it should not acquire a wraparound pair or a circular rotation seam by being placed in the same inventory. The inventory includes both, with type explicit. Open-path reversal/endpoint calibration needs to be frozen separately. Closed loops of length two have S-dir=0 because D(a,b)+D(b,a)=0; one-word paths have no order evidence.

## Other choices required before executable registration

| Topic | Missing choice / necessary correction |
|---|---|
| Calibration partition | Freeze folio-family split (foldout panels grouped), match rules, sample counts, overlap policy and exclusions. Held-out within RD does not mean historically unexposed in this lab. |
| Direction score | Freeze closed-cycle C versus open-path R edges; conditional or joint pair probabilities; smoothing, vocabulary/OOV policy and ties. Ties must not default to forward for accuracy. |
| Length gate | Fix bins, sample/folio requirements, CI method and multiplicity before scoring. The shortest passing bin alone does not establish power in every longer bin; retain all bin outcomes and require declared support for individual calls. |
| Seam estimand | Choose original sequence origin, any old line boundary, or original line origin in a single-line loop. These are distinct questions. Fix tie handling, reversed-coordinate mapping and error distance. |
| ±2 chance | For one uniformly placed target boundary use min(n,5)/n, not unbounded 5/n. For several acceptable boundaries/visual marks use the size of the union of their circular windows divided by n. Short rings may be automatically within ±2; require improvement over their actual null, not only a 50% success threshold. |
| Null acceptance | p>0.05 alone does not establish chance equivalence. Freeze number of null trials, acceptable false-positive rate/interval and the family of null checks. Do not retry seeds after a false alarm. Separate shuffled controls from real ring scoring, which the Phase 0 draft currently mixes. |
| Q3 readout | A three-class probe has no unique decision axis. Define distance/axis and calibration, group by folio/foldout, and freeze pooling/hand/section controls. A ring-trained classifier is an exception to “all signals learned on paragraph only”; identify it as such. |
| H-glyph | Reversal of EVA characters is not reversal of glyph units (`ch`→`hc`). Define and freeze synthetic reversal units, unreadable/alternative handling, and scope the result as a transcription-unit reversal check. Reversing order does not simulate reflected glyph shapes. |
| Position model | Freeze model/features/regularization/CV and continuous-position target, one-word line labels, calibration of probabilities, uncertainty barriers, segment-to-physical-line mapping, and missing-token treatment. Do not bridge unknowns to invent adjacent pairs. |
| Pooled direction | An ordinary sign test is unweighted. Define a separate weighted randomization statistic and clustering for rings sharing a folio; weighted binomial “sign test” is unspecified. Freeze two-sided tests, ties, BH families and stratified outputs. |
| Clock conversion | Source clock comments are transcriber annotations, sometimes absent. They are not independent physical marks. Word offset/n is only an equal-spacing angular proxy; actual clock agreement requires image-based word-boundary geometry and direction. Spirals/fragments/continuations need declared handling. |
| Physical marks | Re's annotation and exposure ledger are pending. Freeze all plausible marks (including none/uncertain), coordinates, excluded loci and mark-count-aware null before seeing model outputs. Do not copy source hints into a supposedly blind visual packet. |
| Corrected order | Keep provisional candidate order separate from an authenticated reading. Significant feature peaks do not by themselves validate a historical start. Define when an order is eligible to export; uncalled/unpowered loci remain unchanged with reasons. |
| Latin | Existing C1 is Hildegard OCR with remapped artificial layout; freeze source-contiguous train/test spans and section provenance. Do not treat remapped Voynich sections as genuine Latin source sections or use synthetic line positions to validate scribal starts. |
| Key sealing | Freeze generation/key/scoring/receipt sequence and hashes. Filesystem separation plus post-score access receipts provide an audit trail, not cryptographic investigator blinding. |

## Proposed next draft (not adopted or registered)

Keep Q1 as direction recovery; give circles closed-cycle scores and spokes open-path scores. Keep Q3 as a separately frozen descriptive/classification analysis.

For Q2, first calibrate **line-boundary localization**, accepting any retained original line boundary in multiline pseudo-rings with union-window chance correction. Treat single designated origin recovery as a separate gate requiring identifiable origin information. Single-line pseudo-rings can test that narrower unique line-origin task only at lengths actually supported by held-out source lines. A multiline line-boundary success must never unlock a claim of recovered unique historical start. If unique-origin calibration cannot be specified or fails, retain candidate boundary profiles as descriptive output and withhold corrected start-point export.

Use a word-shuffle maximum statistic only for boundary-feature pairing; use rotation of independently annotated positions for text–mark agreement, with all marks and selection accounted for. Report inference at the level actually qualified. These changes alter the estimand and therefore are proposals for a new frozen RD revision, not silent repairs to this draft.

## Artifacts and reproduction

Run `preflight.py` with the lab's bundled Python. Outputs are under `results/ringdir/preflight/`: ZL primary inventory; LSI alternate inventory without pooling; all observed codes and selected-code counts; blank visual-annotation worksheet; authored synthetic counterexamples; status and a hash manifest. The manifest records preflight provenance only and is deliberately not named registration.

`glyph_count` is empty because EVA codepoints do not establish glyph segmentation; `eva_codepoint_count` is provided. Missing starts/hands remain empty. Direction/seam calls are NOT_RUN or empty; an underpowered flag cannot be determined before calibration. Every source-selected C/R locus is retained, including short, uncertain, fragmentary or spurious records; eligibility awaits a frozen rule. Inventory rows are loci, not a claim that each is a complete independent ring.

Source text and source comments were seen by the agent during intake, with no fitted features or ring scores. The visual worksheet omits source clock/comment hints. Re's prior exposure is unknown and must be recorded honestly; neither this packet nor the existence of an unfilled worksheet establishes blindness. Phase 10's exposure distinction is retained (see `extensions/phase10_native_bridge_v1/PROTOCOL.md` and `EXPOSURE_AND_RETRIEVAL.json`).
