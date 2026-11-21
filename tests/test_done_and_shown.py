"""Done and shown (Steward, 21 November): finished work is closed by its owner and reaches the Gallery."""
from __future__ import annotations

import unittest

from house import course, home


def house_state(*, shown: bool) -> dict:
    sol = "gpt-6.1-sol"
    people = {"tern": 10, "fern": 5, "rook": 20}
    migrations = {course.TURNS: {"at": 0.0}} | ({home.SHOWN: {"at": 0.0}} if shown else {})
    return {
        "at": 100.0, "sequence": 100,
        "maintenance": {"resident_returns": True, "migrations": migrations},
        "residents": {name: {"awake": False} for name in people},
        "life": {"budgets": {}, "runs": {name: {
            "resident": name, "agent": "codex", "model": sol, "status": "completed",
            "started_sequence": ended - 1, "ended_sequence": ended} for name, ended in people.items()}},
        "tasks": {
            "t1": {"project": "house-day", "status": "done", "artifacts": ["projects/a-day/index.html"]},
            "t2": {"project": "house-day", "status": "done", "artifacts": ["projects/a-day/player.js"]},
            "t3": {"project": "great-x", "status": "claimed", "owner": "rook", "until": 0.0,
                   "artifacts": []},
            "t4": {"project": "fair", "status": "done", "artifacts": ["projects/fair-round-swaps/README.md"]},
            "t5": {"project": "shown", "status": "done", "artifacts": ["projects/stamps/README.md"]},
            "t6": {"project": "door", "status": "done", "artifacts": ["house/view.py"]},
        },
        "shelf": {
            "ideas": {key: {"title": title} for key, title in {
                "a-day": "A Day in This House", "x": "Great X", "fair-swaps": "Fair Swaps",
                "stamps": "Three Runs of Stamps", "door": "The Ten-Second Door"}.items()},
            "projects": {
                "house-day": {"idea": "a-day", "owner": "tern", "status": "active"},
                "great-x": {"idea": "x", "owner": "rook", "status": "active"},
                "fair": {"idea": "fair-swaps", "owner": "fern", "status": "done", "closed_at": 90.0},
                "shown": {"idea": "stamps", "owner": "fern", "status": "done", "closed_at": 90.0},
                "door": {"idea": "door", "owner": "fern", "status": "done", "closed_at": 90.0},
            },
        },
    }


CATALOG = {"version": 1, "projects": [
    {"id": "three-runs-of-stamps", "href": "projects/stamps/index.html", "files": ["projects/stamps/README.md"]}]}


class DoneAndShownTests(unittest.TestCase):
    def test_nothing_changes_before_the_migration(self):
        state = house_state(shown=False)
        self.assertEqual({}, home.closing_projects(state))
        self.assertIsNone(home.closing_owner(state, "codex", 100.0))
        self.assertEqual("", home.closing_line(state, "tern"))
        self.assertEqual([], home.gallery_gaps(state, CATALOG))
        self.assertEqual("fern", course.next_resident(state, "codex", 100.0))

    def test_the_owner_of_a_project_with_nothing_left_open_is_woken_first(self):
        state = house_state(shown=True)
        self.assertEqual(["house-day"], list(home.closing_projects(state)), "an open task keeps a project going")
        self.assertEqual("fern", course.next_resident(state, "codex", 100.0), "fern has slept longest")
        self.assertEqual("tern", home.closing_owner(state, "codex", 100.0), "but the house is waiting for tern")
        self.assertIsNone(home.closing_owner(state, "muse", 100.0), "another family's start is not theirs")
        self.assertIsNone(home.closing_owner(state, "codex", 100.0, lambda who: who != "tern"),
                          "an author is never woken to review their own work")
        state["residents"]["tern"]["awake"] = True
        self.assertIsNone(home.closing_owner(state, "codex", 100.0), "an owner already awake is not woken twice")

    def test_the_owner_is_told_to_close_it_or_set_the_next_task(self):
        state = house_state(shown=True)
        line = home.closing_line(state, "tern")
        self.assertIn("YOUR PROJECT house-day (A Day in This House) HAS NO OPEN TASK", line)
        self.assertIn("site/projects.json", line)
        self.assertIn("project-done", line)
        self.assertIn("--project house-day and --ready", line)
        self.assertEqual("", home.closing_line(state, "fern"))

    def test_finished_work_missing_from_the_gallery_is_named_to_the_house_improver(self):
        state = house_state(shown=True)
        gaps = home.gallery_gaps(state, CATALOG)
        self.assertEqual(["Fair Swaps (projects/fair-round-swaps/)"], gaps,
                         "shown work and house changes without files under projects/ are not named")
        state["shelf"]["projects"]["fair"]["closed_at"] = 100.0 - 8 * 86400
        self.assertEqual([], home.gallery_gaps(state, CATALOG), "only the last week")
        state["shelf"]["projects"]["fair"]["closed_at"] = 90.0
        text = home.focus_prompt(state, "improve", CATALOG)
        self.assertIn("FINISHED BUT NOT IN THE GALLERY", text)
        self.assertIn("Fair Swaps", text)
        self.assertTrue(text.endswith(".\n"))
        self.assertNotIn("FINISHED BUT NOT IN THE GALLERY", home.focus_prompt(state, "room", CATALOG))


if __name__ == "__main__":
    unittest.main()


class GallerySeenTests(unittest.TestCase):
    def coordinator(self, private, running=()):
        import types
        from pathlib import Path
        holder = types.SimpleNamespace(private=Path(private), running=dict.fromkeys(running),
                                       catalog=lambda: CATALOG)
        holder.gallery_offer = lambda state, run: home.Coordinator.gallery_offer(holder, state, run)
        return holder

    def test_one_ordinary_session_at_a_time_is_handed_a_missing_gallery_entry(self):
        import tempfile
        state = house_state(shown=True)
        with tempfile.TemporaryDirectory() as private:
            house = self.coordinator(private)
            self.assertEqual("", house.gallery_offer(state, "r1"), "nothing before the migration")
            state["maintenance"]["migrations"][home.SEEN] = {"at": 0.0}
            first = house.gallery_offer(state, "r1")
            self.assertIn("Fair Swaps (projects/fair-round-swaps/) is finished but has no Gallery entry", first)
            self.assertIn("site/projects.json", first)
            house.running["r1"] = None
            self.assertEqual("", house.gallery_offer(state, "r2"), "only one session holds it at a time")
            del house.running["r1"]
            self.assertIn("Fair Swaps", house.gallery_offer(state, "r3"), "once it ends, the next one gets it")
            state["shelf"]["projects"]["fair"]["status"] = "active"
            self.assertEqual("", self.coordinator(private).gallery_offer(state, "r4"), "nothing missing, nothing said")
