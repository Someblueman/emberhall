"""Kernel contention and review demand at the trusted integration boundary.

The installation failure at original line 56 is consistent with a reproduced
startup/admission race: process lifetime does not establish action admission.
Delaying BOOT by two seconds reproduced a terminal response, not a stuck lock:
``ValueError: action needs its assigned active, awake resident and fixed room``.
The original failed run did not retain its worker response in the test log.
Observe successful source validation before ending the requester, then exercise
the real blocking lock and terminal replay. This is a fixture repair only.
"""
import fcntl
import json
import os
import time
import unittest
from unittest.mock import patch

from house import home, mailbox_jobs, source_delivery
from house.home_work import contribution, room
from tests.test_mailbox import MailboxCase
from house.home import Coordinator


class ContentionTests(MailboxCase):
    def worker_diagnostics(self, job):
        path = self.private / 'jobs' / job
        return {name: (path / name).read_text()[-4000:]
                for name in ('result.json', 'stdout.log', 'stderr.log')
                if (path / name).exists()}

    def setUp(self):
        super().setUp()
        self.arrive()
        self.coordinator = Coordinator(self.record, self.runtime)

    def finish_resident(self):
        self.record.append('sleep', self.resident, {'through': self.record.read()[0]['sequence'], 'note': 'Handoff'})
        self.coordinator.finish(self.run, {'outcome': 'success', 'exit_code': 0,
                                           'usage': {}, 'elapsed_seconds': 1})
    def test_waiting_worker_survives_requester_exit_and_replays(self):
        self.waiting_worker_survives_requester_exit()

    def test_slow_worker_startup_survives_requester_exit_and_replays(self):
        # Startup is deliberately longer than the old one-second guess.
        boot = mailbox_jobs.BOOT.replace('raise SystemExit',
            'import time;time.sleep(2);raise SystemExit')
        with patch.object(mailbox_jobs, 'BOOT', boot):
            self.waiting_worker_survives_requester_exit()

    def waiting_worker_survives_requester_exit(self):
        author = 'contention-author'
        self.record.append('life', 'watch-keeper', {'kind': 'run-start', 'run': author,
            'resident': 'author', 'agent': 'codex', 'model': 'gpt-6.1-sol',
            'source_head': self.base, 'workspace': 'residents/' + author,
            'policy_revision': 'fixture', 'mode': 'work'})
        self.record.append('arrive', 'author', {'name': 'Author'})
        workspace = room(self.record, self.private, author, self.base)
        (workspace / 'note.md').write_text('A contribution.\n')
        (self.private / author).mkdir()
        contribution(workspace, self.base, self.private / author / 'contribution.json', journal_artifacts={})
        self.record.append('life', 'watch-keeper', {'kind': 'run-finish', 'run': author,
            'outcome': 'success', 'exit_code': 0, 'usage': {}, 'elapsed_seconds': 1})
        admitted = self.admission_runtime()
        argv = ['integrate', author, '--as', self.resident, '--reject', 'Retain this rejection.']
        with (self.private / 'integration.lock').open('a+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            job = mailbox_jobs.enqueue(self.record, self.run, argv, 'contention-request')
            mailbox_jobs.tick(self.record)
            child = self.record._mailbox_processes[job]
            self.wait_for_admission(admitted, child, job)
            self.assertTrue(source_delivery.integration_inflight(self.record, self.private))
            self.finish_resident()
            self.assertIsNone(child.poll(), self.worker_diagnostics(job))
        child.wait(timeout=20)
        with patch('house.mailbox_jobs.group_members', return_value=[]), patch('house.mailbox_jobs.group_stopped', return_value=True):
            self.coordinator.reap()
        result = mailbox_jobs.result(self.record, job)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['result']['status'], 'rejected')
        self.assertEqual(mailbox_jobs.enqueue(self.record, self.run, argv, 'contention-request'), job)
        self.assertEqual(mailbox_jobs.result(self.record, job), result)
        self.assertFalse(source_delivery.integration_inflight(self.record, self.private))

    def admission_runtime(self):
        # Observe admission in the real worker before ending its requester.
        # A live process alone does not mean execute/source validation ran.
        # Only add a marker after successful source validation; keep execute,
        # the kernel lock and every integration decision unchanged.
        import zipfile
        from tests.support import SOURCE
        runtime = self.private / 'contention.pyz'
        admitted = self.private / 'contention-admitted'
        with zipfile.ZipFile(runtime, 'w') as archive:
            for file in (SOURCE / 'house').glob('*.py'):
                content = file.read_bytes()
                if file.name == 'integrate.py':
                    content += ("\n_original_source = source\n"
                        "def source(*args, **kwargs):\n"
                        "    value = _original_source(*args, **kwargs)\n"
                        f"    Path({str(admitted)!r}).touch()\n"
                        "    return value\n").encode()
                archive.writestr('house/' + file.name, content)
        self.record._mailbox_runtime = runtime
        return admitted

    def wait_for_admission(self, admitted, child, job):
        self.addCleanup(self.stop_worker, child)
        deadline = time.monotonic() + 20
        while not admitted.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(admitted.exists(), self.worker_diagnostics(job))
        self.assertIsNone(child.poll(), self.worker_diagnostics(job))

    @staticmethod
    def stop_worker(child):
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)

    def test_timeout_waiting_for_lock_and_queued_cancellation(self):
        author = 'timeout-author'
        self.record.append('life', 'watch-keeper', {'kind': 'run-start', 'run': author,
            'resident': 'writer', 'agent': 'codex', 'model': 'gpt-6.1-sol',
            'source_head': self.base, 'workspace': 'residents/' + author,
            'policy_revision': 'fixture', 'mode': 'work'})
        self.record.append('arrive', 'writer', {'name': 'Writer'})
        workspace = room(self.record, self.private, author, self.base)
        (workspace / 'note.md').write_text('A contribution.\n')
        (self.private / author).mkdir()
        contribution(workspace, self.base, self.private / author / 'contribution.json', journal_artifacts={})
        self.record.append('life', 'watch-keeper', {'kind': 'run-finish', 'run': author,
            'outcome': 'success', 'exit_code': 0, 'usage': {}, 'elapsed_seconds': 1})
        admitted = self.admission_runtime()
        argv = ['integrate', author, '--as', self.resident, '--reject', 'A rejection.']
        with (self.private / 'integration.lock').open('a+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            job = mailbox_jobs.enqueue(self.record, self.run, argv, 'timeout-request')
            mailbox_jobs.tick(self.record)
            child = self.record._mailbox_processes[job]
            queued = mailbox_jobs.enqueue(self.record, self.run, argv, 'queued-request')
            self.wait_for_admission(admitted, child, job)
            self.finish_resident()
            self.assertFalse(mailbox_jobs.result(self.record, queued)['ok'])
            path = self.private / 'jobs' / job / 'job.json'
            item = mailbox_jobs.read(path); item['started_at'] = time.time() - 1201
            mailbox_jobs.write(path, item)
            # The real worker is killed; host process enumeration is unavailable here.
            with patch('house.mailbox_jobs.group_members', return_value=[job]), \
                 patch('house.mailbox_jobs.group_stopped', return_value=True):
                self.coordinator.reap()
            self.assertIsNotNone(child.poll())
            self.assertIn('interrupted', mailbox_jobs.result(self.record, job)['error'])
        self.assertFalse(source_delivery.integration_inflight(self.record, self.private))
        self.assertFalse((self.private / author / 'integration.json').exists())

    def test_lock_is_released_on_process_death(self):
        import subprocess, sys
        child = subprocess.Popen([sys.executable, '-c',
            'import fcntl,sys,time; f=open(sys.argv[1],"a+b"); fcntl.flock(f,fcntl.LOCK_EX); print("held",flush=True); time.sleep(30)',
            str(self.private / 'integration.lock')], stdout=subprocess.PIPE, text=True)
        self.addCleanup(lambda: child.poll() is None and child.kill())
        self.assertEqual(child.stdout.readline().strip(), 'held')
        self.assertTrue(source_delivery.integration_busy(self.private))
        child.kill(); child.wait(timeout=5); child.stdout.close()
        self.assertFalse(source_delivery.integration_busy(self.private))


class SchedulingTests(unittest.TestCase):
    def test_reviews_filtered_while_project_and_explorer_remain(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp, patch('house.home.staffing.capacity', return_value={
                'baseline': 1, 'regular': 1}):
            private = Path(tmp)
            state = {'life': {'requests': {'review': {'review_run': 'one'}, 'other': {}}},
                     'tasks': {'review-task': {'review_run': 'one'}, 'build': {'project': 'p'}}}
            demand = {'pending_help': ['review', 'other'], 'ready_tasks': ['review-task', 'build'],
                      'idle_residents': [], 'uncovered_tasks': 2, 'explore_generation': 4, 'wanted_starts': 4}
            result = home.review_demand(state, demand, private, True)
            self.assertEqual(result['pending_help'], ['other'])
            self.assertEqual(result['ready_tasks'], ['build'])
            self.assertEqual(result['explore_generation'], 4)
            (private / 'one').mkdir()
            (private / 'one/contribution.json').write_text(json.dumps({'commit': 'a' * 40}))
            (private / 'one/integration.json').write_text(json.dumps(
                {'run': 'one', 'contribution': 'a' * 40, 'status': 'tests-failed'}))
            demand['pending_help'].append('review'); demand['ready_tasks'].append('review-task')
            result = home.review_demand(state, demand, private, False)
            self.assertEqual(result['pending_help'], ['other'])
            self.assertEqual(result['ready_tasks'], ['build'])


class PreparedActionTests(unittest.TestCase):
    def _prepared(self):
        from types import SimpleNamespace
        from house import integrate
        from house.home_work import git
        from tests import test_integrate
        fixture = test_integrate.IntegrationTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        fixture.candidate('one', 'changed\n')
        with patch.object(integrate.test_sandbox, 'run', return_value=SimpleNamespace(returncode=0)):
            with patch.object(integrate, 'save_result', side_effect=OSError('lost reply')):
                with self.assertRaisesRegex(OSError, 'lost reply'):
                    integrate.integrate(fixture.record, 'one', 'alice', publish=True)
        prepared = json.loads((fixture.private / 'one/integration.json').read_text())
        self.assertEqual(prepared['status'], 'prepared')
        return fixture, prepared

    def test_prepared_review_without_publish_does_not_merge(self):
        from house import integrate
        from house.home_work import git
        fixture, prepared = self._prepared()
        head = git(fixture.repo, 'rev-parse', 'HEAD')
        body = (fixture.repo / 'document.txt').read_text()
        receipt_bytes = (fixture.private / 'one/integration.json').read_bytes()
        with patch.object(integrate.test_sandbox, 'run', side_effect=AssertionError('retested')):
            result = integrate.integrate(fixture.record, 'one', 'bob')
        self.assertEqual(result, prepared)
        self.assertEqual(git(fixture.repo, 'rev-parse', 'HEAD'), head)
        self.assertEqual((fixture.repo / 'document.txt').read_text(), body)
        self.assertEqual((fixture.private / 'one/integration.json').read_bytes(), receipt_bytes)

    def test_prepared_reject_does_not_merge_and_retains_candidate(self):
        from house import integrate
        from house.home_work import git
        fixture, prepared = self._prepared()
        head = git(fixture.repo, 'rev-parse', 'HEAD')
        receipt_bytes = (fixture.private / 'one/integration.json').read_bytes()
        candidate = fixture.private / prepared['candidate']
        self.assertTrue(candidate.is_dir())
        with self.assertRaisesRegex(ValueError, 'does not merge'):
            integrate.integrate(fixture.record, 'one', 'bob', reject='Late rejection.')
        self.assertEqual(git(fixture.repo, 'rev-parse', 'HEAD'), head)
        self.assertEqual((fixture.private / 'one/integration.json').read_bytes(), receipt_bytes)
        self.assertTrue(candidate.is_dir())
        # The retained candidate still publishes on an explicit publish.
        from types import SimpleNamespace
        with patch.object(integrate.test_sandbox, 'run', return_value=SimpleNamespace(returncode=0)):
            result = integrate.integrate(fixture.record, 'one', 'bob', publish=True)
        self.assertEqual(result['status'], 'integrated')

    def test_prepared_explicit_publish_merges_unmerged_candidate(self):
        from types import SimpleNamespace
        from house import integrate
        from house.home_work import git
        fixture, prepared = self._prepared()
        # Undo the already-performed merge to stand in for an interrupted
        # publish that prepared before merging.
        git(fixture.repo, 'reset', '--hard', fixture.base)
        self.assertEqual((fixture.repo / 'document.txt').read_text(), 'base\n')
        with patch.object(integrate.test_sandbox, 'run', return_value=SimpleNamespace(returncode=0)) as tests:
            result = integrate.integrate(fixture.record, 'one', 'bob', publish=True)
        self.assertEqual(result['status'], 'integrated')
        self.assertEqual((fixture.repo / 'document.txt').read_text(), 'changed\n')
        # Publish replays the prepared candidate without rerunning tests.
        self.assertEqual(tests.call_count, 0)

    def test_prepared_publish_refusal_leaves_source_and_candidate(self):
        from types import SimpleNamespace
        from house import integrate
        from house.home_work import git
        fixture, prepared = self._prepared()
        git(fixture.repo, 'reset', '--hard', fixture.base)
        (fixture.repo / 'document.txt').write_text('dirty\n')
        head = git(fixture.repo, 'rev-parse', 'HEAD')
        candidate = fixture.private / prepared['candidate']
        with self.assertRaisesRegex(ValueError, 'shared source changed'):
            integrate.integrate(fixture.record, 'one', 'bob', publish=True)
        self.assertEqual(git(fixture.repo, 'rev-parse', 'HEAD'), head)
        self.assertEqual((fixture.repo / 'document.txt').read_text(), 'dirty\n')
        self.assertTrue(candidate.is_dir())
        self.assertEqual(json.loads((fixture.private / 'one/integration.json').read_text())['status'], 'prepared')
        git(fixture.repo, 'checkout', '--', 'document.txt')
        with patch.object(integrate.test_sandbox, 'run', return_value=SimpleNamespace(returncode=0)):
            result = integrate.integrate(fixture.record, 'one', 'bob', publish=True)
        self.assertEqual(result['status'], 'integrated')
        self.assertEqual((fixture.repo / 'document.txt').read_text(), 'changed\n')


class ReceiptRecoveryTests(unittest.TestCase):
    def test_terminal_failure_receipts_replay_without_tests(self):
        from house import integrate
        from tests import test_integrate
        fixture = test_integrate.IntegrationTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        fixture.candidate('one', 'changed\n')
        report = json.loads((fixture.private / 'one/contribution.json').read_text())
        path = fixture.private / 'one/integration.json'
        for status in ('conflict', 'tests-failed'):
            receipt = {'run': 'one', 'contribution': report['commit'], 'status': status}
            path.write_text(json.dumps(receipt))
            with patch.object(integrate.test_sandbox, 'run', side_effect=AssertionError('retested')):
                self.assertEqual(integrate.integrate(fixture.record, 'one', 'alice', publish=True), receipt)

    def test_merge_before_lost_reply_is_recovered_without_repeating_effects(self):
        from types import SimpleNamespace
        from house import integrate
        from house.home_work import git
        from tests import test_integrate
        fixture = test_integrate.IntegrationTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        fixture.candidate('one', 'changed\n')
        with patch.object(integrate.test_sandbox, 'run', return_value=SimpleNamespace(returncode=0)) as tests:
            with patch.object(integrate, 'save_result', side_effect=OSError('lost reply')):
                with self.assertRaisesRegex(OSError, 'lost reply'):
                    integrate.integrate(fixture.record, 'one', 'alice', publish=True)
            head = git(fixture.repo, 'rev-parse', 'HEAD')
            self.assertEqual(json.loads((fixture.private / 'one/integration.json').read_text())['status'], 'prepared')
            calls = tests.call_count
            with patch.object(integrate, 'git', wraps=integrate.git) as observed:
                result = integrate.integrate(fixture.record, 'one', 'bob', publish=True)
            self.assertEqual(result['status'], 'integrated')
            self.assertEqual(git(fixture.repo, 'rev-parse', 'HEAD'), head)
            self.assertEqual(tests.call_count, calls)
            self.assertFalse(any('merge' in call.args[1:] for call in observed.call_args_list))
