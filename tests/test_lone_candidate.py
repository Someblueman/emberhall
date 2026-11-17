"""One kept idea alone gets a yes or no (Steward, 17 November morning).

Five hours after the higher bar three ideas had each been kept by three residents, both project
slots were empty and nothing could start. The Steward asked whether that was a bug. Two were only
waiting out their six hours; the third, the only kept idea of its scale, was waiting for a rival.
"""
import pathlib
import unittest

from house import body, shelf
from house.home import asked_prompt
from tests import test_shelf
from tests import test_higher_bar
from tests.test_who_asked import HOUR


def plans(*keys):
    return {key: {"milestone": "One usable example", "seconds": 100} for key in keys}


class LoneCandidateTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()
        self.f.state["maintenance"] = {"migrations": {scope: {"at": 1000} for scope in (
            shelf.OPEN_RESEARCH, shelf.WORTH_BUILDING, shelf.WHO_ASKED, shelf.SECOND_LOOK, shelf.SHARED,
            shelf.UNLISTED, shelf.HIGHER)}}

    start, keep, ideas = (getattr(test_higher_bar.HigherBarTests, name) for name in ("start", "keep", "ideas"))

    def lone(self):
        self.f.state["maintenance"]["migrations"][shelf.LONE] = {"at": self.f.state["at"]}

    def kept(self, key, actor="v1", round_id="r1", at=None, checkers=("author", "v3", "other")):
        self.start(actor=actor, round_id=round_id, at=at)
        self.f.send("explore-publish", actor=actor, round=round_id, token=round_id, ideas=[test_higher_bar.idea(key)])
        for checker in checkers:
            self.keep(checker, key)
        return self.ideas()[key]["shelved_at"]

    def test_before_the_change_one_kept_idea_waits_for_a_rival(self):
        f = self.f
        shelved = self.kept("a")
        f.reject("compares at least two ideas", "choice-open", actor="other", at=shelved + 6 * HOUR,
                 choice="c1", milestones=plans("a"))
        self.assertFalse(shelf.ready(f.state, "small", shelved + 6 * HOUR)["open"])
        self.assertNotIn("CHOICE CAN OPEN NOW", asked_prompt(f.state, "v2"))
        self.assertNotIn("vote_from", next(i for i in body.shelf_view(f.state)["ideas"] if i["id"] == "a"))

    def test_one_kept_idea_alone_gets_a_yes_or_no_after_six_hours(self):
        f = self.f
        shelved = self.kept("a")
        self.lone()
        f.reject("has waited its six hours", "choice-open", actor="other", choice="c1", milestones=plans("a"))
        prompt = asked_prompt(f.state, "v2")
        self.assertIn("KEPT AND WAITING FOR THE SMALL SLOT: a (", prompt)
        self.assertIn("The choice can open in 6 h 0 min; until then leave them be.", prompt)
        self.assertNotIn("GREAT SLOT:", prompt)
        self.assertEqual(shelved + 6 * HOUR,
                         next(i for i in body.shelf_view(f.state)["ideas"] if i["id"] == "a")["vote_from"])
        f.state["at"] = shelved + 6 * HOUR
        prompt = asked_prompt(f.state, "v2")
        self.assertIn("A SMALL CHOICE CAN OPEN NOW", prompt)
        self.assertIn("the choice is a plain yes or no", prompt)
        f.send("choice-open", actor="other", choice="c1", milestones=plans("a"))
        self.assertEqual(["a"], f.state["shelf"]["choices"]["c1"]["candidates"])
        self.assertNotIn("CHOICE CAN OPEN NOW", asked_prompt(f.state, "v2"), "nobody is asked to open a second")
        for voter in ("author", "v2", "v3"):
            f.send("choice-vote", actor=voter, choice="c1", idea="a", reason="A real attempt worth the days")
        self.assertEqual("active", f.state["shelf"]["projects"]["c1"]["status"])

    def test_none_of_these_sends_a_lone_idea_to_the_graveyard(self):
        f = self.f
        shelved = self.kept("a")
        self.lone()
        f.send("choice-open", actor="other", at=shelved + 6 * HOUR, choice="c1", milestones=plans("a"))
        f.state["shelf"]["choices"]["c1"]["selection_version"] = 3    # as the live house records it
        f.send("choice-vote", actor="author", choice="c1", idea="a", reason="Worth the days")
        for voter in ("v2", "v3"):
            f.send("choice-vote", actor=voter, choice="c1", idea=None, reason="Not worth weeks of work")
        self.assertEqual("rejected", f.state["shelf"]["choices"]["c1"]["status"])
        self.assertEqual("graveyard", self.ideas()["a"]["status"])
        self.assertNotIn("c1", f.state["shelf"]["projects"])

    def test_a_kept_rival_still_inside_its_six_hours_is_waited_for(self):
        f = self.f
        first = self.kept("a")
        self.lone()
        second = self.kept("b", actor="other", round_id="r2", at=first + 5 * HOUR, checkers=("author", "v3", "v1"))
        f.reject("still inside its six hours", "choice-open", actor="other", at=first + 6 * HOUR,
                 choice="c1", milestones=plans("a"))
        waiting = shelf.ready(f.state, "small", first + 6 * HOUR)
        self.assertEqual((["a"], {"b": second + 6 * HOUR}, False),
                         (waiting["now"], waiting["later"], waiting["open"]))
        f.state["at"] = first + 6 * HOUR
        prompt = asked_prompt(f.state, "v2")
        self.assertIn("KEPT AND WAITING FOR THE SMALL SLOT", prompt)
        self.assertIn("ready)", prompt)
        f.reject("plan for every frozen candidate", "choice-open", actor="other", at=second + 6 * HOUR,
                 choice="c1", milestones=plans("a"))
        f.send("choice-open", actor="other", at=second + 6 * HOUR, choice="c1", milestones=plans("a", "b"))
        self.assertEqual(["a", "b"], f.state["shelf"]["choices"]["c1"]["candidates"])

    def test_a_ready_idea_waits_for_a_rival_only_until_it_is_twelve_hours_old(self):
        f = self.f
        first = self.kept("a")
        self.lone()
        second = self.kept("b", actor="other", round_id="r2", at=first + 5 * HOUR, checkers=("author", "v3", "v1"))
        third = self.kept("c", actor="v1", round_id="r3", at=first + 10 * HOUR, checkers=("author", "v3", "v2"))
        self.assertEqual(second + 6 * HOUR, shelf.ready(f.state, "small", f.state["at"])["at"],
                         "two ready ideas open the choice; the third does not hold it up")
        self.assertEqual(third + 6 * HOUR, shelf.vote_from(f.state, "c", f.state["at"]))
        self.assertEqual(second + 6 * HOUR, shelf.vote_from(f.state, "a", f.state["at"]))
        f.send("idea-second", actor="v2", idea="b", verdict="drop", finding=test_higher_bar.PART)
        self.assertEqual(first + 12 * HOUR, shelf.ready(f.state, "small", f.state["at"])["at"],
                         "the one ready idea waits for its rival only until it is twelve hours old")
        f.reject("only until it is twelve hours old", "choice-open", actor="other", at=first + 11 * HOUR,
                 choice="c1", milestones=plans("a"))
        f.send("choice-open", actor="other", at=first + 12 * HOUR, choice="c1", milestones=plans("a"))
        self.assertEqual(["a"], f.state["shelf"]["choices"]["c1"]["candidates"])

    def test_residents_are_told_not_to_open_tasks_for_checks(self):
        f = self.f
        self.kept("a")
        self.assertNotIn("NO TASKS FOR CHECKS", asked_prompt(f.state, "v2"))
        self.lone()
        prompt = asked_prompt(f.state, "v2")
        for words in ("NO TASKS FOR CHECKS", "eight tasks about checking one film proposal",
                      "Never open a task for your own check", "or once it is twelve hours old"):
            self.assertIn(words, prompt)

    def test_an_idea_not_yet_kept_by_three_holds_nothing_up_and_cannot_enter(self):
        f = self.f
        first = self.kept("a")
        self.lone()
        self.kept("b", actor="other", round_id="r2", at=first + 5 * HOUR, checkers=("author",))
        f.send("choice-open", actor="other", at=first + 6 * HOUR, choice="c1", milestones=plans("a"))
        self.assertEqual(["a"], f.state["shelf"]["choices"]["c1"]["candidates"])

    def test_the_page_and_the_handbook_say_so(self):
        root = pathlib.Path(body.__file__).parents[1]
        source = (root / "site/house.js").read_text()
        for words in ("the council can vote on it from", "ready for the council's vote",
                      "No idea that three residents have checked and kept is waiting."):
            self.assertIn(words, source)
        self.assertIn("upgrade-20261117-lone-candidate", (root / "docs/SHELF.md").read_text())
        self.assertIn("A kept idea does not wait for a rival", (root / "docs/STEWARD_ORDERS.md").read_text())
        self.assertIn("No tasks for checks", (root / "docs/STEWARD_ORDERS.md").read_text())


if __name__ == "__main__":
    unittest.main()
