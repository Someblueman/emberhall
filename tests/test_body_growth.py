"""Real journal export of synthetic room growth; no clock is a live-life claim."""
import base64
import hashlib
import json
import unittest

from house import body, council, maintenance, wake_policy
from tests import test_runtime


class BodyGrowthTests(unittest.TestCase):
    def setUp(self):
        fixture = test_runtime.RuntimeTests(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.record = fixture.record
        state = self.record.read()[0]
        old = maintenance.protected_manifest(state)
        manifest = old | {name: "a" * 64 for name in maintenance.OWNER_MODULES | {"house/building.py"}}
        self.record.append("owner-migrate", "alice", {
            "scope": maintenance.GROWTH_SCOPE, "approval_sha256": maintenance.GROWTH_SHA256,
            "house": state["house_id"], "owner_id": council.OWNER_ID,
            "source_head": "a" * 40, "source_sha256": "b" * 64, "protected_files": manifest,
            "previous_manifest_sha256": maintenance.fingerprint(old),
            "previous_runtime_sha256": "c" * 64, "runtime_sha256": "d" * 64,
            "test_output_sha256": "e" * 64, "test_count": 1})

    def room(self, view, key):
        return next(r for r in view["rooms"] if r["id"] == key)

    def life(self, **data):
        return self.record.append("life", "alice", data)

    def test_normal_recorded_actions_count_as_use_without_rewriting_state(self):
        self.record.append("say", "alice", {"text": "Real conversation at the hearth"})
        state, _, head = self.record.read()
        self.assertIsNone(state["life"]["rooms"]["hearth"]["last_used_at"])
        exported = body.export(self.record)
        hearth = self.room(exported["frames"][-1], "hearth")
        self.assertEqual(hearth["last_used_at"], state["at"])
        self.assertEqual(hearth["last_used_by"], "alice")
        self.assertEqual(self.record.read()[0], state)
        self.assertEqual(self.record.read()[2], head)

    def test_history_retains_construction_opening_closure_without_future_leak(self):
        before = body.export(self.record)
        legacy = self.room(before["frames"][-1], "archive")
        self.assertIsNone(legacy["opened_at"])
        self.assertIsNone(legacy["last_used_at"])
        self.assertTrue(legacy["legacy"])
        self.assertEqual(before["frames"][-1]["floors"][0]["level"], 0)
        self.record.append("task", "alice", {"task": "build-room", "title": "Recover an archive", "description": "Useful work"})
        self.record.append("claim", "alice", {"task": "build-room", "expect": 0, "token": "build-token", "seconds": 60})
        self.life(kind="room-plan", room="recovery", name="Recovery <room>", purpose="Check backup recovery",
                  reason="A real project", floor=0, task="build-room", expect=0)
        construction = body.export(self.record)
        planned = self.room(construction["frames"][-1], "recovery")
        self.assertEqual(planned["status"], "construction")
        self.assertEqual(planned["builder"], "alice")
        self.assertIsNone(planned["opened_at"])
        self.life(kind="activity", room="recovery", task="build-room")
        secret = b"PRIVATE ARTIFACT BYTES"
        self.record.append("finish", "alice", {"task": "build-room", "token": "build-token", "result": "Checked",
            "artifacts": {"private-proof.txt": {"sha256": hashlib.sha256(secret).hexdigest(),
                              "base64": base64.b64encode(secret).decode()}}})
        self.life(kind="room-open", room="recovery", expect=1, evidence="Completed useful recovery work")
        opened = body.export(self.record)
        room = self.room(opened["frames"][-1], "recovery")
        self.assertEqual(room["status"], "open")
        self.assertGreaterEqual(room["opened_at"], room["planned_at"])
        self.assertIsNotNone(room["last_used_at"])
        self.life(kind="room-close", room="recovery", expect=2, reason="Practice moved to the workshop")
        closed = body.export(self.record)
        room = self.room(closed["frames"][-1], "recovery")
        self.assertEqual(room["status"], "closed")
        self.assertEqual([h["kind"] for h in room["history"]], ["room-plan", "room-open", "room-close"])
        self.assertEqual(closed["frames"][:len(before["frames"])], before["frames"])
        self.assertEqual(closed["frames"][:len(construction["frames"])], construction["frames"])
        self.assertEqual(closed["frames"][:len(opened["frames"])], opened["frames"])
        public = json.dumps(closed)
        self.assertNotIn(secret.decode(), public)
        self.assertNotIn(base64.b64encode(secret).decode(), public)
        self.assertNotIn("private-proof.txt", public)
        self.assertNotIn("dust", public)  # Client labels age inference; the record never invents it.
