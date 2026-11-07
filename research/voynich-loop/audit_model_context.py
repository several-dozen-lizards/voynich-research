"""Render fresh Codex role inputs without contacting a model or copying auth.

This qualifies supplied context only. Model inference/Claude transport are not
enabled by this audit, and native analysis remains in isolation.py processes.
"""
import json
from pathlib import Path
import shutil
import subprocess
import uuid
from isolation import ROLES, environment, flags, overrides
from loop import Store, require, utc, filehash, writejson

DISABLED = ("apps", "plugins", "remote_plugin", "shell_tool", "multi_agent", "browser_use", "browser_use_external",
            "computer_use", "image_generation", "in_app_browser", "skill_search", "skill_mcp_dependency_install",
            "hooks", "tool_suggest", "workspace_dependencies", "sleep_tool", "view_image", "code_mode_host", "memories")


def config(input_dir, output_dir):
    import sys
    values = overrides(input_dir, output_dir, Path(sys.executable).resolve())
    values.update({"memories.use_memories": "false", "memories.generate_memories": "false",
        "project_doc_max_bytes": "0", "developer_instructions": '""', "mcp_servers": "{}",
        "web_search": '"disabled"', "history.persistence": '"none"', "tools.view_image": "false",
        "features.skip_host_skill_discovery": "true"})
    values.update({"features." + feature: "false" for feature in DISABLED})
    return values


def main():
    root = Path(__file__).resolve().parent
    require(Store(root).load()[0]["mode"] == "STAGED", "Offline context audit requires inactive setup")
    codex = Path(shutil.which("codex")).resolve()
    base = root / "model-context-audits" / uuid.uuid4().hex
    base.mkdir(parents=True)
    results = []
    for role in ROLES:
        packet = base / role / "input"; packet.mkdir(parents=True)
        control = packet.parent / "control"; control.mkdir()
        output = packet.parent / "output"; output.mkdir()
        runtime = control / "runtime"; runtime.mkdir()
        prompt = f"Neutral offline context audit for role {role}. No research, tools, or model response requested."
        values = config(packet, output)
        proc = subprocess.run([str(codex), "--no-daemon", "debug", "prompt-input", *flags(values), "--", prompt],
            cwd=packet, env=environment(runtime, output), capture_output=True, timeout=30)
        (control / "rendered.json").write_bytes(proc.stdout)
        (control / "stderr.txt").write_bytes(proc.stderr)
        texts, tools, error = "", [], None
        try:
            require(proc.returncode == 0, "Prompt renderer failed")
            data = json.loads(proc.stdout)
            texts = "\n".join(p.get("text", "") for m in data for p in m.get("content", []))
            tools = [t.get("name") for m in data if m.get("type") == "additional_tools"
                     for ns in m.get("tools", []) for t in ns.get("tools", [])]
            require(not any(w.casefold() in texts.casefold() for w in ("MEMORY_SUMMARY", "memories_v2", "Reed mode", "JNSQ")),
                    "Inherited private/project context found")
            # This CLI always inserts its bundled generic skill catalogue. Its
            # roots must be confined to this fresh runtime, with no user plugins.
            import re
            skill_roots = re.findall(r"- `r\d+` = `([^`]+)`", texts)
            require(all(Path(p).resolve().is_relative_to(runtime.resolve()) for p in skill_roots), "External skill catalogue inherited")
            require(any(p.get("text") == prompt for m in data if m.get("role") == "user" for p in m.get("content", [])), "Exact input missing")
            require('<special>:root</special>' in texts and 'access="deny" escalatable="false"' in texts, "Root-deny context absent")
            require(not (runtime / "auth.json").exists(), "Audit must not copy provider credentials")
        except Exception as exc:
            error = str(exc)
        results.append(dict(role=role, status="PASS_CONTEXT_ONLY" if error is None else "FAILED", error=error,
            rendered=str(control / "rendered.json"), rendered_sha256=filehash(control / "rendered.json"),
            generic_tool_declarations=tools, bundled_generic_skill_catalogue_present="<skills_instructions>" in texts,
            exact_prompt=prompt, config=values))
    record = dict(status="PASS_CONTEXT_ONLY" if all(r["status"] == "PASS_CONTEXT_ONLY" for r in results) else "FAILED",
        utc=utc(), roles=results, model_calls=0, credentials_copied=False,
        codex_executable_sha256=filehash(codex), adapter_code_sha256=filehash(Path(__file__)),
        limitation="No model or Claude launch. Supplied-context audit is distinct from native OS-process isolation. Generic declarations can remain despite disabled tool features; never treat this as a zero-tool or full-process inference qualification.")
    writejson(base / "AUDIT.json", record); writejson(root / "MODEL-CONTEXT-AUDIT.json", record)
    print(json.dumps(dict(status=record["status"], roles=[dict(role=r["role"], status=r["status"]) for r in results], model_calls=0), indent=2))
    return 0 if record["status"] == "PASS_CONTEXT_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
