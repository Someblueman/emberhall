"""Delivery and contention repairs cannot alter unrelated protected boundaries."""
import copy
import hashlib
from pathlib import Path
import unittest
from house import maintenance
from tests import test_owner_maintenance


class ChronicleRuntimeMaintenanceTests(unittest.TestCase):
    def test_exact_scope_preserves_house_authority(self):
        for scope, folder in ((maintenance.CHRONICLE_SCOPE, "evidence/chronicle-runtime"),
                              (maintenance.CONTENTION_SCOPE, "evidence/integration-contention")):
            with self.subTest(scope=scope):
                self.check_scope(scope, folder)

    def check_scope(self, scope, folder):
        fixture = test_owner_maintenance.OwnerMaintenanceTests()
        fixture.setUp()
        house = fixture.h
        house.event("owner-migrate", fixture.migration())
        # The installed runtime already contains the source-delivery module.
        # Establish that historical migration before testing this narrow repair.
        old = maintenance.protected_manifest(house.state)
        house.event("owner-migrate", fixture.migration() | {
            "scope": maintenance.DELIVERY_SCOPE,
            "approval_sha256": maintenance.SOURCES[maintenance.DELIVERY_SCOPE],
            "protected_files": old | {
                name: "e" * 64 for name in maintenance.ALLOWED_CHANGES[maintenance.DELIVERY_SCOPE]
            },
        })
        old = maintenance.protected_manifest(house.state)
        approval = Path(__file__).parents[1] / folder / "owner-scope.md"
        self.assertEqual(hashlib.sha256(approval.read_bytes()).hexdigest(), maintenance.SOURCES[scope])
        data = fixture.migration() | {
            "scope": scope, "approval_sha256": maintenance.SOURCES[scope],
            "protected_files": old | {name: "f" * 64 for name in maintenance.ALLOWED_CHANGES[scope]},
        }
        for name in ("house/council.py", "house/home_work.py", "house/providers.py", "house/wake_policy.py",
                     "house/owner_upgrade.py", "house/windows.py", "house/life.py", "house/shelf.py"):
            bad = copy.deepcopy(data)
            bad["protected_files"][name] = "0" * 64
            house.reject("owner-migrate", bad, "outside.*scope|invalid replacement manifest")
        before = copy.deepcopy(house.state)
        house.event("owner-migrate", data)
        for key in ("rules", "rule_revision", "wake_policy", "council", "life"):
            self.assertEqual(house.state[key], before[key])
        house.reject("owner-migrate", data, "already used")
