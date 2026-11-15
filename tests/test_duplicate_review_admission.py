"""Prompt, durable retry responses for equivalent pending publish requests."""
import hashlib
import json
import os
import subprocess
import time
import unittest
import uuid
import zipfile
from unittest.mock import patch

from house import maintenance, mailbox, mailbox_jobs
from house.files import workspace_path
from house.home_work import client, git, room
from house.record import Record
from tests.test_mailbox import MailboxCase
from tests import test_runtime
from tests.support import SOURCE


class DuplicateAcceptanceTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.record._mailbox_runtime = self.runtime
        self.other = "other-reviewer"
        self.other_run = uuid.uuid4().hex

    def argv(self, target="contribution-one", resident=None, mode="--publish", reason="No"):
        resident = self.other if resident is None else resident
        base = ["integrate", target, "--as", resident]
        return base + (["--publish"] if mode == "--publish" else ["--reject", reason]
                       if mode == "--reject" else ["--inspect"])

    def ask(self, target="contribution-one", *, resident=None, run=None, request=None,
            mode="--publish", reason="No"):
        resident = self.resident if resident is None else resident
        return mailbox_jobs.enqueue(self.record, self.run if run is None else run,
            self.argv(target, resident, mode, reason), request or uuid.uuid4().hex)

    def stored(self, job):
        return mailbox_jobs.read(self.private / "jobs" / job / "job.json")

    def answer(self, job):
        answer = mailbox_jobs.result(self.record, job)
        self.assertIsNotNone(answer)
        self.assertTrue(answer["ok"], answer)
        return answer["result"]

    def recorded(self, *, target="contribution-one", resident=None, run=None,
                 mode="--publish", reason="No", status="queued", result=None):
        resident = self.other if resident is None else resident
        run = self.other_run if run is None else run
        request = uuid.uuid4().hex
        job = hashlib.sha256(request.encode()).hexdigest()
        path = self.private / "jobs" / job
        path.mkdir(mode=0o700, parents=True)
        mailbox_jobs.write(path / "job.json", {"id": job, "run": run, "resident": resident,
            "argv": self.argv(target, resident, mode, reason), "requestid": request,
            "runtime": str(self.runtime),
            "runtime_sha256": hashlib.sha256(self.runtime.read_bytes()).hexdigest(),
            "status": status, "created_at": 1.0})
        if result is not None:
            mailbox_jobs.write(path / "result.json", result)
        return job

    def test_equivalent_peer_publish_gets_durable_nonterminal_response(self):
        first = self.recorded()
        mine = self.ask(request="peer-publish")
        answer = self.answer(mine)
        self.assertEqual((answer["status"], answer["existing_job"], answer["intent"]),
                         ("in-progress", first, "publish"))
        self.assertEqual(answer["existing_status"], "queued")
        self.assertEqual(self.stored(mine)["duplicate_of"], first)
        self.assertEqual(self.stored(first)["status"], "queued")
        self.assertEqual(sum(job["status"] == "queued" for job in mailbox_jobs.jobs(self.record)), 1)

    def test_running_publish_is_reported_but_terminal_result_is_not(self):
        first = self.recorded(status="running")
        mine = self.ask(request="running-peer")
        self.assertEqual(self.answer(mine)["existing_job"], first)
        owner = self.stored(first)
        mailbox_jobs.complete(self.record, owner, {"ok": True, "result": {"status": "accepted"}})
        retry = self.ask(request="after-terminal")
        self.assertIsNone(mailbox_jobs.result(self.record, retry))
        self.assertEqual(self.stored(retry)["status"], "queued")

    def test_same_exact_retry_repairs_interruption_after_queued_metadata(self):
        first = self.recorded()
        original = mailbox_jobs.write
        raised = False
        def fail_after_queued_write(path, value):
            nonlocal raised
            original(path, value)
            if path.name == "job.json" and value["id"] != first and value["status"] == "queued" and not raised:
                raised = True
                raise OSError("crash after queued metadata")
        with patch("house.mailbox_jobs.write", side_effect=fail_after_queued_write):
            with self.assertRaisesRegex(OSError, "queued metadata"):
                self.ask(request="crash-queued")
        retry = self.ask(request="crash-queued")
        self.assertEqual(self.answer(retry)["existing_job"], first)
        self.assertEqual(self.stored(retry)["status"], "done")

    def test_same_exact_retry_repairs_interruption_after_result_write(self):
        first = self.recorded()
        original = mailbox_jobs.write
        raised = False
        def fail_after_result(path, value):
            nonlocal raised
            original(path, value)
            if path.name == "result.json" and not raised:
                raised = True
                raise OSError("crash after result")
        with patch("house.mailbox_jobs.write", side_effect=fail_after_result):
            with self.assertRaisesRegex(OSError, "after result"):
                self.ask(request="crash-result")
        retry = self.ask(request="crash-result")
        self.assertEqual(self.answer(retry)["existing_job"], first)
        self.assertEqual(self.stored(retry)["status"], "done")

    def test_same_exact_retry_replays_after_done_metadata_write(self):
        first = self.recorded()
        original = mailbox_jobs.write
        raised = False
        def fail_after_done(path, value):
            nonlocal raised
            original(path, value)
            if path.name == "job.json" and value.get("duplicate_of") == first and not raised:
                raised = True
                raise OSError("crash after done metadata")
        with patch("house.mailbox_jobs.write", side_effect=fail_after_done):
            with self.assertRaisesRegex(OSError, "done metadata"):
                self.ask(request="crash-done")
        retry = self.ask(request="crash-done")
        self.assertEqual(self.answer(retry)["existing_job"], first)
        self.assertEqual(self.stored(retry)["status"], "done")

    def test_running_original_retry_never_becomes_a_duplicate_of_newer_queued_work(self):
        first = self.ask(request="original-running")
        running = self.stored(first)
        running.update(status="running", pgid=12345, started_at=time.time())
        mailbox_jobs.write(self.private / "jobs" / first / "job.json", running)
        later = self.recorded(resident=self.resident, run=self.run)
        queued = self.stored(later)
        queued["created_at"] = running["created_at"] + 1
        mailbox_jobs.write(self.private / "jobs" / later / "job.json", queued)
        self.assertEqual(self.ask(request="original-running"), first)
        self.assertEqual(self.stored(first), running)
        self.assertIsNone(mailbox_jobs.result(self.record, first))
        self.assertEqual(self.stored(later)["status"], "queued")

    def test_queued_crash_retries_keep_older_owner_including_equal_timestamps(self):
        for tied in (False, True):
            with self.subTest(tied=tied):
                # Equal clocks use the same (created_at, id) order on both retries.
                requests = sorted(("older-" + str(tied), "later-" + str(tied)),
                                  key=lambda value: hashlib.sha256(value.encode()).hexdigest())
                target = "queued-target-" + str(tied)
                with patch("house.mailbox_jobs.time.time", return_value=100.0):
                    first = self.ask(target, request=requests[0])
                original = mailbox_jobs.write
                def fail_after_queued(path, value):
                    original(path, value)
                    if path.name == "job.json" and value["id"] != first and value["status"] == "queued":
                        raise OSError("queued admission interrupted")
                with patch("house.mailbox_jobs.time.time", return_value=100.0 if tied else 101.0), \
                     patch("house.mailbox_jobs.write", side_effect=fail_after_queued):
                    with self.assertRaisesRegex(OSError, "admission interrupted"):
                        self.ask(target, request=requests[1])
                self.ask(target, request=requests[0])
                self.assertEqual(self.stored(first)["status"], "queued")
                self.assertIsNone(mailbox_jobs.result(self.record, first))
                second = self.ask(target, request=requests[1])
                self.assertEqual(self.answer(second)["existing_job"], first)
                self.assertNotIn("duplicate_of", self.stored(first))

    def test_real_worker_retry_keeps_process_owned_through_tick_and_requester_exit(self):
        from tests.test_readonly_inspection_jobs import InspectionJobTests
        fixture = InspectionJobTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.paused_runtime(mutation=True)
        argv = ["integrate", fixture.author, "--as", fixture.resident, "--publish"]
        first = mailbox_jobs.enqueue(fixture.record, fixture.run, argv, "live-original")
        mailbox_jobs.tick(fixture.record)
        fixture.wait_entered("mutation-entered")
        child = fixture.record._mailbox_processes[first]
        def reap_worker():
            if child.poll() is None:
                mailbox_jobs.kill_group(child.pid)
            child.wait(timeout=5)
        self.addCleanup(reap_worker)
        running = fixture.metadata(first)
        original = mailbox_jobs.write
        def fail_after_queued(path, value):
            original(path, value)
            if path.name == "job.json" and value["id"] != first and value["status"] == "queued":
                raise OSError("queued admission interrupted")
        with patch("house.mailbox_jobs.write", side_effect=fail_after_queued):
            with self.assertRaisesRegex(OSError, "admission interrupted"):
                mailbox_jobs.enqueue(fixture.record, fixture.run, argv, "live-duplicate")
        mailbox_jobs.enqueue(fixture.record, fixture.run, argv, "live-original")
        self.assertEqual(fixture.metadata(first), running)
        mailbox_jobs.tick(fixture.record)
        self.assertIsNone(child.poll())
        self.assertIs(fixture.record._mailbox_processes[first], child)
        duplicate = mailbox_jobs.enqueue(fixture.record, fixture.run, argv, "live-duplicate")
        self.assertEqual(mailbox_jobs.result(fixture.record, duplicate)["result"]["existing_job"], first)
        fixture.record.append("life", "watch-keeper", {"kind": "run-finish", "run": fixture.run,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        mailbox_jobs.stop(fixture.record, fixture.run, running=False)
        mailbox_jobs.tick(fixture.record)
        self.assertEqual(fixture.metadata(first), running)
        self.assertIsNone(child.poll())
        mailbox_jobs.interrupt(fixture.record, fixture.metadata(first))
        self.assertIsNotNone(child.poll())
        self.assertNotIn(first, fixture.record._mailbox_processes)
        self.assertIn("interrupted", mailbox_jobs.result(fixture.record, first)["error"])

    def test_recovery_discards_a_reversed_queued_duplicate_marker(self):
        first = self.ask(request="older-original")
        second = self.recorded(resident=self.resident, run=self.run)
        later = self.stored(second)
        later["created_at"] = self.stored(first)["created_at"] + 1
        mailbox_jobs.write(self.private / "jobs" / second / "job.json", later)
        # Preserve a response left by the rejected retry-direction implementation.
        mailbox_jobs.duplicate_response(self.record, self.stored(first), later)
        self.ask(request="older-original")
        self.assertEqual(self.stored(first)["status"], "queued")
        self.assertNotIn("duplicate_of", self.stored(first))
        self.assertIsNone(mailbox_jobs.result(self.record, first))
        mailbox_jobs.enqueue(self.record, self.run, later["argv"], later["requestid"])
        self.assertEqual(self.answer(second)["existing_job"], first)

    def test_same_resident_repeat_is_prompt_but_distinct_work_stays_queued(self):
        first = self.ask(request="owner-first")
        second = self.ask(request="owner-second")
        self.assertNotEqual(first, second)
        self.assertEqual(self.answer(second)["existing_job"], first)
        self.assertEqual(self.stored(second)["status"], "done")
        different = self.ask(target="contribution-two", request="owner-distinct-work")
        self.assertIsNone(mailbox_jobs.result(self.record, different))
        self.assertEqual(self.stored(different)["status"], "queued")

    def test_retry_reopens_duplicate_if_original_becomes_terminal(self):
        first = self.recorded()
        duplicate = self.ask(request="duplicate-then-finish")
        self.assertEqual(self.answer(duplicate)["existing_job"], first)
        mailbox_jobs.complete(self.record, self.stored(first),
                              {"ok": True, "result": {"status": "accepted"}})
        self.assertEqual(self.ask(request="duplicate-then-finish"), duplicate)
        self.assertIsNone(mailbox_jobs.result(self.record, duplicate))
        self.assertEqual(self.stored(duplicate)["status"], "queued")
        self.assertNotIn("duplicate_of", self.stored(duplicate))

    def test_terminal_action_result_precedes_done_metadata(self):
        first = self.recorded(status="running")
        request = "terminal-result-before-job-done"
        duplicate = self.ask(request=request)
        self.assertEqual(self.answer(duplicate)["existing_job"], first)
        mailbox_jobs.write(self.private / "jobs" / first / "result.json",
                           {"ok": True, "result": {"status": "accepted"}})
        self.ask(request=request)
        self.assertIsNone(mailbox_jobs.result(self.record, duplicate))
        self.assertEqual(self.stored(duplicate)["status"], "queued")

    def test_rejections_keep_original_queue_semantics_and_reasons(self):
        self.recorded(mode="--reject", reason="First reason")
        one = self.ask(mode="--reject", reason="Different reason", request="reject-one")
        two = self.ask(mode="--reject", reason="Another reason", request="reject-two")
        self.assertIsNone(mailbox_jobs.result(self.record, one))
        self.assertIsNone(mailbox_jobs.result(self.record, two))
        self.assertEqual(self.stored(one)["status"], "queued")
        self.assertEqual(self.stored(two)["status"], "queued")

    def test_distinct_targets_inspections_and_request_collisions_are_preserved(self):
        self.recorded()
        other = self.ask(target="contribution-two", request="other-target")
        inspect = self.ask(request="inspect", mode="--inspect")
        self.assertIsNone(mailbox_jobs.result(self.record, other))
        self.assertIsNone(mailbox_jobs.result(self.record, inspect))
        self.assertEqual(mailbox_jobs.lane(self.record, self.stored(inspect)), "inspection")
        same = self.ask(request="bound-request")
        self.assertEqual(self.ask(request="bound-request"), same)
        with self.assertRaisesRegex(ValueError, "different content"):
            self.ask(target="contribution-two", request="bound-request")

    def test_completed_or_interrupted_owner_does_not_leave_stale_duplicate(self):
        first = self.recorded(status="running")
        request = "owner-interrupts"
        duplicate = self.ask(request=request)
        mailbox_jobs.interrupt(self.record, self.stored(first))
        self.assertIn("interrupted", mailbox_jobs.result(self.record, first)["error"])
        self.ask(request=request)
        self.assertIsNone(mailbox_jobs.result(self.record, duplicate))
        self.assertEqual(self.stored(duplicate)["status"], "queued")

    def test_duplicate_result_survives_fresh_coordinator_record(self):
        first = self.recorded()
        duplicate = self.ask(request="persisted-answer")
        response = mailbox_jobs.result(self.record, duplicate)
        fresh = Record(self.repo)
        self.assertEqual(mailbox_jobs.enqueue(fresh, self.run,
            self.argv(resident=self.resident), "persisted-answer"), duplicate)
        self.assertEqual(mailbox_jobs.result(fresh, duplicate), response)
        self.assertIsNone(mailbox_jobs.result(fresh, first))


class MigratedMailboxAdmissionTests(unittest.TestCase):
    """Exercise both real run bindings through the coordinator mailbox service."""
    def setUp(self):
        fixture = test_runtime.RuntimeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.record, self.repo, self.root = fixture.record, fixture.repo, fixture.root
        self.base = git(self.repo, "rev-parse", "HEAD")
        (self.repo / ".gitignore").write_text(".house-residents/\n")
        git(self.repo, "add", ".gitignore")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c",
            "user.email=test@local", "commit", "-m", "Ignore private rooms")
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.private = self.record.common / "house-home"
        self.private.mkdir()
        self.runtime = self.private / "mailbox-runtime.pyz"
        with zipfile.ZipFile(self.runtime, "w") as archive:
            for path in (SOURCE / "house").glob("*.py"):
                archive.write(path, "house/" + path.name)
        self.record._mailbox_runtime = self.runtime
        self.record.append("arrive", "watch-keeper", {"name": "Mailbox keeper"})
        self.runs = []
        self.migrate(maintenance.RETRY_SCOPE)
        self.migrate()
        self.start_run("reviewer-one")
        self.start_run("reviewer-two")

    def migrate(self, scope=maintenance.WORKSPACE_SCOPE):
        state = self.record.read()[0]
        old = maintenance.protected_manifest(state)
        from house.wake_policy import source_snapshot
        files = source_snapshot(self.repo)["files"]
        names = set(old) | maintenance.OWNER_MODULES
        self.record.append("owner-migrate", "alice", {
            "scope": scope,
            "approval_sha256": maintenance.SOURCES[scope],
            "house": state["house_id"], "owner_id": maintenance.council.OWNER_ID,
            "source_head": self.base, "source_sha256": "a" * 64,
            "protected_files": {name: files[name] for name in names},
            "previous_manifest_sha256": maintenance.fingerprint(old),
            "previous_runtime_sha256": "b" * 64, "runtime_sha256": "c" * 64,
            "test_output_sha256": "d" * 64, "test_count": 1})

    def start_run(self, resident):
        run = uuid.uuid4().hex
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": run,
            "resident": resident, "agent": "codex", "model": "gpt-6.1-sol",
            "source_head": self.base, "workspace": "residents/" + run,
            "policy_revision": "fixture", "mode": "work"})
        workspace = room(self.record, self.private, run, self.base)
        self.record.append("life", "watch-keeper", {"kind": "run-launched", "run": run,
            "pgid": os.getpid()})
        endpoint = client(self.record, workspace, resident, self.runtime)
        self.pump(run, endpoint, workspace, resident, "arrive", "--as", resident,
                  "--name", resident, "--request", "arrival-" + run)
        self.runs.append((run, resident, workspace, endpoint))

    def pump(self, run, endpoint, workspace, resident, *argv):
        process = subprocess.Popen([str(endpoint), *argv], cwd=workspace,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 12
        while process.poll() is None and time.monotonic() < deadline:
            mailbox.service(self.record, self.private, run)
            time.sleep(0.02)
        output, errors = process.communicate(timeout=2)
        self.assertEqual(process.returncode, 0, (output, errors))
        return json.loads(output)

    def stop(self, process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=2)

    def test_same_run_queued_response_discloses_exit_cancellation(self):
        run, resident, workspace, endpoint = self.runs[0]
        argv = ["integrate", "queued-contribution", "--as", resident, "--publish"]
        first = mailbox_jobs.enqueue(self.record, run, argv, "same-run-original")
        answer = self.pump(run, endpoint, workspace, resident, *argv)
        self.assertEqual(answer["status"], "in-progress")
        self.assertEqual(answer["existing_job"], first)
        self.assertEqual(answer["existing_status"], "queued")
        self.assertIn("cancelled if its requesting run exits", answer["note"])
        self.assertIn("not a terminal outcome", answer["note"])
        responses = list((workspace / ".house-mailbox" / "responses").glob("*.json"))
        cached = [json.loads(path.read_text()) for path in responses]
        saved = next(value for value in cached if value.get("result") == answer)
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": run,
            "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        mailbox_jobs.stop(self.record, run, running=False)
        self.assertFalse(mailbox_jobs.result(self.record, first)["ok"])
        # Mailbox answers are immutable snapshots; only a new request can observe
        # a later owner outcome. The prompt answer must disclose this at issuance.
        stored = json.loads((self.private / run / "mailbox" / (saved["id"] + ".json")).read_text())
        self.assertEqual(stored["response"]["result"], answer)
        self.assertFalse(any(event["op"] == "say" and
            event["data"].get("text", "").startswith("house-integration-v1")
            for event in self.record.read()[1]))

    def test_two_migrated_runs_receive_real_prompt_mailbox_response(self):
        (first_run, first_resident, first_room, first_client), \
            (second_run, second_resident, second_room, second_client) = self.runs
        self.assertEqual(first_room.resolve(), self.repo.resolve() / ".house-residents" / first_run)
        self.assertEqual(workspace_path(self.record, first_run), first_room)
        self.assertEqual(second_room.resolve(), self.repo.resolve() / ".house-residents" / second_run)
        self.assertEqual(workspace_path(self.record, second_run), second_room)

        first = subprocess.Popen([str(first_client), "integrate", "contribution-x", "--as",
            first_resident, "--publish"], cwd=first_room, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 12
        while not mailbox_jobs.jobs(self.record) and time.monotonic() < deadline:
            mailbox.service(self.record, self.private, first_run)
            time.sleep(0.02)
        self.assertEqual(len(mailbox_jobs.jobs(self.record)), 1, "first request was not admitted")
        self.assertIsNone(first.poll(), "first request should remain on the single worker lane")
        self.addCleanup(self.stop, first)

        response = self.pump(second_run, second_client, second_room, second_resident,
            "integrate", "contribution-x", "--as", second_resident, "--publish")
        self.assertEqual(response["status"], "in-progress")
        self.assertIn("terminal receipt", response["note"])
        self.assertEqual(len(mailbox_jobs.jobs(self.record)), 2)
        self.assertEqual(sum(item["status"] == "queued" for item in mailbox_jobs.jobs(self.record)), 1)


if __name__ == "__main__":
    unittest.main()
