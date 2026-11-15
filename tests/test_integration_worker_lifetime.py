"""Real trusted workers outlive a requester, but not their coordinator."""
import os
import time
import unittest
import zipfile
from pathlib import Path

from house import mailbox_jobs
from house.home import Coordinator
from house.home_work import contribution, git, room
from house.record import Record
from tests.support import SOURCE
from tests.test_mailbox import MailboxCase


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                 "host process-recovery fixture requires macOS setuid ps")
class IntegrationWorkerLifetimeTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.arrive()
        runtime = self.private / "lifetime.pyz"
        with zipfile.ZipFile(runtime, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                content = file.read_bytes()
                if file.name == "resident_actions.py":
                    content += b'''\ndef execute(record, workspace, resident, run, argv, requestid):
 import time
 from pathlib import Path
 marker = Path(workspace) / "executions"
 with marker.open("a") as out: out.write(run + " " + requestid + "\\n")
 deadline = time.monotonic() + 20
 while not (Path(workspace) / "proceed").exists() and time.monotonic() < deadline: time.sleep(.02)
 return {"run": run, "request": requestid}
'''
                archive.writestr("house/" + file.name, content)
        self.coordinator = Coordinator(self.record, runtime)
        self.addCleanup(lambda: mailbox_jobs.stop(self.record, self.run))
        self.argv = ["integrate", "fixture-contribution", "--as", self.resident, "--publish"]

    def launch(self, request="integration-request"):
        job = mailbox_jobs.enqueue(self.record, self.run, self.argv, request)
        mailbox_jobs.tick(self.record)
        child = self.record._mailbox_processes[job]
        deadline = time.monotonic() + 10
        while not (self.workspace / "executions").exists() and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue((self.workspace / "executions").exists())
        return job, child

    def finish_resident(self):
        self.record.append("sleep", self.resident, {"through": self.record.read()[0]["sequence"], "note": "Fixture handoff"})
        self.coordinator.finish(self.run, {"outcome": "success", "exit_code": 0,
                                           "usage": {}, "elapsed_seconds": 1})

    def test_reaped_requester_keeps_running_action_and_cancels_queue(self):
        job, child = self.launch()
        queued = mailbox_jobs.enqueue(self.record, self.run, self.argv, "queued-request")
        self.finish_resident()
        self.assertIsNone(child.poll())
        self.assertFalse(mailbox_jobs.result(self.record, queued)["ok"])
        self.assertEqual(mailbox_jobs.enqueue(self.record, self.run, self.argv, "integration-request"), job)
        (self.workspace / "proceed").touch()
        child.wait(timeout=10)
        self.coordinator.reap()  # No native residents remain to drive polling.
        self.assertEqual(mailbox_jobs.result(self.record, job), {"ok": True, "result":
                         {"run": self.run, "request": "integration-request"}})
        self.coordinator.reap()
        self.assertEqual((self.workspace / "executions").read_text().splitlines(),
                         [self.run + " integration-request"])
        self.assertFalse(mailbox_jobs.result(self.record, queued)["ok"])

    def test_real_integration_completes_once_after_reviewer_exit(self):
        author_run = "author-fixture"
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": author_run,
            "resident": "author", "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + author_run,
            "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "author", {"name": "Author"})
        author_room = room(self.record, self.private, author_run, self.base)
        project = author_room / "projects" / "fixture"
        project.mkdir(parents=True)
        (project / "note.md").write_text("A contribution.\n")
        (self.private / author_run).mkdir()
        contribution(author_room, self.base, self.private / author_run / "contribution.json", journal_artifacts={})
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": author_run,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        runtime = self.private / "real-integration.pyz"
        with zipfile.ZipFile(runtime, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                content = file.read_bytes()
                if file.name == "resident_actions.py":
                    content += b'''\n_original_execute = execute
def execute(record, workspace, resident, run, argv, requestid):
 from house import integrate
 import time
 original = integrate.test_sandbox.run
 def pause(*args, **kwargs):
  (workspace / "gate-entered").touch()
  deadline = time.monotonic() + 20
  while not (workspace / "proceed").exists() and time.monotonic() < deadline: time.sleep(.02)
  return original(*args, **kwargs)
 integrate.test_sandbox.run = pause
 return _original_execute(record, workspace, resident, run, argv, requestid)
'''
                archive.writestr("house/" + file.name, content)
        self.record._mailbox_runtime = runtime
        argv = ["integrate", author_run, "--as", self.resident, "--publish"]
        job = mailbox_jobs.enqueue(self.record, self.run, argv, "actual-integration")
        mailbox_jobs.tick(self.record)
        child = self.record._mailbox_processes[job]
        deadline = time.monotonic() + 15
        while not (self.workspace / "gate-entered").exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue((self.workspace / "gate-entered").exists())
        self.finish_resident()
        (self.workspace / "proceed").touch()
        child.wait(timeout=30)
        self.coordinator.reap()
        result = mailbox_jobs.result(self.record, job)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["result"]["status"], "integrated")
        before = git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(mailbox_jobs.enqueue(self.record, self.run, argv, "actual-integration"), job)
        self.coordinator.reap()
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), before)
        self.assertEqual(len(list(self.private.glob("integration-*.tests.log"))), 1)

    def test_coordinator_shutdown_and_timeout_stop_orphaned_worker(self):
        job, child = self.launch()
        self.finish_resident()
        self.coordinator.close()
        self.assertIsNotNone(child.poll())
        self.assertIn("interrupted", mailbox_jobs.result(self.record, job)["error"])
        # Recovery is idempotent and preserves the terminal response.
        previous = mailbox_jobs.result(self.record, job)
        mailbox_jobs.recover(Record(self.repo))
        self.assertEqual(mailbox_jobs.result(self.record, job), previous)

    def test_timeout_clears_lock_after_requester_exit(self):
        job, child = self.launch()
        self.finish_resident()
        path = self.private / "jobs" / job / "job.json"
        item = mailbox_jobs.read(path)
        item["started_at"] = time.time() - 1201
        mailbox_jobs.write(path, item)
        self.coordinator.reap()
        self.assertIsNotNone(child.poll())
        self.assertIn("interrupted", mailbox_jobs.result(self.record, job)["error"])
        import fcntl
        with (self.private / "jobs" / "worker.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
