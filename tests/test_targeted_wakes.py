"""Synthetic targeted wakes and real inert coordinator; no live model claims."""
from __future__ import annotations

import copy
import os
import unittest
from unittest.mock import patch

from house import council, life, maintenance
from house.life import workload
from tests import test_resident_returns as return_fixture
from tests import test_owner_maintenance as owner_fixture


class TargetedRecordTests(unittest.TestCase):
    def setUp(self):
        fixture = owner_fixture.OwnerMaintenanceTests()
        fixture.setUp()
        self.h = fixture.h
        migration = fixture.migration() | {"scope": maintenance.CONTINUITY_SCOPE,
            "approval_sha256": maintenance.GROWTH_SHA256}
        migration["protected_files"]["house/model.py"] = maintenance.protected_manifest(self.h.state)["house/model.py"]
        self.h.event("owner-migrate", migration)
        old = maintenance.protected_manifest(self.h.state)
        self.h.event("owner-migrate", fixture.migration() | {
            "scope": maintenance.TARGETED_WAKE_SCOPE,
            "approval_sha256": maintenance.SOURCES[maintenance.TARGETED_WAKE_SCOPE],
            "protected_files": dict(old), "previous_manifest_sha256": maintenance.fingerprint(old)})
        self._supervised("fern", "Fern", "codex", "gpt-6.1-sol", "fern-old")
        self._supervised("cairn", "Cairn", "codex", "gpt-6.1-sol", "cairn-old")
        self.h.event("arrive", {"name": "Manual Mae"}, "manual-mae")

    def _start_run(self, run, resident, agent="codex", model="gpt-6.1-sol"):
        self.h.event("life", {"kind": "run-start", "run": run, "resident": resident,
            "agent": agent, "model": model, "source_head": "a" * 40,
            "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "work"}, "watch-keeper")

    def _supervised(self, resident, name, agent, model, run):
        self._start_run(run, resident, agent, model)
        self.h.event("arrive", {"name": name}, resident)
        self.h.event("life", {"kind": "identity", "agent": agent, "model": model}, resident)
        self.h.event("sleep", {"through": self.h.state["sequence"], "note": f"Continue {name}"}, resident)
        self.h.event("life", {"kind": "run-finish", "run": run, "outcome": "success",
            "exit_code": 0, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")

    def _help(self, request, agent="codex", model="gpt-6.1-sol", target_resident=None, reason="Do work", extra=None):
        data = {"kind": "help", "request": request, "reason": reason}
        if agent is not None:
            data["agent"] = agent
        if model is not None:
            data["model"] = model
        if target_resident is not None:
            data["target_resident"] = target_resident
        if extra:
            data.update(extra)
        return data

    def test_ordinary_help_without_target_unchanged(self):
        self.h.event("life", self._help("ordinary", agent=None, model=None), "alice")
        self.assertEqual(self.h.state["life"]["requests"]["ordinary"]["status"], "pending")
        at = self.h.now + 1000
        self.assertIn("ordinary", workload(self.h.state, at)["pending_help"])

    def test_a_targeted_request_with_nothing_attached_is_a_note_after_the_migration(self):
        self.h.event("life", self._help("before", target_resident="cairn", reason="Coordinate only"), "alice")
        at = max(self.h.now, self.h.state["at"]) + 1000
        self.assertIn("before", workload(self.h.state, at)["pending_help"], "unchanged before the migration")
        self.h.state["maintenance"]["migrations"][life.NOTES] = {"at": self.h.state["at"]}
        self.assertNotIn("before", workload(self.h.state, at)["pending_help"], "a note wakes nobody")
        self.assertEqual(["before"], [key for key, _ in life.waiting_notes(self.h.state, "cairn")])
        self.assertEqual([], life.waiting_notes(self.h.state, "fern"))
        self.h.event("life", {"kind": "help", "request": "untargeted", "reason": "Anyone"}, "alice")
        self.assertIn("untargeted", workload(self.h.state, at)["pending_help"], "untargeted help still wakes")
        from house.maintenance import DELIVERY_SCOPE
        self.h.state["maintenance"]["migrations"][DELIVERY_SCOPE] = {"scope": DELIVERY_SCOPE}
        self.h.event("life", self._help("review", target_resident="fern", extra={"review_run": "cairn-old"}), "alice")
        self.assertFalse(life.note(self.h.state, self.h.state["life"]["requests"]["review"]))
        self.assertIn("review", workload(self.h.state, at)["pending_help"], "a review to do still wakes its resident")

    def test_targeted_help_requires_explicit_matching_route(self):
        self.h.reject("life", {"kind": "help", "request": "t-missing", "reason": "x",
            "target_resident": "cairn"}, "explicit agent and model")
        self.h.reject("life", self._help("t-wrong-model", model="gpt-6-astra", target_resident="cairn"),
            "does not match latest run")
        self.h.event("life", self._help("t-good", target_resident="cairn"), "alice")
        req = self.h.state["life"]["requests"]["t-good"]
        self.assertEqual(req["target_resident"], "cairn")
        self.assertEqual(req["status"], "pending")

    def test_targeted_rejects_unknown_and_manual_only(self):
        self.h.reject("life", self._help("t-unknown", target_resident="ghost"), "unknown targeted resident")
        self.h.reject("life", self._help("t-manual", target_resident="manual-mae"), "not supervised")

    def test_targeted_requires_resident_returns_enabled(self):
        before = copy.deepcopy(self.h.state)
        self.h.state["maintenance"]["resident_returns"] = False
        self.h.reject("life", self._help("t-noflag", target_resident="cairn"),
            "requires resident returns enabled")
        self.h.state = before

    def test_targeted_requires_activation_migration_when_wake_policy(self):
        before = copy.deepcopy(self.h.state)
        del self.h.state["maintenance"]["migrations"][life.TARGETED_SCOPE]
        self.assertIn("wake_policy", self.h.state)
        self.h.reject("life", self._help("t-noact", target_resident="cairn"),
            "requires activation migration")
        self.h.event("life", {"kind": "help", "request": "ord-act", "reason": "Other"}, "alice")
        at = self.h.state["at"] + 10
        self.assertIn("ord-act", workload(self.h.state, at)["pending_help"])
        self.h.state = before
        self.h.event("life", self._help("t-afteract", target_resident="cairn"), "alice")
        self.assertEqual(self.h.state["life"]["requests"]["t-afteract"]["status"], "pending")

    def test_targeted_rejects_source_self_review(self):
        from house.maintenance import DELIVERY_SCOPE
        self.h.state["maintenance"]["migrations"][DELIVERY_SCOPE] = {"scope": DELIVERY_SCOPE}
        data = self._help("t-self", target_resident="cairn")
        data["review_run"] = "cairn-old"
        self.h.reject("life", data, "cannot request source author")
        data2 = self._help("t-other", target_resident="fern")
        data2["review_run"] = "cairn-old"
        self.h.event("life", data2, "alice")
        self.assertEqual(self.h.state["life"]["requests"]["t-other"]["status"], "pending")

    def test_targeted_help_creation_allows_queued_active_awake(self):
        self.h.event("wake", {}, "cairn")
        self.h.event("life", self._help("t-queued-awake", target_resident="cairn"), "alice")
        self.assertEqual(self.h.state["life"]["requests"]["t-queued-awake"]["status"], "pending")
        at = max(self.h.now, self.h.state["at"]) + 1000
        pending = workload(self.h.state, at)["pending_help"]
        self.assertNotIn("t-queued-awake", pending, "awake target must remain pending but not counted as eligible")
        self.h.event("sleep", {"through": self.h.state["sequence"], "note": "sleep again"}, "cairn")
        self._start_run("cairn-active", "cairn")
        self.h.reject("life", {"kind": "run-start", "run": "cairn-race", "resident": "cairn",
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
            "workspace": "residents/cairn-race", "policy_revision": "fixture", "mode": "work"},
            "not eligible", "watch-keeper")
        at2 = max(self.h.now, self.h.state["at"]) + 1000
        pending2 = workload(self.h.state, at2)["pending_help"]
        self.assertNotIn("t-queued-awake", pending2)

    def test_queued_claimed_and_cooled_targets_not_eligible(self):
        self.h.event("task", {"task": "held-target", "title": "Held", "description": "Held"}, "alice")
        self.h.event("claim", {"task": "held-target", "token": "held-token", "expect": 0, "seconds": 600}, "cairn")
        self.h.event("life", self._help("t-claimed", target_resident="cairn"), "alice")
        at = self.h.state["at"] + 10
        self.assertNotIn("t-claimed", workload(self.h.state, at)["pending_help"])
        self.h.event("sleep", {"through": self.h.state["sequence"], "note": "sleep with claim"}, "cairn")
        self.assertNotIn("t-claimed", workload(self.h.state, at)["pending_help"])
        at_expired = self.h.state["tasks"]["held-target"]["until"] + 10
        self.assertIn("t-claimed", workload(self.h.state, at_expired)["pending_help"])
        self.h.event("life", {"kind": "budget", "agent": "codex", "until": at_expired + 9999, "reason": "cooldown"}, "watch-keeper")
        self.assertNotIn("t-claimed", workload(self.h.state, at_expired + 100)["pending_help"])
        self.h.event("life", {"kind": "help", "request": "ordinary-now", "reason": "Other work"}, "alice")
        at_now = at_expired + 100
        self.assertIn("ordinary-now", workload(self.h.state, at_now)["pending_help"])
        self.assertNotIn("t-claimed", workload(self.h.state, at_now)["pending_help"])

    def test_unrelated_work_still_eligible_when_targeted_unavailable(self):
        self.h.event("wake", {}, "cairn")
        self.h.event("life", self._help("t-unavail", target_resident="cairn"), "alice")
        self.h.event("life", {"kind": "help", "request": "ordinary-unavail", "reason": "Other"}, "alice")
        at = self.h.state["at"] + 10
        pending = workload(self.h.state, at)["pending_help"]
        self.assertNotIn("t-unavail", pending)
        self.assertIn("ordinary-unavail", pending)

    def test_run_start_forged_resident_substitution_rejected(self):
        self.h.event("life", self._help("t-forge", target_resident="cairn"), "alice")
        payload = {"kind": "run-start", "run": "forged", "resident": "fern",
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
            "workspace": "residents/forged", "policy_revision": "fixture", "mode": "work",
            "help_request": "t-forge"}
        self.h.reject("life", payload, "targeted admission resident mismatch", "watch-keeper")
        self.assertEqual(self.h.state["life"]["requests"]["t-forge"]["status"], "pending")
        payload2 = {"kind": "run-start", "run": "forged-new", "resident": "resident-new", "agent": "codex",
            "model": "gpt-6.1-sol", "source_head": "a" * 40, "workspace": "residents/forged-new",
            "policy_revision": "fixture", "mode": "work", "help_request": "t-forge"}
        self.h.reject("life", payload2, "targeted admission resident mismatch", "watch-keeper")

    def test_run_start_wrong_route_rejected(self):
        self.h.event("life", self._help("t-wrong-route", target_resident="cairn"), "alice")
        payload = {"kind": "run-start", "run": "wrong-route", "resident": "cairn",
            "agent": "muse", "model": "muse-ember-1.0", "source_head": "a" * 40,
            "workspace": "residents/wrong-route", "policy_revision": "fixture", "mode": "work",
            "help_request": "t-wrong-route"}
        self.h.reject("life", payload, "not eligible|route mismatch", "watch-keeper")
        self.assertEqual(self.h.state["life"]["requests"]["t-wrong-route"]["status"], "pending")

    def test_run_start_exact_target_admits_and_duplicate_rejected(self):
        self.h.event("life", self._help("t-race", target_resident="cairn"), "alice")
        payload = {"kind": "run-start", "run": "first", "resident": "cairn",
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
            "workspace": "residents/first", "policy_revision": "fixture", "mode": "work",
            "help_request": "t-race"}
        self.h.event("life", payload, "watch-keeper")
        self.assertEqual(self.h.state["life"]["requests"]["t-race"]["status"], "assigned")
        payload2 = dict(payload, run="second", workspace="residents/second")
        self.h.reject("life", payload2, "help already taken|not eligible", "watch-keeper")
        self.h.event("life", self._help("t-race2", target_resident="cairn"), "alice")
        at = self.h.state["at"] + 10
        self.assertNotIn("t-race2", workload(self.h.state, at)["pending_help"],
            "second pending for active target must not be eligible")
        payload3 = dict(payload, run="third", workspace="residents/third", help_request="t-race2")
        self.h.reject("life", payload3, "not eligible", "watch-keeper")

    def test_workload_pending_counts_only_eligible_targeted(self):
        self.h.event("life", self._help("t-elig", target_resident="cairn"), "alice")
        at = max(self.h.now, self.h.state["at"]) + 1000
        self.assertIn("t-elig", workload(self.h.state, at)["pending_help"])
        self.h.event("life", self._help("t-elig2", target_resident="cairn"), "alice")
        pending = workload(self.h.state, at)["pending_help"]
        self.assertIn("t-elig", pending)
        self.assertIn("t-elig2", pending)


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                 "inert host coordinator uses process-group recovery")
class TargetedCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.base = return_fixture.ReturnProcessTests()
        self.base.setUp(); self.addCleanup(self.base.doCleanups)
        self.record, self.coordinator = self.base.record, self.base.coordinator
        state = self.record.read()[0]
        old = maintenance.protected_manifest(state)
        self.record.append("owner-migrate", "alice", {
            "scope": maintenance.TARGETED_WAKE_SCOPE,
            "approval_sha256": maintenance.SOURCES[maintenance.TARGETED_WAKE_SCOPE],
            "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64,
            "protected_files": dict(old), "previous_manifest_sha256": maintenance.fingerprint(old),
            "previous_runtime_sha256": "d" * 64, "runtime_sha256": "e" * 64,
            "test_output_sha256": "f" * 64, "test_count": 1})

    def help(self, resident, request="target"):
        self.record.append("life", "alice", {"kind": "help", "request": request,
            "reason": "Synthetic targeted return", "agent": "codex", "model": "gpt-6.1-sol",
            "target_resident": resident})

    def directories(self):
        return {p.name for p in self.coordinator.private.iterdir() if p.is_dir()}

    def test_exact_target_over_older_preserves_cursor_and_fresh_room(self):
        first, older = self.base.stretch()
        self.record.append("wake", older, {})
        second, newer = self.base.stretch()
        self.assertNotEqual(older, newer)
        self.record.append("sleep", older, {"through": self.record.read()[0]["sequence"], "note": "Later"})
        memory = copy.deepcopy(self.record.read()[0]["residents"][newer])
        self.help(newer)
        run = self.coordinator.start("codex", "target")
        self.base.f.drain()
        state = self.record.read()[0]
        self.assertEqual(state["life"]["runs"][run]["resident"], newer)
        self.assertEqual(state["life"]["runs"][run]["outcome"], "success")
        self.assertNotIn(run, (first, second))
        self.assertEqual(state["residents"][newer]["name"], memory["name"])
        self.assertGreater(state["residents"][newer]["cursor"], memory["cursor"])
        prompt = (self.coordinator.private / run / "prompt.txt").read_text()
        self.assertIn("returning as the same resident", prompt)
        self.assertIn('"handoff": "Keep the thread"', prompt)
        self.assertTrue((self.coordinator.private / "residents" / run / ".house-client").is_file())

    def test_unavailable_target_does_not_allocate_or_block_unrelated_tick(self):
        _, resident = self.base.stretch()
        self.record.append("wake", resident, {})
        self.help(resident)
        before = self.directories()
        self.assertIsNone(self.coordinator.start("codex", "target"))
        self.assertEqual(self.directories(), before)
        self.record.append("life", "alice", {"kind": "help", "request": "ordinary", "reason": "Other work",
            "agent": "codex", "model": "gpt-6.1-sol"})
        self.coordinator.tick(poll=False)
        state = self.record.read()[0]
        self.assertEqual(state["life"]["requests"]["target"]["status"], "pending")
        run = state["life"]["requests"]["ordinary"]["run"]
        self.assertNotEqual(state["life"]["runs"][run]["resident"], resident)
        self.base.f.drain()
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["outcome"], "success")

    def test_wrong_provider_and_duplicate_do_not_allocate(self):
        _, resident = self.base.stretch()
        self.help(resident)
        before = self.directories()
        self.assertIsNone(self.coordinator.start("muse", "target"))
        self.assertEqual(self.directories(), before)
        run = self.coordinator.start("codex", "target")
        during = self.directories()
        self.assertIsNone(self.coordinator.start("codex", "target"))
        self.assertEqual(self.directories(), during)
        self.assertEqual(self.record.read()[0]["life"]["requests"]["target"]["run"], run)
        self.base.f.drain()

    def test_wake_between_selection_and_admission_leaves_no_empty_room(self):
        _, resident = self.base.stretch()
        self.help(resident)
        original = self.coordinator.life
        def race(kind, run, **data):
            if kind == "run-start":
                self.record.append("wake", resident, {})
            return original(kind, run, **data)
        before = self.directories()
        with patch.object(self.coordinator, "life", side_effect=race):
            self.assertIsNone(self.coordinator.start("codex", "target"))
        self.assertEqual(self.directories(), before)
        self.assertEqual(self.record.read()[0]["life"]["requests"]["target"]["status"], "pending")
