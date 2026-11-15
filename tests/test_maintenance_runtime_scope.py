"""Combined maintenance registration preserves the owner's fixed boundaries."""
import copy
import hashlib
from pathlib import Path
import unittest

from house import maintenance as owner
from tests import test_owner_maintenance


class MaintenanceRuntimeScopeTests(unittest.TestCase):
    def test_combined_scope_is_exact_authenticated_and_one_use(self):
        fixture = test_owner_maintenance.OwnerMaintenanceTests()
        fixture.setUp()
        h = fixture.h
        h.event("owner-migrate", fixture.migration())
        old = owner.protected_manifest(h.state)
        scope = owner.MAINTENANCE_RUNTIME_SCOPE
        allowed = {"house/integrate.py", "house/wake_policy.py", "house/maintenance.py"}
        self.assertEqual(owner.ALLOWED_CHANGES[scope], allowed)
        data = fixture.migration() | {"scope": scope, "approval_sha256": owner.SOURCES[scope],
            "protected_files": old | {p: "f" * 64 for p in allowed}}
        instruction = Path(__file__).parents[1] / "evidence/maintenance-runtime/owner-scope.md"
        self.assertEqual(hashlib.sha256(instruction.read_bytes()).hexdigest(), data["approval_sha256"])
        for name in ("house/providers.py", "house/council.py", "house/windows.py",
                     "house/home.py", "house/mailbox_jobs.py", "house/test_sandbox.py"):
            bad = copy.deepcopy(data)
            bad["protected_files"][name] = "0" * 64
            h.reject("owner-migrate", bad, "outside.*scope|invalid replacement manifest")
        missing = copy.deepcopy(data)
        missing["protected_files"].pop("house/wake_policy.py")
        h.reject("owner-migrate", missing, "manifest")
        h.reject("owner-migrate", data | {"approval_sha256": "0" * 64}, "approval")
        h.reject("owner-migrate", data | {"test_count": 0}, "passing tests")
        h.reject("owner-migrate", data, "owner", "bob")
        before = copy.deepcopy(h.state)
        h.event("owner-migrate", data)
        for key in ("rules", "rule_revision", "wake_policy", "council", "proposals", "life", "tasks", "shelf"):
            self.assertEqual(before.get(key), h.state.get(key))
        h.reject("owner-migrate", data, "already used")
