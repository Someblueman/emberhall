"""Actual independent Git source copies and actor-fenced journal clients."""
import subprocess
import sys
import zipfile
import time

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
