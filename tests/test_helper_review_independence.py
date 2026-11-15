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
