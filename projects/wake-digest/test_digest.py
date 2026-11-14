import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from house.digest import build_digest, format_markdown, load_inputs


class TestWakeDigest(unittest.TestCase):
    def test_empty_events_preserves_bounds_and_limitations(self):
        payload = {"events": [], "has_more": False, "latest": 100, "through": 100}
        result = build_digest([payload])
        self.assertEqual(result["cursor"]["event_count"], 0)
        self.assertEqual(result["cursor"]["through"], 100)
        self.assertEqual(result["cursor"]["latest"], 100)
        self.assertFalse(result["cursor"]["has_more"])
        self.assertTrue(any("read-only" in lim.lower() for lim in result["limitations"]))

    def test_distinguishes_say_from_accepted_operations(self):
        payload = {
            "events": [
                {
                    "sequence": 10,
                    "actor": "resident-a",
                    "op": "say",
                    "at": 1700000000.0,
                    "id": "say-10",
                    "data": {"text": "I will claim task-x and finish it."},
                },
                {
                    "sequence": 11,
                    "actor": "resident-b",
                    "op": "claim",
                    "at": 1700000001.0,
                    "id": "claim-11",
                    "data": {"task": "task-x", "expect": 0, "seconds": 600, "token": "tok-1"},
                },
            ],
            "has_more": False,
            "latest": 11,
            "through": 11,
        }
        result = build_digest([payload])
        self.assertEqual(len(result["statements"]), 1)
        self.assertEqual(result["statements"][0]["sequence"], 10)
        self.assertEqual(len(result["claims_and_tasks"]), 1)
        self.assertEqual(result["claims_and_tasks"][0]["sequence"], 11)
        self.assertEqual(result["claims_and_tasks"][0]["op"], "claim")
        md = format_markdown(result)
        self.assertIn("Statements / Intentions (`say` — unverified)", md)
        self.assertIn("seq 10", md)
        self.assertIn("seq 11", md)

    def test_retains_errors_corrections_and_project_choices(self):
        payload = {
            "events": [
                {
                    "sequence": 20,
                    "actor": "watch-keeper",
                    "op": "life",
                    "at": 1700000020.0,
                    "id": "life-20",
                    "data": {"kind": "run-finish", "run": "r1", "outcome": "failed", "exit_code": 1},
                },
                {
                    "sequence": 21,
                    "actor": "resident-c",
                    "op": "supersede",
                    "at": 1700000021.0,
                    "id": "sup-21",
                    "data": {"key": "k1", "old": "v1", "new": "v2"},
                },
                {
                    "sequence": 22,
                    "actor": "resident-d",
                    "op": "shelf",
                    "at": 1700000022.0,
                    "id": "shelf-22",
                    "data": {"kind": "choice-vote", "choice": "c1", "idea": "wake-digest"},
                },
            ],
            "has_more": True,
            "latest": 30,
            "through": 22,
        }
        result = build_digest([payload])
        self.assertEqual(len(result["errors_and_failures"]), 1)
        self.assertEqual(result["errors_and_failures"][0]["sequence"], 20)
        self.assertEqual(len(result["corrections"]), 1)
        self.assertEqual(result["corrections"][0]["sequence"], 21)
        self.assertEqual(len(result["project_choices"]), 1)
        self.assertEqual(result["project_choices"][0]["sequence"], 22)
        self.assertTrue(result["cursor"]["has_more"])
        self.assertTrue(any("has_more=True" in lim for lim in result["limitations"]))

    def test_merges_paginated_inputs_and_detects_gaps(self):
        p1 = {
            "events": [
                {"sequence": 1, "actor": "a", "op": "wake", "at": 1.0, "id": "e1", "data": {}},
                {"sequence": 2, "actor": "a", "op": "sleep", "at": 2.0, "id": "e2", "data": {"through": 1}},
            ],
            "has_more": True,
            "latest": 5,
            "through": 2,
        }
        p2 = {
            "events": [
                {"sequence": 2, "actor": "a", "op": "sleep", "at": 2.0, "id": "e2", "data": {"through": 1}},
                {"sequence": 4, "actor": "b", "op": "wake", "at": 4.0, "id": "e4", "data": {}},
            ],
            "has_more": False,
            "latest": 5,
            "through": 4,
        }
        result = build_digest([p1, p2])
        self.assertEqual(result["cursor"]["event_count"], 3)
        self.assertEqual(result["cursor"]["first_sequence"], 1)
        self.assertEqual(result["cursor"]["last_sequence"], 4)
        self.assertEqual(result["cursor"]["gaps"], [[2, 4]])

    def test_cli_json_and_markdown_output(self):
        payload = {
            "events": [
                {
                    "sequence": 1659,
                    "actor": "resident-836035b42f354512a781b26410a12e39",
                    "op": "wake",
                    "at": 1794628693.85,
                    "id": "mailbox-wake-1659",
                    "data": {},
                }
            ],
            "has_more": False,
            "latest": 1660,
            "through": 1660,
        }
        with tempfile.TemporaryDirectory() as tmp:
            in_path = Path(tmp) / "read.json"
            in_path.write_text(json.dumps(payload), encoding="utf-8")
            script = Path(__file__).resolve().parent / "digest.py"
            proc = subprocess.run(
                [sys.executable, str(script), "--input", str(in_path), "--format", "json"],
                capture_output=True,
                text=True,
                check=True,
            )
            parsed = json.loads(proc.stdout)
            self.assertEqual(parsed["cursor"]["event_count"], 1)
            self.assertEqual(parsed["cursor"]["through"], 1660)

    # --- Repair regressions (Keeper probes 1670/1671) ---
    def test_two_contiguous_pages_to_latest_is_complete(self):
        # Keeper probe: [seq1, through1, latest2, has_more:true] + [seq2, through2, latest2, has_more:false]
        # must yield has_more=False with no gaps.
        p1 = {
            "events": [{"sequence": 1, "actor": "a", "op": "wake", "at": 1.0, "id": "e1", "data": {}}],
            "has_more": True,
            "latest": 2,
            "through": 1,
        }
        p2 = {
            "events": [{"sequence": 2, "actor": "a", "op": "sleep", "at": 2.0, "id": "e2", "data": {"through": 2}}],
            "has_more": False,
            "latest": 2,
            "through": 2,
        }
        result = build_digest([p1, p2])
        self.assertEqual(result["cursor"]["event_count"], 2)
        self.assertEqual(result["cursor"]["first_sequence"], 1)
        self.assertEqual(result["cursor"]["last_sequence"], 2)
        self.assertEqual(result["cursor"]["through"], 2)
        self.assertEqual(result["cursor"]["latest"], 2)
        self.assertEqual(result["cursor"]["gaps"], [])
        self.assertFalse(result["cursor"]["has_more"])
        self.assertFalse(any("has_more=True" in lim for lim in result["limitations"]))

    def test_conflicting_duplicate_sequence_rejected(self):
        p1 = {
            "events": [{"sequence": 1, "actor": "a", "op": "wake", "at": 1.0, "id": "e1", "data": {}}],
            "has_more": False,
            "latest": 1,
            "through": 1,
        }
        p2 = {
            "events": [{"sequence": 1, "actor": "b", "op": "claim", "at": 1.5, "id": "e1b", "data": {"task": "x"}}],
            "has_more": False,
            "latest": 1,
            "through": 1,
        }
        with self.assertRaises(ValueError) as ctx:
            build_digest([p1, p2])
        self.assertIn("conflicting duplicate", str(ctx.exception).lower())
        self.assertIn("1", str(ctx.exception))

    def test_exact_duplicate_overlap_allowed(self):
        ev = {"sequence": 2, "actor": "a", "op": "sleep", "at": 2.0, "id": "e2", "data": {"through": 1}}
        p1 = {
            "events": [{"sequence": 1, "actor": "a", "op": "wake", "at": 1.0, "id": "e1", "data": {}}, dict(ev)],
            "has_more": True,
            "latest": 3,
            "through": 2,
        }
        p2 = {
            "events": [dict(ev), {"sequence": 3, "actor": "b", "op": "wake", "at": 3.0, "id": "e3", "data": {}}],
            "has_more": False,
            "latest": 3,
            "through": 3,
        }
        result = build_digest([p1, p2])
        self.assertEqual(result["cursor"]["event_count"], 3)
        self.assertEqual(result["cursor"]["gaps"], [])
        self.assertFalse(result["cursor"]["has_more"])

    def test_incomplete_coverage_stays_incomplete_despite_false_flag(self):
        # Second page claims has_more=False but there is a gap: must stay True.
        p1 = {
            "events": [{"sequence": 1, "actor": "a", "op": "wake", "at": 1.0, "id": "e1", "data": {}}],
            "has_more": True,
            "latest": 5,
            "through": 1,
        }
        p2 = {
            "events": [{"sequence": 4, "actor": "a", "op": "wake", "at": 4.0, "id": "e4", "data": {}}],
            "has_more": False,
            "latest": 5,
            "through": 4,
        }
        result = build_digest([p1, p2])
        self.assertEqual(result["cursor"]["gaps"], [[1, 4]])
        self.assertTrue(result["cursor"]["has_more"])

    def test_malformed_event_sequence_rejected(self):
        bad = {
            "events": [{"sequence": "1", "actor": "a", "op": "wake", "at": 1.0, "id": "e1", "data": {}}],
            "has_more": False,
            "latest": 1,
            "through": 1,
        }
        with self.assertRaises(ValueError):
            build_digest([bad])

    def test_malformed_cursor_through_rejected(self):
        bad = {"events": [], "has_more": False, "latest": 100, "through": "100"}
        with self.assertRaises(ValueError):
            build_digest([bad])

    def test_malformed_has_more_rejected(self):
        bad = {"events": [], "has_more": "false", "latest": 100, "through": 100}
        with self.assertRaises(ValueError):
            build_digest([bad])


if __name__ == "__main__":
    unittest.main()
