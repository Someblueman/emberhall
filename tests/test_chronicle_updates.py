"""Tests for Chronicle updates: course-correction rule, opened rooms, stopped projects, and theme."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from house import chronicle_page, publish

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/emberhall-chronicle-room"


def _rich_events():
    return [
        {
            "sequence": 1,
            "at": 1794600001.0,
            "op": "life",
            "id": "e1",
            "actor": "resident-builder",
            "data": {
                "kind": "room-plan",
                "room": "salvage",
                "name": "The Salvage Room",
                "purpose": "PRIVATE_ROOM_PURPOSE",
                "reason": "PRIVATE_ROOM_REASON",
                "floor": 0,
                "task": "t1",
                "expect": 0,
            },
        },
        {
            "sequence": 2,
            "at": 1794600002.0,
            "op": "life",
            "id": "e2",
            "actor": "resident-other",
            "data": {
                "kind": "room-open",
                "room": "salvage",
                "expect": 1,
                "evidence": "PRIVATE_WRONG_BUILDER_OPEN",
            },
        },
        {
            "sequence": 3,
            "at": 1794600003.0,
            "op": "life",
            "id": "e3",
            "actor": "resident-builder",
            "data": {
                "kind": "room-open",
                "room": "salvage",
                "expect": 1,
                "evidence": "PRIVATE_OPEN_EVIDENCE_SECRET",
            },
        },
        {
            "sequence": 4,
            "at": 1794600004.0,
            "op": "life",
            "id": "e4",
            "actor": "resident-builder",
            "data": {
                "kind": "room-close",
                "room": "salvage",
                "expect": 2,
                "reason": "PRIVATE_CLOSE_REASON",
            },
        },
        {
            "sequence": 5,
            "at": 1794600005.0,
            "op": "life",
            "id": "e5",
            "actor": "resident-rebuilder",
            "data": {
                "kind": "room-repurpose",
                "room": "salvage",
                "name": "The Reopened Room",
                "purpose": "PRIVATE_REPURPOSE_PURPOSE",
                "reason": "PRIVATE_REPURPOSE_REASON",
                "task": "t2",
                "expect": 3,
            },
        },
        {
            "sequence": 6,
            "at": 1794600006.0,
            "op": "life",
            "id": "e6",
            "actor": "resident-rebuilder",
            "data": {
                "kind": "room-open",
                "room": "salvage",
                "expect": 4,
                "evidence": "PRIVATE_REOPEN_EVIDENCE",
            },
        },
        {
            "sequence": 7,
            "at": 1794600007.0,
            "op": "owner-migrate",
            "id": "e7",
            "actor": "keeper-01",
            "data": {"scope": "course-correction-20261115"},
        },
        {
            "sequence": 8,
            "at": 1794600008.0,
            "op": "owner-migrate",
            "id": "e8",
            "actor": "keeper-01",
            "data": {"scope": "unrelated-maintenance-20261115"},
        },
        {
            "sequence": 9,
            "at": 1794600009.0,
            "op": "shelf",
            "id": "e9",
            "actor": "resident-scout",
            "data": {
                "kind": "explore-publish",
                "round": "r1",
                "token": "tok",
                "ideas": [{"idea": "great-thing", "title": "Great Thing"}],
            },
        },
        {
            "sequence": 10,
            "at": 1794600010.0,
            "op": "shelf",
            "id": "e10",
            "actor": "resident-opener",
            "data": {
                "kind": "choice-open",
                "choice": "great-choice-01",
                "slot": "great",
                "milestones": {
                    "great-thing": {
                        "milestones": [
                            {"milestone": "PRIVATE_STAGE_1", "seconds": 86400},
                            {"milestone": "PRIVATE_STAGE_2", "seconds": 86400},
                        ]
                    }
                },
            },
        },
        {
            "sequence": 11,
            "at": 1794600011.0,
            "op": "shelf",
            "id": "e11",
            "actor": "resident-v1",
            "data": {"kind": "choice-vote", "choice": "great-choice-01", "idea": "great-thing", "reason": "PRIVATE_V1"},
        },
        {
            "sequence": 12,
            "at": 1794600012.0,
            "op": "shelf",
            "id": "e12",
            "actor": "resident-v2",
            "data": {"kind": "choice-vote", "choice": "great-choice-01", "idea": "great-thing", "reason": "PRIVATE_V2"},
        },
        {
            "sequence": 13,
            "at": 1794600013.0,
            "op": "shelf",
            "id": "e13",
            "actor": "resident-v3",
            "data": {"kind": "choice-vote", "choice": "great-choice-01", "idea": None, "reason": "PRIVATE_V3"},
        },
        {
            "sequence": 14,
            "at": 1794600014.0,
            "op": "shelf",
            "id": "e14",
            "actor": "resident-opener",
            "data": {"kind": "project-done", "project": "great-choice-01", "evidence": "PRIVATE_TASK_1"},
        },
        {
            "sequence": 15,
            "at": 1794600015.0,
            "op": "shelf",
            "id": "e15",
            "actor": "resident-opener",
            "data": {"kind": "project-drop", "project": "great-choice-01", "lesson": "PRIVATE_DROP_LESSON"},
        },
    ]


class ChronicleUpdateTests(unittest.TestCase):
    def test_course_correction_rooms_stopped_projects_and_great_slot(self):
        events = _rich_events()
        entries = chronicle_page.select_milestones(events)
        by_key = {}
        for item in entries:
            by_key.setdefault(item["category_key"], []).append(item)

        # 1. course-correction-20261115 enacts work-selection-004; unrelated migration ignored.
        rules = by_key.get("rule", [])
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["sequence"], 7)
        self.assertIn("one great work and one small project", rules[0]["title"])
        self.assertIn("work-selection-004", rules[0]["summary"])

        # 2. Only valid builder room-open transitions emit Opened Room milestones.
        rooms = by_key.get("room", [])
        self.assertEqual([r["sequence"] for r in rooms], [3, 6])
        self.assertEqual(rooms[0]["title"], "The Salvage Room")
        self.assertEqual(rooms[0]["summary"], "Room salvage opened on floor 0.")
        self.assertEqual(rooms[1]["title"], "The Reopened Room")
        self.assertEqual(rooms[1]["summary"], "Room salvage opened on floor 0.")

        # 3. Great-work choice notes its slot.
        choices = by_key.get("choice", [])
        self.assertEqual(len(choices), 1)
        self.assertIn("Great-work slot", choices[0]["summary"])

        # 4. Stage 1 passed, then project-drop emits Stopped Project (never Completed Project).
        self.assertEqual([s["sequence"] for s in by_key.get("stage", [])], [14])
        self.assertEqual(by_key.get("project", []), [])
        dropped = by_key.get("dropped", [])
        self.assertEqual(len(dropped), 1)
        self.assertEqual(dropped[0]["sequence"], 15)
        self.assertEqual(dropped[0]["title"], "Great Thing")
        self.assertIn("great-choice-01", dropped[0]["summary"])

        # 5. HTML renders controls, dark mode, footer links, and excludes all PRIVATE_ fields.
        page = chronicle_page.render_html(entries, through=15, house_id="test-house")
        self.assertNotIn("PRIVATE_", page)
        self.assertNotIn("<script", page)
        self.assertIn('id="chronicle-room" value="room"', page)
        self.assertIn("Opened rooms (2)", page)
        self.assertIn('id="chronicle-dropped" value="dropped"', page)
        self.assertIn("Stopped projects (1)", page)
        self.assertIn("prefers-color-scheme: dark", page)
        self.assertIn("color-scheme: light dark", page)
        self.assertIn("forced-colors: active", page)
        self.assertIn("var(--accent-wash)", page)
        self.assertNotIn("#f7e7db;", page.split("@media (prefers-color-scheme: dark)")[1])
        for target in ("#house-view", "#gallery-view", "#projects-view", "#council-view"):
            self.assertIn(target, page)

    def test_standalone_and_publisher_remain_synchronized(self):
        spec = importlib.util.spec_from_file_location("standalone_updates", PROJECT / "chronicle.py")
        standalone = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(standalone)
        events = _rich_events()
        expected = standalone.render_html(standalone.select_milestones(events), through=len(events), house_id="H")
        record = SimpleNamespace(read=lambda: ({"house_id": "H"}, events, "head"))
        self.assertEqual(publish.chronicle_body(record, {}).decode(), expected)


if __name__ == "__main__":
    unittest.main()
