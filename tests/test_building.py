"""Room projections with real task transitions and explicit synthetic migration."""
import base64
import copy
import hashlib
import unittest

from house import building
from house.model import apply_event


class BuildingTests(unittest.TestCase):
    def setUp(self):
        self.now = 1000
        self.counter = 0
        self.state = apply_event(None, {"id": "foundation", "op": "found", "actor": "founder",
            "at": self.now, "data": {"house_id": "room-test", "name": "Fixture", "rules": "Fixture", "owner_key": ""}})
        for actor in ("alice", "bob"):
            self.event("arrive", {"name": actor}, actor)
        self.event("life", {"kind": "room", "room": "old-study", "name": "Old study"})
        self.state["maintenance"] = {"room_growth": True, "at": self.now}
        building.initialize(self.state)

    def event(self, op, data, actor="alice"):
        self.counter += 1
        self.now += 1
        event = {"id": f"event-{self.counter}", "op": op, "actor": actor, "at": self.now, "data": data}
        next_state = copy.deepcopy(self.state)
        if op == "life" and data["kind"] in building.KINDS:
            building.apply(next_state, event)
            next_state["sequence"] += 1
            next_state["at"] = self.now
            next_state["receipts"][event["id"]] = next_state["sequence"]
        else:
            apply_event(next_state, event)
        self.state = next_state
        return event

    def reject(self, data, message, actor="alice"):
        before = copy.deepcopy(self.state)
        with self.assertRaisesRegex(ValueError, message):
            self.event("life", data, actor)
        self.assertEqual(self.state, before)

    def task(self, name="build", actor="alice", seconds=60):
        self.event("task", {"task": name, "title": name, "description": "Useful room construction"}, actor)
        self.event("claim", {"task": name, "expect": 0, "token": name + "-token", "seconds": seconds}, actor)

    def finish(self, name="build", actor="alice", token=None):
        body = b"A reproducible useful room artifact"
        self.event("finish", {"task": name, "token": token or name + "-token", "result": "Built and checked",
            "artifacts": {"proof.txt": {"sha256": hashlib.sha256(body).hexdigest(),
                                         "base64": base64.b64encode(body).decode()}}}, actor)

    def plan(self, **changes):
        return {"kind": "room-plan", "room": "recovery", "name": "Recovery room",
                "purpose": "Restore and verify useful archives", "reason": "Blackout needs repeatable recovery work",
                "floor": 0, "task": "build", "expect": 0} | changes

    def open_room(self):
        self.task(); self.event("life", self.plan()); self.finish()
        self.event("life", {"kind": "room-open", "room": "recovery", "expect": 1, "evidence": "Checked proof.txt"})

    def floor(self, level=1):
        descriptor = {"level": level, "name": "Archive level", "purpose": "Long-lived recovery projects"}
        proposal = "floor-" + str(level)
        self.state.setdefault("council", {"rules": {}})["rules"][proposal] = {
            "mode": "floor", "status": "active", "floor": descriptor}
        building.install_floor(self.state, descriptor, proposal, self.now, self.state["sequence"] + 1)
        return proposal, descriptor

    def test_migration_is_required_and_legacy_dates_are_not_invented(self):
        old = {"rooms": {"old": {"name": "Old", "sequence": 3}}, "presence": {}, "runs": {}}
        state = {"sequence": 5, "life": copy.deepcopy(old), "maintenance": {"room_growth": False, "at": 99}}
        before = copy.deepcopy(state)
        with self.assertRaisesRegex(ValueError, "not authorized"):
            building.initialize(state)
        self.assertEqual(state, before)
        state["maintenance"]["room_growth"] = True
        building.initialize(state)
        room = state["life"]["rooms"]["old"]
        for key in ("purpose", "builder", "planned_at", "opened_at", "last_used_at"):
            self.assertIsNone(room[key])
        self.assertEqual((room["observed_since"], room["generation"], room["history"]), (99, 0, []))
        self.assertEqual(room["sequence"], 3)
        initialized = copy.deepcopy(state)
        building.initialize(state)
        self.assertEqual(state, initialized)
        self.assertEqual(old["rooms"]["old"], {"name": "Old", "sequence": 3})

    def test_plan_requires_purpose_current_builder_task_and_approved_floor(self):
        self.reject(self.plan(), "live task")
        self.task()
        for missing in ("purpose", "reason", "task"):
            data = self.plan(); data.pop(missing)
            self.reject(data, "fields")
        self.reject(self.plan(purpose="  "), "blank")
        self.reject(self.plan(builder="bob"), "fields")
        self.reject(self.plan(), "live task", "bob")
        self.reject(self.plan(floor=1), "not been approved")
        self.reject(self.plan(floor=True), "invalid room floor")
        self.reject(self.plan(expect=True), "generation changed")
        self.event("life", self.plan())
        self.reject(self.plan(), "generation changed")

    def test_opening_needs_later_owned_artifacts_and_activity_is_observed_separately(self):
        self.task(); self.event("life", self.plan())
        old = copy.deepcopy(self.state)
        opening = {"kind": "room-open", "room": "recovery", "expect": 1, "evidence": "Verified fixture"}
        self.reject(opening, "completed construction task")
        with self.assertRaisesRegex(ValueError, "recorded builder"):
            building.activity(copy.deepcopy(self.state), "bob", "recovery", self.now, self.state["sequence"] + 1)
        self.finish()
        self.reject(opening, "recorded builder", "bob")
        self.event("life", opening)
        room = self.state["life"]["rooms"]["recovery"]
        self.assertEqual((room["status"], room["generation"]), ("open", 2))
        self.assertIsNone(room["last_used_at"])
        self.assertEqual(room["history"][-1]["artifacts"], {
            "proof.txt": self.state["tasks"]["build"]["artifacts"]["proof.txt"]["sha256"]})
        building.activity(self.state, "bob", "recovery", self.now, self.state["sequence"] + 1)
        self.assertEqual(room["last_used_by"], "bob")
        self.assertEqual(old["life"]["rooms"]["recovery"]["status"], "construction")
        self.assertIsNone(old["life"]["rooms"]["recovery"]["last_used_at"])

    def test_missing_or_predating_task_artifacts_cannot_open(self):
        self.task(); self.event("life", self.plan()); self.finish()
        opening = {"kind": "room-open", "room": "recovery", "expect": 1, "evidence": "Proof"}
        finished = self.state["tasks"]["build"]["finished_at"]
        self.state["tasks"]["build"]["finished_at"] = self.state["life"]["rooms"]["recovery"]["planned_sequence"]
        self.reject(opening, "later immutable")
        self.state["tasks"]["build"]["finished_at"] = finished
        self.state["tasks"]["build"]["artifacts"] = {}
        self.reject(opening, "later immutable")

    def test_expired_builder_is_replaced_only_after_same_task_reclaim(self):
        self.task(seconds=10); self.event("life", self.plan())
        self.task("unrelated", "bob")
        self.reject(self.plan(expect=1, task="unrelated"), "same construction task", "bob")
        self.now += 20
        self.event("claim", {"task": "build", "expect": 1, "token": "successor", "seconds": 60}, "bob")
        self.event("life", self.plan(expect=1, reason="Former builder lease expired; reclaimed task"), "bob")
        room = self.state["life"]["rooms"]["recovery"]
        self.assertEqual((room["builder"], room["task_generation"]), ("bob", 2))
        self.assertEqual(room["history"][-1]["previous"]["builder"], "alice")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.finish()
        self.finish(actor="bob", token="successor")
        self.event("life", {"kind": "room-open", "room": "recovery", "expect": 2, "evidence": "Successor's proof"}, "bob")

    def test_floor_requires_matching_enactment_contiguity_and_current_authority(self):
        descriptor = {"level": 1, "name": "Unapproved", "purpose": "Needs a council decision"}
        with self.assertRaisesRegex(ValueError, "matching enacted"):
            building.install_floor(self.state, descriptor, "fake", self.now, self.state["sequence"] + 1)
        proposal, descriptor = self.floor()
        with self.assertRaisesRegex(ValueError, "contiguous"):
            building.install_floor(self.state, descriptor, proposal, self.now, self.state["sequence"] + 1)
        with self.assertRaisesRegex(ValueError, "contiguous"):
            self.floor(3)
        self.task(); self.event("life", self.plan(floor=1)); self.finish()
        self.state["council"]["rules"][proposal]["status"] = "repealed"
        self.reject({"kind": "room-open", "room": "recovery", "expect": 1, "evidence": "Too late"}, "no longer active")
        self.event("life", {"kind": "room-close", "room": "recovery", "expect": 1, "reason": "Preserve stopped work"}, "bob")
        self.task("new-work", "bob")
        self.reject({"kind": "room-repurpose", "room": "recovery", "name": "New", "purpose": "New work",
                     "reason": "Try again", "task": "new-work", "expect": 2}, "no longer active", "bob")
        self.assertEqual(self.state["life"]["floors"]["1"]["proposal"], proposal)

    def test_vanished_finished_builder_can_be_closed_and_repurposed_with_new_work(self):
        self.task(); self.event("life", self.plan()); self.finish()
        self.event("life", {"kind": "room-close", "room": "recovery", "expect": 1, "reason": "Builder vanished after finishing"}, "bob")
        self.task("new-work", "bob")
        data = {"kind": "room-repurpose", "room": "recovery", "name": "Restoration room",
                "purpose": "Recovery practice", "reason": "Resume under a new task", "task": "new-work", "expect": 2}
        self.reject(data | {"expect": 1}, "generation changed", "bob")
        self.event("life", data, "bob"); self.finish("new-work", "bob")
        self.event("life", {"kind": "room-open", "room": "recovery", "expect": 3, "evidence": "New completed proof"}, "bob")
        room = self.state["life"]["rooms"]["recovery"]
        self.assertEqual([item["kind"] for item in room["history"]],
                         ["room-plan", "room-close", "room-repurpose", "room-open"])
        self.assertEqual(room["history"][0]["purpose"], "Restore and verify useful archives")

    def test_live_builder_and_confirmed_occupants_prevent_silent_closure(self):
        self.task(); self.event("life", self.plan())
        close = {"kind": "room-close", "room": "recovery", "expect": 1, "reason": "Close carefully"}
        self.reject(close, "another builder", "bob")
        self.finish(); self.event("life", {"kind": "room-open", "room": "recovery", "expect": 1, "evidence": "Proof"})
        self.task("using", "bob", seconds=10)
        self.state["life"]["presence"]["bob"] = {"room": "recovery", "task": "using", "at": self.now}
        self.reject(close | {"expect": 2}, "confirmed awake")
        self.now += 20
        presence = copy.deepcopy(self.state["life"]["presence"])
        self.event("life", close | {"expect": 2})
        self.assertTrue(self.state["residents"]["bob"]["awake"])
        self.assertEqual(self.state["life"]["presence"], presence)
        self.assertEqual(self.state["life"]["rooms"]["recovery"]["history"][-1]["unconfirmed_occupants"], ["bob"])
        with self.assertRaisesRegex(ValueError, "unavailable"):
            building.activity(self.state, "bob", "recovery", self.now, self.state["sequence"] + 1)

    def test_supervised_occupant_blocks_repurpose_but_unconfirmed_mark_does_not(self):
        self.open_room(); self.task("renovate")
        self.state["life"]["presence"]["bob"] = {"room": "recovery", "at": self.now}
        self.state["life"]["runs"]["fixture"] = {"resident": "bob", "status": "active"}
        repurpose = {"kind": "room-repurpose", "room": "recovery", "name": "Practice room",
                     "purpose": "Practice recovery", "reason": "New need", "task": "renovate", "expect": 2}
        self.reject(repurpose, "confirmed awake")
        self.state["life"]["runs"]["fixture"]["status"] = "completed"
        self.event("life", repurpose)
        self.assertEqual(self.state["life"]["rooms"]["recovery"]["history"][-1]["unconfirmed_occupants"], ["bob"])
