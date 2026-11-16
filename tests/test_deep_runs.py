"""Deep runs (Steward decision, 16 November): a research floor and a keep-going answer to early sleep."""
import copy
import json
import unittest
from unittest.mock import patch

from house import mailbox, shelf, stay
from house.home import deep_prompt
from tests import test_shelf
from tests.test_mailbox import MailboxCase
from tests.test_open_research import PART

MINUTE = 60


def cited(key, pages=4):
    return test_shelf.idea(key) | {
        "sources": [f"https://example.org/{key}/{n}" for n in range(pages)],
        "brief": {name: PART for name in shelf.BRIEF_FIELDS}}


class ResearchFloorTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()
        self.f.state["maintenance"] = {"migrations": {shelf.OPEN_RESEARCH: {"at": 1000}}}

    def deep(self):
        self.f.state["maintenance"]["migrations"][shelf.DEEP_RUNS] = {"at": 1000}

    def test_before_the_decision_a_round_may_publish_at_once_with_one_source(self):
        f = self.f
        f.send("explore-start", at=2000, round="r1", expect=0, token="r1", seconds=100)
        quick = [cited("a", pages=1), cited("b", pages=1)]
        f.send("explore-publish", at=2001, round="r1", token="r1", ideas=quick)
        self.assertEqual("published", f.state["shelf"]["rounds"]["r1"]["status"])

    def test_a_round_runs_half_an_hour_and_cites_four_pages_an_idea(self):
        f = self.f
        self.deep()
        f.reject("lease of at least 3600 seconds", "explore-start", at=2000, round="r1", expect=0,
                 token="r1", seconds=3599)
        f.send("explore-start", at=2000, round="r1", expect=0, token="r1", seconds=3600)
        ideas = [cited("a"), cited("b")]
        f.reject("has run 10 of its 30 minutes minimum", "explore-publish", at=2000 + 10 * MINUTE,
                 round="r1", token="r1", ideas=ideas)
        f.reject("has run 29 of its 30", "explore-publish", at=2000 + 30 * MINUTE - 1,
                 round="r1", token="r1", ideas=ideas)
        late = 2000 + 30 * MINUTE
        f.reject("at least four different pages", "explore-publish", at=late, round="r1", token="r1",
                 ideas=[cited("a", pages=3), cited("b")])
        repeated = cited("a"); repeated["sources"] = repeated["sources"][:2] * 2
        f.reject("at least four different pages", "explore-publish", at=late, round="r1", token="r1",
                 ideas=[repeated, cited("b")])
        f.send("explore-publish", at=late, round="r1", token="r1", ideas=ideas)
        self.assertEqual(["a", "b"], f.state["shelf"]["rounds"]["r1"]["ideas"])
        self.assertEqual(4, len(f.state["shelf"]["ideas"]["a"]["sources"]))

    def test_giving_a_round_up_needs_no_floor(self):
        f = self.f
        self.deep()
        f.send("explore-start", at=2000, round="r1", expect=0, token="r1", seconds=3600)
        f.send("explore-release", at=2060, round="r1", token="r1", reason="The reading supported neither idea.")
        self.assertEqual("released", f.state["shelf"]["rounds"]["r1"]["status"])

    def test_refusals_fit_the_short_error_a_resident_is_shown(self):
        f = self.f
        self.deep()
        f.send("explore-start", at=2000, round="r1", expect=0, token="r1", seconds=3600)
        with self.assertRaises(ValueError) as caught:
            f.send("explore-publish", at=2100, round="r1", token="r1", ideas=[cited("a"), cited("b")])
        self.assertLessEqual(len(str(caught.exception)), 300)
        self.assertIn("same round and token", str(caught.exception))


def house(*, deep=True, model="gpt-6.1-sol", task=None, project_status="active"):
    """A run 600 seconds old; sequence 3 is its run-start, later events are its own."""
    state = {"maintenance": {"migrations": {shelf.DEEP_RUNS: {"at": 1}} if deep else {}},
             "life": {"runs": {"run1": {"status": "active", "resident": "builder", "agent": "codex",
                                        "model": model, "started_at": 10_000, "started_sequence": 3}}},
             "tasks": {"slice": {"project": "skein", "status": "open"},
                       "chore": {"status": "open"},
                       "check": {"project": "skein", "helper": "review", "status": "open"}},
             "shelf": {"explorer": None, "rounds": {}, "projects": {"skein": {
                 "status": project_status, "milestone": "A reader can   open the packet\nand follow it."}}}}
    if task:
        state["life"]["runs"]["run1"].update(task=task)
    return state


def claimed(task, actor="builder"):
    return [{"op": "say", "actor": "x", "data": {}}] * 3 + [{"op": "claim", "actor": actor, "data": {"task": task}}]


