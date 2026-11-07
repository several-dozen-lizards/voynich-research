# Inactive deployment status

The research loop remains **STAGED**. No schedule, research cycle, model call, provider credential copy, alpha spend or claim promotion was performed during this setup work.

## Native filesystem boundary

`isolation.py` launches sealed Python capsules through this installation's native Windows MXC sandbox. Each process profile denies the filesystem root, allows only minimum OS/Python runtime reads, makes one input packet read-only, gives the job its own writable output folder and denies network access. No global ACLs, Windows accounts or household processes were changed.

The keeper must start from a normal host context. Starting MXC inside this chat's enclosing sandbox returned “native MXC is unavailable on this executor.” Host-side qualification succeeded through a narrowly scoped approved launch. There is **no fallback to an unrestricted worker**. The runner strips inherited API keys, Python paths, app control-pipe metadata, chat identity and provider credentials. Its trusted bootstrap strips launcher configuration variables before releasing task code; role inputs never contain authentication.

All six native role profiles were tested separately against neutral canaries: input readable; own output writable; input immutable; vault, original full corpus, other-role inputs, keeper/history/credential canaries unreadable; keeper, input, vault and other-role files unwritable; network denied against a working loopback endpoint. These are observations at the tested paths/profiles, not a machine-wide ACL or proof about every possible Windows resource.

An independent Windows Job Object enforces process-tree cleanup, CPU time, total committed memory and process count. The actual sandbox child must be in the job before the keeper sends RUN; a broker-created child is adopted while still blocked in the fixed bootstrap. The bootstrap also checks keeper/full-corpus/vault denial and input immutability before each real job. A failed handshake never releases the task. Closing the job kills surviving descendants. CPU, memory, timeout/descendant cleanup, failed exit and oversized stdout/file outputs have fixed native controls.

Output is size-monitored and checked again before acceptance. Unlike CPU/memory/process membership, the disk limit is a monitored threshold rather than a filesystem quota; a fast writer can overshoot between samples. Links, junctions/reparse points and hardlinks are rejected before the keeper ingests output. Input bytes are hashed before and after execution.

## Runner behavior

`runner.py` runs one explicit Python job for Planner, Sandbox, Freezer, Qualifier, Scorer or Skeptic. The keeper is never a worker. Its packet builder admits only role-appropriate sources: keeper-reviewed worker code, the filtered open corpus, an exact frozen claim packet, a chosen exploratory result, or the exported skeptic packet. Full source corpora, vault data and histories are not accepted as ordinary worker inputs. The current runner deliberately has **no vault-scoring path**; authorized vault scoring needs a separately qualified explicit subset profile, not an exception to the open runner.

The Planner receives a sanitized state file. Qualifier/Scorer code must match a sealed artifact hash; the Scorer requires qualification. Claim-role attempts are one-shot, including crashes. Each sandbox attempt is entered in the ledger before code runs and counts toward the lead's 20-look cap. The keeper reserves the entire approved per-job wall allowance before launch, never refunds a failed attempt and serializes jobs under its lock so two workers cannot race the budget. A successful subprocess is only pending keeper review: it cannot freeze a protocol, assign a scientific PASS, write HELD-UP or spend alpha itself.

The runner is not a full autonomous day-cycle controller. Model-led task planning and free-text output are not automatically converted into code or promoted. Daily orchestration and live provider adapters are separate from these qualified native processes.

## Model sessions remain disabled

`audit_model_context.py` rendered six fresh Codex contexts without invoking a model or copying credentials. It verified exact neutral task input, root-deny permissions, no inherited project/persona/memory content and fresh per-role runtime folders. This CLI still inserts its bundled generic skill catalogue; its roots were verified to be confined to each new runtime. Generic tool declarations can remain. **This is a supplied-context check, not a zero-tool or end-to-end model transport qualification.**

