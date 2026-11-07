# Voynich loop: staged control layer

Implemented 24 October 2026 (America/New_York). **STAGED. No autonomous research worker or daily schedule is running. The vault is not yet sealed.** This follows the supplied design's order: build the ledger/custody layer before activating the loop. `ORIGINAL-SPEC.md` preserves that design verbatim.

Update: native worker filesystem profiles and a one-job Python role runner are implemented and qualified with neutral controls. Dormant Codex/Claude proposal transports are implemented and tested offline. See `DEPLOYMENT.md` for exact scope and `RE-INPUTS.json` for the caps/spec checklist. Model inference remains disabled and live transport qualification is outstanding; native OS qualification is recorded separately from model/vault-wide custody.

25 October budget amendment: Re accepted alpha_V=0.005. It is permanently reserved as a separate nonrecycling v7 familywise envelope. The remaining online LORD++ target is 0.045 with initial wealth 0.020; its next level is 0.010. The nominal project FDR bound remains 0.05 subject to valid family tests and the online method assumptions. This is an explicit hybrid amendment, not one LORD++ test funding several claims. See budget-amendments/v7-joint-alpha-005/AMENDMENT.md. Methodological review and family claim-admission qualification remain explicit activation locks; vault access and the loop remain off.

## What works

`loop.py` is a standard-library keeper-side state machine. It maintains an append-only hash-chained `EVENTS.jsonl` and derives `LEDGER.json`, `QUEUE.json`, `BUDGET.json`, `CONTROL.json`, `VAULT-MANIFEST.json`, and `HELD-UP.md`. A single keeper lock serializes mutations. Projection drift and changed frozen inputs block execution; an intact journal can recover interrupted projections. A broken/truncated journal requires operator recovery from a verified backup, never automatic truncation.

The state machine implements logged exploratory looks, the 20-look cap per lead, five freezes per rolling 30 days, immutable protocol/code hashes, qualification before a one-shot score, separate-model-family skeptic review, exact-request-bound operator decisions, promotion gates, one vault access per hypothesis/subset, independent replication requirements after more than 50 related looks, T1–T3 human declarations, and T4/T5 automatic accounting stops. Paused setup and blocked work are not counted as research exhaustion. Reports are written by the CLI on cycle/end operations, using unambiguous UTC timestamps.

Owning status files may change during concurrent work. Their drift blocks research, but the operator can approve a revised queue citing the new receipt hashes; previous references remain in the journal. This narrow repair route never bypasses frozen protocol/code/result/custody integrity checks.

`skeptic_packet` exports only the frozen protocol, sealed code, qualification evidence, score evidence and related-look count into a fresh folder. It excludes the ledger and exploratory result logs. The reviewer must still be launched in a separately verified process with only that folder readable. Creating the packet alone is not blinding.

`bootstrap.py` seeded the supplied queue against actual owning artifacts. The v3.1 re-score is **already complete**, retrospective, and receives no retroactive global-alpha credit. v4 has concurrent owners with different release scopes: registration-only release in one folder, a separate timing-exception release in another. Neither is a blanket handoff to this loop. v103 stays parked; the three closed research lines stay closed. v5 and v6 specifications are missing from the local project.

## Commands

Run from this directory, with Python 3.10 or newer:

```powershell
python loop.py status
python loop.py verify
python loop.py report
python -m unittest -v test_loop.py
```

The bootstrap and corpus preparation are one-shot; preserve their existing outputs. For a mutation, supply a JSON request:

```powershell
python loop.py freeze --request .\operator-request.json
python loop.py qualify --request .\qualification-receipt.json
python loop.py score --request .\score-receipt.json
python loop.py skeptic_packet --request .\claim-id.json
```

These research commands refuse to run in the current STAGED state. `loop.py --help` lists all actions; each action's exact required fields and checks are in `Store.transition`. Qualifier/scorer/skeptic outputs are **receipts to be validated by the trusted keeper**, not instructions executed by workers. `runner.py` now executes sealed Python jobs behind the qualified OS boundary, and refuses research while STAGED. It reserves resources before execution and retains failed attempts. Model inference, provider billing and daily orchestration remain disabled. `cycle` is an accounting checkpoint, not a model orchestrator.

## Vault preparation and exposure

`SPLIT-PLAN.json` fixes a public seed and deterministic folio-grouped candidate split: 180 of 585 physical L/S candidate loci (30.77%). The nearest prefix of SHA256-ranked folios is chosen to approach 30% of loci while keeping folios intact. All atlas reading codes share the same physical-locus assignment. The zodiac reserve is f72v1, f72v2, f73r and f73v. No manuscript statistic was computed to choose the split.

**This is an exposed/uncertified candidate cohort, not the never-touched v6 subset required for T2.** The existing atlas already contains the labels; v101/v102 also establish why protected word-sequence history cannot be inferred. Missing v6 eligibility means L/S is a provisional infrastructure definition. Preserve this assignment rather than shopping seeds or calling a redesigned split untouched.

`prepare_corpus.py` writes a filtered text-only `open-data/ROWS.json` and stages the two reserve partitions at a separately specified target. It removes *whole reserve folios*, including every alternate reading and paragraph on those folios, from the actual open file. This is stronger than removing only label rows and prevents cross-format copies on the same folio from leaking through the provided corpus. The reduced support must be recomputed and qualified; old full-corpus support cannot be reused unchanged. Original source files remain intact. Newly acquired material must enter custody separately, never automatically enter open data.

