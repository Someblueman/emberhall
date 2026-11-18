"""A higher bar (Steward, 17 November): whom it is for, reach, three checkers, a real comparison.

A checker for one hobby's story files went from idea to project in thirteen minutes on three forum
posts, as the only candidate. The Steward dropped it and asked for art, mathematics, a programming
language, a field moved forward, or work on the house itself.
"""
import pathlib
import time
import types
import unittest
from unittest.mock import patch

from house import body, home, shelf
from house.home import asked_prompt, brief_guide
from tests import test_shelf
from tests.test_open_research import PART
from tests.test_who_asked import ASKED, HOUR, WhoAskedTests, grounded_brief

PLAIN = "A new small programming language in which every value remembers where it came from."
PEOPLE = ASKED + [
    {"who": "A librarian on a mailing list", "where": "https://lists.example.com/archive/77",
     "said": "We have asked three vendors for this and none of them will build it."},
    {"who": "A second maintainer", "where": "https://tracker.example.org/issues/90",
     "said": "Same here, I lose a day to this every single month and I am tired of it."}]
FIELD = [{"who": "A survey of the area", "where": "https://journal.example.org/survey",
          "said": "Whether such a bound holds for all n remains open after forty years."},
         {"who": "A problem list kept by researchers", "where": "https://problems.example.net/112",
          "said": "No construction is known beyond the first few small cases."}]
HOUSE = [{"who": "The Steward", "where": "docs/STEWARD_ORDERS.md",
          "said": "The Steward could not tell from the page whether any work was being done."},
         {"who": "A resident's handoff", "where": "seq:12229",
          "said": "I spent most of this run finding out what the last resident had left unfinished."}]


def high(whom="people", **changes):
    evidence = {"people": PEOPLE, "field": FIELD, "house": HOUSE}[whom]
    return grounded_brief() | {"for": whom, "reach": PART, "rather": PART, "asked": evidence} | changes


def idea(key, whom="people", **changes):
    return test_shelf.idea(key) | {"plain": PLAIN, "brief": high(whom, **changes)}


class HigherBarTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()
        self.f.state["maintenance"] = {"migrations": {scope: {"at": 1000} for scope in (
            shelf.OPEN_RESEARCH, shelf.WORTH_BUILDING, shelf.WHO_ASKED, shelf.SECOND_LOOK, shelf.SHARED,
            shelf.UNLISTED)}}

    publish = WhoAskedTests.publish

    def higher(self):
        self.f.state["maintenance"]["migrations"][shelf.HIGHER] = {"at": self.f.state["at"]}

    def start(self, actor="v1", round_id="r1", at=None):
        f = self.f
        f.send("explore-start", actor=actor, at=at, round=round_id, expect=f.state.get("shelf", {}).get("generation", 0),
               token=round_id, seconds=100)

    def keep(self, actor, key, **more):
        self.f.send("idea-second", actor=actor, idea=key, verdict="keep", finding=PART, **more)

    def ideas(self):
        return self.f.state["shelf"]["ideas"]

    def test_before_the_decision_the_old_brief_stands_and_art_is_not_a_field(self):
        f = self.f
        self.start()
        f.reject("field, worth, benefit, interest, exists, first_version, check and asked", "explore-publish",
                 actor="v1", round="r1", token="r1", ideas=[idea("a")])
        f.reject("software, design or science", "explore-publish", actor="v1", round="r1", token="r1",
                 ideas=[test_shelf.idea("a") | {"plain": PLAIN, "brief": grounded_brief(field="art")}])
        f.send("explore-publish", actor="v1", round="r1", token="r1",
               ideas=[test_shelf.idea("a") | {"plain": PLAIN, "brief": grounded_brief()}])
        self.keep("author", "a")
        self.assertTrue(shelf.grounded(f.state, self.ideas()["a"]), "one second was enough")
        self.assertNotIn("A HIGHER BAR", asked_prompt(f.state, "v2"))
        self.assertNotIn('"for"', brief_guide(f.state)[0])

    def test_a_brief_says_whom_it_is_for_with_evidence_that_fits(self):
        f = self.f
        self.higher()
        self.start()

        def refused(message, whom="people", **changes):
            f.reject(message, "explore-publish", actor="v1", round="r1", token="r1", ideas=[idea("a", whom, **changes)])
        f.reject("for, benefit, interest, reach, rather", "explore-publish", actor="v1", round="r1", token="r1",
                 ideas=[test_shelf.idea("a") | {"plain": PLAIN, "brief": grounded_brief()}])
        refused("people, house, field or play", **{"for": "everyone"})
        refused("useful, beautiful, enabling or fun", worth="popular")
        refused("closest earlier attempts", "field", asked=FIELD[:1], **{"for": "play"})
        refused("art, mathematics or language", field="poetry")
        refused("at least 120 characters", reach="Lots of people.")
        refused("at least 120 characters", rather="It is nicer.")
        refused("4 to 8 people outside Emberhall", asked=ASKED)
        refused("three different sites", asked=PEOPLE[:2] + [PEOPLE[3], PEOPLE[3] | {"who": "Another"}])
        refused("2 to 8 pages", "field", asked=FIELD[:1])
        refused("two different sites", "field", asked=[FIELD[0], FIELD[0] | {"who": "Same journal"}])
        refused("its own record", "house", asked=[HOUSE[0], HOUSE[1] | {"where": "https://example.org/x"}])
        refused("its own record", "house", asked=[HOUSE[0], HOUSE[1] | {"where": "../secrets"}])
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[
            idea("tool"), idea("proof", "field", field="mathematics"), idea("song", "field", field="art", worth="beautiful"),
            idea("handoff", "house")])
        self.start(actor="other", round_id="r2", at=f.state["at"] + 5 * HOUR)
        f.send("explore-publish", actor="other", round="r2", token="r2", ideas=[
            idea("smoke", "field", field="mathematics", worth="fun", **{"for": "play"})])
        self.assertEqual(("play", "fun"), (self.ideas()["smoke"]["brief"]["for"], self.ideas()["smoke"]["brief"]["worth"]))
        self.assertEqual(["people", "field", "field", "house"],
                         [self.ideas()[key]["brief"]["for"] for key in ("tool", "proof", "song", "handoff")])
        self.assertEqual("seq:12229", self.ideas()["handoff"]["brief"]["asked"][1]["where"])
        shape, guide = brief_guide(f.state)
        self.assertIn('"for":"people|house|field|play"', shape)
        self.assertIn("useful|beautiful|enabling|fun", shape)
        self.assertIn("art|mathematics|language", shape)
        self.assertIn("rather (why this deserves days of the house's work", guide)

    def test_three_residents_of_two_kinds_keep_an_idea_and_one_drop_ends_it(self):
        f = self.f
        self.higher()
        self.start()
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[idea("a"), idea("b")])
        grounded = lambda key: shelf.grounded(f.state, self.ideas()[key])
        self.assertIn("a: ", asked_prompt(f.state, "author").split("three checks")[1])
        self.keep("author", "a")
        self.assertNotIn("a: ", asked_prompt(f.state, "author").split("A HIGHER BAR")[1].split("PAGE VIEWER")[0].split("three checks")[-1])
        f.reject("already kept this idea", "idea-second", actor="author", idea="a", verdict="keep", finding=PART)
        self.keep("v3", "a")
        self.assertFalse(grounded("a"), "two keeps")
        f.state["residents"]["v4"] = {"awake": True, "agent": "codex"}
        self.keep("v4", "a")
        self.assertFalse(grounded("a"), "three keeps, but all one kind of mind")
        self.keep("other", "a")
        self.assertTrue(grounded("a"))
        self.assertEqual(["codex", "codex", "codex", "muse"], [e["kind"] for e in shelf.keeps(f.state, self.ideas()["a"])])
        self.keep("author", "b")
        self.keep("other", "b")
        f.send("idea-second", actor="v2", idea="b", verdict="drop", finding=PART + " A handful of hobbyists.")
        self.assertEqual("graveyard", self.ideas()["b"]["status"])
        f.send("idea-brief", actor="v2", idea="a", brief=high())
        self.assertFalse(grounded("a"), "a new brief needs its own three checks")
        self.assertEqual({"a": "shelved"}, {i["id"]: i["status"] for i in body.shelf_view(f.state)["ideas"]
                                            if i["status"] == "shelved"} or {"a": "shelved"})

    def test_an_idea_waits_six_hours_and_a_choice_compares_at_least_two(self):
        f = self.f
        self.higher()
        self.start()
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[idea("a"), idea("b")])
        published = f.state["at"]
        for key in ("a", "b"):
            for actor in ("author", "v3", "other"):
                self.keep(actor, key)
        plans = lambda *keys: {k: {"milestone": "One usable example", "seconds": 100} for k in keys}
        f.reject("compares at least two ideas", "choice-open", actor="other", choice="c1", milestones=plans("a", "b"))
        f.send("idea-second", actor="v2", at=published + 6 * HOUR, idea="b", verdict="drop", finding=PART)
        f.reject("compares at least two ideas", "choice-open", actor="other", choice="c1", milestones=plans("a"))
        self.assertTrue(shelf.grounded(f.state, self.ideas()["a"]), "the one good idea waits; it is not dropped")
        self.start(actor="other", round_id="r2")
        f.send("explore-publish", actor="other", round="r2", token="r2", ideas=[idea("c", "house")])
        for actor in ("author", "v3", "v1"):
            self.keep(actor, "c")
        f.reject("compares at least two ideas", "choice-open", actor="other", choice="c1", milestones=plans("a", "c"))
        f.send("choice-open", actor="other", at=f.state["at"] + 6 * HOUR, choice="c1", milestones=plans("a", "c"))
        self.assertEqual(["a", "c"], f.state["shelf"]["choices"]["c1"]["candidates"])

    def test_residents_are_told_what_to_aim_at_and_that_an_empty_slot_means_house_work(self):
        f = self.f
        self.publish([test_shelf.idea("x") | {"plain": PLAIN, "brief": grounded_brief()},
                      test_shelf.idea("y") | {"plain": PLAIN, "brief": grounded_brief()}], actor="v1")
        self.higher()
        prompt = asked_prompt(f.state, "v2")
        for words in ("A HIGHER BAR", "Art made because it is beautiful", "mathematics with results",
                      "a programming language with an idea of its own", "smoke signals over HTTP",
                      "a terminal emulator in brainfuck", "an absurd thing done with complete seriousness",
                      "for play and judged by whether it is fun", "Start with the Gallery",
                      "NO PROJECT FILLS THE GREAT OR THE SMALL SLOT", "the house is the work"):
            self.assertIn(words, prompt)
        f.state["shelf"]["projects"] = {
            "g": {"idea": "x", "owner": "v1", "status": "active", "slot": "great"},
            "s": {"idea": "y", "owner": "v1", "status": "active", "slot": "small"}}
        self.assertNotIn("NO PROJECT FILLS", asked_prompt(f.state, "v2"))
        self.assertIn("A HIGHER BAR", asked_prompt(f.state, "v2"))

    def test_an_idle_run_works_on_the_house_while_a_slot_is_empty(self):
        f = self.f
        recent = types.SimpleNamespace(running={"r": 1}, focus_record=lambda: {"run": "r", "at": time.time(), "count": 1})
        focus = lambda **how: home.Coordinator.home_focus(recent, f.state, **how)
        with patch("house.course.enabled", lambda state: True):
            self.assertIsNone(focus(idle=True), "before the decision one house run at a time, half an hour apart")
            self.higher()
            self.assertEqual(home.HOME_FOCUS[1], focus(idle=True))
            self.assertIsNone(focus(), "a run with project work selected is not taken from it")
            f.state["shelf"] = shelf.empty() | {"projects": {
                "g": {"idea": "x", "owner": "v1", "status": "active", "slot": "great"},
                "s": {"idea": "y", "owner": "v1", "status": "active", "slot": "small"}}}
            self.assertIsNone(focus(idle=True), "both slots are filled")

    def test_the_page_shows_whom_it_is_for_and_its_reach(self):
        f = self.f
        self.higher()
        self.start()
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[idea("a", "house")])
        for actor in ("author", "v3", "other"):
            self.keep(actor, "a")
        shown = next(i for i in body.shelf_view(f.state)["ideas"] if i["id"] == "a")["brief"]
        self.assertEqual(("house", PART.strip(), PART.strip()), (shown["for"], shown["reach"], shown["rather"]))
        source = (pathlib.Path(body.__file__).parents[1] / "site/house.js").read_text()
        for words in ("Who benefits, and roughly how many", "Why this rather than work on the house",
                      "Where the house's own record shows the need"):
            self.assertIn(words, source)
        wishes = (pathlib.Path(body.__file__).parents[1] / "docs/WISHES.md").read_text()
        self.assertIn("Invent a programming language", wishes)
        self.assertIn("smoke signals over HTTP", wishes)
        source = (pathlib.Path(body.__file__).parents[1] / "site/house.js").read_text()
        self.assertIn("Is it fun: would a stranger grin, stare or argue?", source)
        self.assertIn("Make the house itself better", wishes)

    def test_the_page_shows_every_resident_who_kept_an_idea(self):
        f = self.f
        self.higher()
        self.start()
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[idea("a", "house")])
        for actor in ("author", "v3", "other"):
            self.keep(actor, "a")
        shown = next(i for i in body.shelf_view(f.state)["ideas"] if i["id"] == "a")
        self.assertEqual(["author", "v3", "other"], [keep["author"] for keep in shown["keeps"]])
        self.assertEqual(["codex", "codex", "muse"], [keep["kind"] for keep in shown["keeps"]])
        self.assertEqual([PART.strip()] * 3, [keep["finding"] for keep in shown["keeps"]])
        source = (pathlib.Path(body.__file__).parents[1] / "site/house.js").read_text()
        self.assertIn("Opened the evidence and kept by", source)


if __name__ == "__main__":
    unittest.main()
