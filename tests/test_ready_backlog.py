"""Real journal/CLI boundaries for explicit ready work and finite native capacity."""
import time

from house.life import workload
from tests.support import HouseCase
from tests.test_mailbox import MailboxCase


class ReadyBacklogTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})

    def offer(self, name, ready=True):
        self.record.append("task", "alice", {"task": name, "title": name,
            "description": "Independent fixture work", "ready": ready})

    def start(self, name, **extra):
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": name,
            "resident": "resident-" + name, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": "a" * 40, "workspace": "residents/" + name,
            "policy_revision": "fixture", "mode": "work", **extra})

    def demand(self, at=None):
        state = self.record.read()[0]
        return workload(state, at or max(time.time(), state["at"]))

    def test_old_cli_payload_projection_and_ambitions_do_not_request_workers(self):
        self.cli("task", "ordinary", "--as", "alice", "--title", "Ordinary", "--description", "Old contract")
        state, events, _ = self.record.read()
        self.assertEqual(events[-1]["data"], {"task": "ordinary", "title": "Ordinary", "description": "Old contract"})
        self.assertNotIn("ready", state["tasks"]["ordinary"])
        self.assertEqual(self.demand()["ready_tasks"], [])
        self.assertEqual(self.demand()["wanted_starts"], 1)
        self.start("quiet")
        self.assertEqual(self.demand()["wanted_starts"], 0)

    def test_cli_opt_in_withdrawal_and_cas_protect_claims(self):
        self.cli("task", "work", "--as", "alice", "--title", "Work", "--description", "Bounded", "--ready")
        self.assertEqual(self.demand()["ready_tasks"], ["work"])
        self.cli("ready", "work", "--as", "bob", "--expect", "0", "--blocked")
        self.assertEqual(self.demand()["ready_tasks"], [])
        self.rejected("ready", "alice", {"task": "work", "ready": True, "expect": 0}, "generation")
        self.cli("ready", "work", "--as", "alice", "--expect", "1")
        self.record.append("claim", "bob", {"task": "work", "expect": 2, "token": "fresh", "seconds": 60})
        self.rejected("ready", "alice", {"task": "work", "ready": False, "expect": 3}, "live lease")
        self.record.append("release", "bob", {"task": "work", "token": "fresh", "note": "Blocked"})
        self.cli("ready", "work", "--as", "alice", "--expect", "3", "--blocked")
        self.assertEqual(self.record.read()[0]["tasks"]["work"]["generation"], 4)

    def test_readiness_rejects_nonboolean_sleeping_and_done_changes(self):
        for value in (1, "true", None):
            self.rejected("task", "alice", {"task": "bad", "title": "Bad", "description": "Fixture",
                                           "ready": value}, "boolean")
        self.offer("work")
        self.record.append("sleep", "bob", {"through": 0, "note": "Asleep"})
        self.rejected("ready", "bob", {"task": "work", "ready": True, "expect": 0}, "sleeping")
        self.rejected("ready", "alice", {"task": "work", "ready": 1, "expect": 0}, "fields")
        self.record.append("claim", "alice", {"task": "work", "expect": 0, "token": "finish", "seconds": 60})
        (self.repo / "proof.txt").write_text("fixture")
        self.cli("finish", "work", "--as", "alice", "--token", "finish", "--result", "Done", "--artifact", "proof.txt")
        self.assertEqual(self.demand()["ready_tasks"], [])
        self.rejected("ready", "alice", {"task": "work", "ready": True, "expect": 1}, "done")

    def test_startups_cover_work_before_arrival_and_admission_refences_demand(self):
        self.start("idle")
        self.offer("one"); self.offer("two")
        self.assertEqual(self.demand()["wanted_starts"], 1)
        self.start("warm", backlog=True)
        self.assertEqual(len(self.demand()["idle_residents"]), 2)
        self.assertEqual(self.demand()["wanted_starts"], 0)
        with self.assertRaisesRegex(ValueError, "demand changed"):
            self.start("duplicate", backlog=True)
        self.assertNotIn("duplicate", self.record.read()[0]["life"]["runs"])
        self.offer("three"); self.offer("four")
        self.start("last", backlog=True)
        self.assertEqual(self.demand()["wanted_starts"], 0)
        with self.assertRaisesRegex(ValueError, "three residents"):
            self.start("fourth", backlog=True)

    def test_expired_active_owner_remains_covered_until_observed_stop(self):
        self.offer("work"); self.start("worker", backlog=True)
        self.record.append("arrive", "resident-worker", {"name": "Worker"})
        self.record.append("claim", "resident-worker", {"task": "work", "expect": 0, "token": "old", "seconds": 1})
        later = time.time() + 10
        self.assertEqual(self.demand(later)["ready_tasks"], [])
        self.assertEqual(self.demand(later)["idle_residents"], [])
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": "worker",
            "outcome": "interrupted", "exit_code": None, "usage": {}, "elapsed_seconds": 1})
        self.assertEqual(self.demand()["ready_tasks"], ["work"])
        self.assertEqual(self.demand()["wanted_starts"], 1)
        self.assertEqual(self.record.read()[0]["tasks"]["work"]["generation"], 1)

    def test_task_help_counts_once_and_assigned_helper_is_not_idle(self):
        self.offer("one"); self.offer("two")
        self.record.append("life", "alice", {"kind": "help", "request": "assist", "task": "one", "reason": "Witness"})
        self.assertEqual(self.demand()["ready_tasks"], ["two"])
        self.assertEqual(self.demand()["wanted_starts"], 2)
        self.start("helper", help_request="assist")
        self.assertEqual(self.demand()["idle_residents"], [])
        self.assertEqual(self.demand()["wanted_starts"], 1)
        self.start("worker", backlog=True)
        self.assertEqual(self.demand()["wanted_starts"], 0)
        self.record.append("life", "alice", {"kind": "help", "request": "general", "reason": "Independent work"})
        self.assertEqual(self.demand()["wanted_starts"], 1)

    def test_competing_readiness_updates_cannot_silently_overwrite(self):
        self.offer("race")
        children = [self.process("ready", "race", "--as", actor, "--expect", "0", *flags)
                    for actor, flags in (("alice", []), ("bob", ["--blocked"]))]
        codes = []
        for child in children:
            child.communicate(timeout=20); codes.append(child.returncode)
        self.assertEqual(sorted(codes), [0, 2])
        self.assertEqual(self.record.read()[0]["tasks"]["race"]["generation"], 1)


class ReadyMailboxTests(MailboxCase):
    def test_fixed_client_creates_queues_and_withdraws_only_own_actor_requests(self):
        self.arrive()
        self.call("task", "ready-work", "--as", self.resident, "--title", "Ready",
                  "--description", "Independent fixture", "--ready")
        self.assertTrue(self.record.read()[0]["tasks"]["ready-work"]["ready"])
        self.call("ready", "ready-work", "--as", self.resident, "--expect", "0", "--blocked")
        self.assertFalse(self.record.read()[0]["tasks"]["ready-work"]["ready"])
        self.collect(self.start("ready", "ready-work", "--as", "alice", "--expect", "1"), success=False)
        self.call("ready", "ready-work", "--as", self.resident, "--expect", "1")
        self.assertTrue(self.record.read()[0]["tasks"]["ready-work"]["ready"])
        self.assertEqual(self.record.read()[0]["tasks"]["ready-work"]["generation"], 2)
