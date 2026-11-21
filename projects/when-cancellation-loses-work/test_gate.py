"""Independent oracle mutations and hand-checkable transition boundaries."""
from __future__ import annotations

import copy
import unittest

from admission_model import Machine, execute
from ownership_oracle import violations


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.state = {"queue": [0], "returned": [], "completed": [],
                      "registry": [], "live": [], "held": {}, "free": 3,
                      "terminal": False}

    def test_valid_queue_and_completed(self):
        self.assertEqual(violations((2,), self.state), ())
        self.state["queue"] = []
        self.state["completed"] = [0]
        self.state["terminal"] = True
        self.assertEqual(violations((2,), self.state), ())

    def test_loss_duplicate_and_unknown(self):
        self.state["queue"] = []
        self.assertIn("lost:0", violations((2,), self.state))
        self.state["completed"] = [0, 0, 8]
        self.assertIn("multiple-owners:0", violations((2,), self.state))
        self.assertIn("unknown-job:8", violations((2,), self.state))

    def test_capacity_and_stranding(self):
        self.state.update(queue=[], live=[0], held={0: 2}, free=1)
        self.assertEqual(violations((2,), self.state), ())
        self.state["held"] = {}
        self.assertIn("unreserved-live-job", violations((2,), self.state))
        self.state.update(held={0: 4}, free=-1)
        self.assertIn("wrong-weight:0", violations((2,), self.state))
        self.assertIn("capacity-accounting", violations((2,), self.state))
        self.state.update(live=[], held={0: 2}, free=1)
        self.assertIn("stranded:0", violations((2,), self.state))

    def test_live_registry_ends_at_settlement(self):
        self.state.update(queue=[], registry=[0], held={0: 2}, free=1)
        self.assertEqual(violations((2,), self.state), ())
        self.state["terminal"] = True
        self.assertIn("unsettled-terminal", violations((2,), self.state))


class ModelTests(unittest.TestCase):
    def test_policy_only_changes_signal_recipients(self):
        machines = [Machine((1, 2, 1), p, "owner", True, None)
                    for p in ("bottom_up", "simultaneous")]
        for m in machines:
            # Explicit state: parent awaits worker 0 which awaits its leaf.
            m.queue = [1, 2]
            m.held = {0: 1}
            from admission_model import Worker
            m.workers[0] = Worker(phase="leaf", leaf="waiting", started=True)
            m.parent = "wait"
            m.awaited = 0
        before = [m.snapshot() for m in machines]
        self.assertEqual(before[0], before[1])
        for m in machines:
            m.cancel()
        bottom, simultaneous = [m.snapshot() for m in machines]
        self.assertTrue(bottom["workers"][0]["leaf_pending"])
        self.assertFalse(bottom["parent_pending"])
        self.assertFalse(bottom["workers"][0]["pending"])
        self.assertTrue(simultaneous["parent_pending"])
        self.assertTrue(simultaneous["workers"][0]["pending"])
        clean = copy.deepcopy(simultaneous)
        clean["parent_pending"] = False
        clean["workers"][0]["pending"] = False
        self.assertEqual(bottom, clean)

    def test_cancel_before_and_after_start(self):
        for policy in ("bottom_up", "simultaneous"):
            unsafe = execute((2,), policy, "worker", False, 1)
            self.assertIn("lost:0", violations((2,), unsafe.final))
            self.assertIn("stranded:0", violations((2,), unsafe.final))
            repaired = execute((2,), policy, "owner", False, 1)
            self.assertEqual(violations((2,), repaired.final), ())
            started = execute((2,), policy, "worker", False, 2)
            self.assertEqual(violations((2,), started.final), ())
            self.assertEqual(started.final["returned"], [0])

    def test_frozen_boundary_rejects_unregistered_inputs(self):
        for weights in ((), (4,), (1, 2, 3, 1), (True,), (1.0,)):
            with self.assertRaises(ValueError):
                execute(weights)
        for cut in (500, True, 1.5, -1):
            with self.assertRaises(ValueError):
                execute((1,), cut=cut)
        with self.assertRaises(ValueError):
            execute((1,), consume="false")


if __name__ == "__main__":
    unittest.main()
