"""One exact expired-key retry; synthetic history is not a live provider proof."""
import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from house import life, maintenance as owner, owner_upgrade
from tests import test_owner_backlog as fixtures


class OwnerKeyTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerBacklogTests(); self.prior.setUp()
        self.h = self.prior.h
        self.launcher = self.prior.prior.prior
        self.f = self.launcher.f
        self.proof = owner.FAILED_ATTEMPTS[owner.BACKLOG_SCOPE]
        self.h.event("owner-provider-release", self.launcher.release())
        while self.h.state["sequence"] < 591:
            self.h.event("say", {"text": "Synthetic history"})
        self.h.event("life", self.f.start(self.proof.run), "watch-keeper")
        self.h.event("life", {"kind": "run-launched", "run": self.proof.run, "pgid": 12347}, "watch-keeper")
        self.h.event("life", {"kind": "budget", "agent": "opencode", "until": owner.KEY_BUDGET_UNTIL,
                              "reason": "Synthetic expired key"}, "watch-keeper")
        self.h.event("say", {"text": "Synthetic observed expired-key response"}, "watch-keeper")
        self.h.event("life", {"kind": "run-finish", "run": self.proof.run, "outcome": "failed",
                              "exit_code": 1, "usage": {}, "elapsed_seconds": 16.4}, "watch-keeper")
        self.assertEqual(self.h.state["sequence"], 596)
        self.migration = self.prior.migration()
        self.h.event("owner-migrate", self.migration)

    def release(self):
        return self.f.release() | {"scope": owner.BACKLOG_SCOPE, "approval_sha256": owner.BACKLOG_SHA256,
            "expected_sequence": owner.KEY_BUDGET_SEQUENCE, "expected_until": owner.KEY_BUDGET_UNTIL,
            "expected_observation": self.proof.observation, "failed_run": self.proof.run,
            "failed_output_sha256": self.proof.output_sha256}

    def test_exact_one_use_preserves_all_old_credits_failure_and_hold(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-provider-release", self.release())
        self.h.event("life", self.f.start("new-owner-key"), "watch-keeper")
        self.h.reject("life", self.f.start("second-key-run"), "cooling down", "watch-keeper")
        self.h.reject("owner-provider-release", self.release(), "already used")
        self.assertEqual(self.h.state["life"]["budgets"], before["life"]["budgets"])
        for key, value in before["maintenance"]["releases"].items():
            self.assertEqual(self.h.state["maintenance"]["releases"][key], value)
        self.assertEqual(self.h.state["life"]["runs"][self.proof.run], before["life"]["runs"][self.proof.run])

    def test_wrong_tuple_provider_proof_and_uncertain_usage_reject(self):
        for change, error in (({"agent": "muse"}, "OpenCode"),
                ({"expected_sequence": 300}, "approved hold"),
                ({"expected_sequence": 594.0}, "approved hold"),
                ({"expected_until": owner.RETRY_BUDGET_UNTIL}, "approved hold"),
                ({"failed_run": owner.FAILED_CLI_RUN}, "exact spent"),
                ({"failed_output_sha256": "0" * 64}, "exact spent"),
                ({"approval_sha256": owner.GROWTH_SHA256}, "approval")):
            self.h.reject("owner-provider-release", self.release() | change, error)
        self.h.state["life"]["runs"][self.proof.run]["usage"] = {"input_tokens": 1}
        self.h.reject("owner-provider-release", self.release(), "uncertain failure")

    def test_later_failure_invalidates_granted_and_ungranted_credit(self):
        before = copy.deepcopy(self.h.state)
        for granted in (False, True):
            self.h.state = copy.deepcopy(before)
            if granted:
                self.h.event("owner-provider-release", self.release())
            self.h.event("life", {"kind": "budget", "agent": "opencode", "until": self.h.now + 1,
                                  "reason": "Later shorter failure"}, "watch-keeper")
            if not granted:
                self.h.reject("owner-provider-release", self.release(), "hold changed")
            self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))

    def test_operator_requires_exact_stdout_evidence_and_selected_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            common = Path(tmp).resolve() / ".git"
            directory = common / "house-home" / self.proof.run; directory.mkdir(parents=True)
            output = directory / "stdout.jsonl"; output.write_bytes(b"Synthetic 401")
            record = SimpleNamespace(common=common, read=lambda: (self.h.state, [], "head"), append=Mock())
            with patch.object(owner_upgrade, "authenticate_owner") as auth, \
                 patch.object(owner_upgrade.runtime, "selected", return_value={
                     "runtime_sha256": self.migration["runtime_sha256"]}) as selected, \
                 patch.object(owner_upgrade, "sha", return_value=self.proof.output_sha256) as sha:
                owner_upgrade.release_opencode(record, "alice", owner.BACKLOG_SCOPE)
                auth.assert_called_once(); sha.assert_called_once_with(b"Synthetic 401")
                record.append.assert_called_once_with("owner-provider-release", "alice", self.release(),
                                                       "owner-release-" + owner.BACKLOG_SCOPE)
                record.append.reset_mock()
                sha.return_value = "0" * 64
                with self.assertRaisesRegex(ValueError, "evidence changed"):
                    owner_upgrade.release_opencode(record, "alice", owner.BACKLOG_SCOPE)
                sha.return_value = self.proof.output_sha256
                selected.return_value = {"runtime_sha256": "0" * 64}
                with self.assertRaisesRegex(ValueError, "not selected"):
                    owner_upgrade.release_opencode(record, "alice", owner.BACKLOG_SCOPE)
                record.append.assert_not_called()
