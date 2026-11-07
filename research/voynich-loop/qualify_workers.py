"""Neutral OS-boundary and runner qualification. Does not activate research."""
import argparse
import json
import os
from pathlib import Path
import socket
import uuid
from isolation import execute, ROLES, checked_tree
from loop import Store, filehash, writejson, utc, require, readjson

FIXTURE = r'''
import json, os, socket, sys
from pathlib import Path
c = json.loads(Path(__file__).with_name("canaries.json").read_text())
r = {"allowed_input_read": Path(__file__).with_name("ALLOWED.txt").read_text() == "ALLOWED",
     "environment_clean": not any(k.startswith(("CODEX_", "OPENAI_", "ANTHROPIC_")) or k in ("PYTHONPATH", "PYTHONHOME") for k in os.environ)}
for label, path in c["denied_reads"].items():
    try:
        with open(path, "rb"): pass  # Test access only; never read manuscript/credential bytes.
        r[label] = False
    except PermissionError: r[label] = True
    except Exception: r[label] = False  # Missing file/runtime failure is not denial evidence.
for label, path in c["denied_writes"].items():
    try:
        fd = os.open(path, os.O_WRONLY)  # No truncation or writes even if boundary fails.
        os.close(fd); r[label] = False
    except PermissionError: r[label] = True
    except Exception: r[label] = False
output = Path(c["output"])
try:
    (output / "OWN.txt").write_text("OWN"); r["own_output_write"] = (output / "OWN.txt").read_text() == "OWN"
except Exception: r["own_output_write"] = False
sock = socket.socket()
sock.settimeout(1)
try:
    sock.connect(("127.0.0.1", c["listener_port"])); r["network_denied"] = False
except OSError as exc:
    r["network_denied"] = getattr(exc, "winerror", None) == 10013 or getattr(exc, "errno", None) in (1, 13, 10013)
finally: sock.close()
print(json.dumps(r), flush=True)
raise SystemExit(0 if all(r.values()) else 3)
'''


def qualify(root):
    root = Path(root).resolve()
    store = Store(root)
    state, head, _ = store.load()
    require(state["mode"] == "STAGED", "Qualification requested for inactive setup only")
    store.audit(state)
    attempt = root / "isolation-runs" / ("qualification-" + uuid.uuid4().hex)
    attempt.mkdir(parents=True)
    canary_dir = attempt / "private-canaries"; canary_dir.mkdir()
    denied = {}
    for label in ("keeper_read_denied", "history_read_denied", "credentials_read_denied", "sandbox_history_read_denied"):
        path = canary_dir / (label + ".txt")
        path.write_text("NEUTRAL-PRIVATE-CANARY")
        denied[label] = str(path)
    # A neutral file in the actual staged vault directory; no reserved content opened.
    vault = Path(next(iter(state["vault"]["files"]))).parent
    vault_canary = vault / "BOUNDARY-CANARY.txt"
    if not vault_canary.exists(): vault_canary.write_text("NEUTRAL-VAULT-CANARY")
    require(vault_canary.read_text() == "NEUTRAL-VAULT-CANARY", "Conflicting vault canary")
    denied["vault_read_denied"] = str(vault_canary)
    denied["original_full_corpus_read_denied"] = str(root.parent / "complete-atlas-v56/ROWS.json")
    role_paths = {}
    for role in ROLES:
        folder = attempt / role / "input"; folder.mkdir(parents=True)
        (folder / "ALLOWED.txt").write_text("ALLOWED")
        (folder / "main.py").write_text(FIXTURE, encoding="utf-8")
        role_paths[role] = folder
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0)); listener.listen(16)
    listener.settimeout(2)
    port = listener.getsockname()[1]
    # Positive control: endpoint really is reachable from the trusted coordinator.
    check = socket.create_connection(("127.0.0.1", port), timeout=2)
    accepted, _ = listener.accept(); accepted.close(); check.close()
    results = []
    try:
        for index, role in enumerate(ROLES):
            folder = role_paths[role]
            output = folder.parent / "output"
            other = role_paths[ROLES[(index + 1) % len(ROLES)]] / "ALLOWED.txt"
            reads = dict(denied, other_role_read_denied=str(other))
            writejson(folder / "canaries.json", dict(denied_reads=reads, listener_port=port, output=str(output),
                denied_writes=dict(keeper_code_write_denied=str(root / "loop.py"),
                    input_write_denied=str(folder / "main.py"), vault_write_denied=str(vault_canary),
                    other_role_write_denied=str(other))))
            receipt = execute(folder, output, folder.parent / "control", folder / "main.py", wall_seconds=30)
            checks = None
            if receipt["status"] == "PASS":
                lines = (folder.parent / "control/stdout.txt").read_text(encoding="utf-8").splitlines()
                checks = json.loads(lines[-1])
            results.append(dict(role=role, status="PASS" if checks and all(checks.values()) else "FAILED",
                checks=checks, receipt=str(folder.parent / "control/RECEIPT.json"),
                receipt_sha256=filehash(folder.parent / "control/RECEIPT.json")))
    finally:
        listener.close()
    passed = all(r["status"] == "PASS" for r in results)
    record = dict(status="PASS_PROCESS_BOUNDARIES" if passed else "FAILED", utc=utc(), roles=results,
        ledger_head_before=head, ledger_head_after=store.load()[1], positive_network_control=True,
        mode_after=store.load()[0]["mode"], worker_code_sha256=filehash(root / "isolation.py"),
        qualifier_sha256=filehash(Path(__file__)), model_calls=0, research_tasks=0, alpha_spent=0,
        limitation="Neutral native-process checks only. Model transport/context profiles qualify separately. No claim of machine-wide denial: keeper/current user retain access.")
    writejson(attempt / "QUALIFICATION.json", record)
    writejson(root / "WORKER-ISOLATION.json", record)
    print(json.dumps(dict(status=record["status"], roles=[{k:r[k] for k in ("role", "status")} for r in results],
                         report=str(attempt / "QUALIFICATION.json"), mode=record["mode_after"]), indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    raise SystemExit(qualify(parser.parse_args().root))
