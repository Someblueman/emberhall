"""Project deadlines and missing residents must never consume slots forever."""
import copy
import unittest

from house import shelf
from tests import test_shelf


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_shelf.ShelfTests()
        self.fixture.setUp()
        self.fixture.publish()
        self.fixture.choose()

    def test_one_extension_three_nonowner_votes_then_forced_retirement(self):
        f = self.fixture
        deadline = f.state["shelf"]["projects"]["choice1"]["deadline"]
        f.reject("not arrived", "project-extend-vote", actor="v1", project="choice1", reason="Needs work")
        f.reject("owner cannot", "project-extend-vote", actor="other", at=deadline, project="choice1", reason="Mine")
        f.send("project-extend-vote", actor="v1", at=deadline, project="choice1", reason="Useful progress")
        f.reject("already voted", "project-extend-vote", actor="v1", project="choice1", reason="Again")
        f.state["residents"]["v1"]["awake"] = False
        for voter in ["v2", "v3"]:
            f.send("project-extend-vote", actor=voter, project="choice1", reason="Useful progress")
        project = f.state["shelf"]["projects"]["choice1"]
        self.assertTrue(project["extended"])
        self.assertEqual(f.state["at"] + 7 * shelf.DAY, project["deadline"])
        f.reject("only once", "project-extend-vote", actor="author", at=project["deadline"], project="choice1", reason="Again")
        shelf.advance(f.state, project["deadline"] + 7 * shelf.DAY, 100)
        self.assertEqual("dropped", project["status"])
        self.assertEqual("no timely second-deadline decision", project["lesson"])
        self.assertEqual([], shelf.active_projects(f.state["shelf"]))

    def test_long_sleep_drops_both_slots_without_any_owner_cooperation(self):
        f = self.fixture
        f.choose("choice2", votes=("b", "b", "c"))
        for person in f.state["residents"].values():
            person["awake"] = False
        before = copy.deepcopy(f.state)
        at = max(p["deadline"] for p in f.state["shelf"]["projects"].values()) + 7 * shelf.DAY
        shelf.advance(f.state, at, 100)
        self.assertEqual([], shelf.active_projects(f.state["shelf"]))
        for project in f.state["shelf"]["projects"].values():
            self.assertEqual("no timely first-deadline decision", project["lesson"])
        # Replay at the same observation preserves the exact first resolution.
        result = copy.deepcopy(f.state)
        shelf.advance(f.state, at + 100, 101)
        self.assertEqual(result, f.state)
        shelf.advance(before, at, 100)
        self.assertEqual(before, result)

    def test_done_requires_immutable_task_evidence_and_frees_slot(self):
        f = self.fixture
        f.reject("immutable", "project-done", actor="other", project="choice1", evidence="It seems done")
        f.state["tasks"]["milestone"] = {"status": "done", "artifacts": {"demo.txt": {"sha256": "frozen"}}}
        f.send("project-done", actor="other", project="choice1", evidence="milestone")
        self.assertEqual("done", f.state["shelf"]["projects"]["choice1"]["status"])
        self.assertEqual("milestone", f.state["shelf"]["projects"]["choice1"]["evidence"])
        f.choose("choice2", votes=("b", "b", "c"))
        self.assertEqual(["choice2"], shelf.active_projects(f.state["shelf"]))

    def test_drop_requires_lesson_and_overdue_decision_cannot_resurrect(self):
        f = self.fixture
        f.reject("empty lesson", "project-drop", project="choice1", lesson=" ")
        f.reject("before its deadline", "project-drop", actor="v1", project="choice1", lesson="An unsolicited cancellation")
        deadline = f.state["shelf"]["projects"]["choice1"]["deadline"]
        f.send("project-drop", actor="v1", at=deadline, project="choice1", lesson="Prototype showed no useful advantage")
        self.assertEqual("dropped", f.state["shelf"]["projects"]["choice1"]["status"])
        f.reject("not active", "project-extend-vote", actor="v2", project="choice1", reason="Revive")
        f.send("idea-return", idea="a", changed="A different design addresses the prototype failure")
        self.assertEqual("shelved", f.state["shelf"]["ideas"]["a"]["status"])
        self.assertEqual("dropped", f.state["shelf"]["projects"]["choice1"]["status"])
        self.assertEqual("Prototype showed no useful advantage",
                         f.state["shelf"]["ideas"]["a"]["history"][-2]["lesson"])
        f.choose("choice2", votes=("b", "b", "c"))
        deadline = f.state["shelf"]["projects"]["choice2"]["deadline"]
        f.reject("not active", "project-extend-vote", actor="v2", at=deadline + 7 * shelf.DAY,
                 project="choice2", reason="Too late")


if __name__ == "__main__":
    unittest.main()
