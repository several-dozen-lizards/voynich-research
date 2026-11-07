"""Publish settled transfer/source budgets and current verification without claim scoring."""
from pathlib import Path
import json
from core import save,sha
from held import score,ClaimLocked
from recovery_design import require_recovery_release,RecoveryLocked

ROOT=Path(__file__).resolve().parent

def main():
    assert not (ROOT/'FREEZE.json').exists()
    plans=['QUALIFICATION-PLAN-v5.json','SOURCE-CONTROL-PLAN-v3.json','SOURCE-COVERAGE-PLAN.json',
           'TRANSFER-DIAGNOSTIC-PLAN-v2.json','SOURCE-ENTRYPOINT-PLAN-v2.json']
    for name in plans:
        plan=json.loads((ROOT/name).read_text());assert all(sha(ROOT/p)==s for p,s in plan['files'].items()),name
    q=json.loads((ROOT/'GENERATOR-QUALIFICATION.json').read_text());assert q['plan_sha256']==sha(ROOT/'QUALIFICATION-PLAN-v5.json')
    assert q['mapping_failures']==0 and q['reserve_used_for_mapping_fit'] is False
    diagnostic=json.loads((ROOT/'TRANSFER-DIAGNOSTIC-RESULTS.json').read_text())
    details=json.loads((ROOT/'UNSEEN-UNIT-DIAGNOSIS.json').read_text())
    entry=json.loads((ROOT/'SOURCE-ENTRYPOINT-VERIFICATION.json').read_text())
    policy=json.loads((ROOT/'UNKNOWN-AND-LENGTH-POLICY.json').read_text())
    for call,typ in [(lambda:score(ROOT,'H3',[]),ClaimLocked),(lambda:require_recovery_release(ROOT),RecoveryLocked)]:
        try:call()
        except typ:pass
        else:raise AssertionError('execution gate opened')
    old=json.loads((ROOT/'development-history/transfer-policy-start/PROTOCOL.json').read_text())
    prior=json.loads((ROOT/'development-history/transfer-policy-start/STATUS.json').read_text())
    blockers=[b for b in prior['blockers'] if b['id'] not in ('REAL_LATIN_TRANSFER','PARTITION_SOURCE_LENGTH','CLAIM_EXECUTION')]
    blockers.extend([
        dict(id='SOURCE_SUPPORT',status='POLICY_SETTLED_SCOPE_UNSUPPORTED',detail='Latin development has9709 contiguous slots, insufficient for five reading-cells; longest Gascon development work has10624 slots, insufficient for both scribe3 cells. No padding, partition pooling or source repetition. Complete comparisons remain unsupported at those sizes.'),
        dict(id='FROZEN_TRANSFER',status='POLICY_SETTLED_GAPS_RETAINED',detail='Full reserves show Italian5, Czech4, Gascon17 and real-Latin13 newly unmappable slots. Keep barriers and full-transfer NOT_ESTIMABLE; development mappings unchanged. No normalization/inventory repair trained on reserves.'),
        dict(id='CLAIM_EXECUTION',status='LOCKED',detail='Unknown-unit/source-length contracts now settled and implemented. H3, other held definitions, final priors/layout/runtime settings and a complete claim freeze remain required. Full recovery and manuscript scoring unrun.')])
    old.update(version='v5-transfer-policy-5',status='TRANSFER_DIAGNOSED_POLICIES_SETTLED_CLAIM_LOCKED',blockers=blockers,
        unknown_and_length_policy='UNKNOWN-AND-LENGTH-POLICY.json',policy_sha256=sha(ROOT/'UNKNOWN-AND-LENGTH-POLICY.json'),
        primary_source_entrypoint='source_contract.produce_from_development',generator_qualification_plan='QUALIFICATION-PLAN-v5.json',
        reserve_diagnostic_plan='TRANSFER-DIAGNOSTIC-PLAN-v2.json',H3='UNRESOLVED',claim_freeze_created=False)
    save(ROOT/'PROTOCOL.json',old)
    status=dict(status='TRANSFER_DIAGNOSED_POLICIES_SETTLED_CLAIM_LOCKED',complete=False,H3='UNRESOLVED',claim_freeze=False,
        unknown_policy='SETTLED: original masks retained; newly unmappable words stay barriers; full-transfer unqualified; never fit reserves',
        length_policy='SETTLED: development-only, contiguous same-work run, original slot budget, no wrapping/padding/partition pooling',
        blockers=blockers,development_source_cells_supported=43,development_source_cells_unsupported=7,
        candidate_entrypoint_trials=entry,engineering_tests=42,
        next_step='Retain these support limits. Independent development-source additions require a new cut and newly reserved evaluation material. H3 and other held definitions must be resolved before any claim freeze.',
        pending_claim_deliverables=prior['pending_claim_deliverables'])
    save(ROOT/'STATUS.json',status)
    table='\n'.join(f"| {r['source']} | {r['original_slots']:,} | {r['affected_slots']} | {', '.join(u['unit'] for u in r['unseen_types']) or 'none'} |" for r in details)
    report=f'''TRANSFER ABSTENTIONS DIAGNOSED; UNKNOWN-UNIT/SOURCE-LENGTH POLICIES SETTLED — H3 UNRESOLVED, CLAIM SCORING LOCKED.

# Voynich v5: frozen transfer and finite-source policy

This cut diagnoses the existing reserves and enforces development-only generation. **It fits no mapping, normalizer, inventory extension, abbreviation rate or model parameter to a reserve.** It does not run H1–H8, manuscript inference or full recovery.

## What caused the abstentions

The ten target EVA inventories have sufficient capacity. The source-side development codebooks lack a few literal units:

| Source | Full reserve slots | Newly unmappable slots | Unseen units |
|---|---:|---:|---|
{table}

Italian's five affected words are `mäi`, `mäometto` twice, `portäi`, and `vexilla`. Czech's four contain literal `w`; Gascon's17 contain `ç`. These written forms are retained; no spelling substitution or foreign-word removal is applied. Real Latin has twelve numeric-token slots containing previously unseen digits and one token with U+0301. Labels identify literal transcription codepoints, not inferred meanings. Raw source-unit/line/slot provenance is saved in `UNSEEN-UNIT-DIAGNOSIS.json`.

This extends the earlier first1,000-word sample to complete reserves. It finds additional Italian and Czech gaps. Source gaps repeat identically across ten target inventories: they are not ten independent discoveries. Latin and German have no newly unseen units in their complete reserves. Across60 source/cell views,20 fully transfer and40 remain not estimable for full transfer.

Every transfer codebook exactly reproduces its previously frozen **development-only** baseline. Altering diagnostic reserve content changes coverage but not codebooks. Reserve frequencies were counted for the requested diagnosis; they did not choose mappings, mergers, expansions, rates or acceptance thresholds.

## Unknown-unit policy, now enforced

`UNKNOWN-AND-LENGTH-POLICY.json` fixes the contract:

- Development alone fits inventories, position classes and maps. Calibration/reserve inputs are rejected by the fitting API.
- A newly unmappable word becomes one `None` barrier **in its original slot**, with raw units/provenance retained. Known fragments are not substituted for the word; later words are not repacked or promoted to line start. No adjacency is created across a barrier.
- Original transcription unknowns remain the pre-existing missingness mask. They are distinct from new transfer loss; the qualified scope is registered observable text, not reconstructed missing letters.
- Any newly unmappable originally readable word leaves **full-transfer qualification not estimable**. Supported-slot diagnostics have their own explicit masks and do not certify full-source G2 survival. Conditional held scoring would require its own later frozen estimand and support gate.
- No accent stripping, digit completion, mark merger, silent expansion, reserve reranking or reserve-based alphabet extension is admitted. Any future inventory extension needs independently selected development evidence, a new cut and newly reserved evaluation material.

`transfer_policy.py` implements immutable codebooks and barrier views; `BARRIER-PRESERVING-RESERVE-VIEWS.json` retains every original slot. Sparse source coverage is not a rejected production mechanism.

## Source-length policy, now enforced

Primary fitting/generation uses **development material only**. A corpus must contain one consecutive within-work run long enough for the target's **original slot count, including unknown positions**. Counts pooled across works, missing sections or partitions cannot satisfy that requirement. Eligible start positions are sampled uniformly without inspecting reserve or generated outcomes.

The source-backed entrypoint is **`source_contract.produce_from_development`**. It loads hash-registered development source units into an immutable corpus, samples an admissible same-work window, and delegates to the existing generator registry. Source-start fitting and reserve/calibration generation inputs are rejected. The registry also rejects insufficient budgets and source-wrap overrides before invoking a generator. G1–G4 now use bounded source slices; legacy wrapping remains only in explicitly historical standalone sandbox fixtures, outside the primary entrypoint.

No cyclic reuse, padding, unrelated-work stitching, post-shortage partition pooling or family-specific size reduction is allowed. Naturally repeated words remain present. Independent Monte Carlo draws may reuse the fixed corpus, but do not count as independent corpora. G5's native copying and G6's table reuse are their generative mechanisms and are not external-source padding.

Seven of50 development-language/reading-cell combinations are unsupported:

| Development source | Largest consecutive run | Unsupported cells |
|---|---:|---|
| Latin/Macer |9,709 slots|A-1-F10,137; A-1-H10,352; B-2-H10,031; B-3-F10,912; B-3-H11,331|
| Old Gascon |10,624 slots|B-3-F10,912; B-3-H11,331|

The Gascon development aggregate was14,863 words, but it spans three works; those counts cannot be stitched into one manuscript. Across all150 partition/cell combinations,49 lack the required consecutive run. Complete candidate comparisons at unsupported sizes remain unqualified. A smaller common-size experiment must be separately specified/frozen, not used to rescue a failed cell.

## Verification

- **42/42 engineering tests pass**, including rejection before generator invocation, immutable codebooks, reserve perturbation invariance, gap/work boundaries, original-slot budgets, source-file drift, and retained native missingness.
- Actual-geometry source-entrypoint checks: **58 supported generations and22 correct pre-generator size rejections**,80 cases total. The22 rejections include multiple Latin-dependent families sharing the seven source/cell shortages; these are not22 mechanism eliminations.
- The full mechanism/mapping schedule was replayed using **development Macer chapters only, without wrapping**:200 mechanism trials,1,600 successful group maps, and five published-G5 repeat pairs. No reserve supplied those new mapping fits.
- Current source and transfer plan hashes are unchanged. No claim `FREEZE.json` exists; held and full-recovery locks remain closed.

`RECOVERY-PROTOCOL.json` now incorporates the policy hash, safe source entrypoint and unsupported-size treatment. Its full experiment remains defined but unrun.

## Exposure and preserved history

Earlier whole-reserve representation maps are **diagnostic-only**, not frozen transfer proof. Earlier Macer last40% mechanism controls overlap what later became calibration/reserve partitions; those historical mapping fits are quarantined and never initialize the current development-only transfer. `RESERVE-EXPOSURE-LEDGER.json` preserves this history. We do not call those sources historically untouched.

The previous policies, diagnostics and generator owners remain under `development-history/transfer-policy-start/`, `transfer-policy-v1/` and `group-qualification-3/`. The policy clarification separating pre-existing unknowns from newly lost readable words changed none of the current source-gap outcomes. Earlier source extraction, partition and mapping failures are still retained.

Current artifacts: `UNKNOWN-AND-LENGTH-POLICY.json`, `UNSEEN-UNIT-DIAGNOSIS.json`, `CONTIGUOUS-SOURCE-SUPPORT.json`, `TRANSFER-DIAGNOSTIC-RESULTS.json`, `SOURCE-ENTRYPOINT-VERIFICATION.json`, `STATUS.json`, `VERIFICATION.json`. Prior source/provenance report: `development-history/transfer-policy-start/REPORT.md`.

**H3 remains unresolved.** No replacement estimator, reduced-H3 run, reserve-trained repair or held-out scientific score has been introduced.
'''
    (ROOT/'REPORT.md').write_text(report,encoding='utf-8')
    verification=json.loads((ROOT/'development-history/transfer-policy-start/VERIFICATION.json').read_text())
    verification.update(status=status['status'],engineering_tests=42,failures=0,errors=0,
        claim_ready=False,claim_freeze_exists=False,H3='UNRESOLVED',held_statistics_computed_on_generator_output=False,
        held_statistics_computed_on_manuscript=False,recovery_executed=False,manuscript_fit_performed=False,
        unknown_and_length_policy_settled=True,transfer_codebooks_reproduce_development_baselines=True,
        reserve_perturbation_changes_fitted_codebook=False,reserve_used_for_current_mapping_fit=False,
        active_qualification_plan='QUALIFICATION-PLAN-v5.json',mechanism_trials=200,mapping_trials=1600,mapping_failures=0,
        source_entrypoint_trials=80,supported_source_generations=58,pre_generator_source_rejections=22,
        development_source_cells_supported=43,development_source_cells_unsupported=7,
        current_frozen_plan_owner_hashes_unchanged=True,checked_plans=plans,
        report_sha256=sha(ROOT/'REPORT.md'),policy_sha256=sha(ROOT/'UNKNOWN-AND-LENGTH-POLICY.json'),
        recovery_protocol_sha256=sha(ROOT/'RECOVERY-PROTOCOL.json'),code_hashes={str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob('*.py')})
    verification['code_hashes']['GENERATORS/__init__.py']=sha(ROOT/'GENERATORS/__init__.py')
    save(ROOT/'VERIFICATION.json',verification)
    save(ROOT/'TEST-RESULTS.json',dict(command="python -m unittest discover -s system-types-v5 -p 'test_*.py' -v",tests=42,errors=0,failures=0,exit_code=0,
        scope='Engineering and source policy; no H1–H8 or full recovery scoring'))
    retained=json.loads((ROOT/'RETAINED-FAILURES.json').read_text())
    retained['current_unseen_units']='UNSEEN-UNIT-DIAGNOSIS.json; retained, not repaired from reserve'
    retained['current_source_length']='CONTIGUOUS-SOURCE-SUPPORT.json; seven unsupported development language/cells'
    retained['reserve_exposure']='RESERVE-EXPOSURE-LEDGER.json'
    save(ROOT/'RETAINED-FAILURES.json',retained)
    paths=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(ROOT/'RUNTIME') and not p.is_relative_to(ROOT/'G5-BUILD/classes') and p!=ROOT/'DELIVERY-HASHES.json']
    save(ROOT/'DELIVERY-HASHES.json',{str(p.relative_to(ROOT)):sha(p) for p in paths})
    print(json.dumps(dict(status=status['status'],delivery_files=len(paths),tests=42,reserve_fitted=False,held_scoring=False,recovery_executed=False)))

if __name__=='__main__':main()
