"""Checkpoint maintenance adds one pinned module without changing authority."""
import copy
import unittest

from house import maintenance as owner
from tests import test_owner_launcher as fixtures


class OwnerCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerLauncherTests()
        self.prior.setUp()
        self.h = self.prior.h
        self.h.state["maintenance"].update(resident_returns=True, resident_names=True)

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return self.prior.migration | {
            "scope": owner.CHECKPOINT_SCOPE,
            "protected_files": old | {
                name: "9" * 64 for name in owner.ALLOWED_CHANGES[owner.CHECKPOINT_SCOPE]},
            "previous_manifest_sha256": owner.fingerprint(old),
        }

    def test_one_new_pin_preserves_rules_residents_limits_and_prior_migrations(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-migrate", self.migration())
        after = self.h.state
        for key in ("residents", "tasks", "lessons", "life", "rules", "rule_revision",
                    "council", "proposals", "wake_policy"):
            self.assertEqual(after.get(key), before.get(key), key)
        for key in ("releases", "resident_returns", "resident_names", "room_growth"):
            self.assertEqual(after["maintenance"][key], before["maintenance"][key])
        for key, value in before["maintenance"]["migrations"].items():
            self.assertEqual(after["maintenance"]["migrations"][key], value)
        self.assertEqual(set(owner.protected_manifest(after)) - set(owner.protected_manifest(before)),
                         {"house/checkpoint.py"})

    def test_manifest_is_exact_and_scope_cannot_change_authority_or_release_provider(self):
        good = self.migration()
        for name in ("house/integrate.py", "house/model.py", "house/wake_policy.py",
                     "house/council.py", "house/providers.py", "house/mailbox.py"):
            bad = copy.deepcopy(good)
            bad["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        bad = copy.deepcopy(good)
        del bad["protected_files"]["house/checkpoint.py"]
        self.h.reject("owner-migrate", bad, "replacement manifest")
        bad = copy.deepcopy(good)
        bad["protected_files"]["house/unapproved.py"] = "0" * 64
        self.h.reject("owner-migrate", bad, "replacement manifest")
        self.h.event("owner-migrate", good)
        self.h.reject("owner-migrate", good, "already used")
        self.h.reject("owner-provider-release", self.prior.f.release() | {
            "scope": owner.CHECKPOINT_SCOPE, "approval_sha256": owner.GROWTH_SHA256},
            "only approved OpenCode")
