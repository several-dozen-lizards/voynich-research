# Voynich loop: an agentic research process that runs until a defined end state

**For:** Re, to implement on MOMMATRON with Codex / Claude Code workers.
**Written:** 24 Oct 2026 (Reed).
**Status:** design. Build the ledger and vault first; turn the loop on second.

---

## 0. The constraint that shapes everything

An agent can't recognise "deciphered". It **can** recognise defined, checkable end states. The biggest risk of running autonomously is **finding false patterns at industrial scale**: a loop that runs 500 sandbox looks and freezes the 20 prettiest will "confirm" noise. So the loop runs on four guardrails:

- a **sealed data vault**;
- a **global error budget**;
- an **independent skeptic**;
- **human gates** on anything that becomes a claim.

## 1. End states (the loop stops at any of these and writes a final report)

| ID | End state | Checkable criterion | Who declares |
|---|---|---|---|
| **T1** | **System type determined** | v5: one or two families survive, at least 3 are eliminated, H and F agree, and the recovery control passes | Re, after skeptic review |
| **T2** | **Anchor class found** | v6 T1 or T2 passes at claim tier, **and** replicates on a pre-split, never-touched label subset (§3) | Re |
| **T3** | **Reading** | A proposed value mapping predicts **held-out** material better than every control: label object classes, cross-references, or the vault reserve. Fitting is not enough. | Re, plus an outside expert recommended |
| **T4** | **Exhaustion** | The queue is empty, **or** 30 consecutive cycles pass with no new claim-tier result, **or** the error budget is spent | Automatic: write the final report and stop |
| **T5** | **Budget** | Compute or time cap reached | Automatic: pause and notify Re |

T3 is the only one that counts as "DONE done". T1 and T2 are realistic milestones. T4 is an honest stop. Every end state produces a report.

## 2. Roles

Each role is a separate session with a fresh context per cycle and its own working folder.

1. **Planner.** Reads `LEDGER.json`, proposes the next 1–3 tasks ranked by **expected information ÷ cost**, and writes `QUEUE.json`. It can't run analyses.
2. **Sandbox workers** (one or more). Run exploratory tasks on the **open** data only and write `E-` results to the ledger. They can't freeze anything or touch the vault.
3. **Freezer.** Turns a promising sandbox lead into a frozen protocol, in the format of v3–v6. **Capped at 5 freezes per 30 days.** It must state the error-budget spend.
4. **Qualifier.** Runs synthetic controls at real support for a frozen protocol. It can block a protocol but can't edit one.
5. **Scorer.** Runs a qualified frozen protocol once and writes the result.
6. **Skeptic.** A **different model family** from the Scorer where possible. It sees only the protocol, the code and the results, never the sandbox history that motivated them. Its job is to find a mundane explanation: a confound, a leak, a bug, a selection effect. A skeptic objection blocks promotion until Re rules on it.
7. **Ledger keeper.** The only role allowed to write the "held up" table. It merges results, hashes files, and enforces the rules in §3–4.

Re is the human gate for: promotions to "held up", vault access, end-state declarations, budget increases, and skeptic overrides.

## 3. Data vault (enforced by the filesystem, not by instructions)

- **`vault/`** sits on a path that **no worker process can read**: a different OS user, or a separate drive mounted only for the Scorer during an authorised vault run. It contains:
  - the reserved zodiac folios (Virgo, Libra, Scorpio, Sagittarius);
  - a **pre-split 30% of label loci** (random by folio, drawn once now with a published seed), kept for T2 replication;
  - any newly acquired material (new transcriptions, multispectral readings).
- Vault files are hashed into `VAULT-MANIFEST.json`. **Workers get only the open data**, with vault loci removed at the file level.
- A vault run requires: a frozen and qualified protocol, a skeptic pass on the open-data result, and Re's written OK in the ledger. **Each vault subset can be used once per hypothesis.**

## 4. Error budget (global, online)

