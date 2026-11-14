"""Observed mailbox timing and immutable finishes are separate from native exits."""
import json
import os
import time

from house import mailbox, work_metrics
from house.body import export
from house.life import CONTROLLER
from tests.test_mailbox import MailboxCase


class WorkMetricsTests(MailboxCase):
    def test_real_mailbox_timing_includes_queue_delay_and_retry_is_stable(self):
        self.arrive()
        key = self.raw(["status"])
        request = self.requests / (key + ".json")
        begin = time.time() - 30
        os.utime(request, (begin, begin))
        mailbox.service(self.record, self.private, self.run)
        path = self.private / self.run / "mailbox" / (key + ".json")
        saved = json.loads(path.read_text())
        self.assertAlmostEqual(saved["queued_at"], begin, places=4)
        self.assertGreaterEqual(saved["response_ready_at"] - saved["queued_at"], 30)
        # Same command and stable receipt must retain its original timing.
        self.raw(["status"], key=key)
        mailbox.service(self.record, self.private, self.run)
        self.assertEqual(json.loads(path.read_text()), saved)
        report = work_metrics.waiting(self.private, self.run, begin, time.time())
        self.assertGreaterEqual(report["mailbox_seconds"], 30)
        self.assertEqual(report["voluntary_seconds"], 0)
        self.assertEqual(report["unmeasured_requests"], 0)

    def test_overlaps_old_and_pending_receipts_and_clipping(self):
        directory = self.private / self.run / "mailbox"
        directory.mkdir(parents=True, exist_ok=True)
        samples = [
            {"queued_at": 5, "response_ready_at": 25, "response": {}, "request": {"argv": ["read"]}},
            {"queued_at": 20, "response_ready_at": 40, "response": {}, "request": {"argv": ["wait"]}},
            {"first_seen": 12, "response": {}},
            {"queued_at": 22},
        ]
        for index, item in enumerate(samples):
            (directory / (str(index).zfill(64) + ".json")).write_text(json.dumps(item))
        report = work_metrics.waiting(self.private, self.run, 10, 30)
        self.assertEqual(report, {"run": self.run, "mailbox_seconds": 20, "voluntary_seconds": 10,
                                  "measured_requests": 2, "unmeasured_requests": 2})
        self.assertEqual(work_metrics.seconds([(1, 9), (2, 3), (7, 10)]), 9)

    def test_public_finish_survives_native_failure_without_future_leak_or_log_text(self):
        self.arrive()
        assignment = {"run": self.run, "lane": "work", "reason": "requested-provider",
                      "requested_agent": "codex", "secret": "DO-NOT-EXPORT"}
        self.record.append("say", self.resident, {"text": work_metrics.ASSIGNMENT_PREFIX + json.dumps(assignment)})
        before = export(self.record)["frames"][-1]
        self.assertNotIn("assignment", before["runs"][0])
        self.record.append("say", CONTROLLER, {"text": work_metrics.ASSIGNMENT_PREFIX + json.dumps(assignment)})
        self.call("task", "work", "--as", self.resident, "--title", "Deliver", "--description", "One artifact")
        self.call("claim", "work", "--as", self.resident, "--expect", "0", "--token", "token", "--seconds", "60")
        (self.workspace / "done.txt").write_text("useful draft")
        self.call("finish", "work", "--as", self.resident, "--token", "token", "--result", "Draft",
                  "--artifact", "done.txt")
        item = self.record.read()[0]["life"]["runs"][self.run]
        work_metrics.observe_wait(self.record, self.private, self.run, item, time.time() - item["started_at"])
        receipt = self.record.read()[2]
        work_metrics.observe_wait(self.record, self.private, self.run, item, 999)
        self.assertEqual(self.record.read()[2], receipt)
        self.record.append("life", CONTROLLER, {"kind": "run-finish", "run": self.run,
            "outcome": "failed", "exit_code": 1, "usage": {}, "elapsed_seconds": 60})
        history = export(self.record)
        run = history["frames"][-1]["runs"][0]
        self.assertEqual(run["outcome"], "failed")
        self.assertEqual([x["task"] for x in run["finished_tasks"]], ["work"])
        self.assertGreater(run["waiting"]["measured_requests"], 0)
        self.assertEqual(run["assignment"]["reason"], "requested-provider")
        self.assertEqual(before["runs"][0]["finished_tasks"], [])
        self.assertEqual(history["frames"][before["seq"] - 1], before)
        self.assertNotIn("DO-NOT-EXPORT", json.dumps(history))