`model_broker.py` implements dormant Codex/Claude CLI proposal transports, separate from the native job runner. It uses fresh runtimes, explicit text packets, pinned models, restricted Codex tool profiles / empty Claude tools and MCP, pre-call total/per-cycle reservations, time/CPU/memory/output limits, incomplete/tool-response rejection and exact credential-copy cleanup. Offline tests exercise response handling, launch failures and call reservation using dummy credentials and mocked subprocesses. No real credential was copied. Model output cannot execute itself or admit a scientific result.

There has been no live Codex or Claude inference test and no Claude context audit. The broker refuses dispatch while STAGED and also requires Re-approved model caps, a fully registered custody boundary and provider-specific live transport/billing qualification evidence. The latter does not exist yet. After caps/billing choices are supplied, small separately authorized neutral transport smoke tests remain necessary before research activation. A native-process OS pass must not be used to claim that a separately running trusted CLI transport has the same boundary. New API/credit dollar-spending modes are unsupported without authoritative billing integration; local token estimates cannot enforce that cap.

For that reason the ledger still reports the vault as PREPARED_UNSEALED, with native-worker OS qualification recorded separately. Neither a model worker nor a vault scorer has received reserved data.

## Commands

From this directory:

```powershell
python runner.py status
python loop.py status
python verify.py
```

On the host (no inference, uses fixed neutral fixtures):

```powershell
python qualify_workers.py
python qualify_runner.py
python audit_model_context.py
```

Each qualification creates a new attempt directory and retains failures. `WORKER-ISOLATION.json`, `RUNNER-QUALIFICATION.json` and `MODEL-CONTEXT-AUDIT.json` point to the latest results. Changing boundary code invalidates its qualification; rerun its controls. `python runner.py run --request REQUEST.json` refuses all research dispatch while STAGED, before creating a job directory or starting a subprocess.

## Exactly what Re needs to supply

The editable checklist is `RE-INPUTS.json`; leaving values unset does not authorize a default.

**Caps:** maximum cycles; total calendar duration after activation (including approval pauses, matching the current ledger clock); total native compute allowance in minutes, measured conservatively as the sum of *reserved* per-job wall time; per-job wall/CPU/RAM/output ceilings (or permission to choose them inside the total allowance); and a separate total/per-cycle model-call allowance. For model billing, specify whether to use existing subscriptions only, whether any additional spending is allowed and its dollar ceiling. No additional spending or purchases are authorized currently. Qualification fixture limits are not research budget approval. Provider cost enforcement cannot be inferred from local token estimates or a CLI subscription balance.

**v5:** the full original specification file/text, including the candidate system families and generators, parameter ranges/priors, summary statistics/distances, simulation/fitting protocol, support/splits, elimination/survival rules and recovery-control pass criteria. The loop brief gives a milestone, not those definitions. I will extract the implementation details from the actual spec; Re does not need to retype them separately.

**v6:** the full original specification file/text, defining the label-locus eligibility/reading rules, object-class codebook, independent registration/rating/blinding and agreement/abstention rules, exact T1/T2 hypotheses/statistics/nulls/support/multiplicity and replication rule. The brief does not define what v6 T1/T2 actually test. Also supply the documented custody/exposure basis for any intended never-touched replication cohort. If no such cohort exists, that requirement needs an explicit redesign; the current exposed candidate split will not be relabelled untouched.

If the v5/v6 specs do not exist yet, say so. They can be drafted as designs, but must be distinguished from recovered instructions and frozen only after review.

Official CLI references: [OpenAI developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [Claude Code CLI](https://code.claude.com/docs/en/cli-reference). The executable version, installed flags, actual OS behavior and rendered contexts are pinned in local receipts rather than inferred from documentation alone. Hosted documentation can describe a newer CLI than the installed version; only locally supported flags are used here.

## Current statistical reservation

The v7 joint family now has alpha_V=0.005 reserved irreversibly. B gets0.0025; C pool0.0025 splits over C2-eligible arms (0.00125 /0.0008333333333333334 /0.000625 for2/3/4 arms). This changes the statistical budget only. Compute/model caps remain unset; no vault-execution approval exists. Remaining online LORD++ target/wealth are0.045/0.020. Activation is explicitly blocked pending hybrid-method review and family claim-admission qualification. Original pre-amendment allocation files were archived.
