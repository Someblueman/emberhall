"""Retire the one verified auth incident; newer failures still stop admission."""
import copy
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from house import body, life, maintenance as owner
from house.model import apply_event
from tests import test_owner_key as fixtures


class OwnerRestoredTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        def captured(state, event):
            result = apply_event(state, event)
            self.events.append(copy.deepcopy(event))
            return result
        self.capture = patch("tests.test_council.apply_event", side_effect=captured)
        self.capture.start(); self.addCleanup(self.capture.stop)
        self.prior = fixtures.OwnerKeyTests(); self.prior.setUp()
        self.h, self.f = self.prior.h, self.prior.f
        self.h.event("owner-provider-release", self.prior.release())
        while self.h.state["sequence"] < 928:
            self.h.event("say", {"text": "Synthetic history"})
        self.h.event("life", self.f.start(owner.VERIFIED_KEY_RUN) | {
            "model": "opencode-go/deepseek-v4.1-flash"}, "watch-keeper")
        self.h.event("life", {"kind": "run-launched", "run": owner.VERIFIED_KEY_RUN,
                              "pgid": 12348}, "watch-keeper")
        resident = self.h.state["life"]["runs"][owner.VERIFIED_KEY_RUN]["resident"]
        self.h.event("arrive", {"name": "Juniper"}, resident)
        self.h.event("life", {"kind": "identity", "agent": "opencode",
                              "model": "opencode-go/deepseek-v4.1-flash"}, resident)
        while self.h.state["sequence"] < 956:
            self.h.event("say", {"text": "Synthetic history"})
        self.h.event("life", {"kind": "run-finish", "run": owner.VERIFIED_KEY_RUN,
            "outcome": "success", "exit_code": 0, "usage": {"input_tokens": 10, "output_tokens": 2},
            "elapsed_seconds": 365}, "watch-keeper")
        self.assertEqual(self.h.state["sequence"], 957)

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return self.prior.migration | {"scope": owner.RESTORED_SCOPE,
            "approval_sha256": owner.RESTORED_SHA256,
            "protected_files": old | {name: "8" * 64 for name in owner.ALLOWED_CHANGES[owner.RESTORED_SCOPE]},
            "previous_manifest_sha256": owner.fingerprint(old)}

    def test_retire_only_exact_hold_preserve_history_and_allow_normal_return(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-migrate", self.migration())
        self.assertNotIn("opencode", self.h.state["life"]["budgets"])
        expected = copy.deepcopy(before["life"]); del expected["budgets"]["opencode"]
        self.assertEqual(self.h.state["life"], expected)
        for key in ("residents", "tasks", "rules", "rule_revision", "council", "wake_policy"):
            self.assertEqual(self.h.state[key], before[key])
        self.assertEqual(self.h.state["maintenance"]["releases"], before["maintenance"]["releases"])
        restored = self.h.state["maintenance"]["provider_restored"]["opencode"]
        self.assertEqual(restored["previous"], before["life"]["budgets"]["opencode"])
        self.assertTrue(life.provider_available(self.h.state, "opencode", self.h.now))
        self.h.reject("owner-migrate", self.migration(), "already used")
        self.h.event("life", self.f.start("ordinary-return"), "watch-keeper")
        self.h.event("life", {"kind": "budget", "agent": "opencode", "until": self.h.now + 300,
                              "reason": "New failure after restored account"}, "watch-keeper")
        self.assertEqual(self.h.state["life"]["budgets"]["opencode"]["until"], self.h.now + 300)
        self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))
        self.h.reject("life", self.f.start("blocked-return"), "cooling down", "watch-keeper")

    def test_newer_shorter_failure_and_changed_budget_block_resolution(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("life", {"kind": "budget", "agent": "opencode", "until": self.h.now + 1,
                              "reason": "New shorter failure"}, "watch-keeper")
        self.h.reject("owner-migrate", self.migration(), "hold changed")
        self.h.state = before
        self.h.state["life"]["budgets"]["opencode"]["until"] += 1
        self.h.reject("owner-migrate", self.migration(), "hold changed")

    def test_uncertain_success_wrong_owner_and_unrelated_source_are_rejected(self):
        before = copy.deepcopy(self.h.state)
        for change in ({"outcome": "failed"}, {"exit_code": 1}, {"started_sequence": 930},
                       {"ended_sequence": 958}, {"usage": {}}, {"agent": "muse"},
                       {"model": "opencode-go/kimi-k3.1-pro"}):
            self.h.state = copy.deepcopy(before)
            self.h.state["life"]["runs"][owner.VERIFIED_KEY_RUN].update(change)
            self.h.reject("owner-migrate", self.migration(), "successful native")
        self.h.state = before
        self.h.reject("owner-migrate", self.migration(), "owner", "bob")
        bad = self.migration(); bad["protected_files"]["house/providers.py"] = "0" * 64
        self.h.reject("owner-migrate", bad, "outside.*scope")
        self.h.state["maintenance"]["releases"][owner.BACKLOG_SCOPE]["consumed_run"] = "different"
        self.h.reject("owner-migrate", self.migration(), "successful native")

    def test_public_history_preserves_old_hold_but_current_frame_removes_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            record = SimpleNamespace(root=root, read=lambda: (self.h.state, self.events, "synthetic-head"))
            old = body.export(record, self.h.now)
            self.assertIn("opencode", [b["agent"] for b in old["frames"][-1]["budgets"]])
            self.h.event("owner-migrate", self.migration())
            new = body.export(record, self.h.now)
            self.assertEqual(new["frames"][:-1], old["frames"])
            self.assertNotIn("opencode", [b["agent"] for b in new["frames"][-1]["budgets"]])
