"""Ready work changes dispatch source, never owner limits or earlier pins."""
import copy
import unittest

from house import maintenance as owner
from tests import test_owner_checkpoints as fixtures


class OwnerBacklogTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerCheckpointTests()
        self.prior.setUp()
        self.h = self.prior.h
        self.h.event("owner-migrate", self.prior.migration())

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return self.prior.prior.migration | {"scope": owner.BACKLOG_SCOPE,
            "protected_files": old | {name: "7" * 64 for name in owner.ALLOWED_CHANGES[owner.BACKLOG_SCOPE]},
            "previous_manifest_sha256": owner.fingerprint(old)}

    def test_scope_preserves_history_authority_quotas_and_checkpoint_module(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-migrate", self.migration())
        for key in ("residents", "tasks", "lessons", "life", "rules", "rule_revision",
                    "council", "proposals", "wake_policy"):
            self.assertEqual(self.h.state.get(key), before.get(key), key)
        for key in ("releases", "resident_returns", "resident_names", "room_growth"):
            self.assertEqual(self.h.state["maintenance"][key], before["maintenance"][key])
        for key, value in before["maintenance"]["migrations"].items():
            self.assertEqual(self.h.state["maintenance"]["migrations"][key], value)
        self.assertEqual(owner.protected_manifest(self.h.state)["house/checkpoint.py"],
                         owner.protected_manifest(before)["house/checkpoint.py"])
        self.assertEqual(set(owner.protected_manifest(self.h.state)), set(owner.protected_manifest(before)))

    def test_scope_cannot_change_other_boundaries_or_release_provider(self):
        good = self.migration()
        for name in ("house/checkpoint.py", "house/integrate.py", "house/owner_upgrade.py",
                     "house/council.py", "house/providers.py", "house/wake_policy.py"):
            bad = copy.deepcopy(good); bad["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        self.h.event("owner-migrate", good)
        self.h.reject("owner-migrate", good, "already used")
        self.h.reject("owner-provider-release", self.prior.prior.f.release() | {
            "scope": owner.BACKLOG_SCOPE, "approval_sha256": owner.GROWTH_SHA256},
            "only approved OpenCode")
