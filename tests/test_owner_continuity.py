"""Continuing identities do not confer authority or another provider admission."""
import copy
import unittest

from house import life, maintenance as owner
from tests import test_owner_launcher as fixtures


class OwnerContinuityTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerLauncherTests()
        self.prior.setUp()
        self.h = self.prior.h

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        manifest = dict(old)
        for name in owner.ALLOWED_CHANGES[owner.CONTINUITY_SCOPE]:
            manifest[name] = "9" * 64
        return self.prior.migration | {
            "scope": owner.CONTINUITY_SCOPE,
            "protected_files": manifest,
            "previous_manifest_sha256": owner.fingerprint(old),
        }

    def test_enable_returns_preserves_history_council_room_growth_and_spent_credits(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-migrate", self.migration())
        current = self.h.state
        self.assertTrue(current["maintenance"]["resident_returns"])
        self.assertTrue(current["maintenance"]["room_growth"])
        for key in ("residents", "life", "tasks", "rules", "rule_revision", "council", "proposals", "wake_policy"):
            self.assertEqual(current.get(key), before.get(key), key)
        self.assertEqual(current["maintenance"]["releases"], before["maintenance"]["releases"])
        for scope, prior in before["maintenance"]["migrations"].items():
            self.assertEqual(current["maintenance"]["migrations"][scope], prior)
        old = owner.protected_manifest(before)
        new = owner.protected_manifest(current)
        self.assertEqual(set(old), set(new))
        self.assertEqual({name for name in old if old[name] != new[name]},
                         owner.ALLOWED_CHANGES[owner.CONTINUITY_SCOPE])
        self.assertFalse(life.provider_available(current, "opencode", self.h.now))

    def test_scope_cannot_change_other_boundaries_or_remove_existing_pins(self):
        good = self.migration()
        for name in ("house/council.py", "house/providers.py", "house/opencode_auth.py", "house/building.py"):
            changed = copy.deepcopy(good)
            changed["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", changed, "outside.*scope")
        for added in (False, True):
            changed = copy.deepcopy(good)
            if added:
                changed["protected_files"]["house/unreviewed.py"] = "0" * 64
            else:
                del changed["protected_files"]["house/opencode_auth.py"]
            self.h.reject("owner-migrate", changed, "replacement manifest")

    def test_continuity_scope_never_releases_a_provider_or_replays_migration(self):
        good = self.migration()
        self.h.event("owner-migrate", good)
        self.h.reject("owner-migrate", good, "already used")
        release = self.prior.f.release() | {
            "scope": owner.CONTINUITY_SCOPE,
            "approval_sha256": owner.GROWTH_SHA256,
        }
        before = copy.deepcopy(self.h.state)
        self.h.reject("owner-provider-release", release, "only approved OpenCode")
        self.assertEqual(self.h.state, before)
        self.assertNotIn(owner.CONTINUITY_SCOPE, owner.RELEASE_SCOPES)


if __name__ == "__main__":
    unittest.main()
