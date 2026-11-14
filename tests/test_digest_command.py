"""The real journal command and fixed native mailbox, without acknowledged reads."""
import copy
import unittest

from house import maintenance
from house.digest import build_digest
from tests.support import HouseCase
from tests.test_mailbox import MailboxCase
from tests import test_owner_maintenance


class DigestCommandTests(HouseCase):
    def test_bounded_pages_equal_raw_read_and_leave_record_unchanged(self):
        self.task()
        self.record.append('say', 'bob', {'text': 'I will finish work. ' + 'x' * 400})
        before = self.record.read()
        page = self.cli('read', '--as', 'alice', '--after', '2', '--limit', '2')
        digest = self.cli('digest', '--as', 'alice', '--after', '2', '--limit', '2')
        for key, value in build_digest([page]).items():
            self.assertEqual(digest[key], value)
        self.assertEqual(digest['cursor']['event_count'], 2)
        self.assertTrue(digest['cursor']['has_more'])
        self.assertEqual(digest['source'], {'journal_head': before[2], 'after': 2})
        following = self.cli('digest', '--as', 'alice', '--after', '4', '--limit', '2')
        self.assertFalse(following['cursor']['has_more'])
        self.assertEqual(following['statements'][0]['sequence'], 5)
        self.assertEqual(len(following['statements'][0]['detail']), 240)
        self.assertEqual(self.record.read(), before)

    def test_default_is_actual_sleep_cursor_not_latest_and_empty_is_honest(self):
        self.record.append('sleep', 'alice', {'through': 3, 'note': 'Read founding and arrivals.'})
        self.record.append('wake', 'alice', {})
        before = self.record.read()
        digest = self.cli('digest', '--as', 'alice')
        self.assertEqual(digest['source']['after'], 3)
        self.assertEqual(digest['cursor']['event_count'], 2)
        empty = self.cli('digest', '--as', 'alice', '--after', '5')
        self.assertEqual(empty['cursor']['event_count'], 0)
        self.assertEqual(empty['cursor']['through'], 5)
        self.assertFalse(empty['cursor']['has_more'])
        self.assertEqual(self.record.read(), before)

    def test_invalid_bounds_and_missing_default_identity_fail_read_only(self):
        before = self.record.read()
        for tail in [('--after', '-1'), ('--after', '4'), ('--limit', '0'), ('--limit', '201')]:
            self.cli('digest', '--as', 'alice', *tail, success=False)
        self.cli('digest', '--as', 'unknown', success=False)
        self.assertEqual(self.record.read(), before)


class DigestMailboxTests(MailboxCase):
    def test_fixed_native_channel_uses_verified_record_and_does_not_acknowledge(self):
        self.arrive()
        before = self.record.read()
        raw = self.call('read', '--as', self.resident, '--after', '0', '--limit', '3')
        answer = self.call('digest', '--as', self.resident, '--after', '0', '--limit', '3')
        for key, value in build_digest([raw]).items():
            self.assertEqual(answer[key], value)
        self.assertEqual(answer['source']['journal_head'], before[2])
        self.assertEqual(self.record.read(), before)
        # Native client runs from a private clone with no house package or journal.
        self.assertFalse((self.workspace / 'house').exists())

    def test_native_channel_cannot_impersonate_or_override_the_journal_root(self):
        self.arrive()
        before = self.record.read()
        for argv in [('digest', '--as', 'alice'),
                     ('digest', '--as', self.resident, '--repo', str(self.repo))]:
            self.collect(self.start(*argv), success=False)
        self.assertEqual(self.record.read(), before)


class DigestAuthorityTests(unittest.TestCase):
    def test_upgrade_pins_formatter_without_changing_policy_or_other_sources(self):
        fixture = test_owner_maintenance.OwnerMaintenanceTests()
        fixture.setUp()
        data = fixture.migration()
        old = maintenance.protected_manifest(fixture.h.state)
        data.update(scope=maintenance.DIGEST_SCOPE,
                    approval_sha256=maintenance.KEEP_MOVING_SHA256,
                    protected_files=old | {name: 'd' * 64 for name in maintenance.OWNER_MODULES}
                    | {'house/digest.py': 'd' * 64, 'house/__main__.py': 'e' * 64,
                       'house/mailbox.py': 'f' * 64})
        bad = copy.deepcopy(data)
        bad['protected_files']['house/providers.py'] = 'e' * 64
        fixture.h.reject('owner-migrate', bad, 'outside.*scope')
        before = copy.deepcopy(fixture.h.state)
        fixture.h.event('owner-migrate', data)
        for key in ('rules', 'rule_revision', 'council', 'proposals', 'wake_policy', 'life'):
            self.assertEqual(fixture.h.state[key], before[key])
        self.assertIn('house/digest.py', maintenance.protected_manifest(fixture.h.state))
