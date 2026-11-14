"""Real disposable Git records and competing CLIs; never a live council trial."""
import json
import base64
import time
import uuid
from pathlib import Path
from unittest.mock import patch

from house import council, mailbox
from house.governance import digest
from house.record import Record
from tests import test_mailbox
from tests.support import HouseCase
from tests.test_shelf import idea
from tests.test_council import approval


class ShelfRecordTests(HouseCase):
    def setUp(self):
        super().setUp()
        for actor, agent, model in [('alice', 'codex', 'gpt-6.1-sol'), ('bob', 'muse', 'muse-ember-1.0')]:
            self.record.append('life', actor, {'kind': 'identity', 'agent': agent, 'model': model})

    def start_data(self, key, seconds=60, expect=0):
        return {'kind': 'explore-start', 'round': key, 'token': key, 'seconds': seconds, 'expect': expect}

    def test_actual_competing_cli_claims_have_one_winner_and_receipt_replay(self):
        children = [(actor, self.process('shelf', '--as', actor, '--request', actor + '-round',
                     '--data', json.dumps(self.start_data(actor)))) for actor in ('alice', 'bob')]
        outputs = [(actor, child, child.communicate(timeout=20)) for actor, child in children]
        self.assertEqual([0, 2], sorted(child.returncode for _, child, _ in outputs))
        winner = next(actor for actor, child, _ in outputs if child.returncode == 0)
        state, events, head = self.record.read()
        self.assertEqual(1, len(state['shelf']['rounds']))
        replay = self.cli('shelf', '--as', winner, '--request', winner + '-round', '--data', json.dumps(self.start_data(winner)))
        self.assertTrue(replay['replayed']); self.assertEqual(head, self.record.read()[2])
        self.assertEqual(state, Record(self.repo).read()[0])
        status = self.cli('status')['shelf']
        self.assertTrue(status['enabled']); self.assertIsNone(status['policy'])
        self.assertEqual(winner, status['record']['explorer'])

    def test_expired_writer_cannot_publish_after_recovery_and_dead_client_retries_receipt(self):
        self.record.append('shelf', 'alice', self.start_data('old', seconds=1), 'old-claim')
        process = self.script("from house.record import Record\nimport os,sys\nr=Record(sys.argv[1]);r.append('say','alice',{'text':'Before client crash'},'lost-receipt');os._exit(23)")
        process.communicate(timeout=20); self.assertEqual(23, process.returncode)
        self.assertTrue(self.record.append('say', 'alice', {'text': 'Before client crash'}, 'lost-receipt')['replayed'])
        future = self.record.read()[0]['at'] + 2
        with patch('house.record.time.time', return_value=future):
            self.record.append('shelf', 'bob', self.start_data('new', expect=1))
            self.rejected('shelf', 'alice', {'kind': 'explore-publish', 'round': 'old', 'token': 'old',
                                           'ideas': [idea('a'), idea('b')]}, 'no longer active')
        self.assertEqual('expired', self.record.read()[0]['shelf']['rounds']['old']['status'])

    def test_sleep_run_finish_and_bad_batch_preserve_record(self):
        self.record.append('shelf', 'alice', self.start_data('round'))
        self.rejected('shelf', 'alice', {'kind': 'explore-publish', 'round': 'round', 'token': 'round',
                                       'ideas': [idea('same'), idea('same')]}, 'already used')
        self.assertEqual({}, self.record.read()[0]['shelf']['ideas'])
        self.record.append('sleep', 'alice', {'through': self.record.read()[0]['sequence'], 'note': 'Pause'})
        self.assertEqual('slept', self.record.read()[0]['shelf']['rounds']['round']['status'])
        self.record.append('wake', 'alice', {})
        self.rejected('shelf', 'alice', {'kind': 'explore-publish', 'round': 'round', 'token': 'round',
                                       'ideas': [idea('a'), idea('b')]}, 'no longer active')

    def test_real_journal_trial_isolation_enactment_and_competing_final_votes(self):
        self.repo = self.new_repo('approved-fixture'); self.record = Record(self.repo)
        with patch('house.record.uuid.uuid4', side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
            self.record.found('Isolated fixture', 'Original charter')
        for actor in ('alice', 'bob', 'carol', 'dana', 'erin'):
            self.record.append('arrive', actor, {'name': actor})
        def write(op, data, actor='alice'):
            return self.record.append(op, actor, data)
        write('life', {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6.1-sol'})
        write('council-authorize', approval())
        policy_text = (Path(__file__).parents[1] / 'docs/WORK_SELECTION_PROPOSAL.md').read_text()
        write('council-propose', {'proposal': 'selection', 'mode': 'rule', 'title': 'Selection',
            'text': policy_text, 'reason': 'Synthetic protocol test', 'base': self.record.read()[0]['rule_revision']})
        write('shelf', self.start_data('trial') | {'trial': 'selection'})
        write('shelf', {'kind': 'explore-publish', 'round': 'trial', 'token': 'trial', 'trial': 'selection', 'ideas': [idea('a'), idea('b')]})
        self.assertNotIn('shelf', self.record.read()[0])
        write('shelf', self.start_data('real'))
        write('shelf', {'kind': 'explore-publish', 'round': 'real', 'token': 'real', 'ideas': [idea('a'), idea('b')]})
        choice = {'kind': 'choice-open', 'choice': 'c', 'milestones': {k: {'milestone': 'Demo'} for k in ('a', 'b')}}
        self.rejected('shelf', 'alice', choice, 'require the enacted')
        write('task', {'task': 'fixture-trial', 'title': 'Fixture', 'description': 'Not a live trial'})
        write('claim', {'task': 'fixture-trial', 'expect': 0, 'token': 't', 'seconds': 60})
        write('finish', {'task': 'fixture-trial', 'token': 't', 'result': 'Synthetic trial', 'artifacts': {
            'result.txt': {'sha256': digest('fixture'), 'base64': base64.b64encode(b'fixture').decode()}}})
        write('council-trial', {'proposal': 'selection', 'task': 'fixture-trial', 'evidence': 'Synthetic'})
        for actor in ('bob', 'carol'):
            write('council-endorse', {'proposal': 'selection', 'evidence': 'Synthetic'}, actor)
        write('council-notice', {'proposal': 'selection', 'repository': council.REPOSITORY,
            'issue': council.ISSUE, 'comment_id': 123, 'text_sha256': digest(policy_text)})
        future = time.time() + council.WAIT_SECONDS + 1
        with patch('house.record.time.time', return_value=future):
            write('council-sync', {'repository': council.REPOSITORY, 'issue': council.ISSUE,
                'owner_id': council.OWNER_ID, 'checked_at': future, 'comments': []})
            write('council-enact', {'proposal': 'selection'})
        write('shelf', choice)
        vote = {'kind': 'choice-vote', 'choice': 'c', 'idea': 'a', 'reason': 'Fixture vote'}
        for actor in ('bob', 'carol'):
            write('shelf', vote, actor)
        children = [self.process('shelf', '--as', actor, '--data', json.dumps(vote)) for actor in ('dana', 'erin')]
        for child in children:
            child.communicate(timeout=20)
        self.assertEqual([0, 2], sorted(child.returncode for child in children))
        state = self.record.read()[0]
        self.assertEqual(['c'], list(state['shelf']['projects']))
        self.assertEqual(3, len(state['shelf']['choices']['c']['votes']))
        self.assertEqual({}, state['shelf_trials']['selection']['projects'])


class ShelfMailboxTests(test_mailbox.MailboxCase):
    def test_fixed_channel_replay_identity_and_observed_run_finish(self):
        self.arrive()
        self.call('life', '--as', self.resident, '--data', json.dumps({'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6.1-sol'}))
        command = ['shelf', '--as', self.resident, '--request', 'explore', '--data', json.dumps({
            'kind': 'explore-start', 'round': 'round', 'expect': 0, 'token': 'token', 'seconds': 60})]
        first = self.call(*command); second = self.call(*command)
        self.assertEqual(first['sequence'], second['sequence'])
        with self.assertRaisesRegex(ValueError, 'another resident'):
            mailbox.parse(['shelf', '--as', 'alice', '--data', '{}'], self.repo, self.workspace, self.resident)
        with self.assertRaisesRegex(ValueError, 'not a resident shelf'):
            mailbox.parse(['shelf', '--as', self.resident, '--data', '{"kind":"owner-migrate"}'], self.repo, self.workspace, self.resident)
        self.record.append('life', 'watch-keeper', {'kind': 'run-finish', 'run': self.run, 'outcome': 'interrupted',
                           'exit_code': None, 'usage': {}, 'elapsed_seconds': 1})
        self.assertEqual('slept', self.record.read()[0]['shelf']['rounds']['round']['status'])
