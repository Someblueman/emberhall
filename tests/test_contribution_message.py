"""The coordinator's end-of-run commit names the work the resident finished."""
from pathlib import Path
import tempfile
import unittest

from house.home_work import (FALLBACK_MESSAGE, contribution, contribution_message, finished_titles, git)


def event(op, actor, **data):
    return {"op": op, "actor": actor, "data": data}


class ContributionMessageTests(unittest.TestCase):
    def test_titles_come_from_this_launch_and_this_resident_only(self):
        state = {"tasks": {"a": {"title": "Prove  the\nfirst case"}, "b": {"title": "Check the second"},
                           "c": {"title": "Someone else's"}, "d": {"title": "Before launch"}}}
        events = [event("finish", "r1", task="d"),                       # sequence 1: before launch
                  event("claim", "r1", task="a"),                        # 2
                  event("finish", "r1", task="a"),                       # 3
                  event("finish", "r2", task="c"),                       # 4: another resident
                  event("finish", "r1", task="b"),                       # 5
                  event("finish", "r1", task="a"),                       # 6: repeat is listed once
                  event("finish", "r1", task="missing")]                 # 7: unknown task keeps its id
        run = {"resident": "r1", "launched_sequence": 1}
        self.assertEqual(finished_titles(state, events, run),
                         ["Prove the first case", "Check the second", "missing"])
        self.assertEqual(finished_titles(state, events, {**run, "ended_sequence": 5}), ["Prove the first case"])
        self.assertEqual(finished_titles(state, events, {"resident": "r1"}), [])

    def test_distinct_tasks_with_one_title_and_unsafe_titles(self):
        state = {"tasks": {"a": {"title": "Same"}, "b": {"title": "Same"}, "c": {"title": "  \n "},
                           "d": {"title": "Bad\x00title"}}}
        events = [event("wake", "r1")] + [event("finish", "r1", task=k) for k in "abcd"]
        titles = finished_titles(state, events, {"resident": "r1", "launched_sequence": 1})
        self.assertEqual(titles, ["Same", "Same", "c", "Bad title"])
        self.assertNotIn("\x00", contribution_message(["x\x00y", "z"]))
        self.assertEqual(contribution_message(["\x00", " "]), FALLBACK_MESSAGE)

    def test_message_shapes(self):
        self.assertEqual(contribution_message([]), FALLBACK_MESSAGE)
        self.assertEqual(contribution_message(["Only one"]), "Only one")
        self.assertEqual(contribution_message(["First", "Second", "Third"]),
                         "First\n\nAlso finished in this run:\n- Second\n- Third\n")
        long = contribution_message(["x" * 100]).split("\n", 1)[0]
        self.assertEqual(len(long), 72)
        self.assertTrue(long.endswith("..."))

    def test_uncommitted_room_work_is_committed_under_the_given_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            room = Path(tmp) / "room"; room.mkdir()
            git(room, "init", "--quiet")
            (room / "a.txt").write_text("base\n")
            git(room, "add", "a.txt")
            git(room, "-c", "commit.gpgsign=false", "-c", "user.name=T", "-c", "user.email=t@local",
                "commit", "--quiet", "-m", "base")
            base = git(room, "rev-parse", "HEAD")
            (room / "a.txt").write_text("changed\n")
            (room / "b.txt").write_text("new\n")
            report = contribution(room, base, Path(tmp) / "out.json", journal_artifacts={},
                                  message=contribution_message(["Record the result", "Add a check"]))
            self.assertEqual(report["status"], "pending-review")
            self.assertEqual(sorted(report["paths"]), ["a.txt", "b.txt"])
            self.assertEqual(git(room, "rev-parse", "HEAD"), report["commit"])
            self.assertEqual(git(room, "log", "-1", "--format=%s", report["commit"]), "Record the result")
            self.assertIn("- Add a check", git(room, "log", "-1", "--format=%b", report["commit"]))

    def test_default_message_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            room = Path(tmp) / "room"; room.mkdir()
            git(room, "init", "--quiet")
            git(room, "-c", "commit.gpgsign=false", "-c", "user.name=T", "-c", "user.email=t@local",
                "commit", "--quiet", "--allow-empty", "-m", "base")
            base = git(room, "rev-parse", "HEAD")
            (room / "c.txt").write_text("c\n")
            report = contribution(room, base, Path(tmp) / "out.json", journal_artifacts={})
            self.assertEqual(git(room, "log", "-1", "--format=%s", report["commit"]), FALLBACK_MESSAGE)


if __name__ == "__main__":
    unittest.main()
