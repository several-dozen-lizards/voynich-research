"""One-job keeper runner. Research dispatch remains forbidden while STAGED.

Worker programs are sealed Python capsules; model output is never executed or
promoted implicitly. This does not start a daily cycle or register a schedule.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import shutil
import time
from isolation import ROLES, checked_tree, execute
from loop import Store, GateError, identifier, require, filehash, readjson, writejson, utc, digest, number


def safe_relative(name):
    path = Path(name)
    require(not path.is_absolute() and path.parts and all(p not in ("..", ".") for p in path.parts)
            and ":" not in name and "\\" not in name, "Unsafe packet-relative name")
    return path


def validated_policy(policy):
    require(policy["compute_unit"] == "reserved_worker_wall_seconds", "Explicit conservative compute unit required")
    for key, low in (("max_job_wall_seconds", 1), ("max_job_cpu_seconds", 1), ("memory_mb", 64),
                     ("max_output_bytes", 1024)):
        number(policy[key], low)
    require(policy["max_job_cpu_seconds"] <= policy["max_job_wall_seconds"], "CPU allowance exceeds wall allowance")
    require(type(policy["memory_mb"]) is int and type(policy["max_output_bytes"]) is int, "Integer resource limits required")
    require(policy.get("model_calls_enabled") is False, "This native runner does not make model calls")
    return policy


class Runner:
    def __init__(self, root):
        self.store = Store(root)
        self.root = self.store.root

    def validate_request(self, state, request):
        require(state["mode"] == "ACTIVE" and state["end_state"] is None,
                "RESEARCH DISPATCH DISABLED: loop must remain inactive until explicit activation")
        policy_record = state["control"].get("runner_policy")
        require(policy_record, "Approved runner resource policy is missing")
        policy = validated_policy(policy_record["policy"])
        require(state["control"].get("isolation") and state["vault"]["status"] == "SEALED", "Registered sealed boundary required")
        qualification = readjson(self.root / "WORKER-ISOLATION.json")
        require(qualification["status"] == "PASS_PROCESS_BOUNDARIES", "Native boundary qualification missing")
        require(qualification["worker_code_sha256"] == filehash(self.root / "isolation.py"), "Boundary code changed; requalify")
        require(qualification["qualifier_sha256"] == filehash(self.root / "qualify_workers.py"), "Canary qualification changed; requalify")
        require(len(qualification["roles"]) == len(ROLES) and all(r["status"] == "PASS" for r in qualification["roles"]), "Every role must qualify")
        for role in qualification["roles"]:
            require(filehash(role["receipt"]) == role["receipt_sha256"], "Boundary receipt drift")
        role = request["role"]
        require(role in ROLES, "Unknown role; keeper is never a worker")
        identifier(request["id"])
        require(request["id"] not in state["control"].get("runner_jobs", {}), "Job already attempted; preserve failures")
        b = state["budget"]
        require(b["configuration"] == "RE_APPROVED" and all(b[k] is not None for k in ("max_compute_units", "max_cycles", "max_wall_seconds")), "Finite approved budget missing")
        from datetime import datetime, timezone
        require((datetime.now(timezone.utc) - datetime.fromisoformat(b["started_utc"])).total_seconds()
                + policy["max_job_wall_seconds"] <= b["max_wall_seconds"], "Insufficient remaining wall-time reservation")
        require(b["compute_spent"] + policy["max_job_wall_seconds"] <= b["max_compute_units"], "Insufficient remaining compute reservation")
        require(len(state["cycles"]) < b["max_cycles"], "Cycle cap reached")
        claim = None
        if role in ("qualifier", "scorer", "skeptic"):
            claim = self.store.entry(state, request["claim_id"])
            require(claim["tier"] == "claim" and not claim["closed"], "Open claim required")
            require(request["protocol_sha256"] == claim["protocol_sha256"], "Frozen protocol mismatch")
            if role == "qualifier": require(claim["qualification"] == "PENDING", "Qualification already consumed")
            if role == "scorer": require(claim["qualification"] == "PASS" and claim["result"] == "PENDING", "One-shot qualified score required")
            if role == "skeptic": require(claim["result"] != "PENDING" and claim["skeptic"] == "PENDING", "Score before independent review")
            key = role + ":" + claim["id"]
            require(key not in state["control"].get("runner_claim_attempts", {}), "Claim role already attempted, including failed attempts")
        elif role in ("sandbox", "freezer"):
            task = next((t for t in state["queue"] if t["id"] == request["task_id"]), None)
            require(task and task["status"] == "READY", "Task is not ready")
            identifier(request["lead"])
            if role == "sandbox":
                require(task["tier"] in ("exploratory", "descriptive"), "Sandbox cannot execute claim-tier task")
                looks = sum(e.get("lead") == request["lead"] and e["tier"] == "exploratory" for e in state["entries"])
                require(looks < 20, "Lead reached 20 logged looks")
        return policy, claim

    def stage_packet(self, state, request, folder):
        """Explicit keeper-approved inputs, never a whole project working directory."""
        folder.mkdir(parents=True)
        role = request["role"]
        # Code stays keeper-owned until reviewed and placed in worker-code/.
        code_root = self.root / "worker-code"
        allowed = [code_root]
        if role == "sandbox": allowed.append(self.root / "open-data")
        if role in ("qualifier", "scorer"):
            claim = self.store.entry(state, request["claim_id"])
            allowed.extend([self.root / "protocols" / claim["id"], self.root / "open-data"])
        if role == "skeptic": allowed = [code_root, self.root / "packets" / ("skeptic-" + request["claim_id"])]
        if role == "freezer": allowed.append(self.root / "results" / identifier(request["lead"]))
        supplied = request.get("files", {})
        require(supplied and len(supplied) <= 1000, "Explicit bounded packet files required")
        for name, item in supplied.items():
            dest = folder / safe_relative(name)
            src = Path(item["path"]).resolve()
            require(src.is_file() and not src.is_symlink() and src.stat().st_nlink == 1, "Input must be a regular unlinked file")
            require(any(src.is_relative_to(p.resolve()) for p in allowed),
                    "Role cannot ingest this source; no vault, original corpus, history or other-role inputs")
            require(filehash(src) == item["sha256"], "Input hash mismatch")
            dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dest)
        if role == "planner":
            # Deliberately omit evidence paths, word sequences, code, private approvals and history.
            writejson(folder / "PLANNER-STATE.json", dict(tasks=[{k:t.get(k) for k in ("id", "tier", "status", "reason", "priority")} for t in state["queue"]],
                results=[{k:e.get(k) for k in ("id", "tier", "result", "qualification", "held_up")} for e in state["entries"]],
                next_alpha=__import__("loop").lord_level(state["budget"]), instruction="Propose at most three tasks; do not run analyses."))
        entry = folder / safe_relative(request["entrypoint"])
        require(entry.is_file() and entry.suffix == ".py", "Sealed Python entrypoint required")
        if role in ("qualifier", "scorer"):
            require(filehash(entry) in set(claim["artifacts"].values()), "Execution code was not included in the freeze")
        writejson(folder / "ROLE.json", dict(role=role, job_id=request["id"], output_directory=str(folder.parent / "output"),
            authority="Emit proposal/evidence only. Keeper alone admits results, freezes protocols and promotes claims."))
        return entry

    def run(self, request):
        # Lock covers reservation through completion: other workers cannot race the budget.
        with self.store.lock():
            state, previous, seq = self.store.load(); self.store.audit(state)
            policy, claim = self.validate_request(state, request)
            root = self.root / "worker-runs" / request["id"]
            require(not root.exists(), "Existing run directory; never overwrite")
            entry = self.stage_packet(state, request, root / "input")
            state = copy.deepcopy(state)
            job = dict(role=request["role"], id=request["id"], status="RESERVED", utc=utc(),
                request_sha256=digest(request), input_files=checked_tree(root / "input"),
                compute_reserved=policy["max_job_wall_seconds"], compute_unit=policy["compute_unit"])
            state["control"].setdefault("runner_jobs", {})[request["id"]] = job
            if claim:
                state["control"].setdefault("runner_claim_attempts", {})[request["role"] + ":" + claim["id"]] = request["id"]
            if request["role"] == "sandbox":
                state["entries"].append(dict(id="E-" + request["id"], tier="exploratory", lead=request["lead"],
                    task_id=request["task_id"], result="RUN_RESERVED", held_up=False, utc=utc()))
            state["budget"]["compute_spent"] += policy["max_job_wall_seconds"]
            self.store.commit(state, "runner_reserve", previous, seq)
            # Reservation survives keeper crash, failed execution and restart. No automatic refund.
            denied = {"keeper": str(self.root / "loop.py"), "full_corpus": str(self.root.parent / "complete-atlas-v56/ROWS.json"),
                      "vault": str(Path(next(iter(state["vault"]["files"]))).parent / "BOUNDARY-CANARY.txt")}
            try:
                receipt = execute(root / "input", root / "output", root / "control", entry,
                    wall_seconds=policy["max_job_wall_seconds"], cpu_seconds=policy["max_job_cpu_seconds"],
                    memory_mb=policy["memory_mb"], max_output_bytes=policy["max_output_bytes"], denied_paths=denied)
            except Exception as exc:
                receipt = dict(status="FAILED_KEEPER_EXCEPTION", failure=type(exc).__name__ + ": " + str(exc), utc=utc())
                writejson(root / "FAILED.json", receipt)
            state, previous, seq = self.store.load()
            job = state["control"]["runner_jobs"][request["id"]]
            job.update(status="COMPLETED_PENDING_KEEPER_REVIEW" if receipt["status"] == "PASS" else "FAILED",
                finished_utc=utc(), receipt=str(root / "control/RECEIPT.json") if (root / "control/RECEIPT.json").exists() else str(root / "FAILED.json"))
            job["receipt_sha256"] = filehash(job["receipt"])
            if request["role"] == "sandbox":
                e = self.store.entry(state, "E-" + request["id"])
                e.update(result=job["status"], evidence={job["receipt"]:job["receipt_sha256"]})
            self.store.commit(state, "runner_complete", previous, seq)
            return job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "run"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    runner = Runner(args.root)
    try:
        if args.action == "status":
            state, _, _ = runner.store.load()
            result = dict(mode=state["mode"], research_dispatch_enabled=state["mode"] == "ACTIVE", model_calls_enabled=False,
                isolation=readjson(runner.root / "WORKER-ISOLATION.json")["status"] if (runner.root / "WORKER-ISOLATION.json").exists() else "UNQUALIFIED",
                policy=state["control"].get("runner_policy"), note="One-shot native Python role jobs; no schedule or model inference is activated")
        else:
            require(args.request is not None, "Request required")
            result = runner.run(readjson(args.request))
        print(json.dumps(result, indent=2)); return 0
    except (GateError, KeyError, OSError, ValueError) as exc:
        print("BLOCKED: " + str(exc)); return 2


if __name__ == "__main__":
    raise SystemExit(main())
