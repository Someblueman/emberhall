"""Report scheduling maintenance preserves review authority and resident limits."""
import copy
import unittest

from house import maintenance as owner
from tests import test_owner_launcher as fixtures


class OwnerReportsTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerLauncherTests(); self.prior.setUp()
        self.h = self.prior.h
        self.h.state["maintenance"].update(resident_returns=True, resident_names=True)

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return self.prior.migration | {
            "scope": owner.REPORT_SCOPE,
            "protected_files": old | {name: "9" * 64 for name in owner.ALLOWED_CHANGES[owner.REPORT_SCOPE]},
            "previous_manifest_sha256": owner.fingerprint(old),
        }

    def test_report_scope_changes_only_source_pins(self):
        before = copy.deepcopy(self.h.state)
        self.h.event("owner-migrate", self.migration())
        after = self.h.state
        for key in ("residents", "tasks", "lessons", "life", "rules", "rule_revision", "council", "proposals", "wake_policy"):
            self.assertEqual(after.get(key), before.get(key), key)
        for key in ("releases", "resident_returns", "resident_names", "room_growth"):
            self.assertEqual(after["maintenance"][key], before["maintenance"][key])
        for key, value in before["maintenance"]["migrations"].items():
            self.assertEqual(after["maintenance"]["migrations"][key], value)

    def test_no_review_boundary_provider_or_other_scope_change(self):
        good = self.migration()
        for name in ("house/integrate.py", "house/model.py", "house/wake_policy.py", "house/council.py",
                     "house/providers.py", "house/owner_upgrade.py"):
            changed = copy.deepcopy(good); changed["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", changed, "outside.*scope")
        self.h.event("owner-migrate", good)
        self.h.reject("owner-migrate", good, "already used")
        self.h.reject("owner-provider-release", self.prior.f.release() | {
            "scope": owner.REPORT_SCOPE, "approval_sha256": owner.GROWTH_SHA256}, "only approved OpenCode")
