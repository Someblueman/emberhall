"""Research keeps pace with an empty slot, and a corrected brief is not a death sentence.

Steward, 17 November afternoon: "are we doing enough research now? We have 1 great work in progress
and no small ones and the shelf only holds 2." With three ideas shelved a round could start only
every four hours, and a kept idea three hours from its vote had expired the moment a resident
corrected its brief.
"""
import pathlib
import unittest

from house import shelf
from house.home import asked_prompt
from tests import test_higher_bar
from tests import test_lone_candidate
from tests.test_who_asked import HOUR


class ResearchFlowTests(unittest.TestCase):
    setUp, lone, kept = (getattr(test_lone_candidate.LoneCandidateTests, name) for name in ("setUp", "lone", "kept"))
    start, keep, ideas = (getattr(test_higher_bar.HigherBarTests, name) for name in ("start", "keep", "ideas"))

    def flow(self):
        self.lone()
        self.f.state["maintenance"]["migrations"][shelf.FLOW] = {"at": self.f.state["at"]}

    def three(self):
        """A great project under way, three shelved small ideas, one kept; the last round just started."""
        f = self.f
        first = self.kept("a")
        f.state["shelf"]["ideas"]["x"] = dict(self.ideas()["a"], status="project", scale="great")
        f.state["shelf"]["projects"]["g"] = {"idea": "x", "owner": "v1", "status": "active", "slot": "great",
                                             "deadline": f.state["at"] + 1000 * HOUR, "extended": False}
        self.start(actor="other", round_id="r2")
        f.send("explore-publish", actor="other", round="r2", token="r2",
               ideas=[test_higher_bar.idea("b"), test_higher_bar.idea("c")])
        return first

    def test_before_the_change_a_round_waits_four_hours(self):
        f = self.f
        self.three()
        self.lone()
        self.assertEqual([], shelf.thin(f.state, f.state["shelf"]))
        self.assertFalse(shelf.research_open(f.state, f.state["shelf"], f.state["at"] + HOUR, 3))
        f.reject("started recently", "explore-start", actor="v1", round="r3", token="r3", seconds=100,
                 expect=f.state["shelf"]["generation"])

    def test_rounds_follow_one_another_while_a_free_slot_lacks_two_kept_ideas(self):
        f = self.f
        self.three()
        self.flow()
        self.assertEqual(["small"], shelf.thin(f.state, f.state["shelf"]))
        self.assertTrue(shelf.research_open(f.state, f.state["shelf"], f.state["at"], 3))
        self.start(actor="v1", round_id="r3")
        self.assertEqual("r3", f.state["shelf"]["explorer"])

    def test_a_filled_slot_or_two_kept_ideas_bring_the_gap_back(self):
        f = self.f
        self.three()
        self.flow()
        for key in ("b", "c"):
            for checker in ("author", "v1", "v3"):
                self.keep(checker, key)
        self.assertEqual([], shelf.thin(f.state, f.state["shelf"]), "three kept small ideas are a real choice")
        f.state["shelf"]["projects"]["g"]["status"] = "done"
        self.assertEqual(["great"], shelf.thin(f.state, f.state["shelf"]))
        f.state["shelf"]["projects"]["g"]["status"] = "active"
        self.assertFalse(shelf.research_open(f.state, f.state["shelf"], f.state["at"] + HOUR, 3))
        self.assertTrue(shelf.research_open(f.state, f.state["shelf"], f.state["at"] + 4 * HOUR, 3))

    def test_before_the_change_correcting_a_kept_brief_after_six_hours_ends_the_idea(self):
        f = self.f
        first = self.kept("a")
        self.lone()
        f.send("idea-brief", actor="v2", at=first + 6 * HOUR + 60, idea="a", brief=test_higher_bar.high("field"))
        self.start(actor="v2", round_id="tick", at=first + 6 * HOUR + 120)
        self.assertEqual("graveyard", self.ideas()["a"]["status"])

    def test_a_corrected_brief_on_a_kept_idea_gets_six_fresh_hours_for_its_checks(self):
        f = self.f
        first = self.kept("a")
        self.flow()
        corrected = first + 6 * HOUR + 60
        f.send("idea-brief", actor="v2", at=corrected, idea="a", brief=test_higher_bar.high("field"))
        self.assertFalse(shelf.grounded(f.state, self.ideas()["a"]), "the checks start again")
        self.assertEqual(corrected + 6 * HOUR, shelf.brief_due(f.state, self.ideas()["a"]))
        self.start(actor="v2", round_id="tick", at=corrected + 5 * HOUR)
        self.assertEqual("shelved", self.ideas()["a"]["status"])
        for checker in ("author", "v3", "other"):
            self.keep(checker, "a")
        self.assertTrue(shelf.grounded(f.state, self.ideas()["a"]))
        self.assertIsNone(shelf.brief_due(f.state, self.ideas()["a"]))

    def test_a_new_brief_does_not_keep_an_unchecked_idea_alive(self):
        f = self.f
        self.flow()
        self.start()
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[test_higher_bar.idea("a")])
        shelved = self.ideas()["a"]["shelved_at"]
        f.send("idea-brief", actor="v2", at=shelved + 5 * HOUR, idea="a", brief=test_higher_bar.high("field"))
        self.assertEqual(shelved + 6 * HOUR, shelf.brief_due(f.state, self.ideas()["a"]))

    def test_residents_and_the_handbook_are_told(self):
        f = self.f
        self.kept("a")
        self.lone()
        self.assertNotIn("CORRECTING A KEPT IDEA'S BRIEF", asked_prompt(f.state, "v2"))
        self.flow()
        self.assertIn("CORRECTING A KEPT IDEA'S BRIEF clears its three checks", asked_prompt(f.state, "v2"))
        root = pathlib.Path(shelf.__file__).parents[1]
        self.assertTrue("upgrade-20261117-research-flow" in (root / "docs/SHELF.md").read_text())
        self.assertTrue("Research keeps pace with an empty slot" in (root / "docs/STEWARD_ORDERS.md").read_text())
        source = (root / "house/home.py").read_text()
        self.assertIn("rounds follow one another without the four-hour gap", source)
