"""Real integrator receipts and command boundaries for receipt-backed review closure."""
import base64
import json
import os
import unittest

from house import __main__ as cli
from house import integrate, mailbox, resident_actions, review_completion
from house.home_work import git
from tests import test_review_completion as fixtures


class ReviewCompletionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewCompletionTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.record = self.f.record
        self.commit = self.f._setup_contribution()
        self.reviewer = "boundary-reviewer"

    def task(self):
        return self.f._setup_task(reviewer=self.reviewer)

    def commit_file(self, repo, path, content):
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        git(repo, "add", path)
        git(repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "boundary fixture")
        return git(repo, "rev-parse", "HEAD")

    def contribution(self, path, content):
        workspace = self.f.private / "residents/source-run"
        git(workspace, "rm", "contribution.txt")
        self.commit = self.commit_file(workspace, path, content)
        (self.f.private / "source-run/contribution.json").write_text(
            json.dumps({"base": self.f.base, "commit": self.commit}))

    def projection(self):
        task = self.record.read()[0]["tasks"]["review-task"]
        self.assertEqual(task["status"], "done")
        self.assertEqual(len(task["artifacts"]), 1)
        return json.loads(base64.b64decode(next(iter(task["artifacts"].values()))["base64"]))

    def test_real_advanced_rejection_and_cli_replay(self):
        token = self.task()
        advanced = self.commit_file(self.f.repo, "advanced.txt", "later source\n")
        receipt = integrate.integrate(self.record, "source-run", self.reviewer, reject="Found defect")
        self.assertEqual(receipt["base"], advanced)
        self.assertNotEqual(receipt["base"], self.f.base)
        # Exercise parser and dispatch together in the fixture's enabled-helper
        # process. Native worker use is a separate installation acceptance check.
        argv = ["--repo", str(self.f.repo), "review-complete", "review-task",
                "--as", self.reviewer, "--token", token, "--request", "boundary-close"]
        first = cli.run(cli.parser().parse_args(argv))
        seq = first["sequence"]
        self.assertEqual(self.projection()["status"], "rejected")
        (self.f.private / "source-run/integration.json").unlink()
        again = cli.run(cli.parser().parse_args(argv))
        self.assertEqual(again["sequence"], seq)
        changed = argv.copy(); changed[changed.index(token)] = "wrong-token"
        with self.assertRaisesRegex(ValueError, "token mismatch"):
            cli.run(cli.parser().parse_args(changed))

    def test_real_advanced_integration_through_fixed_action(self):
        self.contribution("research/explorations/receipt-probe.md", "A fixture note.\n")
        self.commit_file(self.f.repo, "advanced.txt", "later source\n")
        run = "boundary-review-run"
        workspace = self.f.private / "residents" / run
        workspace.mkdir()
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": run,
            "resident": self.reviewer, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": git(self.f.repo, "rev-parse", "HEAD"), "workspace": "residents/" + run,
            "policy_revision": "fixture", "mode": "review"})
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": run, "pgid": os.getpid()})
        token = self.task()
        receipt = integrate.integrate(self.record, "source-run", self.reviewer, publish=True)
        self.assertEqual(receipt["status"], "integrated")
        self.assertNotEqual(receipt["base"], self.f.base)
        argv = ["review-complete", "--as", self.reviewer, "--task", "review-task", "--token", token]
        parsed = mailbox.parse(argv, self.f.repo, workspace, self.reviewer)
        self.assertEqual(parsed.command, "review-complete")
        result = resident_actions.execute(self.record, workspace, self.reviewer, run, argv, "action-close")
        projection = self.projection()
        self.assertEqual(projection["status"], "integrated")
        self.assertEqual(projection["candidate_head"], receipt["candidate_head"])
        self.assertNotIn("candidate", projection)
        self.assertNotIn("diagnostics", projection)
        self.assertEqual(resident_actions.known_result(self.record, self.reviewer, run, argv,
                                                     "action-close")["sequence"], result["sequence"])
        with self.assertRaisesRegex(ValueError, "root"):
            mailbox.parse(argv + ["--repo", "/tmp/another-house"], self.f.repo, workspace, self.reviewer)

    def test_real_conflict_stays_a_conflict(self):
        token = self.task()
        self.commit_file(self.f.repo, "contribution.txt", "incompatible shared contribution\n")
        receipt = integrate.integrate(self.record, "source-run", self.reviewer, publish=True)
        self.assertEqual(receipt["status"], "conflict")
        review_completion.complete(self.record, "review-task", self.reviewer, token, "conflict-close")
        self.assertEqual(self.projection()["status"], "conflict")

    @unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "nested candidate supervisor needs macOS host process inspection")
    def test_real_test_failure_stays_failed(self):
        self.contribution("projects/probe/test_failure.py",
                          "import unittest\nclass Failure(unittest.TestCase):\n def test_failure(self): self.fail('intentional fixture')\n")
        token = self.task()
        receipt = integrate.integrate(self.record, "source-run", self.reviewer, publish=True)
        self.assertEqual(receipt["status"], "tests-failed")
        review_completion.complete(self.record, "review-task", self.reviewer, token, "failed-close")
        self.assertEqual(self.projection()["status"], "tests-failed")
        self.assertNotIn("diagnostics", self.projection())
