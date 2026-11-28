"""Actual independent Git source copies and actor-fenced journal clients."""
import hashlib
import json
import os
import subprocess
import sys
import unittest.mock
import zipfile
import time

from house.home import Coordinator, pending_contributions
from house.life import CONTROLLER
from house.home_work import client, contribution, git, preserve, room
from house.mailbox import service
from tests.support import HouseCase, SOURCE


class PrivateWorkTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "source.txt").write_text("base\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Initial source")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"
        self.private.mkdir()
        self.runtime = self.private / "runtime.pyz"
        with zipfile.ZipFile(self.runtime, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                archive.write(file, "house/" + file.name)

    def test_same_path_edits_in_two_source_rooms_cannot_overwrite(self):
        first = room(self.record, self.private, "one", self.base)
        second = room(self.record, self.private, "two", self.base)
        (first / "source.txt").write_text("first\n")
        (second / "source.txt").write_text("second\n")
        preserved = preserve(self.private, "one", first)
        self.assertIsNotNone(preserved["rescue"])
        report = contribution(first, self.base, self.private / "candidate.json", journal_artifacts={})
        self.assertEqual(report["paths"], ["source.txt"])
        self.assertEqual((self.repo / "source.txt").read_text(), "base\n")
        self.assertEqual((second / "source.txt").read_text(), "second\n")
        self.assertEqual(git(self.repo, "worktree", "list", "--porcelain").count("worktree "), 1)

    def test_retained_source_depends_only_on_permanent_objects_and_is_idempotent(self):
        workspace = room(self.record, self.private, "one", self.base)
        (workspace / "source.txt").write_text("retained\n")
        destination = self.private / "one/contribution.json"
        report = contribution(workspace, self.base, destination, journal_artifacts={})
        archive = destination.parent / ("source-" + report['commit'] + ".git")
        self.assertEqual(report['retained_source'], 'git-objects-v1')
        self.assertEqual((archive / 'objects/info/alternates').read_text().splitlines(),
                         [str((self.record.common / 'objects').resolve())])
        self.assertNotIn(str(workspace), (archive / 'config').read_text())
        before = {str(p.relative_to(archive)): p.read_bytes() for p in archive.rglob('*') if p.is_file()}
        self.assertEqual(contribution(workspace, self.base, destination, journal_artifacts={}), report)
        self.assertEqual(before, {str(p.relative_to(archive)): p.read_bytes()
                                  for p in archive.rglob('*') if p.is_file()})

    def test_retention_failure_keeps_live_room_contribution_without_false_marker(self):
        workspace = room(self.record, self.private, "one", self.base)
        (workspace / "source.txt").write_text("keep this\n")
        destination = self.private / "one/contribution.json"
        with unittest.mock.patch('house.home_work.retain_source', side_effect=OSError('full')):
            report = contribution(workspace, self.base, destination, journal_artifacts={})
        self.assertEqual(report['status'], 'pending-review')
        self.assertNotIn('retained_source', report)
        self.assertEqual(report['retained_source_error'], 'OSError')
        self.assertEqual(json.loads(destination.read_text()), report)
        self.assertEqual(git(workspace, 'show', report['commit'] + ':source.txt'), 'keep this')

    def test_fixed_client_rejects_other_actor_and_global_repo_override(self):
        workspace = room(self.record, self.private, "one", self.base)
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": "one",
            "resident": "client-worker", "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/one", "policy_revision": "fixture", "mode": "work"})
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": "one", "pgid": 12345})
        self.record.append("arrive", "client-worker", {"name": "Worker"})
        (self.private / "one").mkdir()
        command = client(self.record, workspace, "client-worker", self.runtime)
        def execute(args):
            process = subprocess.Popen([str(command), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            deadline = time.monotonic() + 10
            while process.poll() is None and time.monotonic() < deadline:
                service(self.record, self.private, "one")
                time.sleep(.02)
            if process.poll() is None:
                process.kill()
            out, err = process.communicate(timeout=2)
            return subprocess.CompletedProcess(args, process.returncode, out, err)
        good = execute(["say", "--as", "client-worker", "Hello"])
        self.assertEqual(good.returncode, 0, good.stderr)
        for args in (["say", "--as", "bob", "Impersonation"], ["--repo", str(workspace), "status"],
                     ["found", "--name", "Replacement"], ["life", "--as", "client-worker", "--data", '{"kind":"run-start"}']):
            rejected = execute(args)
            self.assertEqual(rejected.returncode, 2)
        self.assertEqual(self.record.read()[1][-1]["data"]["text"], "Hello")
        self.assertEqual(git(workspace, "status", "--porcelain"), "")


class RoomContributionDeliveryTests(HouseCase):
    """Safe finished artifacts queue despite unsafe/locked worktree state.

    Pre-fix source called watch_recovery.capture (strict whole-worktree
    abort) and `git add --all` in the room index, so the stranded cases below
    raised ValueError / left no contribution.json. They demonstrably fail
    against the pre-fix home_work (capture raises on any unsafe path and
    room-index git add fails on a stale lock).
    """

    def setUp(self):
        super().setUp()
        (self.repo / "source.txt").write_text("base\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Initial source")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"
        self.private.mkdir()

    def _report(self, run, workspace, artifacts=None):
        dest = self.private / run / "contribution.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        return contribution(workspace, self.base, dest,
                            journal_artifacts=artifacts or {}), dest

    def _show(self, workspace, commit, name):
        return subprocess.run(["git", "-C", str(workspace), "show", f"{commit}:{name}"],
                              check=True, capture_output=True).stdout

    def test_safe_finished_file_queued_beside_oversized_file(self):
        workspace = room(self.record, self.private, "big", self.base)
        safe = workspace / "safe.txt"
        safe.write_text("safe bytes\n")
        digest = hashlib.sha256(b"safe bytes\n").hexdigest()
        big = workspace / "big.bin"
        big.write_bytes(b"\x00" * (9 * 1024 * 1024))
        report, dest = self._report("big", workspace,
                                    {"safe.txt": {"task": "t", "sequence": 1, "sha256": digest}})
        self.assertEqual(report["status"], "pending-review")
        self.assertEqual(report["paths"], ["safe.txt"])
        self.assertEqual([e["path"] for e in report["excluded"]], ["big.bin"])
        self.assertEqual(report["excluded"][0]["reason"], "exceeds file limit")
        self.assertEqual(self._show(workspace, report["commit"], "safe.txt"), b"safe bytes\n")
        tree = subprocess.run(["git", "-C", str(workspace), "ls-tree", "-r",
                               "--name-only", report["commit"]],
                              check=True, capture_output=True, text=True).stdout
        self.assertNotIn("big.bin", tree)
        journal_blob = dest.read_bytes()
        self.assertLess(len(journal_blob), 64 * 1024)
        self.assertNotIn(b"\x00" * 32, journal_blob)
        # pending-review queues; source checkout untouched.
        self.assertEqual(self._pending(), [{"run": "big", "commit": report["commit"], "paths": ["safe.txt"]}])
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.base)
        self.assertFalse((self.repo / "safe.txt").exists())

    def test_safe_finished_file_with_stale_index_lock(self):
        workspace = room(self.record, self.private, "locked", self.base)
        (workspace / "safe.txt").write_text("locked safe\n")
        index_before = (workspace / ".git" / "index").read_bytes()
        lock = workspace / ".git" / "index.lock"
        lock.write_bytes(b"")
        report, _ = self._report("locked", workspace)
        self.assertEqual(report["status"], "pending-review")
        self.assertEqual(report["paths"], ["safe.txt"])
        self.assertEqual(self._show(workspace, report["commit"], "safe.txt"), b"locked safe\n")
        self.assertEqual((workspace / ".git" / "index").read_bytes(), index_before)
        self.assertEqual(lock.read_bytes(), b"")
        self.assertEqual(self._pending(), [{"run": "locked", "commit": report["commit"], "paths": ["safe.txt"]}])

    def test_literal_finished_paths_do_not_stage_excluded_files(self):
        for safe_name, unsafe_name in (("*.txt", "secret.txt"),
                                       ("file[1].txt", "file1.txt"),
                                       (":(glob)*.txt", "secret.txt")):
            for unsafe_kind in ("symlink", "oversized"):
                with self.subTest(path=safe_name, excluded=unsafe_kind):
                    run = f"literal-{len(list(self.private.glob('literal-*')))}"
                    workspace = room(self.record, self.private, run, self.base)
                    body = b"safe finished bytes\n"
                    (workspace / safe_name).write_bytes(body)
                    unsafe = workspace / unsafe_name
                    if unsafe_kind == "symlink":
                        unsafe.symlink_to("source.txt")
                        reason = "symlink"
                    else:
                        unsafe.write_bytes(b"x" * (9 * 1024 * 1024))
                        reason = "exceeds file limit"
                    report, _ = self._report(run, workspace, {safe_name: {
                        "task": "t", "sequence": 1,
                        "sha256": hashlib.sha256(body).hexdigest()}})
                    self.assertEqual(report["status"], "pending-review")
                    self.assertEqual(report["paths"], [safe_name])
                    self.assertEqual(report["excluded"], [{"path": unsafe_name, "reason": reason}])
                    self.assertEqual(self._show(workspace, report["commit"], safe_name), body)
                    tree = subprocess.run(["git", "-C", str(workspace), "ls-tree", "-rz",
                                           "--name-only", report["commit"]],
                                          check=True, capture_output=True).stdout.split(b"\0")
                    self.assertNotIn(unsafe_name.encode(), tree)

    def test_unsafe_only_room_produces_blocked_receipt(self):
        workspace = room(self.record, self.private, "blocked", self.base)
        (workspace / "evil").symlink_to("source.txt")
        report, dest = self._report("blocked", workspace)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["paths"], [])
        self.assertEqual(report["commit"], self.base)
        self.assertEqual([e["path"] for e in report["excluded"]], ["evil"])
        self.assertEqual(git(workspace, "rev-parse", "HEAD"), self.base)
        self.assertTrue(dest.is_file())
        self.assertEqual(self._pending(), [])
        # Unsafe bytes never entered any commit.
        tree = subprocess.run(["git", "-C", str(workspace), "ls-tree", "-r",
                               "--name-only", report["commit"]],
                              check=True, capture_output=True, text=True).stdout
        self.assertNotIn("evil", tree)

    def test_finish_queues_safe_bytes_after_strict_rescue_refuses_symlink(self):
        self.record.append("arrive", CONTROLLER, {"name": "Clock"})
        run = "finished"
        (self.private / run).mkdir()
        workspace = room(self.record, self.private, run, self.base)
        self.record.append("life", CONTROLLER, {"kind": "run-start", "run": run,
            "resident": "resident-finished", "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + run,
            "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "resident-finished", {"name": "Finch"})
        body = b"finished safe bytes\n"
        (workspace / "*.txt").write_bytes(body)
        (workspace / "secret.txt").symlink_to("source.txt")
        self.record.append("task", "resident-finished", {"task": "safe", "title": "Safe",
                                             "description": "Fixture artifact"})
        self.record.append("claim", "resident-finished", {"task": "safe", "expect": 0,
            "token": "safe", "seconds": 60})
        from house.files import artifact
        self.record.append("finish", "resident-finished", {"task": "safe", "token": "safe",
            "result": "Built", "artifacts": {"*.txt": artifact(workspace, "*.txt")}})
        with self.assertRaisesRegex(ValueError, "bounded regular files"):
            preserve(self.private, run, workspace)
        runtime = self.root / "inert-runtime.pyz"
        runtime.touch()  # finish never executes this fixture runtime or a model.
        coordinator = Coordinator(self.record, runtime)
        coordinator.finish(run, {"outcome": "success", "exit_code": 0,
            "usage": {}, "elapsed_seconds": 1})
        saved = self.private / run
        error = json.loads((saved / "preservation-error.json").read_text())
        self.assertEqual(error, {"error": "ValueError", "workspace_retained": True})
        report = json.loads((saved / "contribution.json").read_text())
        self.assertEqual(report["status"], "pending-review")
        self.assertEqual(report["paths"], ["*.txt"])
        self.assertEqual(report["excluded"], [{"path": "secret.txt", "reason": "symlink"}])
        self.assertEqual(self._show(workspace, report["commit"], "*.txt"), body)
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["outcome"], "success")

    def test_no_changes_and_journal_recorded_unchanged(self):
        workspace = room(self.record, self.private, "clean", self.base)
        report, _ = self._report("clean", workspace)
        self.assertEqual(report["status"], "no-changes")
        self.assertEqual(report["paths"], [])
        self.assertEqual(report["commit"], self.base)

        workspace2 = room(self.record, self.private, "rec", self.base)
        name = "evidence/native-residents/report.md"
        body = b"A claim still needs independent evidence.\n"
        path = workspace2 / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        artifacts = {name: {"task": "t", "sequence": 7,
                            "sha256": hashlib.sha256(body).hexdigest()}}
        report2, _ = self._report("rec", workspace2, artifacts)
        self.assertEqual(report2["status"], "journal-recorded")
        self.assertEqual(self._show(workspace2, report2["commit"], name), body)
        self.assertEqual(self._pending(), [])

    def test_failed_working_scan_reports_blocked_error_instead_of_no_changes(self):
        clean_ws = room(self.record, self.private, "true-clean", self.base)
        clean_report, _ = self._report("true-clean", clean_ws)
        self.assertEqual(clean_report["status"], "no-changes")
        self.assertNotIn("error", clean_report)

        broken_ws = room(self.record, self.private, "scan-fail", self.base)
        note = broken_ws / "uncommitted.txt"
        note.write_bytes(b"keep me\n")
        with unittest.mock.patch(
            "house.home_work._working_changed",
            side_effect=subprocess.CalledProcessError(128, ["git", "diff"], stderr=b"corrupt"),
        ):
            report, _ = self._report("scan-fail", broken_ws)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["paths"], [])
        self.assertEqual(report["commit"], self.base)
        self.assertIn("working-tree-scan-failed:", report["error"])
        self.assertEqual(note.read_bytes(), b"keep me\n")
        self.assertEqual(self._pending(), [])

    def _pending(self):
        return pending_contributions(self.private)
