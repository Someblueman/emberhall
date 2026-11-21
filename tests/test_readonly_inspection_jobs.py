"""Real bounded inspection workers alongside the serialized action worker."""
import fcntl
import time
import zipfile
from unittest.mock import patch

from house import mailbox_jobs
from house.home_work import contribution, room
from house.record import Record
from tests.support import SOURCE
from tests.test_mailbox import MailboxCase


class InspectionJobTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.arrive()
        self.record._mailbox_runtime = self.runtime
        # ps is unavailable in resident/candidate sandboxes. Model only process
        # enumeration with our exact owned Popen handles; Git, workers, signals,
        # durable receipts and inherited kernel locks remain real. This does not
        # witness host-wide process identification or descendant recovery.
        for name, replacement in (("group_members", self.members), ("group_stopped", self.stopped)):
            observation = patch("house.mailbox_jobs." + name, side_effect=replacement)
            observation.start()
            self.addCleanup(observation.stop)
        self.addCleanup(lambda: mailbox_jobs.stop(self.record, self.run))
        self.author = "inspection-author"
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": self.author,
            "resident": "author", "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + self.author,
            "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "author", {"name": "Author"})
        author_room = room(self.record, self.private, self.author, self.base)
        (author_room / "note.md").write_text("Committed inspection bytes.\n")
        contribution(author_room, self.base, self.private / self.author / "contribution.json",
                     journal_artifacts={})
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": self.author,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})

    def members(self, pgid):
        for job, child in getattr(self.record, "_mailbox_processes", {}).items():
            if child.pid == pgid:
                return [job] if child.poll() is None else []
        raise AssertionError("fixture queried a group it does not own")

    def stopped(self, pgid):
        for child in getattr(self.record, "_mailbox_processes", {}).values():
            if child.pid == pgid:
                child.wait(timeout=5)
                return True
        raise AssertionError("fixture queried a group it does not own")

    def enqueue(self, name, *mode):
        return mailbox_jobs.enqueue(self.record, self.run,
            ["integrate", self.author, "--as", self.resident, *mode], name)

    def wait_result(self, job):
        deadline = time.monotonic() + 10
        while mailbox_jobs.result(self.record, job) is None and time.monotonic() < deadline:
            mailbox_jobs.tick(self.record)
            time.sleep(.02)
        result = mailbox_jobs.result(self.record, job)
        self.assertIsNotNone(result, "worker did not finish within fixture deadline")
        return result

    def metadata(self, job):
        return mailbox_jobs.read(self.private / "jobs" / job / "job.json")

    def paused_runtime(self, *, mutation=False):
        runtime = self.private / "paused-inspection.pyz"
        with zipfile.ZipFile(runtime, "w") as archive:
            for file in (SOURCE / "house").glob("*.py"):
                content = file.read_bytes()
                if file.name == "resident_actions.py":
                    content += b'''
_original_execute = execute
def execute(record, workspace, resident, run, argv, requestid):
 from house import integrate
 import time
 original_source = integrate.source
 def source(*args, **kwargs):
  value = original_source(*args, **kwargs)
  if not kwargs.get("admitted"): (workspace / "source-admitted").touch()
  if kwargs.get("admitted") and HOLD_MUTATION:
   (workspace / "mutation-entered").touch()
   deadline = time.monotonic() + 20
   while not (workspace / "proceed").exists() and time.monotonic() < deadline: time.sleep(.02)
  return value
 integrate.source = source
 original = integrate.inspect_contribution
 def pause(*args, **kwargs):
  if not HOLD_MUTATION:
   (workspace / "inspection-entered").touch()
   deadline = time.monotonic() + 20
   while not (workspace / "proceed").exists() and time.monotonic() < deadline: time.sleep(.02)
  return original(*args, **kwargs)
 integrate.inspect_contribution = pause
 return _original_execute(record, workspace, resident, run, argv, requestid)
'''.replace(b'HOLD_MUTATION', str(mutation).encode())
                archive.writestr("house/" + file.name, content)
        self.record._mailbox_runtime = runtime

    def wait_entered(self, marker="inspection-entered"):
        deadline = time.monotonic() + 10
        while not (self.workspace / marker).exists() and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue((self.workspace / marker).exists())

    def test_exact_inspection_finishes_while_mutation_holds_lock_and_mutations_serialize(self):
        self.paused_runtime(mutation=True)
        writer = self.enqueue("writer", "--reject", "Fixture rejection")
        mailbox_jobs.tick(self.record)
        self.wait_entered("mutation-entered")  # Real integrator holds integration.lock.
        child = self.record._mailbox_processes[writer]
        second_writer = self.enqueue("second-writer", "--reject", "Fixture rejection")
        inspection = self.enqueue("inspection", "--inspect", "--path", "note.md")
        result = self.wait_result(inspection)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["result"]["content"], "Committed inspection bytes.\n")
        self.assertIsNone(child.poll())
        self.assertEqual(self.metadata(writer)["status"], "running")
        self.assertEqual(self.metadata(second_writer)["status"], "queued")
        self.assertFalse((self.private / self.author / "integration.json").exists())
        (self.workspace / "proceed").touch()
        self.assertEqual(self.wait_result(writer)["result"]["status"], "rejected")
        self.assertEqual(self.wait_result(second_writer)["result"]["status"], "rejected")

    def test_three_inspections_run_at_once_each_under_its_own_inherited_lock(self):
        self.paused_runtime()
        looks = [self.enqueue(f"inspection-{n}", "--inspect", *(["--path", "note.md"] if n % 2 else []))
                 for n in range(4)]
        mailbox_jobs.tick(self.record)
        self.wait_entered()
        mailbox_jobs.tick(self.record)
        self.assertEqual(["running"] * 3 + ["queued"], [self.metadata(job)["status"] for job in looks])
        for name in ("inspection", "inspection-1", "inspection-2"):
            with (self.private / "jobs" / (name + ".lock")).open("a+b") as lock:
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        (self.workspace / "proceed").touch()
        for job in looks:
            self.assertTrue(self.wait_result(job)["ok"])

    def test_lane_reparses_entire_fixed_command_and_ignores_stored_labels(self):
        base = ["integrate", self.author, "--as", self.resident]
        for mode in (["--inspect"], ["--inspect", "--path", "note.md"]):
            item = {"argv": base + mode, "run": self.run, "resident": self.resident,
                    "lane": "worker"}
            self.assertEqual(mailbox_jobs.lane(self.record, item), "inspection")
        for argv in (base, base + ["--publish"], base + ["--reject", "No"],
                     base + ["--path", "note.md"],
                     ["council", "--as", self.resident, "status"],
                     ["checkpoint", "--as", self.resident, "--task", "x", "--token", "x"],
                     ["runtime-refresh", "--as", self.resident, "--task", "x"],
                     ["runtime-test", "--as", self.resident, "--task", "x", "--token", "x"],
                     ["review-complete", "--as", self.resident, "--task", "x", "--token", "x"]):
            self.assertEqual(mailbox_jobs.lane(self.record, {
                "argv": argv, "run": self.run, "resident": self.resident, "lane": "inspection"}), "worker")
        for argv in (base + ["--inspect", "--publish"], base + ["--inspect", "--reject", "No"],
                     base + ["--inspect", "--repo", "/tmp"],
                     base + ["--inspect", "--artifacts-from=/tmp"],
                     base + ["--inspect", "--unknown"],
                     ["integrate", self.author, "--as", "alice", "--inspect"],
                     ["council", "--as", self.resident, "authorize"],
                     ["integrate", self.author, "--as", self.resident, "--ins"],
                     ["verify"]):
            with self.subTest(argv=argv), self.assertRaises(ValueError):
                mailbox_jobs.lane(self.record, {"argv": argv, "run": self.run,
                                               "resident": self.resident})

    def test_inspection_still_checks_source_independence_and_exact_changed_path(self):
        jobs = [self.enqueue("wrong-path", "--inspect", "--path", "source.txt")]
        jobs.append(mailbox_jobs.enqueue(self.record, self.run,
            ["integrate", self.run, "--as", self.resident, "--inspect"], "active-source"))
        for job in jobs:
            result = self.wait_result(job)
            self.assertFalse(result["ok"], result)
        self.assertIn("exact changed", mailbox_jobs.result(self.record, jobs[0])["error"])
        self.assertIn("stopped resident", mailbox_jobs.result(self.record, jobs[1])["error"])
        self.assertFalse((self.private / self.author / "integration.json").exists())

    def test_stopped_requester_cancels_both_queues_but_preserves_started_jobs(self):
        self.paused_runtime()
        with (self.private / "integration.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            writer = self.enqueue("running-writer", "--reject", "Retain")
            inspection = self.enqueue("running-inspection", "--inspect")
            mailbox_jobs.tick(self.record)
            self.wait_entered()
            queued = [self.enqueue("queued-writer", "--reject", "Retain"),
                      self.enqueue("queued-inspection", "--inspect")]
            self.wait_entered("source-admitted")
            self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": self.run,
                "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
            mailbox_jobs.stop(self.record, self.run, running=False)
            for job in queued:
                self.assertFalse(mailbox_jobs.result(self.record, job)["ok"])
            for job in (writer, inspection):
                self.assertIsNone(self.record._mailbox_processes[job].poll())
                self.assertEqual(self.metadata(job)["status"], "running")
            (self.workspace / "proceed").touch()
        # Publication keeps its existing admitted-reviewer contract; inspection
        # still rechecks an awake independent reviewer when it reads the source.
        self.assertTrue(self.wait_result(writer)["ok"])
        inspected = self.wait_result(inspection)
        self.assertFalse(inspected["ok"], inspected)
        self.assertIn("different, awake resident", inspected["error"])
        stopped = self.enqueue("after-requester-exit", "--inspect")
        self.assertIn("stopped", self.wait_result(stopped)["error"])

    def test_recovery_stops_both_owned_lanes_retains_results_and_releases_locks(self):
        self.paused_runtime()
        with (self.private / "integration.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            writer = self.enqueue("recover-writer", "--reject", "Retain")
            inspection = self.enqueue("recover-inspection", "--inspect")
            mailbox_jobs.tick(self.record)
            self.wait_entered()
            fresh = Record(self.repo)
            mailbox_jobs.recover(fresh)
            for job in (writer, inspection):
                self.assertIsNotNone(self.record._mailbox_processes[job].poll())
                self.assertIn("interrupted", mailbox_jobs.result(fresh, job)["error"])
            previous = [mailbox_jobs.result(fresh, job) for job in (writer, inspection)]
            mailbox_jobs.recover(fresh)
            self.assertEqual([mailbox_jobs.result(fresh, job) for job in (writer, inspection)], previous)
        for name in ("worker", "inspection"):
            with (self.private / "jobs" / (name + ".lock")).open("a+b") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.assertFalse((self.private / self.author / "integration.json").exists())
        (self.workspace / "proceed").touch()
        following = self.enqueue("after-recovery", "--inspect")
        self.assertTrue(self.wait_result(following)["ok"])

    def test_timeout_is_per_lane_and_unknown_group_is_never_signalled(self):
        self.paused_runtime()
        with (self.private / "integration.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            writer = self.enqueue("timeout-writer", "--reject", "Retain")
            inspection = self.enqueue("timeout-inspection", "--inspect")
            mailbox_jobs.tick(self.record)
            self.wait_entered()
            item = self.metadata(inspection)
            item["started_at"] = time.time() - 1201
            mailbox_jobs.write(self.private / "jobs" / inspection / "job.json", item)
            mailbox_jobs.tick(self.record)
            self.assertIn("interrupted", mailbox_jobs.result(self.record, inspection)["error"])
            self.assertIsNone(self.record._mailbox_processes[writer].poll())
            unknown = self.metadata(writer)
            with patch("house.mailbox_jobs.group_members", return_value=["unrelated service"]), \
                    patch("house.mailbox_jobs.kill_group") as kill:
                with self.assertRaisesRegex(ValueError, "unidentified"):
                    mailbox_jobs.interrupt(self.record, unknown)
                kill.assert_not_called()
        self.assertTrue(self.wait_result(writer)["ok"])

    def test_inspection_runtime_and_durable_launch_gate_remain_enforced(self):
        job = self.enqueue("changed-runtime", "--inspect")
        original = self.runtime.read_bytes()
        self.runtime.write_bytes(b"changed pinned runtime")
        mailbox_jobs.tick(self.record)
        self.assertIn("before launch", mailbox_jobs.result(self.record, job)["error"])
        self.assertFalse(getattr(self.record, "_mailbox_processes", {}))
        self.runtime.write_bytes(original)
        job = self.enqueue("failed-gate", "--inspect")
        original_write = mailbox_jobs.write
        def refuse(path, value):
            if path.name == "job.json" and value["status"] == "running":
                raise ValueError("injected durable receipt failure")
            return original_write(path, value)
        with patch("house.mailbox_jobs.write", side_effect=refuse):
            mailbox_jobs.tick(self.record)
        self.assertIn("failed to launch", mailbox_jobs.result(self.record, job)["error"])
        self.assertFalse(mailbox_jobs.result(self.record, job)["ok"])

    def test_completed_inspection_result_survives_lost_coordinator_handles(self):
        job = self.enqueue("saved-inspection", "--inspect", "--path", "note.md")
        mailbox_jobs.tick(self.record)
        self.record._mailbox_processes[job].wait(timeout=10)
        fresh = Record(self.repo)
        mailbox_jobs.recover(fresh)
        result = mailbox_jobs.result(fresh, job)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["result"]["content"], "Committed inspection bytes.\n")
        mailbox_jobs.recover(fresh)
        self.assertEqual(mailbox_jobs.result(fresh, job), result)

    def test_duplicate_running_lane_fails_closed_before_start_or_signal(self):
        for mode, count in ((["--inspect"], mailbox_jobs.SLOTS["inspection"] + 1),
                            (["--publish"], mailbox_jobs.SLOTS["worker"] + 1)):
            item = {"argv": ["integrate", self.author, "--as", self.resident, *mode],
                    "run": self.run, "resident": self.resident, "status": "running"}
            with patch("house.mailbox_jobs.jobs", return_value=[item.copy() for _ in range(count)]), \
                    patch("house.mailbox_jobs.start") as start, \
                    patch("house.mailbox_jobs.interrupt") as interrupt:
                with self.assertRaisesRegex(ValueError, "more trusted action workers"):
                    mailbox_jobs.tick(self.record)
                start.assert_not_called()
                interrupt.assert_not_called()
