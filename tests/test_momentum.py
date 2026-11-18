"""The next project follows the last; research keeps a bench; more residents are home.

Steward, 17 November evening: "still concerned that we don't have another small project after a few
hours. Research also seems to not really happen or very slowly ... Maybe we need more residents for
a while, if so maybe we can have an Astra resident drive the research for a bit."
"""
import pathlib
import unittest
from pathlib import Path

from house import course, providers, shelf, staffing
from house.home import CHECKS_FOCUS, HOME_FOCUS, asked_prompt, choose_provider
from tests import test_higher_bar
from tests import test_lone_candidate
from tests.test_lone_candidate import plans
from tests.test_who_asked import HOUR


def on(state):
    state["maintenance"]["migrations"][shelf.MOMENTUM] = {"at": state["at"]}


class MomentumTests(unittest.TestCase):
    setUp, lone, kept = (getattr(test_lone_candidate.LoneCandidateTests, name) for name in ("setUp", "lone", "kept"))
    start, keep, ideas = (getattr(test_higher_bar.HigherBarTests, name) for name in ("start", "keep", "ideas"))

    def flow(self):
        self.lone()
        self.f.state["maintenance"]["migrations"][shelf.FLOW] = {"at": self.f.state["at"]}

    def test_before_the_change_a_kept_small_idea_waits_six_hours_for_its_vote(self):
        f = self.f
        first = self.kept("a")
        self.flow()
        self.assertEqual(first + 6 * HOUR, shelf.vote_from(f.state, "a", first + HOUR))
        f.reject("six hours", "choice-open", actor="v1", at=first + 2 * HOUR, choice="c1",
                 milestones=plans("a"))

    def test_a_kept_small_idea_can_be_voted_on_after_one_hour(self):
        f = self.f
        first = self.kept("a")
        self.flow()
        on(f.state)
        self.assertEqual(3600, shelf.cool(f.state, "small"))
        self.assertEqual(6 * HOUR, shelf.cool(f.state, "great"), "a great work still waits six hours")
        self.assertEqual(first + HOUR, shelf.vote_from(f.state, "a", first + 60))
        f.reject("hour", "choice-open", actor="v1", at=first + HOUR / 2, choice="c0",
                 milestones=plans("a"))
        f.send("choice-open", actor="v1", at=first + HOUR + 60, choice="c1", milestones=plans("a"))
        self.assertEqual("open", f.state["shelf"]["choices"]["c1"]["status"])
        self.assertIn("waits one hour", asked_prompt(f.state, "v3"))

    def test_research_keeps_a_bench_even_when_both_slots_are_full(self):
        f = self.f
        self.kept("a")
        self.flow()
        whole = f.state["shelf"]
        for slot in ("great", "small"):
            whole["ideas"]["x" + slot] = dict(self.ideas()["a"], status="project", scale=slot)
            whole["projects"][slot] = {"idea": "x" + slot, "owner": "v1", "status": "active", "slot": slot,
                                       "deadline": f.state["at"] + 1000 * HOUR, "extended": False}
        self.start(actor="other", round_id="r2")
        f.send("explore-publish", actor="other", round="r2", token="r2",
               ideas=[test_higher_bar.idea("b"), test_higher_bar.idea("c")])
        whole = f.state["shelf"]
        self.assertEqual([], shelf.thin(f.state, whole), "before the change full slots mean the four-hour gap")
        self.assertFalse(shelf.research_open(f.state, whole, f.state["at"] + HOUR, 3))
        on(f.state)
        self.assertEqual(["great", "small"], shelf.thin(f.state, whole))
        self.assertTrue(shelf.research_open(f.state, whole, f.state["at"], 3))
        for key in ("b", "c"):
            for checker in ("author", "v1", "v3"):
                self.keep(checker, key)
        self.assertEqual(["great"], shelf.thin(f.state, f.state["shelf"]), "three kept small ideas fill that bench")

    def test_the_same_kind_may_take_the_next_round(self):
        f = self.f
        self.kept("a")
        self.flow()
        kind = f.state["residents"]["v1"]["agent"]
        other = next(key for key, person in f.state["residents"].items()
                     if person.get("agent") not in (None, kind) and person["awake"])
        self.assertEqual(kind, f.state["shelf"]["last_kind"])
        self.assertTrue(other)
        f.reject("another kind", "explore-start", actor="v1", round="r2", token="r2", seconds=3600,
                 expect=f.state["shelf"]["generation"])
        on(f.state)
        self.start(actor="v1", round_id="r2")
        self.assertEqual("r2", f.state["shelf"]["explorer"])

    def test_more_residents_are_home(self):
        state = {"maintenance": {"migrations": {staffing.SCOPE: {"at": 1}}}, "life": {"runs": {}}}
        self.assertEqual((2, 3, 2, 4), tuple(staffing.capacity(state)[key] for key in
                                             ("baseline", "regular_limit", "helper_limit", "total_limit")))
        state["maintenance"]["migrations"][staffing.MOMENTUM] = {"at": 2}
        self.assertEqual((3, 5, 3, 7), tuple(staffing.capacity(state)[key] for key in
                                             ("baseline", "regular_limit", "helper_limit", "total_limit")))
        self.assertEqual(shelf.MOMENTUM, staffing.MOMENTUM)

    def test_research_rotates_and_astra_is_an_ordinary_route(self):
        # 18 November: the one-night scout is gone. The next round goes to a different kind from the last.
        state = {"at": 10.0, "maintenance": {"migrations": {staffing.SCOPE: {"at": 1}, staffing.MOMENTUM: {"at": 2}}},
                 "life": {"runs": {}, "budgets": {}}, "shelf": {"last_kind": "codex"}, "residents": {}, "tasks": {}}
        self.assertFalse(hasattr(providers, "SCOUT"))
        self.assertFalse(hasattr(course, "scout"))
        self.assertNotEqual("codex", choose_provider(state, 10.0, exploring=True))
        self.assertEqual(("gpt-6.1-sol", "gpt-6.2-astra"), providers.ROTATION["codex"])
        self.assertEqual("gpt-6.1-sol", course.route(state, "codex", at=10.0))
        state["life"]["runs"]["r"] = {"status": "completed", "agent": "codex", "model": "gpt-6.1-sol",
                                      "resident": "s", "started_sequence": 1}
        self.assertEqual("gpt-6.2-astra", course.route(state, "codex", at=10.0), "the routes take turns")
        self.assertEqual("gpt-6.1-sol", course.route(state, "codex", strong=True, at=10.0))
        self.assertEqual("gpt-6.1-sol", providers.STRONG["codex"], "Explorers and great works stay on Sol")

    def test_an_explorer_is_told_the_wishes_are_equal_and_what_recent_rounds_brought(self):
        from house.home import field_mix
        state = {"maintenance": {"migrations": {}}, "shelf": {"ideas": {}}}
        self.assertEqual("", field_mix(state), "before the higher bar there are no such fields")
        state["maintenance"]["migrations"][shelf.HIGHER] = {"at": 1}
        text = field_mix(state)
        self.assertIn("in no order", text)
        self.assertNotIn("the last", text)
        state["shelf"]["ideas"] = {
            f"i{n}": {"shelved_sequence": n, "brief": {"field": field}}
            for n, field in enumerate(["software"] + ["art"] * 3 + ["mathematics"] + [None], start=1)}
        state["shelf"]["ideas"]["old"] = {"shelved_sequence": 0}
        text = field_mix(state, last=4)
        self.assertIn("the last 4 ideas brought here were: art 3, mathematics 1; none were software, design, "
                      "science, language", text)
        self.assertIn("not a quota", text)

    def test_researchers_and_voters_are_told_what_the_house_lately_chose(self):
        from house.home import chosen_mix
        state = {"maintenance": {"migrations": {}}, "shelf": {"ideas": {}, "choices": {}}}
        self.assertEqual("", chosen_mix(state), "before the higher bar a brief does not say whom it is for")
        state["maintenance"]["migrations"][shelf.HIGHER] = {"at": 1}
        self.assertEqual("", chosen_mix(state), "nothing chosen yet, nothing to say")
        whom = ["people", "play", "play", "field", "play", None]
        state["shelf"]["ideas"] = {f"i{n}": ({"brief": {"for": value}} if value else {}) for n, value in enumerate(whom)}
        state["shelf"]["choices"] = {
            **{f"c{n}": {"status": "closed", "winner": f"i{n}", "closed_sequence": n} for n in range(len(whom))},
            "open": {"status": "open", "candidates": ["i1"]}, "none": {"status": "closed", "winner": None}}
        text = chosen_mix(state, last=4)
        self.assertIn("the last 4 projects the house chose were for: play 3, field 1; none were for people, house", text)
        self.assertIn("not a quota", text)

    def test_only_play_is_judged_by_the_grin_and_no_form_is_the_default(self):
        from house import home
        source = Path(home.__file__).read_text()
        self.assertNotIn("Two tests for any idea: would a stranger grin", source)
        self.assertNotIn("must do something a visitor can see, run or follow", source)
        self.assertIn("The grin is the test for fun only", home.HIGHER_GUIDE)
        self.assertIn("do not dress a result, a language or a tool as a game or a story", home.HIGHER_GUIDE)
        for words in ("little \"art\" pieces rather than anything else", "The grin is the test for play only",
                      "a library with a real program that imports it", "none is the default",
                      "This is not a quota and play is still welcome"):
            self.assertIn(words, home.NOT_A_TOY)

    def test_checks_focus_is_outside_the_old_rotation(self):
        self.assertNotIn(CHECKS_FOCUS, HOME_FOCUS)

    def test_every_fifth_house_run_is_given_to_second_looks(self):
        import time
        import types
        from house import course as course_model, home
        f = self.f
        self.flow()
        f.state["maintenance"]["migrations"][course_model.SCOPE] = {"at": 1}
        f.state["maintenance"]["migrations"][staffing.SCOPE] = {"at": 1}
        turn = lambda count: home.Coordinator.home_focus(types.SimpleNamespace(
            running={}, focus_record=lambda: {"run": "gone", "at": time.time() - 7200, "count": count}), f.state)
        self.assertEqual(list(HOME_FOCUS) + [HOME_FOCUS[0]], [turn(count) for count in range(5)])
        on(f.state)
        self.assertEqual([*HOME_FOCUS, CHECKS_FOCUS, HOME_FOCUS[0]], [turn(count) for count in range(6)])

    def test_the_handbook_and_orders_say_so(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        self.assertTrue("upgrade-20261117-momentum" in (root / "docs/SHELF.md").read_text())
        orders = (root / "docs/STEWARD_ORDERS.md").read_text()
        for words in ("The next project follows the last", "Second looks", "one hour"):
            self.assertTrue(words in orders, words)


if __name__ == "__main__":
    unittest.main()
