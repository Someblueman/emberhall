"""Review-task completion from a terminal integration receipt."""
import base64
import hashlib
import json
import shutil
from pathlib import Path
from unittest.mock import patch

from house import review_completion
from house.home_work import git
from house import staffing
from tests.support import HouseCase


class ReviewCompletionTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "source.txt").write_text("base\n")
        git(self.repo, "add", "source.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "fixture")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        # Enable helper staffing for this fixture without a full owner migration.
        patcher = patch.object(staffing, "enabled", lambda state: True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.private = self.record.common / "house-home"
        self.private.mkdir(exist_ok=True)

    def _setup_contribution(self, run="source-run", author=None):
        import subprocess
        if author is None:
            author = run + "-author"
        workspace = self.private / "residents" / run
        if workspace.exists():
            subprocess.run(["rm", "-rf", str(workspace)], check=True)
        workspace.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--no-tags",
                        str(self.repo), str(workspace)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(workspace), "remote", "remove", "origin"], capture_output=True)
        (workspace / "contribution.txt").write_text("contribution\n")
        git(workspace, "add", "contribution.txt")
        git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "contribution")
        commit = git(workspace, "rev-parse", "HEAD")
        # Run-start with a fresh resident not yet in residents, then arrive.
        # This matches the checkpoint fixture order and the life.py fence.
        self.record.append("life", "watch-keeper", {
            "kind": "run-start", "run": run, "resident": author,
            "agent": "codex", "model": "gpt-6.1-sol", "source_head": self.base,
            "workspace": "residents/" + run, "policy_revision": "fixture", "mode": "work"})
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": run, "pgid": 12345})
        self.record.append("arrive", author, {"name": author.replace("-", " ").title()})
        self.record.append("life", "watch-keeper", {
            "kind": "run-finish", "run": run, "outcome": "success",
            "exit_code": 0, "usage": {"input_tokens": 1}, "elapsed_seconds": 1})
        # Contribution report for source() validation.
        (self.private / run).mkdir(parents=True, exist_ok=True)
        (self.private / run / "contribution.json").write_text(json.dumps(
            {"base": self.base, "commit": commit}))
        return commit

    def _setup_task(self, task="review-task", reviewer=None, run="source-run"):
        if reviewer is None:
            reviewer = task + "-reviewer"
        state = self.record.read()[0]
        if reviewer not in state["residents"]:
            self.record.append("arrive", reviewer, {"name": reviewer.replace("-", " ").title()})
        self.record.append("task", reviewer, {
            "task": task, "title": "Review", "description": "Review",
            "helper": "review", "review_run": run})
        token = "token-" + task
        self.record.append("claim", reviewer, {
            "task": task, "token": token, "expect": 0, "seconds": 3600})
        return token

    def _write_receipt(self, run, commit, status="integrated", actor="bob", base=None, **extra):
        base = base or self.base
        receipt = {"run": run, "actor": actor, "base": base, "contribution": commit,
                   "status": status,
                   "candidate": "integration-deadbeef",
                   "diagnostics": {"kind": "tail"}}
        if status == "integrated":
            if "candidate_head" not in extra:
                if commit != "0" * 40:
                    git(self.repo, "fetch", str(self.private / "residents" / run), commit)
                    git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                        "-c", "user.email=test@local", "merge", "--no-ff", "FETCH_HEAD", "-m", f"merge {run}")
                    receipt["candidate_head"] = git(self.repo, "rev-parse", "HEAD")
                else:
                    receipt["candidate_head"] = commit
            receipt["test_scope"] = "prose"
            receipt["test_exit"] = 0
        elif status == "rejected":
            receipt["reason"] = "defect X"
        receipt.update(extra)
        (self.private / run / "integration.json").write_text(json.dumps(receipt, indent=2))
        return receipt

    def test_integrated_completion_stores_safe_projection(self):
        commit = self._setup_contribution()
        token = self._setup_task()
        reviewer = "review-task-reviewer"
        self._write_receipt("source-run", commit, status="integrated", actor=reviewer)
        result = review_completion.complete(self.record, "review-task", reviewer, token, "req-1")
        # terminal finish receipt (ordinary finish semantics)
        self.assertIn("sequence", result)
        # Task is done.
        task = self.record.read()[0]["tasks"]["review-task"]
        self.assertEqual(task["status"], "done")
        self.assertEqual(task["result"][:20], "Review completed via")
        self.assertNotIn("accepted", task["result"].lower().replace("without asserting", ""))
        # Projection artifact exists and is safe.
        artifacts = task["artifacts"]
        self.assertEqual(len(artifacts), 1)
        name, saved = next(iter(artifacts.items()))
        self.assertEqual(name, "evidence/review-completions/review-task-source-run.json")
        body = base64.b64decode(saved["base64"])
        self.assertEqual(hashlib.sha256(body).hexdigest(), saved["sha256"])
        projection = json.loads(body)
        self.assertEqual(projection["task"], "review-task")
        self.assertEqual(projection["review_run"], "source-run")
        self.assertEqual(projection["status"], "integrated")
        self.assertEqual(projection["contribution"], commit)
        # Private fields omitted.
        self.assertNotIn("candidate", projection)
        self.assertNotIn("diagnostics", projection)
        self.assertNotIn("integration-deadbeef", body.decode())

    def test_rejected_status_remains_distinct(self):
        commit = self._setup_contribution()
        token = self._setup_task(task="review-task2", run="source-run")
        reviewer = "review-task2-reviewer"
        self._write_receipt("source-run", commit, status="rejected", actor=reviewer)
        result = review_completion.complete(self.record, "review-task2", reviewer, token, "req-reject")
        task = self.record.read()[0]["tasks"]["review-task2"]
        body = base64.b64decode(next(iter(task["artifacts"].values()))["base64"])
        self.assertEqual(json.loads(body)["status"], "rejected")

    def test_absent_receipt_rejected(self):
        commit = self._setup_contribution()
        reviewer = "review-absent-reviewer"
        token = self._setup_task(task="review-absent", reviewer=reviewer)
        with self.assertRaisesRegex(ValueError, "absent"):
            review_completion.complete(self.record, "review-absent", reviewer, token, "req-absent")

    def test_prepared_receipt_rejected(self):
        commit = self._setup_contribution()
        reviewer = "review-prepared-reviewer"
        token = self._setup_task(task="review-prepared", reviewer=reviewer)
        self._write_receipt("source-run", commit, status="prepared", actor=reviewer)
        with self.assertRaisesRegex(ValueError, "not terminal"):
            review_completion.complete(self.record, "review-prepared", reviewer, token, "req-prepared")

    def test_mismatched_contribution_rejected(self):
        commit = self._setup_contribution()
        reviewer = "review-mismatch-reviewer"
        token = self._setup_task(task="review-mismatch", reviewer=reviewer)
        self._write_receipt("source-run", "0" * 40, status="integrated", actor=reviewer)
        with self.assertRaisesRegex(ValueError, "mismatch"):
            review_completion.complete(self.record, "review-mismatch", reviewer, token, "req-mismatch")

    def test_foreign_token_rejected(self):
        commit = self._setup_contribution()
        reviewer = "review-foreign-reviewer"
        token = self._setup_task(task="review-foreign", reviewer=reviewer)
        self._write_receipt("source-run", commit, status="integrated", actor=reviewer)
        with self.assertRaisesRegex(ValueError, "token"):
            review_completion.complete(self.record, "review-foreign", reviewer, "wrong", "req-foreign")

    def test_foreign_owner_rejected(self):
        commit = self._setup_contribution()
        reviewer = "review-owner-reviewer"
        token = self._setup_task(task="review-owner", reviewer=reviewer)
        self._write_receipt("source-run", commit, status="integrated", actor=reviewer)
        # A different awake resident tries to complete it.
        self.record.append("arrive", "outsider", {"name": "Outsider"})
        with self.assertRaisesRegex(ValueError, "not owned"):
            review_completion.complete(self.record, "review-owner", "outsider", token, "req-owner")

    def test_author_self_review_rejected(self):
        author = "selfrun-author"
        commit = self._setup_contribution(run="selfrun", author=author)
        # wake author before it can be forced to attempt self-review.
        self.record.append("wake", author, {})
        # Task owned by the author - must be rejected as non-independent.
        token = self._setup_task(task="review-self", reviewer=author, run="selfrun")
        self._write_receipt("selfrun", commit, status="integrated", actor=author)
        # integrate.source enforces author != actor; review_completion must
        # also enforce independence, so either message proves the fence.
        with self.assertRaisesRegex(ValueError, "different|independent"):
            review_completion.complete(self.record, "review-self", author, token, "req-self")

    def test_non_review_task_rejected(self):
        self.record.append("arrive", "plain-reviewer", {"name": "Plain Reviewer"})
        self.record.append("task", "plain-reviewer", {"task": "plain", "title": "Plain", "description": "x"})
        self.record.append("claim", "plain-reviewer", {"task": "plain", "token": "plain-tok", "expect": 0, "seconds": 3600})
        commit = self._setup_contribution(run="other-run")
        self._write_receipt("other-run", commit, status="integrated", actor="plain-reviewer")
        with self.assertRaisesRegex(ValueError, "not a review"):
            review_completion.complete(self.record, "plain", "plain-reviewer", "plain-tok", "req-plain")

    def test_idempotent_retry_preserves_result(self):
        commit = self._setup_contribution()
        reviewer = "review-idem-reviewer"
        token = self._setup_task(task="review-idem", reviewer=reviewer)
        self._write_receipt("source-run", commit, status="integrated", actor=reviewer)
        first = review_completion.complete(self.record, "review-idem", reviewer, token, "idem-req")
        seq = first["sequence"]
        head = self.record.read()[2]
        again = review_completion.complete(self.record, "review-idem", reviewer, token, "idem-req")
        self.assertEqual(again["sequence"], seq)
        self.assertTrue(again.get("replayed"))
        self.assertEqual(self.record.read()[2], head, "retry must not append a new event")

    def test_known_result_recovers_lost_reply(self):
        commit = self._setup_contribution()
        reviewer = "review-known-reviewer"
        token = self._setup_task(task="review-known", reviewer=reviewer)
        self._write_receipt("source-run", commit, status="integrated", actor=reviewer)
        result = review_completion.complete(self.record, "review-known", reviewer, token, "known-req")
        known = review_completion.known_result(self.record, "review-known", reviewer, token, "known-req")
        self.assertEqual(known["sequence"], result["sequence"])
        self.assertTrue(known["replayed"])

    def test_stale_lease_rejected_after_expiry(self):
        commit = self._setup_contribution()
        reviewer = "review-stale-reviewer"
        self.record.append("arrive", reviewer, {"name": reviewer.replace("-", " ").title()})
        self.record.append("task", reviewer, {"task": "review-stale", "title": "t", "description": "d",
                                           "helper": "review", "review_run": "source-run"})
        token = "stale-tok"
        self.record.append("claim", reviewer, {"task": "review-stale", "token": token, "expect": 0, "seconds": 1})
        self._write_receipt("source-run", commit, status="integrated", actor=reviewer)
        # Force expiry by editing state at beyond until (simulate time passage by bumping at).
        # Claim was at state at == now, until = now+1. Advance by sleeping? Instead directly patch.
        state = self.record.read()[0]
        # Move at 100 seconds forward via a no-op but advance event? We cannot move at without an event.
        # Add a say event later to advance at.
        import time as _time
        # Sleep 2 seconds so wall clock exceeds until.
        import time
        time.sleep(1.2)
        with self.assertRaisesRegex(ValueError, "expired"):
            review_completion.complete(self.record, "review-stale", reviewer, token, "stale-req")

    def test_advanced_base_rejection_and_integration_succeed(self):
        commit = self._setup_contribution(run="adv-run")
        # Advance shared HEAD after contribution source_head was recorded.
        (self.repo / "shared.txt").write_text("advanced\n")
        git(self.repo, "add", "shared.txt")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "advance shared")
        advanced_head = git(self.repo, "rev-parse", "HEAD")

        reviewer = "adv-reviewer"
        tok_rej = self._setup_task(task="review-adv-rej", reviewer=reviewer, run="adv-run")
        self._write_receipt("adv-run", commit, status="rejected", actor=reviewer, base=advanced_head)
        res_rej = review_completion.complete(self.record, "review-adv-rej", reviewer, tok_rej, "adv-rej-req")
        self.assertIn("sequence", res_rej)
        self.assertEqual(self.record.read()[0]["tasks"]["review-adv-rej"]["status"], "done")

        # Now merge the contribution onto advanced_head and record integrated receipt.
        tok_int = self._setup_task(task="review-adv-int", reviewer=reviewer, run="adv-run")
        self._write_receipt("adv-run", commit, status="integrated", actor=reviewer, base=advanced_head)
        res_int = review_completion.complete(self.record, "review-adv-int", reviewer, tok_int, "adv-int-req")
        self.assertIn("sequence", res_int)
        self.assertEqual(self.record.read()[0]["tasks"]["review-adv-int"]["status"], "done")

    def test_forged_integrated_anchor_rejected(self):
        commit = self._setup_contribution(run="forged-run")
        reviewer = "forged-reviewer"
        token = self._setup_task(task="review-forged", reviewer=reviewer, run="forged-run")
        # Receipt claims integrated with candidate_head == commit (not merged into shared HEAD).
        self._write_receipt("forged-run", commit, status="integrated", actor=reviewer,
                            candidate_head=commit)
        with self.assertRaisesRegex(ValueError, "outside current source history"):
            review_completion.complete(self.record, "review-forged", reviewer, token, "forged-req")

    def test_all_four_terminal_outcomes(self):
        for idx, status in enumerate(("rejected", "conflict", "tests-failed", "integrated")):
            run_id = f"term-run-{idx}"
            commit = self._setup_contribution(run=run_id)
            reviewer = f"term-reviewer-{idx}"
            task_id = f"review-term-{idx}"
            token = self._setup_task(task=task_id, reviewer=reviewer, run=run_id)
            self._write_receipt(run_id, commit, status=status, actor=reviewer)
            res = review_completion.complete(self.record, task_id, reviewer, token, f"term-req-{idx}")
            self.assertIn("sequence", res)
            self.assertEqual(self.record.read()[0]["tasks"][task_id]["status"], "done")

    def test_terminal_completion_survives_cleaned_source_room(self):
        for index, status in enumerate(("rejected", "conflict", "tests-failed", "integrated")):
            with self.subTest(status=status):
                run = f"cleaned-{index}"
                commit = self._setup_contribution(run=run)
                reviewer = f"cleaned-reviewer-{index}"
                task = f"review-cleaned-{index}"
                token = self._setup_task(task=task, reviewer=reviewer, run=run)
                self._write_receipt(run, commit, status=status, actor=reviewer)
                workspace = self.private / "residents" / run
                receipt_path = self.private / run / "integration.json"
                report_path = self.private / run / "contribution.json"
                receipt, report = receipt_path.read_bytes(), report_path.read_bytes()
                shutil.rmtree(workspace)

                result = review_completion.complete(self.record, task, reviewer, token, f"close-{run}")

                self.assertIn("sequence", result)
                self.assertEqual(self.record.read()[0]["tasks"][task]["status"], "done")
                self.assertFalse(workspace.exists())
                self.assertEqual(receipt_path.read_bytes(), receipt)
                self.assertEqual(report_path.read_bytes(), report)

    def test_cleaned_room_does_not_bypass_receipt_or_identity_checks(self):
        commit = self._setup_contribution(run="cleaned")
        reviewer = "cleaned-reviewer"
        task = "review-cleaned"
        token = self._setup_task(task=task, reviewer=reviewer, run="cleaned")
        receipt = self._write_receipt("cleaned", commit, actor=reviewer)
        shutil.rmtree(self.private / "residents" / "cleaned")
        path = self.private / "cleaned" / "integration.json"
        invalid = [
            ({"status": "prepared"}, "not terminal"),
            ({"status": "reviewed"}, "not terminal"),
            ({"contribution": "0" * 40}, "contribution mismatch"),
            ({"candidate_head": "0" * 40}, "outside current source history"),
            ({"actor": "cleaned-author"}, "not independent"),
            ({"run": "another-run"}, "run mismatch"),
        ]
        for changes, reason in invalid:
            with self.subTest(changes=changes):
                path.write_text(json.dumps(receipt | changes))
                with self.assertRaisesRegex(ValueError, reason):
                    review_completion.complete(self.record, task, reviewer, token, "invalid-cleaned")
                self.assertEqual(self.record.read()[0]["tasks"][task]["status"], "claimed")
        path.write_text(json.dumps(receipt))
        report_path = self.private / "cleaned" / "contribution.json"
        report = json.loads(report_path.read_text())
        report_path.write_text(json.dumps(report | {"commit": "0" * 40}))
        with self.assertRaisesRegex(ValueError, "contribution mismatch"):
            review_completion.complete(self.record, task, reviewer, token, "changed-report")
        path.unlink()
        with self.assertRaisesRegex(ValueError, "absent"):
            review_completion.complete(self.record, task, reviewer, token, "missing-cleaned")

    def test_terminal_receipt_still_checks_existing_source_room(self):
        commit = self._setup_contribution()
        reviewer = "changed-reviewer"
        task = "review-changed"
        token = self._setup_task(task=task, reviewer=reviewer)
        self._write_receipt("source-run", commit, actor=reviewer)
        workspace = self.private / "residents" / "source-run"
        git(workspace, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "--allow-empty", "-m", "changed")
        with self.assertRaisesRegex(ValueError, "identity changed"):
            review_completion.complete(self.record, task, reviewer, token, "changed-room")

    def test_retry_token_collision_and_post_expiry_immutable_replay(self):
        commit = self._setup_contribution(run="retry-run")
        reviewer = "retry-reviewer"
        self.record.append("arrive", reviewer, {"name": "Retry Reviewer"})
        self.record.append("task", reviewer, {"task": "review-retry", "title": "t", "description": "d",
                                              "helper": "review", "review_run": "retry-run"})
        token = "retry-tok"
        self.record.append("claim", reviewer, {"task": "review-retry", "token": token, "expect": 0, "seconds": 1})
        self._write_receipt("retry-run", commit, status="rejected", actor=reviewer)
        first = review_completion.complete(self.record, "review-retry", reviewer, token, "retry-req")
        # Changed token with same requestid must be rejected.
        with self.assertRaisesRegex(ValueError, "token mismatch"):
            review_completion.complete(self.record, "review-retry", reviewer, "wrong-tok", "retry-req")
        # Mutate/remove integration.json and let lease expire; same-payload retry must still replay.
        (self.record.common / "house-home" / "retry-run" / "integration.json").unlink()
        import time
        time.sleep(1.2)
        replay = review_completion.complete(self.record, "review-retry", reviewer, token, "retry-req")
        self.assertEqual(replay["sequence"], first["sequence"])
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["status"], "rejected")

    def test_cli_and_resident_actions_wiring(self):
        from house import __main__ as house_main
        from house import resident_actions
        args = house_main.parser().parse_args(
            ["review-complete", "--as", "r1", "--request", "req1", "task1", "--token", "tok1"]
        )
        self.assertEqual(args.command, "review-complete")
        self.assertEqual(args.actor, "r1")
        self.assertEqual(args.request, "req1")
        self.assertEqual(args.task, "task1")
        self.assertEqual(args.token, "tok1")

        act_args = resident_actions.parser().parse_args(
            ["review-complete", "--as", "r1", "--request", "req1", "--task", "task1", "--token", "tok1"]
        )
        self.assertEqual(act_args.command, "review-complete")
        self.assertEqual(act_args.actor, "r1")
        self.assertEqual(act_args.request, "req1")
        self.assertEqual(act_args.task, "task1")
        self.assertEqual(act_args.token, "tok1")
