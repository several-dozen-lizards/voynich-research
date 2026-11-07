
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
