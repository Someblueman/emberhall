"""Disposable verified journals: helper authorization, metadata and atomic admissions."""
import copy
import hashlib
import json
import uuid
from pathlib import Path
from unittest.mock import patch

from house import council, home, life, maintenance, staffing, work_metrics
from house.model import apply_event
from house.record import Record
from tests.support import HouseCase
from tests.test_council import approval
from tests.test_wake_policy import approval as wake_approval


def migrate(record, scope):
    state = record.read()[0]
    old = maintenance.protected_manifest(state)
    names = set(old) | maintenance.OWNER_MODULES
    for key, module in ((maintenance.PROJECT_WORK_SCOPE, 'project_work'),
                        (maintenance.DELIVERY_SCOPE, 'source_delivery'),
                        (maintenance.HELPER_SCOPE, 'staffing')):
        if scope == key:
            names.add('house/' + module + '.py')
    data = {'scope': scope, 'approval_sha256': maintenance.SOURCES[scope],
        'house': state['house_id'], 'owner_id': council.OWNER_ID,
        'source_head': 'a' * 40, 'source_sha256': 'b' * 64,
        'protected_files': {n: old.get(n, 'd' * 64) for n in names},
        'previous_manifest_sha256': maintenance.fingerprint(old),
        'previous_runtime_sha256': 'c' * 64, 'runtime_sha256': 'd' * 64,
        'test_output_sha256': 'e' * 64, 'test_count': 1}
    record.append('owner-migrate', 'alice', data)
    return data


