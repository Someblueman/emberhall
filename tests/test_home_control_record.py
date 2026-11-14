"""Real competing Git writers; all owner receipts here are synthetic fixtures."""
import json
import uuid
from unittest.mock import patch

from house import council, maintenance, mailbox, wake_policy
from house.record import Record
from tests.support import HouseCase
from tests.test_council import approval
from tests.test_wake_policy import approval as wake_approval


class AdmissionRecordTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.repo = self.new_repo('approved-fixture'); self.record = Record(self.repo)
        with patch('house.record.uuid.uuid4', side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
            self.record.found('Isolated fixture', 'Original charter')
        for actor in ('alice', 'watch-keeper'):
            self.record.append('arrive', actor, {'name': actor})
        self.record.append('council-authorize', 'alice', approval())
        self.record.append('council-wake-authorize', 'alice', wake_approval())
        old = maintenance.protected_manifest(self.record.read()[0])
        self.record.append('owner-migrate', 'alice', {
            'scope': maintenance.KEEP_MOVING_SCOPE, 'approval_sha256': maintenance.KEEP_MOVING_SHA256,
            'house': council.APPROVED_HOUSE, 'owner_id': council.OWNER_ID,
            'source_head': 'a'*40, 'source_sha256': 'b'*64,
            'protected_files': old | {k: 'c'*64 for k in maintenance.ALLOWED_CHANGES[maintenance.KEEP_MOVING_SCOPE]},
            'previous_manifest_sha256': maintenance.fingerprint(old), 'previous_runtime_sha256': 'd'*64,
            'runtime_sha256': 'e'*64, 'test_output_sha256': 'f'*64, 'test_count': 1})
        self.pause = {'house': council.APPROVED_HOUSE, 'owner_id': council.OWNER_ID,
            'scope': maintenance.KEEP_MOVING_SCOPE, 'approval_sha256': maintenance.KEEP_MOVING_SHA256,
            'expect': 0, 'seconds': 60, 'reason': 'Synthetic finite pause'}

    def writer(self, op, actor, data, request):
        return self.script('from house.record import Record\nimport sys\n'
            f'Record(sys.argv[1]).append({op!r},{actor!r},{data!r},{request!r})')

    def test_competing_pauses_have_one_winner_and_lost_receipt_replays(self):
        writers = [self.writer('owner-admissions', 'alice', self.pause, name) for name in ('one', 'two')]
        for writer in writers:
            writer.communicate(timeout=20)
        self.assertEqual([0, 1], sorted(w.returncode for w in writers))
        winner = 'one' if writers[0].returncode == 0 else 'two'
        state, _, head = self.record.read()
        self.assertEqual(1, state['maintenance']['admissions']['generation'])
        self.assertTrue(self.record.append('owner-admissions', 'alice', self.pause, winner)['replayed'])
        self.assertEqual(head, self.record.read()[2])
        self.assertEqual(state, Record(self.repo).read()[0])

    def test_run_start_and_pause_serialize_without_losing_an_admitted_run(self):
        data = {'kind': 'run-start', 'run': 'one', 'resident': 'new-resident', 'agent': 'codex',
            'model': 'gpt-6.1-sol', 'source_head': 'a'*40, 'workspace': 'residents/one',
            'policy_revision': wake_policy.active_policy(self.record.read()[0])['revision'], 'mode': 'work'}
        writers = [self.writer('owner-admissions', 'alice', self.pause, 'pause'),
                   self.writer('life', 'watch-keeper', data, 'start')]
        for writer in writers:
            writer.communicate(timeout=20)
        self.assertEqual(0, writers[0].returncode)
        state, events, _ = self.record.read()
        if writers[1].returncode == 0:
            self.assertEqual('owner-admissions', events[-1]['op'])
            self.assertEqual('active', state['life']['runs']['one']['status'])
        else:
            self.assertNotIn('one', state.get('life', {}).get('runs', {}))
        self.rejected('life', 'watch-keeper', data, 'owner paused admissions')

    def test_resident_mailbox_cannot_operate_owner_control(self):
        with self.assertRaises(ValueError):
            mailbox.parse(['owner-admissions', '--as', 'alice', '--data', json.dumps(self.pause)],
                          self.repo, self.repo, 'alice')
