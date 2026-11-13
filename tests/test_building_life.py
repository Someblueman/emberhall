"""Full model dispatch after an explicit synthetic room-growth migration."""
import base64
import copy
import hashlib
import json
import unittest

from house import building, council
from tests import test_council as fixtures


class BuildingLifeTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.CouncilTests()
        self.h.setUp()
        self.h.authorize()

    def enable(self):
        self.h.state["maintenance"] = {"room_growth": True, "at": self.h.now}
        building.initialize(self.h.state)

    def work(self, task="build", actor="alice"):
        self.h.event("task", {"task": task, "title": task, "description": "A useful purpose"}, actor)
        self.h.event("claim", {"task": task, "expect": 0, "token": task + "-token", "seconds": 60}, actor)

    def complete(self, task="build", actor="alice"):
        body = b"Observed construction and verification"
        self.h.event("finish", {"task": task, "token": task + "-token", "result": "Useful work completed",
            "artifacts": {"room-proof.txt": {"sha256": hashlib.sha256(body).hexdigest(),
                                              "base64": base64.b64encode(body).decode()}}}, actor)

    def plan(self, **changes):
        return {"kind": "room-plan", "room": "repair", "name": "Repair workshop", "purpose": "Restore archives",
                "reason": "Blackout needs recovery space", "floor": 0, "task": "build", "expect": 0} | changes

    def upper_floor(self):
        h = self.h
        descriptor = {"level": 1, "name": "Practice floor", "purpose": "Recovery practice and independent checks"}
        h.event("council-propose", {"proposal": "floor-one", "mode": "floor", "title": "Practice floor",
                "text": json.dumps(descriptor), "reason": "Sustained work", "base": h.state["rule_revision"]})
        h.trial("floor-one"); h.endorse("floor-one", "bob"); h.endorse("floor-one", "carol")
        h.notice("floor-one"); h.now += council.WAIT_SECONDS; h.sync(); h.enact("floor-one")

    def test_pre_migration_room_replay_stays_plain_and_no_past_usage_is_fabricated(self):
        h = self.h
        h.event("life", {"kind": "room", "room": "old-study", "name": "Old study"})
        h.event("life", {"kind": "activity", "room": "old-study"})
        old = copy.deepcopy(h.state)
        self.assertEqual(set(old["life"]["rooms"]["old-study"]), {"name", "sequence"})
        self.assertNotIn("floors", old["life"])
        h.reject("life", self.plan(), "not authorized")
        self.enable()
        migrated = h.state["life"]["rooms"]["old-study"]
        self.assertIsNone(migrated["last_used_at"])
        self.assertIsNone(migrated["opened_at"])
        self.assertEqual(migrated["observed_since"], h.now)
        h.reject("life", {"kind": "room", "room": "shortcut", "name": "Bypass"}, "room-plan")
        h.now += 5
        h.event("life", {"kind": "activity", "room": "old-study"})
        room = h.state["life"]["rooms"]["old-study"]
        self.assertEqual((room["last_used_at"], room["last_used_sequence"]), (h.now, h.state["sequence"]))
        self.assertEqual(set(old["life"]["rooms"]["old-study"]), {"name", "sequence"})

    def test_accepted_presence_updates_use_and_rejected_construction_activity_cannot(self):
        h = self.h
        self.enable(); self.work(); h.event("life", self.plan())
        h.reject("life", {"kind": "activity", "room": "repair"}, "construction task")
        self.work("other", "bob")
        h.reject("life", {"kind": "activity", "room": "repair", "task": "other"}, "construction task", "bob")
        h.reject("life", {"kind": "activity", "room": "repair", "task": "build"}, "own live task", "bob")
        self.assertIsNone(h.state["life"]["rooms"]["repair"]["last_used_at"])
        self.assertNotIn("bob", h.state["life"]["presence"])
        h.event("life", {"kind": "activity", "room": "repair", "task": "build"})
        room = h.state["life"]["rooms"]["repair"]
        self.assertEqual(room["last_used_sequence"], h.state["life"]["presence"]["alice"]["sequence"])
        h.reject("life", {"kind": "activity", "room": "repair", "task": "build", "at": h.now - 100}, "fields")
        self.complete()
        h.reject("life", {"kind": "activity", "room": "repair", "task": "build"}, "own live task")
        h.event("life", {"kind": "room-open", "room": "repair", "expect": 1, "evidence": "Accepted room-proof.txt"})
        h.event("life", {"kind": "activity", "room": "repair"}, "bob")
        h.event("life", {"kind": "room-close", "room": "repair", "expect": 2, "reason": "Pause this practice"})
        h.reject("life", {"kind": "activity", "room": "repair"}, "unavailable", "bob")
        self.assertTrue(h.state["residents"]["bob"]["awake"])
        self.assertEqual(h.state["life"]["presence"]["bob"]["room"], "repair")

    def test_floor_enactment_room_opening_repeal_and_blocked_new_use_approval(self):
        h = self.h
        self.enable(); self.upper_floor(); self.work()
        before = copy.deepcopy(h.state)
        h.event("life", self.plan(floor=1)); self.complete()
        h.event("life", {"kind": "room-open", "room": "repair", "expect": 1, "evidence": "Useful recovery artifacts"})
        h.event("life", {"kind": "activity", "room": "repair"}, "bob")
        h.sync([h.comment("REPEAL floor-one")])
        self.assertEqual(h.state["life"]["rooms"]["repair"]["status"], "open")
        self.assertEqual(h.state["life"]["floors"]["1"]["proposal"], "floor-one")
        self.work("new-build")
        h.reject("life", self.plan(room="other-room", floor=1, task="new-build"), "no longer active")
        h.reject("life", {"kind": "room-repurpose", "room": "repair", "name": "New purpose", "purpose": "New work",
                          "reason": "Changed practice", "task": "new-build", "expect": 2}, "no longer active")
        self.assertNotIn("repair", before["life"]["rooms"])
        self.assertEqual(h.state["life"]["rooms"]["repair"]["history"][-1]["kind"], "room-open")

    def test_two_room_changes_cannot_silently_overwrite_the_same_generation(self):
        h = self.h
        self.enable(); self.work(); h.event("life", self.plan())
        self.work("second", "bob")
        h.reject("life", self.plan(task="second"), "generation changed", "bob")
        h.event("life", {"kind": "room-close", "room": "repair", "expect": 1, "reason": "Explicit cancellation"})
        repurpose = {"kind": "room-repurpose", "room": "repair", "name": "Independent lab", "purpose": "Separate checks",
                     "reason": "Reclaimed closed space", "task": "second", "expect": 1}
        h.reject("life", repurpose, "generation changed", "bob")
        h.event("life", repurpose | {"expect": 2}, "bob")
        self.complete("second", "bob")
        h.event("life", {"kind": "room-open", "room": "repair", "expect": 3, "evidence": "Independent artifacts"}, "bob")
        room = h.state["life"]["rooms"]["repair"]
        self.assertEqual(room["builder"], "bob")
        self.assertIsNone(room["closed_at"])
        self.assertIn("room-close", [event["kind"] for event in room["history"]])
        h.event("sleep", {"through": h.state["sequence"], "note": "Synthetic sleep"}, "bob")
        h.reject("life", {"kind": "room-close", "room": "repair", "expect": 4, "reason": "Asleep change"},
                 "awake resident", "bob")
