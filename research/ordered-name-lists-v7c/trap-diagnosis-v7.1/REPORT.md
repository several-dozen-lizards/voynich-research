# Why the v7.1 dictionary trap reached PARTIAL

Status: verified descriptive diagnosis. It does not change attempts1/2 or make a Voynich reading claim.

The apparent residual was entirely in the deliberately fixed character fallback. The fitted whole-word dictionary values contributed no gain over C3.

| Reading | Memorized entries: real / every C3 key | Fallback real hits | Original C3 median fallback hits | Original E1 tail | Role-preserving sensitivity tail |
|---|---:|---:|---:|---:|---:|
| H |111 /111|5|0|1/1001|65/1001 =0.06494|
| F |105 /105|5|0|1/1001|84/1001 =0.08392|

The H fallback examples are cholor→color, os→os, okor→odor, oeeo→oleo and otam→tam under the pre-existing normalized-edit-distance<=0.25 lexical rule. These are literal EVA-to-Latin spelling coincidences under the fixed identity fallback; they are not recovered meanings. Every token receipt, source position, best matching lexicon form and null hit count is retained.

## What the null was doing

In H, the key has250base-map entries:26character fallback entries and224whole-word entries. The latter use an x default, overridden by their section rules. Including the literal character x,225base entries therefore contain x. The original global permutation puts an expected23.4x values into the26character fallback slots, whereas the real key has only1. The analogous F expectation is23.37903.

The existing C3 follows its specified global value-frequency rule. Its arithmetic is correct. For the intended reference test, however, its broad randomization also destroys the deliberately different base-map use roles. A structured fake key can therefore earn a small E1 tail without earning a coherent reading. The original negative coherence correctly blocks PASS.

The frozen sensitivity preserves base values separately within the declared roles and keeps the context-rule permutation. Its results are labelled diagnostic and were never substituted into either recorded verdict. A generic role-preserving sampler was then implemented from KEY condition structure alone, without looking for WORD prefixes, source forms, decoded values or desired results. Its1000H/F hashes exactly reproduce the sensitivity draws; renaming unit identifiers preserves its behavior and all K/value-frequency invariants.

## Control and coverage repairs

Source-first C1b changes165raw words in each trap view, compared with115words changed by the old post-tokenization shuffle. The additional50changes reach opaque whole-word units. The fixed tokenizer is applied again after shuffling, with unknown barriers and word geometry preserved. The new validated builder rejects missing raw source, inconsistent registered tokenization, duplicate source IDs and reserved material. It reproduces the old character-based known-cipher controls exactly.

The two undecodable held slots in each reading are native transcription uncertainties. There are zero key-induced unknowns. The original E3/E4 abstention policy remains unchanged. The approved next attempt uses a source-only, jointly native-readable whole-line qualification cohort; all exclusions remain ledgered. It does not quietly delete failures from a key-specific score.

All six saved v5 generator families also have completed E1-only trap diagnostics under the unchanged tokenizer. These do not qualify E2/E5, revise a verdict, or stand in for the complete new qualification.

## Preserved decisions

v7.1 still returns PARTIAL in both readings, as recorded. Fixing C1 alone cannot alter a PARTIAL label defined by the real-text C3 rank. The strict FAIL gate was not relaxed.

The user approved the concrete v7.2 proposal in this chat: retain original C3, add the role-preserving comparison, require matching components in both banks, and re-qualify with complete trap support and controls. Its new attempt is separate at [attempt-3-v7.2](../attempt-3-v7.2/). This diagnostic is exposed design evidence, not an independent validation of that amendment.

Verification:20focused tests and200integrity/method checks passed. All163attempt2 files still match their saved hashes. See [VERIFICATION.json](VERIFICATION.json), [RESULTS.json](RESULTS.json), [NULL-STRUCTURE.json](NULL-STRUCTURE.json) and the per-token/per-key receipts.
