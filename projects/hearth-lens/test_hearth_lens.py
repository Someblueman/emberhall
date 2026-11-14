"""Real disposable journals and CLI checks; no canonical house operations."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from tests.support import HouseCase

SCRIPT = Path(__file__).with_name("hearth_lens.py")
spec = importlib.util.spec_from_file_location("hearth_lens", SCRIPT)
lens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)


class HearthLensTests(HouseCase):
    def run_lens(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=20)

    def trace(self, **args):
        state, events, head = self.record.read()
        return lens.build_trace(state, events, head, **args)

    def test_expired_reclaim_is_distinct_from_released_claim_and_ready_generation(self):
        self.task()
        base = self.record.read()[0]["at"]

        def append(offset, op, actor, data):
            with patch("house.record.time.time", return_value=base + offset):
                return self.record.append(op, actor, data)

        append(1, "claim", "alice", {"task": "work", "expect": 0, "token": "SECRET-one", "seconds": 2})
        append(3, "say", "bob", {"text": "At the exact lease boundary."})
        self.assertEqual(self.trace(task="work")["summary_at_head"]["status"],
                         "lease expired; fate unconfirmed")
        second = append(4, "claim", "bob", {"task": "work", "expect": 1, "token": "SECRET-two", "seconds": 2})
        append(5, "release", "bob", {"task": "work", "token": "SECRET-two", "note": "Hand over."})
        append(8, "ready", "alice", {"task": "work", "expect": 2, "ready": False})
        third = append(9, "claim", "alice", {"task": "work", "expect": 3, "token": "SECRET-three", "seconds": 60})
        content = b"PRIVATE_ARTIFACT"
        append(10, "finish", "alice", {"task": "work", "token": "SECRET-three", "result": "Finished.",
               "artifacts": {"note.txt": {"sha256": hashlib.sha256(content).hexdigest(),
                                          "base64": base64.b64encode(content).decode()}}})
        trace = self.trace(task="work")
        rows = {item["sequence"]: item for item in trace["events"]}
        self.assertEqual(rows[second["sequence"]]["inference"]["generation"], 1)
        self.assertEqual(rows[second["sequence"]]["fields"]["generation"], 2)
        self.assertNotIn("inference", rows[third["sequence"]])
        self.assertEqual(rows[third["sequence"]]["fields"]["generation"], 4)
        self.assertEqual(trace["summary_at_head"]["status"], "done")
        serialized = json.dumps(trace)
        self.assertNotIn("SECRET-", serialized)
        self.assertNotIn("PRIVATE_ARTIFACT", serialized)
        self.assertNotIn(base64.b64encode(content).decode(), serialized)

    def test_task_and_resident_follow_explicit_help_run_and_controller_receipts(self):
        self.task()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        help_receipt = self.record.append("life", "alice", {
            "kind": "help", "task": "work", "request": "assist", "reason": "Independent help"})
        start = {"kind": "run-start", "run": "r1", "resident": "resident-r1", "agent": "codex",
                 "model": "gpt-6.1-sol", "source_head": "a" * 40, "workspace": "residents/r1",
                 "policy_revision": "fixture", "mode": "work", "help_request": "assist"}
        started = self.record.append("life", "watch-keeper", start)
        self.record.append("arrive", "resident-r1", {"name": "Helper"})
        launched = self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": "r1", "pgid": 12345})
        report = self.record.append("say", "watch-keeper", {"text": 'house-home-result-v1 {"run":"r1","outcome":"success"}'})
        finish = self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": "r1",
                  "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        resolved = self.record.append("life", "watch-keeper", {"kind": "help-resolved", "request": "assist", "reason": "Handled"})
        unrelated = self.record.append("say", "bob", {"text": "Mention work, alice and r1 without a typed link."})
        expected = {item["sequence"] for item in (help_receipt, started, launched, report, finish, resolved)}
        for selector in ({"task": "work"}, {"resident": "alice"}, {"resident": "resident-r1"}):
            sequences = {item["sequence"] for item in self.trace(**selector)["events"]}
            self.assertTrue(expected <= sequences)
            self.assertNotIn(unrelated["sequence"], sequences)

    def test_bound_pages_preserve_references_order_counts_and_full_head_summary(self):
        self.task()
        for n in range(5):
            self.record.append("say", "alice", {"text": f"A note {n}"})
        before = copy.deepcopy(self.record.read())
        trace = self.trace(resident="alice", limit=2)
        older = self.trace(resident="alice", limit=200, before=trace["page"]["next_before"])
        together = older["events"] + trace["events"]
        self.assertEqual([item["sequence"] for item in together],
                         [2, 4, 5, 6, 7, 8, 9])
        self.assertEqual(trace["page"]["omitted_earlier"], 5)
        self.assertEqual(older["summary_at_head"], trace["summary_at_head"])
        self.assertEqual(older["source"], trace["source"])
        for item in together:
            self.assertEqual(item["id"], before[1][item["sequence"] - 1]["id"])
        self.assertEqual(self.record.read(), before)
        missing = self.trace(task="does-not-exist")
        self.assertIsNone(missing["summary_at_head"])
        self.assertEqual(missing["page"]["matching_total"], 0)

    def test_untrusted_speech_reports_are_bounded_and_control_characters_stay_quoted(self):
        for text in ('house-home-result-v1 {broken',
                     'house-home-result-v1 {"run":[],"task":{},"model":{"nested":1}}',
                     'house-home-result-v1 {"run":"x","model":"' + 'z' * 500 + '"}',
                     '\x1b[31m' + 'a' * 500):
            self.record.append("say", "alice", {"text": text, "task": []})
        trace = self.trace(resident="alice")
        rendered = lens.format_text(trace)
        self.assertNotIn('\x1b', rendered)
        self.assertNotIn('z' * 181, rendered)
        self.assertTrue(any(row.get("detail_truncated") for row in trace["events"]))
        self.assertTrue(any("model" in row.get("fields_truncated", []) for row in trace["events"]))

    def test_source_review_edges_follow_stopped_contribution_without_prose_matching(self):
        # Graph-only fixture: verification/authority is tested through real journals above.
        events = [
            {"op": "life", "actor": "alice", "data": {"kind": "help", "task": "work", "request": "build"}},
            {"op": "life", "actor": "watch-keeper", "data": {"kind": "run-start", "run": "builder", "help_request": "build", "resident": "one"}},
            {"op": "life", "actor": "watch-keeper", "data": {"kind": "help", "request": "review", "review_run": "builder"}},
            {"op": "life", "actor": "watch-keeper", "data": {"kind": "run-start", "run": "reviewer", "help_request": "review", "resident": "two"}},
            {"op": "say", "actor": "bob", "data": {"text": "work, build, review and reviewer"}},
        ]
        self.assertEqual(lens.links(events, task="work", resident=None),
                         ({"build", "review"}, {"builder", "reviewer"}))

    def test_real_cli_is_read_only_and_rejects_incomplete_journal_without_output(self):
        self.task()
        (self.repo / "source.txt").write_text("Source remains staged.")
        self.record.git("add", "source.txt")
        before = copy.deepcopy(self.record.read())
        refs = self.record.git("for-each-ref")
        index = (self.record.gitdir / "index").read_bytes()
        result = self.run_lens("--task", "work", "--json", "--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["source"]["journal_head"], before[2])
        self.assertEqual(output["events"][0]["sequence"], 4)
        text = self.run_lens("--resident", "alice")
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn("filtered view does not acknowledge", text.stdout)
        self.assertEqual(self.record.read(), before)
        self.assertEqual(self.record.git("for-each-ref"), refs)
        self.assertEqual((self.record.gitdir / "index").read_bytes(), index)
        # Only this disposable fixture is damaged; no repair or partial output.
        self.record.git("update-ref", "refs/house/foundation", before[2])
        broken_refs = self.record.git("for-each-ref")
        failed = self.run_lens("--task", "work")
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, "")
        self.assertIn("foundation anchor mismatch", failed.stderr)
        self.assertEqual(self.record.git("for-each-ref"), broken_refs)
        with self.assertRaisesRegex(ValueError, "missing foundation"):
            lens.build_trace(before[0], before[1][3:], before[2], task="work")

    def test_cli_invalid_bounds_and_unfounded_repository_never_create_a_journal(self):
        for args in (("--task", "work", "--limit", "0"), ("--task", "work", "--limit", "201"),
                     ("--task", "work", "--before", "0"), ("--task", ""),
                     ("--task", "work", "--resident", "alice")):
            failed = self.run_lens(*args)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(failed.stdout, "")
        empty = self.new_repo("empty")
        failed = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(empty), "--task", "work"],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, "")
        self.assertFalse((empty / ".git/refs/heads/house-ledger").exists())
