"""Voynich research ledger. Standard library; keeper-side, staged by default.

No model invocation or scheduler installation is implicit in this program.
EVENTS.jsonl is authoritative; JSON/Markdown files are checked projections.
Run `python loop.py --help`. See README.md for the OS security boundary.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path


class GateError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise GateError(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def filehash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def readjson(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      parse_constant=lambda x: (_ for _ in ()).throw(GateError("Nonfinite JSON")))


def writejson(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n")
    # Defender/OneDrive may transiently hold a Windows file without delete sharing.
    # Keep replacement atomic; never fall back to overwriting the destination.
    for attempt in range(6):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(.025 * (2 ** attempt))


def number(value, low=0, high=float("inf")):
    require(type(value) in (int, float) and math.isfinite(value) and low <= value <= high,
            "Expected finite number in allowed range")
    return value


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", value), "Invalid id")
    require(value not in (".", ".."), "Invalid id")
    return value


def gamma(t):
    return 1 / (t * (t + 1)) if t > 0 else 0.0


def lord_level(budget):
    """LORD++, gamma_t=1/(t(t+1)); infinite sum gamma=1."""
    t = len(budget["tests"]) + 1
    rejections = [i + 1 for i, test in enumerate(budget["tests"]) if test["rejected"]]
    a = budget["w0"] * gamma(t)
    if rejections:
        a += (budget["fdr_target"] - budget["w0"]) * gamma(t - rejections[0])
        a += budget["fdr_target"] * sum(gamma(t - r) for r in rejections[1:])
    return a


def held_table(state):
    rows = ["# Held up", "", "Only keeper-promoted claim-tier findings appear here.", "",
            "| ID | Protocol SHA256 | Result | Decision |", "|---|---|---|---|"]
    for e in state["entries"]:
        if e.get("held_up"):
            rows.append(f"| {e['id']} | {e['protocol_sha256']} | {e['result']} | {e['re_decision']} |")
    if not any(e.get("held_up") for e in state["entries"]):
        rows += ["", "No claims promoted."]
    return "\n".join(rows) + "\n"


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()

    @contextlib.contextmanager
    def lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / ".keeper.lock"
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise GateError("Keeper locked; inspect owner/crash before manual lock recovery")
        try:
            os.write(fd, f"{os.getpid()} {utc()}".encode())
            os.close(fd)
            yield
        finally:
            path.unlink()

    def load(self, projections=True):
        previous = None
        state = None
        journal = self.root / "EVENTS.jsonl"
        require(journal.exists(), "Initialize ledger first")
        for seq, line in enumerate(journal.read_text(encoding="utf-8").splitlines(), 1):
            try:
                event = json.loads(line)
                h = event.pop("sha256")
                require(event["seq"] == seq and event["previous"] == previous and digest(event) == h,
                        "Journal integrity failure")
                previous, state = h, event["state"]
            except (ValueError, KeyError) as exc:
                raise GateError(f"Journal invalid at line {seq}: {exc}")
        require(state is not None, "Empty journal")
        if projections:
            for name, expected in self.projections(state).items():
                require(readjson(self.root / name) == expected, f"Projection drift: {name}; use recover")
            require((self.root / "HELD-UP.md").read_text(encoding="utf-8") == held_table(state),
                    "HELD-UP.md was edited outside keeper")
        return state, previous, seq

    def projections(self, s):
        return {"LEDGER.json": {"schema_version": 1, "entries": s["entries"], "cycles": s["cycles"],
                                "mode": s["mode"], "end_state": s["end_state"]},
                "QUEUE.json": s["queue"], "BUDGET.json": s["budget"],
                "VAULT-MANIFEST.json": s["vault"], "CONTROL.json": s["control"]}

    def render(self, s):
        for name, obj in self.projections(s).items():
            writejson(self.root / name, obj)
        (self.root / "HELD-UP.md").write_text(held_table(s), encoding="utf-8")

    def commit(self, s, action, previous=None, seq=0):
        event = dict(seq=seq + 1, utc=utc(), action=action, previous=previous, state=s)
        event["sha256"] = digest(event)
        with (self.root / "EVENTS.jsonl").open("a", encoding="utf-8", newline="\n") as f:
            f.write(canonical(event).decode() + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.render(s)

    def initialize(self, queue, split_plan=None):
        with self.lock():
            require(not (self.root / "EVENTS.jsonl").exists(), "Already initialized")
            for p in ("protocols", "results", "sandbox", "skeptic", "digests", "reports", "decisions", "packets"):
                (self.root / p).mkdir(exist_ok=True)
            state = dict(schema_version=1, mode="STAGED", end_state=None, entries=[], cycles=[], queue=queue,
                control=dict(created_utc=utc(), runtime=dict(python=sys.version, platform=platform.platform()),
                    isolation=None, approvals={}, no_claim_cycles=0, last_promoted_count=0,
                    historical_look_counts_certified=False, dependence_review=None),
                vault=dict(status="UNPROVISIONED", files={}, subsets={}, split_plan=split_plan,
                           historical_exposure="EXPOSED_OR_UNCERTIFIED; new split cannot erase exposure"),
                budget=dict(method="LORD++", gamma="1/(t*(t+1))", fdr_target=.05, w0=.025,
                    alpha_wealth=.025, tests=[], freezes=[], freeze_cap_30_days=5,
                    sandbox_cap_per_lead=20, no_claim_cycle_cap=30,
                    max_cycles=None, max_wall_seconds=None, max_compute_units=None,
                    compute_spent=0, active_wall_seconds=0, started_utc=None,
                    configuration="PROPOSED; requires Re budget approval before activation"))
            self.commit(state, "initialize")

    def evidence(self, evidence):
        require(isinstance(evidence, dict) and evidence, "Hashed evidence is required")
        for p, h in evidence.items():
            require(Path(p).is_absolute() and len(h) == 64 and filehash(p) == h, f"Evidence changed: {p}")
        return dict(evidence)

    def audit(self, state, queue_sources=True):
        """All registered immutable inputs, every cycle; no vault content read by workers."""
        for e in state["entries"]:
            if e.get("evidence"):
                self.evidence(e["evidence"])
            if e.get("protocol_sha256"):
                folder = self.root / "protocols" / e["id"]
                require(filehash(folder / "PROTOCOL.json") == e["protocol_sha256"], "Frozen protocol drift")
                self.evidence(e["artifacts"])
            for key in ("qualification_evidence", "score_evidence", "skeptic_evidence", "replication_evidence"):
                if e.get(key):
                    self.evidence(e[key])
        if queue_sources:
            for item in state["queue"]:
                if item.get("sources"):
                    self.evidence(item["sources"])
        isolation = state["control"].get("isolation")
        runner_policy = state["control"].get("runner_policy")
        native = state["control"].get("native_worker_qualification")
        for family in state["budget"].get("family_envelopes", {}).values():
            self.evidence(family["evidence"])
        if native:
            self.evidence(native["evidence"])
        if runner_policy:
            self.evidence(runner_policy["qualification_evidence"])
        for job in state["control"].get("runner_jobs", {}).values():
            if job.get("receipt_sha256"):
                self.evidence({job["receipt"]:job["receipt_sha256"]})
        model_policy = state["control"].get("model_policy")
        if model_policy:
            self.evidence(model_policy["transport_evidence"])
        for job in state["control"].get("model_jobs", {}).values():
            if job.get("receipt_sha256"):
                self.evidence({job["receipt"]:job["receipt_sha256"]})
        if state["vault"].get("split_plan"):
            self.evidence(state["vault"]["split_plan"])
        if isolation:
            self.evidence(isolation["evidence"])
        if state["vault"].get("custody_evidence"):
            self.evidence(state["vault"]["custody_evidence"])
            self.evidence(state["vault"]["open_files"])
        if state["vault"].get("files"):
            self.evidence(state["vault"]["files"])

    def approval(self, s, req, action, target):
        key = req.get("approval_id")
        a = s["control"]["approvals"].get(key)
        require(a and not a["used"] and a["action"] == action and a["target"] == target,
                "Re's action/target-specific unused approval required")
        self.evidence(a["evidence"])
        require(a["request_sha256"] == digest({k: v for k, v in req.items() if k != "approval_id"}),
                "Approval does not bind this exact request")
        a["used"] = True
        return key

    def entry(self, s, id):
        found = [e for e in s["entries"] if e["id"] == id]
        require(len(found) == 1, "Unknown entry")
        return found[0]

    def apply(self, action, req):
        with self.lock():
            s, previous, seq = self.load()
            # Mutable owner-status receipts can legitimately change. Permit only
            # operator approval/queue repair through that specific drift; never
            # bypass frozen protocol, code, result or custody integrity checks.
            self.audit(s, queue_sources=action not in ("approve", "queue"))
            s = copy.deepcopy(s)
            result = self.transition(s, action, req)
            # Check finite and serializable values before committing any event.
            canonical(s)
            self.commit(s, action, previous, seq)
            return result

    def transition(self, s, action, q):
        b = s["budget"]
        if s["mode"] == "ACTIVE" and action in ("look", "freeze", "qualify", "score", "vault_access"):
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(b["started_utc"])).total_seconds()
            require(elapsed < b["max_wall_seconds"] and b["compute_spent"] < b["max_compute_units"]
                    and len(s["cycles"]) < b["max_cycles"], "T5 cap reached; run cycle to persist stop/report")
        if action == "approve":
            # Operator-only intake. OS ACLs must prevent workers calling the keeper.
            id = identifier(q["id"])
            require(id not in s["control"]["approvals"], "Decision id already used")
            require(q["actor"] == "Re" and q["written_ok"].strip(), "Written Re decision required")
            s["control"]["approvals"][id] = dict(action=q["action"], target=q["target"],
                request_sha256=q["request_sha256"], evidence=self.evidence(q["evidence"]),
                written_ok=q["written_ok"], utc=utc(), used=False)
            return id

        if action == "stage_custody":
            require(s["mode"] == "STAGED" and s["vault"]["status"] == "UNPROVISIONED", "One-shot custody staging only")
            evidence = self.evidence(q["evidence"])
            require(len(evidence) == 1, "One preparation receipt required")
            receipt = readjson(next(iter(evidence)))
            require(receipt["status"] == "PREPARED_UNSEALED" and receipt["file_level_exclusion_verified"] is True,
                    "Filtered corpus preparation must pass")
            s["vault"].update(status="PREPARED_UNSEALED", custody_evidence=evidence,
                open_files=self.evidence(receipt["open_files"]), files=self.evidence(receipt["vault_files"]))
            return "Custody staged; OS isolation still unqualified"

        if action == "configure":
            self.approval(s, q, action, "budget")
            require(not b["tests"], "Cannot reset statistical budget after testing")
            for key in ("max_cycles", "max_wall_seconds", "max_compute_units"):
                b[key] = number(q[key], 1)
            require(type(q["max_cycles"]) is int, "Integer cycle cap required")
            b["configuration"] = "RE_APPROVED"
            return "Configured finite operational caps; FDR settings unchanged"

        if action == "configure_runner":
            self.approval(s, q, action, "runner")
            require(s["mode"] == "STAGED", "Configure runner before activation")
            p = q["policy"]
            require(p["compute_unit"] == "reserved_worker_wall_seconds" and p["model_calls_enabled"] is False,
                    "Native worker unit must be explicit; model calls remain disabled")
            for key, lower in (("max_job_wall_seconds", 1), ("max_job_cpu_seconds", 1), ("memory_mb", 64), ("max_output_bytes", 1024)):
                number(p[key], lower)
            require(p["max_job_cpu_seconds"] <= p["max_job_wall_seconds"], "CPU allowance exceeds wall allowance")
            require(type(p["memory_mb"]) is int and type(p["max_output_bytes"]) is int, "Integer resource limits required")
            s["control"]["runner_policy"] = dict(policy=p, qualification_evidence=self.evidence(q["qualification_evidence"]), utc=utc())
            b["compute_unit"] = p["compute_unit"]
            return "Runner resource policy registered; loop remains staged and model calls disabled"

        if action == "record_native_qualification":
            require(s["mode"] == "STAGED", "Record setup qualification without activating")
            evidence = self.evidence(q["evidence"])
            records = [readjson(p) for p in evidence]
            statuses = {r.get("status") for r in records if isinstance(r, dict)}
            require({"PASS_PROCESS_BOUNDARIES", "PASS_NATIVE_RUNNER_CONTROLS", "PASS_CONTEXT_ONLY"} <= statuses,
                    "OS, runner fault controls, and offline context evidence required")
            s["control"]["native_worker_qualification"] = dict(evidence=evidence, utc=utc(),
                scope="Native Python workers and offline Codex context only; no model inference/Claude transport qualified")
            s["vault"]["native_worker_boundary"] = "OS_QUALIFIED"
            return "Native setup receipts recorded; loop remains STAGED and vault-wide model custody remains unsealed"

        if action == "configure_models":
            self.approval(s, q, action, "models")
            require(s["mode"] == "STAGED", "Configure models before activation")
            p = q["policy"]
            require(p["billing_mode"] == "existing_subscriptions_only" and p["additional_spend_usd"] == 0,
                    "New API/credit spending requires a separate authoritative billing integration")
            for key, lower in (("max_total_calls", 1), ("max_calls_per_cycle", 1), ("max_input_bytes", 1024),
                               ("max_output_bytes", 1024), ("wall_seconds", 1), ("cpu_seconds", 1), ("memory_mb", 64)):
                number(p[key], lower)
                require(type(p[key]) is int, "Integer model caps required")
            require(p["cpu_seconds"] <= p["wall_seconds"], "Model CPU exceeds wall allowance")
            providers = q["qualified_providers"]
            require(providers and set(providers) <= {"openai", "anthropic"} and set(p["models"]) == set(providers), "Explicit qualified providers/models required")
            evidence = self.evidence(q["transport_evidence"])
            receipts = [readjson(path) for path in evidence]
            require(all(any(r.get("status") == "PASS_NEUTRAL_MODEL_TRANSPORT" and r.get("provider") == provider for r in receipts) for provider in providers),
                    "Bounded neutral live transport qualification is still required per provider")
            require(all(isinstance(p["models"][v], str) and p["models"][v].strip() for v in providers), "Pin each model explicitly")
            require(set(p["credential_files"]) == set(providers), "Explicit minimum credential-file sources required")
            s["control"]["model_policy"] = dict(policy=p, qualified_providers=providers, transport_evidence=evidence, utc=utc())
            return "Model policy registered; loop remains STAGED"

        if action == "isolation":
            self.approval(s, q, action, "isolation")
            checks = ("worker_vault_read_denied", "worker_keeper_write_denied", "skeptic_sandbox_read_denied",
                      "network_denied", "fresh_context_verified", "all_roles_probed")
            require(all(q.get(k) is True for k in checks), "Every OS canary must pass")
            require(q.get("enforcement") in ("separate_os_principals", "deny_by_default_process_sandbox"),
                    "Filesystem isolation required")
            s["control"]["isolation"] = dict(evidence=self.evidence(q["evidence"]), checks=checks,
                enforcement=q["enforcement"], worker_principals=q["worker_principals"], utc=utc())
            return "Isolation receipts registered; deployment must match tested principals/profiles"

        if action == "vault":
            self.approval(s, q, action, "vault")
            require(s["control"]["isolation"], "Qualify filesystem isolation first")
            require(s["vault"]["status"] != "SEALED", "Vault registration is one-shot")
            files = self.evidence(q["files"])
            require(q["subsets"] and all(v["files"] for v in q["subsets"].values()), "Explicit subsets required")
            for name, subset in q["subsets"].items():
                identifier(name)
                require(all(p in files for p in subset["files"]), "Subset outside manifest")
                require(subset["exposure"] in ("FRESH_VERIFIED", "EXPOSED_OR_UNCERTIFIED"), "Exposure classification required")
                self.evidence(subset["custody_evidence"])
                subset["uses"] = []
            s["vault"].update(status="SEALED", files=files, subsets=q["subsets"], sealed_utc=utc())
            return "Sealed manifest registered; no content copied into project"

        if action == "activate":
            self.approval(s, q, action, "loop")
            require(s["mode"] == "STAGED", "Already active or ended")
            require(not s["control"].get("family_error_control_review_required", False),
                    "Hybrid family error-control amendment requires methodological review")
            require(not b.get("family_envelopes") or s["control"].get("family_claim_admission_ready") is True,
                    "Family claim-admission path is not qualified")
            require(s["control"]["isolation"] and s["vault"]["status"] == "SEALED", "Vault and role isolation not ready")
            require(b["configuration"] == "RE_APPROVED", "Finite budget needs approval")
            s["control"]["dependence_review"] = self.evidence(q["statistical_review"])
            require(q["historical_look_counts_certified"] is True, "Certify historical selection counts or bound conservatively")
            s["control"]["historical_look_counts_certified"] = True
            s["mode"] = "ACTIVE"
            b["started_utc"] = utc()
            return "Active; cycle command dispatch remains operator/runner owned"

        if action == "look":
            require(s["mode"] == "ACTIVE", "Exploratory work disabled while staged or stopped")
            id, lead = identifier(q["id"]), identifier(q["lead"])
            require(not any(e["id"] == id for e in s["entries"]), "Duplicate id")
            task = next((t for t in s["queue"] if t["id"] == q["task_id"]), None)
            require(task and task["status"] == "READY" and task["tier"] in ("exploratory", "descriptive"), "Task not executable")
            require(sum(e.get("lead") == lead and e["tier"] == "exploratory" for e in s["entries"]) < 20,
                    "20 looks: freeze or drop lead")
            s["entries"].append(dict(id=id, lead=lead, tier="exploratory", task_id=task["id"],
                result=q["result"], evidence=self.evidence(q["evidence"]), utc=utc(), held_up=False))
            return id

        if action == "drop_lead":
            self.approval(s, q, action, q["lead"])
            task = next((t for t in s["queue"] if t["id"] == q["task_id"]), None)
            require(task is not None, "Unknown task")
            task.update(status="PARKED", reason=q["reason"])
            return "Lead parked; all looks retained"

        if action == "freeze":
            require(s["mode"] == "ACTIVE", "Freeze disabled while staged/stopped")
            id = identifier(q["id"])
            require(not any(e["id"] == id for e in s["entries"]), "Duplicate id")
            require(not any(e["tier"] == "claim" and not e.get("closed") for e in s["entries"]),
                    "Resolve earlier claim before new freeze; statistical decisions are serialized")
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            require(sum(datetime.fromisoformat(t) >= cutoff for t in b["freezes"]) < 5, "Five freezes per rolling 30 days reached")
            p = q["protocol"]
            required = ("hypothesis_id", "lead", "estimand", "null", "analysis", "support", "controls",
                        "multiplicity", "selection_validity", "dependence_justification", "data_partition",
                        "code_entrypoint", "scorer_model_family", "spec_sources", "historical_related_looks")
            require(all(p.get(k) is not None and p[k] != "" for k in required), "Incomplete frozen protocol")
            require(p["data_partition"] in ("open", "fresh", "vault"), "Unknown data partition")
            require(p["data_partition"] != "vault", "Freeze open protocol first; vault run is separately authorized")
            number(p["historical_related_looks"], 0)
            require(type(p["historical_related_looks"]) is int, "Integer historical look bound required")
            self.evidence(p["spec_sources"])
            artifacts = self.evidence(q["artifacts"])
            require(Path(p["code_entrypoint"]).is_absolute() and p["code_entrypoint"] in artifacts,
                    "Code entrypoint must be sealed")
            level = lord_level(b)
            require(math.isclose(number(q["alpha"], 0, 1), level, rel_tol=1e-12, abs_tol=0), "Alpha must equal next LORD++ allocation")
            require(level <= b["alpha_wealth"] + 1e-12, "Alpha wealth exhausted")
            related = p["historical_related_looks"] + sum(e.get("lead") == p["lead"] and e["tier"] == "exploratory" for e in s["entries"])
            now = utc()
            doc = dict(protocol=p, alpha=level, related_sandbox_looks=related, artifacts=artifacts,
                       frozen_utc=now, environment=dict(python=sys.version, platform=platform.platform()))
            folder = self.root / "protocols" / id
            require(not folder.exists(), "Existing freeze folder; preserve failed attempt")
            folder.mkdir()
            writejson(folder / "PROTOCOL.json", doc)
            e = dict(id=id, hypothesis_id=p["hypothesis_id"], lead=p["lead"], tier="claim",
                protocol_sha256=filehash(folder / "PROTOCOL.json"), frozen_utc=now,
                artifacts=artifacts, alpha_spent=level, test_index=len(b["tests"]) + 1,
                related_sandbox_looks=related, qualification="PENDING", result="PENDING",
                skeptic="PENDING", re_decision=None, held_up=False, closed=False,
                scorer_model_family=p["scorer_model_family"], vault_runs=[], replication=None)
            s["entries"].append(e)
            b["alpha_wealth"] -= level
            b["tests"].append(dict(id=id, alpha=level, rejected=False, outcome="RESERVED"))
            b["freezes"].append(now)
            return dict(id=id, alpha=level, related_looks=related)

        if action in ("qualify", "score", "skeptic", "promote", "close", "vault_access", "replicate"):
            require(s["mode"] == "ACTIVE", "Claim processing disabled while staged/stopped")
            e = self.entry(s, q["id"])
            require(e["tier"] == "claim" and not e["closed"], "Not an open claim")
            require(q["protocol_sha256"] == e["protocol_sha256"], "Wrong frozen protocol hash")

            if action == "qualify":
                require(e["qualification"] == "PENDING", "Qualification is immutable")
                require(q["verdict"] in ("PASS", "BLOCKED"), "Invalid qualification verdict")
                require(q["real_support"] is True and q["null_and_recovery_controls"] is True,
                        "Controls at real support required")
                e["qualification"] = q["verdict"]
                e["qualification_evidence"] = self.evidence(q["evidence"])
                if q["verdict"] == "BLOCKED":
                    e["result"], e["closed"] = "BLOCKED", True
                    b["tests"][e["test_index"] - 1]["outcome"] = "BLOCKED_SPEND_RETAINED"
                return e["qualification"]

            if action == "score":
                require(e["qualification"] == "PASS" and e["result"] == "PENDING", "Qualified one-shot score required")
                require(q["model_family"] == e["scorer_model_family"], "Scorer family changed")
                require(q["result"] in ("SCORED", "NOT ESTIMABLE", "UNDERPOWERED", "BLOCKED"), "Invalid result")
                e["score_evidence"] = self.evidence(q["evidence"])
                p = q.get("p_value")
                if q["result"] == "SCORED":
                    number(p, 0, 1)
                    reject = p <= e["alpha_spent"]
                    e["result"] = "PASS" if reject else "NO PASS"
                else:
                    require(p is None, "Unsupported results must not have inferential p-values")
                    reject = False
                    e["result"] = q["result"]
                e["p_value"] = p
                test = b["tests"][e["test_index"] - 1]
                test.update(rejected=reject, outcome=e["result"])
                if reject:
                    # Statistical rejection earns; neither human acceptance nor unknown truth earns.
                    prior = sum(t["rejected"] for t in b["tests"][:e["test_index"] - 1])
                    b["alpha_wealth"] += b["fdr_target"] if prior else b["fdr_target"] - b["w0"]
                return e["result"]

            if action == "skeptic":
                require(e["result"] != "PENDING" and e["skeptic"] == "PENDING", "Score once before skeptic")
                require(q["model_family"] != e["scorer_model_family"], "Independent model family required in v1")
                require(q["verdict"] in ("CLEAR", "OBJECTION"), "Invalid skeptic verdict")
                require(q["blind_packet_only"] is True and q["related_look_count"] == e["related_sandbox_looks"],
                        "Skeptic must receive selection count and blind packet only")
                e["skeptic"], e["skeptic_model_family"] = q["verdict"], q["model_family"]
                e["skeptic_evidence"] = self.evidence(q["evidence"])
                return e["skeptic"]

            if action == "vault_access":
                self.approval(s, q, action, e["id"] + ":" + q["subset"])
                require(e["qualification"] == "PASS" and e["result"] == "PASS" and e["skeptic"] == "CLEAR",
                        "Qualified open pass and skeptic clear required before vault")
                subset = s["vault"]["subsets"].get(q["subset"])
                require(subset is not None, "Unknown vault subset")
                require(e["hypothesis_id"] not in subset["uses"], "Subset already used by hypothesis")
                require(q["replication_protocol_sha256"] == e["protocol_sha256"], "Replication protocol must already be frozen")
                frozen = readjson(self.root / "protocols" / e["id"] / "PROTOCOL.json")
                require(isinstance(frozen["protocol"].get("replication_rule"), dict), "Freeze replication rule before open score")
                subset["uses"].append(e["hypothesis_id"])
                e["vault_runs"].append(dict(subset=q["subset"], authorized_utc=utc(), outcome="AUTHORIZED_UNRUN"))
                return "Authorization consumed before access; a failed/crashed run still consumes subset"

            if action == "replicate":
                require(e["result"] == "PASS" and e["skeptic"] == "CLEAR" and e["replication"] is None,
                        "Independent replication only after open pass and review")
                self.approval(s, q, action, e["id"])
                frozen = readjson(self.root / "protocols" / e["id"] / "PROTOCOL.json")
                require(isinstance(frozen["protocol"].get("replication_rule"), dict), "Replication cannot be invented after open score")
                require(q["verdict"] in ("PASS", "NO PASS", "BLOCKED"), "Invalid replication result")
                require(q["source"] in ("vault", "fresh"), "Independent data required")
                if q["source"] == "vault":
                    run = next((r for r in e["vault_runs"] if r["subset"] == q["subset"]), None)
                    require(run and run["outcome"] == "AUTHORIZED_UNRUN", "Authorize vault access first")
                    subset = s["vault"]["subsets"][q["subset"]]
                    require(subset["exposure"] == "FRESH_VERIFIED", "Exposed/uncertified reserve cannot certify replication")
                    run["outcome"] = q["verdict"]
                require(q["pre_split_never_touched"] is True and q["frozen_decision_rule"] is True,
                        "Presplit independent material and frozen replication rule required")
                e["replication_evidence"] = self.evidence(q["evidence"])
                e["replication"] = dict(verdict=q["verdict"], source=q["source"], subset=q.get("subset"),
                    pre_split_never_touched=True, custody_evidence=self.evidence(q["custody_evidence"]))
                return q["verdict"]

            if action == "promote":
                approval = self.approval(s, q, action, e["id"])
                require(e["result"] == "PASS" and e["qualification"] == "PASS", "Only qualified claim-tier PASS can be held up")
                require(e["skeptic"] == "CLEAR", "Unresolved skeptic objection blocks promotion")
                if e["related_sandbox_looks"] > 50:
                    require(e["replication"] and e["replication"]["verdict"] == "PASS", ">50 related looks requires independent replication")
                e.update(held_up=True, closed=True, re_decision=approval)
                return "HELD UP"

            if action == "close":
                require(e["result"] != "PENDING", "Cannot silently abandon a scored slot")
                self.approval(s, q, action, e["id"])
                e["closed"] = True
                e["closure_reason"] = q["reason"]
                if e["skeptic"] == "OBJECTION":
                    s["mode"] = "PAUSED_REVIEW"
                return "Closed; original test spend/reward retained; objection pauses statistical stream"

        if action == "queue":
            self.approval(s, q, action, "queue")
            require(len(q["tasks"]) <= 3, "Planner proposes at most three tasks")
            for task in q["tasks"]:
                identifier(task["id"])
                self.evidence(task["sources"])
                require(task["status"] in ("READY", "BLOCKED", "PARKED", "COMPLETE"), "Invalid task state")
                require(task["id"] not in ("v103", "rosettes-leaveout", "ey-blocking", "letter-substitution"), "Closed or parked by source design")
                number(task["expected_information"], 0)
                number(task["cost"], 1e-12)
                task["priority"] = task["expected_information"] / task["cost"]
                old = next((t for t in s["queue"] if t["id"] == task["id"]), None)
                if old:
                    s["queue"].remove(old)
                s["queue"].append(task)
            s["queue"].sort(key=lambda t: -t.get("priority", 0))
            return "Queue updated from operator-reviewed planner proposal"

        if action == "cycle":
            # Caller/runner supplies measured usage. Paused setup never becomes exhaustion.
            if s["mode"] != "ACTIVE":
                return dict(mode=s["mode"], executed=False, reason="Setup/review/end-state gate")
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(b["started_utc"])).total_seconds()
            b["compute_spent"] += number(q.get("compute_units", 0), 0)
            b["active_wall_seconds"] = elapsed
            promoted = sum(e.get("held_up", False) for e in s["entries"])
            c = s["control"]
            c["no_claim_cycles"] = 0 if promoted > c["last_promoted_count"] else c["no_claim_cycles"] + 1
            c["last_promoted_count"] = promoted
            s["cycles"].append(dict(utc=utc(), promoted_total=promoted, compute_units=q.get("compute_units", 0)))
            pending = any(e["tier"] == "claim" and not e.get("closed") for e in s["entries"])
            if len(s["cycles"]) >= b["max_cycles"] or elapsed >= b["max_wall_seconds"] or b["compute_spent"] >= b["max_compute_units"]:
                s["mode"], s["end_state"] = "PAUSED_BUDGET", "T5"
            elif pending or (not any(t["status"] == "READY" for t in s["queue"]) and any(t["status"] == "BLOCKED" for t in s["queue"])):
                # Waiting cycles are not 30 unsuccessful research cycles.
                c["no_claim_cycles"] = max(0, c["no_claim_cycles"] - 1)
                s["mode"] = "PAUSED_REVIEW"
            elif c["no_claim_cycles"] >= 30 or b["alpha_wealth"] <= 1e-15 or not any(t["status"] in ("READY", "BLOCKED") for t in s["queue"]):
                s["mode"], s["end_state"] = "STOPPED", "T4"
            return dict(mode=s["mode"], end_state=s["end_state"], executed=False,
                        reason="Accounting checkpoint; runner executes separate role jobs")

        if action == "end":
            target = q["end_state"]
            require(target in ("T1", "T2", "T3"), "T4/T5 are automatic")
            self.approval(s, q, action, target)
            self.evidence(q["evidence"])
            if target == "T1":
                require(q["surviving_families"] in (1, 2) and q["eliminated_families"] >= 3 and
                        q["hf_agree"] is True and q["recovery_pass"] is True and q["skeptic_clear"] is True,
                        "T1 criteria not met")
            else:
                e = self.entry(s, q["id"])
                require(e["held_up"] and e["replication"] and e["replication"]["verdict"] == "PASS", "Held-up independent replication required")
                require(q["class"] in (("v6-T1", "v6-T2") if target == "T2" else ("value-mapping",)), "Wrong end-state class")
                if target == "T3":
                    require(q["beats_every_control_on_heldout"] is True, "T3 must beat all frozen controls")
            s["end_state"], s["mode"] = target, "STOPPED"
            return target

        if action == "resume":
            self.approval(s, q, action, "loop")
            require(s["mode"] == "PAUSED_REVIEW" and s["end_state"] is None, "T4/T5/ended runs need a new approved epoch, not silent reset")
            s["mode"] = "ACTIVE"
            return "Resumed"

        raise GateError("Unknown action")

    def report(self):
        with self.lock():
            s, _, _ = self.load()
            self.audit(s)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            # Reports use exact UTC stamps; scheduler supplies user's local daily date.
            text = (f"# Voynich loop report\n\nUTC: {utc()}\n\nMode: {s['mode']}; end state: {s['end_state'] or 'none'}.\n\n"
                    f"Completed checkpoints: {len(s['cycles'])}; claim slots: {len(s['budget']['tests'])}; "
                    f"held up: {sum(e.get('held_up', False) for e in s['entries'])}.\n\n"
                    f"Alpha wealth: {s['budget']['alpha_wealth']:.12g}; next LORD++ level: {lord_level(s['budget']):.12g}.\n\n"
                    f"Vault: {s['vault']['status']}. Role isolation: {'registered' if s['control']['isolation'] else 'unqualified'}.\n\n"
                    "No decipherment is inferred from operational status or a statistical rejection.\n\n"
                    "## Queue\n\n" + "\n".join(f"- {t['id']}: {t['status']} — {t['reason']}" for t in s['queue']) + "\n")
            path = self.root / ("reports" if s["end_state"] else "digests") / (stamp + ".md")
            path.write_text(text, encoding="utf-8")
            return str(path)

    def skeptic_packet(self, id):
        """One fresh input folder; no sandbox logs, ledger, memories or lead reports."""
        with self.lock():
            s, _, _ = self.load()
            self.audit(s)
            e = self.entry(s, identifier(id))
            require(e["tier"] == "claim" and e["result"] != "PENDING", "Score before packaging skeptic input")
            folder = self.root / "packets" / ("skeptic-" + id)
            require(not folder.exists(), "Packet already exists; do not overwrite")
            folder.mkdir()
            import shutil
            shutil.copyfile(self.root / "protocols" / id / "PROTOCOL.json", folder / "PROTOCOL.json")
            for category, files in (("code", e["artifacts"]), ("qualification", e["qualification_evidence"]),
                                    ("score", e["score_evidence"])):
                for i, src in enumerate(sorted(files)):
                    shutil.copyfile(src, folder / f"{category}-{i:03d}{Path(src).suffix}")
            writejson(folder / "TASK.json", dict(role="skeptic", id=id, protocol_sha256=e["protocol_sha256"],
                related_sandbox_looks=e["related_sandbox_looks"], scorer_model_family=e["scorer_model_family"],
                instruction="Find confounds, leakage, bugs and selection effects. Use only this packet. Return CLEAR or OBJECTION with evidence; you cannot promote."))
            manifest = {p.name: filehash(p) for p in folder.iterdir()}
            writejson(folder / "PACKET-MANIFEST.json", manifest)
            return str(folder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("action", choices=("status", "verify", "recover", "report", "approve", "stage_custody", "configure", "configure_runner", "configure_models", "record_native_qualification", "isolation", "vault",
        "activate", "look", "drop_lead", "freeze", "qualify", "score", "skeptic", "promote", "close", "vault_access", "replicate", "queue", "cycle", "end", "resume", "skeptic_packet"))
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    store = Store(args.root)
    try:
        if args.action == "recover":
            with store.lock():
                s, _, _ = store.load(projections=False)
                store.audit(s)
                store.render(s)
            result = "Projections recovered from intact journal"
        elif args.action == "skeptic_packet":
            require(args.request is not None, "Request with id required")
            result = store.skeptic_packet(readjson(args.request)["id"])
        elif args.action == "report":
            result = store.report()
        elif args.action in ("status", "verify"):
            with store.lock():
                s, h, seq = store.load()
                store.audit(s)
            result = dict(mode=s["mode"], end_state=s["end_state"], events=seq, head=h,
                          vault=s["vault"]["status"], next_alpha=lord_level(s["budget"]),
                          claims=len(s["budget"]["tests"]), note="Ledger integrity verified; this is not OS isolation qualification")
        else:
            require(args.request is not None or args.action == "cycle", "--request JSON required")
            result = store.apply(args.action, readjson(args.request) if args.request else {})
            if args.action in ("cycle", "end"):
                store.report()
        print(json.dumps(result, indent=2))
    except (GateError, OSError, KeyError, TypeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
