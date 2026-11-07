"""Native runner fault controls. Fixed local fixtures; no research/model calls."""
import ctypes
from ctypes import wintypes as W
import json
from pathlib import Path
import uuid
from isolation import execute
from loop import Store, require, writejson, filehash, utc

FIXTURES = {
    "success": 'print("NATIVE_FIXTURE_OK", flush=True)',
    "nonzero": 'raise SystemExit(13)',
    "output_limit": 'print("x" * 100000, flush=True)',
    "file_output_limit": '''import os
from pathlib import Path
(Path(os.environ["TEMP"]) / "LARGE.bin").write_bytes(b"x" * 8192)
''',
    "descendant_timeout": '''import subprocess,sys,time,json
p=subprocess.Popen([sys.executable,"-I","-S","-u","-c","import time; time.sleep(60)"])
print(json.dumps({"descendant_pid":p.pid}),flush=True)
time.sleep(60)
''',
    "cpu_limit": 'while True: pass',
    "memory_limit": '''try:
    a=bytearray(1024*1024*1024)
    print("MEMORY_NOT_LIMITED",flush=True)
    raise SystemExit(5)
except MemoryError:
    print("MEMORY_LIMIT_ENFORCED",flush=True)
''',
}


def process_alive(pid):
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]; api.OpenProcess.restype = W.HANDLE
    api.GetExitCodeProcess.argtypes = [W.HANDLE, ctypes.POINTER(W.DWORD)]
    api.CloseHandle.argtypes = [W.HANDLE]
    handle = api.OpenProcess(0x1000, False, pid)
    if not handle:
        require(ctypes.get_last_error() == 87, "Cannot determine descendant liveness")
        return False
    try:
        code = W.DWORD()
        require(bool(api.GetExitCodeProcess(handle, ctypes.byref(code))), "Cannot query child exit")
        return code.value == 259
    finally: api.CloseHandle(handle)


def main():
    root = Path(__file__).resolve().parent
    state, head, _ = Store(root).load()
    require(state["mode"] == "STAGED", "Fault controls require inactive setup")
    attempt = root / "runner-qualification" / uuid.uuid4().hex
    attempt.mkdir(parents=True)
    results = []
    denied = dict(keeper=str(root / "loop.py"), vault=str(Path(next(iter(state["vault"]["files"]))).parent / "BOUNDARY-CANARY.txt"))
    for name, code in FIXTURES.items():
        base = attempt / name; folder = base / "input"; folder.mkdir(parents=True)
        (folder / "main.py").write_text(code, encoding="utf-8")
        receipt = execute(folder, base / "output", base / "control", folder / "main.py", denied_paths=denied,
            wall_seconds=4 if name == "descendant_timeout" else 12,
            cpu_seconds=1 if name == "cpu_limit" else 8, max_output_bytes=4096 if name in ("output_limit", "file_output_limit") else 1048576)
        text = (base / "control/stdout.txt").read_text(encoding="utf-8")
        checks = dict(contained=receipt["child_contained"], immutable=receipt["input_unchanged"])
        if name == "success": checks["expected"] = receipt["status"] == "PASS" and "NATIVE_FIXTURE_OK" in text
        elif name == "nonzero": checks["expected"] = receipt["status"] == "FAILED" and receipt["returncode"] == 13
        elif name == "output_limit": checks["expected"] = receipt["failure"] == "OUTPUT_LIMIT"
        elif name == "file_output_limit": checks["expected"] = receipt["status"] == "FAILED" and "OUTPUT_FILE_LIMIT" in str(receipt["failure"])
        elif name == "descendant_timeout":
            checks["expected"] = receipt["failure"] == "WALL_TIMEOUT"
            descendants = [json.loads(line)["descendant_pid"] for line in text.splitlines() if '"descendant_pid"' in line]
            checks["descendant_killed"] = len(descendants) == 1 and not process_alive(descendants[0])
        elif name == "cpu_limit": checks["expected"] = receipt["status"] == "FAILED" and receipt["failure"] != "WALL_TIMEOUT"
        elif name == "memory_limit": checks["expected"] = receipt["status"] == "PASS" and "MEMORY_LIMIT_ENFORCED" in text
        results.append(dict(fixture=name, passed=all(checks.values()), checks=checks,
            receipt=str(base / "control/RECEIPT.json"), receipt_sha256=filehash(base / "control/RECEIPT.json")))
    record = dict(status="PASS_NATIVE_RUNNER_CONTROLS" if all(r["passed"] for r in results) else "FAILED", utc=utc(),
        results=results, ledger_head_before=head, ledger_head_after=Store(root).load()[1],
        isolation_code_sha256=filehash(root / "isolation.py"), runner_code_sha256=filehash(root / "runner.py"),
        model_calls=0, research_tasks=0, mode_after=Store(root).load()[0]["mode"])
    writejson(attempt / "QUALIFICATION.json", record)
    writejson(root / "RUNNER-QUALIFICATION.json", record)
    print(json.dumps(dict(status=record["status"], results=[{k:r[k] for k in ("fixture", "passed")} for r in results],
                         mode=record["mode_after"], report=str(attempt / "QUALIFICATION.json")), indent=2))
    return 0 if record["status"] == "PASS_NATIVE_RUNNER_CONTROLS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
