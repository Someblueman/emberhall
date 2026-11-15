"""Project handoff activation leaves law and native sandbox authority intact."""
import copy
import hashlib
from pathlib import Path
import unittest
from house import maintenance as owner
from tests import test_owner_maintenance


class ProjectContinuationMaintenanceTests(unittest.TestCase):
    def test_narrow_one_use_activation(self):
        fixture = test_owner_maintenance.OwnerMaintenanceTests(); fixture.setUp()
        h = fixture.h
        h.event("owner-migrate", fixture.migration())
        old = owner.protected_manifest(h.state)
        scope = owner.PROJECT_CONTINUATION_SCOPE
        allowed = owner.OWNER_MODULES | {"house/home.py", "house/project_delivery.py"}
        self.assertEqual(owner.ALLOWED_CHANGES[scope], allowed)
        data = fixture.migration() | {"scope": scope, "approval_sha256": owner.SOURCES[scope],
            "protected_files": old | {p: "f" * 64 for p in allowed}}
        path = Path(__file__).parents[1] / "evidence/project-continuation/owner-scope.md"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), data["approval_sha256"])
        missing = copy.deepcopy(data); missing["protected_files"].pop("house/project_delivery.py")
        h.reject("owner-migrate", missing, "manifest")
        for name in ("house/providers.py", "house/council.py", "house/wake_policy.py",
                     "house/windows.py", "house/life.py", "house/mailbox_jobs.py", "house/test_sandbox.py"):
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
