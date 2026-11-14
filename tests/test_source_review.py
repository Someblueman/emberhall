"""Review admission, bounded queue and lifecycle; fixtures make no model calls."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from house import home, maintenance, source_delivery as delivery
from tests import test_explorer_dispatch, test_home
from tests.test_explorer_dispatch_home import configure


class SourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.prior = test_explorer_dispatch.ExplorerDispatchTests(); self.prior.setUp()
        self.h = self.prior.h

    def migration(self):
        old = maintenance.protected_manifest(self.h.state)
        return self.prior.migration() | {"scope": maintenance.DELIVERY_SCOPE,
            "protected_files": old | {name: "a" * 64 for name in
                                      maintenance.ALLOWED_CHANGES[maintenance.DELIVERY_SCOPE]}}

    def enable(self):
        self.h.event("owner-migrate", self.migration())

    def test_activation_preserves_all_policy_and_requires_owner_and_exact_pins(self):
        before = copy.deepcopy(self.h.state)
        good = self.migration()
        self.h.reject("owner-migrate", good, "owner operator", "bob")
        for path in ("house/council.py", "house/shelf.py", "house/providers.py", "house/test_sandbox.py"):
            bad = copy.deepcopy(good); bad["protected_files"][path] = "0" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        bad = copy.deepcopy(good); del bad["protected_files"]["house/source_delivery.py"]
        self.h.reject("owner-migrate", bad, "replacement manifest")
        self.assertFalse(delivery.enabled(before))
        self.h.event("owner-migrate", good)
        self.assertTrue(delivery.enabled(self.h.state))
        for key in before.keys() - {"maintenance", "sequence", "at", "receipts"}:
            self.assertEqual(before[key], self.h.state[key], key)

    def test_review_tool_migration_preserves_policy_and_cannot_widen_permissions(self):
        self.enable()
        before = copy.deepcopy(self.h.state)
        old = maintenance.protected_manifest(before)
        data = self.migration() | {"scope": maintenance.REVIEW_TOOLS_SCOPE,
            "protected_files": old | {name: "b" * 64 for name in
                                      maintenance.ALLOWED_CHANGES[maintenance.REVIEW_TOOLS_SCOPE]}}
        for path in ("house/providers.py", "house/windows.py", "house/test_sandbox.py", "house/council.py"):
            bad = copy.deepcopy(data); bad["protected_files"][path] = "c" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        self.h.event("owner-migrate", data)
        for key in before.keys() - {"maintenance", "sequence", "at", "receipts"}:
            self.assertEqual(before[key], self.h.state[key], key)

    def test_review_requires_stopped_source_and_rejects_returning_author_atomically(self):
        request = {"kind": "help", "request": "review", "review_run": "source", "reason": "Review"}
        self.h.reject("life", request, "not enabled")
        self.h.event("owner-migrate", self.migration())
        self.h.reject("life", request, "stopped contribution")
        self.prior.start("source")
        self.h.reject("life", request, "stopped contribution")
        self.h.event("arrive", {"name": "Writer"}, "resident-source")
        self.h.event("sleep", {"through": 0, "note": "Done"}, "resident-source")
        self.h.event("life", {"kind": "run-finish", "run": "source", "outcome": "success",
            "exit_code": 0, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        self.h.event("life", request)
        data = self.prior.start_data("reviewer", help_request="review")
        self.h.reject("life", data | {"resident": "resident-source"}, "independent", "watch-keeper")
        self.h.event("life", data, "watch-keeper")
        self.assertEqual(self.h.state["life"]["requests"]["review"]["status"], "assigned")

    def test_queue_prioritizes_product_one_at_a_time_and_preserves_failed_reviews(self):
        self.h.event("owner-migrate", self.migration())
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory)
            for run, path in (("a", "research/note.md"), ("z", "projects/player.js")):
                self.prior.start(run)
                self.h.event("life", {"kind": "run-finish", "run": run, "outcome": "success",
                    "exit_code": 0, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
                (private / run).mkdir()
                (private / run / "contribution.json").write_text(json.dumps(
                    {"status": "pending-review", "commit": run * 40, "paths": [path]}))
            harness = self.h
            class Record:
                def read(self): return (harness.state, [], "fixture")
                def append(self, op, actor, data, request): harness.event(op, data, actor)
            record = Record()
            (private / "z/integration.json").write_text("{")
            self.assertEqual(len(home.pending_contributions(private)), 2)
            delivery.queue_review(record, private)
            self.assertEqual(list(self.h.state["life"]["requests"]), ["source-review-z"])
            delivery.queue_review(record, private)
            self.assertEqual(len(self.h.state["life"]["requests"]), 1)
            result = {"run": "z", "contribution": "z" * 40, "status": "tests-failed"}
            (private / "z/integration.json").write_text(json.dumps(result))
            self.h.event("life", {"kind": "help-resolved", "request": "source-review-z", "reason": "Retain failure"}, "watch-keeper")
            delivery.queue_review(record, private)
            self.assertIn("source-review-a", self.h.state["life"]["requests"])
            for text in ('{', '[]', json.dumps(result | {"status": "reviewed"})):
                (private / "z/integration.json").write_text(text)
                self.assertIsNone(delivery.review_result(private, "z"))


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                 "inert native fixture requires host process observation")
class ReviewLifecycleTests(unittest.TestCase):
    def test_sleep_without_integration_requeues_review_instead_of_resolving(self):
        f = test_home.HomeTests(); f.setUp(); self.addCleanup(f.doCleanups)
        configure(f, SourceReviewTests)
        (f.repo / "source.txt").write_text("base\n")
        test_home.git(f.repo, "add", "source.txt")
        test_home.git(f.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                      "-c", "user.email=test@local", "commit", "-m", "Fixture")
        f.coordinator = home.Coordinator(f.record, f.runtime)
        self.addCleanup(f.coordinator.close)
        source = f.coordinator.start("codex"); f.drain()
        (f.coordinator.private / source / "integration.json").write_text("{")
        delivery.queue_review(f.record, f.coordinator.private)
        key = "source-review-" + source
        for status in (None, "reviewed", "integrated"):
            run = f.coordinator.start("codex", key)
            actor = f.record.read()[0]["life"]["runs"][run]["resident"]
            op = "wake" if actor in f.record.read()[0]["residents"] else "arrive"
            f.record.append(op, actor, {} if op == "wake" else {"name": "Reviewer"})
            f.record.append("sleep", actor, {"through": f.record.read()[0]["sequence"], "note": "Handoff"})
            if status:
                path = f.coordinator.private / source
                commit = json.loads((path / "contribution.json").read_text())["commit"]
                (path / "integration.json").write_text(json.dumps(
                    {"run": source, "contribution": commit, "status": status}))
            f.drain()
            expected = "resolved" if status == "integrated" else "pending"
            self.assertEqual(f.record.read()[0]["life"]["requests"][key]["status"], expected)
