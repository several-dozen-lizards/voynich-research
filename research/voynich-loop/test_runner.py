"""Synthetic keeper/runner tests. OS qualification is separate and uses canaries."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from loop import Store, GateError, filehash, writejson, utc
from runner import Runner, safe_relative, validated_policy
from isolation import ROLES, checked_tree, environment


class RunnerTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parent / ".test-runs"
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temp.name)
        self.store = Store(self.root)
        self.store.initialize([dict(id="task", tier="exploratory", status="READY", reason="synthetic", sources={})])
        self.runner = Runner(self.root)
        self.policy = dict(compute_unit="reserved_worker_wall_seconds", max_job_wall_seconds=10,
            max_job_cpu_seconds=5, memory_mb=384, max_output_bytes=4096, model_calls_enabled=False)
        (self.root / "worker-code").mkdir()
        self.code = self.root / "worker-code/main.py"
        self.code.write_text('print("fixture")')
        for name in ("isolation.py", "qualify_workers.py", "loop.py"):
            (self.root / name).write_text("synthetic boundary file")
        self.receipt = self.root / "mock-qualification.json"
        writejson(self.receipt, {"synthetic": True})
        self.ev = {str(self.receipt):filehash(self.receipt)}
        writejson(self.root / "WORKER-ISOLATION.json", dict(status="PASS_PROCESS_BOUNDARIES",
            worker_code_sha256=filehash(self.root / "isolation.py"), qualifier_sha256=filehash(self.root / "qualify_workers.py"),
            roles=[dict(role=r, status="PASS", receipt=str(self.receipt), receipt_sha256=filehash(self.receipt)) for r in ROLES]))

    def tearDown(self): self.temp.cleanup()

    def request(self, id="job"):
        return dict(id=id, role="sandbox", task_id="task", lead="lead", entrypoint="main.py",
                    files={"main.py":dict(path=str(self.code), sha256=filehash(self.code))})

    def active_fixture(self):
        s, h, n = self.store.load()
        s["mode"] = "ACTIVE"
        s["budget"].update(max_cycles=5, max_compute_units=20, max_wall_seconds=600, started_utc=utc(), configuration="RE_APPROVED")
        s["control"].update(isolation={"evidence":self.ev}, runner_policy={"policy":self.policy, "qualification_evidence":self.ev})
        s["vault"].update(status="SEALED", files={str(self.receipt):filehash(self.receipt)})
        self.store.commit(s, "SYNTHETIC_ACTIVE_FIXTURE_NOT_DEPLOYMENT", h, n)

    def fake_execute(self, input_dir, output_dir, control_dir, entrypoint, **kw):
        control_dir.mkdir(parents=True); output_dir.mkdir()
        value = dict(status="FAILED", fixture=True)
        writejson(control_dir / "RECEIPT.json", value)
        return value

    def test_inactive_blocks_before_any_subprocess_or_job_directory(self):
        with patch("runner.execute") as child:
            with self.assertRaises(GateError): self.runner.run(self.request())
            child.assert_not_called()
        self.assertFalse((self.root / "worker-runs").exists())

    def test_resource_reservation_survives_failure_and_counts_look(self):
        self.active_fixture()
        with patch("runner.execute", side_effect=self.fake_execute): result = self.runner.run(self.request())
        s = self.store.load()[0]
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(s["budget"]["compute_spent"], 10)
        self.assertEqual(s["entries"][0]["result"], "FAILED")
        self.assertEqual(s["entries"][0]["tier"], "exploratory")
        self.assertEqual(s["budget"]["alpha_wealth"], .025)

    def test_duplicate_job_cannot_rerun_or_spend_twice(self):
        self.active_fixture()
        with patch("runner.execute", side_effect=self.fake_execute) as child:
            self.runner.run(self.request())
            with self.assertRaises(GateError): self.runner.run(self.request())
            self.assertEqual(child.call_count, 1)
        self.assertEqual(self.store.load()[0]["budget"]["compute_spent"], 10)

    def test_insufficient_budget_blocks_before_launch(self):
        self.active_fixture()
        with patch("runner.execute", side_effect=self.fake_execute) as child:
            self.runner.run(self.request("one")); self.runner.run(self.request("two"))
            with self.assertRaises(GateError): self.runner.run(self.request("three"))
            self.assertEqual(child.call_count, 2)

    def test_keeper_exception_still_consumes_reservation(self):
        self.active_fixture()
        with patch("runner.execute", side_effect=OSError("synthetic launcher error")):
            result = self.runner.run(self.request())
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(self.store.load()[0]["budget"]["compute_spent"], 10)
        self.assertTrue((self.root / "worker-runs/job/FAILED.json").exists())

    def test_packet_rejects_original_private_source(self):
        self.active_fixture()
        request = self.request()
        request["files"]["PRIVATE.json"] = dict(path=str(self.receipt), sha256=filehash(self.receipt))
        with self.assertRaises(GateError): self.runner.run(request)
        self.assertEqual(self.store.load()[0]["budget"]["compute_spent"], 0)

    def test_changed_boundary_requires_requalification(self):
        self.active_fixture()
        (self.root / "isolation.py").write_text("changed")
        with self.assertRaises(GateError): self.runner.run(self.request())

    def test_hash_mismatch_blocks_packet(self):
        self.active_fixture()
        request = self.request(); self.code.write_text("changed")
        with self.assertRaises(GateError): self.runner.run(request)

    def test_path_traversal_blocked(self):
        for path in ("../private", "C:/private", "a/../../b", "a\\b", "C:relative"):
            with self.assertRaises(GateError): safe_relative(path)

    def test_invalid_or_model_enabled_policy_rejected(self):
        for field, value in (("max_job_wall_seconds", 0), ("memory_mb", 0), ("max_output_bytes", float("nan")),
                             ("model_calls_enabled", True), ("compute_unit", "unknown")):
            p = dict(self.policy); p[field] = value
            with self.assertRaises(GateError): validated_policy(p)

    def test_hardlinked_input_rejected(self):
        import os
        link = self.root / "link.py"
        try:
            os.link(self.code, link)
        except PermissionError:
            self.skipTest("Enclosing executor denies hardlink creation; host qualification runs this test outside it")
        try:
            with self.assertRaises(GateError): checked_tree(self.root / "worker-code")
        finally: link.unlink()

    def test_environment_does_not_inherit_secrets_or_host_control_pipe(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY":"FAKE", "ANTHROPIC_API_KEY":"FAKE", "CODEX_APP_TOOLS_PIPE_PATH":"FAKE", "PYTHONPATH":"FAKE"}):
            env = environment(self.root / "runtime", self.root / "output")
        self.assertFalse(any(k in env for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CODEX_APP_TOOLS_PIPE_PATH", "PYTHONPATH")))


if __name__ == "__main__": unittest.main(verbosity=2)