`CUSTODY-PREPARATION.json` records file hashes and exclusion checks. **PREPARED_UNSEALED is not SEALED.** Both coordinator and the current desktop chat can still read the original project. The keeper registers and checks the staged packet hashes; the manifest remains PREPARED_UNSEALED until filesystem enforcement is independently qualified and registered. No image packet is included, and no existing images were opened. A future image packet must remove entire reserved pages and be checked independently.

## Security boundary before activation

The research roles must not share this keeper process's filesystem rights. Give each role a fresh process and private work folder. Sandbox workers read only the filtered open packet; the Planner gets a sanitized ledger plus Re's notes, and cannot run analyses. The Freezer produces a proposal; only the trusted keeper commits it. The Qualifier cannot alter a freeze. The Scorer sees only qualified frozen inputs. The Skeptic receives only its exported packet and uses a different model family. The keeper alone writes this directory, code, protocols and claims table. Re's decision inbox must be operator-owned.

Use separate OS principals/mounted custody, or a tested OS-enforced deny-by-default process sandbox with equivalent restrictions. A folder, prompt, fresh context, or Python check is insufficient. Every worker must fail neutral-canary reads of the vault, original full corpus, other role folders, project artifacts, histories and credentials; fail keeper/code writes; and have network access denied so the public manuscript cannot be reacquired. The allowed packet must remain readable. Verify the exact launched profile and rendered context, including disabled memories/connectors/inherited history; do not infer isolation from another chat's successful probe. Run these checks before supplying reserve data. Qualify the separately authorized scorer profile as well, and revoke access after each run.

The CLI's `approve` action is intentionally **operator-only**, not an identity authentication service. It records written Re authorization with hashed evidence and binds it to the canonical SHA256 of an exact request (excluding `approval_id`). Workers must have no access to the keeper interpreter, editable control code, decision inbox or its writable directories. Otherwise a worker could forge a decision or rewrite a hash chain. Hash chains detect accidental drift relative to their retained head; an external keeper-owned backup/head is required against malicious replacement. Unit tests are not OS security qualification.

Register real isolation receipts with `isolation`, provisioned immutable files/subsets with `vault`, finite caps with `configure`, and a methodological review of selection/dependence with `activate`. Each requires an explicit, action-specific Re approval receipt. Do not fabricate approvals from this implementation request.

## Statistical accounting

Original initialization defaults (now historical): FDR target 0.05, initial wealth 0.025 and first LORD++ level 0.0125. The disjoint family amendment above supersedes those values before any registered claim test. The online gamma remains `1/(t(t+1))`; allocations follow the LORD++ equation. A claim freeze retains its spend even on qualification failure. Online slots stay serialized; the v7 family is separately reserved without refunds or online rewards.

For the remaining online stream a statistical rejection earns 0.025 for the first and 0.045 thereafter. Vault-family results never earn online wealth. We cannot observe "true discoveries"; human enthusiasm and promotion do not earn alpha. An objection blocks promotion and future freezes until resolved. Closing an objection pauses the statistical stream; evidence of invalid p-values requires methodological repair/new approved design rather than silently deleting a bad slot or keeping recycled credit in service. This version has no budget-increase, skeptic-override or statistical-reset shortcut; those require a separately reviewed extension. A fresh statistical epoch is not permission to restart multiplicity accounting over the same tested hypotheses.

LORD++ does **not** make retrospectively selected p-values valid or solve dependence from repeated manuscript use. Each frozen protocol must document selection validity, dependence assumptions, support, controls and within-test multiplicity; activation requires a hashed statistical review. H/F are alternate readings, not independent replications. Recovery qualification must use the allocated threshold and actual support; a .05 qualification is insufficient if the next level is .0125. Replication must be defined in the original freeze; it is a conjunctive requirement on that hypothesis, earns no additional reward, and cannot create an extra claim without its own allocation. Previously exposed data cannot certify fresh replication.

Sources: [onlineFDR theory and LORD++ equation](https://dsrobertson.github.io/onlineFDR/articles/theory.html), [Ramdas et al., 2017](https://arxiv.org/abs/1710.00499). `STATISTICAL-NOTES.md` records the implementation choices and limits.

## Remaining deployment inputs

- Full v5 and v6 specifications, including label eligibility, recovery controls and exact end-state evidence.
- A credible fresh/never-touched replication cohort, or an explicit revised T2 design. Existing exposed labels cannot meet the supplied T2 criterion.
- Keeper/worker principals or exact restrictive process profiles, custody target and successful OS canary/context receipts.
- Re-approved total time, cycle and compute caps. Dollar accounting needs a provider usage source or a conservative prepaid reservation; self-reported token estimates are insufficient.
- Native role processes and resource reservations are implemented. Live model transport, provider usage enforcement, automated role-output interpretation and full daily orchestration still require qualification before activation. No role may mutate the keeper directly.
- A daily schedule and digest delivery route/time in America/New_York, activated only after these gates. No email/message sending is authorized by a generic digest requirement.

The ledger/corpus tools are usable now; autonomous research and a sealed vault are not claimed complete.