class StayTests(unittest.TestCase):
    NOW = 10_000 + 10 * MINUTE

    def answer(self, state, events=(), note="Done for now.", now=None, refused=0):
        return stay.refusal(state, list(events), "run1", note, self.NOW if now is None else now, refused)

    def test_nothing_is_held_before_the_decision_or_outside_deep_work(self):
        self.assertIsNone(self.answer(house(deep=False, task="slice")))
        self.assertIsNone(self.answer(house()))
        self.assertIsNone(self.answer(house(task="chore")))
        self.assertIsNone(self.answer(house(), claimed("chore")))
        self.assertIsNone(self.answer(house(task="check")), "a helper-marked review stays short")
        self.assertIsNone(self.answer(house(task="slice", model="gpt-6-luna")), "helpers are never held")
        self.assertIsNone(self.answer(house(task="slice", project_status="done")))
        self.assertIsNone(self.answer(house(), claimed("slice", actor="someone-else")))
        self.assertIsNone(stay.refusal(house(task="slice"), [], "unknown-run", "", self.NOW, 0))

    def test_a_building_stretch_is_asked_to_keep_going(self):
        for state, events in ((house(task="slice"), []), (house(), claimed("slice"))):
            text = self.answer(state, events)
            self.assertIn("used 10 of its 45 minutes", text)
            self.assertIn("project skein", text)
            self.assertIn("A reader can open the packet and follow it.", text)
            self.assertIn("BLOCKED:", text)
            self.assertIn("new request ID", text)
            self.assertLessEqual(len(text), 1200)

    def test_a_builder_is_never_trapped(self):
        state = house(task="slice")
        self.assertIsNone(self.answer(state, note="BLOCKED: the page needs a real browser; need raised."))
        self.assertIsNone(self.answer(state, now=10_000 + stay.BUDGET_SECONDS))
        self.assertIsNotNone(self.answer(state, now=10_000 + stay.BUDGET_SECONDS - 1))
        self.assertIsNotNone(self.answer(state, refused=stay.REFUSALS - 1))
        self.assertIsNone(self.answer(state, refused=stay.REFUSALS))

    def test_an_explorer_holding_a_round_publishes_or_gives_it_up_first(self):
        state = house()
        state["shelf"].update(explorer="r1", rounds={"r1": {
            "owner": "builder", "status": "active", "started_at": 10_000 + 4 * MINUTE}})
        text = self.answer(state, note="BLOCKED: tired")
        self.assertIn("research round r1, 6 minutes old", text)
        self.assertIn("explore-release", text)
        self.assertIn("30-minute", text)
        self.assertEqual({"kind": "research", "round": "r1", "started_at": 10_000 + 4 * MINUTE},
                         stay.stretch(state, [], "run1"))
        state["shelf"]["rounds"]["r1"]["owner"] = "another"
        self.assertIsNone(self.answer(state))
        state["shelf"]["rounds"]["r1"].update(owner="builder", status="published")
        self.assertIsNone(self.answer(state))

    def test_a_long_milestone_is_shortened(self):
        state = house(task="slice")
        state["shelf"]["projects"]["skein"]["milestone"] = "word " * 400
        self.assertLessEqual(len(self.answer(state)), 1200)

    def test_prompt_explains_the_stretch_only_once_installed(self):
        self.assertEqual("", deep_prompt(house(deep=False, task="slice"), {"task": "slice"}))
        general = deep_prompt(house(), {})
        self.assertIn("DEEP RUNS", general)
        self.assertIn("about 45 minutes", general)
        self.assertIn("BLOCKED:", general)
        self.assertIn("slice of the milestone", general)
        self.assertNotIn("This run is a building stretch on project", general)
        self.assertIn("This run is a building stretch on project skein", deep_prompt(house(), {"task": "slice"}))
        self.assertNotIn("This run is a building stretch on project", deep_prompt(house(), {"task": "check"}))


class StayMailboxTests(MailboxCase):
    def sleep(self, request, note="Handoff: nothing left."):
        through = self.record.read()[0]["sequence"]
        return self.start("sleep", "--as", self.resident, "--through", str(through), "--note", note,
                          "--request", request)

    def test_an_early_sleep_is_answered_not_recorded_and_a_later_one_goes_through(self):
        self.arrive()
        said = "Not yet. " + "Keep building toward the milestone. " * 20
        answers = iter([said, None])
        with patch("house.stay.refusal", side_effect=lambda *args: next(answers)) as asked:
            before = self.record.read()[0]["sequence"]
            errors = self.collect(self.sleep("sleep-1"), success=False)
            self.assertIn(said.strip(), errors)
            state = self.record.read()[0]
            self.assertEqual(before, state["sequence"], "a refused sleep is never a journal event")
            self.assertTrue(state["residents"][self.resident]["awake"])
            log = json.loads((self.private / self.run / "mailbox" / stay.LOG).read_text())
            self.assertEqual(1, log["refused"])
            self.assertEqual(0, asked.call_args_list[0].args[-1])
            self.collect(self.sleep("sleep-2"))
            self.assertEqual(1, asked.call_args_list[1].args[-1], "the second request knows it was refused once")
        self.assertFalse(self.record.read()[0]["residents"][self.resident]["awake"])

    def test_ordinary_runs_sleep_as_before(self):
        self.arrive()
        self.collect(self.sleep("sleep-1"))
        self.assertFalse(self.record.read()[0]["residents"][self.resident]["awake"])
        self.assertFalse((self.private / self.run / "mailbox" / stay.LOG).exists())


if __name__ == "__main__":
    unittest.main()
