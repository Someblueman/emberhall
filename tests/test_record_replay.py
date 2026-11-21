"""A Record replays only what is new, and never hands out the replay it keeps (21 November)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from house import record as record_module
from house.record import REF, Record
from tests.support import HouseCase


class IncrementalReplayTests(HouseCase):
    def fresh(self):
        return Record(self.repo).read()

    def test_a_second_read_applies_only_the_new_events_and_matches_a_full_replay(self):
        self.record.read()
        self.record.append("arrive", "carol", {"name": "Carol"})
        applied = []
        real = record_module.apply_event
        with patch("house.record.apply_event", lambda state, event: applied.append(event) or real(state, event)):
            state, events, head = self.record.read()
        self.assertEqual(1, len(applied), "only Carol's arrival was replayed")
        self.assertEqual(self.fresh(), (state, events, head))

    def test_what_a_caller_changes_never_reaches_the_next_read(self):
        state, events, _ = self.record.read()
        state["residents"].clear()
        events[0]["data"]["name"] = "changed"
        again = self.record.read()
        self.assertEqual(self.fresh(), again)
        self.assertIn("alice", again[0]["residents"])

    def test_history_that_does_not_extend_the_kept_replay_is_replayed_from_the_foundation(self):
        before = self.record.read()
        self.record.append("arrive", "carol", {"name": "Carol"})
        self.record.read()
        self.record.git("update-ref", REF, before[2])
        self.assertEqual(before, self.record.read())
        self.assertNotIn("carol", self.record.read()[0]["residents"])

    def test_a_failed_replay_keeps_nothing(self):
        self.record.read()
        self.record.append("arrive", "carol", {"name": "Carol"})
        with patch("house.record.apply_event", side_effect=ValueError("broken")):
            with self.assertRaises(ValueError):
                self.record.read()
        self.assertIsNone(self.record._replay)
        self.assertEqual(self.fresh(), self.record.read())


if __name__ == "__main__":
    unittest.main()
