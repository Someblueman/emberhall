"""The coordinator repair upgrade preserves owner and council boundaries."""
import copy
import hashlib
from pathlib import Path
import unittest
from house import maintenance
from tests import test_owner_maintenance


class CoordinatorRepairsMaintenanceTests(unittest.TestCase):
    def test_exact_scope_preserves_house_authority(self):
        fixture = test_owner_maintenance.OwnerMaintenanceTests()
        fixture.setUp()
        house = fixture.h
        house.event("owner-migrate", fixture.migration())
        # The live house already enrolled staffing during its helper migration.
        old = maintenance.protected_manifest(house.state)
        house.event("owner-migrate", fixture.migration() | {
            "scope": maintenance.HELPER_SCOPE,
            "approval_sha256": maintenance.SOURCES[maintenance.HELPER_SCOPE],
            "protected_files": old | {"house/staffing.py": "d" * 64},
        })
        old = maintenance.protected_manifest(house.state)
        scope = maintenance.COORDINATOR_REPAIRS_SCOPE
        approval = Path(__file__).parents[1] / "evidence/coordinator-repairs/owner-scope.md"
        self.assertEqual(hashlib.sha256(approval.read_bytes()).hexdigest(), maintenance.SOURCES[scope])
        data = fixture.migration() | {
            "scope": scope, "approval_sha256": maintenance.SOURCES[scope],
            "protected_files": old | {name: "f" * 64 for name in maintenance.ALLOWED_CHANGES[scope]},
        }
        for name in ("house/council.py", "house/providers.py", "house/wake_policy.py",
                     "house/owner_upgrade.py", "house/windows.py", "house/life.py", "house/shelf.py"):
            bad = copy.deepcopy(data)
            bad["protected_files"][name] = "e" * 64
            house.reject("owner-migrate", bad, "outside.*scope|invalid replacement manifest")
        before = copy.deepcopy(house.state)
        house.event("owner-migrate", data)
        for key in ("rules", "rule_revision", "wake_policy", "council", "life"):
            self.assertEqual(house.state[key], before[key])
        house.reject("owner-migrate", data, "already used")
