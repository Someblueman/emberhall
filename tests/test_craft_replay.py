import json
import unittest
import hashlib
from pathlib import Path

from house import craft_replay as replay
from house.life import CONTROLLER
from house.work_metrics import ASSIGNMENT_PREFIX


def history():
    # All four families have had eight work turns. The Explorer moves Codex
    # behind OpenCode in recency without changing the work-lane counts.
    runs = {}
    for i in range(32):
        kind = replay.KINDS[i % 4]
        runs[str(i)] = dict(agent=kind, model="ordinary", started_sequence=i + 1, ended_sequence=i + 2)
    runs["explorer"] = dict(agent="codex", model="ordinary", explore_generation=1,
                            started_sequence=33, ended_sequence=34)
    return {"sequence": 50, "life": {"runs": runs, "requests": {}}}


def row(family, passes, finished=4, missing=0):
    return dict(family=family, area="project/proof", eligible_claims=4, eligible_finishes=finished,
                reviewed_runs=4, first_pass=passes, no_review_receipt=missing,
                quota_claims=8, quota_runs=8)


def event(seq, op, data, actor=CONTROLLER, request=None):
    return dict(sequence=seq, at=float(seq), op=op, data=data, actor=actor, id=request or str(seq))


def pages():
    admission = dict(kind="run-start", agent="opencode", model="ordinary", mode="work",
                     resident="builder", run="next", task="job", backlog=True)
    observation = dict(run="next", lane="work", reason="balanced", helper=False,
                       window=32, prior_starts=dict.fromkeys(replay.KINDS, 8))
    return [
        event(36, "task", {"task": "job", "project": "proof"}, actor="author"),
        event(37, "owner-migrate", {"protected_files": {
            "house/" + name + ".py": hashlib.sha256(
                Path(replay.__file__).with_name(name + ".py").read_bytes()).hexdigest()
            for name in ("home", "life", "maintenance", "providers", "staffing", "work_metrics")}}),
        event(38, "life", admission),
        event(39, "say", {"text": ASSIGNMENT_PREFIX + json.dumps(observation)},
              request="home-next-assignment"),
    ]


class CraftReplay(unittest.TestCase):
    def setUp(self):
        self.status = history()
        self.budgets = {"budgets": {}, "model_budgets": {
            "codex": {"old": {"sequence": 20, "until": 25}}}}
        self.fit = {"first": 1, "through": 37, "rows": [row("opencode", 1), row("agy", 4)]}

    def report(self, events=None):
        events = events or pages()
        for e in events:
            data = e["data"]
            if data.get("kind") == "run-start":
                self.status["life"]["runs"][data["run"]] = dict(
                    data, started_sequence=e["sequence"], ended_sequence=e["sequence"] + 1)
        return replay.replay(self.status, self.budgets, self.fit, [events])

    def test_real_picker_tie_with_conservative_outcomes(self):
        result = self.report()
        decision, = result["decisions"]
        self.assertEqual((decision["baseline"], decision["candidate"]), ("opencode", "agy"))
        self.assertEqual(decision["ordinary_floor"], 8)
        self.assertEqual(result["observed_alternate_outcomes"], 0)
        self.fit["rows"][1]["eligible_finishes"] = 3
        self.assertEqual(self.report()["would_change"], 0)
        self.fit["rows"][1] = row("agy", 4, missing=12)
        self.assertEqual(self.report()["would_change"], 0)
        self.fit["rows"][1] = row("agy", 3) | {"reviewed_runs": 3}
        self.assertEqual(self.report()["would_change"], 0)

    def test_no_trade_of_floor_or_busy_priority(self):
        # Put the oldest start in the baseline family. Each still has eight.
        runs = self.status["life"]["runs"]
        runs["0"]["agent"], runs["1"]["agent"] = "opencode", "codex"
        self.assertEqual(self.report()["decisions"][0]["reason"], "family floor")
        runs["0"]["agent"], runs["1"]["agent"] = "codex", "opencode"
        runs["31"]["ended_sequence"] = 48  # agy is still busy at decision time
        self.assertNotIn("agy", self.report()["decisions"][0]["tied"])
        self.assertEqual(self.report()["would_change"], 0)

    def test_later_tags_claims_and_explorer_or_target_cannot_change_admission(self):
        for update, expected in [({"explore_generation": 9}, "Explorer"),
                                 ({"help_request": "named"}, "help or review"),
                                 ({"agent": "codex", "model": "gpt-6-luna"}, "helper")]:
            with self.subTest(update=update):
                events = pages()
                events[2]["data"].update(update)
                self.assertEqual(self.report(events)["excluded"], {expected: 1})
        events = pages()
        events[0]["data"].pop("project")
        events.append(event(40, "ready", {"task": "job", "project": "proof"}, "author"))
        self.assertFalse(self.report(events)["decisions"])
        events[2]["data"].pop("task")
        events.append(event(41, "claim", {"task": "job"}, "builder"))
        self.assertEqual(self.report(events)["excluded"], {"no task at admission": 1})

    def test_wrong_receipt_or_mismatched_observed_baseline_is_visible(self):
        events = pages()
        events[3]["actor"] = "builder"
        self.assertFalse(self.report(events)["decisions"])
        events = pages()
        events[2]["data"]["agent"] = "agy"
        decision, = self.report(events)["decisions"]
        self.assertEqual(decision["reason"], "baseline mismatch")
        self.assertEqual(decision["candidate"], "agy")

    def test_future_cooldown_gap_or_new_install_cannot_be_backfilled(self):
        events = pages()
        self.budgets["budgets"]["agy"] = {"sequence": 38, "until": 56}
        with self.assertRaisesRegex(ValueError, "postdates"):
            self.report(events)
        self.budgets["budgets"].clear()
        with self.assertRaisesRegex(ValueError, "contiguous"):
            self.report(events[:1] + events[2:])
        events.append(event(40, "renovation-install", {}))
        with self.assertRaisesRegex(ValueError, "changed at 40"):
            self.report(events)

    def test_a_second_tie_in_same_work_window_keeps_its_turn(self):
        events = pages()
        for seq, kind in [(40, "codex"), (41, "agy"), (42, "muse")]:
            events.append(event(seq, "life", {"kind": "run-start", "agent": kind, "model": "ordinary",
                                              "run": kind, "mode": "work"}))
        events.append(event(43, "say", {"text": "between turns"}))
        second = dict(events[2]["data"], run="later")
        obs = json.loads(events[3]["data"]["text"][len(ASSIGNMENT_PREFIX):])
        events.append(event(44, "life", second))
        events.append(event(45, "say", {"text": ASSIGNMENT_PREFIX + json.dumps(obs | {"run": "later"})},
                            request="home-later-assignment"))
        decisions = self.report(events)["decisions"]
        self.assertEqual([r["reason"] for r in decisions],
                         ["historical preference", "one change per work window"])

    def test_wrong_policy_or_invalid_denominator_stops_the_report(self):
        events = pages()
        events[1]["data"]["protected_files"]["house/home.py"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "home.py differs"):
            self.report(events)
        self.fit["rows"][0]["eligible_finishes"] = 5
        with self.assertRaisesRegex(ValueError, "denominators"):
            self.report()
