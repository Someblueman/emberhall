"""Finite admission reservations for generic resident coverage."""
from unittest.mock import patch

from house import life, staffing
from tests.support import HouseCase


class IdleCoverageTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", life.CONTROLLER, {"name": "Clock"})

    def offer(self, task="work", **extra):
        self.record.append("task", "alice", {"task": task, "title": "Ready work",
            "description": "A bounded fixture", "ready": True, **extra})

    def start(self, run="idle", resident=None, **extra):
        self.record.append("life", life.CONTROLLER, {"kind": "run-start", "run": run,
            "resident": resident or "resident-" + run, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": "a" * 40, "workspace": "residents/" + run,
            "policy_revision": "fixture", "mode": "work", **extra})

    def test_unclaimed_generic_run_covers_work_until_exact_reservation_boundary(self):
        self.offer()
        self.start(backlog=True)
        state = self.record.read()[0]
        started = state["life"]["runs"]["idle"]["started_at"]

        recent = life.workload(state, started + life.EXPLORER_ADMISSION_SECONDS - 0.001)
        self.assertEqual(["resident-idle"], recent["idle_residents"])
        self.assertEqual([], recent["uncovered_task_ids"])

        expired = life.workload(state, started + life.EXPLORER_ADMISSION_SECONDS)
        self.assertEqual([], expired["idle_residents"])
        self.assertEqual(["work"], expired["uncovered_task_ids"])
        capacity = staffing.capacity(state)
        self.assertLessEqual(expired["wanted_starts"], capacity["total_limit"] - 1)
        self.assertEqual("active", state["life"]["runs"]["idle"]["status"])
        with patch("house.record.time.time", return_value=started + life.EXPLORER_ADMISSION_SECONDS):
            self.start("replacement", backlog=True)
        admitted = self.record.read()[0]
        self.assertEqual("active", admitted["life"]["runs"]["replacement"]["status"])
        self.assertLessEqual(life.workload(admitted, admitted["at"])["wanted_starts"],
                             staffing.capacity(admitted)["total_limit"] - 2)

    def test_pinned_policy_keeps_legacy_accounting_until_migration(self):
        self.offer()
        self.start(backlog=True)
        state = self.record.read()[0]
        started = state["life"]["runs"]["idle"]["started_at"]
        state["wake_policy"] = {"fixture": True}
        later = started + life.EXPLORER_ADMISSION_SECONDS + 1

        self.assertEqual(["resident-idle"], life.workload(state, later)["idle_residents"])
        state["maintenance"] = {"migrations": {life.IDLE_COVERAGE_SCOPE: {}}}
        self.assertEqual([], life.workload(state, later)["idle_residents"])

    def test_live_claim_remains_owned_after_generic_admission_reservation_expires(self):
        self.offer()
        self.start(backlog=True)
        self.record.append("arrive", "resident-idle", {"name": "Worker"})
        self.record.append("claim", "resident-idle", {"task": "work", "expect": 0,
            "token": "live-claim", "seconds": 3600})
        state = self.record.read()[0]
        started = state["life"]["runs"]["idle"]["started_at"]

        demand = life.workload(state, started + life.EXPLORER_ADMISSION_SECONDS + 1)
        self.assertEqual([], demand["ready_tasks"])
        self.assertEqual([], demand["idle_residents"])
        self.assertEqual([], demand["uncovered_task_ids"])
        self.assertEqual("resident-idle", state["tasks"]["work"]["owner"])

    def test_expired_generic_reservations_feed_eligible_ballot_matching(self):
        state = self.record.read()[0]
        state["life"] = life.empty()
        state["shelf"] = {"choices": {"choice": {"status": "open",
            "votes": {"bob": {"idea": "idea"}}, "candidates": ["idea"]}},
            "ideas": {"idea": {"author": "alice"}}}
        state["tasks"]["ballot"] = {"status": "open", "generation": 0, "owner": None,
            "until": 0, "ready": True, "ballot_choice": "choice"}
        state["life"]["runs"]["ineligible"] = {"resident": "bob", "status": "active",
            "started_at": state["at"], "started_sequence": state["sequence"]}
        state["residents"]["carol"] = {"name": "Carol", "awake": True, "cursor": 0, "note": "Fixture"}
        state["life"]["runs"]["eligible"] = {"resident": "carol", "status": "active",
            "started_at": state["at"], "started_sequence": state["sequence"]}

        recent = life.workload(state, state["at"])
        self.assertEqual(["ballot"], recent["ready_tasks"])
        self.assertEqual(["bob", "carol"], recent["idle_residents"])
        self.assertEqual([], recent["uncovered_task_ids"])

        expired = life.workload(state, state["at"] + life.EXPLORER_ADMISSION_SECONDS)
        self.assertEqual([], expired["idle_residents"])
        self.assertEqual(["ballot"], expired["uncovered_task_ids"])

