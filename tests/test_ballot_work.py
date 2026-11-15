"""Ballot role metadata and eligibility; synthetic journals, no live ballot."""
import copy

from house import ballot_work, life
from house.model import apply_event
from tests.support import HouseCase
from tests.test_project_work import projects, start_data


class BallotWorkTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = projects(self)
        self.repo = self.record.root

    def test_cli_annotation_generation_and_inactive_gate(self):
        self.cli('task', 'legacy', '--as', 'alice', '--title', 'Legacy', '--description', 'Fixture')
        self.cli('ready', 'legacy', '--as', 'bob', '--expect', '0', '--ballot-choice', 'later')
        self.assertEqual('later', self.record.read()[0]['tasks']['legacy']['ballot_choice'])
        self.cli('ready', 'legacy', '--as', 'bob', '--expect', '0', '--clear-ballot-choice', success=False)
        self.cli('ready', 'legacy', '--as', 'bob', '--expect', '1', '--clear-ballot-choice')
        self.cli('task', 'linked', '--as', 'alice', '--title', 'Linked', '--description', 'Fixture',
                 '--ballot-choice', 'later', '--ready')
        state = self.record.read()[0]
        self.assertNotIn('ballot_choice', state['tasks']['legacy'])
        state['wake_policy'] = {'fixture': True}
        from house.maintenance import BACKLOG_SCOPE
        state['maintenance'] = {'migrations': {BACKLOG_SCOPE: {}}}
        event = {'id': 'disabled', 'op': 'ready', 'actor': 'alice', 'at': state['at'],
                 'data': {'task': 'legacy', 'expect': 2, 'ready': True, 'ballot_choice': 'later'}}
        with self.assertRaisesRegex(ValueError, 'ballot work runtime'):
            apply_event(state, event)
        state['maintenance']['migrations'][ballot_work.SCOPE] = {}
        self.assertEqual('later', apply_event(state, event)['tasks']['legacy']['ballot_choice'])

    def test_open_independence_closed_disposition_and_matching(self):
        state = self.record.read()[0]
        choice = state['shelf']['choices']['later']
        choice['status'] = 'open'
        choice['votes'] = {'bob': {'idea': 'a'}}
        task = {'ballot_choice': 'later'}
        self.assertFalse(ballot_work.eligible(state, task, 'alice'))  # candidate author
        self.assertFalse(ballot_work.eligible(state, task, 'bob'))
        self.assertTrue(ballot_work.eligible(state, task, 'carol'))
        self.assertFalse(ballot_work.eligible(state, task, 'new-identity'))
        state['tasks'].update(one=copy.copy(task), two=copy.copy(task), generic={})
        self.assertEqual(2, len(ballot_work.uncovered(state, ['one', 'two', 'generic'], ['bob'])))
        self.assertEqual(1, len(ballot_work.uncovered(state, ['one', 'two', 'generic'], ['bob', 'carol'])))
        choice['status'] = 'selected'
        self.assertTrue(ballot_work.eligible(state, task, 'bob'))
        self.assertEqual([], ballot_work.uncovered(state, ['one', 'generic'], ['bob', 'carol']))

    def test_atomic_admission_rechecks_choice_vote_and_generation(self):
        state = self.record.read()[0]
        state['shelf']['choices']['later']['status'] = 'open'
        state['shelf']['choices']['later']['votes'] = {}
        state['maintenance'] = {'resident_returns': True}
        state['residents']['bob']['awake'] = False
        state['life']['runs']['old'] = {'resident': 'bob', 'status': 'completed',
            'agent': 'codex', 'model': 'gpt-6.1-sol', 'started_sequence': 1, 'ended_sequence': 2}
        task_event = {'id': 'offer', 'op': 'task', 'actor': 'alice', 'at': state['at'],
            'data': {'task': 'ballot', 'title': 'Fixture', 'description': 'Fixture',
                     'ready': True, 'ballot_choice': 'later'}}
        state = apply_event(state, task_event)
        data = start_data('new', backlog=True, task='ballot', task_generation=0, ballot_open=True)
        data['resident'] = 'bob'
        event = {'id': 'start', 'op': 'life', 'actor': life.CONTROLLER, 'at': state['at'], 'data': data}
        accepted = apply_event(copy.deepcopy(state), event)
        self.assertEqual('ballot', accepted['life']['runs']['new']['task'])
        voted = copy.deepcopy(state)
        voted['shelf']['choices']['later']['votes']['bob'] = {'idea': 'a'}
        with self.assertRaisesRegex(ValueError, 'eligibility'):
            apply_event(voted, event)
        closed = copy.deepcopy(state)
        closed['shelf']['choices']['later']['status'] = 'selected'
        with self.assertRaisesRegex(ValueError, 'choice state changed'):
            apply_event(closed, event)
        reclaimed = copy.deepcopy(state)
        reclaimed['tasks']['ballot']['generation'] += 1
        with self.assertRaisesRegex(ValueError, 'generation changed'):
            apply_event(reclaimed, event)
        event['data']['ballot_open'] = False
        self.assertEqual('ballot', apply_event(closed, event)['life']['runs']['new']['task'])

    def test_targeted_admission_and_direct_lawful_vote(self):
        state = self.record.read()[0]
        choice = state['shelf']['choices']['later']
        choice['status'] = 'open'
        choice['votes'] = {}
        state['shelf']['ideas']['b']['author'] = 'carol'
        event = {'id': 'lawful', 'op': 'shelf', 'actor': 'alice', 'at': state['at'],
                 'data': {'kind': 'choice-vote', 'choice': 'later', 'idea': 'b', 'reason': 'Fixture'}}
        voted = apply_event(copy.deepcopy(state), event)
        self.assertTrue(voted['shelf']['choices']['later']['votes']['alice']['counted'])
        state['maintenance'] = {'resident_returns': True}
        state['residents']['bob']['awake'] = False
        state['life']['runs']['old'] = {'resident': 'bob', 'status': 'completed',
            'agent': 'codex', 'model': 'gpt-6.1-sol', 'started_sequence': 1, 'ended_sequence': 2}
        state = apply_event(state, {'id': 'offer', 'op': 'task', 'actor': 'alice', 'at': state['at'],
            'data': {'task': 'ballot', 'title': 'Fixture', 'description': 'Fixture',
                     'ready': True, 'ballot_choice': 'later'}})
        state['life']['requests']['target'] = {'status': 'pending', 'task': 'ballot',
            'agent': 'codex', 'model': 'gpt-6.1-sol', 'target_resident': 'bob'}
        data = start_data('targeted', help_request='target', task='ballot', task_generation=0, ballot_open=True)
        data['resident'] = 'bob'
        event = {'id': 'target-start', 'op': 'life', 'actor': life.CONTROLLER, 'at': state['at'], 'data': data}
        self.assertEqual('assigned', apply_event(copy.deepcopy(state), event)['life']['requests']['target']['status'])
        forged = copy.deepcopy(event)
        forged['data']['task'] = 'trial'
        with self.assertRaisesRegex(ValueError, 'binding changed'):
            apply_event(copy.deepcopy(state), forged)
        state['shelf']['choices']['later']['votes']['bob'] = {'idea': 'a'}
        with self.assertRaisesRegex(ValueError, 'eligibility'):
            apply_event(state, event)

    def test_workload_and_provider_use_actual_eligible_return(self):
        from house import home
        state = self.record.read()[0]
        state['shelf']['choices']['later']['status'] = 'open'
        state['shelf']['choices']['later']['votes'] = {'bob': {'idea': 'a'}}
        state = apply_event(state, {'id': 'offer', 'op': 'task', 'actor': 'alice', 'at': state['at'],
            'data': {'task': 'ballot', 'title': 'Fixture', 'description': 'Fixture',
                     'ready': True, 'ballot_choice': 'later'}})
        state['life']['runs']['idle'] = {'resident': 'bob', 'status': 'active', 'agent': 'codex',
            'model': 'gpt-6.1-sol', 'started_at': state['at'], 'started_sequence': 1}
        demand = life.workload(state, state['at'])
        self.assertEqual(['ballot'], demand['uncovered_task_ids'])
        state['maintenance'] = {'resident_returns': True}
        state['residents']['carol']['awake'] = False
        state['life']['runs']['return'] = {'resident': 'carol', 'status': 'completed',
            'agent': 'agy', 'model': 'gemini-4-argon-medium', 'started_sequence': 2, 'ended_sequence': 3}
        self.assertEqual('agy', home.choose_provider(state, state['at'], ballot_task=state['tasks']['ballot']))
        state['shelf']['choices']['later']['votes']['carol'] = {'idea': 'a'}
        self.assertIsNone(home.choose_provider(state, state['at'], ballot_task=state['tasks']['ballot']))

    def test_dispatch_lost_choice_race_removes_unadmitted_room(self):
        from unittest.mock import patch
        from house import home
        state = self.record.read()[0]
        state['shelf']['choices']['later']['status'] = 'open'
        state['shelf']['choices']['later']['votes'] = {}
        state['maintenance'] = {'resident_returns': True}
        state['residents']['bob']['awake'] = False
        state['life']['runs']['old'] = {'resident': 'bob', 'status': 'completed',
            'agent': 'codex', 'model': 'gpt-6.1-sol', 'started_sequence': 1, 'ended_sequence': 2}
        state = apply_event(state, {'id': 'offer', 'op': 'task', 'actor': 'alice', 'at': state['at'],
            'data': {'task': 'ballot', 'title': 'Fixture', 'description': 'Fixture',
                     'ready': True, 'ballot_choice': 'later'}})
        runtime = self.root / 'inert.pyz'
        runtime.write_bytes(b'inert')
        coordinator = home.Coordinator(self.record, runtime)
        private = coordinator.private
        with patch.object(coordinator, 'refresh_runtime'), patch.object(coordinator, 'resolve_completed_help'), \
             patch.object(coordinator.record, 'read', return_value=(state, [], 'a' * 40)), \
             patch('house.home.active_policy', return_value={'revision': 'fixture'}), \
             patch('house.home.source_head', return_value='a' * 40), \
             patch.object(coordinator, 'life', side_effect=ValueError('ballot choice state changed')):
            self.assertIsNone(coordinator.start('codex', backlog=True, task_id='ballot', task_generation=0))
        self.assertEqual([], list(private.iterdir()))
