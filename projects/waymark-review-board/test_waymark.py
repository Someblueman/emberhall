"""Real disposable verified journals and actual CLI boundaries; no model calls."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from house import life
from tests.support import HouseCase
from tests.test_helper_staffing import fixture, offer, regulars, start_data

SCRIPT = Path(__file__).with_name("waymark.py")
spec = importlib.util.spec_from_file_location("waymark", SCRIPT)
waymark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(waymark)


class WaymarkTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = fixture(self)
        self.repo = self.record.root

    def end(self, run):
        return self.record.append("life", life.CONTROLLER, {
            "kind": "run-finish", "run": run, "outcome": "success", "exit_code": 0,
            "usage": {}, "elapsed_seconds": 1})

    def source(self, run, path="projects/demo/app.py"):
        start = self.record.append("life", life.CONTROLLER, start_data(run))
        who = "resident-" + run
        self.record.append("arrive", who, {"name": "Name " + run})
        self.record.append("life", life.CONTROLLER, {"kind": "run-launched", "run": run, "pgid": 12345})
        self.record.append("task", who, {"task": run + "-work", "title": "Work", "description": "Fixture"})
        self.record.append("claim", who, {"task": run + "-work", "expect": 0,
            "token": "SECRET-TOKEN", "seconds": 1800})
        body = b"PRIVATE_ARTIFACT_BODY"
        finish = self.record.append("finish", who, {"task": run + "-work", "token": "SECRET-TOKEN",
            "result": "PRIVATE result", "artifacts": {path: {
                "sha256": hashlib.sha256(body).hexdigest(), "base64": base64.b64encode(body).decode()}}})
        stop = self.end(run)
        return start, finish, stop

    def review(self, run, commit="b" * 40, paths=None, *, key=None):
        key = key or "review-" + run
        reason = (f"Independently review stopped contribution {run}, commit {commit}, "
                  f"paths {json.dumps(paths or ['projects/demo/app.py'])}. You are not its author.")
        return self.record.append("life", "alice", {"kind": "help", "request": key,
            "review_run": run, "reason": reason})

    def report(self, run, status="integrated", commit="b" * 40):
        return self.record.append("say", "bob", {"text": "house-integration-v1 " + json.dumps({
            "run": run, "actor": "bob", "contribution": commit, "status": status})})

    def read(self, **options):
        return waymark.read_board(str(self.repo), "alice", **options)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo),
            "--reviewer", "alice", *args], cwd=self.root, capture_output=True, text=True, timeout=30)

    def test_pending_terminal_and_author_rows_keep_exact_event_references(self):
        start, finish, stop = self.source("pending")
        request = self.review("pending")
        self.source("terminal")
        self.review("terminal")
        accepted = self.report("terminal")
        # Receipt replay is another announcement for the same contribution.
        replay = self.report("terminal")
        self.source("aaa-unknown")
        result = self.read(include_excluded=True)
        rows = {row["run"]: row for row in result["rows"]}
        self.assertEqual(result["totals"], {"suggested": 1, "excluded": 1, "unknown": 1})
        self.assertEqual([row["run"] for row in result["rows"]], ["pending", "terminal", "aaa-unknown"])
        row = rows["pending"]
        self.assertEqual(row["decision"], "suggested")
        self.assertEqual(row["commit"], "b" * 40)
        self.assertEqual(row["paths"], {"names": ["projects/demo/app.py"], "omitted": 0})
        self.assertEqual(row["start"]["sequence"], start["sequence"])
        self.assertEqual(row["stop"]["sequence"], stop["sequence"])
        self.assertEqual(row["finishes"][0]["event"],
                         {"sequence": finish["sequence"], "id": finish["request"]})
        self.assertEqual(row["metadata_events"], [{"sequence": request["sequence"], "id": request["request"]}])
        self.assertEqual(rows["terminal"]["reasons"], ["recorded-terminal-review"])
        self.assertEqual(rows["terminal"]["terminal"][0]["event"]["sequence"], replay["sequence"])
        self.assertGreater(replay["sequence"], accepted["sequence"])
        self.assertIsNone(rows["aaa-unknown"]["commit"])
        self.assertIn("unverified", row["metadata_basis"])
        self.assertTrue(row["private_pending_and_receipt_status"].startswith("unknown"))
        own = waymark.read_board(str(self.repo), "resident-pending", include_excluded=True)
        self.assertIn("source-author", next(r for r in own["rows"] if r["run"] == "pending")["reasons"])
        serialized = json.dumps(result)
        for secret in ("SECRET-TOKEN", "PRIVATE_ARTIFACT_BODY", "PRIVATE result",
                       base64.b64encode(b"PRIVATE_ARTIFACT_BODY").decode(), "workspace", "pgid"):
            self.assertNotIn(secret, serialized)

    def test_all_terminal_receipt_statuses_are_excluded(self):
        self.source("source")
        self.review("source")
        for status in ("integrated", "rejected", "conflict", "tests-failed"):
            with self.subTest(status=status):
                self.report("source", status)
                row = self.read(include_excluded=True)["rows"][0]
                self.assertEqual(row["reasons"], ["recorded-terminal-review"])
                self.assertEqual(row["terminal"][0]["status"], status)

    def test_assigned_help_blocks_until_recorded_stop_without_claiming_liveness(self):
        self.source("pending")
        request = self.review("pending")
        started = self.record.append("life", life.CONTROLLER, start_data(
            "reviewer", help_request="review-pending", mode="review"))
        row = self.read(include_excluded=True)["rows"][0]
        self.assertEqual(row["reasons"], ["active-assignment"])
        self.assertEqual(row["assignments"][0]["event"]["sequence"], request["sequence"])
        self.assertIn("not process liveness", row["assignments"][0]["basis"])
        self.end("reviewer")
        self.assertEqual(self.read()["rows"][0]["decision"], "suggested")
        self.assertLess(request["sequence"], started["sequence"])

    def test_bound_task_generations_and_claim_increment_are_not_confused(self):
        self.source("pending")
        self.review("pending")
        regulars(self.record)
        offer(self.record, "bound", helper="review", review_run="pending")
        self.record.append("life", "alice", {"kind": "help", "request": "bound-help",
            "task": "bound", "reason": "Bounded review"})
        hint = self.record.append("life", life.CONTROLLER, start_data("helper", "gpt-6-luna",
            help_request="bound-help", task="bound", task_generation=0, mode="review"))
        self.assertEqual(self.read(include_excluded=True)["rows"][0]["reasons"], ["active-assignment"])
        self.record.append("ready", "alice", {"task": "bound", "expect": 0, "ready": True})
        stale = self.read()["rows"][0]
        self.assertEqual(stale["decision"], "suggested")
        self.assertEqual(stale["stale_assignments"][0]["event"]["sequence"], hint["sequence"])
        self.assertEqual(stale["stale_assignments"][0]["current_generation"], 1)
        self.record.append("arrive", "resident-helper", {"name": "Helper"})
        claimed = self.record.append("claim", "resident-helper", {"task": "bound", "expect": 1,
            "token": "SECRET-live", "seconds": 1800})
        live = self.read(include_excluded=True)["rows"][0]
        self.assertEqual(live["reasons"], ["active-assignment"])
        self.assertEqual(live["stale_assignments"], [])
        self.assertEqual(live["assignments"][0]["event"]["sequence"], claimed["sequence"])
        at = self.record.read()[0]["at"]
        with patch("house.record.time.time", return_value=at + 1801):
            self.record.append("say", "alice", {"text": "Past the lease, no stop observed"})
        expired = self.read(include_excluded=True)["rows"][0]
        self.assertEqual(expired["reasons"], ["active-assignment"])
        self.assertIn("unended owner after lease expiry", expired["assignments"][0]["basis"])
        self.end("helper")
        self.assertEqual(self.read()["rows"][0]["decision"], "suggested")

    def test_helper_runs_are_removed_before_ordinary_rotation_window(self):
        for n in range(32):
            key = "ordinary" + str(n)
            self.record.append("life", life.CONTROLLER, start_data(key))
            self.end(key)
        regulars(self.record)  # Two active ordinary work starts are also counted.
        for n in range(2):
            key = "helper" + str(n)
            offer(self.record, key)
            self.record.append("life", "alice", {"kind": "help", "request": key,
                "task": key, "reason": "Bounded helper"})
            self.record.append("life", life.CONTROLLER, start_data(key, "gpt-6-luna",
                help_request=key, task=key, task_generation=0))
            self.end(key)
        rotation = self.read()["ordinary_rotation"]
        self.assertEqual(rotation["window"], 32)
        self.assertEqual(rotation["work"], {"codex": 32, "opencode": 0, "muse": 0, "agy": 0})
        self.assertEqual(sum(rotation["review"].values()), 0)

    def test_prefix_before_request_is_explicitly_incomplete_and_future_bounds_fail(self):
        _, _, stop = self.source("pending")
        self.review("pending")
        earlier = self.read(through=stop["sequence"])
        self.assertTrue(earlier["source"]["incomplete_prefix"])
        self.assertEqual(earlier["source"]["through"], stop["sequence"])
        self.assertEqual(earlier["rows"][0]["decision"], "unknown")
        self.assertIsNone(earlier["rows"][0]["commit"])
        self.assertFalse(self.read()["source"]["incomplete_prefix"])
        for args in (("--through", "99999"), ("--through", "0"), ("--limit", "51"),
                     ("--limit", "0"), ("--offset", "-1"), ("--reviewer", "unknown")):
            failed = self.cli(*args)
            self.assertEqual(failed.returncode, 2, failed.stderr)
            self.assertEqual(failed.stdout, "")

    def test_untrusted_announcements_conflicts_safe_output_and_bounded_pages(self):
        self.source("z-source", "other.txt")
        self.review("z-source", paths=["other.txt"])
        self.source("a-source")
        self.review("a-source", paths=["projects/demo/\x1b[31m.py", "/private/secret", "../secret"])
        for payload in ([], {"run": [], "status": "integrated"},
                        {"run": "z-source", "actor": "bob", "contribution": "b" * 40, "status": []},
                        {"run": "z-source", "actor": "someone-else", "contribution": "b" * 40, "status": "integrated"}):
            self.record.append("say", "bob", {"text": "house-integration-v1 " + json.dumps(payload)})
        self.record.append("say", "bob", {"text": "house-integration-v1 {broken"})
        self.review("z-source", commit="c" * 40, paths=["other.txt"], key="conflicting")
        result = self.read(limit=1)
        self.assertEqual(result["ignored_integration_announcements"], 5)
        self.assertEqual(result["page"]["next_offset"], 1)
        self.assertEqual(result["rows"][0]["run"], "a-source")
        self.assertEqual(result["rows"][0]["paths"]["omitted"], 3)
        second = self.read(limit=1, offset=1)["rows"][0]
        self.assertEqual(second["run"], "z-source")
        self.assertIn("conflicting recorded contribution commits", second["unknown"])
        self.assertIsNone(second["commit"])
        for text in ("\x1b", "/private/secret", "../secret"):
            self.assertNotIn(text, json.dumps(result))

    def test_real_cli_keeps_refs_index_and_saved_cursors_and_fails_closed(self):
        self.source("pending")
        self.review("pending")
        (self.repo / "source.txt").write_text("Staged bytes stay here")
        self.record.git("add", "source.txt")
        before = copy.deepcopy(self.record.read())
        refs = self.record.git("for-each-ref")
        index = (self.record.gitdir / "index").read_bytes()
        actual = self.cli("--limit", "1")
        self.assertEqual(actual.returncode, 0, actual.stderr)
        self.assertEqual(json.loads(actual.stdout), self.read(limit=1))
        self.assertEqual(self.record.read(), before)
        self.assertEqual(self.record.git("for-each-ref"), refs)
        self.assertEqual((self.record.gitdir / "index").read_bytes(), index)
        # Damage only this disposable fixture, after freezing its original refs.
        self.record.git("update-ref", "refs/house/foundation", before[2])
        broken = self.record.git("for-each-ref")
        failed = self.cli()
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, "")
        self.assertIn("foundation anchor mismatch", failed.stderr)
        self.assertEqual(self.record.git("for-each-ref"), broken)
        self.assertEqual((self.record.gitdir / "index").read_bytes(), index)

    def test_absent_journal_is_never_founded_or_restored(self):
        empty = self.new_repo("empty")
        result = self.cli("--repo", str(empty))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertFalse((empty / ".git/refs/heads/house-ledger").exists())
