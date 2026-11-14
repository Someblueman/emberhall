"""Synthetic authority/clock tests: scheduling does not grant a research lease."""
import copy
import unittest

from house import home, life, maintenance, shelf_gate
from tests import test_selection_repair as fixtures
from tests.test_shelf import idea


class ExplorerDispatchTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.SelectionRepairTests(); self.prior.setUp()
        self.h = self.prior.h
        self.h.event("owner-migrate", self.prior.migration())

    def migration(self):
        old = maintenance.protected_manifest(self.h.state)
        data = self.prior.migration()
        data.pop("rule_base")
        return data | {"scope": maintenance.EXPLORER_SCOPE,
            "approval_sha256": maintenance.KEEP_MOVING_SHA256,
            "previous_manifest_sha256": maintenance.fingerprint(old),
            "protected_files": old | {name: "9" * 64 for name in
                                      maintenance.ALLOWED_CHANGES[maintenance.EXPLORER_SCOPE]}}

    def enable(self):
        self.h.event("owner-migrate", self.migration())

    def start_data(self, key, **extra):
        return {"kind": "run-start", "run": key, "resident": "resident-" + key,
                "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
                "workspace": "residents/" + key, "policy_revision": "fixture", "mode": "work", **extra}

    def start(self, key, **extra):
        self.h.event("life", self.start_data(key, **extra), "watch-keeper")

    def demand(self):
        return life.workload(self.h.state, self.h.now)

    def test_activation_preserves_rules_quotas_and_rejects_other_authority_changes(self):
        before = copy.deepcopy(self.h.state)
        self.assertIsNone(self.demand()["explore_generation"])
        good = self.migration()
        self.h.reject("owner-migrate", good, "owner operator", "bob")
        for path in ("house/shelf.py", "house/shelf_gate.py", "house/providers.py", "house/wake_policy.py"):
            bad = copy.deepcopy(good); bad["protected_files"][path] = "0" * 64
            self.h.reject("owner-migrate", bad, "outside.*scope")
        self.enable()
        for key in before.keys() - {"maintenance", "sequence", "at", "receipts"}:
            self.assertEqual(before[key], self.h.state[key], key)
        self.h.reject("owner-migrate", good, "already used")
        self.assertEqual(0, self.demand()["explore_generation"])
        self.h.sync([self.h.comment("REPEAL " + shelf_gate.REVISED_POLICY_ID)])
        self.assertIsNone(self.demand()["explore_generation"])

    def test_atomic_admission_has_one_reservation_and_no_fake_lease(self):
        self.enable(); self.start("first", explore_generation=0)
        self.assertIsNone(self.demand()["explore_generation"])
        self.assertNotIn("shelf", self.h.state)
        self.assertEqual([], self.demand()["idle_residents"])
        self.h.reject("life", self.start_data("racer", explore_generation=0), "demand changed", "watch-keeper")
        self.h.reject("life", self.start_data("bad", explore_generation=True), "invalid Explorer", "watch-keeper")
        self.h.reject("life", self.start_data("both", explore_generation=0, backlog=True), "invalid Explorer", "watch-keeper")

    def test_stopped_or_unresponsive_admission_becomes_available(self):
        self.enable(); self.start("crash", explore_generation=0)
        self.h.event("life", {"kind": "run-finish", "run": "crash", "outcome": "interrupted",
            "exit_code": None, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        self.assertEqual(0, self.demand()["explore_generation"])
        self.start("quiet", explore_generation=0)
        self.h.now += life.EXPLORER_ADMISSION_SECONDS
        self.assertEqual(0, self.demand()["explore_generation"])
        self.start("replacement", explore_generation=0)
        self.assertIsNone(self.demand()["explore_generation"])

    def test_actual_lease_suppresses_demand_and_sleep_or_expiry_recovers(self):
        self.enable()
        self.h.event("life", {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"})
        self.h.event("shelf", {"kind": "explore-start", "round": "actual", "expect": 0,
                              "token": "actual", "seconds": 60})
        self.assertIsNone(self.demand()["explore_generation"])
        self.h.now += 60
        self.assertEqual(1, self.demand()["explore_generation"])
        self.h.event("sleep", {"through": 0, "note": "Expired research remains recoverable"})
        self.assertEqual(1, self.demand()["explore_generation"])
        self.h.reject("life", self.start_data("stale", explore_generation=0), "demand changed", "watch-keeper")

    def test_full_shelf_suppresses_exploration_then_rejection_reopens_it(self):
        self.enable()
        self.h.event("life", {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"})
        self.h.event("shelf", {"kind": "explore-start", "round": "r", "expect": 0, "token": "r", "seconds": 60})
        self.h.event("shelf", {"kind": "explore-publish", "round": "r", "token": "r",
                              "ideas": [idea(k) for k in "abc"]})
        self.assertIsNone(self.demand()["explore_generation"])
        self.h.event("shelf", {"kind": "choice-open", "choice": "c",
                              "milestones": {k: {"milestone": "Useful demonstration"} for k in "abc"}})
        for actor in ("alice", "bob", "carol"):
            self.h.event("shelf", {"kind": "choice-vote", "choice": "c", "idea": None,
                                  "reason": "Too little distinct value"}, actor)
        self.assertEqual(1, self.demand()["explore_generation"])

    def test_research_lease_is_useful_work_after_admission_reservation_expires(self):
        self.enable(); self.start("research", explore_generation=0)
        actor = "resident-research"
        self.h.event("arrive", {"name": "Researcher"}, actor)
        self.h.event("life", {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"}, actor)
        self.h.event("shelf", {"kind": "explore-start", "round": "long", "expect": 0,
                              "token": "long", "seconds": 1800}, actor)
        self.h.event("task", {"task": "build", "title": "Build", "description": "Chosen work", "ready": True})
        self.h.now += life.EXPLORER_ADMISSION_SECONDS
        self.assertEqual([], self.demand()["idle_residents"])
        self.assertEqual(1, self.demand()["uncovered_tasks"])
        self.assertIsNone(self.demand()["explore_generation"])

    def test_capacity_pause_and_quota_remain_binding(self):
        self.enable()
        for key in ("one", "two", "three"):
            self.start(key)
        self.assertEqual(0, self.demand()["wanted_starts"])
        self.h.reject("life", self.start_data("four", explore_generation=0), "three residents", "watch-keeper")
        self.h.state["maintenance"]["admissions"] = {"until": self.h.now + 60}
        self.h.reject("life", self.start_data("paused", explore_generation=0), "paused", "watch-keeper")
        self.h.state["maintenance"].pop("admissions")
        self.h.state["life"]["runs"] = {}
        self.h.event("life", {"kind": "budget", "agent": "codex", "until": self.h.now + 60,
                              "reason": "Synthetic quota"}, "watch-keeper")
        self.h.reject("life", self.start_data("quota", explore_generation=0), "cooling down", "watch-keeper")
        self.h.state["shelf"] = {"last_kind": "muse"}
        picked = home.choose_provider(self.h.state, self.h.now, exploring=True)
        self.assertNotIn(picked, ("codex", "muse"))
        self.h.state["life"]["budgets"].update({k: {"until": self.h.now + 60} for k in ("opencode", "agy")})
        self.assertEqual("muse", home.choose_provider(self.h.state, self.h.now, exploring=True))
