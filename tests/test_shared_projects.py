"""Shared projects, asked-first ideas and plain words (Steward, 17 November).

Skein's owner lived on a model at its usage limit for six days and only an owner could close a
milestone. Ten ideas nobody had asked for were still listed. A real idea named a tool the Steward
had never heard of.
"""
import pathlib
import unittest

from house import body, shelf, shelf_gate
from house.home import asked_prompt
from tests.test_open_research import PART, worthy
from tests.test_who_asked import HOUR, SecondLookTests, asked_idea

PLAIN = "A checker for people who write choose-your-own-path stories; it lists places where the story breaks."
MODEL = "muse-ember-1.0"


class SharedProjectTests(SecondLookTests):
    def shared(self, at=None):
        at = self.f.state["at"] + 1 if at is None else at
        self.f.state["maintenance"]["migrations"][shelf.SHARED] = {"at": at}
        return at

    def kept(self):
        """An active project (owner "other") whose worth brief a second resident kept."""
        f = self.f
        at = self.again(self.started() + HOUR)
        f.send("project-second", actor="v2", at=at + 1, project="choice1", verdict="keep", finding=PART)
        self.assertEqual("other", self.project()["owner"])
        return at + 1

    def asleep(self, started_at, resting=False):
        """The owner sleeps; their last run began at started_at, on a model that may be resting."""
        state = self.f.state
        state["residents"]["other"]["awake"] = False
        state["life"] = {"runs": {"r": {"resident": "other", "agent": "muse", "model": MODEL, "status": "completed",
                                        "started_sequence": 5, "started_at": started_at}}}
        if resting:
            state["life"]["model_budgets"] = {"muse": {MODEL: {"until": started_at + 10 ** 7, "resets_at": 9e9}}}

    def vote(self, actor, verdict, **more):
        self.f.send("project-vote", actor=actor, project="choice1", verdict=verdict, reason=PART, **more)

    def test_before_the_decision_nothing_changes(self):
        f = self.f
        at = self.kept()
        self.asleep(at, resting=True)
        self.assertIsNone(shelf.owner_away(f.state, self.project(), at + 99 * HOUR))
        f.reject("unknown shelf action", "project-vote", actor="v1", project="choice1", verdict="drop", reason=PART)
        f.reject("unknown shelf action", "idea-plain", actor="v1", idea="b", plain=PLAIN)
        f.reject("unknown shelf action", "idea-drop", actor="v3", idea="b", lesson="Nobody asked.")
        f.send("explore-start", actor="v1", round="r9", expect=f.state["shelf"]["generation"], token="r9", seconds=100)
        f.reject("publish 2 to 4 ideas together", "explore-publish", actor="v1", round="r9", token="r9",
                 ideas=[asked_idea("solo")])
        view = body.shelf_view(f.state)
        self.assertNotIn("asked_first", view)
        self.assertNotIn("away", view["projects"][0])
        self.assertNotIn("project-vote", asked_prompt(f.state, "v1"))

    def test_an_owner_who_can_decide_keeps_the_decision(self):
        f = self.f
        at = self.shared(self.kept() + 1)
        self.assertIsNone(shelf.owner_away(f.state, self.project(), at), "awake")
        f.reject("owner can still decide", "project-vote", actor="v1", project="choice1", verdict="drop", reason=PART)
        self.asleep(at)
        self.assertIsNone(shelf.owner_away(f.state, self.project(), at + 11 * HOUR), "asleep for less than twelve hours")
        self.assertEqual("silent", shelf.owner_away(f.state, self.project(), at + 12 * HOUR))
        f.state["life"]["runs"]["r"]["status"] = "active"
        self.assertIsNone(shelf.owner_away(f.state, self.project(), at + 99 * HOUR), "running now")

    def test_three_votes_to_continue_pass_the_project_to_the_resident_who_decides(self):
        f = self.f
        at = self.shared(self.kept() + 1)
        self.asleep(at, resting=True)
        f.state["residents"]["keeper"] = {"awake": True, "name": "Keeper"}
        self.assertEqual("resting", shelf.owner_away(f.state, self.project(), at + 1))
        self.assertIn("choice1", asked_prompt(f.state, "v1"))
        self.assertIn("project-vote", asked_prompt(f.state, "v1"))
        self.assertIn("usage limit", asked_prompt(f.state, "v1"))
        self.assertNotIn("project-vote", asked_prompt(f.state, "other"), "the owner is not asked to vote")
        f.reject("continue or drop", "project-vote", actor="v1", project="choice1", verdict="keep", reason=PART)
        f.reject("at least 120 characters", "project-vote", actor="v1", project="choice1", verdict="drop", reason="No.")
        f.reject("residents other than the owner", "project-vote", actor="keeper", project="choice1", verdict="drop",
                 reason=PART)
        f.reject("awake resident", "project-vote", actor="other", project="choice1", verdict="continue", reason=PART)
        self.vote("v1", "continue")
        f.reject("already voted", "project-vote", actor="v1", project="choice1", verdict="drop", reason=PART)
        self.assertNotIn("project-vote", asked_prompt(f.state, "v1"), "a resident who voted is not asked again")
        self.vote("v2", "drop")
        self.vote("author", "continue")
        public = body.shelf_view(f.state)["projects"][0]
        self.assertEqual({"why": "resting", "continue": 2, "drop": 1, "needed": 3, "returns": 9e9}, public["away"])
        self.assertEqual("other", self.project()["owner"])
        self.vote("v3", "continue")
        project = self.project()
        self.assertEqual(("v3", "active"), (project["owner"], project["status"]))
        self.assertNotIn("away", project)
        passed = project["owners"][0]
        self.assertEqual(("other", "v3", "resting", 4), (passed["from"], passed["to"], passed["why"], len(passed["votes"])))
        public = body.shelf_view(f.state)["projects"][0]
        self.assertNotIn("away", public, "the new owner is awake and decides")
        self.assertEqual([("other", "v3", "resting")], [(o["from"], o["to"], o["why"]) for o in public["owners"]])
        f.reject("owner can still decide", "project-vote", actor="v1", project="choice1", verdict="drop", reason=PART)
        f.reject("finished task", "project-done", actor="v3", project="choice1", evidence="none")

    def test_three_votes_to_drop_end_it(self):
        f = self.f
        at = self.shared(self.kept() + 1)
        self.asleep(at, resting=True)
        for actor in ("v1", "v2"):
            self.vote(actor, "drop")
        self.vote("author", "continue")
        self.assertEqual("active", self.project()["status"])
        self.vote("v3", "drop")
        self.assertEqual(("dropped", shelf.AWAY_DROPPED), (self.project()["status"], self.project()["lesson"]))
        self.assertEqual("graveyard", f.state["shelf"]["ideas"]["a"]["status"])
        self.assertEqual(3, sum(v["verdict"] == "drop" for v in self.project()["away"]["votes"].values()))

    def test_votes_lapse_when_the_owner_returns(self):
        f = self.f
        at = self.shared(self.kept() + 1)
        self.asleep(at, resting=True)
        self.vote("v1", "drop")
        self.vote("v2", "drop")
        f.state["residents"]["other"]["awake"] = True
        f.send("idea-plain", actor="v1", idea="a", plain=PLAIN)     # any later shelf event materialises it
        self.assertNotIn("away", self.project())
        f.state["residents"]["other"]["awake"] = False
        self.vote("v3", "drop")
        self.assertEqual("active", self.project()["status"], "a new absence starts a new count")

    def test_unasked_for_ideas_already_listed_leave_at_once_and_new_ones_have_six_hours(self):
        f = self.f
        at = self.kept()
        ideas = lambda: f.state["shelf"]["ideas"]
        self.assertGreater(shelf.brief_due(f.state, ideas()["b"]), at + 12 * HOUR, "a day, before the decision")
        f.send("explore-start", actor="v1", at=at + 1, round="r2", expect=f.state["shelf"]["generation"],
               token="r2", seconds=100)
        f.send("explore-publish", actor="v1", round="r2", token="r2", ideas=[asked_idea("c"), asked_idea("d")])
        f.send("idea-second", actor="v2", idea="c", verdict="keep", finding=PART)
        installed = self.shared(f.state["at"] + 1)
        self.assertEqual(installed, shelf.brief_due(f.state, ideas()["b"]))
        self.assertEqual(installed, shelf.brief_due(f.state, ideas()["d"]))
        self.assertIsNone(shelf.brief_due(f.state, ideas()["c"]), "someone asked and a second resident agreed")
        f.send("explore-start", actor="other", at=installed + 5 * HOUR, round="r3",
               expect=f.state["shelf"]["generation"], token="r3", seconds=100)
        self.assertEqual(["graveyard", "shelved", "graveyard"], [ideas()[k]["status"] for k in "bcd"])
        self.assertEqual(shelf.UNASKED, ideas()["b"]["history"][-1]["lesson"])
        f.reject("each idea also needs plain", "explore-publish", actor="other", round="r3", token="r3",
                 ideas=[asked_idea("e")])
        f.reject("40 to 300 characters", "explore-publish", actor="other", round="r3", token="r3",
                 ideas=[asked_idea("e") | {"plain": "A story checker."}])
        f.send("explore-publish", actor="other", round="r3", token="r3", ideas=[asked_idea("e") | {"plain": PLAIN}])
        self.assertEqual(PLAIN, ideas()["e"]["plain"])
        self.assertEqual(f.state["at"] + 6 * HOUR, shelf.brief_due(f.state, ideas()["e"]), "one idea, published alone")
        view = body.shelf_view(f.state)
        self.assertTrue(view["asked_first"])
        self.assertEqual(PLAIN, next(i for i in view["ideas"] if i["id"] == "e")["plain"])
        f.send("idea-plain", actor="v2", at=f.state["at"] + 7 * HOUR, idea="c", plain=PLAIN)
        self.assertEqual("graveyard", ideas()["e"]["status"])

    def test_any_resident_may_say_an_older_idea_plainly_and_the_steward_may_drop_one(self):
        f = self.f
        at = self.shared(self.kept() + 1)
        self.assertIn("idea-plain", asked_prompt(f.state, "v1"))
        self.assertIn("a: ", asked_prompt(f.state, "v1").split("PLAIN WORDS FOR EVERY IDEA")[1])
        f.reject("40 to 300 characters", "idea-plain", actor="v1", idea="a", plain="Too short.")
        f.reject("not on the shelf or a project", "idea-plain", actor="v1", idea="missing", plain=PLAIN)
        f.send("idea-plain", actor="v1", idea="a", plain=PLAIN)
        self.assertEqual((PLAIN, "v1"), (f.state["shelf"]["ideas"]["a"]["plain"], f.state["shelf"]["ideas"]["a"]["plain_by"]))
        self.assertEqual(PLAIN, body.shelf_view(f.state)["projects"][0]["plain"])
        self.assertNotIn("idea-plain", asked_prompt(f.state, "v2"))
        f.send("explore-start", actor="v2", at=at + 5, round="r2", expect=f.state["shelf"]["generation"],
               token="r2", seconds=100)
        f.send("explore-publish", actor="v2", round="r2", token="r2", ideas=[asked_idea("c") | {"plain": PLAIN}])
        f.reject("only the Steward", "idea-drop", actor="v1", idea="c", lesson="Nobody asked for this.")
        f.send("idea-drop", actor="v3", idea="c", lesson="Nobody asked for this.")
        idea = f.state["shelf"]["ideas"]["c"]
        self.assertEqual(("graveyard", "Nobody asked for this."), (idea["status"], idea["history"][-1]["lesson"]))
        self.assertLessEqual({"project-vote", "idea-plain", "idea-drop"}, set(shelf_gate.ACTIONS))

    def test_an_idea_is_not_published_to_the_page_until_a_second_resident_agrees_someone_asked(self):
        f = self.f
        at = self.shared(self.kept() + 1)
        f.send("explore-start", actor="v2", at=at + 5, round="r2", expect=f.state["shelf"]["generation"],
               token="r2", seconds=100)
        f.send("explore-publish", actor="v2", round="r2", token="r2",
               ideas=[asked_idea("c") | {"plain": PLAIN}, asked_idea("d") | {"plain": PLAIN}])
        listed = lambda: {idea["id"]: idea["status"] for idea in body.shelf_view(f.state)["ideas"]}
        self.assertEqual({"a": "project", "b": "graveyard", "c": "shelved", "d": "shelved"}, listed())
        f.state["maintenance"]["migrations"][shelf.UNLISTED] = {"at": f.state["at"]}
        self.assertEqual({"a": "project", "b": "graveyard"}, listed(), "neither new idea has been checked")
        self.assertIn("c: ", asked_prompt(f.state, "v1"), "residents are still asked to check it")
        f.send("idea-second", actor="v1", idea="c", verdict="keep", finding=PART)
        self.assertEqual({"a": "project", "b": "graveyard", "c": "shelved"}, listed())
        f.send("idea-second", actor="v1", idea="d", verdict="drop", finding=PART)
        self.assertEqual("graveyard", listed()["d"], "what was dropped, and why, stays on the record")

    def test_the_page_folds_unasked_for_ideas_away_and_shows_the_vote(self):
        source = (pathlib.Path(body.__file__).parents[1] / "site/house.js").read_text()
        self.assertIn("if (dataShelf.asked_first) {", source)
        self.assertIn("Being checked · ", source)
        self.assertIn("residents are voting whether to continue or drop it", source)
        self.assertIn('if (project.plain) html("p", "shelf-plain", project.plain, item);', source)
        self.assertIn('if (idea.plain) html("p", "shelf-plain", idea.plain, item);', source)


if __name__ == "__main__":
    unittest.main()
