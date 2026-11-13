"""A separately recorded repair grant never refunds the original spent permit."""
import copy
import unittest

from house import maintenance as owner, life
from tests import test_owner_maintenance as fixtures


class OwnerCLIRepairTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.OwnerMaintenanceTests(); self.f.setUp(); self.h = self.f.h
        self.h.event("owner-migrate", self.f.migration())
        self.h.event("owner-provider-release", self.f.release())
        while self.h.state["sequence"] < 461:
            self.h.event("say", {"text": "Synthetic history"})
        self.h.event("life", self.f.start(owner.FAILED_CLI_RUN), "watch-keeper")
        self.h.event("life", {"kind": "run-launched", "run": owner.FAILED_CLI_RUN, "pgid": 12345}, "watch-keeper")
        self.h.event("say", {"text": "Synthetic observed local CLI parser error"}, "watch-keeper")
        self.h.event("life", {"kind": "budget", "agent": "opencode", "until": self.h.now + 300,
                              "reason": "failed"}, "watch-keeper")
        self.h.event("life", {"kind": "run-finish", "run": owner.FAILED_CLI_RUN, "outcome": "failed",
                              "exit_code": 1, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        self.assertEqual(self.h.state["sequence"], 466)
        migration = self.f.migration() | {"scope": owner.REPAIR_SCOPE, "approval_sha256": owner.GROWTH_SHA256}
        migration["protected_files"]["house/providers.py"] = "f" * 64
        migration["protected_files"]["house/opencode_auth.py"] = "a" * 64
        self.h.event("owner-migrate", migration)

    def release(self):
        return self.f.release() | {"scope": owner.REPAIR_SCOPE, "approval_sha256": owner.GROWTH_SHA256,
            "expected_observation": owner.FAILED_CLI_OBSERVATION,
            "failed_run": owner.FAILED_CLI_RUN, "failed_output_sha256": owner.FAILED_CLI_SHA256}

    def test_separate_repair_credit_keeps_old_failure_and_spent_credit(self):
        old = copy.deepcopy(self.h.state["maintenance"]["releases"][owner.RETRY_SCOPE])
        budget = copy.deepcopy(self.h.state["life"]["budgets"]["opencode"])
        self.h.event("owner-provider-release", self.release())
        self.h.event("life", self.f.start("corrected-cli"), "watch-keeper")
        self.h.reject("life", self.f.start("extra-attempt"), "cooling down", "watch-keeper")
        self.h.reject("owner-provider-release", self.release(), "already used")
        self.assertEqual(self.h.state["maintenance"]["releases"][owner.RETRY_SCOPE], old)
        self.assertEqual(self.h.state["life"]["budgets"]["opencode"], budget)
        self.assertEqual(self.h.state["life"]["runs"][owner.FAILED_CLI_RUN]["outcome"], "failed")

    def test_uncertain_or_model_attempt_and_changed_error_evidence_are_rejected(self):
        before = copy.deepcopy(self.h.state)
        for change in ({"usage": {"output_tokens": 1}}, {"exit_code": 0}, {"outcome": "interrupted"}):
            self.h.state = copy.deepcopy(before)
            self.h.state["life"]["runs"][owner.FAILED_CLI_RUN].update(change)
            self.h.reject("owner-provider-release", self.release(), "uncertain failure")
        self.h.state = before
        self.h.reject("owner-provider-release", self.release() | {"failed_output_sha256": "0" * 64}, "exact spent")
        self.h.reject("owner-provider-release", self.release() | {"expected_observation": 465.0}, "exact spent")
        failed = self.h.state["life"]["runs"][owner.FAILED_CLI_RUN]
        self.h.event("arrive", {"name": "Synthetic late arrival"}, failed["resident"])
        self.h.reject("owner-provider-release", self.release(), "uncertain failure")

    def test_late_arrival_invalidates_an_already_granted_credit(self):
        self.h.event("owner-provider-release", self.release())
        failed = self.h.state["life"]["runs"][owner.FAILED_CLI_RUN]
        self.h.event("arrive", {"name": "Synthetic late arrival"}, failed["resident"])
        self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))
        self.h.reject("life", self.f.start("after-late-arrival"), "cooling down", "watch-keeper")
        grant = self.h.state["maintenance"]["releases"][owner.REPAIR_SCOPE]
        self.assertNotIn("consumed_run", grant)

    def test_new_failure_invalidates_repair_credit_before_or_after_grant(self):
        before = copy.deepcopy(self.h.state)
        failure = {"kind": "budget", "agent": "opencode", "until": self.h.now + 1, "reason": "New shorter failure"}
        self.h.event("life", failure, "watch-keeper")
        self.h.reject("owner-provider-release", self.release(), "hold changed")
        self.h.state = before
        self.h.event("owner-provider-release", self.release())
        self.h.event("life", failure, "watch-keeper")
        self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))
        self.h.reject("life", self.f.start("stale-repair"), "cooling down", "watch-keeper")
