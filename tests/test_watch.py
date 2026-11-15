"""Real inert child processes: no model request, credential, or scheduler install."""
from __future__ import annotations

import datetime as dt
import json
import os
import unittest
import signal
import subprocess
import sys
import time

from house.watch import ACTOR, entries, local_day, message, run_watch
from tests.support import HouseCase, SOURCE


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host process-recovery fixture requires macOS setuid ps")
class WatchTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / 'docs').mkdir()
        (self.repo / 'docs/WATCH_PROMPT.md').write_text('An inert test prompt.\n')
        self.record.git('add', 'docs/WATCH_PROMPT.md')
        self.record.git('-c', 'commit.gpgsign=false', 'commit', '-m', 'test prompt')
        self.fixture = self.root / 'codex-inert'
        self.fixture.write_text(f'''#!{sys.executable}
import json, os, pathlib, subprocess, sys, time
args = sys.argv[1:]
assert args[:3] == ['exec', '--approve-for-me', '--json'], args
assert args[-1] == '-'
repo = pathlib.Path(args[args.index('-C') + 1])
final = pathlib.Path(args[args.index('-o') + 1])
prompt = sys.stdin.read()
assert prompt.startswith('RUNNER ASSIGNMENT: your resident ID is watch-'), prompt
if 'RECOVERY ONLY:' not in prompt:
    assert prompt.endswith('An inert test prompt.\\n'), prompt
else:
    assert 'Claim only this bounded repair' in prompt, prompt
(repo / '.git/seen-prompt').write_text(prompt)
print(json.dumps({{'type': 'turn.started', 'secret': 'PRIVATE-FIXTURE'}}), flush=True)
mode = os.environ.get('WATCH_TEST_MODE', 'success')
(repo / '.git/child-pid').write_text(str(os.getpid()))
if mode in ('dirty-fail', 'dirty-timeout'):
    (repo / 'docs/WATCH_PROMPT.md').write_text('partial tracked edit')
    (repo / 'unfinished.txt').write_text('unfinished but valuable bytes')
    if mode == 'dirty-fail':
        sys.exit(7)
    mode = 'sleep'
if mode == 'dirty-staged':
    (repo / 'docs/WATCH_PROMPT.md').write_text('staged partial bytes')
    subprocess.run(['git', '-C', str(repo), 'add', 'docs/WATCH_PROMPT.md'], check=True)
    (repo / 'docs/WATCH_PROMPT.md').write_text('An inert test prompt.\\n')
    sys.exit(7)
if mode == 'break-imports':
    (repo / 'house/watch.py').write_text('invalid syntax !!!')
    (repo / 'house/model.py').write_text('also broken !!!')
    (repo / 'unfinished.txt').write_text('rescue after broken imports')
    sys.exit(7)
if mode == 'sleep':
    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    time.sleep(60)
final.write_text('PRIVATE-FIXTURE final')
sys.exit(7 if mode == 'fail' else 0)
''')
        self.fixture.chmod(0o700)

    def watch_process(self, seconds=5, mode='success'):
        return subprocess.Popen(
            [sys.executable, '-m', 'house.watch', '--repo', str(self.repo), 'run',
             '--codex', str(self.fixture), '--seconds', str(seconds)], cwd=SOURCE,
            env=dict(os.environ, WATCH_TEST_MODE=mode), text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def wait_for_child(self):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if (self.repo / '.git/child-pid').exists():
                return int((self.repo / '.git/child-pid').read_text())
            time.sleep(0.02)
        self.fail('inert child did not start')

    def history(self):
        return entries(self.record.read()[1])

    def collect(self, process):
        out, err = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0, err)
        return json.loads(out)

    def test_success_argv_private_logs_and_read_only_inspection(self):
        result = self.collect(self.watch_process())
        self.assertEqual(result['outcome'], 'success')
        path = self.record.common / 'house-watch' / result['run']
        self.assertEqual(path.stat().st_mode & 0o777, 0o700)
        supervisor_log = path.parent / (result['run'] + '-supervisor.log')
        self.assertEqual(supervisor_log.stat().st_mode & 0o777, 0o600)
        for file in path.iterdir():
            self.assertEqual(file.stat().st_mode & 0o777, 0o600)
        self.assertIn('PRIVATE-FIXTURE', (path / 'events.jsonl').read_text())
        self.assertNotIn('PRIVATE-FIXTURE', json.dumps(self.record.read()[1]))
        self.assertEqual(self.record.git('status', '--porcelain'), b'')
        before = self.record.read()[2]
        result = subprocess.run([sys.executable, '-m', 'house.watch', '--repo', str(self.repo),
                                 'inspect'], cwd=SOURCE, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['starts_today'], 1)
        self.assertEqual(self.record.read()[2], before)

    def test_failures_count_and_thirteenth_start_is_denied(self):
        for _ in range(12):
            result = run_watch(self.record, str(self.root / 'absent'), seconds=2)
            self.assertEqual(result['outcome'], 'child-failed')
        result = run_watch(self.record, str(self.fixture), seconds=2)
        self.assertEqual(result['reason'], 'daily-limit')
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 12)
        self.assertFalse((self.repo / '.git/child-pid').exists())

    def test_dirty_or_claimed_checkout_skips_without_spending_start(self):
        (self.repo / 'someone-elses-work').write_text('preserve me')
        self.assertEqual(run_watch(self.record, str(self.fixture))['reason'], 'dirty-checkout')
        (self.repo / 'someone-elses-work').unlink()
        self.task()
        self.record.append('claim', 'alice', {'task': 'work', 'expect': 0,
                                            'token': 'alice-active', 'seconds': 60})
        self.assertEqual(run_watch(self.record, str(self.fixture))['reason'], 'live-task-claim')
        self.assertFalse(any(x['kind'] == 'start' for x in self.history()))

    def test_concurrent_invocation_skips_and_timeout_kills_entire_group(self):
        first = self.watch_process(seconds=1.2, mode='sleep')
        pid = self.wait_for_child()
        second = self.collect(self.watch_process())
        self.assertEqual(second['reason'], 'active-run')
        result = self.collect(first)
        self.assertEqual(result['outcome'], 'timeout')
        from house.watch import group_members
        self.assertEqual(group_members(pid), [])
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 1)
        self.assertTrue(any(x['kind'] == 'timeout' for x in self.history()))

    def test_launcher_death_does_not_release_supervisor_lock_or_deadline(self):
        launcher = self.watch_process(seconds=1.4, mode='sleep')
        self.wait_for_child()
        launcher.kill()
        launcher.communicate(timeout=5)
        self.assertEqual(self.collect(self.watch_process())['reason'], 'active-run')
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if any(x['kind'] == 'finish' for x in self.history()):
                break
            time.sleep(0.05)
        else:
            self.fail('surviving supervisor did not finish')
        self.assertEqual(self.history()[-1]['outcome'], 'timeout')

    def test_dead_supervisor_recovers_orphan_before_next_start(self):
        launcher = self.watch_process(seconds=20, mode='sleep')
        pid = self.wait_for_child()
        # Parent PID of the inert Codex is the separate deadline supervisor.
        supervisor = int(subprocess.check_output(['ps', '-o', 'ppid=', '-p', str(pid)]))
        os.kill(supervisor, signal.SIGKILL)
        result = self.collect(launcher)
        self.assertEqual(result['kind'], 'recovered-interruption')
        from house.watch import group_members
        self.assertEqual(group_members(pid), [])
        self.assertEqual(self.collect(self.watch_process())['outcome'], 'success')

    def test_unlaunched_interruption_is_recovered_and_nonzero_exit_recorded(self):
        self.record.append('arrive', ACTOR, {'name': 'Watch keeper'}, 'watch-keeper-arrival-v1')
        self.record.append('say', ACTOR, message('start', 'lost-before-spawn', local_day=local_day(time.time())),
                           'watch-lost-before-spawn-start')
        result = self.collect(self.watch_process(mode='fail'))
        self.assertEqual(result['exit_code'], 7)
        self.assertTrue(any(x['kind'] == 'recovered-interruption' and
                            x['run'] == 'lost-before-spawn' for x in self.history()))

    def test_local_civil_day_handles_dst_and_hard_deadline_cannot_expand(self):
        old = os.environ.get('TZ')
        try:
            os.environ['TZ'] = 'Europe/London'
            time.tzset()
            summer = dt.datetime(2026, 7, 1, 23, 30, tzinfo=dt.timezone.utc).timestamp()
            winter = dt.datetime(2026, 11, 1, 23, 30, tzinfo=dt.timezone.utc).timestamp()
            self.assertEqual(local_day(summer), '2026-07-02')
            self.assertEqual(local_day(winter), '2026-11-01')
        finally:
            if old is None:
                os.environ.pop('TZ', None)
            else:
                os.environ['TZ'] = old
            time.tzset()
        for seconds in (0, 1201, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                run_watch(self.record, str(self.fixture), seconds=seconds)

    def test_next_runner_recovers_when_launcher_and_supervisor_both_die(self):
        launcher = self.watch_process(seconds=20, mode='dirty-timeout')
        pid = self.wait_for_child()
        deadline = time.monotonic() + 5
        while not (self.repo / 'unfinished.txt').exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue((self.repo / 'unfinished.txt').exists())
        supervisor = int(subprocess.check_output(['ps', '-o', 'ppid=', '-p', str(pid)]))
        launcher.kill()
        launcher.communicate(timeout=5)
        os.kill(supervisor, signal.SIGKILL)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            result = self.collect(self.watch_process())
            if result.get('reason') != 'active-run':
                break
            time.sleep(0.05)
        self.assertEqual(result['outcome'], 'success')
        self.assertEqual(sum(x['kind'] == 'recovered-interruption' for x in self.history()), 1)
        from house.watch import group_members
        self.assertEqual(group_members(pid), [])

    def test_closed_summary_pipe_does_not_replay_completed_run(self):
        process = self.watch_process()
        process.stdout.close()
        process.wait(timeout=10)
        error = process.stderr.read()
        process.stderr.close()
        self.assertEqual(process.returncode, 2, error)
        self.assertNotIn('Exception ignored', error)
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 1)
        self.assertEqual(sum(x['kind'] == 'finish' for x in self.history()), 1)

    def test_prior_civil_day_does_not_consume_current_day_quota(self):
        self.record.append('arrive', ACTOR, {'name': 'Watch keeper'}, 'watch-keeper-arrival-v1')
        yesterday = (dt.date.fromisoformat(local_day(time.time())) - dt.timedelta(days=1)).isoformat()
        # Synthetic prior-day history; model executions themselves remain inert real processes.
        for index in range(12):
            run = f'previous-day-{index}'
            self.record.append('say', ACTOR, message('start', run, local_day=yesterday))
            self.record.append('say', ACTOR, message('finish', run, outcome='child-failed'))
        result = self.collect(self.watch_process())
        self.assertEqual(result['outcome'], 'success')
        from house.watch import inspect
        self.assertEqual(inspect(self.record)['starts_today'], 1)

    def test_elapsed_wall_deadline_never_releases_model_gate(self):
        import fcntl
        from house.watch import private_root, worker
        self.record.append('arrive', ACTOR, {'name': 'Watch keeper'}, 'watch-keeper-arrival-v1')
        run = 'elapsed-wall-deadline'
        self.record.append('say', ACTOR, message('start', run, seconds=20,
                           local_day=local_day(time.time()), deadline_at=time.time() - 1, resident='watch-expired'))
        with (private_root(self.record) / 'runner.lock').open('a+b') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            result = worker(self.record, run, lock.fileno(), str(self.fixture),
                            self.repo / 'docs/WATCH_PROMPT.md', time.monotonic() + 20)
        self.assertEqual(result, 1)
        self.assertFalse((self.repo / '.git/child-pid').exists())
        self.assertEqual(self.history()[-1]['outcome'], 'timeout')

    def test_delayed_cleanup_preserves_known_child_result_for_recovery(self):
        import fcntl
        from unittest.mock import patch
        from house.watch import admit, private_root, recover, worker
        self.record.append('arrive', ACTOR, {'name': 'Watch keeper'}, 'watch-keeper-arrival-v1')
        run = 'delayed-cleanup'
        prompt = (self.repo / 'docs/WATCH_PROMPT.md').resolve()
        with (private_root(self.record) / 'runner.lock').open('a+b') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            admit(self.record, run, 10, prompt, str(self.fixture))
            # Model the cleanup-deadline branch, not a fabricated model result:
            # the actual inert child must run and return zero first.
            with patch('house.watch.group_stopped', return_value=False):
                code = worker(self.record, run, lock.fileno(), str(self.fixture),
                              prompt, time.monotonic() + 10)
            self.assertEqual(code, 1)
            self.assertFalse(any(x['kind'] == 'finish' for x in self.history()))
            observed = [x for x in self.history() if x['kind'] == 'execution-result']
            self.assertEqual(len(observed), 1, 'known child outcome was discarded')
            self.assertEqual(observed[0]['exit_code'], 0)
            self.assertIsNone(recover(self.record))
        final = self.history()[-1]
        self.assertEqual(final['kind'], 'finish')
        self.assertEqual(final['outcome'], 'success')
        self.assertTrue(final['recovered'])
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 1)

    def test_scheduled_dirty_failure_can_resume_without_reset(self):
        failed = self.collect(self.watch_process(mode='dirty-fail'))
        self.assertEqual(failed['outcome'], 'child-failed')
        resumed = self.collect(self.watch_process())
        self.assertEqual(resumed.get('kind'), 'finish', resumed)
        self.assertEqual((self.repo / 'unfinished.txt').read_text(), 'unfinished but valuable bytes')
        self.assertEqual((self.repo / 'docs/WATCH_PROMPT.md').read_text(), 'partial tracked edit')

    def test_unrelated_edit_after_snapshot_blocks_recovery(self):
        self.collect(self.watch_process(mode='dirty-fail'))
        (self.repo / 'someone-elses-work').write_text('unrelated edit after rescue')
        result = self.collect(self.watch_process())
        self.assertEqual(result['reason'], 'dirty-checkout-changed-after-rescue')
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 1)

    def test_rescue_preserves_index_worktree_and_untracked_outside_public_objects(self):
        import base64
        from house.watch_recovery import rescue_git
        self.collect(self.watch_process(mode='dirty-fail'))
        rescue = next(x for x in self.history() if x['kind'] == 'rescue')
        payload = json.loads(rescue_git(self.record.common / 'house-watch/rescue.git',
                                       'show', rescue['commit'] + ':rescue.json'))
        self.assertEqual(base64.b64decode(payload['files']['unfinished.txt']['base64']),
                         b'unfinished but valuable bytes')
        self.assertEqual(base64.b64decode(payload['files']['docs/WATCH_PROMPT.md']['base64']),
                         b'partial tracked edit')
        self.assertEqual(base64.b64decode(payload['index'][0]['base64']),
                         b'An inert test prompt.\n')
        with self.assertRaises(ValueError):
            self.record.git('cat-file', '-e', rescue['commit'])
        self.assertNotIn('unfinished but valuable bytes', json.dumps(self.record.read()[1]))
        first = next(x for x in self.history() if x['kind'] == 'start')
        self.collect(self.watch_process())
        second = [x for x in self.history() if x['kind'] == 'start'][-1]
        self.assertEqual(second['prior_resident'], first['resident'])
        self.assertNotEqual(second['resident'], first['resident'])
        prompt = (self.repo / '.git/seen-prompt').read_text()
        self.assertIn('RECOVERY ONLY:', prompt)
        self.assertNotIn('An inert test prompt.', prompt)
        self.assertIn(second['resident'], prompt)
        self.assertIn(first['resident'], prompt)

    def test_recovery_waits_for_prior_residents_live_lease(self):
        self.collect(self.watch_process(mode='dirty-fail'))
        old = next(x for x in self.history() if x['kind'] == 'start')['resident']
        self.record.append('arrive', old, {'name': 'Original scheduled resident'})
        self.record.append('task', old, {'task': 'unfinished', 'title': 'Unfinished',
                                       'description': 'Original scheduled ownership'})
        self.record.append('claim', old, {'task': 'unfinished', 'expect': 0,
                                        'token': 'original-token', 'seconds': 1})
        self.assertEqual(self.collect(self.watch_process())['reason'], 'live-task-claim')
        time.sleep(1.1)
        self.assertEqual(self.collect(self.watch_process())['kind'], 'finish')
        task = self.record.read()[0]['tasks']['unfinished']
        self.assertEqual((task['owner'], task['token'], task['generation']),
                         (old, 'original-token', 1))

    def test_special_untracked_files_are_not_followed_or_read(self):
        from house.watch_recovery import capture
        path = self.repo / 'special'
        os.mkfifo(path)
        # Git does not report an untracked FIFO; it remains untouched and unread.
        self.assertIsNone(capture(self.record))
        import stat
        self.assertTrue(stat.S_ISFIFO(path.lstat().st_mode))
        path.unlink()
        path.symlink_to(self.root / 'private-missing-target')
        with self.assertRaises(ValueError):
            capture(self.record)

    def test_pinned_runtime_recovers_even_when_mutable_core_imports_break(self):
        import shutil
        from house.watch import private_root
        from house.watch_recovery import prepare_runtime
        (self.repo / 'house').mkdir()
        for source in (SOURCE / 'house').glob('*.py'):
            shutil.copyfile(source, self.repo / 'house' / source.name)
        self.record.git('add', 'house')
        self.record.git('-c', 'commit.gpgsign=false', 'commit', '-m', 'reviewed runtime fixture')
        runtime = prepare_runtime(self.record, private_root(self.record))
        self.assertEqual(runtime['source_head'], self.record.git('rev-parse', 'HEAD').decode().strip())
        self.assertEqual(prepare_runtime(self.record, private_root(self.record)), runtime)
        def pinned(mode='success'):
            return subprocess.Popen([sys.executable, runtime['entry'], '--repo', str(self.repo),
                                     'run', '--codex', str(self.fixture), '--seconds', '5'],
                                    cwd=self.repo, env=dict(os.environ, WATCH_TEST_MODE=mode),
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(self.collect(pinned('break-imports'))['outcome'], 'child-failed')
        broken = subprocess.run([sys.executable, '-m', 'house.watch', 'inspect'],
                                cwd=self.repo, capture_output=True, text=True)
        self.assertNotEqual(broken.returncode, 0)
        self.assertIn('SyntaxError', broken.stderr)
        verified = subprocess.run([sys.executable, runtime['entry'], 'house', '--repo',
                                   str(self.repo), 'verify'], cwd=self.repo,
                                  capture_output=True, text=True, check=True)
        self.assertTrue(json.loads(verified.stdout)['valid'])
        self.assertEqual(self.collect(pinned())['outcome'], 'success')
        self.assertEqual((self.repo / 'house/watch.py').read_text(), 'invalid syntax !!!')
        self.assertEqual((self.repo / 'unfinished.txt').read_text(), 'rescue after broken imports')
        self.assertIn(runtime['entry'], (self.repo / '.git/seen-prompt').read_text())
        with self.assertRaises(ValueError):
            prepare_runtime(self.record, private_root(self.record))

    def test_staged_bytes_survive_when_worktree_matches_head(self):
        import base64
        from house.watch_recovery import rescue_git
        self.assertEqual(self.collect(self.watch_process(mode='dirty-staged'))['exit_code'], 7)
        rescue = next(x for x in self.history() if x['kind'] == 'rescue')
        payload = json.loads(rescue_git(self.record.common / 'house-watch/rescue.git',
                                       'show', rescue['commit'] + ':rescue.json'))
        self.assertEqual(base64.b64decode(payload['index'][0]['base64']), b'staged partial bytes')
        self.assertEqual(base64.b64decode(payload['files']['docs/WATCH_PROMPT.md']['base64']),
                         b'An inert test prompt.\n')
        self.assertEqual(self.collect(self.watch_process())['outcome'], 'success')
        self.assertEqual(self.record.git('show', ':docs/WATCH_PROMPT.md'), b'staged partial bytes')
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 2)

    def test_timed_out_dirty_resident_is_recoverable_without_human_cleanup(self):
        timed_out = self.collect(self.watch_process(seconds=1.2, mode='dirty-timeout'))
        self.assertEqual(timed_out['outcome'], 'timeout')
        self.assertEqual(self.collect(self.watch_process())['outcome'], 'success')
        self.assertEqual((self.repo / 'unfinished.txt').read_text(), 'unfinished but valuable bytes')
        self.assertEqual((self.repo / 'docs/WATCH_PROMPT.md').read_text(), 'partial tracked edit')
        self.assertEqual(sum(x['kind'] == 'start' for x in self.history()), 2)

    def test_rescue_records_staged_rename_as_deletion_and_new_file(self):
        from house.watch_recovery import capture
        self.record.git('mv', 'docs/WATCH_PROMPT.md', 'docs/renamed.md')
        payload = json.loads(capture(self.record))
        self.assertIsNone(payload['files']['docs/WATCH_PROMPT.md'])
        self.assertIn('docs/renamed.md', payload['files'])


class WatchLaneDeadlineTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / 'docs').mkdir()
        self.prompt = (self.repo / 'docs/WATCH_PROMPT.md').resolve()
        self.prompt.write_text('An inert test prompt.\n')
        self.record.git('add', 'docs/WATCH_PROMPT.md')
        self.record.git('-c', 'commit.gpgsign=false', 'commit', '-m', 'test prompt')
        self.record.append('arrive', ACTOR, {'name': 'Watch keeper'},
                           'watch-keeper-arrival-v1')
        self.fixture = self.root / 'codex-inert'
        self.fixture.write_text(f'''#!{sys.executable}
import pathlib, sys, time
assert sys.argv[1:4] == ['exec', '--approve-for-me', '--json']
assert sys.stdin.read().startswith('RUNNER ASSIGNMENT:')
(pathlib.Path(sys.argv[sys.argv.index('-o') + 1]).parent / 'started').write_text('started')
time.sleep(0)
''')
        self.fixture.chmod(0o700)

    def history(self):
        return entries(self.record.read()[1])

    def execute(self, run, seconds, lane=None, *, remaining=None, cleanup=True):
        import fcntl
        from unittest.mock import patch
        from house.watch import admit, private_root, worker
        admit(self.record, run, seconds, self.prompt, str(self.fixture), lane=lane)
        children = []
        popen = subprocess.Popen

        def launch(*args, **kwargs):
            child = popen(*args, **kwargs)
            if '_exec' in args[0]:
                children.append(child)
            return child

        def stopped(pgid):
            # This inert fixture has no descendants. Observe its actual Popen;
            # host-wide ps/group-recovery coverage stays in WatchTests.
            self.assertEqual([p.pid for p in children], [pgid])
            self.assertIsNotNone(children[0].poll())
            return cleanup

        with (private_root(self.record) / 'runner.lock').open('a+b') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            with patch('house.watch.subprocess.Popen', side_effect=launch), \
                    patch('house.watch.group_stopped', side_effect=stopped):
                result = worker(self.record, run, lock.fileno(), str(self.fixture),
                                self.prompt, time.monotonic() +
                                (seconds if remaining is None else remaining))
        return result, children

    def test_invalid_lane_and_duration_do_not_mutate_admission(self):
        from house.watch import admit
        before = self.record.read()[2]
        for lane, seconds in ((None, 1201), ('build', 3601), ('unknown', 1),
                              ('build', 0), ('build', float('inf')),
                              ('build', float('nan'))):
            with self.subTest(lane=lane, seconds=seconds):
                for call in (lambda: run_watch(self.record, str(self.fixture),
                                               seconds=seconds, lane=lane),
                             lambda: admit(self.record, 'bad', seconds, self.prompt,
                                           str(self.fixture), lane=lane)):
                    with self.assertRaises(ValueError):
                        call()
                self.assertEqual(self.record.read()[2], before)

    def test_build_boundaries_exit_early_without_padding(self):
        began = time.monotonic()
        for seconds in (3599, 3600):
            with self.subTest(seconds=seconds):
                code, children = self.execute('build-' + str(seconds), seconds, 'build')
                self.assertEqual(code, 0)
                self.assertEqual(children[0].returncode, 0)
                self.assertEqual(self.history()[-1]['outcome'], 'success')
        self.assertLess(time.monotonic() - began, 15)
        starts = [x for x in self.history() if x['kind'] == 'start']
        self.assertEqual([(x['seconds'], x['lane']) for x in starts],
                         [(3599, 'build'), (3600, 'build')])
        for start in starts:
            self.assertAlmostEqual(start['deadline_at'] - start['at'], start['seconds'], places=2)

    def test_short_lanes_and_legacy_starts_keep_short_ceiling(self):
        for lane in (None, 'review', 'vote', 'upkeep'):
            with self.subTest(lane=lane):
                with self.assertRaises(ValueError):
                    run_watch(self.record, str(self.fixture), seconds=1201, lane=lane)
                self.assertEqual(self.execute('short-' + str(lane), 1200, lane)[0], 0)
        legacy = next(x for x in self.history() if x['run'] == 'short-None')
        self.assertNotIn('lane', legacy)

    def test_worker_rejects_invalid_recorded_lane_and_duration(self):
        import fcntl
        from house.watch import private_root, worker
        for index, (lane, seconds) in enumerate((('build', 3601), ('review', 1201),
                                                (None, 1201), ('unknown', 1))):
            run = 'invalid-worker-' + str(index)
            fields = {} if lane is None else {'lane': lane}
            self.record.append('say', ACTOR, message('start', run, seconds=seconds, **fields))
            with (private_root(self.record) / 'runner.lock').open('a+b') as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                with self.assertRaises(ValueError):
                    worker(self.record, run, lock.fileno(), str(self.fixture),
                           self.prompt, time.monotonic() + seconds)
            self.assertFalse((private_root(self.record) / run).exists())

    def test_build_timeout_kills_real_child_and_retains_outcome(self):
        self.fixture.write_text(self.fixture.read_text().replace('time.sleep(0)', 'time.sleep(60)'))
        code, children = self.execute('build-timeout', 3600, 'build', remaining=2)
        self.assertEqual(code, 1)
        self.assertTrue((self.record.common / 'house-watch/build-timeout/started').exists())
        self.assertEqual(children[0].returncode, -signal.SIGKILL)
        self.assertEqual(self.history()[-1]['outcome'], 'timeout')
        self.assertEqual(sum(x['kind'] == 'timeout' for x in self.history()), 1)

    def test_build_nonzero_exit_is_not_a_timeout(self):
        self.fixture.write_text(self.fixture.read_text().replace('time.sleep(0)', 'sys.exit(7)'))
        code, children = self.execute('build-failed', 3600, 'build')
        self.assertEqual((code, children[0].returncode), (1, 7))
        self.assertEqual(self.history()[-1]['outcome'], 'child-failed')
        self.assertFalse(any(x['kind'] == 'timeout' for x in self.history()))

    def test_known_early_result_survives_delayed_cleanup_recovery(self):
        from house.watch import recover
        code, children = self.execute('build-recovery', 3600, 'build', cleanup=False)
        self.assertEqual((code, children[0].returncode), (1, 0))
        self.assertFalse(any(x['kind'] == 'finish' for x in self.history()))
        from unittest.mock import patch
        with patch('house.watch.group_members', return_value=[]):
            self.assertIsNone(recover(self.record))
        final = self.history()[-1]
        self.assertEqual((final['kind'], final['outcome'], final['exit_code']),
                         ('finish', 'success', 0))
        self.assertTrue(final['recovered'])

    def test_cli_rejects_overlong_build_before_start(self):
        before = self.record.read()[2]
        result = subprocess.run([sys.executable, '-m', 'house.watch', '--repo', str(self.repo),
                                 'run', '--lane', 'build', '--seconds', '3601'], cwd=SOURCE,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)['error'], 'ValueError')
        self.assertEqual(self.record.read()[2], before)
        # Real CLI accepts both build boundaries and the lane default. A dirty
        # fixture stops at admission, before any supervisor or model can start.
        (self.repo / 'unrelated-work').write_text('preserve')
        for extra in ([], ['--seconds', '3599'], ['--seconds', '3600']):
            accepted = subprocess.run([sys.executable, '-m', 'house.watch', '--repo',
                                       str(self.repo), 'run', '--lane', 'build', *extra],
                                      cwd=SOURCE, capture_output=True, text=True, timeout=10)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(json.loads(accepted.stdout)['reason'], 'dirty-checkout')
        self.assertFalse(any(x['kind'] == 'start' for x in self.history()))

    def test_inspect_exposes_lane_limits_without_mutation(self):
        from house.watch import inspect
        before = self.record.read()[2]
        summary = inspect(self.record)
        self.assertEqual(summary['deadline_seconds'], 1200)
        self.assertEqual(summary['deadline_seconds_by_lane'],
                         {'build': 3600, 'review': 1200, 'vote': 1200, 'upkeep': 1200})
        self.assertEqual(self.record.read()[2], before)
