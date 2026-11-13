"""Keep exact finished testimony in Git without creating an endless review queue."""
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch
import unittest
import zipfile

from house.files import artifact
from house.home import Coordinator, pending_contributions
from house.home_work import contribution, finished_reports, git, room
from house.integrate import integrate
from tests.support import HouseCase


class ReportRetentionTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        (self.repo / "source.txt").write_text("base\n")
        prior = self.repo / "evidence/native-residents/prior.md"
        prior.parent.mkdir(parents=True); prior.write_text("published history\n")
        tests = self.repo / "tests"; tests.mkdir()
        (tests / "test_source.py").write_text(
            "import pathlib,unittest\nclass Source(unittest.TestCase):\n"
            " def test_unchanged(self): self.assertEqual(pathlib.Path('source.txt').read_text(),'base\\n')\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Source and prior report")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"; self.private.mkdir()
        self.counter = 0

    def new_run(self):
        self.counter += 1
        run = f"run-{self.counter}"
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": run,
            "resident": run, "agent": "codex", "model": "gpt-6.1-sol", "source_head": self.base,
            "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "review"})
        self.record.append("arrive", run, {"name": run})
        workspace = room(self.record, self.private, run, self.base)
        (self.private / run).mkdir()
        return run, workspace

    def launch(self, run):
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": run, "pgid": 12345})

    def end(self, run):
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": run,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})

    def finish(self, workspace, name, actor):
        task = "task-" + str(self.record.read()[0]["sequence"])
        self.record.append("task", actor, {"task": task, "title": "Report", "description": "Owned fixture"})
        self.record.append("claim", actor, {"task": task, "expect": 0, "token": task, "seconds": 300})
        return self.record.append("finish", actor, {"task": task, "token": task, "result": "Unreviewed testimony",
            "artifacts": {name: artifact(workspace, name)}})

    def capture(self, run, workspace):
        state, events, _ = self.record.read()
        return contribution(workspace, self.base, self.private / run / "contribution.json",
                            journal_artifacts=finished_reports(events, state["life"]["runs"][run]))

    def test_exact_finished_report_is_retained_but_not_accepted_or_queued(self):
        run, workspace = self.new_run(); self.launch(run)
        name = "evidence/native-residents/report.md"
        (workspace / name).write_bytes(b"A claim still needs independent evidence.\n")
        finish = self.finish(workspace, name, run)
        before = self.record.read()
        report = self.capture(run, workspace)
        self.assertEqual(report["status"], "journal-recorded")
        self.assertEqual(report["journal_artifacts"][name]["sequence"], finish["sequence"])
        self.assertEqual(pending_contributions(self.private), [])
        self.assertFalse((self.repo / name).exists())
        self.assertEqual(self.record.read(), before)
        self.assertEqual(subprocess.check_output(["git", "-C", str(workspace), "show", report["commit"] + ":" + name]),
                         (workspace / name).read_bytes())
        self.end(run)
        self.assertEqual(self.capture(run, workspace), report)
        with self.assertRaisesRegex(ValueError, "different, awake"):
            integrate(self.record, run, run, publish=True)

    def test_missing_foreign_prelaunch_postrun_and_changed_artifacts_stay_pending(self):
        for case in ("unfinished", "foreign", "prelaunch", "postrun", "changed", "unlaunched"):
            with self.subTest(case=case):
                run, workspace = self.new_run()
                name = "evidence/native-residents/report.json"; (workspace / name).write_text('{"claim":1}\n')
                if case not in ("prelaunch", "unlaunched"): self.launch(run)
                if case == "postrun": self.end(run)
                if case != "unfinished": self.finish(workspace, name, "bob" if case == "foreign" else run)
                if case == "prelaunch": self.launch(run)
                if case == "changed": (workspace / name).write_text('{"claim":2}\n')
                self.assertEqual(self.capture(run, workspace)["status"], "pending-review")
                if case != "postrun": self.end(run)

    def test_modifications_deletions_renames_mixed_and_nonreport_paths_stay_pending(self):
        for case in ("modify", "delete", "rename", "mixed", "partialreports", "nested", "executable", "source", "newline", "symlink"):
            with self.subTest(case=case):
                run, workspace = self.new_run(); self.launch(run)
                name = {"modify": "evidence/native-residents/prior.md", "nested": "evidence/native-residents/sub/report.md",
                        "source": "source.txt", "newline": "evidence/native-residents/report\nname.md"}.get(
                            case, "evidence/native-residents/report.md")
                (workspace / name).parent.mkdir(parents=True, exist_ok=True)
                (workspace / name).write_text("published history\n" if case == "rename" else
                                               "target" if case == "symlink" else "report\n")
                self.finish(workspace, name, run)
                if case in ("delete", "rename"): (workspace / "evidence/native-residents/prior.md").unlink()
                if case == "mixed": (workspace / "source.txt").write_text("changed\n")
                if case == "partialreports":
                    (workspace / "evidence/native-residents/z-unfinished.json").write_text("{}\n")
                if case == "executable": (workspace / name).chmod(0o755)
                if case == "symlink":
                    (workspace / name).unlink(); (workspace / name).symlink_to("target")
                    git(workspace, "add", ".")
                    git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
                        "user.email=test@local", "commit", "-m", "Committed symlink with matching blob bytes")
                self.assertEqual(self.capture(run, workspace)["status"], "pending-review")
                self.end(run)

    def test_latest_finish_wins_and_later_launch_cannot_reuse_old_proof(self):
        run, workspace = self.new_run(); self.launch(run)
        name = "evidence/native-residents/report.md"; (workspace / name).write_text("first\n")
        self.finish(workspace, name, run)
        (workspace / name).write_text("second\n"); last = self.finish(workspace, name, run)
        state, events, _ = self.record.read(); item = state["life"]["runs"][run]
        self.assertEqual(finished_reports(events, item)[name]["sequence"], last["sequence"])
        later = item | {"launched_sequence": state["sequence"]}
        self.assertEqual(finished_reports(events, later), {})
        (workspace / name).write_text("first\n")
        self.assertEqual(self.capture(run, workspace)["status"], "pending-review")

    def test_failed_receipt_replace_preserves_prior_json_and_candidate(self):
        run, workspace = self.new_run(); self.launch(run)
        name = "evidence/native-residents/report.md"; (workspace / name).write_text("report\n")
        first = self.capture(run, workspace)
        path = self.private / run / "contribution.json"; before = path.read_bytes()
        self.finish(workspace, name, run)
        with patch("house.home_work.os.replace", side_effect=OSError("interrupted publication")):
            with self.assertRaisesRegex(OSError, "interrupted publication"): self.capture(run, workspace)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(git(workspace, "rev-parse", "HEAD"), first["commit"])
        self.assertEqual(self.capture(run, workspace)["status"], "journal-recorded")

    def test_coordinator_preserves_finished_report_after_interruption(self):
        run, workspace = self.new_run(); self.launch(run)
        name = "evidence/native-residents/report.md"; (workspace / name).write_text("finished before crash\n")
        self.finish(workspace, name, run)
        runtime = self.private / "unused-fixture-runtime.pyz"
        with zipfile.ZipFile(runtime, "w") as archive:
            archive.writestr("__main__.py", "raise AssertionError('terminal preservation must not execute a runtime')\n")
        coordinator = Coordinator(self.record, runtime)
        coordinator.finish(run, {"outcome": "interrupted", "exit_code": -9, "usage": {}, "elapsed_seconds": 1})
        report = json.loads((self.private / run / "contribution.json").read_text())
        self.assertEqual(report["status"], "journal-recorded")
        self.assertTrue((self.private / run / "preservation.json").is_file())
        self.assertEqual(self.record.read()[0]["life"]["runs"][run]["outcome"], "interrupted")
        self.assertEqual(pending_contributions(self.private), [])

    @unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX"), "cannot nest candidate sandbox")
    def test_explicit_independent_publication_remains_available(self):
        run, workspace = self.new_run(); self.launch(run)
        name = "evidence/native-residents/report.md"; (workspace / name).write_text("publish deliberately\n")
        self.finish(workspace, name, run); self.capture(run, workspace); self.end(run)
        result = integrate(self.record, run, "alice", publish=True)
        self.assertEqual(result["status"], "integrated")
        self.assertEqual((self.repo / name).read_text(), "publish deliberately\n")
