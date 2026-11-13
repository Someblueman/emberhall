"""Real private archives and lost-pointer recovery; owner authentication is isolated."""
import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from house import maintenance, owner_upgrade, runtime
from house.home import single_coordinator
from house.home_work import git
from tests import test_runtime


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX"),
                 "owner preparation needs an outer host to create its own restrictive sandbox")
class OwnerUpgradeTests(unittest.TestCase):
    def setUp(self):
        fixture = test_runtime.RuntimeTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.record, self.repo, self.root = fixture.record, fixture.repo, fixture.root
        self.original = runtime.activate(self.record, "alice")
        self.initial_authority = copy.deepcopy(self.record.read()[0]["wake_policy"])
        source = self.repo / "house/model.py"
        source.write_text(source.read_text() + "\n# Synthetic reviewed owner maintenance fixture.\n")
        (self.repo / "tests/test_small.py").write_text(
            "import unittest\nclass Tiny(unittest.TestCase):\n def test_actual_execution(self): self.assertEqual(2+2,4)\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Reviewed owner fixture")
        approval = self.root / "owner.txt"; approval.write_text(maintenance.OPENCODE_APPROVAL)
        self.plan = owner_upgrade.prepare(self.record, "alice", maintenance.RETRY_SCOPE,
                                           approval, git(self.repo, "rev-parse", "HEAD"))

    def apply(self):
        with patch("house.owner_upgrade.authenticate_owner"):
            return owner_upgrade.apply(self.record, self.plan)

    def test_lost_response_after_append_resumes_exact_authorization(self):
        with patch("house.owner_upgrade.atomic_json", side_effect=OSError("power loss")):
            with self.assertRaisesRegex(OSError, "power loss"):
                self.apply()
        state, _, head = self.record.read()
        self.assertIn(maintenance.RETRY_SCOPE, state["maintenance"]["migrations"])
        self.assertEqual(runtime.selected(self.record), self.original)
        with patch("house.owner_upgrade.authenticate_owner", side_effect=AssertionError("no new authorization")):
            recovered = owner_upgrade.apply(self.record, self.plan)
        self.assertTrue(recovered["receipt"]["replayed"])
        self.assertEqual(self.record.read()[2], head)
        self.assertEqual(runtime.selected(self.record), recovered["runtime"])
        self.assertEqual(self.record.read()[0]["wake_policy"], self.initial_authority)
        self.assertTrue(self.apply()["receipt"]["replayed"])
        self.assertEqual(self.record.read()[2], head)
        with self.assertRaisesRegex(ValueError, "tested later"):
            runtime.activate(self.record, "alice")

    def test_failure_before_append_keeps_original_pointer_and_record(self):
        head = self.record.read()[2]
        with patch.object(self.record, "append", side_effect=OSError("before append")):
            with self.assertRaisesRegex(OSError, "before append"):
                self.apply()
        self.assertEqual(self.record.read()[2], head)
        self.assertEqual(runtime.selected(self.record), self.original)
        self.assertFalse(self.apply()["receipt"]["replayed"])

    def test_live_coordinator_and_dirty_source_prevent_migration(self):
        head = self.record.read()[2]
        with single_coordinator(self.record.common / "house-home"):
            with self.assertRaises((BlockingIOError, ValueError)):
                self.apply()
        (self.repo / "house/model.py").write_text("# unrelated dirty source\n")
        with self.assertRaisesRegex(ValueError, "clean committed"):
            self.apply()
        self.assertEqual(self.record.read()[2], head)
        self.assertEqual(runtime.selected(self.record), self.original)

    def test_failed_or_all_skipped_test_output_is_not_a_proof(self):
        for raw, status in ((b"\nRan 2 tests in 0.1s\n\nOK (skipped=2)\n", 0),
                            (b"\nRan 2 tests in 0.1s\n\nFAILED (errors=1)\n", 1),
                            (b"\nRan 2 tests in 0.1s\n\nOK\n", 1)):
            with self.assertRaisesRegex(ValueError, "execute and pass"):
                owner_upgrade.passed_count(raw, status)

    def test_changed_archive_and_previous_runtime_reject(self):
        data = json.loads(self.plan.read_text())
        data["migration"]["previous_runtime_sha256"] = "1" * 64
        data["previous_runtime"]["runtime_sha256"] = "1" * 64
        self.plan.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "runtime changed since"):
            self.apply()
        target = Path(data["target_runtime"]["entry"])
        with target.open("ab") as output:
            output.write(b"damaged")
        with self.assertRaisesRegex(ValueError, "runtime bytes changed"):
            self.apply()
