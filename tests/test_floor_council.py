"""Synthetic clocks exercise real council gates; these are not lived approvals."""
import copy
import json
from pathlib import Path
import unittest

from house import body, building, council, mailbox, resident_actions
from tests import test_council as fixtures


class FloorCouncilTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.CouncilTests()
        self.h.setUp()
        self.h.authorize()
        self.h.state["maintenance"] = {"room_growth": True, "at": self.h.now}
        building.initialize(self.h.state)

    def proposal(self, name="floor-one", level=1, **changes):
        return {"proposal": name, "mode": "floor", "title": "Archive level",
                "text": json.dumps({"level": level, "name": "Archive level", "purpose": "Shared recovery practice"}),
                "reason": "A sustained project needs space", "base": self.h.state["rule_revision"]} | changes

    def ready(self, name="floor-one", level=1):
        h = self.h
        h.event("council-propose", self.proposal(name, level))
        h.trial(name)
        h.endorse(name, "bob")
        h.endorse(name, "carol")
        h.notice(name)

    def enact(self, name="floor-one"):
        self.h.now += council.WAIT_SECONDS
        self.h.sync()
        self.h.enact(name)

    def test_floor_keeps_trial_independence_notice_full_window_and_fresh_sync(self):
        h = self.h
        h.event("council-propose", self.proposal())
        before = copy.deepcopy(h.state)
        h.reject("council-enact", {"proposal": "floor-one"}, "trial")
        h.trial("floor-one")
        h.reject("council-endorse", {"proposal": "floor-one", "evidence": "Self"}, "author")
        h.endorse("floor-one", "bob")
        h.reject("council-enact", {"proposal": "floor-one"}, "two independent")
        h.endorse("floor-one", "carol")
        h.reject("council-enact", {"proposal": "floor-one"}, "notice")
        h.notice("floor-one")
        h.reject("council-enact", {"proposal": "floor-one"}, "24-hour")
        h.sync()
        h.now += council.WAIT_SECONDS
        h.reject("council-enact", {"proposal": "floor-one"}, "fresh")
        h.sync(); h.enact("floor-one")
        rule = h.state["council"]["rules"]["floor-one"]
        floor = h.state["life"]["floors"]["1"]
        self.assertEqual(rule["mode"], "floor")
        self.assertEqual(rule["floor"], json.loads(rule["text"]))
        self.assertEqual((floor["proposal"], floor["enacted_at"]), ("floor-one", h.now))
        self.assertEqual(set(before["life"]["floors"]), {"0"})
        self.assertNotEqual(before["rule_revision"], h.state["rule_revision"])

    def test_mode_requires_migration_and_exact_unambiguous_descriptor(self):
        self.h.state["maintenance"]["room_growth"] = False
        self.h.reject("council-propose", self.proposal(), "not authorized")
        self.h.state["maintenance"]["room_growth"] = True
        for raw in ("not JSON", "[]", '{"level":1,"level":2,"name":"X","purpose":"Y"}',
                    '{"level":true,"name":"X","purpose":"Y"}',
                    '{"level":0,"name":"X","purpose":"Y"}',
                    '{"level":1.0,"name":"X","purpose":"Y"}',
                    '{"level":1,"name":"X","purpose":" "}',
                    '{"level":1,"name":"X","purpose":"Y","veto_window_seconds":0}'):
            self.h.reject("council-propose", self.proposal(text=raw), ".")
        self.assertNotIn("floor-one", self.h.state["proposals"])

    def test_competing_floor_cannot_use_stale_base_or_skip_a_level(self):
        h = self.h
        self.ready("first")
        self.ready("competing")
        self.enact("first")
        h.reject("council-enact", {"proposal": "competing"}, "stale rule revision")
        self.assertEqual(set(h.state["life"]["floors"]), {"0", "1"})
        self.ready("skip-level", 3)
        h.now += council.WAIT_SECONDS; h.sync()
        h.reject("council-enact", {"proposal": "skip-level"}, "contiguous")
        self.assertEqual(h.state["proposals"]["skip-level"]["status"], "pending")
        self.assertNotIn("skip-level", h.state["council"]["rules"])
        self.assertNotIn("3", h.state["life"]["floors"])

    def test_veto_and_repeal_leave_no_backdoor_or_erased_physical_floor(self):
        h = self.h
        self.ready("vetoed")
        h.sync([h.comment("VETO vetoed")])
        h.now += council.WAIT_SECONDS; h.sync()
        h.reject("council-enact", {"proposal": "vetoed"}, "not pending")
        self.assertEqual(set(h.state["life"]["floors"]), {"0"})
        self.ready("built")
        self.enact("built")
        floor = copy.deepcopy(h.state["life"]["floors"]["1"])
        h.sync([h.comment("REPEAL built", comment_id=9002)])
        self.assertEqual(h.state["council"]["rules"]["built"]["status"], "repealed")
        self.assertEqual(h.state["life"]["floors"]["1"], floor)
        public = next(f for f in body.floor_views(h.state) if f["level"] == 1)
        self.assertEqual(public["authorization"], "repealed")
        self.assertEqual(public["enacted_at"], floor["enacted_at"])
        with self.assertRaisesRegex(ValueError, "no longer active"):
            building.approved_floor(h.state, 1)

    def test_native_capability_accepts_room_operations_but_no_floor_authority_operation(self):
        args = resident_actions.parse(["council", "--as", "alice", "propose", "floor-one", "--title", "Floor",
            "--file", "floor.json", "--reason", "Real need", "--mode", "floor"], "alice")
        self.assertEqual(args.mode, "floor")
        for kind in sorted(building.KINDS):
            args = mailbox.parse(["life", "--as", "alice", "--data", json.dumps({"kind": kind})],
                                 Path("/canonical"), Path("/own-room"), "alice")
            self.assertEqual(json.loads(args.data)["kind"], kind)
        for kind in ("floor", "floor-enact", "room-growth-authorize", "run-start"):
            with self.assertRaisesRegex(ValueError, "not a resident life command"):
                mailbox.parse(["life", "--as", "alice", "--data", json.dumps({"kind": kind})],
                              Path("/canonical"), Path("/own-room"), "alice")
