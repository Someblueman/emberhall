"""Independent review and conflicting real source contributions preserve work."""
import json
import os
import unittest
from house.home_work import contribution, git, room
from house.integrate import integrate
from house.home import pending_contributions
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

    def test_accepted_retry_keeps_receipt_history_and_does_no_new_work(self):
        self.candidate("one", "first\n")
        accepted = integrate(self.record, "one", "alice", publish=True)
        path = self.private / "one/integration.json"
        original = path.read_bytes()
        head = git(self.repo, "rev-parse", "HEAD")
        journal = self.record.read()[2]
        candidates = sorted(self.private.glob("integration-*"))
        for publish in (False, True):
            self.assertEqual(integrate(self.record, "one", "bob", publish=publish), accepted)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)
            self.assertEqual(self.record.read()[2], journal)
            self.assertEqual(sorted(self.private.glob("integration-*")), candidates)
            self.assertEqual(pending_contributions(self.private), [])
        # A read-only receipt replay must not touch someone else's dirty work.
        (self.repo / "document.txt").write_text("uncommitted next task\n")
        self.assertEqual(integrate(self.record, "one", "bob"), accepted)
        self.assertEqual((self.repo / "document.txt").read_text(), "uncommitted next task\n")

    def test_operator_acceptance_survives_later_commits_without_self_review(self):
        workspace = self.candidate("one", "first\n")
        (self.repo / "document.txt").write_text("first\n")
        git(self.repo, "add", "document.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Curated acceptance")
        accepted = {"run": "one", "actor": "alice", "status": "integrated",
                    "contribution": git(workspace, "rev-parse", "HEAD"),
                    "canonical_commit": git(self.repo, "rev-parse", "HEAD")}
        path = self.private / "one/integration.json"
        # Existing operator-curated receipts bind canonical_commit, not candidate_head.
        path.write_text(json.dumps(accepted))
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "--allow-empty", "-m", "Later work")
        self.assertEqual(integrate(self.record, "one", "bob"), accepted)
        self.record.append("wake", "author-one", {})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, "one", "author-one")
        self.record.append("sleep", "bob", {"through": 0, "note": "Rest"})
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, "one", "bob")

    def test_inconsistent_acceptance_and_changed_contribution_fail_closed(self):
        workspace = self.candidate("one", "first\n")
        accepted = integrate(self.record, "one", "alice", publish=True)
        path = self.private / "one/integration.json"
        for field, value in (("run", "other"), ("contribution", "0" * 40),
                             ("candidate_head", "0" * 40), ("candidate_head", "--all"),
                             ("canonical_commit", 7), ("canonical_commit", self.base),
                             ("candidate_head", self.base)):
            with self.subTest(field=field, value=value):
                broken = dict(accepted, **{field: value})
                path.write_text(json.dumps(broken))
                before = path.read_bytes()
                with self.assertRaisesRegex(ValueError, "accepted contribution"):
                    integrate(self.record, "one", "bob")
                self.assertEqual(path.read_bytes(), before)
        other = self.candidate("other", "second\n")
        other_head = git(other, "rev-parse", "HEAD")
        git(self.repo, "fetch", str(other), other_head)
        path.write_text(json.dumps(dict(accepted, candidate_head=other_head)))
        with self.assertRaisesRegex(ValueError, "outside current source history"):
            integrate(self.record, "one", "bob")
        path.write_text(json.dumps(accepted))
        git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "--allow-empty", "-m", "Changed candidate")
        with self.assertRaisesRegex(ValueError, "identity changed"):
            integrate(self.record, "one", "bob")
        self.assertEqual(json.loads(path.read_text()), accepted)

    def test_concurrent_replays_preserve_accepted_receipt(self):
        self.candidate("one", "first\n")
        accepted = integrate(self.record, "one", "alice", publish=True)
        path = self.private / "one/integration.json"
        original, journal = path.read_bytes(), self.record.read()[2]
        script = """
import json,sys
from house.record import Record
from house.integrate import integrate
try:
 print(json.dumps(integrate(Record(sys.argv[1]), 'one', 'bob', publish=True)))
except BlockingIOError:
 sys.exit(2)
"""
        processes = [self.script(script), self.script(script)]
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertIn(process.returncode, (0, 2), err)
            if process.returncode == 0:
                self.assertEqual(json.loads(out), accepted)
        self.assertTrue(any(p.returncode == 0 for p in processes))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(self.record.read()[2], journal)
