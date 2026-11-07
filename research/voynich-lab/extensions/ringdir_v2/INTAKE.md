# RD-v2 intake — 2026-11-06

Status: DRAFT_STAGED, NOT REGISTERED, NO CALIBRATION GENERATED OR SCORED. The attachment is preserved byte-for-byte in `SPEC_USER_DRAFT.md`. RD-v1 and RD-C2 are unchanged. This intake incorporates the user's exposure clarification; it is not another calibration run or a change to old registrations.

## Exposure wording for the working draft

Re reports no retained recall of the inventory details. Prior availability of transcription metadata is recorded as provenance; it does not establish recollection or use of specific start positions. Do not assert that Re saw each named comment or comparison without evidence, and do not automatically label her visual annotation non-blind from availability alone.

For prospective annotation, record whether source start-position hints are consulted during annotation, and freeze the annotation before text-derived model outputs are viewed. An independent annotator is an optional stronger control, not a prerequisite imposed by this intake. Describe the actual annotation procedure; do not claim historical never-exposed blindness. This is a short process note, not a finding of contamination.

Replace the draft's sentence “No real-ring text or scores have been seen by anyone” with: **No real-ring model scores have been computed in RD. The agent read raw transcription excerpts/comments during source intake. Re reports no retained recall of the inventory details.** Those are separate facts. No permanent memory update was requested or made.

## Read-only eligibility check

Applied the supplied general thresholds directly to the frozen inventory, before generation or feature scoring. Counts use the frozen baseline tokenization and codepoint counts; unknown-token ratio is not a measurement of real manuscript damage.

| Quantity | Count |
|---|---:|
| Circular loci before exclusions | 84 |
| Excluded by the supplied general rules | 3 |
| Remaining circular loci | 81 |
| Remaining 41–80-word loci | 12 |
| Clean among those 12 | 3 |
| Uncertain among those 12 | 9 |
| Maximum radial word count | 8 |

| Excluded locus | Words | EVA codepoints | Unknown words | Rule triggered |
|---|---:|---:|---:|---|
| f57v.3 | 68 | 72 | 16 | codepoints/word <2; unknown fraction >.20 |
| f57v.5 | 35 | 61 | 2 | codepoints/word <2 |
| f70r1.1 | 2 | 17 | 1 | unknown fraction >.20 |

These exclusions are the consequence of the proposed rule, not new evidence that the excluded texts are nonlinguistic. The three long clean loci remain f72r3.14, fRos.20 and fRos.62. Eligibility is not a power result.

## Items to settle in the executable registration

- The workspace search did not locate exact files named `ending_consistency.py` or `abbrev_function.py`. Do not substitute later ending analyses and call them the Oct 22 freeze. Bind the intended source/segmentation and its Latin analogue before S-dir-stem runs; otherwise use the draft's NOT_RUN disposition. The S-m ending-table source also needs an exact pointer and hash. These missing dependencies do not by themselves close independent word/glyph/position chains.
- Runnable v5 generators exist at `system-types-v5/GENERATORS/__init__.py`; existence is not an RD-v2 binding or permission to execute old owning pipelines. Arm F still needs frozen input/output identities, parameters, split and Naibbe binding.
- Arm P needs a fixed number of sets, exact family-mapping/fallback rules, a decision threshold for weighted/unweighted calls, and an exact-balanced mixed condition (with a stated odd-size policy). A random independent 50% reversal probability is not the same as an exactly balanced set. Account for shared source families between sets when reporting reliability.
- Arm U needs an explicit raw uncertainty parser: first alternatives and genuinely unreadable units are different. Preserve uncertainty barriers rather than remove tokens and create new adjacencies. Run the same uncertainty policy for models and controls.
- Arm K needs its peak definition, number of shuffles, tie/zero-peak handling and support/class balance frozen. Test support for each k without manufacturing long single lines. A significant peak count measures the registered feature peaks, not automatically the number of historical construction units.
- Arm O needs paragraph completeness rules (`<%>` through `<$>` with no missing/excluded segment), feature windows for S-p1/S-m, and standardization fitted only on training paragraphs. Keep whole-paragraph origins distinct from arbitrary first-window boundaries. A k=1 line-boundary result does not by itself establish that a target ring was authored as a paragraph; retain that transfer assumption.
- Freeze fresh seeds, sample counts, per-arm stop/dependency rules and all executable code before any RD-v2 generation/scoring. Prior passes are prior evidence only, exactly as the new draft requests. The selected design is motivated by previous results and must be reported that way; no exposure alarm is required to state this.

No real-ring output or new empirical calibration was produced during this intake. The user's exposure clarification does not authorize a change to historical receipts.
