"""Exact synthetic history: launcher correction does not refund earlier credits."""
import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from house import life, maintenance as owner, owner_upgrade
from tests import test_owner_cli_repair as fixtures


class OwnerLauncherTests(unittest.TestCase):
    def setUp(self):
        self.repair = fixtures.OwnerCLIRepairTests(); self.repair.setUp()
        self.f, self.h = self.repair.f, self.repair.h
        self.h.event("owner-provider-release", self.repair.release())
        while self.h.state["sequence"] < 526:
            self.h.event("say", {"text": "Synthetic history"})
        self.h.event("life", self.f.start(owner.FAILED_BOOTSTRAP_RUN), "watch-keeper")
        self.h.event("life", {"kind": "run-launched", "run": owner.FAILED_BOOTSTRAP_RUN,
                              "pgid": 12346}, "watch-keeper")
        self.h.event("say", {"text": "Synthetic observed pre-model bootstrap failure"}, "watch-keeper")
        self.h.event("life", {"kind": "budget", "agent": "opencode", "until": self.h.now + 300,
                              "reason": "failed"}, "watch-keeper")
        self.h.event("life", {"kind": "run-finish", "run": owner.FAILED_BOOTSTRAP_RUN,
            "outcome": "failed", "exit_code": 2, "usage": {}, "elapsed_seconds": 13.5}, "watch-keeper")
        self.assertEqual(self.h.state["sequence"], 531)
        # The actual launcher migration follows room growth: its pins must survive.
        growth = self.f.migration() | {"scope": owner.GROWTH_SCOPE, "approval_sha256": owner.GROWTH_SHA256}
        growth["protected_files"]["house/building.py"] = "b" * 64
        self.h.event("owner-migrate", growth)
        self.before_migration = copy.deepcopy(self.h.state)
        self.migration = self.f.migration() | {"scope": owner.LAUNCHER_SCOPE,
                                               "approval_sha256": owner.GROWTH_SHA256}
        self.migration["protected_files"].update({name: "e" * 64 for name in owner.OWNER_MODULES})
        self.h.event("owner-migrate", self.migration)

    def release(self):
        return self.f.release() | {"scope": owner.LAUNCHER_SCOPE, "approval_sha256": owner.GROWTH_SHA256,
            "expected_observation": 530, "failed_run": owner.FAILED_BOOTSTRAP_RUN,
            "failed_output_sha256": owner.FAILED_BOOTSTRAP_SHA256}

    def test_one_new_admission_preserves_spent_credits_hold_and_failures(self):
        releases = copy.deepcopy(self.h.state["maintenance"]["releases"])
        budget = copy.deepcopy(self.h.state["life"]["budgets"]["opencode"])
        runs = copy.deepcopy(self.h.state["life"]["runs"])
        self.h.event("owner-provider-release", self.release())
        self.h.event("life", self.f.start("pinned-native-launch"), "watch-keeper")
        self.h.reject("life", self.f.start("second-launch"), "cooling down", "watch-keeper")
        self.h.reject("owner-provider-release", self.release(), "already used")
        for scope, value in releases.items():
            self.assertEqual(self.h.state["maintenance"]["releases"][scope], value)
        for run, value in runs.items():
            self.assertEqual(self.h.state["life"]["runs"][run], value)
        self.assertEqual(self.h.state["life"]["budgets"]["opencode"], budget)
        self.assertEqual(self.h.state["maintenance"]["releases"][owner.LAUNCHER_SCOPE]["consumed_run"],
                         "pinned-native-launch")

    def test_migration_retains_building_auth_and_all_existing_enforcement(self):
        old = owner.protected_manifest(self.before_migration)
        actual = owner.protected_manifest(self.h.state)
        self.assertEqual(set(old), set(actual))
        self.assertEqual({name for name in actual if old[name] != actual[name]}, owner.OWNER_MODULES)
        self.assertTrue(self.h.state["maintenance"]["room_growth"])
        self.h.state = copy.deepcopy(self.before_migration)
        for name in ("house/providers.py", "house/opencode_auth.py", "house/building.py", "house/council.py"):
            bad = copy.deepcopy(self.migration); bad["protected_files"][name] = "0" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        bad = copy.deepcopy(self.migration); del bad["protected_files"]["house/building.py"]
        self.h.reject("owner-migrate", bad, "replacement manifest")
        bad = copy.deepcopy(self.migration); bad["protected_files"]["house/new_auth.py"] = "0" * 64
        self.h.reject("owner-migrate", bad, "replacement manifest")

    def test_wrong_proof_scope_and_spent_predecessor_rejected(self):
        for change, error in (({"scope": owner.REPAIR_SCOPE}, "already used"),
                ({"scope": "opencode-unlimited"}, "approval"),
                ({"approval_sha256": owner.OPENCODE_SHA256}, "approval"),
                ({"failed_run": owner.FAILED_CLI_RUN}, "exact spent"),
                ({"failed_output_sha256": "0" * 64}, "exact spent"),
                ({"expected_observation": 530.0}, "exact spent")):
            self.h.reject("owner-provider-release", self.release() | change, error)
        self.h.state["maintenance"]["releases"][owner.REPAIR_SCOPE]["consumed_run"] = "different-run"
        self.h.reject("owner-provider-release", self.release(), "exact spent")

    def test_model_usage_status_sequence_and_late_arrival_reject(self):
        before = copy.deepcopy(self.h.state)
        for change in ({"usage": {"input_tokens": 1}}, {"exit_code": 1}, {"status": "active"},
                       {"outcome": "interrupted"}, {"started_sequence": 528}, {"ended_sequence": 532},
                       {"agent": "codex"}):
            self.h.state = copy.deepcopy(before)
            self.h.state["life"]["runs"][owner.FAILED_BOOTSTRAP_RUN].update(change)
            self.h.reject("owner-provider-release", self.release(), "uncertain failure")
        for granted in (False, True):
            self.h.state = copy.deepcopy(before)
            if granted: self.h.event("owner-provider-release", self.release())
            resident = self.h.state["life"]["runs"][owner.FAILED_BOOTSTRAP_RUN]["resident"]
            self.h.event("arrive", {"name": "Synthetic late arrival"}, resident)
            if not granted: self.h.reject("owner-provider-release", self.release(), "uncertain failure")
            self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))
            self.h.reject("life", self.f.start("late-arrival-launch"), "cooling down", "watch-keeper")

    def test_new_failure_invalidates_credit_before_and_after_release(self):
        before = copy.deepcopy(self.h.state)
        for granted in (False, True):
            self.h.state = copy.deepcopy(before)
            if granted: self.h.event("owner-provider-release", self.release())
            self.h.event("life", {"kind": "budget", "agent": "opencode", "until": self.h.now + 1,
                                  "reason": "new failure"}, "watch-keeper")
            if not granted: self.h.reject("owner-provider-release", self.release(), "hold changed")
            self.assertFalse(life.provider_available(self.h.state, "opencode", self.h.now))
            self.h.reject("life", self.f.start("after-new-failure"), "cooling down", "watch-keeper")

    def test_operator_requires_retained_empty_destination_and_regular_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            common = Path(tmp).resolve() / ".git"
            directory = common / "house-home" / owner.FAILED_BOOTSTRAP_RUN
            directory.mkdir(parents=True)
            error = directory / "stderr.log"; error.write_bytes(b"synthetic retained failure")
            output = directory / "stdout.jsonl"; output.touch()
            record = SimpleNamespace(common=common, read=lambda: (self.h.state, [], "head"), append=Mock())
            selected = {"runtime_sha256": self.migration["runtime_sha256"]}
            with patch.object(owner_upgrade, "authenticate_owner") as auth, \
                 patch.object(owner_upgrade.runtime, "selected", return_value=selected), \
                 patch.object(owner_upgrade, "sha", return_value=owner.FAILED_BOOTSTRAP_SHA256) as sha:
                owner_upgrade.release_opencode(record, "alice", owner.LAUNCHER_SCOPE)
                auth.assert_called_once(); sha.assert_called_once_with(b"synthetic retained failure")
                record.append.assert_called_once_with("owner-provider-release", "alice", self.release(),
                                                       "owner-release-" + owner.LAUNCHER_SCOPE)
                record.append.reset_mock()
                for suffix in ("", "-wal", "-shm", "-journal"):
                    path = directory / ("opencode.db" + suffix)
                    for link in (False, True):
                        path.symlink_to(directory / "missing") if link else path.touch()
                        with self.assertRaisesRegex(ValueError, "destination evidence"):
                            owner_upgrade.release_opencode(record, "alice", owner.LAUNCHER_SCOPE)
                        path.unlink()
                for name in ("stdout.jsonl", "stderr.log"):
                    path = directory / name; original = path.read_bytes(); path.unlink()
                    path.symlink_to(directory / "missing")
                    with self.assertRaises(ValueError):
                        owner_upgrade.release_opencode(record, "alice", owner.LAUNCHER_SCOPE)
                    path.unlink(); path.write_bytes(original)
                output.write_bytes(b"unexpected output")
                with self.assertRaisesRegex(ValueError, "stdout"):
                    owner_upgrade.release_opencode(record, "alice", owner.LAUNCHER_SCOPE)
                output.write_bytes(b"")
                sha.return_value = "0" * 64
                with self.assertRaisesRegex(ValueError, "evidence changed"):
                    owner_upgrade.release_opencode(record, "alice", owner.LAUNCHER_SCOPE)
                sha.return_value = owner.FAILED_BOOTSTRAP_SHA256
                moved = directory.with_name("retained-original"); directory.rename(moved); directory.symlink_to(moved)
                with self.assertRaisesRegex(ValueError, "evidence changed"):
                    owner_upgrade.release_opencode(record, "alice", owner.LAUNCHER_SCOPE)
                record.append.assert_not_called()
