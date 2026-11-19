"""Real journal fixtures for the descriptive, strictly earlier tie comparison."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_trial
import tie_replay


class TieReplayTests(unittest.TestCase):
    def setUp(self):
        self.house = test_trial.TrialTests()
        self.house.setUp()
        self.house.install()
        self.record = {"ideas": {"codes": {"brief": {"sequence": 8, "field": "mathematics"}},
                                 "rooms": {"brief": {"sequence": 9, "field": "design"}}},
                       "projects": {"math": {"started_sequence": 15, "idea": "codes"},
                                    "house": {"started_sequence": 16, "idea": "rooms"}}}

    def review(self, run, verdict="integrated"):
        value = {"actor": "reviewer", "run": run, "base": "b" * 40,
                 "contribution": "c" * 40, "status": verdict, "test_exit": 0}
        seq = self.house.add("say", "reviewer", text="house-integration-v1 " + json.dumps(value))
        self.house.events[-1]["id"] = f"87654321-4321-4321-8321-{seq:012d}"
        return seq

    def offer(self, name, family="codex", verdict="integrated", **kwargs):
        self.house.add("task", "writer", task=name, project="math")
        seq = self.house.offer(name, name, finished=True, **kwargs)
        next(e for e in self.house.events if e["sequence"] == seq)["data"]["agent"] = family
        if verdict:
            self.review(name, verdict)
        return seq

    def result(self):
        end = self.house.events[-1]["sequence"]
        return tie_replay.replay({"sequence": end, "shelf": {"record": self.record}}, self.house.events, end)

    def train(self):
        for i in range(3):
            self.offer(f"base-{i}", verdict="rejected")
            self.offer(f"alt-{i}", "agy")

    def test_earlier_receiving_results_can_prefer_only_a_recorded_alternative(self):
        self.train()
        self.offer("decision")
        result = self.result()
        row = result["decisions"][-1]
        self.assertEqual(("agy", "codex", 0, False),
                         (row["evidence_preference"], row["routing_choice"],
                          result["routing_weight"], result["alternative_outcomes_estimated"]))
        self.assertEqual((3, 0, 3, 3), (row["earlier"]["codex"]["reviewed"],
                         row["earlier"]["codex"]["passed"], row["earlier"]["agy"]["reviewed"],
                         row["earlier"]["agy"]["passed"]))
        self.assertNotIn("private-claim-token", json.dumps(result))
        start = row["offer"]
        receipt = next(e for e in self.house.events if e["sequence"] == row["assignment"])
        value = json.loads(receipt["data"]["text"].split(" ", 1)[1])
        value["tied_families"] = ["codex"]
        receipt["data"]["text"] = "house-assignment-v1 " + json.dumps(value)
        singleton = self.result()["decisions"][-1]
        self.assertEqual((start, "codex", "sole recorded choice"),
                         (singleton["offer"], singleton["evidence_preference"], singleton["reason"]))

    def test_later_review_cannot_qualify_an_earlier_decision(self):
        self.train()
        self.offer("late", "agy", verdict=None)
        self.offer("decision")
        before = self.result()["decisions"][-1]
        self.review("late", "rejected")
        after = self.result()["decisions"][-1]
        self.assertEqual(before, after)
        self.assertEqual(1, after["earlier"]["agy"]["missing_review"])

    def test_quota_other_claimants_and_mixed_fields_do_not_supply_reviews(self):
        self.house.events.pop()  # Keep the unresolved training offer before installation.
        self.offer("open", "agy", verdict=None)
        self.house.events.pop()  # This receiving run has not exited at the cutoff.
        self.house.install()
        self.offer("quota", "agy", outcome="quota")
        self.offer("unlaunched", "agy", launched=False)
        self.offer("elsewhere", "agy")
        claim = next(e for e in self.house.events if e["op"] == "claim" and e["data"]["task"] == "elsewhere")
        finish = next(e for e in self.house.events if e["op"] == "finish" and e["data"]["task"] == "elsewhere")
        claim["actor"] = finish["actor"] = "other-resident"
        self.offer("mixed", "agy", verdict=None)
        exit_event = self.house.events.pop()
        self.house.add("task", "writer", task="design", project="house")
        self.house.add("claim", "mixed", task="design", expect=0, token="another")
        self.house.add("life", **exit_event["data"])
        self.review("mixed")
        self.offer("decision")
        row = self.result()["decisions"][-1]["earlier"]["agy"]
        self.assertEqual((2, 1, 0, 1), tuple(row[k] for k in
                         ("eligible_offers", "finished", "reviewed", "unattributed_review")))
        self.assertEqual((1, 1, 1), tuple(row[k] for k in ("quota", "open", "closed_without_launch")))

    def test_threshold_equal_scores_and_unknown_field_keep_baseline(self):
        for family in ("codex", "agy"):
            for i in range(2):
                self.offer(f"{family}-{i}", family)
        self.offer("decision")
        self.assertIn("insufficient", self.result()["decisions"][-1]["reason"])
        self.offer("third-base")
        self.offer("third-alt", "agy")
        self.offer("tied")
        self.assertIn("equal scores", self.result()["decisions"][-1]["reason"])
        self.record["projects"]["math"]["brief"] = {"sequence": self.house.events[-1]["sequence"], "field": "design"}
        self.assertEqual("earlier project brief unavailable", self.result()["decisions"][-1]["reason"])

    def test_runtime_change_and_explorer_turn_do_not_enter_comparison(self):
        self.train()
        self.offer("explore")
        start = next(e for e in self.house.events if e["op"] == "life" and e["data"].get("run") == "explore")
        start["data"]["explore_generation"] = 1
        receipt = next(e for e in self.house.events if e["id"] == "home-explore-assignment")
        value = json.loads(receipt["data"]["text"].split(" ", 1)[1])
        for key in ("task", "task_generation", "tied_families"):
            del value[key]
        receipt["data"]["text"] = "house-assignment-v1 " + json.dumps(value)
        self.house.install(proposal="new", protected_files=self.house.manifest | {"house/home.py": "0" * 64})
        self.offer("after-change")
        self.assertEqual(6, len(self.result()["decisions"]))

    def test_real_cli_before_installation_and_invalid_page(self):
        self.house.events = self.house.events[:2]
        with tempfile.TemporaryDirectory() as tmp:
            page, status = Path(tmp) / "page.json", Path(tmp) / "status.json"
            end = self.house.events[-1]["sequence"]
            page.write_text(json.dumps({"events": self.house.events, "through": end, "latest": end, "has_more": False}))
            status.write_text(json.dumps({"sequence": end, "shelf": {"record": self.record}}))
            args = [sys.executable, str(Path(tie_replay.__file__)), "--status", str(status), str(page)]
            run = subprocess.run(args, capture_output=True, text=True, cwd=tmp)
            self.assertEqual(0, run.returncode, run.stderr)
            self.assertIn("0 enrolled comparisons", run.stdout)
            page.write_text("{}")
            self.assertEqual(2, subprocess.run(args, capture_output=True).returncode)