- All **claim-tier** tests across the whole project share one **online false-discovery control**: alpha-investing (Foster & Stine) or LORD++.
  - Each test spends wealth, and each true discovery earns some back.
  - The Freezer must read the current α-wealth and declare the test's α before freezing.
- **Sandbox looks don't spend α, but they're all logged.** A claim-tier test motivated by a sandbox look **must** record how many related looks preceded it.
  - The Skeptic sees that count.
  - More than 50 related looks forces at least one replication on vault or fresh material before promotion.
- **Descriptive results never enter the "held up" table.**

## 5. Cycle

1. The Planner reads the ledger and queues tasks.
2. Sandbox workers run the E tasks and log the results.
3. The Planner picks at most one lead to propose for freezing, and the Freezer writes the protocol.
4. The Qualifier runs controls. If they fail, the protocol is blocked and logged.
5. The Scorer runs the protocol once.
6. The Skeptic reviews it. An objection goes to Re.
7. The Ledger keeper updates the ledger, checks the end states, and either writes a final report or schedules the next cycle.

**Cadence:** one cycle per day, run as a scheduled task, plus a daily digest to Re. The cycle pauses when Re needs to decide something.

## 6. Initial queue (seeded from 24 Oct)

1. v4.2-C: the odds-ratio context map (descriptive).
2. A frozen re-score of the v3.1 blocked cells (P1-F, bath, B-Q1), using the follow-up qualification.
3. v5: system-type ABC. Sandbox the generators, then freeze.
4. v6: label-object dataset. Registration and rating are infrastructure; T1 and T2 are claim tier.
5. A transcription upgrade, rerunning the attempt-C frozen test on a newer IVTFF transcription (robustness).
6. v4: image context. Continue only if registration yield is at least 30% of reading units on rated pages. Otherwise park it.
7. Source-tradition structural matching, which depends on v5's survivors.

**Parked:** v103. **Closed:** Rosettes leave-out grids, ey/eey "blocking", letter-substitution decoders.

## 7. Files

```
voynich-loop/
  LEDGER.json          # every result: id, tier, protocol hash, status, α spent, related-look count, skeptic verdict
  HELD-UP.md           # the only claims table, written by the Ledger keeper alone
  QUEUE.json
  BUDGET.json          # α-wealth, compute spent, caps
  protocols/<id>/      # frozen specs plus hashes (read-only after freeze)
  results/<id>/
  sandbox/<worker>/
  skeptic/<id>.md
  digests/YYYY-MM-DD.md
  VAULT-MANIFEST.json  # hashes only; the vault itself is elsewhere
```

## 8. Ledger entry schema (minimum)

```json
{"id":"v6-T1-pharma-H","tier":"claim","protocol_sha256":"…","frozen_utc":"…",
 "alpha_spent":0.004,"related_sandbox_looks":12,"qualification":"PASS",
 "result":"PASS|NO PASS|NOT ESTIMABLE|UNDERPOWERED|BLOCKED",
 "skeptic":"CLEAR|OBJECTION:<file>","re_decision":null,"held_up":false}
```

## 9. Known failure modes and the countermeasure for each

| Failure mode | Countermeasure |
|---|---|
| Agent drift / goal creep | The Planner can only queue from the ledger plus Re's notes. Every task cites its spec. |
| Slicing spirals | A sandbox cap of 20 looks per lead before it must be frozen or dropped |
| Self-grading | The Skeptic is a different model with no sandbox history |
| Leaks into the vault | Filesystem separation and hash checks on every cycle |
| Error-budget gaming | α is declared before freezing, and the Ledger keeper verifies it |
| Endless compute | T5 caps and a daily digest |
| Silent tool changes | Code is hashed per protocol, and environment versions are logged |

## 10. What it can't promise

The loop can **eliminate**, **characterise** and **find anchors** efficiently, and stop honestly. T3 probably needs something the manuscript alone may not contain: a source-text match or a bilingual. The loop's job is to get you to the point where that kind of recognition can happen, and to keep a record clean enough that a recognition could be trusted.