def fixture(case, *, activate=True):
    record = Record(case.new_repo('helpers'))
    with patch('house.record.uuid.uuid4', side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
        record.found('Synthetic helper house', 'Fixture charter')
    for name in ('alice', 'bob', life.CONTROLLER):
        record.append('arrive', name, {'name': name})
    record.append('council-authorize', 'alice', approval())
    record.append('council-wake-authorize', 'alice', wake_approval())
    for scope in (maintenance.BACKLOG_SCOPE, maintenance.PROJECT_WORK_SCOPE,
                  maintenance.CONTINUITY_SCOPE, maintenance.DELIVERY_SCOPE, maintenance.TARGETED_WAKE_SCOPE):
        migrate(record, scope)
    if activate:
        migrate(record, maintenance.HELPER_SCOPE)
    return record


def start_data(key, model='gpt-6.1-sol', **extra):
    return {'kind': 'run-start', 'run': key, 'resident': 'resident-' + key,
        'agent': 'codex', 'model': model, 'source_head': 'a' * 40,
        'workspace': 'residents/' + key, 'policy_revision': 'fixture', 'mode': 'work', **extra}


def offer(record, key, **extra):
    record.append('task', 'alice', {'task': key, 'title': key, 'description': 'Bounded fixture',
                                   'ready': True, 'helper': 'build', **extra})


def regulars(record):
    for key in ('primary-one', 'primary-two'):
        record.append('life', 'alice', {'kind': 'help', 'request': key, 'reason': 'Bounded regular fixture'})
        record.append('life', life.CONTROLLER, start_data(key, help_request=key))


class HelperRecordTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record = fixture(self)
        self.repo = self.record.root

    def start(self, key, task='work', model='gpt-6-luna', **extra):
        self.record.append('life', life.CONTROLLER, start_data(key, model,
                           backlog=True, task=task, task_generation=0, **extra))

    def test_activation_is_strict_and_legacy_baseline_remains_one(self):
        state, events, _ = self.record.read()
        legacy = copy.deepcopy(state)
        legacy['tasks']['new'] = {'status': 'open', 'ready': True, 'helper': 'build'}
        del legacy['maintenance']['migrations'][staffing.SCOPE]
        self.assertEqual(staffing.capacity(legacy)['baseline'], 1)
        self.assertEqual(staffing.capacity(legacy)['total_limit'], 3)
        for data, op in (({'task': 'fresh', 'title': 'New', 'description': 'X', 'helper': 'build'}, 'task'),
                         (start_data('helper', 'gpt-6-luna'), 'life'),
                         ({'kind': 'help', 'request': 'h', 'reason': 'X', 'agent': 'codex',
                           'model': 'gpt-6.1-terra', 'task': 'new'}, 'life'),
                         ({'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6-luna'}, 'life')):
            actor = life.CONTROLLER if data.get('kind') == 'run-start' else 'alice'
            with self.assertRaisesRegex(ValueError, 'activation migration'):
                apply_event(legacy, {'id': 'bad', 'op': op, 'actor': actor, 'at': legacy['at'], 'data': data})
        del legacy['wake_policy']
        self.assertFalse(staffing.enabled(legacy))
        replay = None
        for event in events:
            replay = apply_event(replay, event)
        self.assertEqual(state, replay)

    def test_cli_metadata_generations_clear_and_live_claim_boundary(self):
        self.cli('task', 'work', '--as', 'alice', '--title', 'Work', '--description', 'Bounded',
                 '--ready', '--helper', 'build')
        self.cli('ready', 'work', '--as', 'bob', '--expect', '0', '--helper', 'review')
        self.assertEqual(self.record.read()[0]['tasks']['work']['helper'], 'review')
        self.record.append('claim', 'alice', {'task': 'work', 'expect': 1, 'token': 'own', 'seconds': 60})
        self.rejected('ready', 'bob', {'task': 'work', 'expect': 2, 'ready': True, 'helper': 'none'}, 'live lease')
        self.record.append('release', 'alice', {'task': 'work', 'token': 'own', 'note': 'Fixture'})
        self.cli('ready', 'work', '--as', 'bob', '--expect', '2', '--helper', 'none', '--blocked')
        task = self.record.read()[0]['tasks']['work']
        self.assertNotIn('helper', task)
        self.assertEqual(task['generation'], 3)
        self.rejected('ready', 'alice', {'task': 'work', 'expect': 2, 'ready': True, 'helper': 'build'}, 'generation')
        for value in ('research', 'none', None, 1):
            self.rejected('task', 'alice', {'task': 'bad', 'title': 'X', 'description': 'X', 'helper': value}, 'helper role')

    def test_helpers_need_two_regulars_and_cannot_take_general_or_explorer_wakes(self):
        offer(self.record, 'work')
        self.rejected('life', life.CONTROLLER, start_data('early', 'gpt-6-luna',
                      task='work', task_generation=0, backlog=True), 'helper capacity')
        regulars(self.record)
        self.rejected('life', life.CONTROLLER, start_data('idle', 'gpt-6-luna'), 'bounded task')
        self.rejected('life', life.CONTROLLER, start_data('explore', 'gpt-6-luna', explore_generation=0), 'cannot explore')
        self.rejected('life', 'alice', {'kind': 'help', 'request': 'unbound', 'reason': 'X',
                      'agent': 'codex', 'model': 'gpt-6-luna'}, 'eligible task')
        self.start('luna')
        offer(self.record, 'second')
        self.start('terra', task='second', model='gpt-6.1-terra')
        self.assertEqual(staffing.capacity(self.record.read()[0]),
                         {'baseline': 2, 'total_limit': 4, 'regular_limit': 3, 'helper_limit': 2,
                          'regular': 2, 'helpers': 2, 'total': 4})
        self.rejected('life', life.CONTROLLER, start_data('fifth'), 'capacity')

    def test_regular_limit_stays_three_and_helper_limit_stays_two_after_regular_exit(self):
        regulars(self.record)
        self.record.append('life', 'alice', {'kind': 'help', 'request': 'third-work', 'reason': 'Busy regular'})
        self.record.append('life', life.CONTROLLER, start_data('third', help_request='third-work'))
        self.rejected('life', life.CONTROLLER, start_data('fourth'), 'capacity')
        offer(self.record, 'work'); self.start('helper')
        self.assertEqual(staffing.capacity(self.record.read()[0])['total'], 4)
        # A stopped regular frees a total slot, but the two-regular floor still applies.
        for key in ('third', 'primary-two'):
            self.record.append('life', life.CONTROLLER, {'kind': 'run-finish', 'run': key,
                'outcome': 'interrupted', 'exit_code': None, 'usage': {}, 'elapsed_seconds': 1})
        offer(self.record, 'new')
        self.rejected('life', life.CONTROLLER, start_data('too-early', 'gpt-6.1-terra',
                      task='new', task_generation=0, backlog=True), 'helper capacity')

    def test_admission_rechecks_generation_readiness_pause_and_codex_cooldown(self):
        regulars(self.record); offer(self.record, 'work')
        self.cli('ready', 'work', '--as', 'alice', '--expect', '0', '--blocked')
        self.rejected('life', life.CONTROLLER, start_data('stale', 'gpt-6-luna',
                      task='work', task_generation=0, backlog=True), 'generation changed')
        self.rejected('life', life.CONTROLLER, start_data('blocked', 'gpt-6-luna',
                      task='work', task_generation=1, backlog=True), 'demand changed')
        self.cli('ready', 'work', '--as', 'alice', '--expect', '1')
        self.record.append('life', life.CONTROLLER, {'kind': 'budget', 'agent': 'codex',
            'until': self.record.read()[0]['at'] + 600, 'reason': 'Synthetic quota'})
        self.rejected('life', life.CONTROLLER, start_data('cooled', 'gpt-6-luna',
                      task='work', task_generation=2, backlog=True), 'cooling down')
        state = self.record.read()[0]
        state['maintenance']['admissions'] = {'until': state['at'] + 100}
        with self.assertRaisesRegex(ValueError, 'paused admissions'):
            apply_event(state, {'id': 'paused', 'op': 'life', 'actor': life.CONTROLLER, 'at': state['at'],
                               'data': start_data('paused', 'gpt-6-luna')})

    def test_two_processes_reserve_one_task_without_claiming_it(self):
        regulars(self.record); offer(self.record, 'work')
        children = [self.process('life', '--as', life.CONTROLLER, '--data', json.dumps(
            start_data(key, model, backlog=True, task='work', task_generation=0)))
            for key, model in (('one', 'gpt-6-luna'), ('two', 'gpt-6.1-terra'))]
        codes = []
        for child in children:
            child.communicate(timeout=20); codes.append(child.returncode)
        self.assertEqual(sorted(codes), [0, 2])
        task = self.record.read()[0]['tasks']['work']
        self.assertEqual((task['status'], task['generation'], task['owner']), ('open', 0, None))
        self.assertEqual(staffing.capacity(self.record.read()[0])['helpers'], 1)

    def test_source_review_requires_stopped_non_author_and_exact_target_route(self):
        self.record.append('life', life.CONTROLLER, start_data('source'))
        self.record.append('arrive', 'resident-source', {'name': 'Author'})
        self.record.append('life', 'resident-source', {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6.1-sol'})
        self.record.append('sleep', 'resident-source', {'through': 0, 'note': 'Fixture'})
        self.record.append('life', life.CONTROLLER, {'kind': 'run-finish', 'run': 'source',
            'outcome': 'success', 'exit_code': 0, 'usage': {}, 'elapsed_seconds': 1})
        regulars(self.record)
        self.record.append('life', 'alice', {'kind': 'help', 'request': 'review', 'reason': 'Review source',
            'review_run': 'source', 'agent': 'codex', 'model': 'gpt-6-luna'})
        self.rejected('life', life.CONTROLLER, start_data('self', 'gpt-6-luna', resident='resident-source',
                      help_request='review', mode='review'), 'not eligible|independent')
        self.rejected('life', life.CONTROLLER, start_data('wrong-model', 'gpt-6.1-terra',
                      help_request='review', mode='review'), 'requested model')
        self.record.append('life', life.CONTROLLER, start_data('reviewer', 'gpt-6-luna',
                           help_request='review', mode='review'))
        self.assertEqual(self.record.read()[0]['life']['requests']['review']['run'], 'reviewer')

    def test_helper_starts_do_not_change_regular_rotation_window_or_busy_family(self):
        state = self.record.read()[0]
        state.setdefault('life', life.empty())['runs'] = {'old': dict(start_data('old'), status='completed', started_sequence=1)}
        ordinary = home.choose_provider(state, state['at'])
        for i in range(40):
            state['life']['runs'][str(i)] = dict(start_data(str(i), 'gpt-6-luna'),
                                                status='active', started_sequence=i + 2)
        self.assertEqual(work_metrics.counts(state, 'work', home.KINDS)['codex'], 1)
        self.assertEqual(home.choose_provider(state, state['at']), ordinary)

    def test_scope_hash_manifest_and_protected_boundaries(self):
        from tests import test_owner_maintenance
        f = test_owner_maintenance.OwnerMaintenanceTests(); f.setUp()
        h = f.h; old = maintenance.protected_manifest(h.state)
        data = f.migration() | {'scope': staffing.SCOPE, 'approval_sha256': maintenance.SOURCES[staffing.SCOPE],
            'protected_files': old | {p: 'f' * 64 for p in maintenance.OWNER_MODULES | {'house/staffing.py'}}}
        self.assertEqual(hashlib.sha256((Path(__file__).parents[1] / 'evidence/helper-staffing/owner-scope.md').read_bytes()).hexdigest(),
                         data['approval_sha256'])
        missing = copy.deepcopy(data); missing['protected_files'].pop('house/staffing.py')
        h.reject('owner-migrate', missing, 'manifest')
        for name in ('house/council.py', 'house/wake_policy.py', 'house/mailbox.py'):
            bad = copy.deepcopy(data); bad['protected_files'][name] = 'e' * 64
            h.reject('owner-migrate', bad, 'outside.*scope')
        before = copy.deepcopy(h.state)
        h.event('owner-migrate', data)
        for key in ('rules', 'rule_revision', 'wake_policy', 'council', 'life'):
            self.assertEqual(h.state[key], before[key])
