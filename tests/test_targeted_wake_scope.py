"""One-use targeted-return maintenance leaves owner-only boundaries intact."""
import copy
import hashlib
from pathlib import Path
import unittest

from house import maintenance as owner
from tests import test_owner_maintenance


class TargetedWakeScopeTests(unittest.TestCase):
    def test_exact_scope_preserves_law_and_rejects_unrelated_changes(self):
        fixture = test_owner_maintenance.OwnerMaintenanceTests(); fixture.setUp()
        fixture.h.event("owner-migrate", fixture.migration())
        h = fixture.h
        old = owner.protected_manifest(h.state)
        scope = owner.TARGETED_WAKE_SCOPE
        self.assertEqual(owner.ALLOWED_CHANGES[scope],
                         {"house/maintenance.py", "house/life.py", "house/home.py"})
        data = fixture.migration() | {"scope": scope,
            "approval_sha256": owner.SOURCES[scope],
            "previous_manifest_sha256": owner.fingerprint(old),
            "protected_files": old | {p: "f" * 64 for p in owner.ALLOWED_CHANGES[scope]}}
        path = Path(__file__).parents[1] / "evidence/targeted-wakes/owner-scope.md"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), data["approval_sha256"])
        for name in ("house/providers.py", "house/council.py", "house/steward.py",
                     "house/wake_policy.py", "house/mailbox.py", "house/owner_upgrade.py"):
            bad = copy.deepcopy(data); bad["protected_files"][name] = "e" * 64
            h.reject("owner-migrate", bad, "outside.*scope")
        h.reject("owner-migrate", data | {"approval_sha256": "0" * 64}, "approval")
        h.reject("owner-migrate", data | {"test_count": 0}, "passing tests")
        h.reject("owner-migrate", data, "owner", "bob")
        before = copy.deepcopy(h.state)
        h.event("owner-migrate", data)
        self.assertIn(scope, h.state["maintenance"]["migrations"])
        for key in ("council", "proposals", "wake_policy", "rules", "rule_revision", "life", "tasks", "shelf"):
            self.assertEqual(before.get(key), h.state.get(key))
        h.reject("owner-migrate", data, "already used")
