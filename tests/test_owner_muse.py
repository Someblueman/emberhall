"""Per-run workspace trust has no authority over quotas or council rules."""
import copy
import unittest

from house import maintenance as owner
from tests import test_owner_search


class OwnerMuseTests(unittest.TestCase):
    def setUp(self):
        prior = test_owner_search.OwnerSearchTests(); prior.setUp()
        self.h = prior.h
        self.h.event('owner-migrate', prior.migration())

    def migration(self):
        old = owner.protected_manifest(self.h.state)
        return {'scope': owner.MUSE_TRUST_SCOPE, 'approval_sha256': owner.KEEP_MOVING_SHA256,
                'house': self.h.state['house_id'], 'owner_id': owner.council.OWNER_ID,
                'source_head': 'a' * 40, 'source_sha256': 'a' * 64,
                'protected_files': old | {name: '8' * 64 for name in owner.ALLOWED_CHANGES[owner.MUSE_TRUST_SCOPE]},
                'previous_manifest_sha256': owner.fingerprint(old),
                'previous_runtime_sha256': 'b' * 64, 'runtime_sha256': 'c' * 64,
                'test_output_sha256': 'd' * 64, 'test_count': 1}

    def test_scope_preserves_house_state_and_cannot_repeat(self):
        before = copy.deepcopy(self.h.state)
        self.h.event('owner-migrate', self.migration())
        for key, value in before.items():
            if key not in {'maintenance', 'sequence', 'at', 'receipts'}:
                self.assertEqual(self.h.state[key], value, key)
        self.h.reject('owner-migrate', self.migration(), 'already used')

    def test_no_council_mailbox_or_provider_release_power(self):
        for path in ('house/council.py', 'house/mailbox.py', 'house/home.py',
                     'house/owner_upgrade.py', 'house/windows.py'):
            bad = self.migration(); bad['protected_files'][path] = '0' * 64
            self.h.reject('owner-migrate', bad, 'outside.*scope')
        self.h.event('owner-migrate', self.migration())
        self.h.reject('owner-provider-release', {
            'scope': owner.MUSE_TRUST_SCOPE, 'approval_sha256': owner.KEEP_MOVING_SHA256,
            'house': self.h.state['house_id'], 'owner_id': owner.council.OWNER_ID,
            'agent': 'opencode', 'expected_sequence': 594, 'expected_until': owner.KEY_BUDGET_UNTIL,
        }, 'only approved OpenCode')
