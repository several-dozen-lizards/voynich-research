"""Keeper-owned Windows process boundary. No model calls or activation.

The exact Codex binary/profile and Python runtime are pinned in each receipt.
Every job starts suspended inside a kill-on-close Job Object. A trusted bootstrap
must prove that the actual sandbox child is in that job before any task executes.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time
import uuid
from loop import GateError, require, filehash, writejson, utc, digest

ROLES = ("planner", "sandbox", "freezer", "qualifier", "scorer", "skeptic")
BOOTSTRAP = r'''
import json, os, sys, runpy
allowed = {"SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS", "PATH", "TEMP", "TMP", "PYTHONIOENCODING"}
allowed = {k.upper() for k in allowed}
for key in list(os.environ):
    if key.upper() not in allowed:
        del os.environ[key]
# MXC can replace TEMP/TMP during launch. Bind the research task's normal
# scratch to the monitored private output, rather than a shared launcher temp.
os.environ["TEMP"] = sys.argv[3]
os.environ["TMP"] = sys.argv[3]
guards = {}
for name, path in json.loads(sys.argv[2]).items():
    try:
        with open(path, "rb"): pass
        guards[name] = False
    except PermissionError: guards[name] = True
    except Exception: guards[name] = False
try:
    fd = os.open(sys.argv[1], os.O_WRONLY); os.close(fd); guards["input_immutable"] = False
except PermissionError: guards["input_immutable"] = True
except Exception: guards["input_immutable"] = False
print(json.dumps({"boundary_ready_pid":os.getpid(), "boundary_guards":guards}), flush=True)
if sys.stdin.readline().strip() != "RUN":
    raise SystemExit(90)
sys.argv = [sys.argv[1]]
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(sys.argv[0]))
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def checked_tree(folder):
    """Reject links/junctions/hardlinks before the keeper reads worker outputs."""
    folder = Path(folder).resolve()
    files = {}
    for path in folder.rglob("*"):
        st = path.lstat()
        require(not path.is_symlink() and not (getattr(st, "st_file_attributes", 0) & 0x400), "Linked/reparse worker output rejected")
        require(path.resolve().is_relative_to(folder), "Output escapes folder")
        if path.is_file():
            require(st.st_nlink == 1, "Hardlinked worker file rejected")
            files[str(path.relative_to(folder))] = filehash(path)
    return files


def output_usage(folder, file_limit=4096):
    count = total = 0
    for current, dirs, files in os.walk(folder, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            st = path.lstat()
            require(not path.is_symlink() and not (getattr(st, "st_file_attributes", 0) & 0x400), "Linked/reparse output rejected")
            if name in files:
                count += 1
                require(st.st_nlink == 1, "Hardlinked output rejected")
                total += st.st_size
                require(count <= file_limit, "OUTPUT_FILE_COUNT_LIMIT")
    return total


def overrides(input_dir, output_dir, python_exe):
    mapping = {":root": "deny", ":minimal": "read", ":slash_tmp": "deny", str(Path(python_exe).parent): "read",
               str(Path(input_dir).resolve()): "read", str(Path(output_dir).resolve()): "write"}
    return {"default_permissions": '"worker"', "windows.sandbox": '"mxc"',
            "permissions.worker.filesystem": "{" + ",".join(json.dumps(k) + "=" + json.dumps(v) for k, v in mapping.items()) + "}",
            "permissions.worker.network.enabled": "false"}


def flags(config):
    return [part for k, v in config.items() for part in ("-c", k + "=" + v)]


def environment(runtime_dir, output_dir):
    # No inherited API keys, proxy URLs, Python paths, hooks or provider tokens.
    allowed = ("SystemRoot", "SystemDrive", "WINDIR", "COMSPEC", "PATHEXT", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
               "LOCALAPPDATA", "APPDATA", "USERPROFILE", "ProgramData", "ProgramFiles", "ProgramFiles(x86)")
    env = {k: os.environ[k] for k in allowed if k in os.environ}
    env.update(CODEX_HOME=str(runtime_dir), TEMP=str(output_dir), TMP=str(output_dir),
               PATH=str(Path(os.environ["SystemRoot"]) / "System32"), PYTHONIOENCODING="utf-8")
    return env


class WindowsJob:
    def __init__(self, memory_bytes, cpu_seconds, process_limit=16):
        require(os.name == "nt", "This backend requires Windows")
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, W.LPCWSTR]
        self.api.CreateJobObjectW.restype = W.HANDLE
        self.api.SetInformationJobObject.argtypes = [W.HANDLE, ctypes.c_int, ctypes.c_void_p, W.DWORD]
        self.api.AssignProcessToJobObject.argtypes = [W.HANDLE, W.HANDLE]
        self.api.TerminateJobObject.argtypes = [W.HANDLE, W.UINT]
        self.api.CloseHandle.argtypes = [W.HANDLE]
        self.api.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
        self.api.OpenProcess.restype = W.HANDLE
        self.api.IsProcessInJob.argtypes = [W.HANDLE, W.HANDLE, ctypes.POINTER(W.BOOL)]
        self.name = "Local\\voynich-" + uuid.uuid4().hex
        self.handle = self.api.CreateJobObjectW(None, self.name)
        require(bool(self.handle), "CreateJobObject failed")
        class Basic(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong),
                        ("flags", W.DWORD), ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t),
                        ("process_limit", W.DWORD), ("affinity", ctypes.c_size_t), ("priority", W.DWORD), ("scheduling", W.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(n, ctypes.c_ulonglong) for n in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]
        class Extended(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", IO), ("process_memory", ctypes.c_size_t),
                        ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]
        limits = Extended()
        limits.basic.flags = 0x2000 | 0x200 | 0x8 | 0x4  # kill-on-close, job memory, process count, job CPU time
        limits.basic.job_time = int(cpu_seconds * 10_000_000)
        limits.basic.process_limit = process_limit
        limits.job_memory = memory_bytes
        if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            err = ctypes.get_last_error(); self.close(); raise OSError(err, "SetInformationJobObject")

    def attach_and_resume(self, proc):
        require(bool(self.api.AssignProcessToJobObject(self.handle, W.HANDLE(int(proc._handle)))), "Cannot contain worker process tree")
        nt = ctypes.WinDLL("ntdll")
        nt.NtResumeProcess.argtypes = [W.HANDLE]
        nt.NtResumeProcess.restype = ctypes.c_long
        require(nt.NtResumeProcess(W.HANDLE(int(proc._handle))) == 0, "Cannot resume contained worker")

    def contains(self, pid):
        handle = self.api.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            yes = W.BOOL()
            return bool(self.api.IsProcessInJob(handle, self.handle, ctypes.byref(yes))) and bool(yes.value)
        finally:
            self.api.CloseHandle(handle)

    def adopt_bootstrap(self, pid):
        # A sandbox broker can create the child outside the CLI's process tree.
        # Only our fixed bootstrap is running here, blocked on the RUN handshake.
        handle = self.api.OpenProcess(0x1000 | 0x100 | 0x1, False, pid)
        if not handle:
            return False
        try:
            return bool(self.api.AssignProcessToJobObject(self.handle, handle)) and self.contains(pid)
        finally:
            self.api.CloseHandle(handle)

    def terminate(self):
        if self.handle:
            self.api.TerminateJobObject(self.handle, 91)

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def execute(input_dir, output_dir, control_dir, entrypoint, *, codex=None, wall_seconds=30,
            cpu_seconds=10, memory_mb=384, max_output_bytes=1024 * 1024, denied_paths=None):
    """Execute one sealed Python capsule. This primitive never grants research authority."""
    require(os.name == "nt", "Windows backend only")
    input_dir, output_dir, control_dir = map(lambda p: Path(p).resolve(), (input_dir, output_dir, control_dir))
    require(all(not a.is_relative_to(b) for a in (input_dir, output_dir, control_dir) for b in (input_dir, output_dir, control_dir) if a != b), "Input/output/control folders must be disjoint")
    entrypoint = Path(entrypoint).resolve()
    require(entrypoint.is_relative_to(input_dir) and entrypoint.is_file(), "Entrypoint must be inside sealed input")
    require(wall_seconds > 0 and cpu_seconds > 0 and memory_mb >= 64 and max_output_bytes > 0, "Invalid process limits")
    require(not control_dir.exists() and not output_dir.exists(), "Never overwrite a job attempt")
    denied_paths = dict(denied_paths or {})
    require(all(Path(p).is_file() for p in denied_paths.values()), "Negative guard paths must exist")
    control_dir.mkdir(parents=True); output_dir.mkdir(parents=True)
    runtime = control_dir / "runtime"; runtime.mkdir()
    codex = Path(codex or shutil.which("codex") or "").resolve()
    require(codex.is_file(), "Codex executable unavailable")
    python = Path(sys.executable).resolve()
    config = overrides(input_dir, output_dir, python)
    command = [str(codex), "sandbox", *flags(config), "-P", "worker", "-C", str(input_dir), "--",
               str(python), "-I", "-S", "-u", "-c", BOOTSTRAP, str(entrypoint), json.dumps(denied_paths), str(output_dir)]
    sealed = checked_tree(input_dir)
    receipt = dict(status="STARTING", utc_started=utc(), command=command, profile=config,
        input_files=sealed, codex_sha256=filehash(codex), python_sha256=filehash(python),
        boundary_code_sha256=filehash(Path(__file__)), limits=dict(wall_seconds=wall_seconds,
        cpu_seconds=cpu_seconds, memory_mb=memory_mb, max_output_bytes=max_output_bytes),
        model_calls=0, child_contained=False)
    writejson(control_dir / "START.json", receipt)
    deadline = time.monotonic() + wall_seconds
    job = WindowsJob(memory_mb * 1024 * 1024, cpu_seconds)
    proc = None
    chunks = queue.Queue(maxsize=64)
    stdout, stderr = bytearray(), bytearray()
    failure = None
    started = time.monotonic()
    next_size_check = started
    threads = []
    try:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=input_dir, env=environment(runtime, output_dir), creationflags=0x4 | 0x08000000)
        job.attach_and_resume(proc)
        def pump(name, pipe):
            try:
                while True:
                    block = pipe.read1(4096)
                    if not block: break
                    while True:
                        try: chunks.put((name, block), timeout=.1); break
                        except queue.Full:
                            if time.monotonic() > deadline: return
            finally:
                pipe.close()
        for name, pipe in (("stdout", proc.stdout), ("stderr", proc.stderr)):
            thread = threading.Thread(target=pump, args=(name, pipe), daemon=True)
            thread.start(); threads.append(thread)
        while True:
            if time.monotonic() >= deadline:
                failure = "WALL_TIMEOUT"; break
            if time.monotonic() >= next_size_check:
                require(output_usage(output_dir) <= max_output_bytes, "OUTPUT_FILE_LIMIT")
                next_size_check = time.monotonic() + .1
            try:
                name, block = chunks.get(timeout=.05)
                (stdout if name == "stdout" else stderr).extend(block)
                if len(stdout) + len(stderr) > max_output_bytes:
                    failure = "OUTPUT_LIMIT"; break
            except queue.Empty:
                if proc.poll() is not None and not any(t.is_alive() for t in threads) and chunks.empty(): break
            if not receipt["child_contained"] and b"\n" in stdout:
                hello = json.loads(bytes(stdout).split(b"\n", 1)[0])
                require(type(hello.get("boundary_ready_pid")) is int, "Invalid bootstrap handshake")
                require(hello.get("boundary_guards") and all(hello["boundary_guards"].values()), "Per-job denial/immutability guard failed; task not released")
                require(job.contains(hello["boundary_ready_pid"]) or job.adopt_bootstrap(hello["boundary_ready_pid"]),
                        "Sandbox child escaped job containment; task was not released")
                receipt.update(child_contained=True, child_pid=hello["boundary_ready_pid"], boundary_guards=hello["boundary_guards"])
                proc.stdin.write(b"RUN\n"); proc.stdin.flush(); proc.stdin.close()
        if failure: job.terminate()
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
        job.terminate()
    finally:
        job.close()  # also kills descendants after normal parent exit
        if proc:
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
        for t in threads: t.join(timeout=1)
        while not chunks.empty():
            name, block = chunks.get_nowait()
            dest = stdout if name == "stdout" else stderr
            if len(stdout) + len(stderr) + len(block) <= max_output_bytes: dest.extend(block)
        (control_dir / "stdout.txt").write_bytes(stdout[:max_output_bytes])
        (control_dir / "stderr.txt").write_bytes(stderr[:max_output_bytes])
    unchanged = checked_tree(input_dir) == sealed
    try:
        output_files = checked_tree(output_dir)
        total_size = sum((output_dir / p).stat().st_size for p in output_files)
        if total_size > max_output_bytes:
            failure = failure or "OUTPUT_FILE_LIMIT"
    except GateError as exc:
        output_files = {}; failure = failure or str(exc)
    if not failure and proc and proc.returncode != 0:
        failure = "PROCESS_EXIT_" + str(proc.returncode)
    receipt.update(status="PASS" if not failure and proc and proc.returncode == 0 and receipt["child_contained"] and unchanged else "FAILED",
        failure=failure, returncode=proc.returncode if proc else None, elapsed_seconds=time.monotonic()-started,
        utc_finished=utc(), input_unchanged=unchanged, output_files=output_files,
        stdout_sha256=filehash(control_dir / "stdout.txt"), stderr_sha256=filehash(control_dir / "stderr.txt"))
    writejson(control_dir / "RECEIPT.json", receipt)
    return receipt
