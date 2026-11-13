"""Naming repairs preserve the existing house and confer no provider authority."""
import copy
import unittest

from house import maintenance as owner
from tests import test_owner_launcher as fixtures


class OwnerNamesTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerLauncherTests()
        self.prior.setUp()
        self.h = self.prior.h
        self.h.state["maintenance"]["resident_returns"] = True

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return self.prior.migration | {
            "scope": owner.NAMING_SCOPE,
            "protected_files": old | {name: "9" * 64 for name in owner.ALLOWED_CHANGES[owner.NAMING_SCOPE]},
            "previous_manifest_sha256": owner.fingerprint(old),
        }

    def test_enables_names_without_renaming_anyone_or_changing_authority(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-migrate", self.migration())
        after = self.h.state
        self.assertTrue(after["maintenance"]["resident_names"])
        self.assertTrue(after["maintenance"]["resident_returns"])
        self.assertTrue(after["maintenance"]["room_growth"])
        for key in ("residents", "tasks", "lessons", "life", "rules", "rule_revision", "council", "proposals", "wake_policy"):
            self.assertEqual(after.get(key), before.get(key), key)
        self.assertEqual(after["maintenance"]["releases"], before["maintenance"]["releases"])
        for key, value in before["maintenance"]["migrations"].items():
            self.assertEqual(after["maintenance"]["migrations"][key], value)

    def test_scope_preserves_other_pins_and_cannot_release_a_provider(self):
        good = self.migration()
        for name in ("house/council.py", "house/providers.py", "house/life.py", "house/opencode_auth.py"):
            changed = copy.deepcopy(good)
            changed["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", changed, "outside.*scope")
        changed = copy.deepcopy(good)
        del changed["protected_files"]["house/opencode_auth.py"]
        self.h.reject("owner-migrate", changed, "replacement manifest")
        self.h.event("owner-migrate", good)
        self.h.reject("owner-migrate", good, "already used")
        self.h.reject("owner-provider-release", self.prior.f.release() | {
            "scope": owner.NAMING_SCOPE, "approval_sha256": owner.GROWTH_SHA256}, "only approved OpenCode")


if __name__ == "__main__":
    unittest.main()
