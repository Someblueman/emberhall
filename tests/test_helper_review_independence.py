"""Real-journal task bindings fence source authors before run reservation."""
import hashlib
import json

from house import life
from house.model import apply_event
from tests.support import HouseCase
from tests.test_helper_staffing import fixture, offer, regulars, start_data


class HelperReviewIndependenceTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = fixture(self)
        self.repo = self.record.root

    def source(self, model='gpt-6-luna'):
        if model == 'gpt-6-luna':
            regulars(self.record)
            offer(self.record, 'source-work')
            extra = dict(backlog=True, task='source-work', task_generation=0)
        else:
            extra = {}
        self.record.append('life', life.CONTROLLER, start_data('source', model, **extra))
        self.record.append('arrive', 'resident-source', {'name': 'Author'})
        self.record.append('life', 'resident-source',
                           {'kind': 'identity', 'agent': 'codex', 'model': model})
        self.record.append('sleep', 'resident-source', {'through': 0, 'note': 'Fixture source'})
        self.record.append('life', life.CONTROLLER, {'kind': 'run-finish', 'run': 'source',
            'outcome': 'success', 'exit_code': 0, 'usage': {}, 'elapsed_seconds': 1})

    def review(self):
        offer(self.record, 'review', helper='review', review_run='source')

    def help(self):
        self.record.append('life', 'alice', {'kind': 'help', 'request': 'review-help',
            'reason': 'Review the bound task', 'task': 'review'})

    def test_backlog_rejects_returning_author_before_reserving_and_admits_peer(self):
        self.source()
        self.review()
        self.assertEqual(self.record.read()[0]['tasks']['review']['review_run'], 'source')
        data = start_data('return', 'gpt-6-luna', resident='resident-source', mode='review',
                          backlog=True, task='review', task_generation=0)
        self.rejected('life', life.CONTROLLER, data, 'task reviewer must be independent')
        self.record.append('life', life.CONTROLLER, data | {'resident': 'resident-peer'})
        state = self.record.read()[0]
        self.assertEqual(state['life']['runs']['return']['resident'], 'resident-peer')
        self.assertEqual((state['tasks']['review']['generation'], state['tasks']['review']['owner']), (0, None))

    def test_helper_help_rejects_author_and_admits_peer(self):
        self.source()
        self.review()
        self.help()
        data = start_data('return', 'gpt-6-luna', resident='resident-source', mode='review',
                          help_request='review-help', task='review', task_generation=0)
        self.rejected('life', life.CONTROLLER, data, 'task reviewer must be independent')
        self.assertEqual(self.record.read()[0]['life']['requests']['review-help']['status'], 'pending')
        self.record.append('life', life.CONTROLLER, data | {'resident': 'resident-peer'})
        self.assertEqual(self.record.read()[0]['life']['requests']['review-help']['run'], 'return')

    def test_ordinary_help_cannot_hide_bound_task_by_omitting_admission_task(self):
        self.source('gpt-6.1-sol')
        self.review()
        self.help()
        data = start_data('return', resident='resident-source', help_request='review-help', mode='review')
        self.rejected('life', life.CONTROLLER, data, 'task reviewer must be independent')
        self.record.append('life', life.CONTROLLER, data | {'resident': 'resident-peer'})

    def test_binding_validation_rejects_invalid_or_non_stopped_source_and_wrong_role(self):
        self.record.append('life', life.CONTROLLER, start_data('active'))
        data = {'task': 'review', 'title': 'Review', 'description': 'Bounded', 'helper': 'review'}
        for value in (None, '', 7, 'unknown', 'active'):
            with self.subTest(review_run=value):
                self.rejected('task', 'alice', data | {'review_run': value},
                              'invalid review_run|stopped contribution')
        for role in (None, 'build'):
            with self.subTest(helper=role):
                bad = data | {'review_run': 'active'}
                if role is None:
                    del bad['helper']
                else:
                    bad['helper'] = role
                self.rejected('task', 'alice', bad, 'requires helper review')

    def test_cli_stores_binding_and_old_unbound_events_replay_identically(self):
        # A digest frozen against the pre-fix projection catches added defaults.
        self.record.append('task', 'alice', {'task': 'ordinary', 'title': 'Ordinary',
                                           'description': 'Bounded'})
        offer(self.record, 'unbound', helper='review')
        tasks = self.record.read()[0]['tasks']
        self.assertEqual(hashlib.sha256(json.dumps(tasks, sort_keys=True).encode()).hexdigest(),
                         '39f12f96f50d9bfec4d35f4023d26729825488a4545fc27f016d1dd14a929baa')
        state, events, _ = self.record.read()
        replay = None
        for event in events:
            replay = apply_event(replay, event)
        self.assertEqual(state, replay)
        self.source()
        self.cli('task', 'review', '--as', 'alice', '--title', 'Review', '--description', 'Bounded',
                 '--ready', '--helper', 'review', '--review-run', 'source')
        self.assertEqual(self.record.read()[0]['tasks']['review']['review_run'], 'source')

    def test_unbound_helper_review_and_build_admit_as_before(self):
        regulars(self.record)
        for key, role in (('review', 'review'), ('build', 'build')):
            offer(self.record, key, helper=role)
            self.record.append('life', life.CONTROLLER, start_data(key, 'gpt-6-luna',
                backlog=True, task=key, task_generation=0, mode='review' if role == 'review' else 'work'))
            self.assertNotIn('review_run', self.record.read()[0]['tasks'][key])

    def test_unbound_ordinary_backlog_admits_as_before(self):
        self.record.append('task', 'alice', {'task': 'ordinary', 'title': 'Ordinary',
                                           'description': 'Bounded', 'ready': True})
        self.record.append('life', life.CONTROLLER, start_data('ordinary', backlog=True))
        self.assertNotIn('review_run', self.record.read()[0]['tasks']['ordinary'])

    def test_bound_helper_review_chooser_picks_peer_not_most_idle_author_and_no_peer_is_clean_non_start(self):
        import os
        import sys
        import time
        import unittest
        import zipfile
        from unittest.mock import patch

        from house import home
        from house.home_work import git
        from tests.support import SOURCE

        if os.environ.get('EMBERHALL_CANDIDATE_SANDBOX') == '1':
            self.skipTest('host process fixture requires macOS setuid ps')
        (self.repo / 'source.txt').write_text('base\n')
        git(self.repo, 'add', 'source.txt')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Initial source')
        runtime = self.root / 'runtime.pyz'
        with zipfile.ZipFile(runtime, 'w') as archive:
            for file in (SOURCE / 'house').glob('*.py'):
                if file.name != 'opencode_auth.py':
                    archive.write(file, 'house/' + file.name)
            archive.writestr('house/opencode_auth.py', 'def bootstrap(executable, source, private, env):\n'
                " (private / 'auth-prepared').write_text('synthetic account fixture')\n")
            archive.writestr('__main__.py', 'import sys\nfrom house.home import main\nraise SystemExit(main(sys.argv[2:]))\n')
        native = self.root / 'native.py'
        native.write_text('import json,sys,time\nfrom pathlib import Path\n'
            "Path('source.txt').write_text('resident contribution\\n')\n"
            "Path(sys.argv[1]).write_text('native launched')\n"
            'time.sleep(float(sys.argv[2]))\n'
            "print(json.dumps({'type':'turn.completed','usage':{'input_tokens':3,'output_tokens':2}}),flush=True)\n")
        delay = 0.1

        def command(kind, model, workspace, private, client, **kwargs):
            env = dict(os.environ, EMBERHALL_OPENCODE_SOURCE_DB=str(private / 'synthetic-auth.db'))
            return [sys.executable, str(native), str(private / 'native-started'), str(delay)], env

        for target, value in (('active_policy', lambda _: {'revision': 'synthetic-fixture-policy'}),
                              ('active_prompt', lambda _: 'Inert test fixture; no model call.'),
                              ('group_members', lambda pid: []),
                              ('group_stopped', lambda pid: True),
                              ('providers.command', command)):
            helper = patch('house.home.' + target, value)
            helper.start()
            self.addCleanup(helper.stop)
        coordinator = home.Coordinator(self.record, runtime)
        self.addCleanup(coordinator.close)

        def drain():
            deadline = time.monotonic() + 15
            while coordinator.running and time.monotonic() < deadline:
                coordinator.tick(start=False, poll=False)
                time.sleep(0.03)
            self.assertFalse(coordinator.running, 'fixture process failed to finish')

        self.source()
        offer(self.record, 'peer-work')
        self.record.append('life', life.CONTROLLER, start_data(
            'peer', 'gpt-6-luna', backlog=True, task='peer-work', task_generation=0))
        self.record.append('arrive', 'resident-peer', {'name': 'Peer'})
        self.record.append('life', 'resident-peer',
                           {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6-luna'})
        self.record.append('sleep', 'resident-peer', {'through': 0, 'note': 'Fixture peer'})
        self.record.append('life', life.CONTROLLER, {'kind': 'run-finish', 'run': 'peer',
            'outcome': 'success', 'exit_code': 0, 'usage': {}, 'elapsed_seconds': 1})
        self.review()
        run = coordinator.start('codex', backlog=True, task_id='review',
                                task_generation=0, helper_model='gpt-6-luna')
        self.assertIsNotNone(run)
        state = self.record.read()[0]
        self.assertEqual(state['life']['runs'][run]['resident'], 'resident-peer')
        self.assertEqual(state['life']['runs'][run]['task'], 'review')
        self.assertEqual(state['life']['runs'][run]['mode'], 'review')
        offer(self.record, 'review2', helper='review', review_run='source')
        before_head = self.record.read()[2]
        before_runs = set(self.record.read()[0]['life']['runs'])
        before_private = set(p.name for p in coordinator.private.iterdir())
        self.assertIsNone(coordinator.start('codex', backlog=True, task_id='review2',
                                            task_generation=0, helper_model='gpt-6-luna'))
        self.assertEqual(self.record.read()[2], before_head)
        self.assertEqual(set(self.record.read()[0]['life']['runs']), before_runs)
        self.assertEqual(set(p.name for p in coordinator.private.iterdir()), before_private)
        drain()
