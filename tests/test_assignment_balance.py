"""Fair opportunities by assignment type, without equalizing tokens or duration."""
import unittest

from house.home import KINDS, choose_provider
from house.work_metrics import counts


class AssignmentBalanceTests(unittest.TestCase):
    def setUp(self):
        self.state = {"life": {"runs": {}, "requests": {}, "budgets": {}}}

    def add(self, kind, *, lane="work", status="completed"):
        runs = self.state["life"]["runs"]
        key = str(len(runs) + 1)
        run = {"agent": kind, "status": status, "started_sequence": len(runs) + 1}
        if lane == "review":
            run["help_request"] = key
            self.state["life"]["requests"][key] = {"review_run": "earlier"}
        elif lane == "explore":
            run["explore_generation"] = 1
        runs[key] = run

    def test_recent_opportunities_rebalance_despite_oldest_start(self):
        for kind in ["codex"] * 8 + ["opencode", "muse", "agy"]:
            self.add(kind)
        self.assertEqual(choose_provider(self.state, 100), "opencode")
        for _ in range(128):
            self.add(choose_provider(self.state, 100))
        # The oldest item falls out after selection, so a rolling window can
        # differ by two even when the next opportunity goes to the least used.
        recent = counts(self.state, "work", KINDS)
        self.assertLessEqual(max(recent.values()) - min(recent.values()), 2)
        self.assertEqual(sum(recent.values()), 32)

    def test_review_and_exploration_do_not_consume_ordinary_opportunities(self):
        for _ in range(10):
            self.add("codex", lane="review")
            self.add("muse", lane="explore")
        self.add("opencode")
        self.add("agy")
        self.assertEqual(choose_provider(self.state, 100), "codex")
        self.assertEqual(choose_provider(self.state, 100, reviewing=True), "muse")
        self.assertEqual(choose_provider(self.state, 100, exploring=True), "codex")

    def test_cooldown_busy_and_explicit_exception_remain_real(self):
        self.add("codex", status="active")
        self.assertEqual(choose_provider(self.state, 100), "opencode")
        self.assertEqual(choose_provider(self.state, 100, "codex"), "codex")
        self.state["life"]["budgets"]["codex"] = {"until": 101}
        self.assertEqual(choose_provider(self.state, 100, "codex"), "opencode")
        self.state["life"]["budgets"] = {kind: {"until": 101} for kind in KINDS}
        self.assertIsNone(choose_provider(self.state, 100))
        self.assertIsNotNone(choose_provider(self.state, 101))

    def test_last_explorer_kind_yields_and_old_history_does_not_create_debt(self):
        self.state["shelf"] = {"last_kind": "codex"}
        self.assertEqual(choose_provider(self.state, 100, exploring=True), "opencode")
        for _ in range(100):
            self.add("muse")
        for _ in range(32):
            self.add("codex")
        self.assertEqual(counts(self.state, "work", KINDS)["muse"], 0)
        # Failures are attempts too; no endless attempts to repay a missing success.
        for run in self.state["life"]["runs"].values():
            run["outcome"] = "failed"
        self.assertEqual(choose_provider(self.state, 100), "opencode")
