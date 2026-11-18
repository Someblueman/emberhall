"""Current task pages through real CLI and fixed mailbox boundaries."""
import json
from unittest.mock import patch

from house.work_status import task_page
from tests.support import HouseCase
from tests.test_mailbox import MailboxCase


class WorkStatusTests(HouseCase):
    def offer(self, name, **extra):
        self.record.append("task", "alice", {"task": name, "title": name,
            "description": "Own only " + name + ".txt; acceptance: the file is readable.", **extra})

    def test_pages_keep_exact_claim_context_and_exclude_finished_history(self):
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        self.offer("zebra", ready=True)
        self.offer("apple", ready=True)
        self.offer("held")
        self.record.append("claim", "bob", {"task": "held", "expect": 0,
            "token": "held-token", "seconds": 3600})
        self.offer("not-queued")
        self.offer("finished", ready=True)
        self.record.append("claim", "alice", {"task": "finished", "expect": 0,
            "token": "done-token", "seconds": 3600})
        (self.repo / "done.txt").write_text("immutable payload")
        self.cli("finish", "finished", "--as", "alice", "--token", "done-token",
                 "--result", "A long historical result", "--artifact", "done.txt")
        before = self.record.read()

        first = self.cli("status", "--tasks", "--limit", "2")
        self.assertEqual(list(first["tasks"]), ["apple", "held"])
        self.assertEqual(first["page"], {"offset": 0, "limit": 2, "total": 3,
            "shown": 2, "has_more": True, "next_offset": 2})
        self.assertEqual(first["source"]["journal_head"], before[2])
        self.assertEqual(first["source"]["sequence"], before[0]["sequence"])
        held = first["tasks"]["held"]
        self.assertEqual(held["description"], before[0]["tasks"]["held"]["description"])
        self.assertEqual((held["generation"], held["owner"], held["available"]), (1, "bob", False))
        self.assertTrue(first["tasks"]["apple"]["available"])
        self.assertNotIn("token", held)
        self.assertEqual(first["omitted"], {"done": 1, "unqueued_open": 1})
        self.assertNotIn("immutable payload", json.dumps(first))
        self.assertNotIn("historical result", json.dumps(first))
        second = self.cli("status", "--tasks", "--limit", "2", "--offset", "2")
        self.assertEqual(list(second["tasks"]), ["zebra"])
        self.assertIsNone(second["page"]["next_offset"])
        self.assertEqual(first["source"]["journal_head"], second["source"]["journal_head"])
        beyond = self.cli("status", "--tasks", "--offset", "50")
        self.assertEqual(beyond["tasks"], {})
        self.assertEqual(self.record.read(), before)

        full = self.cli("status")
        self.assertIn("finished", full["tasks"])
        self.assertIn("not-queued", full["tasks"])
        self.assertIn("lessons", full)
        self.assertIn("token", full["tasks"]["held"])

    def test_empty_queue_and_invalid_arguments_do_not_write(self):
        before = self.record.read()
        result = self.cli("status", "--tasks")
        self.assertEqual(result["tasks"], {})
        self.assertEqual(result["page"]["total"], 0)
        self.assertFalse(result["page"]["has_more"])
        for tail in (("--tasks", "--limit", "0"), ("--tasks", "--limit", "51"),
                     ("--tasks", "--offset", "-1"), ("--limit", "1"), ("--offset", "0")):
            self.cli("status", *tail, success=False)
        self.assertEqual(self.record.read(), before)

    def test_availability_is_one_clock_snapshot_and_pages_identify_changed_records(self):
        self.offer("held")
        self.record.append("claim", "bob", {"task": "held", "expect": 0,
            "token": "lease", "seconds": 60})
        state, _, head = self.record.read()
        expiry = state["tasks"]["held"]["until"]
        with patch("house.work_status.time.time", return_value=expiry - 1) as clock:
            live = task_page(state, head, limit=1, offset=0)
        clock.assert_called_once_with()
        self.assertFalse(live["tasks"]["held"]["available"])
        with patch("house.work_status.time.time", return_value=expiry):
            expired = task_page(state, head, limit=1, offset=0)
        self.assertTrue(expired["tasks"]["held"]["available"])
        self.assertEqual(expired["tasks"]["held"]["generation"], 1)
        self.assertEqual(expired["tasks"]["held"]["owner"], "bob")
        self.offer("another")
        changed = self.cli("status", "--tasks")
        self.assertNotEqual(changed["source"]["journal_head"], live["source"]["journal_head"])
        self.assertIn("restart", " ".join(changed["limitations"]))


class WorkStatusMailboxTests(MailboxCase):
    def test_fixed_client_pages_without_changing_journal_or_saved_cursor(self):
        self.arrive()
        for name in ("second", "first"):
            self.call("task", name, "--as", self.resident, "--title", name,
                      "--description", "Exclusive fixture file", "--ready")
        before = self.record.read()
        first = self.call("status", "--tasks", "--limit", "1")
        second = self.call("status", "--tasks", "--limit", "1", "--offset", "1")
        self.assertEqual(list(first["tasks"]), ["first"])
        self.assertEqual(list(second["tasks"]), ["second"])
        self.assertEqual(first["source"]["journal_head"], before[2])
        self.collect(self.start("status", "--tasks", "--limit", "0"), success=False)
        self.assertEqual(self.record.read(), before)
        self.assertIn("lessons", self.call("status"))
