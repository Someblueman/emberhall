"""Offline fixture tests for the handover rehearsal checker (stdlib only)."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("check.py")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import importlib.util

spec = importlib.util.spec_from_file_location("handover_check", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def make_event(seq, op, actor, at, data, id_):
    return {"sequence": seq, "id": id_, "op": op, "actor": actor, "at": at, "data": data}


def complete_events(now=1000):
    return [
        make_event(1, "found", "founder", 0, {"rules": "r", "house_id": "h"}, "f1"),
        make_event(2, "arrive", "alice", 10, {"name": "Alice"}, "a1"),
        make_event(3, "task", "alice", 20, {"task": "work", "title": "Work", "description": "d"}, "t1"),
        make_event(4, "claim", "alice", 30, {"task": "work", "expect": 0, "token": "tok", "seconds": 3600}, "c1"),
        make_event(5, "say", "alice", 40, {"text": "working"}, "s1"),
        make_event(6, "finish", "alice", 50, {"task": "work", "token": "tok", "result": "done", "artifacts": {"evidence/out.md": {"sha256": "x", "base64": "eA=="}}}, "f2"),
        make_event(7, "say", "alice", 60, {"text": "see evidence/out.md and [Evidence](evidence/out.md)"}, "s2"),
        make_event(8, "sleep", "alice", 70, {"through": 7, "note": "Finished work seq 4 to 7, artifact evidence/out.md present. Link [Evidence](evidence/out.md) resolves. Head 7."}, "sl1"),
    ]


def live_claim_events():
    evs = complete_events()
    # Replace finish with a live claim still leased at head.
    evs[5] = make_event(6, "claim", "alice", 50, {"task": "work", "expect": 1, "token": "tok2", "seconds": 3600}, "c2")
    evs[7] = make_event(8, "sleep", "alice", 70, {"through": 7, "note": "Sleeping with live claim on work."}, "sl1")
    return evs


def expired_claim_events():
    evs = complete_events()
    evs[5] = make_event(6, "claim", "alice", 50, {"task": "work", "expect": 1, "token": "tok2", "seconds": 5}, "c2")
    # Head is at 70; lease until 55 <= 70 => expired, not live.
    evs[7] = make_event(8, "sleep", "alice", 70, {"through": 7, "note": "Sleeping with expired claim on work."}, "sl1")
    return evs


class HandoverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        (self.root / "evidence").mkdir()
        (self.root / "evidence" / "out.md").write_text("out", encoding="utf-8")

    def run_check(self, events, through, root=None):
        p = self.root / "journal.json"
        p.write_text(json.dumps(events), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check", str(p), "--through", str(through),
             "--root", str(root or self.root), "--json"],
            capture_output=True, text=True, timeout=20,
        )
        return result

    def test_complete_handoff_passes(self):
        r = self.run_check(complete_events(), 7)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertTrue(data["ok"])
        self.assertTrue(data["checks"]["sequences"]["ok"])
        self.assertTrue(data["checks"]["artifacts"]["ok"])
        self.assertTrue(data["checks"]["claims"]["ok"])
        self.assertTrue(data["checks"]["links"]["ok"])

    def test_missing_artifact_fails_closed(self):
        # Remove the artifact file; finish still names it.
        (self.root / "evidence" / "out.md").unlink()
        r = self.run_check(complete_events(), 7)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertFalse(data["ok"])
        self.assertFalse(data["checks"]["artifacts"]["ok"])
        self.assertTrue(any("missing" in e for e in data["checks"]["artifacts"]["errors"]))

    def test_live_claim_fails_but_expired_does_not(self):
        r_live = self.run_check(live_claim_events(), 7)
        self.assertEqual(r_live.returncode, 1, r_live.stderr + r_live.stdout)
        data = json.loads(r_live.stdout)
        self.assertFalse(data["checks"]["claims"]["ok"])
        self.assertTrue(any("live claim" in e for e in data["checks"]["claims"]["errors"]))

        r_exp = self.run_check(expired_claim_events(), 7)
        self.assertEqual(r_exp.returncode, 0, r_exp.stderr + r_exp.stdout)
        data2 = json.loads(r_exp.stdout)
        self.assertTrue(data2["checks"]["claims"]["ok"])
        self.assertTrue(any("expired" in w for w in data2["checks"]["claims"]["warnings"]))

    def test_sequence_beyond_head_fails(self):
        evs = complete_events()
        # Note names a future sequence while through stays at head.
        evs[7] = make_event(8, "sleep", "alice", 70, {"through": 7, "note": "Claimed seq 99 tomorrow."}, "sl1")
        r = self.run_check(evs, 7)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertFalse(data["checks"]["sequences"]["ok"])

    def test_through_beyond_head_is_invalid_input(self):
        r = self.run_check(complete_events(), 999)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("exceeds", r.stderr)

    def test_cli_text_output_is_stable(self):
        p = self.root / "journal.json"
        p.write_text(json.dumps(complete_events()), encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--check", str(p), "--through", "7", "--root", str(self.root)],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Handover rehearsal", r.stdout)
        self.assertIn("Result: PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
