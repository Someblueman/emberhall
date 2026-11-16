"""Plain words (Steward, 16 November): a thread says what a person will notice, and the page lists the day's work."""
import copy

from house import body, shelf
from house.home import asked_prompt
from house.model import apply_event
from tests.support import HouseCase

PLAIN = "A comment that looks empty on the page is also treated as empty when it is saved."


class PlainWorkTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.state = copy.deepcopy(self.record.read()[0])
        self.number = 0

    def task(self, state, **data):
        self.number += 1
        event = {"id": f"plain-{self.number}", "op": "task", "actor": "alice", "at": state["at"] + 1,
                 "data": {"task": f"t{self.number}", "title": "Keep editor Unicode body validation aligned",
                          "description": "Bounded", **data}}
        return apply_event(copy.deepcopy(state), event)

    def installed(self):
        state = copy.deepcopy(self.state)
        state.setdefault("maintenance", {}).setdefault("migrations", {}).update(
            {shelf.WHO_ASKED: {"at": state["at"]}, shelf.SECOND_LOOK: {"at": state["at"]}})
        return state

    def test_before_the_decision_a_task_has_no_plain_line(self):
        self.assertNotIn("plain", self.task(self.state)["tasks"]["t1"])
        with self.assertRaisesRegex(ValueError, "not enabled yet"):
            self.task(self.state, plain=PLAIN)

    def test_a_new_task_says_in_everyday_words_what_a_person_will_notice(self):
        state = self.installed()
        for bad in ({}, {"plain": "Fix it."}, {"plain": "   " * 20}, {"plain": 5}, {"plain": "x" * 201}):
            with self.assertRaises(ValueError, msg=bad):
                self.task(state, **bad)
        with self.assertRaisesRegex(ValueError, "a task needs --plain: one everyday sentence"):
            self.task(state)
        after = self.task(state, plain=PLAIN)
        task = after["tasks"][f"t{self.number}"]
        self.assertEqual(PLAIN, task["plain"])
        self.assertEqual(PLAIN, body.public_task("t", task)["plain"])
        self.assertNotIn("plain", body.public_task("t", {k: v for k, v in task.items() if k != "plain"}))
        self.assertIn("`task` now requires --plain", asked_prompt(state | {"shelf": {}}, "alice"))
        self.assertNotIn("--plain", asked_prompt(self.state | {"shelf": {}, "maintenance": {"migrations": {
            shelf.WHO_ASKED: {"at": 1}}}}, "alice"))

    def test_the_page_lists_what_was_finished_in_the_last_day_and_which_were_checks(self):
        day = body.WORK_SECONDS
        def done(seq, title, **more):
            return {"title": title, "status": "done", "owner": "alice", "until": 0, "generation": 1,
                    "finished_at": seq, **more}
        state = {"tasks": {
            "old": done(1, "Built long ago"),
            "made": done(2, "Make the diff table fit a phone", plain=PLAIN, project="skein"),
            "marked": done(3, "Look again at the table", helper="review"),
            "named": done(4, "Independently inspect the packet", project="skein"),
            "open": {"title": "Not finished", "status": "open", "owner": None, "until": 0, "generation": 0},
            "unknown": done(99, "Finished at a moment this replay never saw")}}
        times = {1: 1000, 2: 1000 + day, 3: 1500 + day, 4: 2000 + day}
        work = body.work_view(state, times, 2000 + day)
        self.assertEqual(["made", "marked", "named"], [item["id"] for item in work])
        self.assertEqual([False, True, True], [item["check"] for item in work])
        self.assertEqual((PLAIN, "skein", "alice", 1000 + day),
                         tuple(work[0][k] for k in ("plain", "project", "owner", "at")))
        self.assertNotIn("plain", work[1])
        state["tasks"] |= {f"many{n}": done(2, "Another piece of work") for n in range(body.WORK_LIMIT + 5)}
        self.assertEqual(body.WORK_LIMIT, len(body.work_view(state, times, 2000 + day)))

    def test_the_public_record_carries_the_work_only_after_the_decision(self):
        self.record.append("task", "alice", {"task": "work", "title": "Useful work", "description": "Bounded"})
        frame = body.export(self.record)["frames"][-1]
        self.assertNotIn("work", frame)
        self.assertEqual("Useful work", frame["event"]["title"])
