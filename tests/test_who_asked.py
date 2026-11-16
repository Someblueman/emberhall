"""Who asked (Steward decision, 16 November): quoted askers, a second resident, and briefed projects."""
import copy
import unittest

from house import body, council, shelf, shelf_gate
from house.home import ASKED_GUIDE, asked_prompt, brief_guide, focus_prompt
from tests import test_shelf
from tests.test_open_research import PART, worthy

HOUR = 3600
ASKED = [
    {"who": "A maintainer on an issue tracker", "where": "https://tracker.example.org/issues/41",
     "said": "I keep doing this by hand every release and it takes me most of a day."},
    {"who": "A teacher on a forum", "where": "https://forum.example.net/t/900",
     "said": "Is there any tool that does this without sending my files somewhere?"},
]


def grounded_brief(**changes):
    return worthy("x")["brief"] | {"asked": copy.deepcopy(ASKED)} | changes


def asked_idea(key):
    return test_shelf.idea(key) | {"brief": grounded_brief()}


class WhoAskedTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()
        self.f.state["maintenance"] = {"migrations": {
            shelf.OPEN_RESEARCH: {"at": 1000}, shelf.WORTH_BUILDING: {"at": 1000}}}

    def install(self, at=None):
        at = self.f.state["at"] if at is None else at
        self.f.state["maintenance"]["migrations"][shelf.WHO_ASKED] = {"at": at}
        return at

    def publish(self, ideas, round_id="r1", actor="author", at=None):
        f = self.f
        generation = f.state.get("shelf", {}).get("generation", 0)
        f.send("explore-start", actor=actor, at=at, round=round_id, expect=generation, token=round_id, seconds=100)
        f.send("explore-publish", actor=actor, round=round_id, token=round_id, ideas=ideas)

    def test_before_the_decision_nothing_changes(self):
        f = self.f
        self.publish([worthy("a"), worthy("b")])
        ideas = f.state["shelf"]["ideas"]
        self.assertTrue(shelf.grounded(f.state, ideas["a"]))
        self.assertIsNone(shelf.brief_due(f.state, ideas["a"]))
        f.reject("field, worth, benefit, interest, exists, first_version and check", "idea-brief", actor="other",
                 idea="a", brief=grounded_brief())
        f.reject("unknown shelf action", "idea-second", actor="other", idea="a", verdict="keep", finding=PART)
        f.reject("unknown shelf action", "project-brief", actor="other", project="p", brief=grounded_brief())
        self.assertEqual("", asked_prompt(f.state, "author"))
        self.assertNotIn("asked", brief_guide(f.state)[0])
        self.assertNotIn("grounded", body.shelf_view(f.state)["ideas"][0])
        f.choose(votes=("a", "a", "b"))
        self.assertEqual("active", f.state["shelf"]["projects"]["choice1"]["status"])

    def test_a_brief_quotes_people_on_two_sites(self):
        f = self.f
        self.install()
        f.send("explore-start", round="r1", expect=0, token="r1", seconds=100)

        def refused(message, **changes):
            f.reject(message, "explore-publish", round="r1", token="r1",
                     ideas=[test_shelf.idea("a") | {"brief": grounded_brief(**changes)}, asked_idea("b")])
        f.reject("check and asked", "explore-publish", round="r1", token="r1", ideas=[worthy("a"), asked_idea("b")])
        refused("asked lists 2 to 6 places", asked=ASKED[:1])
        refused("asked lists 2 to 6 places", asked="people want it")
        refused("who, where and said", asked=[ASKED[0], {"who": "x", "where": "https://example.net/1"}])
        refused("HTTP", asked=[ASKED[0], ASKED[1] | {"where": "a forum somewhere"}])
        refused("at least 40 characters", asked=[ASKED[0], ASKED[1] | {"said": "I want this."}])
        refused("two different sites", asked=[ASKED[0], ASKED[1] | {"where": "https://www.tracker.example.org/b"}])
        f.send("explore-publish", round="r1", token="r1", ideas=[asked_idea("a"), asked_idea("b")])
        brief = f.state["shelf"]["ideas"]["a"]["brief"]
        self.assertEqual(ASKED, brief["asked"])
        self.assertIn('"asked"', brief_guide(f.state)[0])
        self.assertTrue(brief_guide(f.state)[1].endswith(ASKED_GUIDE))

    def test_a_second_resident_keeps_or_drops_and_a_new_brief_needs_a_new_second(self):
        f = self.f
        self.install()
        self.publish([asked_idea("a"), asked_idea("b"), asked_idea("c")])
        f.send("idea-brief", actor="other", idea="b", brief=grounded_brief())
        ideas = lambda: f.state["shelf"]["ideas"]
        self.assertFalse(shelf.grounded(f.state, ideas()["a"]))
        f.reject("neither the idea nor its brief", "idea-second", actor="author", idea="a", verdict="keep", finding=PART)
        f.reject("neither the idea nor its brief", "idea-second", actor="other", idea="b", verdict="keep", finding=PART)
        f.reject("keep or drop", "idea-second", actor="v1", idea="a", verdict="maybe", finding=PART)
        f.reject("at least 120 characters", "idea-second", actor="v1", idea="a", verdict="keep", finding="Looks fine.")
        f.reject("not on the shelf", "idea-second", actor="v1", idea="missing", verdict="keep", finding=PART)
        f.send("idea-second", actor="v1", idea="a", verdict="keep", finding=PART)
        self.assertTrue(shelf.grounded(f.state, ideas()["a"]))
        self.assertIsNone(shelf.brief_due(f.state, ideas()["a"]))
        self.assertEqual("v1", ideas()["a"]["second"]["author"])
        f.send("idea-brief", actor="v2", idea="a", brief=grounded_brief())
        self.assertFalse(shelf.grounded(f.state, ideas()["a"]), "a replaced brief has not been checked")
        f.send("idea-second", actor="v3", idea="c", verdict="drop", finding=PART + "Nobody asked.")
        self.assertEqual("graveyard", ideas()["c"]["status"])
        self.assertEqual({"seconded_out": True, "by": "v3", "lesson": PART + "Nobody asked."},
                         {k: v for k, v in ideas()["c"]["history"][-1].items() if k != "sequence"})
        self.assertLessEqual({"idea-second", "project-brief"}, set(shelf_gate.ACTIONS))

    def test_an_idea_nobody_stands_behind_leaves_after_a_day_and_cannot_be_chosen(self):
        f = self.f
        self.publish([worthy("old"), worthy("old2")])
        at = self.install()
        ideas = lambda: f.state["shelf"]["ideas"]
        self.assertEqual(at + shelf.SECOND_SECONDS, shelf.brief_due(f.state, ideas()["old"]))
        f.reject("no shelved idea of that scale has shown who asked", "choice-open", actor="other", choice="c1",
                 milestones={k: {"milestone": "One usable example", "seconds": 100} for k in ("old", "old2")})
        f.send("idea-brief", actor="other", idea="old", brief=grounded_brief())
        self.assertEqual(at + shelf.SECOND_SECONDS, shelf.brief_due(f.state, ideas()["old"]),
                         "askers alone do not keep an idea")
        f.send("idea-second", actor="v1", idea="old", verdict="keep", finding=PART)
        f.reject("plan for every frozen candidate", "choice-open", actor="other", choice="c1",
                 milestones={k: {"milestone": "One usable example", "seconds": 100} for k in ("old", "old2")})
        shelf.advance(f.state, at + shelf.SECOND_SECONDS, 900)
        self.assertEqual(("shelved", "graveyard"), (ideas()["old"]["status"], ideas()["old2"]["status"]))
        self.assertEqual(shelf.UNGROUNDED, ideas()["old2"]["history"][-1]["lesson"])
        f.send("choice-open", actor="other", at=at + shelf.SECOND_SECONDS + 1, choice="c1",
               milestones={"old": {"milestone": "One usable example", "seconds": 100}})
        self.assertEqual(["old"], f.state["shelf"]["choices"]["c1"]["candidates"])

    def test_a_project_chosen_earlier_has_six_hours_for_a_brief_from_someone_else(self):
        f = self.f
        self.publish([worthy("a"), worthy("b")])
        f.choose(votes=("a", "a", "b"))
        project = lambda: f.state["shelf"]["projects"]["choice1"]
        self.assertEqual(("active", "other"), (project()["status"], project()["owner"]))
        self.assertIsNone(shelf.project_due(f.state, project()))
        at = self.install()
        self.assertEqual(at + 6 * HOUR, shelf.project_due(f.state, project()))
        view = body.shelf_view(f.state)["projects"][0]
        self.assertEqual(at + 6 * HOUR, view["brief_due"])
        f.reject("does not own it", "project-brief", actor="other", project="choice1", brief=grounded_brief())
        f.reject("check and asked", "project-brief", actor="v1", project="choice1", brief=worthy("x")["brief"])
        f.reject("not active", "project-brief", actor="v1", project="nothing", brief=grounded_brief())
        self.assertIn("choice1", asked_prompt(f.state, "v1"))
        self.assertIn("DO THIS FIRST", asked_prompt(f.state, "v1"))
        self.assertIn("6 h left", asked_prompt(f.state, "v1"))
        owner = asked_prompt(f.state, "other")
        self.assertNotIn("DO THIS FIRST", owner)
        self.assertIn("You cannot write its worth brief yourself", owner)
        unbriefed = copy.deepcopy(f.state)
        shelf.advance(unbriefed, at + 6 * HOUR - 1, 900)
        self.assertEqual("active", unbriefed["shelf"]["projects"]["choice1"]["status"])
        shelf.advance(unbriefed, at + 6 * HOUR, 901)
        self.assertEqual(("dropped", shelf.UNBRIEFED_PROJECT),
                         tuple(unbriefed["shelf"]["projects"]["choice1"][k] for k in ("status", "lesson")))
        self.assertEqual("graveyard", unbriefed["shelf"]["ideas"]["a"]["status"])
        f.send("project-brief", actor="v1", at=at + HOUR, project="choice1", brief=grounded_brief())
        self.assertIsNone(shelf.project_due(f.state, project()))
        shelf.advance(f.state, at + 7 * HOUR, 902)
        self.assertEqual("active", project()["status"])
        view = body.shelf_view(f.state)["projects"][0]
        self.assertNotIn("brief_due", view)
        self.assertEqual("v1", view["brief"]["author"])
        self.assertEqual(ASKED[0]["where"], view["brief"]["asked"][0]["where"])
        self.assertNotIn("DO THIS FIRST", asked_prompt(f.state, "v2"))

    def test_a_project_chosen_under_the_test_needs_no_second_brief(self):
        f = self.f
        self.install()
        self.publish([asked_idea("a"), asked_idea("b")])
        for key in "ab":
            f.send("idea-second", actor="v1", idea=key, verdict="keep", finding=PART)
        f.choose(votes=("a", "a", "b"))
        self.assertIsNone(shelf.project_due(f.state, f.state["shelf"]["projects"]["choice1"]))

    def test_a_need_says_what_residents_tried_first(self):
        f = self.f
        self.publish([worthy("a"), worthy("b")])
        f.state["council"] = {"authorized_by": "v3"}
        need = {"need": "n1", "need_kind": "server", "for": "a", "ask": "A small always-on server",
                "cost": "about 5 dollars a month", "unlocks": PART, "without": PART}
        f.send("need-raise", **need)
        self.install()
        f.reject("unexpected shelf fields", "need-raise", **(need | {"need": "n2"}))
        f.reject("tried each need at least 120", "need-raise", **(need | {"need": "n2", "tried": "Nothing yet."}))
        f.send("need-raise", **(need | {"need": "n2", "tried": PART}))
        view = {item["id"]: item for item in body.shelf_view(f.state)["needs"]}
        self.assertNotIn("tried", view["n1"])
        self.assertEqual(" ".join(PART.split()), view["n2"]["tried"])

    def test_public_view_and_prompts_show_askers_and_who_may_second(self):
        f = self.f
        self.install()
        self.publish([asked_idea("a"), asked_idea("b")])
        f.send("idea-second", actor="v1", idea="a", verdict="keep", finding=PART)
        view = {idea["id"]: idea for idea in body.shelf_view(f.state)["ideas"]}
        self.assertEqual((True, False), (view["a"]["grounded"], view["b"]["grounded"]))
        self.assertEqual("v1", view["a"]["second"]["author"])
        self.assertNotIn("second", view["b"])
        self.assertEqual(ASKED[1]["said"], view["b"]["brief"]["asked"][1]["said"])
        self.assertNotIn("brief_due", view["a"])
        self.assertIn("brief_due", view["b"])
        self.assertNotIn("waiting for a second resident you may be", asked_prompt(f.state, "author"))
        prompt = asked_prompt(f.state, "v2")
        self.assertIn("waiting for a second resident you may be: b: b", prompt)
        self.assertNotIn("a: a", prompt)
        for words in ("PAGE VIEWER", "view PATH --as v2", "never asks for the Steward's time", "tried"):
            self.assertIn(words, prompt)
        self.assertIn("show who asked", focus_prompt(f.state | {"life": {}}, "research"))


if __name__ == "__main__":
    unittest.main()
