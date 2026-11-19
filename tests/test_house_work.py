"""A third project slot, house work (Steward, 18 November).

"there's never any 'new' work happening in the house, it looks and feels the same and all work is
either patching existing things or projects". In 48 hours 67 public-page tasks finished and nearly all
added one control to an existing room. A house-focus run finishes one small thing in its own files, and
anything bigger had only the shelf, whose two slots fill with outward ideas. Owner migration
upgrade-20261118-house-work adds a third scale and slot, "house": one work on Emberhall itself that
takes days, chosen by the same vote and built by several residents.
"""
import copy
import pathlib
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from house import body, home, project_work, shelf
from house.home import asked_prompt, focus_prompt
from tests import test_higher_bar, test_shelf
from tests.test_lone_candidate import plans
from tests.test_who_asked import HOUR


def house_idea(key, **changes):
    return test_higher_bar.idea(key, "house", **changes) | {"scale": "house"}


def scaled(key, which):
    return test_higher_bar.idea(key) | {"scale": which}


class HouseWorkTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()
        original = shelf.apply
        self.addCleanup(setattr, shelf, "apply", original)
        shelf.apply = lambda state, event, selection_version=3: original(state, event, selection_version=3)
        self.f.state["maintenance"] = {"migrations": {scope: {"at": 1000} for scope in (
            shelf.OPEN_RESEARCH, shelf.WORTH_BUILDING, shelf.WHO_ASKED, shelf.SECOND_LOOK, shelf.SHARED,
            shelf.UNLISTED, shelf.HIGHER, shelf.LONE, shelf.FLOW, shelf.MOMENTUM)}}

    start, keep, ideas = (getattr(test_higher_bar.HigherBarTests, name) for name in ("start", "keep", "ideas"))

    def on(self):
        self.f.state["maintenance"]["migrations"][shelf.HOUSE_WORK] = {"at": self.f.state["at"]}

    def kept(self, entry, actor="v1", round_id="r1", at=None, checkers=("author", "v3", "other")):
        key = entry["idea"]
        self.start(actor=actor, round_id=round_id, at=at)
        self.f.send("explore-publish", actor=actor, round=round_id, token=round_id, ideas=[entry])
        for checker in checkers:
            self.keep(checker, key)
        return self.ideas()[key]["shelved_at"]

    def occupy(self, *slots):
        whole = self.f.state["shelf"]
        for slot in slots:
            whole["ideas"]["x" + slot] = dict(self.ideas()["a"], status="project", scale=slot)
            whole["projects"]["p" + slot] = {"idea": "x" + slot, "owner": "v1", "status": "active", "slot": slot,
                                             "milestone": "m", "deadline": self.f.state["at"] + 1000 * HOUR,
                                             "extended": False, "extension_votes": {}}

    def vote(self, choice, idea, voters=("v2", "v3", "other")):
        for voter in voters:
            self.f.send("choice-vote", actor=voter, choice=choice, idea=idea, reason="Worth the days")

    # Before the migration nothing is accepted and nothing changes.

    def test_before_the_migration_every_house_input_is_refused(self):
        f = self.f
        self.start()
        f.reject("scale must be great or small", "explore-publish", actor="v1", round="r1", token="r1",
                 ideas=[house_idea("a")])
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[test_higher_bar.idea("s")])
        f.reject("slot must be great or small", "choice-open", actor="v2", choice="c1", slot="house",
                 milestones=plans("s"))
        self.assertEqual(("great", "small"), shelf.scales(f.state))
        self.assertIsNone(shelf.house_work(f.state))

    def test_before_the_migration_thin_ready_and_cool_are_as_they_were(self):
        f = self.f
        first = self.kept(test_higher_bar.idea("a"))
        self.assertEqual(["great", "small"], shelf.thin(f.state, f.state["shelf"]))
        self.assertEqual(6 * HOUR, shelf.cool(f.state, "house"), "no house scale yet: the old six hours")
        self.assertEqual(HOUR, shelf.cool(f.state, "small"))
        self.assertEqual(shelf.COOL_SECONDS, shelf.cool(f.state, "great"))
        self.assertEqual(first + HOUR, shelf.vote_from(f.state, "a", first))
        self.assertEqual([], shelf.ready(f.state, "house", first + 9 * HOUR)["now"])
        self.assertFalse(shelf.ready(f.state, "house", first + 9 * HOUR)["open"])
        self.assertEqual({"great": 2, "small": 3, "house": 2}, shelf.BENCH)
        self.on()
        self.assertEqual(["great", "small", "house"], shelf.thin(f.state, f.state["shelf"]))

    def test_a_house_slot_project_that_somehow_exists_changes_nothing_before_the_migration(self):
        f = self.f
        self.kept(test_higher_bar.idea("a"))
        self.occupy("house")
        self.assertIsNone(shelf.house_work(f.state))
        self.assertNotIn("HOUSE WORK", focus_prompt(f.state, "improve"))
        self.assertNotIn("house idea", focus_prompt(f.state, "improve"))
        for words in ("things to make sessions more efficient for everyone", "docs/skills/README.md",
                      "removes a cost you met in your own runs"):
            self.assertIn(words, focus_prompt(f.state, "improve"), "a run that improves the house may lighten sessions")

    # After it: a house idea needs a house brief.

    def test_a_house_idea_needs_a_house_brief_when_published_and_when_rebriefed(self):
        f = self.f
        self.on()
        self.start()
        f.reject("research brief that is for the house", "explore-publish", actor="v1", round="r1", token="r1",
                 ideas=[test_higher_bar.idea("a") | {"scale": "house"}])
        f.reject("research brief that is for the house", "explore-publish", actor="v1", round="r1", token="r1",
                 ideas=[test_higher_bar.idea("a", "field") | {"scale": "house"}])
        f.reject("scale must be great, small or house", "explore-publish", actor="v1", round="r1", token="r1",
                 ideas=[test_higher_bar.idea("a") | {"scale": "room"}])
        f.send("explore-publish", actor="v1", round="r1", token="r1", ideas=[house_idea("a")])
        self.assertEqual("house", self.ideas()["a"]["scale"])
        f.reject("research brief that is for the house", "idea-brief", actor="v2", idea="a",
                 brief=test_higher_bar.high("people"))
        self.assertEqual("house", self.ideas()["a"]["brief"]["for"])
        f.send("idea-brief", actor="v2", idea="a", brief=test_higher_bar.high("house"))
        self.assertEqual("v2", self.ideas()["a"]["brief"]["author"])

    def test_a_small_idea_may_still_carry_a_house_brief(self):
        f = self.f
        self.on()
        self.kept(test_higher_bar.idea("a", "house"))
        self.assertEqual(("small", "house"), (shelf.scale(self.ideas()["a"]), self.ideas()["a"]["brief"]["for"]))

    # The slot and the choice.

    def test_a_house_idea_is_kept_chosen_and_becomes_a_project_beside_great_and_small(self):
        f = self.f
        self.on()
        first = self.kept(house_idea("a"))
        self.assertTrue(shelf.grounded(f.state, self.ideas()["a"]))
        self.assertEqual(HOUR, shelf.cool(f.state, "house"), "a kept house idea waits one hour, like small")
        self.assertEqual(first + HOUR, shelf.vote_from(f.state, "a", first))
        self.occupy("great", "small")
        self.assertTrue(shelf.slot_free(f.state["shelf"], "house"))
        f.reject("hour", "choice-open", actor="v1", at=first + HOUR / 2, choice="c1", slot="house",
                 milestones=plans("a"))
        self.assertTrue(shelf.ready(f.state, "house", first + HOUR)["open"])
        f.send("choice-open", actor="v1", at=first + HOUR, choice="c1", slot="house", milestones=plans("a"))
        self.assertEqual(("house", ["a"]), (f.state["shelf"]["choices"]["c1"]["slot"],
                                             f.state["shelf"]["choices"]["c1"]["candidates"]))
        self.vote("c1", "a")
        project = f.state["shelf"]["projects"]["c1"]
        self.assertEqual(("active", "house", "One usable example"), (project["status"], project["slot"], project["milestone"]))
        self.assertNotIn("stage", project, "one milestone and a deadline, not the staged great mechanics")
        self.assertEqual(3, len(shelf.active_projects(f.state["shelf"])))
        self.assertFalse(shelf.slot_free(f.state["shelf"], "house"))
        self.assertEqual("c1", shelf.house_work(f.state))
        self.assertEqual("project", self.ideas()["a"]["status"])
        f.reject("house project slot is occupied", "choice-open", actor="v1", choice="c2", slot="house",
                 milestones=plans("a"))
        # It closes like a small project: the owner finishes it with a completed task.
        f.state["tasks"]["t1"] = {"status": "done", "artifacts": ["x"]}
        f.send("project-done", actor="v1", project="c1", evidence="t1")
        self.assertEqual("done", f.state["shelf"]["projects"]["c1"]["status"])
        self.assertTrue(shelf.slot_free(f.state["shelf"], "house"))
        self.assertIsNone(shelf.house_work(f.state))

    def test_a_house_choice_holds_only_house_ideas_and_the_others_never_hold_them(self):
        f = self.f
        self.on()
        first = self.kept(house_idea("h"))
        self.kept(test_higher_bar.idea("s"), actor="other", round_id="r2", checkers=("author", "v1", "v3"))
        self.kept(scaled("g", "great"), actor="other", round_id="r3", checkers=("author", "v1", "v3"))
        at = f.state["at"] + 7 * HOUR
        f.reject("plan for every frozen candidate", "choice-open", actor="v2", at=at, choice="c1", slot="house",
                 milestones=plans("h", "s"))
        f.reject("plan for every frozen candidate", "choice-open", actor="v2", at=at, choice="c1", slot="small",
                 milestones=plans("s", "h"))
        f.reject("plan for every frozen candidate", "choice-open", actor="v2", at=at, choice="c1", slot="great",
                 milestones={key: [{"milestone": "a"}, {"milestone": "b"}] for key in ("g", "h")})
        f.send("choice-open", actor="v2", at=at, choice="c1", slot="small", milestones=plans("s"))
        self.assertEqual(["s"], f.state["shelf"]["choices"]["c1"]["candidates"])
        self.vote("c1", None)
        f.send("choice-open", actor="v2", choice="c2", slot="house", milestones=plans("h"))
        self.assertEqual(["h"], f.state["shelf"]["choices"]["c2"]["candidates"])
        self.assertEqual("open", f.state["shelf"]["choices"]["c2"]["status"])
        self.assertEqual("shelved", self.ideas()["h"]["status"] if first else "")

    def test_only_house_ideas_means_a_small_choice_has_nothing_to_freeze(self):
        f = self.f
        self.on()
        self.kept(house_idea("h"))
        f.reject("kept idea of that scale", "choice-open", actor="v2", at=f.state["at"] + 7 * HOUR, choice="c1",
                 slot="small", milestones=plans("h"))
        f.reject("kept idea of that scale", "choice-open", actor="v2", at=f.state["at"] + 7 * HOUR, choice="c1",
                 slot="great", milestones=plans("h"))

    def test_a_choice_without_a_slot_never_takes_a_house_idea(self):
        f = self.f
        self.on()
        self.kept(house_idea("h"))
        self.kept(test_higher_bar.idea("s"), actor="other", round_id="r2", checkers=("author", "v1", "v3"))
        original = shelf.apply
        # An older selection rule (version 2) opens a choice without a slot and sees every shelved idea of the old kinds.
        candidate = copy.deepcopy(f.state)
        original(candidate, {"actor": "v2", "at": f.state["at"] + 7 * HOUR, "data": {
            "kind": "choice-open", "choice": "c1", "milestones": plans("s")}}, selection_version=2)
        self.assertEqual(["s"], candidate["shelf"]["choices"]["c1"]["candidates"])

    # Research and the bench.

    def test_a_full_shelf_of_outward_ideas_does_not_block_house_research(self):
        # On the day of the migration the shelf held its ten kept outward ideas. House ideas have a bench
        # of their own, so a short house bench still opens a round, and house ideas do not count to ten.
        def state(migrated, house=0):
            ideas = {f"s{n}": {"status": "shelved", "scale": "small" if n < 7 else "great"} for n in range(10)}
            ideas |= {f"h{n}": {"status": "shelved", "scale": "house"} for n in range(house)}
            scopes = [shelf.OPEN_RESEARCH, shelf.UNBACKED, shelf.FLOW, shelf.MOMENTUM] + ([shelf.HOUSE_WORK] * migrated)
            return {"maintenance": {"migrations": {scope: {"at": 1} for scope in scopes}},
                    "shelf": shelf.empty() | {"ideas": ideas, "research_at": 10 ** 9}}
        with patch.object(shelf, "grounded", lambda state, idea: True):
            before = state(False)
            self.assertEqual(10, shelf.shelf_load(before, before["shelf"]))
            self.assertFalse(shelf.research_open(before, before["shelf"], 10 ** 9 + 60, 3), "full, as before")
            after = state(True)
            self.assertEqual(["house"], shelf.thin(after, after["shelf"]))
            self.assertTrue(shelf.research_open(after, after["shelf"], 10 ** 9 + 60, 3))
            full = state(True, house=2)
            self.assertEqual(10, shelf.shelf_load(full, full["shelf"]), "house ideas are counted apart")
            self.assertEqual([], shelf.thin(full, full["shelf"]))
            self.assertFalse(shelf.research_open(full, full["shelf"], 10 ** 9 + 60, 3), "both benches full")

    def test_thin_reports_house_when_the_bench_is_short(self):
        f = self.f
        self.on()
        self.kept(house_idea("a"))
        whole = f.state["shelf"]
        self.assertIn("house", shelf.thin(f.state, whole), "one kept house idea is under the bench of two")
        self.assertTrue(shelf.research_open(f.state, whole, f.state["at"], 3))
        self.kept(house_idea("b"), actor="other", round_id="r2", checkers=("author", "v1", "v3"))
        self.assertNotIn("house", shelf.thin(f.state, f.state["shelf"]), "two kept house ideas fill that bench")
        self.occupy("great", "small", "house")
        self.assertNotIn("house", shelf.thin(f.state, f.state["shelf"]), "a full bench needs no research")
        self.assertEqual(["great", "small"], shelf.thin(f.state, f.state["shelf"]))

    # The page: it reads scale and slot as plain labels.

    def test_the_page_view_carries_a_house_idea_and_project_through(self):
        f = self.f
        self.on()
        first = self.kept(house_idea("a"))
        f.send("choice-open", actor="v1", at=first + HOUR, choice="c1", slot="house", milestones=plans("a"))
        self.vote("c1", "a")
        view = body.shelf_view(f.state)
        self.assertEqual("house", next(i for i in view["ideas"] if i["id"] == "a")["scale"])
        self.assertEqual("house", next(p for p in view["projects"] if p["id"] == "c1")["slot"])

    # Staffing: builders go to the active project with the fewest builders; a third is no different.

    def test_builders_are_spread_over_three_active_projects(self):
        deadline = 10 ** 12
        state = {"at": 100.0, "maintenance": {}, "tasks": {}, "life": {"runs": {}, "requests": {}},
                 "shelf": {"projects": {}}}
        for slot in ("great", "small", "house"):
            state["shelf"]["projects"]["p" + slot] = {"status": "active", "slot": slot, "deadline": deadline}
            state["tasks"]["t" + slot] = {"ready": True, "status": "open", "project": "p" + slot, "generation": 1,
                                          "until": 0, "owner": None}
        state["life"]["runs"] = {
            "r1": {"status": "active", "resident": "a", "task": "tgreat", "task_generation": 1, "started_at": 0},
            "r2": {"status": "active", "resident": "b", "task": "tsmall", "task_generation": 1, "started_at": 0}}
        for run in state["life"]["runs"].values():
            state["tasks"][run["task"]]["owner"] = run["resident"]
        picked = project_work.first(state, 100.0, ["thouse"], [])
        self.assertEqual({"task": "thouse", "task_generation": 1}, picked, "the unstaffed third project is next")
        state["life"]["runs"]["r3"] = {"status": "active", "resident": "c", "task": "thouse", "task_generation": 1,
                                       "started_at": 0}
        state["tasks"]["thouse"]["owner"] = "c"
        state["tasks"]["thouse2"] = dict(state["tasks"]["thouse"], owner=None)
        state["tasks"]["tgreat2"] = dict(state["tasks"]["tgreat"], owner=None)
        state["tasks"]["tgreat2"]["project"] = "pgreat"
        self.assertEqual({"task": "tgreat2", "task_generation": 1},
                         project_work.first(state, 100.0, ["thouse2", "tgreat2"], []),
                         "with one builder on each, the tie goes by deadline then project id")

    # Prompts.

    def active_work(self):
        f = self.f
        self.on()
        first = self.kept(house_idea("a"))
        f.send("choice-open", actor="v1", at=first + HOUR, choice="c1", slot="house",
               milestones={"a": {"milestone": "The front page opens on what the house is doing now", "seconds": 100}})
        self.vote("c1", "a")

    def test_house_focus_runs_advance_an_active_house_work(self):
        f = self.f
        self.active_work()
        for focus in ("improve", "room"):
            prompt = focus_prompt(f.state, focus)
            self.assertIn("advance the house work now under way instead of picking a separate small thing", prompt)
            self.assertIn("project c1", prompt)
            self.assertIn(self.ideas()["a"]["title"], prompt)
            self.assertIn("The front page opens on what the house is doing now", prompt)
            self.assertIn("--project c1 and --ready", prompt)
            self.assertIn("exactly as project builders do", prompt)
            self.assertNotIn("Pick one thing", prompt)
            self.assertNotIn("—", prompt)
        self.assertIn("docs/BUILDING.md", focus_prompt(f.state, "room"))
        self.assertNotIn("HOUSE WORK", focus_prompt(f.state, "tend"))

    def test_without_a_house_work_the_focus_text_stays_and_points_to_the_shelf(self):
        f = self.f
        for focus in ("improve", "room"):
            plain = focus_prompt(f.state, focus)
            self.assertNotIn("house idea", plain, "before the migration the text is as it was")
            self.assertTrue(plain.endswith(".\n"))
        self.on()
        for focus in ("improve", "room"):
            prompt = focus_prompt(f.state, focus)
            self.assertIn("bigger than one run, bring it to the shelf as a house idea instead of shrinking it", prompt)
            self.assertTrue(prompt.endswith(".\n"))
        self.assertIn("Pick one thing", focus_prompt(f.state, "improve"))
        self.assertIn("If a room is under construction, continue it.", focus_prompt(f.state, "room"))

    def test_a_task_of_the_house_work_is_told_what_it_belongs_to(self):
        f = self.f
        self.active_work()
        f.state["tasks"]["t9"] = {"project": "c1", "status": "open"}
        from house import course
        f.state["maintenance"]["migrations"][course.SCOPE] = {"at": 1}
        text = home.course_prompt(f.state, {"task": "t9"})
        self.assertIn("HOUSE WORK (c1)", text)
        self.assertIn("The front page opens on what the house is doing now", text)

    def test_the_council_is_told_a_house_choice_can_open(self):
        f = self.f
        self.on()
        self.kept(house_idea("a"))
        f.state["at"] += HOUR
        prompt = asked_prompt(f.state, "v2")
        self.assertIn("A HOUSE CHOICE CAN OPEN NOW", prompt)
        self.assertIn("slot house", prompt)
        self.assertIn("NO PROJECT FILLS THE GREAT OR THE SMALL SLOT", prompt)

    def test_an_explorer_is_told_what_a_house_idea_is(self):
        f = self.f
        self.on()
        self.kept(house_idea("a"))
        state = f.state
        state["life"] = {"runs": {"run1": {"agent": "codex", "model": "gpt-6.1-sol", "explore_generation": 0,
                                           "status": "active", "resident": "newbie"}}, "requests": {}, "rooms": {}}
        state["tasks"] = {}
        state["wake_policy"] = None
        stub = types.SimpleNamespace(record=types.SimpleNamespace(read=lambda: (state, [], 0)), focus=None,
                                     running={}, private=Path(tempfile.mkdtemp()))
        with tempfile.TemporaryDirectory() as folder, patch("house.home.active_prompt", lambda state: ""):
            prompt = home.Coordinator.prompt(stub, state, "run1", "newbie", Path(folder), Path(folder) / "client", None)
        self.assertIn("Bring a house idea", prompt)
        for words in ("a change to Emberhall itself that takes days", "a visitor or a resident would notice",
                      "a new room, a rethought front page, a new ability for residents or a different look and feel",
                      "not another control, filter or paging link on an existing room", "seq:NUMBER or a path"):
            self.assertIn(words, prompt)
        for words in ("things to make sessions more efficient for everyone", "weighing the same as the others",
                      "tools other residents can use or skills", "docs/skills/README.md",
                      "a resident other than its builder has used it"):
            self.assertIn(words, prompt)
        self.assertIn("Bring a great idea", prompt)
        self.assertIn("Bring a small idea", prompt, "the other short benches are still asked for")
        self.assertLess(prompt.index("Bring a small idea"), prompt.index("Bring a house idea"))

    def test_the_handbook_and_orders_say_so(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        handbook = " ".join((root / "docs/SHELF.md").read_text().split())
        self.assertIn("upgrade-20261118-house-work", handbook)
        self.assertIn("never any 'new' work happening in the house", handbook)
        orders = (root / "docs/STEWARD_ORDERS.md").read_text()
        self.assertIn("upgrade-20261118-house-work", orders)
        self.assertIn("its own project slot", " ".join((root / "docs/WISHES.md").read_text().split()))


if __name__ == "__main__":
    unittest.main()
