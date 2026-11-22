"""The offline summary preserves pending work and does not turn history into authority."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.status_brief import summarize


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "status_brief.py"


def snapshot():
    return {
        "house_id": "example", "name": "Test house", "sequence": 50, "rule_revision": "current",
        "residents": {"fern": {"name": "Fern", "awake": True, "cursor": 20}},
        "tasks": {
            "ready": {"status": "open", "ready": True, "generation": 0, "plain": "Build the next piece."},
            "held": {"status": "claimed", "owner": "another", "generation": 1, "available": False},
            "expired": {"status": "claimed", "owner": "old", "generation": 2, "available": True},
            "unqueued": {"status": "open", "ready": False},
            "finished-secret": {"status": "done", "result": "DO NOT PRINT HISTORY"},
        },
        "shelf": {"record": {
            "ideas": {},
            "projects": {
                "research": {"status": "active", "slot": "great", "owner": "another", "stage": 1,
                             "milestones": [{}, {}, {}], "milestone": "Prove the result."},
                "old-project": {"status": "done"}},
            "choices": {"vote": {"status": "open", "candidates": ["one", "two"], "votes": {"fern": {}}},
                        "old-choice": {"status": "closed"}},
        }},
        "life": {"requests": {"help": {"status": "assigned", "reason": "Review the build."},
                              "old-help": {"status": "resolved"}}},
        "proposals": {
            "old-pin": {"status": "pending", "base": "earlier", "title": "Old source"},
            "new-pin": {"status": "pending", "base": "current", "title": "New source"},
            "enacted-secret": {"status": "enacted"}},
    }


class StatusBriefTests(unittest.TestCase):
    def test_current_work_history_and_authority_remain_distinct(self):
        data = snapshot()
        before = copy.deepcopy(data)
        result = summarize(data, resident="fern")
        for expected in ("saved status at sequence 50", "saved cursor 20; 30 later events",
                         "research [great; owner another] stage 2/3", "Ready open tasks (1)",
                         "Recorded claims (2)", "available at capture: True", "Unqueued open tasks omitted: 1",
                         "Open project choices (1)", "Unresolved help requests (1)",
                         "base differs", "No enactment gate is assessed"):
            self.assertIn(expected, result)
        for hidden in ("finished-secret", "DO NOT PRINT HISTORY", "old-project", "old-choice",
                       "old-help", "enacted-secret"):
            self.assertNotIn(hidden, result)
        self.assertLess(result.index("new-pin"), result.index("old-pin"))
        self.assertLess(result.index("Open project choices"), result.index("Active projects"))
        self.assertIn("your vote is recorded", result)
        self.assertEqual(data, before)

    def test_unvoted_choices_come_first_and_authorship_is_not_eligibility(self):
        data = snapshot()
        shelf = data["shelf"]["record"]
        shelf["choices"]["z-waiting"] = {"status": "open", "candidates": ["own"], "votes": {}}
        shelf["ideas"]["own"] = {"status": "shelved", "author": "other",
                                  "brief": {"author": "fern"}}
        result = summarize(data, resident="fern", limit=1)
        self.assertIn("z-waiting: candidates own; 0 recorded votes; no vote recorded by you", result)
        self.assertIn("you wrote a candidate or its current brief", result)
        self.assertIn("Vote eligibility is not assessed", result)
        self.assertNotIn("vote: candidates", result)
        shelf["ideas"]["own"] = {"status": "shelved", "author": "fern"}
        self.assertIn("you wrote a candidate", summarize(data, resident="fern"))
        self.assertNotIn("recorded by you", summarize(data))
        self.assertNotIn("your vote", summarize(data))

    def test_explicit_limits_and_printable_single_lines(self):
        data = snapshot()
        data["tasks"]["ready"]["plain"] = "A\nB\x1b" + "x" * 400
        result = summarize(data, limit=1)
        self.assertIn("Recorded claims (2)", result)
        self.assertIn("1 more omitted", result)
        self.assertIn("A B?", result)
        self.assertIn("…", result)
        self.assertNotIn("\x1b", result)

    def test_bad_or_incomplete_input_never_becomes_an_empty_success(self):
        invalid = [None, [], {}, {"source": {"sequence": 50}, "tasks": {}}]
        for field, value in [("sequence", True), ("tasks", []), ("shelf", {}),
                             ("proposals", {"bad": {}}), ("life", {"requests": []})]:
            data = snapshot()
            data[field] = value
            invalid.append(data)
        missing_ideas = snapshot()
        del missing_ideas["shelf"]["record"]["ideas"]
        invalid.append(missing_ideas)
        for field, value in [("votes", []), ("votes", {"fern": None}), ("candidates", "one")]:
            data = snapshot()
            data["shelf"]["record"]["choices"]["vote"][field] = value
            invalid.append(data)
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(ValueError):
                summarize(data)
        for limit in (0, 51):
            with self.assertRaises(ValueError):
                summarize(snapshot(), limit=limit)
        with self.assertRaisesRegex(ValueError, "resident not in snapshot"):
            summarize(snapshot(), resident="absent")

    def test_shelf_uses_current_brief_and_names_resident_relationship(self):
        data = snapshot()
        ideas = data["shelf"]["record"]["ideas"]
        ideas["waiting"] = {"status": "shelved", "scale": "great", "title": "A result",
                            "author": "writer", "brief": {"sequence": 40, "author": "editor"},
                            "seconds": [{"brief": 39, "author": "fern", "finding": "OLD SECRET"},
                                        {"brief": 40, "author": "other", "finding": "NEW SECRET"}]}
        ideas["hidden"] = {"status": "graveyard", "title": "HIDDEN HISTORY"}
        ideas["unbriefed"] = {"status": "shelved", "author": "fern"}
        result = summarize(data, resident="fern")
        for expected in ("Shelved ideas (2)", "brief 40; recorded keeps 1",
                         "no keep by you on this brief", "no brief; you wrote the idea or brief",
                         "Selection eligibility and waiting periods are not assessed"):
            self.assertIn(expected, result)
        for hidden in ("HIDDEN HISTORY", "OLD SECRET", "NEW SECRET"):
            self.assertNotIn(hidden, result)
        ideas["waiting"]["seconds"].append({"brief": 40, "author": "fern"})
        self.assertIn("recorded keeps 2; you kept this brief", summarize(data, resident="fern"))
        ideas["waiting"]["brief"]["author"] = "fern"
        self.assertIn("recorded keeps 2; you wrote the idea or brief", summarize(data, resident="fern"))
        self.assertIn("1 more omitted", summarize(data, limit=1))
        self.assertNotIn("no keep by you", summarize(data))
        for bad in (None, {}, [None], [{"brief": 40}]):
            ideas["waiting"]["seconds"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                summarize(data)

    def test_file_and_stdin_cli_agree_and_malformed_input_fails(self):
        text = json.dumps(snapshot())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            path.write_text(text)
            file_result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--resident", "fern"],
                                         capture_output=True, text=True)
        stdin_result = subprocess.run([sys.executable, str(SCRIPT), "-", "--resident", "fern"],
                                      input=text, capture_output=True, text=True)
        self.assertEqual(file_result.returncode, 0, file_result.stderr)
        self.assertEqual(file_result.stdout, stdin_result.stdout)
        self.assertEqual(stdin_result.returncode, 0, stdin_result.stderr)
        bad = subprocess.run([sys.executable, str(SCRIPT), "-"], input='{"sequence":',
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")
        self.assertIn("Cannot summarize status", bad.stderr)


if __name__ == "__main__":
    unittest.main()
