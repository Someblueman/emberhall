"""Expired task withdrawals close only the older ordinary help they replace."""
import unittest
from unittest.mock import patch

from house import home
from house.life import CONTROLLER
from tests.support import HouseCase


class HelpWithdrawalTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", CONTROLLER, {"name": "Watch keeper"})

    def task_and_help(self, *, ready=True, request="older-help"):
        self.record.append("task", "alice", {"task": "work", "title": "Work",
            "description": "A bounded test", **({"ready": True} if ready else {})})
        self.record.append("life", "alice", {"kind": "help", "request": request,
            "reason": "Help with this work", "task": "work"})

    def claim_then_withdraw(self, *, seconds=1):
        self.record.append("claim", "alice", {"task": "work", "expect": 0,
            "token": "claim-token", "seconds": seconds})
        task = self.record.read()[0]["tasks"]["work"]
        with patch("house.record.time.time", return_value=task["until"] + 1):
            self.record.append("ready", "alice", {"task": "work", "expect": 1, "ready": False})

    def coordinator(self):
        runtime = self.root / "runtime.pyz"
        runtime.touch()
        coordinator = home.Coordinator(self.record, runtime)
        coordinator.refresh_runtime = lambda: True
        self.addCleanup(coordinator.close)
        return coordinator

    def test_expired_claim_withdrawal_resolves_once_before_help_admission(self):
        self.task_and_help()
        self.claim_then_withdraw()
        coordinator = self.coordinator()

        coordinator.resolve_completed_help()
        state, events, _ = self.record.read()
        self.assertEqual("resolved", state["life"]["requests"]["older-help"]["status"])
        self.assertEqual("claimed", state["tasks"]["work"]["status"])
        self.assertEqual("alice", state["tasks"]["work"]["owner"])
        self.assertEqual(1, sum(e["data"].get("request") == "older-help"
                                and e["data"].get("kind") == "help-resolved" for e in events))
        self.assertIsNone(coordinator.start("codex", "older-help"))
        coordinator.resolve_completed_help()
        self.assertEqual(1, sum(e["data"].get("request") == "older-help"
                                and e["data"].get("kind") == "help-resolved"
                                for e in self.record.read()[1]))

    def test_live_claim_without_a_withdrawal_stays_pending(self):
        self.task_and_help()
        self.record.append("claim", "alice", {"task": "work", "expect": 0,
            "token": "claim-token", "seconds": 3600})
        self.coordinator().resolve_completed_help()
        state = self.record.read()[0]
        self.assertEqual("pending", state["life"]["requests"]["older-help"]["status"])
        self.assertEqual("alice", state["tasks"]["work"]["owner"])

    def test_requeue_keeps_old_help_closed_and_preserves_newer_help(self):
        self.task_and_help()
        self.claim_then_withdraw()
        self.record.append("life", "bob", {"kind": "help", "request": "newer-help",
            "reason": "A later request", "task": "work"})
        self.record.append("ready", "alice", {"task": "work", "expect": 2, "ready": True})

        self.coordinator().resolve_completed_help()
        state = self.record.read()[0]
        self.assertEqual("resolved", state["life"]["requests"]["older-help"]["status"])
        self.assertEqual("pending", state["life"]["requests"]["newer-help"]["status"])
        self.assertTrue(state["tasks"]["work"]["ready"])

    def test_missing_readiness_history_does_not_resolve_help(self):
        self.task_and_help(ready=False)
        self.record.append("claim", "alice", {"task": "work", "expect": 0,
            "token": "claim-token", "seconds": 1})
        self.coordinator().resolve_completed_help()
        self.assertEqual("pending", self.record.read()[0]["life"]["requests"]["older-help"]["status"])

    def test_unfinished_source_review_is_not_closed_by_task_withdrawal(self):
        from tests.test_explorer_dispatch_home import configure
        from tests.test_source_review import SourceReviewTests
        configure(self, SourceReviewTests)
        reviewer = "resident-withdrawal-reviewer"
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": "source",
            "resident": reviewer, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": "a" * 40, "workspace": "residents/source",
            "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", reviewer, {"name": "Source reviewer"})
        self.record.append("sleep", reviewer, {"through": self.record.read()[0]["sequence"],
            "note": "Source process stopped"})
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": "source",
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        self.record.append("task", "alice", {"task": "work", "title": "Work",
            "description": "A bounded test", "ready": True})
        self.record.append("life", "alice", {"kind": "help", "request": "source-review-help",
            "reason": "Review this source", "task": "work", "review_run": "source"})
        self.record.append("claim", "alice", {"task": "work", "expect": 0,
            "token": "claim-token", "seconds": 1})
        task = self.record.read()[0]["tasks"]["work"]
        with patch("house.record.time.time", return_value=task["until"] + 1):
            self.record.append("ready", "alice", {"task": "work", "expect": 1, "ready": False})

        self.coordinator().resolve_completed_help()
        self.assertEqual("pending", self.record.read()[0]["life"]["requests"]
                         ["source-review-help"]["status"])


if __name__ == "__main__":
    unittest.main()
