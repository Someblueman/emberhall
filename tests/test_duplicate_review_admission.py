"""A second resident's acceptance answers instead of waiting behind the first.

These are fixture jobs and synthetic residents. They do not perform an actual
integration, and no result here is a terminal acceptance or rejection.
"""
import hashlib
import unittest
import uuid

from house import mailbox_jobs
from house.record import Record
from tests.test_mailbox import MailboxCase


class DuplicateAcceptanceTests(MailboxCase):
    def setUp(self):
        super().setUp()
        self.record._mailbox_runtime = self.runtime
        self.other = "other-reviewer"
        self.other_run = uuid.uuid4().hex

    def argv(self, target, resident, mode, reason="unsuitable for this house"):
        base = ["integrate", target, "--as", resident]
        if mode == "--publish":
            return base + ["--publish"]
        if mode == "--inspect":
            return base + ["--inspect"]
        return base + ["--reject", reason]

    def ask(self, target="contribution-one", *, resident=None, run=None, request=None,
            mode="--publish"):
        resident = self.resident if resident is None else resident
        run = self.run if run is None else run
        return mailbox_jobs.enqueue(self.record, run,
            self.argv(target, resident, mode), request or uuid.uuid4().hex)

    def stored(self, job):
        return mailbox_jobs.read(self.private / "jobs" / job / "job.json")

    def answer(self, job):
        response = mailbox_jobs.result(self.record, job)
        self.assertIsNotNone(response, "expected an immediate durable answer")
        self.assertTrue(response["ok"], response)
        return response["result"]

    def recorded_job(self, *, target="contribution-one", resident=None, run=None,
                     mode="--publish", status="queued", created_at=1.0,
                     result=None, request="fixture-job"):
        """Durably record another resident's job without admitting a live run."""
        resident = self.other if resident is None else resident
        run = self.other_run if run is None else run
        job = hashlib.sha256(repr((resident, run, target, mode, request)).encode()).hexdigest()
        path = self.private / "jobs" / job
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        mailbox_jobs.write(path / "job.json", {
            "id": job, "run": run, "resident": resident,
            "argv": self.argv(target, resident, mode), "requestid": request,
            "runtime": str(self.runtime),
            "runtime_sha256": hashlib.sha256(self.runtime.read_bytes()).hexdigest(),
            "status": status, "created_at": created_at})
        if result is not None:
            mailbox_jobs.write(path / "result.json", result)
        return job

    def test_second_resident_publish_answers_in_progress(self):
        first = self.recorded_job()
        mine = self.ask(request="my-publish")
        answer = self.answer(mine)
        self.assertEqual(answer["status"], "in-progress")
        self.assertEqual(answer["contribution"], "contribution-one")
        self.assertEqual(answer["intent"], "publish")
        self.assertEqual(answer["existing_job"], first)
        self.assertEqual(answer["existing_status"], "queued")
        self.assertEqual(answer["existing_resident"], self.other)
        self.assertIn("terminal receipt", answer["note"])
        self.assertIn("new request id", answer["note"])
        self.assertEqual(self.stored(mine)["status"], "done")
        self.assertEqual(self.stored(mine)["duplicate_of"], first)
        self.assertEqual(self.stored(first)["status"], "queued")
        self.assertIsNone(mailbox_jobs.result(self.record, first),
                          "the first acceptance alone still owns the worker lane")
        self.assertEqual(sum(item["status"] == "queued"
                             for item in mailbox_jobs.jobs(self.record)), 1)

    def test_running_acceptance_is_also_reported_in_progress(self):
        first = self.recorded_job(status="running")
        answer = self.answer(self.ask(request="while-running"))
        self.assertEqual(answer["status"], "in-progress")
        self.assertEqual(answer["existing_job"], first)
        self.assertEqual(answer["existing_status"], "running")

    def test_a_residents_own_second_request_keeps_ordinary_queue_semantics(self):
        first = self.ask(request="own-first")
        second = self.ask(request="own-second")
        self.assertIsNone(mailbox_jobs.result(self.record, second))
        self.assertEqual(self.stored(second)["status"], "queued")
        self.assertNotIn("duplicate_of", self.stored(second))
        self.assertEqual(self.stored(first)["status"], "queued")
        self.assertEqual(sum(item["status"] == "queued"
                             for item in mailbox_jobs.jobs(self.record)), 2)

    def test_distinct_contributions_are_not_suppressed(self):
        self.recorded_job(target="contribution-one")
        other = self.ask(target="contribution-two", request="other-contribution")
        self.assertIsNone(mailbox_jobs.result(self.record, other))
        self.assertEqual(self.stored(other)["status"], "queued")

    def test_publish_and_reject_intents_are_not_merged(self):
        self.recorded_job(mode="--publish")
        rejecting = self.ask(mode="--reject", request="reject-same-contribution")
        self.assertIsNone(mailbox_jobs.result(self.record, rejecting))
        self.assertEqual(self.stored(rejecting)["status"], "queued")

    def test_equivalent_rejection_is_reported_in_progress(self):
        first = self.recorded_job(mode="--reject")
        answer = self.answer(self.ask(mode="--reject", request="reject-second"))
        self.assertEqual(answer["intent"], "reject")
        self.assertEqual(answer["existing_job"], first)

    def test_exact_request_retry_returns_the_same_job_and_collision_is_refused(self):
        first = self.ask(request="same-request")
        self.assertEqual(self.ask(request="same-request"), first)
        self.assertEqual(len(mailbox_jobs.jobs(self.record)), 1)
        self.assertIsNone(mailbox_jobs.result(self.record, first))
        with self.assertRaisesRegex(ValueError, "different content"):
            self.ask(target="contribution-two", request="same-request")

    def test_completed_work_is_not_reported_in_progress(self):
        first = self.recorded_job(status="done", result={
            "ok": True,
            "result": {"status": "accepted", "candidate_head": "a" * 40}})
        following = self.ask(request="after-completion")
        self.assertIsNone(mailbox_jobs.result(self.record, following))
        self.assertEqual(self.stored(following)["status"], "queued")
        self.assertNotIn("duplicate_of", self.stored(following))
        self.assertEqual(self.answer(first)["status"], "accepted")

    def test_interrupted_acceptance_releases_the_next_request(self):
        first = self.recorded_job(status="running")
        item = self.stored(first)
        mailbox_jobs.interrupt(self.record, item)
        self.assertIn("interrupted", mailbox_jobs.result(self.record, first)["error"])
        following = self.ask(request="after-interruption")
        self.assertIsNone(mailbox_jobs.result(self.record, following))
        self.assertEqual(self.stored(following)["status"], "queued")

    def test_inspection_lane_is_neither_blocked_by_nor_blocking_acceptance(self):
        inspection = self.ask(request="inspect-first", mode="--inspect")
        publishing = self.ask(request="publish-after-inspect")
        self.assertIsNone(mailbox_jobs.result(self.record, publishing))
        self.assertEqual(self.stored(publishing)["status"], "queued")
        self.assertEqual(self.stored(inspection)["status"], "queued")
        self.assertEqual(mailbox_jobs.lane(self.record, self.stored(inspection)), "inspection")
        self.assertEqual(mailbox_jobs.lane(self.record, self.stored(publishing)), "worker")
        beside = self.ask(request="inspect-beside", mode="--inspect")
        self.assertIsNone(mailbox_jobs.result(self.record, beside))
        self.assertEqual(self.stored(beside)["status"], "queued")

    def test_in_progress_answer_survives_coordinator_memory_loss(self):
        first = self.recorded_job()
        mine = self.ask(request="my-publish")
        answer = self.answer(mine)
        fresh = Record(self.repo)
        mailbox_jobs.recover(fresh)
        self.assertIsNone(mailbox_jobs.result(fresh, first),
                          "the first acceptance still owns the worker lane")
        self.assertEqual(mailbox_jobs.result(fresh, mine), {"ok": True, "result": answer})
        self.assertEqual(sum(item["status"] == "queued"
                             for item in mailbox_jobs.jobs(fresh)), 1)


if __name__ == "__main__":
    unittest.main()
