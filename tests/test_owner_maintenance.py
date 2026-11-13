"""Synthetic clocks test owner maintenance; none are live approvals or elapsed life."""
import contextlib
import copy
import io
import unittest

from house import council, home, life, maintenance as owner, resident_actions, wake_policy
from tests import test_council
from tests.test_wake_policy import approval


class OwnerMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.h = test_council.CouncilTests(); self.h.setUp(); self.h.authorize()
        self.h.event("council-wake-authorize", approval())
        self.h.now = 1794600000
        self.h.event("arrive", {"name": "Controller"}, "watch-keeper")
        while self.h.state["sequence"] < 299:
            self.h.event("say", {"text": "Synthetic history"})
        self.h.event("life", {"kind": "budget", "agent": "opencode",
            "until": owner.RETRY_BUDGET_UNTIL, "reason": "Fixture expired credential"}, "watch-keeper")
        self.assertEqual(self.h.state["sequence"], 300)

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        manifest = old | {name: "d" * 64 for name in owner.OWNER_MODULES}
        manifest["house/model.py"] = "c" * 64
        return {"scope": owner.RETRY_SCOPE, "approval_sha256": owner.OPENCODE_SHA256,
            "house": self.h.state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64, "protected_files": manifest,
            "previous_manifest_sha256": owner.fingerprint(old), "previous_runtime_sha256": "c" * 64,
            "runtime_sha256": "d" * 64, "test_output_sha256": "e" * 64, "test_count": 1}

    def release(self):
        return {"scope": owner.RETRY_SCOPE, "approval_sha256": owner.OPENCODE_SHA256,
            "house": self.h.state["house_id"], "owner_id": council.OWNER_ID, "agent": "opencode",
            "expected_sequence": 300, "expected_until": owner.RETRY_BUDGET_UNTIL}

    def test_initial_authority_and_pending_council_are_unchanged(self):
        self.h.propose(); self.h.trial(); self.h.endorse(); self.h.notice()
        before = copy.deepcopy(self.h.state)
        policy = wake_policy.active_policy(before)
        self.h.event("owner-migrate", self.migration())
        for key in ("rules", "rule_revision", "council", "proposals", "wake_policy", "life"):
            self.assertEqual(self.h.state[key], before[key])
        self.assertEqual(wake_policy.active_policy(self.h.state), policy)
        manifest = owner.protected_manifest(self.h.state)
        wake_policy.protected_source(self.h.state, {"files": manifest})
        with self.assertRaisesRegex(ValueError, "protected enforcement"):
            wake_policy.protected_source(self.h.state, {"files": before["wake_policy"]["protected_files"]})
        self.h.reject("council-enact", {"proposal": "rule-one"}, "two independent")
        with self.assertRaisesRegex(ValueError, "enacted"):
            wake_policy.later_wake(self.h.state, "alice", "made-up")

    def test_wrong_owner_house_source_scope_and_test_claim_reject(self):
        good = self.migration()
        for patch, error in (({"house": "another"}, "house"), ({"owner_id": 0}, "owner"),
                ({"approval_sha256": "0" * 64}, "approval"), ({"test_count": 0}, "tests"),
                ({"previous_manifest_sha256": "0" * 64}, "stale")):
            self.h.reject("owner-migrate", good | patch, error)
        self.h.reject("owner-migrate", good, "owner", "bob")
        bad = copy.deepcopy(good); bad["protected_files"]["house/providers.py"] = "f" * 64
        self.h.reject("owner-migrate", bad, "outside.*scope")
        self.h.event("owner-migrate", good)
        self.h.reject("owner-migrate", good, "already used")

    def test_exact_hold_releases_once_without_claiming_success(self):
        prior = copy.deepcopy(self.h.state["life"]["budgets"]["opencode"])
        self.h.event("owner-migrate", self.migration())
        self.h.event("owner-provider-release", self.release())
        budget = self.h.state["life"]["budgets"]["opencode"]
        self.assertEqual(budget, prior)
        self.assertEqual(self.h.state["maintenance"]["releases"][owner.RETRY_SCOPE]["previous"], prior)
        self.assertEqual(self.h.state["life"]["runs"], {})
        self.assertTrue(life.provider_available(self.h.state, "opencode", self.h.now))
        self.h.reject("owner-provider-release", self.release(), "already used")

    def test_release_rejects_wrong_provider_hold_caller_time_and_expiry(self):
        self.h.event("owner-migrate", self.migration())
        good = self.release()
        for patch, error in (({"agent": "codex"}, "OpenCode"),
                ({"expected_sequence": 300.0}, "approved hold"),
                ({"expected_sequence": 301}, "approved hold"),
                ({"expected_until": owner.RETRY_BUDGET_UNTIL + 1}, "approved hold"),
                ({"until": self.h.now - 10}, "fields"), ({"at": self.h.now + 86400}, "fields")):
            self.h.reject("owner-provider-release", good | patch, error)
        self.h.now = owner.RETRY_BUDGET_UNTIL
        self.h.reject("owner-provider-release", good, "already elapsed")

    def test_new_failure_wins_and_future_backoff_remains_monotonic(self):
        self.h.event("owner-migrate", self.migration())
        self.h.event("life", {"kind": "budget", "agent": "opencode",
            "until": owner.RETRY_BUDGET_UNTIL + 900, "reason": "New observed failure"}, "watch-keeper")
        self.h.reject("owner-provider-release", self.release(), "hold changed")
        before = copy.deepcopy(self.h.state["life"]["budgets"]["opencode"])
        self.h.event("life", {"kind": "budget", "agent": "opencode",
            "until": self.h.now + 1, "reason": "Shorter ordinary request"}, "watch-keeper")
        self.assertEqual(self.h.state["life"]["budgets"]["opencode"], before)

    def test_active_native_run_prevents_schema_migration(self):
        self.h.state["life"]["runs"]["live-fixture"] = {"status": "active"}
        self.h.reject("owner-migrate", self.migration(), "drain native")

    def start(self, run):
        return {"kind": "run-start", "run": run, "resident": "resident-" + run,
            "agent": "opencode", "model": "opencode-go/kimi-k3.1-pro", "source_head": "a" * 40,
            "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "work"}

    def test_racing_starts_consume_one_credit_even_if_launch_crashes(self):
        self.h.event("owner-migrate", self.migration())
        self.h.event("owner-provider-release", self.release())
        self.assertEqual(home.choose_provider(self.h.state, self.h.now, "opencode"), "opencode")
        self.h.event("life", self.start("first"), "watch-keeper")
        permit = self.h.state["maintenance"]["releases"][owner.RETRY_SCOPE]
        self.assertEqual(permit["consumed_run"], "first")
        self.h.reject("life", self.start("second"), "cooling down", "watch-keeper")
        self.h.event("life", {"kind": "run-finish", "run": "first", "outcome": "interrupted",
            "exit_code": None, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        self.h.reject("life", self.start("third"), "cooling down", "watch-keeper")
        self.assertNotEqual(home.choose_provider(self.h.state, self.h.now, "opencode"), "opencode")
        self.h.now = owner.RETRY_BUDGET_UNTIL
        self.h.event("life", self.start("ordinary-later"), "watch-keeper")

    def test_new_shorter_failure_blocks_release_and_invalidates_granted_permit(self):
        self.h.event("owner-migrate", self.migration())
        before = copy.deepcopy(self.h.state)
        failure = {"kind": "budget", "agent": "opencode", "until": self.h.now + 60,
                   "reason": "A newer shorter failure"}
        self.h.event("life", failure, "watch-keeper")
        self.h.reject("owner-provider-release", self.release(), "hold changed")
        self.h.state = before
        self.h.event("owner-provider-release", self.release())
        self.h.event("life", failure, "watch-keeper")
        self.h.reject("life", self.start("invalidated"), "cooling down", "watch-keeper")
        self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))

    def test_resident_action_parser_has_no_owner_operations(self):
        with contextlib.redirect_stderr(io.StringIO()):
            for argv in (["owner-upgrade", "apply", "plan"],
                         ["council", "--as", "bob", "owner-migrate"],
                         ["council", "--as", "bob", "release-opencode"]):
                with self.assertRaises(SystemExit):
                    resident_actions.parse(argv, "bob")
