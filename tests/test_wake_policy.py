"""Synthetic council/lifecycle fixtures and real test subprocesses; no live approvals."""
import os
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
import uuid

from house import council, wake_policy as policy
from house.governance import canonical, digest
from house.record import Record
from tests import test_council as fixtures
from tests.support import HouseCase


def approval(source="Synthetic fixture"):
    return policy.approval(source, {"source_head": "a" * 40,
                                   "files": {name: "b" * 64 for name in policy.PROTECTED_FILES}})


def artifact(body):
    return {"sha256": hashlib.sha256(body).hexdigest(), "base64": base64.b64encode(body).decode()}


class WakePolicyTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.CouncilTests()
        self.h.setUp()
        self.h.authorize()

    def authorize(self):
        self.h.event("council-wake-authorize", approval("Pinned owner fixture"))

    def enact(self, name="prompt-one", value="Follow the garden ambition."):
        h = self.h
        h.event("council-propose", {"proposal": name, "mode": "wake-prompt", "title": name,
            "text": value, "reason": "A useful trial", "base": h.state["rule_revision"]})
        h.trial(name); h.endorse(name); h.endorse(name, "carol"); h.notice(name)
        h.now += council.WAIT_SECONDS
        h.sync(); h.enact(name)

    def start(self):
        h = self.h
        h.event("arrive", {"name": "Controller"}, "watch-keeper")
        h.now += 1
        h.event("life", {"kind": "run-start", "run": "later", "resident": "eve",
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
            "workspace": "residents/later", "policy_revision": policy.active_policy(h.state)["revision"],
            "mode": "work"}, "watch-keeper")
        h.event("life", {"kind": "run-launched", "run": "later", "pgid": 12345}, "watch-keeper")
        h.event("arrive", {"name": "Eve"}, "eve")

    def completed_report(self, changes=None):
        h = self.h
        active = policy.active_policy(h.state)
        manifest = {**self.h.state["wake_policy"]["protected_files"], "tests/test_case.py": "c" * 64}
        output = b"Ran 1 test in 0.001s\n\nOK\n"
        report = {"format": "emberhall-runtime-test-v1", "house": h.state["house_id"],
            "resident": "eve", "run": "later", "proposal": active["proposal"],
            "policy_revision": active["revision"], "envelope_sha256": policy.ENVELOPE_SHA256,
            "source_head": "a" * 40, "source_sha256": digest(canonical(manifest).decode()),
            "files": manifest, "command": [str(Path(sys.executable).resolve()), *policy.TEST_ARGS],
            "exit_code": 0, "test_count": 1, "started_at": h.now, "finished_at": h.now,
            "output_sha256": hashlib.sha256(output).hexdigest()}
        report.update(changes or {})
        h.event("task", {"task": "runtime-check", "title": "Test runtime", "description": "Fixture"}, "eve")
        h.event("claim", {"task": "runtime-check", "token": "test-token", "expect": 0, "seconds": 60}, "eve")
        h.event("finish", {"task": "runtime-check", "token": "test-token", "result": "Fixture receipt",
            "artifacts": {policy.REPORT_NAME: artifact(canonical(report) + b"\n"),
                          "runtime-test-output.txt": artifact(output)}}, "eve")

    def test_explicit_exact_authorization_preserves_prior_rules_and_limits(self):
        h = self.h
        original = copy.deepcopy(h.state)
        for key in ("source_sha256", "prompt_sha256", "envelope_sha256"):
            h.reject("council-wake-authorize", approval("Fixture") | {key: "0" * 64}, "authorization")
        with self.assertRaisesRegex(ValueError, "not authorized"):
            policy.active_prompt(h.state)
        self.authorize()
        for key in ("rules", "rule_revision", "council", "tasks", "proposals"):
            self.assertEqual(h.state[key], original[key])
        h.reject("council-wake-authorize", approval("Again"), "already")
        self.assertIn("STEWARD-PROTECTED", policy.active_prompt(h.state))
        self.assertIsNone(policy.active_policy(h.state)["proposal"])

    def test_wake_prompt_uses_all_existing_gates_and_cannot_set_protected_fields(self):
        h = self.h
        proposal = {"proposal": "prompt", "mode": "wake-prompt", "title": "Prompt",
                    "text": "Grow", "reason": "Trial", "base": h.state["rule_revision"]}
        h.reject("council-propose", proposal, "authorization")
        self.authorize()
        h.reject("council-propose", proposal | {"envelope_sha256": "0" * 64}, "fields")
        h.reject("council-propose", proposal | {"mode": "protected-limits"}, "only additive")
        h.event("council-propose", proposal)
        h.reject("council-enact", {"proposal": "prompt"}, "no trial")
        h.trial("prompt"); h.endorse("prompt"); h.notice("prompt")
        h.now += council.WAIT_SECONDS; h.sync()
        h.reject("council-enact", {"proposal": "prompt"}, "two independent")
        h.endorse("prompt", "carol"); h.enact("prompt")
        self.assertEqual(policy.active_policy(h.state)["text"], "Grow")
        self.assertEqual(policy.active_policy(h.state)["protected_limits"], policy.OWNER_LIMITS)

    def test_new_prompt_supersedes_old_and_repeal_returns_to_authorized_baseline(self):
        self.authorize(); self.enact()
        first = policy.active_policy(self.h.state)["revision"]
        self.enact("prompt-two", "Follow the archive ambition.")
        self.assertEqual(self.h.state["proposals"]["prompt-one"]["status"], "superseded")
        self.assertNotEqual(policy.active_policy(self.h.state)["revision"], first)
        self.h.sync([self.h.comment("REPEAL prompt-two")])
        self.assertEqual(policy.active_policy(self.h.state)["text"], policy.INITIAL_PROMPT)
        self.assertIsNone(policy.active_policy(self.h.state)["proposal"])

    def test_draft_and_unlaunched_or_earlier_or_foreign_wakes_do_not_qualify(self):
        self.authorize()
        with self.assertRaisesRegex(ValueError, "enacted"):
            policy.later_wake(self.h.state, "alice", "later")
        self.enact(); self.start()
        policy.later_wake(self.h.state, "eve", "later")
        for changes, message in (({"launched_sequence": None}, "launched"),
                ({"started_sequence": 1}, "before"), ({"resident": "alice"}, "assigned"),
                ({"status": "completed"}, "launched"), ({"policy_revision": "old"}, "revision")):
            state = copy.deepcopy(self.h.state)
            state["life"]["runs"]["later"].update(changes)
            with self.assertRaisesRegex(ValueError, message):
                policy.later_wake(state, "eve", "later")

    def test_test_report_requires_actual_outcome_identity_time_and_output(self):
        self.authorize(); self.enact(); self.start()
        before = copy.deepcopy(self.h.state)
        for changes, message in (({"exit_code": 1}, "did not pass"),
                ({"exit_code": False}, "did not pass"), ({"test_count": 0}, "did not pass"),
                ({"run": "another"}, "binding"), ({"envelope_sha256": "0" * 64}, "binding"),
                ({"source_sha256": "0" * 64}, "source identity"),
                ({"started_at": self.h.now - 1}, "clock"),
                ({"finished_at": self.h.now + 1}, "clock"),
                ({"command": ["python", "-c", "pass"]}, "command"),
                ({"output_sha256": "0" * 64}, "output")):
            with self.subTest(changes=changes):
                self.h.state = copy.deepcopy(before)
                self.completed_report(changes)
                self.h.reject("council-runtime-tested", {"task": "runtime-check", "run": "later"}, message, "eve")
        self.h.state = before
        self.completed_report()
        self.h.event("council-runtime-tested", {"task": "runtime-check", "run": "later"}, "eve")
        self.h.reject("council-runtime-tested", {"task": "runtime-check", "run": "later"}, "already", "eve")
        self.h.sync([self.h.comment("REPEAL prompt-one")])
        with self.assertRaisesRegex(ValueError, "enacted"):
            policy.report_for(self.h.state, "eve", "later", "runtime-check")


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host-only sandbox boundary fixture cannot nest macOS sandboxes")
class RuntimeProcessTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = Record(self.new_repo("approved"))
        self.source = self.new_repo("source")
        (self.source / "house").mkdir(); (self.source / "tests").mkdir()
        for name in policy.PROTECTED_FILES:
            (self.source / name).write_text("# Test fixture, not a deployable runtime\n")
        (self.source / "tests/test_example.py").write_text(
            "import unittest\nclass Example(unittest.TestCase):\n    def test_real(self): self.assertEqual(2+2,4)\n")
        self.git("add", "."); self.git("-c", "commit.gpgsign=false", "commit", "-m", "fixture")
        old = time.time() - council.WAIT_SECONDS - 5
        with patch("house.record.time.time", return_value=old), patch(
                "house.record.uuid.uuid4", side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
            self.record.found("Synthetic runtime fixture", "Fixture charter")
        with patch("house.record.time.time", return_value=old):
            for actor in ("alice", "bob", "carol", "watch-keeper"):
                self.record.append("arrive", actor, {"name": actor})
            self.record.append("council-authorize", "alice", fixtures.approval())
            self.record.append("council-wake-authorize", "alice", policy.approval("Synthetic fixture", policy.source_snapshot(self.source)))
            state = self.record.read()[0]
            self.record.append("council-propose", "alice", {"proposal": "new-wake", "mode": "wake-prompt",
                "title": "New wake", "text": "Grow the test garden", "reason": "Fixture", "base": state["rule_revision"]})
            self.claim_task("trial", "alice")
            self.record.append("finish", "alice", {"task": "trial", "token": "trial", "result": "Fixture",
                "artifacts": {"fixture.txt": artifact(b"A simulated pre-enactment trial")}})
            self.record.append("council-trial", "alice", {"proposal": "new-wake", "task": "trial", "evidence": "Synthetic"})
            for actor in ("bob", "carol"):
                self.record.append("council-endorse", actor, {"proposal": "new-wake", "evidence": "Synthetic"})
            self.record.append("council-notice", "alice", {"proposal": "new-wake", "repository": council.REPOSITORY,
                "issue": council.ISSUE, "comment_id": 1, "text_sha256": digest("Grow the test garden")})
        self.record.append("council-sync", "alice", {"repository": council.REPOSITORY,
            "issue": council.ISSUE, "owner_id": council.OWNER_ID, "checked_at": time.time(), "comments": []})
        self.record.append("council-enact", "alice", {"proposal": "new-wake"})
        active = policy.active_policy(self.record.read()[0])
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": "later", "resident": "eve",
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": policy.source_snapshot(self.source)["source_head"],
            "workspace": "residents/later", "policy_revision": active["revision"], "mode": "work"})
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": "later", "pgid": 12345})
        self.record.append("arrive", "eve", {"name": "Eve"})
        self.claim_task("runtime-check", "eve")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.source), *args], check=True, capture_output=True).stdout

    def claim_task(self, name, actor):
        self.record.append("task", actor, {"task": name, "title": name, "description": "Fixture task"})
        self.record.append("claim", actor, {"task": name, "token": name, "expect": 0, "seconds": 300})

    def run_tests(self):
        return policy.test_runtime(self.record, "eve", "later", "runtime-check", "runtime-check", self.source)

    def test_real_subprocess_receipt_binds_clean_commit_and_later_wake(self):
        result = self.run_tests()
        self.assertTrue(result["tested"])
        gate = policy.refresh_gate(self.record, "eve", "runtime-check", "later", self.source)
        self.assertEqual(gate["source_head"], self.git("rev-parse", "HEAD").decode().strip())
        self.assertEqual(gate["policy_revision"], policy.active_policy(self.record.read()[0])["revision"])
        (self.source / "house/council.py").write_text("# Untested bytes\n")
        with self.assertRaisesRegex(ValueError, "clean committed"):
            policy.refresh_gate(self.record, "eve", "runtime-check", "later", self.source)
        self.git("add", "."); self.git("-c", "commit.gpgsign=false", "commit", "-m", "changed")
        with self.assertRaisesRegex(ValueError, "protected enforcement"):
            policy.refresh_gate(self.record, "eve", "runtime-check", "later", self.source)

    def test_failed_real_tests_preserve_output_but_grant_no_refresh(self):
        (self.source / "tests/test_example.py").write_text(
            "import unittest\nclass Example(unittest.TestCase):\n    def test_bad(self): self.fail('real fixture failure')\n")
        self.git("add", "."); self.git("-c", "commit.gpgsign=false", "commit", "-m", "failing fixture")
        self.assertFalse(self.run_tests()["tested"])
        state = self.record.read()[0]
        self.assertEqual(state["tasks"]["runtime-check"]["status"], "done")
        self.assertEqual(state["wake_policy"]["tests"], {})
        with self.assertRaisesRegex(ValueError, "did not pass"):
            policy.refresh_gate(self.record, "eve", "runtime-check", "later", self.source)

    def test_protected_edits_cannot_be_blessed_by_green_tests(self):
        (self.source / "house/providers.py").write_text("# Would weaken a sandbox\n")
        self.git("add", "."); self.git("-c", "commit.gpgsign=false", "commit", "-m", "changed boundary")
        with self.assertRaisesRegex(ValueError, "protected enforcement"):
            self.run_tests()
        self.assertEqual(self.record.read()[0]["tasks"]["runtime-check"]["status"], "claimed")

    def test_entirely_skipped_suite_cannot_authorize_runtime_refresh(self):
        (self.source / "tests/test_example.py").write_text(
            "import unittest\n@unittest.skip('fixture')\nclass Example(unittest.TestCase):\n"
            "    def test_skipped(self): pass\n")
        self.git("add", "."); self.git("-c", "commit.gpgsign=false", "commit", "-m", "skipped fixture")
        self.assertFalse(self.run_tests()["tested"])
        self.assertEqual(self.record.read()[0]["wake_policy"]["tests"], {})

    def test_unprotected_house_source_can_evolve_with_new_tested_commit(self):
        (self.source / "house/garden.py").write_text("# An improved visual room\n")
        self.git("add", "."); self.git("-c", "commit.gpgsign=false", "commit", "-m", "new room")
        self.assertTrue(self.run_tests()["tested"])
        gate = policy.refresh_gate(self.record, "eve", "runtime-check", "later", self.source)
        self.assertIn("house/garden.py", gate["files"])
