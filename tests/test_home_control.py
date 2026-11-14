"""Simulated owner pauses exercise admission fencing, expiry and authority."""
import copy
import unittest

from house import home_control, life, maintenance
from tests import test_owner_shelf as fixtures


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.OwnerShelfTests(); fixture.setUp()
        self.h = fixture.h
        self.migration = fixture.migration()

    def pause(self, **changes):
        return {'house': self.h.state['house_id'], 'owner_id': maintenance.council.OWNER_ID,
            'scope': maintenance.KEEP_MOVING_SCOPE, 'approval_sha256': maintenance.KEEP_MOVING_SHA256,
            'expect': 0, 'seconds': 60, 'reason': 'Synthetic safe upgrade', **changes}

    def run_data(self):
        return {'kind': 'run-start', 'run': 'fixture-run', 'resident': 'new-resident',
            'agent': 'codex', 'model': 'gpt-6.1-sol', 'source_head': 'a' * 40,
            'workspace': 'residents/fixture-run', 'policy_revision': 'synthetic', 'mode': 'work'}

    def test_pause_fences_run_start_expires_and_preserves_usage(self):
        h = self.h
        h.reject('owner-admissions', self.pause(), 'runtime is not enabled')
        h.event('owner-migrate', self.migration)
        before = copy.deepcopy(h.state['life'])
        h.event('owner-admissions', self.pause())
        self.assertEqual(before, h.state['life'])
        self.assertEqual(0, life.workload(h.state, h.now)['wanted_starts'])
        h.reject('life', self.run_data(), 'owner paused admissions', life.CONTROLLER)
        h.reject('owner-admissions', self.pause(seconds=0), 'generation changed')
        h.now += 61
        self.assertFalse(home_control.paused(h.state, h.now))
        self.assertGreater(life.workload(h.state, h.now)['wanted_starts'], 0)
        h.event('life', self.run_data(), life.CONTROLLER)

    def test_resume_cas_and_owner_boundary(self):
        h = self.h
        h.event('owner-migrate', self.migration)
        for change in ({'seconds': 3601}, {'seconds': -1}, {'seconds': True}, {'reason': ''}):
            h.reject('owner-admissions', self.pause(**change), 'invalid|needs a reason')
        h.reject('owner-admissions', self.pause(), 'owner operator', 'bob')
        h.event('owner-admissions', self.pause())
        h.event('owner-admissions', self.pause(expect=1, seconds=0))
        self.assertFalse(home_control.paused(h.state, h.now))
        self.assertEqual(2, h.state['maintenance']['admissions']['generation'])

    def test_already_admitted_run_is_not_rewritten_or_killed(self):
        h = self.h
        h.event('owner-migrate', self.migration)
        h.event('life', self.run_data(), life.CONTROLLER)
        before = copy.deepcopy(h.state['life'])
        h.event('owner-admissions', self.pause())
        self.assertEqual(before, h.state['life'])
        h.event('life', {'kind': 'run-launched', 'run': 'fixture-run', 'pgid': 12345}, life.CONTROLLER)
        self.assertEqual(0, life.workload(h.state, h.now)['wanted_starts'])
