import json
from pathlib import Path
P=Path(__file__).parent
q=json.loads((P/'QUALIFICATION.json').read_text());mask=json.loads((P/'NOISE-MASK.json').read_text())
report=f'''# v7.2 attempt3 — dual-bank requalification

25October2026. **{q['status']}**.

The approved v7.2 amendment retains original C3 and requires a supplementary context-role-preserving bank. It fixes source-first controls and tests the actual dictionary trap on a preregistered, jointly native-readable H/F cohort. Earlier failed attempts remain unchanged.

## Outcomes

| Case | v7.2 verdict | Original coherence bits | Role-bank coherence bits | Same evaluations above99th in both |
|---|---|---:|---:|---|
'''
for name,z in q['cases'].items():
 report+=f"| {name} | {z['combined']['verdict']} | {z['original']['coherence_bits']:.3f} | {z['role']['coherence_bits']:.3f} | {', '.join(z['combined']['shared_above99']) or 'none'} |\n"
report+='\n| Fresh proposal cohort | n | Verdict counts | PASS rate | Exact one-sided95% upper PASS bound | Gate |\n|---|---:|---|---:|---:|---|\n'
for kind,z in q['negative'].items():report+=f"| {kind} | {z['n']} | {z['tally']} | {z['PASS_rate']:.2%} | {z['CP95_upper']:.4%} | {'PASS' if z['gate'] else 'FAIL'} |\n"
report+='\nAll qualification gates are reported individually in [QUALIFICATION.json](QUALIFICATION.json). PARTIAL rates are reported rather than gated. The two negative cohorts are kept separate; their error bounds are not pooled. The 20%-corrupted key remains a reported near miss, with no requirement that it FAIL. Its PASS does not establish exact key recovery.\n'
report+='''
## The trap is now scored completely

The fixed source-support rule selected the first40jointly present, native-readable H/F paragraph lines in the same eight training and eight held pages used by attempt2. Eighteen native-uncertainty exclusions remain in [TRAP-COVERAGE.json](TRAP-COVERAGE.json), together with all other nonadmitted lines and reasons. No key-dependent deletion or source repair was performed. Source selection and its input seal preceded trap fitting.

Both fitted negative keys have finite E3/E4 and zero undecodable held slots. Their scores, controls and random-key banks are complete. Their literal FAILs therefore do not depend on the two native uncertain slots that blocked attempt2. H/F are separate negative fits on paired source lines, not independent manuscript populations or a semantic cross-reading decoding result.

| Trap reading | E1 original-bank upper tail | E1 role-bank upper tail | E3 order gain bits/char | E4 target negative-loss value | Undecodable tokens |
|---|---:|---:|---:|---:|---:|
'''
for r in ('H','F'):
 z=q['cases']['TRAP-'+r];c=json.loads((P/('TRAP-'+r+'-C1-ONLY.json')).read_text());report+=f"| {r} | {z['original']['metrics']['E1']['mc_p']:.6f} | {z['role']['metrics']['E1']['mc_p']:.6f} | {c['observed']['E3']['value']:.6f} | {c['observed']['E4']['value']:.6f} | {c['observed']['E6']['ambiguous_or_unknown']} |\n"
report+='''
## What changed, and what did not

The [preceding diagnosis](../trap-diagnosis-v7.1/REPORT.md) located the old PARTIAL edge in five character-fallback spelling coincidences per reading. The memorized dictionary entries had exactly the same match count in every original C3 draw. Inactive whole-word x defaults dominated the original global permutation's fallback slots. That permutation followed its stated global frequency rule; the new supplementary comparison conditions on the already-declared use roles without deleting the original test.

The new sampler derives role strata solely from the KEY's rule-condition structure. It preserves unit inventory, context slots/conditions, all global and within-role value multisets and K. It uses no WORD-prefix heuristic, decoded forms, held values or desired outcomes to define strata. Each bank has1,000random draws. Key hashes and distinct-key counts are retained.

A PASS must pass coherence and matched controls in each bank and have at least two of the SAME E1–E5 above the99th-percentile criterion in both. A non-PASS becomes PARTIAL only if the SAME component reaches99.8th in both. Otherwise it is FAIL. The strict trap FAIL gate remains intact. The original E1–E6 functions, K, reserved rejection and all historical outcomes were preserved.

C1a/C1b now shuffle registered raw source before retokenizing with the fixed key. The validated builder checks immutable inputs, raw/tokenized agreement, word geometry, endpoint classes, unknown barriers and duplicate/reserved IDs. It reproduces the earlier character-key controls exactly and can also disrupt opaque whole-word units.

The accelerated worker preserves the raw scores exactly in reference comparisons against the untouched original implementation. It caches word decoding, lexicon queries and LM probabilities; it does not change the scoring definition or add a new uncertainty penalty.

## Noise, generators and provenance

'''
report+=f"The new synthetic H/F held readings have {mask['changed']}/{mask['sites']} differing source-character sites ({mask['realized_rate']:.6%}), using seed{mask['seed']} and the previously measured nonzodiac disagreement rate. Disjoint corruption masks are saved; each raw reading is retokenized consistently. Training stays clean. This is substitution-noise qualification and does not model native transcription boundary errors.\n\n"
report+='''All six v5 generator outputs are the unchanged, sealed outputs already produced through the qualified development entrypoint in attempt2. Their owner/source provenance and file hash are retained in V5-C2-PROVENANCE.json. No generator fitting, new v5 reserve access, model selection or claim recovery occurred here. PublishedG5 retains native geometry and seed-line exclusion. Actual-trap controls are tokenized with that trap's unchanged whole-word/fallback tokenizer and appropriate section metadata. Each C2 percentile is calculated separately in both banks, across the same corresponding1,000keys.

Original known/corrupt banks are reused only after exact equality of the scoring projection and all key hashes is asserted. New noise/trap/control banks are evaluated afresh. Every new bank has an input checksum in its checkpoint header. Reuse references, key hashes and checkpoints remain inspectable; source/tokenizer metadata is not silently ignored when determining whether scored words match.

## Scope

This is an infrastructure qualification on declared fixtures, not a decipherment or universal error guarantee. The positive uses an already-exposed edited Latin herbal with artificial12-word lines; the fresh negative draws are from its declared key family. Two actual overfit negatives test one dictionary-fit recipe. The source-first adapter currently supports the two stated fixture tokenizer modes. E2/v6 multi-token object/pair adapters and detailed E5/numeral arithmetic qualification remain to be completed before those capabilities are claimed. Native-uncertain whole-corpus language losses remain fail-closed; the readable qualification cohort does not certify a new missing-data policy.

The amendment and known-fixture reuse followed an exposed diagnosis and human approval. This is method development, not an independent historical validation. A future fixed key still needs provenance, a valid unbuilt-on test set, the appropriate adapters and controls, and its own frozen evaluation.

PartB/C requirements are unchanged. LISTS is still a source draft; no C2 structural look, ordered-name alignment or vault test ran. The separately administered alpha reservation and vault locks were not altered. The user's v7.2 approval authorized this qualification only.

[VERIFICATION.json](VERIFICATION.json) and [TEST-LOG.txt](TEST-LOG.txt) record independent arithmetic, source/control, key-bank, confidence-bound and preservation checks. All keys, selected/excluded source receipts, noisy inputs, null banks and failed controls are retained. Attempts1/2 are historical records, not overwritten by this result.
'''
(P/'REPORT.md').write_text(report,encoding='utf8');print(q['status'])
