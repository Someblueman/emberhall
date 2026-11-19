"""Exercise the portable cohort reader through its command line and journal page format."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.support import SOURCE

READER = SOURCE / "projects/kind-craft-and-routing/cohort.py"


class CohortTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.events = []

    def event(self, op, data, actor="watch-keeper", request=None):
        seq = len(self.events) + 1
        self.events.append({"sequence": seq, "op": op, "data": data, "actor": actor, "id": request or str(seq)})
        return seq

    def start(self, run, task, *, help_id=None):
        binding = {"help_request": help_id} if help_id else {"task": task, "task_generation": 0}
        return self.event("life", {"kind": "run-start", "agent": "codex", "run": run, **binding})

    def assign(self, run, task, *, help_id=None, tied=("codex",), actor="watch-keeper", **changes):
        data = {"run": run, "lane": "work", "reason": "balanced", "helper": False, "help_request": help_id}
        if tied is not None:
            data.update(task=task, task_generation=0, tied_families=list(tied))
        data.update(changes)
        return self.event("say", {"text": "house-assignment-v1 " + json.dumps(data)},
                          actor, f"home-{run}-assignment")

    def finish(self, run, outcome):
        return self.event("life", {"kind": "run-finish", "run": run, "outcome": outcome})

    def offer(self, run, task, outcome="success", **kwargs):
        seq = self.start(run, task)
        self.assign(run, task, **kwargs)
        if outcome:
            self.finish(run, outcome)
        return seq

    def read(self, *, after=0, chunks=None, error=None):
        paths = []
        for i, (begin, end) in enumerate(chunks or [(0, len(self.events))]):
            path = Path(self.directory.name) / f"page-{i}.json"
            path.write_text(json.dumps({"events": self.events[begin:end], "latest": len(self.events),
                                        "through": end, "has_more": end < len(self.events)}))
            paths.append(path)
        command = [sys.executable, str(READER), "--after", str(after), *paths]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if error:
            self.assertEqual(2, result.returncode)
            self.assertIn(error, result.stderr)
            self.assertEqual("", result.stdout)
        else:
            self.assertEqual(0, result.returncode, result.stderr)
            return json.loads(result.stdout)

    def test_quota_retries_and_duplicate_tasks_do_not_fill_twenty_places(self):
        first = self.offer("a", "one", "quota")
        retry = self.offer("b", "one", tied=("codex", "muse"))
        self.offer("c", "one", "failed")
        for i in range(2, 22):
            self.offer(str(i), f"task-{i}", "interrupted")
        report = self.read(chunks=[(0, 11), (11, len(self.events))])
        self.assertEqual((20, 1, 19, 1, 2), (report["enrolled_tasks"], report["genuine_ties"],
                         report["singletons"], report["quota_exits"], report["repeat_offers"]))
        self.assertEqual(retry, report["enrolled_starts"][0])
        self.assertEqual(first, report["offers"][1]["repeat_of"])
        self.assertEqual(report["offers"][-2]["start"], report["twentieth_start"])
        self.assertEqual("after cutoff", report["offers"][-1]["disposition"])

    def test_pending_early_offer_waits_for_its_exit_and_trial_follows_start_order(self):
        early = self.offer("early", "one", None)
        later = self.offer("later", "two")
        pending = self.read()
        self.assertEqual(([], early, 1), (pending["enrolled_starts"], pending["first_unresolved"],
                                         pending["pending_exits"]))
        self.finish("early", "quota")
        self.assertEqual([later], self.read()["enrolled_starts"])
        self.events[-1]["data"]["outcome"] = "success"
        self.assertEqual([early, later], self.read()["enrolled_starts"])

    def test_help_before_interval_can_be_resolved_using_an_earlier_page(self):
        self.event("life", {"kind": "help", "request": "request", "task": "one"}, "alice")
        start = self.start("a", "one", help_id="request")
        self.assign("a", "one", help_id="request")
        self.finish("a", "success")
        self.assertEqual(start, self.read(after=1, chunks=[(1, 4)])["first_unresolved"])
        self.assertEqual([start], self.read(after=1, chunks=[(0, 1), (1, 4)])["enrolled_starts"])

    def test_twentieth_place_waits_for_an_earlier_run_but_later_runs_cannot_move_it(self):
        for i in range(19):
            self.offer(str(i), f"task-{i}")
        open_start = self.offer("open", "pending", None)
        cutoff = self.offer("next", "twentieth")
        self.offer("still-open", "later", None)
        pending = self.read()
        self.assertEqual((19, open_start, None), (pending["enrolled_tasks"], pending["first_unresolved"],
                                                  pending["twentieth_start"]))
        self.finish("open", "quota")
        completed = self.read()
        self.assertEqual((20, None, cutoff), (completed["enrolled_tasks"], completed["first_unresolved"],
                                              completed["twentieth_start"]))

    def test_historical_missing_observation_cannot_be_filled_by_a_resident_message(self):
        self.start("a", "one")
        self.assign("a", "one", actor="alice")
        self.assign("a", "one", tied=None)
        self.finish("a", "success")
        self.offer("b", "two")
        report = self.read()
        self.assertEqual((0, 1, 1), (report["enrolled_tasks"], report["missing_shortlists"], report["first_unresolved"]))
        self.assertNotIn("tied_families", report["offers"][0])

    def test_special_task_role_is_read_at_start_and_can_be_cleared(self):
        self.event("task", {"task": "one", "helper": "build"}, "alice")
        self.offer("a", "one", tied=None)
        self.event("ready", {"task": "one", "helper": "none"}, "alice")
        regular = self.offer("b", "one")
        self.assertEqual([regular], self.read()["enrolled_starts"])

    def test_malformed_or_conflicting_shortlists_fail_with_receipt_number(self):
        for change in ({"task_generation": True}, {"task": "other"}, {"tied_families": ["muse"]},
                       {"tied_families": ["codex", "codex"]}, {"tied_families": ["codex", "other"]},
                       {"reason": "direct"}, {"helper": True}, {"lane": "explore"}):
            with self.subTest(change=change):
                self.events = []
                self.start("a", "one")
                self.assign("a", "one")
                text = self.events[-1]["data"]["text"]
                value = json.loads(text.removeprefix("house-assignment-v1 "))
                self.events[-1]["data"]["text"] = "house-assignment-v1 " + json.dumps(value | change)
                self.read(error="start 1" if {"lane", "helper", "reason"}.intersection(change) else "admission 1")

    def test_missing_or_overlapping_pages_cannot_hide_an_earlier_offer(self):
        self.offer("a", "one")
        self.offer("b", "two")
        for chunks in ([(1, 6)], [(0, 3), (2, 6)], [(0, 2), (3, 6)]):
            self.read(chunks=chunks, error="gap or overlap")
        self.events[1]["sequence"] = 100
        self.read(error="invalid journal event at 2")
