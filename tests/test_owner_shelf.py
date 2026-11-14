"""Owner activation adds two source pins, not a council enactment or web access."""
import copy
import unittest

from house import maintenance as owner, shelf_gate
from tests import test_owner_backlog as fixtures


class OwnerShelfTests(unittest.TestCase):
    def setUp(self):
        self.prior = fixtures.OwnerBacklogTests(); self.prior.setUp()
        self.h = self.prior.h
        self.h.event('owner-migrate', self.prior.migration())

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return self.prior.migration() | {'scope': owner.SHELF_SCOPE, 'approval_sha256': owner.SHELF_SHA256,
            'protected_files': old | {name: '6' * 64 for name in owner.ALLOWED_CHANGES[owner.SHELF_SCOPE]},
            'previous_manifest_sha256': owner.fingerprint(old)}

    def test_scope_and_activation_preserve_authority_history_and_budgets(self):
        before = copy.deepcopy(self.h.state)
        self.h.reject('shelf', {'kind': 'explore-release'}, 'runtime is not enabled')
        self.h.event('owner-migrate', self.migration())
        self.assertTrue(shelf_gate.enabled(self.h.state))
        self.assertIsNone(shelf_gate.policy(self.h.state))
        for key in ('residents', 'tasks', 'lessons', 'life', 'rules', 'rule_revision', 'council', 'proposals', 'wake_policy'):
            self.assertEqual(before.get(key), self.h.state.get(key), key)
        for key, value in before['maintenance'].items():
            if key not in {'migrations', 'protected_files', 'at'}:
                self.assertEqual(value, self.h.state['maintenance'][key], key)
        self.assertEqual(set(owner.protected_manifest(self.h.state)) - set(owner.protected_manifest(before)),
                         {'house/shelf.py', 'house/shelf_gate.py'})
        self.assertNotIn('shelf', self.h.state)
        self.h.reject('shelf', {'kind': 'choice-open'}, 'require the enacted')

    def test_other_sources_provider_releases_and_missing_pins_reject(self):
        good = self.migration()
        for path in ('house/council.py', 'house/providers.py', 'house/wake_policy.py', 'house/home.py'):
            bad = copy.deepcopy(good); bad['protected_files'][path] = '0' * 64
            self.h.reject('owner-migrate', bad, 'outside.*scope')
        bad = copy.deepcopy(good); del bad['protected_files']['house/shelf_gate.py']
        self.h.reject('owner-migrate', bad, 'replacement manifest')
        self.h.event('owner-migrate', good)
        self.h.reject('owner-migrate', good, 'already used')
        self.h.reject('owner-provider-release', {'scope': owner.SHELF_SCOPE, 'approval_sha256': owner.SHELF_SHA256,
            'house': self.h.state['house_id'], 'owner_id': owner.council.OWNER_ID, 'agent': 'opencode',
            'expected_sequence': 594, 'expected_until': owner.KEY_BUDGET_UNTIL}, 'only approved OpenCode')
