"""Offline transport tests. No credentials, network or inference."""
import json
from pathlib import Path
import tempfile
import io
import sys
import unittest
from unittest.mock import patch
from loop import Store, GateError
from loop import writejson, filehash, utc
from model_broker import ModelBroker, command_for, check_response


class ModelBrokerTests(unittest.TestCase):
    def test_inactive_refuses_before_provider_lookup_or_credential_access(self):
        base = Path(__file__).resolve().parent / ".test-runs"
        base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            store = Store(folder); store.initialize([])
            with patch("model_broker.subprocess.Popen") as proc, patch("model_broker.shutil.copyfile") as auth:
                with self.assertRaises(GateError): ModelBroker(folder).run({})
                proc.assert_not_called(); auth.assert_not_called()
            self.assertFalse((Path(folder) / "model-runs").exists())

    def test_codex_starts_fresh_with_audited_permissions_and_no_resume(self):
        root = Path(__file__).resolve().parent
        cmd = command_for("openai", root / "codex.exe", root / "packet", root / "control", "PINNED-MODEL")
        self.assertIn("--ephemeral", cmd); self.assertIn("--ignore-user-config", cmd)
        self.assertIn("exec", cmd); self.assertNotIn("resume", cmd); self.assertNotIn("fork", cmd)
        self.assertIn("--model", cmd); self.assertIn("PINNED-MODEL", cmd)
        self.assertIn("features.shell_tool=false", cmd)
        self.assertIn("permissions.worker.network.enabled=false", cmd)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", cmd)

    def test_claude_has_no_tools_mcp_or_user_settings(self):
        root = Path(__file__).resolve().parent
        cmd = command_for("anthropic", root / "claude.exe", root / "packet", root / "control", "PINNED-MODEL")
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertEqual(cmd[cmd.index("--setting-sources") + 1], "")
        self.assertIn("--strict-mcp-config", cmd); self.assertIn("--disable-slash-commands", cmd)
        self.assertNotIn("--continue", cmd); self.assertNotIn("--resume", cmd)
        self.assertNotIn("--dangerously-skip-permissions", cmd)

    def test_codex_completed_proposal_accepted(self):
        events = [dict(type="item.completed", item=dict(type="agent_message", text="proposal")), dict(type="turn.completed")]
        self.assertEqual(check_response("openai", "\n".join(json.dumps(e) for e in events)), "proposal")

    def test_codex_tools_or_incomplete_stream_rejected(self):
        for events in ([dict(type="item.completed", item=dict(type="command_execution", command="anything")), dict(type="turn.completed")],
                       [dict(type="item.completed", item=dict(type="agent_message", text="partial"))]):
            with self.assertRaises(GateError): check_response("openai", "\n".join(json.dumps(e) for e in events))

    def test_claude_error_result_rejected(self):
        with self.assertRaises(GateError): check_response("anthropic", json.dumps(dict(type="result", is_error=True, result="failed")))
        self.assertEqual(check_response("anthropic", json.dumps(dict(type="result", is_error=False, result="proposal"))), "proposal")

    def transport_fixture(self, folder):
        root = Path(folder); store = Store(root); store.initialize([])
        proof = root / "FAKE-PROOF.json"; writejson(proof, {"synthetic":True})
        credential = root / "FAKE-AUTH.json"; writejson(credential, {"fake":True})
        packet = root / "packets/model-planner-job"; packet.mkdir()
        (packet / "TASK.txt").write_text("Synthetic task")
        s, h, seq = store.load(); s["mode"] = "ACTIVE"
        s["vault"]["status"] = "SEALED"
        s["budget"].update(started_utc=utc(), max_cycles=5, max_wall_seconds=600)
        ev = {str(proof):filehash(proof)}
        s["control"]["isolation"] = {"evidence":ev}
        s["control"]["model_policy"] = dict(qualified_providers=["openai"], transport_evidence=ev,
            policy=dict(models={"openai":"FAKE-MODEL"}, billing_mode="existing_subscriptions_only", additional_spend_usd=0,
                max_total_calls=2, max_calls_per_cycle=1, max_input_bytes=4096, max_output_bytes=4096,
                wall_seconds=10, cpu_seconds=2, memory_mb=384, credential_files={"openai":str(credential)}))
        store.commit(s, "SYNTHETIC_TRANSPORT_FIXTURE", h, seq)
        q = dict(id="job", provider="openai", role="planner", packet=str(packet),
            packet_files={"TASK.txt":filehash(packet / "TASK.txt")}, task="Return a synthetic proposal")
        return store, q

    def test_mock_transport_reserves_call_and_removes_dummy_credential(self):
        base = Path(__file__).resolve().parent / ".test-runs"; base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            store, q = self.transport_fixture(folder)
            class FakeProc:
                stdin = None
                returncode = 0
                def poll(self): return 0
                def wait(self, timeout=None): return 0
            def fake_popen(*args, **kwargs):
                events = [dict(type="item.completed", item=dict(type="agent_message", text="UNTRUSTED PROPOSAL")),dict(type="turn.completed")]
                kwargs["stdout"].write("\n".join(json.dumps(e) for e in events).encode())
                p = FakeProc(); p.stdin = io.BytesIO(); return p
            with patch("model_broker.shutil.which", return_value=sys.executable), patch("model_broker.WindowsJob"), patch("model_broker.subprocess.Popen", side_effect=fake_popen):
                result = ModelBroker(folder).run(q)
            self.assertEqual(result["status"], "COMPLETED_PENDING_KEEPER_REVIEW")
            self.assertTrue(result["credential_copy_removed"])
            self.assertFalse((Path(folder) / "model-runs/job/runtime/auth.json").exists())
            self.assertEqual(len(store.load()[0]["control"]["model_jobs"]), 1)
            self.assertFalse(store.load()[0]["entries"])

    def test_mock_transport_failure_consumes_call_and_cleans_dummy_credential(self):
        base = Path(__file__).resolve().parent / ".test-runs"; base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            store, q = self.transport_fixture(folder)
            with patch("model_broker.shutil.which", return_value=sys.executable), patch("model_broker.WindowsJob"), patch("model_broker.subprocess.Popen", side_effect=OSError("synthetic launch error")):
                result = ModelBroker(folder).run(q)
            self.assertEqual(result["status"], "FAILED")
            self.assertTrue(result["credential_copy_removed"])
            self.assertEqual(len(store.load()[0]["control"]["model_jobs"]), 1)
            with self.assertRaises(GateError): ModelBroker(folder).run(q)


if __name__ == "__main__": unittest.main(verbosity=2)
