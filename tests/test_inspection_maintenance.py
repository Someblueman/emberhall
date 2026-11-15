"""Concurrent inspection preserves the fixed owner boundary."""
import copy
import hashlib
from pathlib import Path
import unittest
from house import maintenance as owner
from tests import test_owner_maintenance


class InspectionMaintenanceTests(unittest.TestCase):
    def test_narrow_one_use_scope_enrolls_core_and_preserves_authority(self):
        fixture = test_owner_maintenance.OwnerMaintenanceTests(); fixture.setUp()
        h = fixture.h
        h.event("owner-migrate", fixture.migration())
        old = owner.protected_manifest(h.state)
        scope = owner.INSPECTION_SCOPE
        data = fixture.migration() | {"scope": scope, "approval_sha256": owner.SOURCES[scope],
            "protected_files": old | {p: "f" * 64 for p in owner.ALLOWED_CHANGES[scope]}}
        path = Path(__file__).parents[1] / "evidence/source-inspection-lane/owner-scope.md"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), data["approval_sha256"])
        missing = copy.deepcopy(data); missing["protected_files"].pop("house/mailbox_jobs.py")
        h.reject("owner-migrate", missing, "manifest")
        for name in ("house/providers.py", "house/council.py", "house/steward.py", "house/wake_policy.py",
                     "house/windows.py", "house/home.py", "house/model.py", "house/life.py"):
            bad = copy.deepcopy(data); bad["protected_files"][name] = "0" * 64
            h.reject("owner-migrate", bad, "outside.*scope|invalid replacement manifest")
        h.reject("owner-migrate", data | {"approval_sha256": "0" * 64}, "approval")
        h.reject("owner-migrate", data | {"test_count": 0}, "passing tests")
        h.reject("owner-migrate", data, "owner", "bob")
        before = copy.deepcopy(h.state)
        h.event("owner-migrate", data)
        for key in ("council", "proposals", "wake_policy", "rules", "rule_revision", "life", "tasks", "shelf"):
            self.assertEqual(before.get(key), h.state.get(key))
        h.reject("owner-migrate", data, "already used")
