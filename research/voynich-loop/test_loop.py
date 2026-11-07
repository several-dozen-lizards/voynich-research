"""Synthetic state-machine tests only. Never reads or scores manuscript material."""
import copy
import tempfile
import unittest
from pathlib import Path
from loop import Store, GateError, digest, filehash, lord_level, utc, readjson


class LedgerTests(unittest.TestCase):
    def setUp(self):
        test_root = Path(__file__).resolve().parent / ".test-runs"
        test_root.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=test_root)
        self.root = Path(self.tmp.name)
        self.store = Store(self.root)
        self.receipt = self.root / "receipt.txt"
        self.receipt.write_text("Synthetic test evidence, never a real human decision")
        self.ev = {str(self.receipt): filehash(self.receipt)}
        self.store.initialize([dict(id="task", tier="exploratory", status="READY", reason="synthetic", sources=self.ev)])

    def tearDown(self):
        self.tmp.cleanup()

    def state(self):
        return self.store.load()[0]

    def mock_active(self):
        # Fixture-only: does NOT claim actual OS deployment. Never used in production bootstrap.
        s, h, n = self.store.load()
        s["mode"] = "ACTIVE"
        s["budget"].update(max_cycles=100, max_wall_seconds=86400, max_compute_units=100,
                            started_utc=utc(), configuration="RE_APPROVED")
        self.store.commit(s, "SYNTHETIC_TEST_FIXTURE", h, n)

    def authorized(self, action, target, request):
        q = copy.deepcopy(request)
        id = f"approval-{len(self.state()['control']['approvals'])}"
        self.store.apply("approve", dict(id=id, actor="Re", written_ok="Synthetic fixture only",
            action=action, target=target, request_sha256=digest(q), evidence=self.ev))
        q["approval_id"] = id
        return self.store.apply(action, q)

    def freeze(self, id="claim", looks=0):
        p = dict(hypothesis_id="hypothesis", lead="lead", estimand="difference", null="zero",
                 analysis="fixed", support="real support", controls="null/recovery", multiplicity="one test",
                 selection_validity="synthetic independent p", dependence_justification="independent synthetic",
                 data_partition="open", code_entrypoint=str(self.receipt), scorer_model_family="family-A",
                 spec_sources=self.ev, historical_related_looks=looks,
                 replication_rule=dict(alpha="same frozen conjunctive hypothesis; no extra reward", support="fixed"))
        return self.store.apply("freeze", dict(id=id, protocol=p, artifacts=self.ev,
                                                alpha=lord_level(self.state()["budget"])))

    def request(self, id="claim", **kw):
        e = self.store.entry(self.state(), id)
        return dict(id=id, protocol_sha256=e["protocol_sha256"], **kw)

    def qualify(self, id="claim", verdict="PASS"):
        return self.store.apply("qualify", self.request(id, verdict=verdict, real_support=True,
                   null_and_recovery_controls=True, evidence=self.ev))

    def score(self, id="claim", p=0):
        return self.store.apply("score", self.request(id, result="SCORED", model_family="family-A", p_value=p, evidence=self.ev))

    def skeptic(self, id="claim", verdict="CLEAR", family="family-B"):
        e = self.store.entry(self.state(), id)
        return self.store.apply("skeptic", self.request(id, verdict=verdict, model_family=family,
            blind_packet_only=True, related_look_count=e["related_sandbox_looks"], evidence=self.ev))

    def ready_claim(self, looks=0):
        self.mock_active()
        self.freeze(looks=looks)
        self.qualify()
        self.score()
        self.skeptic()

    def test_staged_no_research_or_false_exhaustion(self):
        with self.assertRaises(GateError): self.freeze()
        for _ in range(31): self.store.apply("cycle", {})
        self.assertIsNone(self.state()["end_state"])
        self.assertEqual(len(self.state()["cycles"]), 0)

    def test_activate_requires_real_deployment_receipts(self):
        with self.assertRaises(GateError):
            self.authorized("activate", "loop", dict(statistical_review=self.ev, historical_look_counts_certified=True))
        self.assertEqual(self.state()["mode"], "STAGED")

    def test_lord_reference_values_and_reward(self):
        self.mock_active()
        self.assertAlmostEqual(lord_level(self.state()["budget"]), .0125)
        self.freeze(); self.qualify(); self.score()
        b = self.state()["budget"]
        self.assertAlmostEqual(b["alpha_wealth"], .0375)
        self.assertAlmostEqual(lord_level(b), .025 / 6 + .025 / 2)

    def test_no_refund_for_qualification_failure(self):
        self.mock_active(); self.freeze(); self.qualify(verdict="BLOCKED")
        b = self.state()["budget"]
        self.assertAlmostEqual(b["alpha_wealth"], .0125)
        self.assertAlmostEqual(lord_level(b), .025 / 6)

    def test_only_one_pending_claim(self):
        self.mock_active(); self.freeze()
        with self.assertRaises(GateError): self.freeze("second")

    def test_score_requires_qualification_and_is_one_shot(self):
        self.mock_active(); self.freeze()
        with self.assertRaises(GateError): self.score()
        self.qualify(); self.score()
        with self.assertRaises(GateError): self.score()

    def test_nan_and_out_of_range_p_rejected(self):
        self.mock_active(); self.freeze(); self.qualify()
        for p in (float("nan"), float("inf"), -.1, 1.1, True):
            with self.assertRaises(GateError): self.score(p=p)
        self.assertEqual(self.store.entry(self.state(), "claim")["result"], "PENDING")

    def test_no_pass_does_not_earn(self):
        self.mock_active(); self.freeze(); self.qualify(); self.score(p=.5)
        self.assertAlmostEqual(self.state()["budget"]["alpha_wealth"], .0125)

    def test_same_family_skeptic_blocked(self):
        self.mock_active(); self.freeze(); self.qualify(); self.score()
        with self.assertRaises(GateError): self.skeptic(family="family-A")

    def test_skeptic_objection_blocks_promotion(self):
        self.mock_active(); self.freeze(); self.qualify(); self.score(); self.skeptic(verdict="OBJECTION")
        with self.assertRaises(GateError): self.authorized("promote", "claim", self.request())

    def test_human_gate_and_exact_request_binding(self):
        self.ready_claim()
        with self.assertRaises(GateError): self.store.apply("promote", self.request())
        self.authorized("promote", "claim", self.request())
        self.assertTrue(self.store.entry(self.state(), "claim")["held_up"])
        with self.assertRaises(GateError): self.authorized("promote", "claim", self.request())

    def test_over_fifty_requires_replication(self):
        self.ready_claim(looks=51)
        with self.assertRaises(GateError): self.authorized("promote", "claim", self.request())

    def test_twenty_look_cap(self):
        self.mock_active()
        for i in range(20):
            self.store.apply("look", dict(id=f"E-{i}", lead="lead", task_id="task", result="no lead", evidence=self.ev))
        with self.assertRaises(GateError):
            self.store.apply("look", dict(id="E-21", lead="lead", task_id="task", result="x", evidence=self.ev))
        self.freeze()
        self.assertEqual(self.store.entry(self.state(), "claim")["related_sandbox_looks"], 20)

    def test_five_freeze_cap_rolling_window(self):
        self.mock_active()
        for i in range(5): self.freeze(f"claim{i}"); self.qualify(f"claim{i}", verdict="BLOCKED")
        with self.assertRaises(GateError): self.freeze("six")

    def test_changed_frozen_code_blocks(self):
        self.mock_active(); self.freeze()
        self.receipt.write_text("changed code")
        with self.assertRaises(GateError): self.qualify()

    def test_changed_protocol_blocks(self):
        self.mock_active(); self.freeze()
        (self.root / "protocols/claim/PROTOCOL.json").write_text("{}")
        with self.assertRaises(GateError): self.qualify()

    def test_projection_tamper_detected_and_recoverable(self):
        (self.root / "BUDGET.json").write_text("{}")
        with self.assertRaises(GateError): self.store.load()
        s, _, _ = self.store.load(projections=False)
        self.store.render(s)
        self.store.load()

    def test_journal_tamper_detected(self):
        p = self.root / "EVENTS.jsonl"
        p.write_text(p.read_text().replace('STAGED', 'ACTIVE'))
        with self.assertRaises(GateError): self.store.load(projections=False)

    def test_lock_blocks_second_keeper(self):
        with self.store.lock():
            with self.assertRaises(GateError): self.store.apply("cycle", {})

    def test_empty_queue_exhaustion(self):
        self.mock_active()
        s, h, n = self.store.load(); s["queue"] = []; self.store.commit(s, "fixture", h, n)
        self.store.apply("cycle", {})
        self.assertEqual(self.state()["end_state"], "T4")

    def test_thirty_no_claim_cycles_stop(self):
        self.mock_active()
        for _ in range(30): self.store.apply("cycle", {})
        self.assertEqual(self.state()["end_state"], "T4")
        self.assertTrue(Path(self.store.report()).exists())

    def test_blocked_queue_pauses_not_exhausted(self):
        self.mock_active()
        s, h, n = self.store.load(); s["queue"][0]["status"] = "BLOCKED"; self.store.commit(s, "fixture", h, n)
        self.store.apply("cycle", {})
        self.assertEqual(self.state()["mode"], "PAUSED_REVIEW")
        self.assertIsNone(self.state()["end_state"])
        self.assertEqual(self.state()["control"]["no_claim_cycles"], 0)

    def test_compute_cap_t5(self):
        self.mock_active(); self.store.apply("cycle", dict(compute_units=100))
        self.assertEqual(self.state()["end_state"], "T5")
        with self.assertRaises(GateError): self.freeze()

    def test_pending_review_on_thirtieth_cycle_does_not_exhaust(self):
        self.mock_active(); self.freeze()
        s, h, n = self.store.load()
        s["control"]["no_claim_cycles"] = 29
        self.store.commit(s, "fixture", h, n)
        self.store.apply("cycle", {})
        self.assertEqual(self.state()["mode"], "PAUSED_REVIEW")
        self.assertIsNone(self.state()["end_state"])
        self.assertEqual(self.state()["control"]["no_claim_cycles"], 29)

    def test_atomic_replace_retries_transient_windows_lock(self):
        from unittest.mock import patch
        from loop import writejson
        import os
        real_replace = os.replace
        calls = []
        def temporary_lock(a, b):
            calls.append(1)
            if len(calls) == 1:
                raise PermissionError("synthetic sharing lock")
            return real_replace(a, b)
        with patch("loop.os.replace", side_effect=temporary_lock):
            writejson(self.root / "retry.json", {"ok": True})
        self.assertEqual(readjson(self.root / "retry.json"), {"ok": True})
        self.assertEqual(len(calls), 2)

    def test_mutable_queue_source_can_be_reviewed_without_editing_history(self):
        self.receipt.write_text("new owner status")
        with self.assertRaises(GateError): self.store.apply("cycle", {})
        newev = {str(self.receipt): filehash(self.receipt)}
        task = dict(id="task", tier="exploratory", status="READY", reason="Re reviewed updated owner status",
                    sources=newev, expected_information=1, cost=1)
        q = {"tasks": [task]}
        self.store.apply("approve", dict(id="owner-update", actor="Re", written_ok="synthetic", action="queue",
            target="queue", request_sha256=digest(q), evidence=newev))
        self.store.apply("queue", dict(q, approval_id="owner-update"))
        self.store.audit(self.state())
        self.assertEqual(self.state()["queue"][0]["sources"], newev)

    def test_skeptic_packet_has_no_look_history(self):
        self.ready_claim()
        p = Path(self.store.skeptic_packet("claim"))
        names = {x.name for x in p.iterdir()}
        self.assertNotIn("LEDGER.json", names)
        self.assertNotIn("EVENTS.jsonl", names)
        self.assertEqual(readjson(p / "TASK.json")["related_sandbox_looks"], 0)
        with self.assertRaises(GateError): self.store.skeptic_packet("claim")

    def test_vault_subset_once_per_hypothesis(self):
        self.ready_claim()
        s, h, n = self.store.load()
        s["vault"].update(status="SEALED", files=self.ev, subsets={"labels": dict(files=list(self.ev), exposure="FRESH_VERIFIED", uses=[])})
        self.store.commit(s, "fixture", h, n)
        req = self.request(subset="labels", replication_protocol_sha256=self.store.entry(self.state(), "claim")["protocol_sha256"])
        self.authorized("vault_access", "claim:labels", req)
        with self.assertRaises(GateError): self.authorized("vault_access", "claim:labels", req)

    def test_exposed_reserve_cannot_pass_replication(self):
        self.ready_claim()
        s, h, n = self.store.load()
        s["vault"].update(status="SEALED", files=self.ev, subsets={"labels": dict(files=list(self.ev), exposure="EXPOSED_OR_UNCERTIFIED", uses=[])})
        self.store.commit(s, "fixture", h, n)
        e = self.store.entry(self.state(), "claim")
        self.authorized("vault_access", "claim:labels", self.request(subset="labels", replication_protocol_sha256=e["protocol_sha256"]))
        with self.assertRaises(GateError):
            self.authorized("replicate", "claim", self.request(verdict="PASS", source="vault", subset="labels",
                pre_split_never_touched=True, frozen_decision_rule=True, evidence=self.ev, custody_evidence=self.ev))

    def test_t2_requires_held_up_replication(self):
        self.ready_claim()
        self.authorized("promote", "claim", self.request())
        with self.assertRaises(GateError):
            self.authorized("end", "T2", dict(end_state="T2", id="claim", **{"class": "v6-T1"}, evidence=self.ev))

    def test_approval_cannot_authorize_a_changed_request(self):
        self.ready_claim()
        original = self.request()
        self.store.apply("approve", dict(id="bound", actor="Re", written_ok="fixture", action="promote",
            target="claim", request_sha256=digest(original), evidence=self.ev))
        with self.assertRaises(GateError):
            self.store.apply("promote", dict(original, approval_id="bound", extra="changed"))
        self.assertFalse(self.state()["control"]["approvals"]["bound"]["used"])

    def test_synthetic_corpus_partition_excludes_all_readings_and_formats(self):
        from prepare_corpus import prepare
        from loop import writejson
        rows = []
        for folio in ("f1r", "f2r", "f3r"):
            for tr in ("H", "F"):
                for fmt in ("P", "L"):
                    rows.append([tr, folio, "test", "1", "A", fmt, "x", "x", folio + "." + fmt, ["dummy"], "dummy"])
        source, plan = self.root / "rows.json", self.root / "plan.json"
        writejson(source, rows)
        writejson(plan, dict(source_sha256=filehash(source), reserved_zodiac_folios=["f2r"],
                            folios=[dict(folio="f3r", partition="candidate_reserve")]))
        receipt = prepare(source, plan, self.root / "open", self.root / "vault")
        self.assertEqual(receipt["counts"], {"open": 4, "zodiac": 4, "candidate-label-folios": 4})
        self.assertEqual({r[1] for r in readjson(self.root / "open/ROWS.json")}, {"f1r"})
        self.assertFalse(receipt["filesystem_isolation_qualified"])
        with self.assertRaises(GateError): prepare(source, plan, self.root / "open", self.root / "vault")

    def test_replication_then_promotion_and_t2(self):
        self.ready_claim(looks=51)
        self.authorized("replicate", "claim", self.request(verdict="PASS", source="fresh",
            pre_split_never_touched=True, frozen_decision_rule=True, evidence=self.ev, custody_evidence=self.ev))
        self.authorized("promote", "claim", self.request())
        self.authorized("end", "T2", dict(end_state="T2", id="claim", **{"class": "v6-T1"}, evidence=self.ev))
        self.assertEqual(self.state()["end_state"], "T2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
