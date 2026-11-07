"""Dormant Codex/Claude CLI proposal transport, owned by the keeper.

This is NOT an OS-isolated analysis worker. Models get packet text and no
authority to execute code/admit results. Native analysis uses runner.py.
No live inference is allowed without ACTIVE state, approved call caps and
provider-specific transport/billing qualification evidence.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import uuid
from audit_model_context import config
from isolation import WindowsJob, environment, flags, checked_tree, ROLES
from loop import Store, require, GateError, filehash, readjson, writejson, identifier, utc, digest


def command_for(provider, exe, packet, control, model):
    require(provider in ("openai", "anthropic") and isinstance(model, str) and model.strip(), "Explicit provider/model required")
    if provider == "openai":
        return [str(exe), "--no-daemon", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
                "--json", "--color", "never", "--model", model, *flags(config(packet, control / "tool-output")), "--", "-"]
    return [str(exe), "--print", "--output-format", "json", "--model", model,
            "--tools", "", "--permission-mode", "dontAsk", "--setting-sources", "",
            "--mcp-config", "{}", "--strict-mcp-config", "--disable-slash-commands", "--session-id", str(uuid.uuid4()),
            "--system-prompt", "Work only from the supplied task packet. Return a proposal or review. You have no tools. Do not infer or claim access to omitted data."]


def check_response(provider, stdout):
    """Reject incomplete turns, invalid streams and attempted tool operations."""
    if provider == "anthropic":
        value = json.loads(stdout)
        require(value.get("type") == "result" and not value.get("is_error") and isinstance(value.get("result"), str), "Claude turn incomplete/error")
        require(not value.get("tool_use"), "Tool-use response rejected")
        return value["result"]
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    require(any(e.get("type") == "turn.completed" for e in events), "Codex turn incomplete")
    allowed_items = {"agent_message", "reasoning", "plan"}
    for event in events:
        item = event.get("item")
        if item:
            require(item.get("type") in allowed_items, "Model attempted a tool operation; result ineligible")
    texts = [e["item"].get("text", "") for e in events if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "agent_message"]
    require(texts, "No final proposal")
    return texts[-1]


class ModelBroker:
    def __init__(self, root):
        self.store = Store(root); self.root = self.store.root

    def run(self, request):
        with self.store.lock():
            s, previous, seq = self.store.load(); self.store.audit(s)
            require(s["mode"] == "ACTIVE" and s["end_state"] is None, "MODEL DISPATCH DISABLED: loop remains inactive")
            require(s["control"].get("isolation") and s["vault"]["status"] == "SEALED", "Full registered model/custody boundary required")
            record = s["control"].get("model_policy")
            require(record, "Re-approved model caps and qualified transport are missing")
            p = record["policy"]
            from datetime import datetime, timezone
            require(len(s["cycles"]) < s["budget"]["max_cycles"], "Cycle cap reached")
            require((datetime.now(timezone.utc) - datetime.fromisoformat(s["budget"]["started_utc"])).total_seconds()
                    + p["wall_seconds"] <= s["budget"]["max_wall_seconds"], "Insufficient remaining calendar-time reservation")
            self.store.evidence(record["transport_evidence"])
            provider = request["provider"]
            require(provider in p["models"] and provider in record["qualified_providers"], "Provider transport not qualified")
            require(request["role"] in ROLES, "Unknown role")
            id = identifier(request["id"])
            require(id not in s["control"].get("model_jobs", {}), "Model job already attempted")
            jobs = s["control"].get("model_jobs", {})
            cycle = len(s["cycles"])
            require(len(jobs) < p["max_total_calls"] and sum(j["cycle"] == cycle for j in jobs.values()) < p["max_calls_per_cycle"], "Model call cap exhausted")
            require(p["billing_mode"] == "existing_subscriptions_only" and p["additional_spend_usd"] == 0,
                    "This broker cannot enforce new API/credit dollar spending; separate billing integration required")
            packet = Path(request["packet"]).resolve()
            require(packet.parent == self.root / "packets" and packet.name == "model-" + request["role"] + "-" + id, "Keeper-prepared role packet required")
            require(checked_tree(packet) == request["packet_files"], "Model packet drift")
            if request["role"] in ("scorer", "qualifier", "skeptic"):
                claim = self.store.entry(s, request["claim_id"])
                require(claim["tier"] == "claim" and not claim["closed"], "Open claim required")
                require(request["protocol_sha256"] == claim["protocol_sha256"], "Frozen model-task protocol mismatch")
                if request["role"] == "scorer":
                    require(provider == claim["scorer_model_family"] and claim["qualification"] == "PASS" and claim["result"] == "PENDING", "Qualified pending scorer/model family required")
                if request["role"] == "skeptic":
                    require(provider != claim["scorer_model_family"] and claim["result"] != "PENDING" and claim["skeptic"] == "PENDING", "Scored result and different skeptic family required")
            chunks = []
            total_bytes = 0
            for name in sorted(request["packet_files"]):
                path = packet / name
                require(path.suffix.lower() in (".json", ".md", ".txt", ".py", ".csv"), "Text-only model packet required")
                data = path.read_bytes(); total_bytes += len(data)
                require(total_bytes <= p["max_input_bytes"], "Model input-size cap exceeded")
                chunks.append(dict(name=name, content=data.decode("utf-8-sig")))
            prompt = json.dumps(dict(role=request["role"], task=request["task"], packet=chunks,
                authority="Proposals only. Do not execute code, claim access to omitted files, score unfrozen tests or promote results."), ensure_ascii=False).encode()
            require(len(prompt) <= p["max_input_bytes"], "Serialized model request exceeds input cap")
            base = self.root / "model-runs" / id
            require(not base.exists(), "Existing attempt directory")
            base.mkdir(parents=True)
            runtime = base / "runtime"; runtime.mkdir()
            (base / "tool-output").mkdir()
            exe = Path(shutil.which("codex" if provider == "openai" else "claude") or "").resolve()
            require(exe.is_file(), "Provider CLI unavailable")
            command = command_for(provider, exe, packet, base, p["models"][provider])
            job_record = dict(id=id, provider=provider, role=request["role"], cycle=cycle, status="RESERVED",
                utc=utc(), request_sha256=digest(request), prompt_sha256=__import__("hashlib").sha256(prompt).hexdigest(),
                executable_sha256=filehash(exe), broker_sha256=filehash(Path(__file__)))
            s = copy.deepcopy(s); s["control"].setdefault("model_jobs", {})[id] = job_record
            self.store.commit(s, "model_reserve", previous, seq)
            env = environment(runtime, base)
            env.pop("CODEX_HOME", None)
            env["CODEX_HOME" if provider == "openai" else "CLAUDE_CONFIG_DIR"] = str(runtime)
            # Only a minimum credential file is provisioned, after reservation.
            # No credential, config or past conversation enters the model packet.
            source = Path(p["credential_files"][provider])
            auth = runtime / ("auth.json" if provider == "openai" else ".credentials.json")
            outcome = {"status":"FAILED", "failure":None}
            job = None; proc = None
            try:
                require(source.is_file() and not source.is_symlink() and source.stat().st_size <= 2 * 1024 * 1024,
                        "Minimum bounded credential file required")
                shutil.copyfile(source, auth)
                job = WindowsJob(p["memory_mb"] * 1024 * 1024, p["cpu_seconds"])
                with (base / "stdout.txt").open("wb") as out, (base / "stderr.txt").open("wb") as err:
                    proc = subprocess.Popen(command, cwd=packet, env=env, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                            creationflags=0x4 | 0x08000000)
                    job.attach_and_resume(proc)
                    def feed():
                        try:
                            proc.stdin.write(prompt); proc.stdin.close()
                        except (OSError, ValueError): pass
                    feeder = threading.Thread(target=feed, daemon=True); feeder.start()
                    deadline = time.monotonic() + p["wall_seconds"]
                    while proc.poll() is None:
                        require(time.monotonic() < deadline, "MODEL_TIMEOUT")
                        require(sum((base / n).stat().st_size for n in ("stdout.txt", "stderr.txt")) <= p["max_output_bytes"], "MODEL_OUTPUT_LIMIT")
                        time.sleep(.05)
                    require(proc.returncode == 0, "Provider CLI failed")
                require(sum((base / n).stat().st_size for n in ("stdout.txt", "stderr.txt")) <= p["max_output_bytes"], "MODEL_OUTPUT_LIMIT")
                proposal = check_response(provider, (base / "stdout.txt").read_text(encoding="utf-8"))
                (base / "PROPOSAL.txt").write_text(proposal, encoding="utf-8")
                require(checked_tree(packet) == request["packet_files"], "Model packet changed")
                outcome["status"] = "COMPLETED_PENDING_KEEPER_REVIEW"
            except Exception as exc:
                outcome["failure"] = type(exc).__name__ + ": " + str(exc)
            finally:
                if job: job.close()
                if proc:
                    try: proc.wait(timeout=5)
                    except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
                if auth.exists():
                    try: auth.unlink()
                    except OSError as exc:
                        outcome.update(status="FAILED_CREDENTIAL_CLEANUP", failure=type(exc).__name__ + ": exact credential copy could not be removed")
            outcome.update(utc_finished=utc(), credential_copy_removed=not auth.exists(),
                scope="Trusted CLI transport only. This is not native worker OS-isolation qualification or scientific result admission.")
            writejson(base / "RECEIPT.json", outcome)
            s, previous, seq = self.store.load()
            s["control"]["model_jobs"][id].update(outcome, receipt=str(base / "RECEIPT.json"), receipt_sha256=filehash(base / "RECEIPT.json"))
            self.store.commit(s, "model_complete", previous, seq)
            return outcome


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(ModelBroker(Path(__file__).resolve().parent).run(readjson(args.request)), indent=2))
    except (GateError, KeyError, OSError) as exc:
        print("BLOCKED: " + str(exc)); raise SystemExit(2)
