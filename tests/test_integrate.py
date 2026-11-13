"""Independent review and conflicting real source contributions preserve work."""
import os
import unittest
from house.home_work import contribution, git, room
from house.integrate import integrate
from tests.support import HouseCase


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host-only sandbox boundary fixture cannot nest macOS sandboxes")
class IntegrationTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        (self.repo / "tests").mkdir()
        (self.repo / "tests/test_document.py").write_text(
            "import pathlib,unittest\nclass Document(unittest.TestCase):\n"
            " def test_document(self): self.assertIn(pathlib.Path('document.txt').read_text(), ['base\\n','first\\n','second\\n'])\n")
        (self.repo / "document.txt").write_text("base\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Base source")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"
        self.private.mkdir()

    def candidate(self, run, text):
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": run,
            "resident": "author-" + run, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "author-" + run, {"name": "Author"})
        workspace = room(self.record, self.private, run, self.base)
        (workspace / "document.txt").write_text(text)
        (self.private / run).mkdir()
        contribution(workspace, self.base, self.private / run / "contribution.json")
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": run,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        return workspace

    def test_wren_self_review_rejected_and_two_conflicting_contributions_retained(self):
        first = self.candidate("one", "first\n")
        second = self.candidate("two", "second\n")
        self.record.append("wake", "author-one", {})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, "one", "author-one", publish=True)
        result = integrate(self.record, "one", "alice", publish=True)
        self.assertEqual(result["status"], "integrated")
        self.assertEqual((self.repo / "document.txt").read_text(), "first\n")
        result = integrate(self.record, "two", "bob", publish=True)
        self.assertEqual(result["status"], "conflict")
        self.assertEqual((self.repo / "document.txt").read_text(), "first\n")
        self.assertEqual((second / "document.txt").read_text(), "second\n")
        self.assertEqual((first / "document.txt").read_text(), "first\n")
