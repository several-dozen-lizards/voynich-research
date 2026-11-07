# v8 blind plant-part prominence — separate rating pass

Input to each independent call: this manual and exactly one complete page image. No tools, transcription, folio identity, text features, other images, other ratings, or research hypotheses. Do not identify plants or read the writing. Judge drawn geometry only.

First record eligibility: SINGLE_MAIN_PLANT, MULTIPLE_PLANTS, NO_MAIN_PLANT, or UNCERTAIN. A single main plant is one connected or clearly unified main botanical illustration. Separate disconnected detail drawings need not exclude a main plant; record them. If multiple equally substantial plants prevent a unique main drawing, choose MULTIPLE_PLANTS. Preserve ambiguity; do not choose a plant to fit the task.

Only for SINGLE_MAIN_PLANT, rate each part 0, 1, or 2:
- ROOT: below-ground root or rootstock drawing.
- STEM-LEAF: stem and leaves considered together.
- FLOWER: blossom or inflorescence drawing.
- SEED-FRUIT: seed, pod, fruit, or seed-head drawing.

Use the same geometric scale for each part:
0 = absent or minimal: not drawn or only a tiny, rudimentary indication.
1 = normal: clearly depicted and proportionate within the page's main drawing.
2 = emphasised or enlarged: conspicuously dominant, expanded, or elaborated relative to that drawing's other parts.

These are relative drawing judgments, not biological size expectations. Do not use species identification or supposed natural proportions. An uncertain organ must be marked unrateable with a brief reason; do not infer an organ from the text. Use null rather than a forced integer. Record the visible reason for every score and any ambiguous boundary.

Return exactly one JSON object:
{"task_id":"provided opaque ID","eligibility":"SINGLE_MAIN_PLANT|MULTIPLE_PLANTS|NO_MAIN_PLANT|UNCERTAIN","parts":{"ROOT":null,"STEM-LEAF":null,"FLOWER":null,"SEED-FRUIT":null},"reasons":{"ROOT":"","STEM-LEAF":"","FLOWER":"","SEED-FRUIT":""},"eligibility_reason":"","uncertainties":[]}

For ineligible or uncertain pages, all four scores must be null. Never silently replace a missing or invalid response with 0.

Research-side collection rule (do not append research context to individual calls): two independent raters from different model families, or a human route satisfying the spec. Keep model/version, prompt/manual/image hashes, session identifiers, original errors and retries. Run raw quadratic-weighted kappa separately for each part before any adjudication. ROOT needs kappa >= .60; each other part has its own gate. Undefined kappa abstains. Report missing pairs and eligibility disagreement; paired-subset agreement alone does not establish full-cohort coverage.
