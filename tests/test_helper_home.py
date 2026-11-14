"""Coordinator admission/assignment checks; no model, network or live activation."""
import json
import os
import sys
import time
import unittest
import zipfile
from unittest.mock import patch

from house import home, life, mailbox, providers, staffing
from house.home_work import git
from tests.support import HouseCase, SOURCE
from tests.test_helper_staffing import fixture, offer, regulars, start_data
from tests.test_mailbox import MailboxCase


class HelperHomeTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = fixture(self)
        self.repo = self.record.root
        (self.repo / 'source.txt').write_text('base')
        git(self.repo, 'add', 'source.txt')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test', '-c',
            'user.email=test@local', 'commit', '-m', 'Fixture')
        self.runtime = self.root / 'inert.pyz'; self.runtime.write_bytes(b'inert')
        self.coordinator = home.Coordinator(self.record, self.runtime)

    def demand(self, state=None):
        state = state or self.record.read()[0]
        return life.workload(state, state['at'])

    def launch_failure(self, **kwargs):
        # The real journal, private clone, prompt, client and assignment run; the
        # native boundary stops before a process can execute.
        with patch('house.home.providers.command', side_effect=ValueError('inert native boundary')):
            return self.coordinator.start('codex', **kwargs)

    def test_two_regular_baseline_without_idle_helper_launch(self):
        self.assertEqual(self.demand()['wanted_starts'], 2)
        self.record.append('life', life.CONTROLLER, start_data('one'))
        self.assertEqual(self.demand()['wanted_starts'], 1)
        self.record.append('life', life.CONTROLLER, start_data('two'))
        self.assertEqual(self.demand()['wanted_starts'], 0)
        self.assertIsNone(staffing.select(self.record.read()[0], time.time(), self.demand()))
        report = home.inspect(self.record)
        self.assertEqual(report['capacity'], 4)
        self.assertEqual(report['staffing']['regular'], 2)
        self.assertFalse(any(r['helper'] for r in report['recorded_active']))

    def test_finite_task_binding_prompt_and_alternating_models(self):
        regulars(self.record); offer(self.record, 'work')
        state = self.record.read()[0]
        plan = staffing.select(state, state['at'], self.demand())
        self.assertEqual(plan, {'task': 'work', 'task_generation': 0, 'helper_model': 'gpt-6-luna'})
        run = self.launch_failure(backlog=True, task_id='work', task_generation=0, helper_model=plan['helper_model'])
        item = self.record.read()[0]['life']['runs'][run]
        self.assertEqual((item['model'], item['task'], item['mode'], item['outcome']),
                         ('gpt-6-luna', 'work', 'work', 'failed'))
        prompt = (self.coordinator.private / run / 'prompt.txt').read_text()
        self.assertIn('Suggested task: work; generation 0', prompt)
        self.assertIn('Bounded helper assignment', prompt)
        self.assertIn('explicitly sleep', prompt)
        # The same Codex cooldown covers both helpers and ordinary Codex.
        state = self.record.read()[0]
        self.assertIsNone(staffing.select(state, state['at'], life.workload(state, state['at'])))
        later = state['life']['budgets']['codex']['until'] + 1
        plan = staffing.select(state, later, life.workload(state, later))
        self.assertEqual(plan['helper_model'], 'gpt-6.1-terra')
        assignments = [e for e in self.record.read()[1] if e['id'] == f'home-{run}-assignment']
        receipt = json.loads(assignments[0]['data']['text'][len(home.work_metrics.ASSIGNMENT_PREFIX):])
        self.assertTrue(receipt['helper'])

    def test_lost_generation_and_capacity_races_leave_no_room_or_process(self):
        regulars(self.record); offer(self.record, 'work')
        old_life = self.coordinator.life
        def race(kind, run, **data):
            self.record.append('claim', 'alice', {'task': 'work', 'expect': 0, 'token': 'won', 'seconds': 60})
            return old_life(kind, run, **data)
        with patch.object(self.coordinator, 'life', side_effect=race):
            self.assertIsNone(self.coordinator.start('codex', backlog=True,
                task_id='work', task_generation=0, helper_model='gpt-6-luna'))
        self.assertEqual(list(self.coordinator.private.iterdir()), [])
        self.assertEqual(self.coordinator.running, {})
        self.assertEqual(len(self.record.read()[0]['life']['runs']), 2)

    def test_tick_uses_helper_only_after_baseline_and_cooldown_falls_back_to_regular(self):
        regulars(self.record); offer(self.record, 'work')
        calls = []
        def capture(kind, help_id=None, **kwargs):
            calls.append((kind, help_id, kwargs)); return None
        with patch.object(self.coordinator, 'start', side_effect=capture):
            self.coordinator.tick(poll=False)
        self.assertEqual(calls[0][0], 'codex')
        self.assertEqual(calls[0][2]['helper_model'], 'gpt-6-luna')
        self.record.append('life', life.CONTROLLER, {'kind': 'budget', 'agent': 'codex',
            'until': time.time() + 900, 'reason': 'Fixture quota'})
        calls.clear()
        with patch.object(self.coordinator, 'start', side_effect=capture):
            self.coordinator.tick(poll=False)
        self.assertNotEqual(calls[0][0], 'codex')
        self.assertNotIn('helper_model', calls[0][2])

    def test_project_priority_does_not_allow_unrelated_helper_to_jump_queue(self):
        regulars(self.record); offer(self.record, 'helper')
        state = self.record.read()[0]
        state['shelf'] = {'projects': {'chosen': {'status': 'active', 'deadline': state['at'] + 600}}}
        state['tasks']['ordinary-project'] = dict(state['tasks']['helper'], project='chosen')
        state['tasks']['ordinary-project'].pop('helper')
        demand = self.demand(state)
        self.assertIsNone(staffing.select(state, state['at'], demand))
        state['tasks']['ordinary-project']['helper'] = 'review'
        plan = staffing.select(state, state['at'], self.demand(state))
        self.assertEqual(plan['task'], 'ordinary-project')

    def test_helper_task_help_rebinds_generation_and_review_mode(self):
        regulars(self.record); offer(self.record, 'work', helper='review')
        self.record.append('life', 'alice', {'kind': 'help', 'request': 'assist', 'task': 'work',
            'reason': 'Bounded review', 'agent': 'codex', 'model': 'gpt-6.1-terra'})
        run = self.launch_failure(help_id='assist')
        item = self.record.read()[0]['life']['runs'][run]
        self.assertEqual((item['task'], item['task_generation'], item['mode']), ('work', 0, 'review'))
        self.assertNotIn('backlog', item)

    def test_returning_helper_keeps_exact_identity_and_model(self):
        regulars(self.record); offer(self.record, 'work')
        self.record.append('life', life.CONTROLLER, start_data('old', 'gpt-6-luna',
            task='work', task_generation=0, backlog=True))
        self.record.append('arrive', 'resident-old', {'name': 'Fixture helper'})
        self.record.append('life', 'resident-old', {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6-luna'})
        self.record.append('sleep', 'resident-old', {'through': 0, 'note': 'Saved helper handoff'})
        self.record.append('life', life.CONTROLLER, {'kind': 'run-finish', 'run': 'old',
            'outcome': 'success', 'exit_code': 0, 'usage': {}, 'elapsed_seconds': 1})
        state = self.record.read()[0]
        self.assertTrue(life.return_eligible(state, 'resident-old', 'codex', 'gpt-6-luna', state['at']))
        self.assertFalse(life.return_eligible(state, 'resident-old', 'codex', 'gpt-6.1-terra', state['at']))
        self.rejected('life', 'alice', {'kind': 'help', 'request': 'unbound-target', 'reason': 'X',
            'target_resident': 'resident-old', 'agent': 'codex', 'model': 'gpt-6-luna'}, 'eligible task')
        self.record.append('life', 'alice', {'kind': 'help', 'request': 'target', 'reason': 'Bounded task',
            'target_resident': 'resident-old', 'agent': 'codex', 'model': 'gpt-6-luna', 'task': 'work'})
        run = self.launch_failure(help_id='target')
        self.assertEqual(self.record.read()[0]['life']['runs'][run]['resident'], 'resident-old')
        self.assertIn('Saved helper handoff', (self.coordinator.private / run / 'prompt.txt').read_text())

    def test_helper_command_preserves_native_auth_search_and_sandbox_arguments(self):
        path = self.root
        for model in staffing.HELPER_MODELS:
            with patch('house.providers.shutil.which', return_value='/fixture/codex'), patch.dict(os.environ,
                      {'OPENAI_API_KEY': 'fake', 'CODEX_API_KEY': 'fake', 'OPENROUTER_API_KEY': 'fake'}):
                argv, env = providers.command('codex', model, path, path, path / 'client', web=True)
            self.assertEqual(argv[argv.index('-m') + 1], model)
            self.assertIn('--search', argv)
            self.assertIn('forced_login_method="chatgpt"', argv)
            self.assertIn('--approve-for-me', argv)
            for key in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENROUTER_API_KEY'):
                self.assertNotIn(key, env)

    @unittest.skipIf(os.environ.get('EMBERHALL_CANDIDATE_SANDBOX') == '1',
                     'host process-recovery fixture requires macOS setuid ps')
    def test_real_inert_helpers_get_two_separate_rooms_and_native_outcomes(self):
        regulars(self.record)
        for key in ('one', 'two', 'three'):
            offer(self.record, key)
        with zipfile.ZipFile(self.runtime, 'w') as archive:
            for file in (SOURCE / 'house').glob('*.py'):
                archive.write(file, 'house/' + file.name)
            archive.writestr('__main__.py', 'import sys\nfrom house.home import main\n'
                              'raise SystemExit(main(sys.argv[2:]))\n')
        native = self.root / 'native.py'
        native.write_text('import json,time\nfrom pathlib import Path\n'
                          'Path("source.txt").write_text("private helper work")\n'
                          'time.sleep(0.1)\nprint(json.dumps({"type":"turn.completed",'
                          '"usage":{"input_tokens":3,"output_tokens":2}}),flush=True)\n')
        def command(kind, model, workspace, private, client, **kwargs):
            return [sys.executable, str(native)], dict(os.environ)
        self.addCleanup(self.coordinator.close)
        with patch('house.home.providers.command', side_effect=command):
            result = self.coordinator.tick(poll=False)
        self.assertEqual(len(result['started']), 2)
        self.assertEqual(home.inspect(self.record)['staffing']['total'], 4)
        self.assertEqual({r['model'] for r in home.inspect(self.record)['recorded_active'] if r['helper']},
                         set(staffing.HELPER_MODELS))
        deadline = time.monotonic() + 15
        while self.coordinator.running and time.monotonic() < deadline:
            self.coordinator.tick(start=False, poll=False)
            time.sleep(0.03)
        self.assertFalse(self.coordinator.running)
        state = self.record.read()[0]
        for run in result['started']:
            item = state['life']['runs'][run]
            self.assertEqual(item['outcome'], 'success')
            self.assertEqual(item['usage'], {'input_tokens': 3, 'output_tokens': 2})
            candidate = json.loads((self.coordinator.private / run / 'contribution.json').read_text())
            self.assertEqual(candidate['paths'], ['source.txt'])
        self.assertEqual((self.repo / 'source.txt').read_text(), 'base')


class HelperMailboxTests(MailboxCase):
    def test_flags_reach_reducer_before_activation_and_actor_cannot_be_changed(self):
        self.arrive()
        error = self.collect(self.start('task', 'work', '--as', self.resident, '--title', 'Work',
                             '--description', 'Bounded', '--ready', '--helper', 'build'), success=False)
        self.assertIn('activation migration', error)
        args = mailbox.parse(['ready', 'work', '--as', self.resident, '--expect', '0', '--helper', 'none'],
                             self.repo, self.workspace, self.resident)
        self.assertEqual(args.helper, 'none')
        with self.assertRaisesRegex(ValueError, 'another resident'):
            mailbox.parse(['ready', 'work', '--as', 'alice', '--expect', '0', '--helper', 'review'],
                          self.repo, self.workspace, self.resident)
