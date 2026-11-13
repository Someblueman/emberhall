"""Real journal rejection boundaries for a mixed, continuous household."""
import time
import json

from tests.support import HouseCase


class LifeTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})

    def life(self, data, actor="alice"):
        return self.record.append("life", actor, data)

    def start(self, run):
        return {"kind": "run-start", "run": run, "resident": "resident-" + run,
                "agent": "codex", "model": "gpt-6.1-sol", "source_head": "a" * 40,
                "workspace": "residents/" + run, "policy_revision": "baseline", "mode": "work"}

    def test_capacity_is_journal_enforced_and_interruption_frees_slot(self):
        for n in range(3):
            self.life(self.start(str(n)), "watch-keeper")
        self.rejected("life", "watch-keeper", self.start("4"), "three residents")
        self.life({"kind": "run-finish", "run": "0", "outcome": "interrupted",
                   "exit_code": None, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        self.life(self.start("4"), "watch-keeper")
        self.assertEqual(len(self.record.read()[0]["life"]["runs"]), 4)

    def test_concurrent_process_admission_cannot_exceed_three(self):
        children = [self.process("life", "--as", "watch-keeper", "--data", json.dumps(self.start(str(n))))
                    for n in range(8)]
        codes = []
        for child in children:
            child.communicate(timeout=30)
            codes.append(child.returncode)
        self.assertEqual(codes.count(0), 3)
        self.assertEqual(codes.count(2), 5)
        self.assertEqual(len(self.record.read()[0]["life"]["runs"]), 3)

    def test_model_allowlist_controller_and_budget(self):
        self.rejected("life", "alice", self.start("x"), "only the supervisor")
        bad = self.start("x") | {"model": "openrouter/anything"}
        self.rejected("life", "watch-keeper", bad, "outside")
        self.life({"kind": "budget", "agent": "codex", "until": time.time() + 3600,
                   "reason": "Observed usage limit"}, "watch-keeper")
        self.rejected("life", "watch-keeper", self.start("x"), "cooling down")

    def test_ambition_cas_preserves_other_resident_thread(self):
        data = {"kind": "ambition", "ambition": "recovery", "title": "Recover safely",
                "description": "Useful disaster recovery", "status": "growing",
                "next_step": "Verify an actual backup", "expect": 0}
        self.life(data)
        self.rejected("life", "bob", data | {"next_step": "Overwrite"}, "generation changed")
        self.life(data | {"expect": 1, "next_step": "Add portable inventory"}, "bob")
        self.assertEqual(self.record.read()[0]["life"]["ambitions"]["recovery"]["generation"], 2)

    def test_activity_requires_existing_room_and_own_live_task(self):
        self.task()
        self.rejected("life", "alice", {"kind": "activity", "room": "fake"}, "unknown room")
        self.rejected("life", "alice", {"kind": "activity", "room": "workshop", "task": "work"},
                      "own live task")
        self.record.append("claim", "alice", {"task": "work", "token": "t", "expect": 0, "seconds": 60})
        self.life({"kind": "activity", "room": "workshop", "task": "work"})

    def test_process_launch_is_single_observation_and_unknown_usage_stays_empty(self):
        self.life(self.start("x"), "watch-keeper")
        data = {"kind": "run-launched", "run": "x", "pgid": 12345}
        self.life(data, "watch-keeper")
        self.rejected("life", "watch-keeper", data, "already launched")
        self.life({"kind": "run-finish", "run": "x", "outcome": "quota",
                   "exit_code": 1, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        run = self.record.read()[0]["life"]["runs"]["x"]
        self.assertEqual(run["usage"], {})
        self.assertGreater(run["launched_sequence"], run["started_sequence"])

    def test_help_is_taken_once_and_artifacts_can_come_from_private_checkout(self):
        self.life({"kind": "help", "request": "test-repair", "reason": "Independent witness"})
        self.life(self.start("x") | {"help_request": "test-repair"}, "watch-keeper")
        self.rejected("life", "watch-keeper", self.start("y") | {"help_request": "test-repair"},
                      "already taken")
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "t", "expect": 0, "seconds": 60})
        private = self.root / "source"
        private.mkdir()
        (private / "evidence.txt").write_text("actual work in an isolated source checkout")
        self.cli("--artifacts-from", str(private), "finish", "work", "--as", "alice", "--token", "t",
                 "--result", "preserved", "--artifact", "evidence.txt")
        self.assertIn("evidence.txt", self.record.read()[0]["tasks"]["work"]["artifacts"])

    def test_quiet_resident_wakes_on_actual_journal_change(self):
        cursor = self.record.read()[0]["sequence"]
        waiting = self.process("wait", "--as", "alice", "--after", str(cursor), "--seconds", "10")
        self.record.append("say", "bob", {"text": "Something worth noticing"})
        out, err = waiting.communicate(timeout=12)
        self.assertEqual(waiting.returncode, 0, err)
        self.assertTrue(json.loads(out)["changed"])

    def test_wren_stopped_worker_lease_is_fenced_for_immediate_successor(self):
        self.life(self.start("x"), "watch-keeper")
        self.record.append("arrive", "resident-x", {"name": "Former worker"})
        self.task()
        self.record.append("claim", "resident-x", {"task": "work", "token": "old", "expect": 0, "seconds": 86400})
        self.life({"kind": "run-finish", "run": "x", "outcome": "quota",
                   "exit_code": 1, "usage": {}, "elapsed_seconds": 2}, "watch-keeper")
        self.record.append("claim", "bob", {"task": "work", "token": "new", "expect": 1, "seconds": 60})
        self.rejected("renew", "resident-x", {"task": "work", "token": "old", "seconds": 60}, "stale")
        self.assertEqual(self.record.read()[0]["life"]["runs"]["x"]["released_tasks"], ["work"])

    def test_concurrent_shorter_failure_cannot_clear_quota_cooldown(self):
        until = time.time() + 900
        self.life({"kind": "budget", "agent": "muse", "until": until, "reason": "quota"}, "watch-keeper")
        self.life({"kind": "budget", "agent": "muse", "until": until - 600, "reason": "failed"}, "watch-keeper")
        self.assertEqual(self.record.read()[0]["life"]["budgets"]["muse"]["until"], until)

    def test_resident_cannot_mislabel_its_supervised_agent_kind(self):
        self.life(self.start("x"), "watch-keeper")
        self.record.append("arrive", "resident-x", {"name": "Worker"})
        self.rejected("life", "resident-x", {"kind": "identity", "agent": "muse", "model": "muse-ember-1.0"},
                      "differs from actual")

    def test_native_success_without_resolved_help_requeues_the_request(self):
        self.life({"kind": "help", "request": "still-needed", "reason": "Needs an actual handoff"})
        self.life(self.start("x") | {"help_request": "still-needed"}, "watch-keeper")
        self.life({"kind": "run-finish", "run": "x", "outcome": "success",
                   "exit_code": 0, "usage": {}, "elapsed_seconds": 1}, "watch-keeper")
        request = self.record.read()[0]["life"]["requests"]["still-needed"]
        self.assertEqual(request["status"], "pending")
        self.assertNotIn("run", request)
