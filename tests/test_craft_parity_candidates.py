"""Replay controller observations from disposable journals. No provider process is started."""
import json
from pathlib import Path
from runpy import run_path
import unittest
from unittest.mock import patch

from house import home, life, providers, work_metrics
from house.home_work import git
from house.record import Record
from tests.support import HouseCase
from tests.test_project_work import projects, start_data
from tests.test_quota_rest import house, rest


class DispatchReceiptTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = projects(self)
        self.repo = self.record.root
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
            "-c", "user.email=test@local", "commit", "--allow-empty", "-m", "Fixture source")
        runtime = self.root / "inert.pyz"
        runtime.write_bytes(b"inert")
        self.coordinator = home.Coordinator(self.record, runtime)
        for p in (patch("house.home.time.time", return_value=self.record.read()[0]["at"]),
                  patch("house.home.active_policy", return_value={"revision": "fixture"}),
                  patch("house.home.home_work.room", side_effect=ValueError("Stop at room creation"))):
            p.start()
            self.addCleanup(p.stop)

    def offer(self, task="build", **extra):
        self.record.append("task", "alice", {"task": task, "title": "Build", "description": "Fixture",
                                             "ready": True, **extra})

    def help(self, **extra):
        self.record.append("life", "alice", {"kind": "help", "request": "assist", "reason": "Fixture", **extra})

    def hold(self, agent):
        self.record.append("life", life.CONTROLLER, {"kind": "budget", "agent": agent,
                           "until": self.record.read()[0]["at"] + 3600, "reason": "Fixture"})

    def dispatch(self):
        result = self.coordinator.tick(poll=False)
        run, = result["started"]
        state, events, _ = Record(self.repo).read()
        receipt = events[state["receipts"][f"home-{run}-assignment"] - 1]
        self.assertEqual(("say", life.CONTROLLER), (receipt["op"], receipt["actor"]))
        observation = json.loads(receipt["data"]["text"].removeprefix(work_metrics.ASSIGNMENT_PREFIX))
        self.assertEqual(run, observation["run"])
        return state["life"]["runs"][run], observation

    def test_project_decision_survives_changed_availability_before_start(self):
        self.offer(project="earlier")
        self.hold("agy")
        start = self.coordinator.start

        def start_after_budget_change(*args, **kwargs):
            self.hold("opencode")
            return start(*args, **kwargs)

        with patch.object(self.coordinator, "start", side_effect=start_after_budget_change):
            run, observation = self.dispatch()
        self.assertEqual(("codex", "build", 0), (run["agent"], run["task"], run["task_generation"]))
        self.assertEqual(("build", 0), (observation["task"], observation["task_generation"]))
        self.assertEqual(["codex", "opencode", "muse"], observation["tied_families"])

    def test_ordinary_task_help_records_singleton_without_changing_admission_binding(self):
        self.offer()
        self.help(task="build")
        for agent in ("codex", "muse", "agy"):
            self.hold(agent)
        run, observation = self.dispatch()
        self.assertEqual(("opencode", "assist"), (run["agent"], run["help_request"]))
        self.assertNotIn("task", run)
        self.assertEqual(("build", 0, ["opencode"]), (
            observation["task"], observation["task_generation"], observation["tied_families"]))

    def test_task_help_becoming_ballot_work_leaves_the_next_ordinary_offer_readable(self):
        self.offer()
        self.help(task="build")
        start = self.coordinator.start

        def retag_before_start(*args, **kwargs):
            self.record.append("ready", "alice", {"task": "build", "expect": 0, "ready": True,
                                                   "ballot_choice": "later"})
            return start(*args, **kwargs)

        with patch.object(self.coordinator, "start", side_effect=retag_before_start):
            ballot, observation = self.dispatch()
        self.assertEqual((ballot["task_generation"], ballot["ballot_open"]), (1, False))
        self.assertTrue({"task", "task_generation", "tied_families"}.isdisjoint(observation))
        self.record.append("ready", "alice", {"task": "build", "expect": 1, "ready": False})
        self.offer(task="next", project="earlier")
        ordinary, _ = self.dispatch()
        events = [event | {"sequence": i} for i, event in enumerate(self.record.read()[1], 1)]
        reader = Path(__file__).resolve().parents[1] / "projects/kind-craft-and-routing/cohort.py"
        cohort = run_path(str(reader))["roster"](events, 0, len(events))
        self.assertEqual(cohort["enrolled_starts"], [ordinary["started_sequence"]])
        self.assertEqual([item["task"] for item in cohort["offers"]], ["next"])

    def test_unbound_help_generation_changes_after_start_has_read_its_state(self):
        self.offer()
        self.help(task="build")
        append_life = self.coordinator.life

        def change_during_admission(kind, run, **data):
            if kind == "run-start":
                self.record.append("ready", "alice", {"task": "build", "expect": 0, "ready": True})
            return append_life(kind, run, **data)

        with patch.object(self.coordinator, "life", side_effect=change_during_admission):
            run, observation = self.dispatch()
        self.assertEqual(run["help_request"], "assist")
        self.assertNotIn("tied_families", observation)

    def test_change_after_admission_keeps_the_original_shortlist(self):
        self.offer()
        self.help(task="build")
        append_life = self.coordinator.life

        def change_after_start(kind, run, **data):
            if kind != "run-start":
                return append_life(kind, run, **data)
            self.record.append("say", "alice", {"text": "Unrelated event before the wake"})
            receipt = append_life(kind, run, **data)
            self.record.append("ready", "alice", {"task": "build", "expect": 0, "ready": True})
            return receipt

        with patch.object(self.coordinator, "life", side_effect=change_after_start):
            run, observation = self.dispatch()
        self.assertEqual((observation["task"], observation["task_generation"]), ("build", 0))
        self.assertIn(run["agent"], observation["tied_families"])

    def test_oldest_start_can_win_from_the_middle_of_a_tie(self):
        for agent in ("muse", "agy", "codex", "opencode"):
            self.record.append("life", life.CONTROLLER, start_data(agent, agent=agent,
                               model=providers.DEFAULTS[agent]))
            self.record.append("life", life.CONTROLLER, {"kind": "run-finish", "run": agent,
                               "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        self.offer(project="earlier")
        run, observation = self.dispatch()
        self.assertEqual("muse", run["agent"])
        self.assertEqual(list(home.KINDS), observation["tied_families"])

    def test_lost_task_claim_emits_no_shortlist(self):
        self.offer(project="earlier")
        start = self.coordinator.start

        def start_after_claim(*args, **kwargs):
            self.record.append("claim", "alice", {"task": "build", "expect": 0,
                               "token": "before-admission", "seconds": 60})
            return start(*args, **kwargs)

        with patch.object(self.coordinator, "start", side_effect=start_after_claim):
            self.assertEqual([], self.coordinator.tick(poll=False)["started"])
        self.assertFalse(any(e["data"].get("text", "").startswith(work_metrics.ASSIGNMENT_PREFIX)
                             for e in self.record.read()[1]))

    def test_preferred_unavailable_request_has_no_parity_observation(self):
        self.offer(project="earlier")
        self.help(task="build", agent="codex")
        self.hold("codex")
        run, observation = self.dispatch()
        self.assertEqual(("opencode", "preferred-unavailable"), (run["agent"], observation["reason"]))
        self.assertTrue({"task", "task_generation", "tied_families"}.isdisjoint(observation))

    def test_unbound_request_has_no_parity_observation(self):
        self.help()
        _, observation = self.dispatch()
        self.assertNotIn("tied_families", observation)

    def test_task_text_outside_safe_identifier_has_no_parity_observation(self):
        self.offer(task="private/label", project="earlier")
        run, observation = self.dispatch()
        self.assertEqual("private/label", run["task"])
        self.assertTrue({"task", "task_generation", "tied_families"}.isdisjoint(observation))


class FamilyPriorityTests(unittest.TestCase):
    def test_quota_transferred_share_busy_floor_and_recency(self):
        state = house()
        for model in providers.ROTATION["opencode"]:
            rest(state, "opencode", model, 9000)
        runs = state["life"]["runs"]

        def add(agent, status):
            sequence = len(runs) + 1
            runs[str(sequence)] = {"agent": agent, "status": status, "started_sequence": sequence}

        add("muse", "completed")
        add("codex", "completed")
        add("agy", "completed")
        add("codex", "active")
        # Codex still has room for another run. Two starts / two shares ties one / one.
        tied = []
        self.assertEqual("muse", home.choose_provider(state, 2000, tied_families=tied))
        self.assertEqual(["codex", "muse", "agy"], tied)
        runs["2"]["status"] = "active"
        tied = []
        self.assertEqual("muse", home.choose_provider(state, 2000, tied_families=tied))
        self.assertEqual(["muse", "agy"], tied)
        add("muse", "completed")
        tied = []
        self.assertEqual("agy", home.choose_provider(state, 2000, tied_families=tied))
        self.assertEqual(["agy"], tied)
