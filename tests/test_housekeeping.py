"""Finished rooms and integration checkouts are removed only when nothing still needs them."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from house import housekeeping

NOW = 1_000_000.0


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=T", "-c", "user.email=t@local",
                           "-c", "commit.gpgsign=false", *args], capture_output=True, check=True,
                          text=True).stdout.strip()


class HousekeepingTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="housekeeping-"))
        self.addCleanup(lambda: self.base.exists() and housekeeping._remove(self.base))
        self.root = self.base / "house"
        self.root.mkdir()
        git(self.root, "init", "-q", "-b", "main")
        (self.root / "a.txt").write_text("a\n")
        git(self.root, "add", "-A"); git(self.root, "commit", "-qm", "base")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.private = self.root / ".git/house-home"
        (self.private / "jobs").mkdir(parents=True)
        self.runs = {}
        test = self

        class FakeRecord:
            root = test.root
            common = test.root / ".git"

            def read(self):
                return {"life": {"runs": test.runs}}, [], "h"
        self.record = FakeRecord()
        patcher = patch.object(housekeeping, "workspace_path",
                               side_effect=lambda record, run, state: self.root / ".house-residents" / run)
        patcher.start(); self.addCleanup(patcher.stop)

    def room(self, run, *, ended=NOW - 7200, preserved=True, contribution=None, receipt=None, commit=False):
        path = self.root / ".house-residents" / run
        subprocess.run(["git", "clone", "-q", "--no-local", str(self.root), str(path)], check=True)
        if commit:
            (path / "b.txt").write_text("resident work\n")
            git(path, "add", "-A"); git(path, "commit", "-qm", "work")
        os.chmod(path / ".git/objects", 0o500)  # Git leaves read-only pieces behind.
        folder = self.private / run
        folder.mkdir()
        if preserved:
            (folder / "preservation.json").write_text("{}")
        if contribution:
            (folder / "contribution.json").write_text(json.dumps(contribution))
        if receipt:
            (folder / "integration.json").write_text(json.dumps(receipt))
        self.runs[run] = {"status": "completed", "ended_at": ended, "source_head": self.head}
        return path

    def sweep(self, **kwargs):
        return housekeeping.sweep(self.record, self.private, now=NOW, **kwargs)

    def test_only_rooms_nothing_needs_are_removed(self):
        done = self.room("done")
        recent = self.room("recent", ended=NOW - 60)
        unsaved = self.room("unsaved", preserved=False)
        waiting = self.room("waiting", contribution={"status": "pending-review", "commit": "c1"})
        reviewed = self.room("reviewed", contribution={"status": "pending-review", "commit": "c2"},
                             receipt={"contribution": "c2", "status": "rejected"})
        busy = self.room("busy")
        (self.private / "jobs/j1").mkdir()
        (self.private / "jobs/j1/job.json").write_text(json.dumps({"run": "busy", "status": "running"}))
        self.runs["active"] = {"status": "active", "ended_at": NOW}
        dry = self.sweep()
        self.assertEqual({"done", "reviewed"}, {item["run"] for item in dry["rooms"]})
        self.assertTrue(done.exists())  # A report removes nothing.
        report = self.sweep(apply=True)
        self.assertEqual({"done", "reviewed"}, {item["run"] for item in report["rooms"]})
        self.assertFalse(done.exists() or reviewed.exists())
        for kept in (recent, unsaved, waiting, busy):
            self.assertTrue(kept.exists(), kept.name)
        self.assertGreater(report["bytes"], 0)

    def test_unmerged_commits_are_bundled_before_removal(self):
        room = self.room("work", commit=True)
        work = git(room, "rev-parse", "HEAD")
        self.sweep(apply=True)
        self.assertFalse(room.exists())
        bundle = self.private / "work/room-commits.bundle"
        git(self.root, "bundle", "verify", "-q", str(bundle))
        git(self.root, "fetch", "-q", str(bundle), "HEAD")
        self.assertEqual(work, git(self.root, "rev-parse", "FETCH_HEAD"))

    def test_integration_checkouts_follow_their_receipts(self):
        for name, status in (("a" * 32, "integrated"), ("b" * 32, "prepared"), ("c" * 32, None), ("d" * 32, None)):
            (self.private / ("integration-" + name)).mkdir()
            if status:
                run = self.private / ("run-" + name)
                run.mkdir()
                (run / "integration.json").write_text(json.dumps({"candidate": "integration-" + name, "status": status}))
        os.utime(self.private / ("integration-" + "d" * 32), (NOW - 7200, NOW - 7200))
        os.utime(self.private / ("integration-" + "c" * 32), (NOW, NOW))
        report = self.sweep(apply=True)
        self.assertEqual({"integration-" + "a" * 32, "integration-" + "d" * 32},
                         {item["name"] for item in report["checkouts"]})
        self.assertTrue((self.private / ("integration-" + "b" * 32)).exists())
        self.assertTrue((self.private / ("integration-" + "c" * 32)).exists())

    def test_never_runs_during_an_integration(self):
        room = self.room("done")
        with (self.private / "integration.lock").open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            report = self.sweep(apply=True)
        self.assertIn("skipped", report)
        self.assertTrue(room.exists())
