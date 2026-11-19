import json
import unittest

import test_tie_replay
import turn_loss
from house.work_metrics import WINDOW


class TurnLossTests(unittest.TestCase):
    def setUp(self):
        self.source = test_tie_replay.TieReplayTests()
        self.source.setUp()
        self.source.train()
        self.house = self.source.house
        self.target = self.source.offer("compare")

    def inputs(self):
        runs = {}
        requests = {}
        for event in self.house.events:
            data = event["data"]
            if event["op"] == "life" and data["kind"] == "run-start":
                runs[data["run"]] = data | {"started_sequence": event["sequence"]}
            if event["op"] == "life" and data["kind"] == "help":
                requests[data["request"]] = data
        end = self.house.events[-1]["sequence"]
        status = {"sequence": end, "shelf": {"record": self.source.record},
                  "life": {"runs": runs, "requests": requests}}
        recent = []
        for event in self.house.events:
            if not event["id"].endswith("-assignment"):
                continue
            prefix, raw = event["data"]["text"].split(" ", 1)
            obs = json.loads(raw)
            run = runs[obs["run"]]
            if (obs["lane"] == "work" and not obs["helper"]):
                obs["prior_starts"] = {f: recent[-WINDOW:].count(f) for f in turn_loss.FAMILIES}
                obs["window"] = WINDOW
                recent.append(run["agent"])
            event["data"]["text"] = prefix + " " + json.dumps(obs)
        return status, self.house.events, end

    def target_result(self):
        return next(row for row in turn_loss.report(*self.inputs())["decisions"]
                    if row["offer"] == self.target)

    def test_later_loss_has_first_window_and_excludes_protected_lanes(self):
        for name, lane, is_helper in [("scout", "explore", False), ("helper", "work", True),
                                      ("review", "review", False)]:
            if lane == "review":
                self.house.add("life", "writer", kind="help", request="review-help", review_run="prior")
            seq = self.house.offer(name, name, help_request="review-help" if lane == "review" else None)
            start = next(e["data"] for e in self.house.events if e["sequence"] == seq)
            if lane == "explore":
                start["explore_generation"] = 1
            if is_helper:
                start["model"] = "gpt-6.1-terra"
            receipt = next(e for e in self.house.events if e["id"] == f"home-{name}-assignment")
            prefix, raw = receipt["data"]["text"].split(" ", 1)
            value = json.loads(raw)
            for field in ("task", "task_generation", "tied_families"):
                value.pop(field)
            receipt["data"]["text"] = prefix + " " + json.dumps(value | {"helper": is_helper, "lane": lane})
        for i in range(30):
            last = self.source.offer(f"later-{i}", "agy", outcome="quota")
        row = self.target_result()
        self.assertEqual("family loses its last turn", row["state"])
        self.assertEqual((31, last, last + 1),
                         (row["windows_checked"], row["first_loss"]["window_through"],
                          row["first_loss"]["receipt"]))

    def test_first_window_loss_and_complete_horizon(self):
        decision = {"offer": 40, "task": "one", "baseline": "codex", "evidence_preference": "agy",
                    "tied_families": ["codex", "agy"]}
        turns = [(s, str(s), "agy" if s < 40 else "codex") for s in range(1, 73)]
        receipts = {s: s + 100 for s, _, _ in turns}
        row = turn_loss.compare(turns, 39, decision, receipts, None)
        self.assertEqual((1, 40), (row["windows_checked"], row["first_loss"]["window_through"]))
        turns[38] = (39, "39", "codex")
        row = turn_loss.compare(turns, 39, decision, receipts, None)
        self.assertEqual(("no last turn lost in all affected windows", WINDOW, None),
                         (row["state"], row["windows_checked"], row["first_loss"]))

    def test_short_horizon_change_and_missing_receipt_stay_distinct(self):
        row = self.target_result()
        self.assertEqual(("partial follow-up", 1), (row["state"], row["windows_checked"]))
        self.house.install(proposal="new", protected_files=self.house.manifest | {"house/home.py": "0"*64})
        self.source.offer("after-change", "agy")
        self.assertEqual("follow-up stopped at policy change", self.target_result()["state"])
        args = self.inputs()
        receipt = next(e for e in self.house.events if e["id"] == "home-compare-assignment")
        prefix, raw = receipt["data"]["text"].split(" ", 1)
        value = json.loads(raw)
        del value["prior_starts"]
        receipt["data"]["text"] = prefix + " " + json.dumps(value)
        self.assertEqual("missing window receipt", turn_loss.report(*args)["decisions"][-1]["state"])

    def test_disagreeing_count_and_missing_status_admission_fail(self):
        args = self.inputs()
        receipt = next(e for e in self.house.events if e["id"] == "home-compare-assignment")
        prefix, raw = receipt["data"]["text"].split(" ", 1)
        value = json.loads(raw)
        value["prior_starts"]["codex"] = 123
        receipt["data"]["text"] = prefix + " " + json.dumps(value)
        with self.assertRaisesRegex(ValueError, "prior work starts disagree"):
            turn_loss.report(*args)
        del args[0]["life"]["runs"]["compare"]
        with self.assertRaisesRegex(ValueError, "status lacks admission"):
            turn_loss.report(*args)


if __name__ == "__main__":
    unittest.main()
