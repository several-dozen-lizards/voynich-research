"""Verify ledger integrity, actual corpus custody partition, and synthetic gates."""
import io
import json
import sys
import unittest
from pathlib import Path
from bootstrap import candidate_split
from loop import Store, filehash, readjson, require, utc, writejson


def main():
    root = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(root), pattern="test_*.py")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    run_dir = root / "verification-runs"
    run_dir.mkdir(exist_ok=True)
    (run_dir / (utc().replace(":", "-") + ".txt")).write_text(stream.getvalue(), encoding="utf-8")
    (root / "TEST-RESULTS.txt").write_text(stream.getvalue(), encoding="utf-8")
    require(result.wasSuccessful(), "Synthetic test failure; see TEST-RESULTS.txt")
    native = readjson(root / "WORKER-ISOLATION.json")
    faults = readjson(root / "RUNNER-QUALIFICATION.json")
    context = readjson(root / "MODEL-CONTEXT-AUDIT.json")
    require(native["status"] == "PASS_PROCESS_BOUNDARIES" and native["worker_code_sha256"] == filehash(root / "isolation.py"), "Native boundary missing or stale")
    require(faults["status"] == "PASS_NATIVE_RUNNER_CONTROLS" and faults["isolation_code_sha256"] == filehash(root / "isolation.py")
            and faults["runner_code_sha256"] == filehash(root / "runner.py"), "Runner controls missing or stale")
    require(context["status"] == "PASS_CONTEXT_ONLY" and context["adapter_code_sha256"] == filehash(root / "audit_model_context.py"), "Offline model context audit missing or stale")
    for item in native["roles"] + faults["results"]:
        require(filehash(item["receipt"]) == item["receipt_sha256"], "Native qualification receipt changed")
    for item in context["roles"]:
        require(filehash(item["rendered"]) == item["rendered_sha256"], "Rendered context changed")
    store = Store(root)
    state, head, seq = store.load()
    store.audit(state)
    plan = readjson(root / "SPLIT-PLAN.json")
    source = root.parent / "complete-atlas-v56/ROWS.json"
    require(plan == candidate_split(source), "Split not reproducible")
    custody = readjson(root / "CUSTODY-PREPARATION.json")
    rows = readjson(source)
    opened = readjson(next(iter(custody["open_files"])))
    vault = {Path(p).stem: readjson(p) for p in custody["vault_files"]}
    excluded = set(plan["reserved_zodiac_folios"]) | {r["folio"] for r in plan["folios"] if r["partition"] == "candidate_reserve"}
    require(opened == [r for r in rows if r[1] not in excluded], "Open file differs from frozen exclusion")
    require(sum(custody["counts"].values()) == len(rows), "Partition lost or duplicated rows")
    for name, part in vault.items():
        allowed = set(plan["reserved_zodiac_folios"]) if name == "zodiac" else excluded - set(plan["reserved_zodiac_folios"])
        require(part == [r for r in rows if r[1] in allowed], "Vault file differs from frozen partition")
    artifact_names = ["loop.py", "bootstrap.py", "prepare_corpus.py", "test_loop.py", "verify.py", "README.md",
                      "runner.py", "isolation.py", "qualify_workers.py", "qualify_runner.py", "test_runner.py", "audit_model_context.py",
                      "model_broker.py", "test_model_broker.py",
                      "family_budget.py", "test_family_budget.py",
                      "DEPLOYMENT.md", "RE-INPUTS.json",
                      "STATISTICAL-NOTES.md", "ORIGINAL-SPEC.md", "SPLIT-PLAN.json", "CUSTODY-PREPARATION.json", "TEST-RESULTS.txt"]
    record = dict(status="PASS_STAGED_CONTROL_AND_CORPUS_CHECKS", utc=utc(),
        synthetic_tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
        ledger_events=seq, ledger_head=head, mode=state["mode"], vault_status=state["vault"]["status"],
        corpus_counts=custody["counts"], source_rows=len(rows),
        source_hash_unchanged=filehash(source) == plan["source_sha256"],
        actual_file_partitions_exact=True, split_reproducible=True,
        alpha_spent=sum(t["alpha"] for t in state["budget"]["tests"])+state["budget"].get("family_fwer_reserved",0),
        online_alpha_spent=sum(t["alpha"] for t in state["budget"]["tests"]),
        family_alpha_reserved=state["budget"].get("family_fwer_reserved",0),
        os_isolation_qualified=readjson(root / "WORKER-ISOLATION.json")["status"] == "PASS_PROCESS_BOUNDARIES",
        native_worker_runner_implemented=True, native_role_profiles=len(native["roles"]), native_fault_controls=len(faults["results"]),
        offline_model_contexts=len(context["roles"]), dormant_model_transports_implemented=True, model_inference_qualified=False,
        autonomous_runner_implemented=False, schedule_active=False,
        historical_replication_reserve_certified=False,
        initial_test_environment_issue="OS sandbox TEMP denied atomic rename; fixtures moved into workspace. A later transient Windows sharing lock prompted bounded retry preserving atomic replacement, plus a regression test. Prior recorded test output retained. No manuscript score ran.",
        artifacts={name: filehash(root / name) for name in artifact_names})
    writejson(root / "VERIFICATION.json", record)
    print(json.dumps({k: record[k] for k in ("status", "synthetic_tests", "mode", "vault_status", "corpus_counts", "alpha_spent", "os_isolation_qualified", "autonomous_runner_implemented", "schedule_active")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
