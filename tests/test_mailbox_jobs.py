"""Real trusted worker processes; synthetic house fixtures, never live approvals."""
import json
import os
import signal
import subprocess
import sys
import time
import unittest
import uuid
import zipfile
from unittest.mock import patch

from house import council, mailbox, mailbox_jobs, resident_actions
from house.record import Record
from tests.support import SOURCE
from tests.test_council import approval
from tests.test_mailbox import MailboxCase


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host process-recovery fixture requires macOS setuid ps")
class JobTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.record._mailbox_runtime = self.runtime
        self.addCleanup(lambda: mailbox_jobs.stop(self.record, self.run))
        self.arrive()

    def collect(self, process, success=True):
        deadline = time.monotonic() + 15
        while process.poll() is None and time.monotonic() < deadline:
            mailbox.service(self.record, self.private, self.run)
            mailbox_jobs.tick(self.record)
            self.assertLessEqual(sum(item["status"] == "running" for item in mailbox_jobs.jobs(self.record)), 1)
            time.sleep(0.02)
        output, errors = process.communicate(timeout=2)
        self.assertEqual(process.returncode, 0 if success else 2, (output, errors))
        return json.loads(output) if success else errors

    def fixture_runtime(self, suffix):
        path = self.private / "worker-fixture.pyz"
        with zipfile.ZipFile(path, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                content = file.read_bytes()
                if file.name == "resident_actions.py":
                    content += suffix.encode()
                archive.writestr("house/" + file.name, content)
        self.record._mailbox_runtime = path

    def test_jobs_use_pinned_code_and_client_ignores_workspace_module_shadows(self):
        for name in ("pathlib.py", "json.py"):
            (self.workspace / name).write_text("raise RuntimeError('workspace module must never load')\n")
        first = self.start("council", "--as", self.resident, "--request", "status-one", "status")
        second = self.start("council", "--as", self.resident, "--request", "status-two", "status")
        self.assertIsNone(self.collect(first)["council"])
        self.assertIsNone(self.collect(second)["council"])
        self.assertEqual([item["status"] for item in mailbox_jobs.jobs(self.record)], ["done", "done"])
        # A repeated explicit request uses its preserved result, not another worker.
        self.assertIsNone(self.call("council", "--as", self.resident, "--request", "status-one", "status")["council"])
        self.assertEqual(len(mailbox_jobs.jobs(self.record)), 2)

    def test_checkpoint_worker_exports_private_prefix_and_recovers_lost_result(self):
        self.call("task", "checkpoint-work", "--as", self.resident,
                  "--title", "Checkpoint", "--description", "Synthetic export fixture")
        self.call("claim", "checkpoint-work", "--as", self.resident,
                  "--expect", "0", "--token", "checkpoint-token")
        before = self.record.read()
        argv = ["checkpoint", "--as", self.resident, "--task", "checkpoint-work",
                "--token", "checkpoint-token"]
        job = mailbox_jobs.enqueue(self.record, self.run, argv, "checkpoint-worker-proof")
        mailbox_jobs.tick(self.record)
        child = self.record._mailbox_processes[job]
        child.wait(timeout=15)
        result_path = self.private / "jobs" / job / "result.json"
        original = json.loads(result_path.read_text())
        self.assertTrue(original["ok"], original)
        result_path.unlink()  # Accepted export, lost worker result.
        fresh = Record(self.repo)
        mailbox_jobs.recover(fresh)
        recovered = mailbox_jobs.result(fresh, job)
        self.assertEqual(recovered, original)
        receipt = recovered["result"]
        self.assertEqual(receipt["head"], before[2])
        restored = Record(self.new_repo("export-restored"))
        restored.restore(str(self.workspace / receipt["bundle"]), receipt["anchor"])
        self.assertEqual(restored.read(), before)
        self.assertEqual(self.record.read(), before)
        self.record._mailbox_processes.clear()

    def test_action_parser_denies_owner_initializers_roots_and_other_identity(self):
        for argv in (["council", "--as", self.resident, "authorize"],
                     ["checkpoint", "--as", self.resident, "--task", "x", "--token", "x", "--destination", "/tmp"],
                     ["checkpoint", "--as", "alice", "--task", "x", "--token", "x"],
                     ["checkpoint", "--as", self.resident, "--task", "x"],
                     ["council", "--as", self.resident, "authorize-wake", "--source", "x"],
                     ["runtime-test", "--as", self.resident, "--task", "x", "--token", "x", "--source-repo", "/tmp"],
                     ["runtime-refresh", "--as", "alice", "--task", "x"],
                     ["integrate", "other", "--as", self.resident, "--repo", "/tmp"]):
            key = self.raw(argv)
            for _ in range(3):
                mailbox.service(self.record, self.private, self.run)
            response = json.loads((self.responses / (key + ".json")).read_text())
            self.assertFalse(response["ok"])
        self.assertEqual(mailbox_jobs.jobs(self.record), [])

    def test_long_worker_does_not_block_other_mail_and_recovery_preserves_interruption(self):
        self.fixture_runtime("\ndef execute(*args):\n import time\n time.sleep(30)\n return {'unexpected': True}\n")
        job = mailbox_jobs.enqueue(self.record, self.run,
            ["council", "--as", self.resident, "status"], "slow-fixture-job")
        before = time.monotonic()
        mailbox_jobs.tick(self.record)
        self.assertLess(time.monotonic() - before, 2)
        self.assertTrue(self.call("verify")["valid"])
        fresh = Record(self.repo)  # Lost coordinator memory, same durable job.
        mailbox_jobs.recover(fresh)
        response = mailbox_jobs.result(fresh, job)
        self.assertFalse(response["ok"])
        self.assertIn("interrupted", response["error"])
        mailbox_jobs.stop(self.record, self.run)  # Reap the first parent's handle.
        for child in self.record._mailbox_processes.values():
            child.wait(timeout=5)
        self.record._mailbox_processes.clear()

    def test_known_worker_result_survives_coordinator_memory_loss(self):
        job = mailbox_jobs.enqueue(self.record, self.run,
            ["council", "--as", self.resident, "status"], "known-fixture-job")
        mailbox_jobs.tick(self.record)
        child = self.record._mailbox_processes[job]
        child.wait(timeout=10)
        fresh = Record(self.repo)
        mailbox_jobs.recover(fresh)
        self.assertTrue(mailbox_jobs.result(fresh, job)["ok"])
        self.record._mailbox_processes.clear()

    def test_worker_cannot_launch_before_its_persistent_receipt(self):
        job = mailbox_jobs.enqueue(self.record, self.run,
            ["council", "--as", self.resident, "status"], "rejected-fixture-job")
        original = mailbox_jobs.write
        def refuse(path, value):
            if path.name == "job.json" and value["status"] == "running":
                raise ValueError("injected receipt rejection")
            return original(path, value)
        with patch("house.mailbox_jobs.write", refuse):
            mailbox_jobs.tick(self.record)
        response = mailbox_jobs.result(self.record, job)
        self.assertFalse(response["ok"])
        self.assertIn("launch", response["error"])

    def test_queued_action_dies_with_requester_and_unknown_group_is_not_signalled(self):
        job = mailbox_jobs.enqueue(self.record, self.run,
            ["council", "--as", self.resident, "status"], "stopped-fixture-job")
        mailbox_jobs.stop(self.record, self.run)
        self.assertFalse(mailbox_jobs.result(self.record, job)["ok"])
        item = {"id": job, "pgid": 12345, "resident": self.resident, "run": self.run,
                "argv": ["council", "--as", self.resident, "status"], "requestid": "unknown"}
        with patch("house.mailbox_jobs.group_members", return_value=["unrelated service"]), \
                patch("house.mailbox_jobs.kill_group") as kill:
            with self.assertRaisesRegex(ValueError, "unidentified"):
                mailbox_jobs.interrupt(self.record, item)
            kill.assert_not_called()

    @unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1", "host sandbox fixture cannot nest")
    def test_worker_death_during_sandbox_test_keeps_descendant_identifiable(self):
        self.fixture_runtime("\ndef execute(record, workspace, *args):\n"
            " import sys\n from house.test_sandbox import run\n"
            " with (workspace/'sandbox-tests.log').open('w') as output:\n"
            "  return run([sys.executable,'-c',\"from pathlib import Path;import time;Path('test-started').write_text('yes');time.sleep(30)\"],workspace,stdout=output,timeout=60)\n")
        job = mailbox_jobs.enqueue(self.record, self.run,
            ["council", "--as", self.resident, "status"], "sandbox-descendant-fixture")
        mailbox_jobs.tick(self.record)
        child = self.record._mailbox_processes[job]
        deadline = time.monotonic() + 10
        while not (self.workspace / "test-started").exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.03)
        self.assertTrue((self.workspace / "test-started").exists())
        os.kill(child.pid, signal.SIGKILL)
        child.wait(timeout=5)
        self.assertTrue(any(job in command for command in mailbox_jobs.group_members(child.pid)))
        fresh = Record(self.repo)
        mailbox_jobs.recover(fresh)
        self.assertTrue(mailbox_jobs.group_stopped(child.pid))
        self.assertFalse(mailbox_jobs.result(fresh, job)["ok"])
        self.record._mailbox_processes.clear()
        fresh._mailbox_runtime = self.runtime
        following = mailbox_jobs.enqueue(fresh, self.run,
            ["council", "--as", self.resident, "status"], "after-crash-fixture")
        deadline = time.monotonic() + 10
        while mailbox_jobs.result(fresh, following) is None and time.monotonic() < deadline:
            mailbox_jobs.tick(fresh)
            time.sleep(0.03)
        self.assertTrue(mailbox_jobs.result(fresh, following)["ok"])

    def test_changed_runtime_is_rejected_before_worker_imports(self):
        job = mailbox_jobs.enqueue(self.record, self.run,
            ["council", "--as", self.resident, "status"], "runtime-change-fixture")
        self.runtime.write_bytes(b"not the pinned archive")
        mailbox_jobs.tick(self.record)
        self.assertFalse(getattr(self.record, "_mailbox_processes", {}))
        reply = mailbox_jobs.result(self.record, job)
        self.assertFalse(reply["ok"])
        self.assertIn("before launch", reply["error"])


