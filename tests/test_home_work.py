"""Actual independent Git source copies and actor-fenced journal clients."""
import subprocess
import sys
import zipfile

from house.home_work import client, contribution, git, preserve, room
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
        report = contribution(first, self.base, self.private / "candidate.json")
        self.assertEqual(report["paths"], ["source.txt"])
        self.assertEqual((self.repo / "source.txt").read_text(), "base\n")
        self.assertEqual((second / "source.txt").read_text(), "second\n")
        self.assertEqual(git(self.repo, "worktree", "list", "--porcelain").count("worktree "), 1)

    def test_fixed_client_rejects_other_actor_and_global_repo_override(self):
        workspace = room(self.record, self.private, "one", self.base)
        command = client(self.record, workspace, "alice", self.runtime)
        good = subprocess.run([str(command), "say", "--as", "alice", "Hello"], capture_output=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        for args in (["say", "--as", "bob", "Impersonation"], ["--repo", str(workspace), "status"],
                     ["found", "--name", "Replacement"], ["life", "--as", "alice", "--data", '{"kind":"run-start"}']):
            rejected = subprocess.run([str(command), *args], capture_output=True)
            self.assertEqual(rejected.returncode, 2)
        self.assertEqual(self.record.read()[1][-1]["data"]["text"], "Hello")
        self.assertEqual(git(workspace, "status", "--porcelain"), "")