class CouncilActionTests(MailboxCase):
    def setUp(self):
        super().setUp()
        # Separate real repository with the approved fixture house ID. This is a
        # test-only founding identity, not a live Steward approval.
        approved = Record(self.new_repo("approved"))
        with patch("house.record.uuid.uuid4", side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
            approved.found("Approved fixture", "Original rules")
        for actor in ("alice", "watch-keeper"):
            approved.append("arrive", actor, {"name": actor})
        approved.append("council-authorize", "alice", approval())
        approved.append("life", "watch-keeper", {"kind": "run-start", "run": self.run,
            "resident": self.resident, "agent": "codex", "model": "gpt-6.1-sol", "source_head": self.base,
            "workspace": "residents/" + self.run, "policy_revision": "fixture", "mode": "work"})
        approved.append("life", "watch-keeper", {"kind": "run-launched", "run": self.run, "pgid": os.getpid()})
        approved.append("arrive", self.resident, {"name": "Resident"})
        self.approved = approved
        self.action_room = approved.common / "house-home" / "residents" / self.run
        self.action_room.mkdir(parents=True)

    def execute(self, *args, request="action-fixture"):
        return resident_actions.execute(self.approved, self.action_room, self.resident, self.run,
            ["council", "--as", self.resident, *args], request)

    def test_proposal_is_local_snapshot_and_cannot_skip_trial_or_wake_authorization(self):
        (self.action_room / "proposal.md").write_text("Preserve useful errors.")
        proposed = self.execute("propose", "rule-one", "--title", "One", "--file", "proposal.md", "--reason", "Observed")
        (self.action_room / "proposal.md").write_text("Changed after acceptance")
        self.assertEqual(self.execute("propose", "rule-one", "--title", "One", "--file", "proposal.md",
                                     "--reason", "Observed")["sequence"], proposed["sequence"])
        self.assertEqual(self.approved.read()[0]["proposals"]["rule-one"]["text"], "Preserve useful errors.")
        with self.assertRaisesRegex(ValueError, "trial"):
            self.execute("endorse", "rule-one", "--evidence", "Not enough", request="endorse-fixture")
        with self.assertRaisesRegex(ValueError, "authorization"):
            self.execute("propose", "wake-one", "--title", "Wake", "--file", "proposal.md",
                         "--reason", "Fixture", "--mode", "wake-prompt", request="wake-fixture")
        with self.assertRaisesRegex(ValueError, "relative"):
            self.execute("propose", "escape", "--title", "Escape", "--file", "../proposal.md", "--reason", "No",
                         request="escape-fixture")
        original = self.approved.read()[0]["rule_revision"]
        # Stub only the network transport. The real journal gate still rejects.
        with patch("house.steward.sync", return_value={}):
            with self.assertRaisesRegex(ValueError, "trial"):
                self.execute("enact", "rule-one", request="enact-fixture")
        self.assertEqual(self.approved.read()[0]["rule_revision"], original)
