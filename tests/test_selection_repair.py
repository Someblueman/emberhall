"""Owner-only immediate correction, preserved history, and real selection outcomes."""
import copy
from pathlib import Path
import unittest

from house import maintenance, shelf, shelf_gate
from tests import test_owner_shelf, test_shelf


class SelectionRepairTests(unittest.TestCase):
    def setUp(self):
        self.prior = test_owner_shelf.OwnerShelfTests(); self.prior.setUp()
        self.h = self.prior.h
        self.h.event('owner-migrate', self.prior.migration())
        self.h.propose('work-selection-002', (Path(__file__).parents[1] / 'docs/WORK_SELECTION_PROPOSAL.md').read_text())

    def migration(self):
        old = maintenance.protected_manifest(self.h.state)
        return self.prior.migration() | {
            'scope': maintenance.SELECTION_SCOPE, 'approval_sha256': maintenance.SELECTION_SHA256,
            'rule_base': self.h.state['rule_revision'], 'previous_manifest_sha256': maintenance.fingerprint(old),
            'protected_files': old | {name: '8'*64 for name in maintenance.ALLOWED_CHANGES[maintenance.SELECTION_SCOPE]}}

    def test_direct_owner_enactment_preserves_protections_and_can_be_repealed(self):
        before = copy.deepcopy(self.h.state)
        self.h.event('owner-migrate', self.migration())
        state = self.h.state; key = shelf_gate.REVISED_POLICY_ID
        self.assertEqual(shelf_gate.policy(state), key)
        self.assertNotEqual(before['rule_revision'], state['rule_revision'])
        self.assertEqual(state['proposals']['work-selection-002']['status'], 'superseded')
        self.assertEqual(state['proposals'][key]['ratification']['method'], 'direct-owner')
        self.assertIsNone(state['proposals'][key]['notice'])
        for k in ('wake_policy', 'residents', 'tasks', 'lessons', 'life', 'shelf_trials', 'shelf'):
            self.assertEqual(before.get(k), state.get(k), k)
        for k in ('source_sha256', 'authorized_by', 'last_sync', 'decisions', 'base_charter', 'base_active'):
            self.assertEqual(before['council'][k], state['council'][k], k)
        self.h.ready('later-normal-rule')
        self.h.sync()
        self.h.reject('council-enact', {'proposal':'later-normal-rule'}, '24-hour')
        self.h.sync([self.h.comment('REPEAL '+key)])
        self.assertIsNone(shelf_gate.policy(self.h.state))

    def test_wrong_authority_changed_base_repeat_and_extra_scope_reject(self):
        good = self.migration()
        self.h.reject('owner-migrate', good, 'owner operator', 'bob')
        for key, value, error in [('approval_sha256','0'*64,'owner approval'),
                                  ('rule_base','0'*64,'rule base changed')]:
            self.h.reject('owner-migrate', good | {key:value}, error)
        for name in ('house/council.py','house/providers.py','house/wake_policy.py'):
            bad=copy.deepcopy(good);bad['protected_files'][name]='0'*64
            self.h.reject('owner-migrate',bad,'outside.*scope')
        self.h.event('owner-migrate',good)
        self.h.reject('owner-migrate',good,'already used')

    def test_rule_and_owner_instruction_are_exactly_bound(self):
        from house.governance import digest
        root=Path(__file__).parents[1]
        self.assertEqual((root/'docs/WORK_SELECTION_RULE.md').read_text(),shelf_gate.REVISED_POLICY_TEXT)
        self.assertEqual(digest((root/'evidence/selection-repair/owner-direction.txt').read_text()),maintenance.SELECTION_SHA256)
        self.assertEqual(digest((root/'docs/WORK_SELECTION_PROPOSAL.md').read_text()),shelf_gate.POLICY_SHA256)


class RejectShortlistTests(unittest.TestCase):
    def fixture(self):
        fixture=test_shelf.ShelfTests();fixture.setUp();fixture.publish()
        state=fixture.state
        def send(kind, actor='v1', **data):
            candidate=copy.deepcopy(state)
            shelf.apply(candidate, {'actor':actor,'at':state['at']+1,'data':{'kind':kind,**data}},selection_version=2)
            candidate.update(at=state['at']+1,sequence=state['sequence']+1)
            state.clear();state.update(candidate)
        send('choice-open',choice='review',milestones={k:{'milestone':'One useful demonstration'} for k in ('a','b','c')})
        return state,send

    def test_reject_keeps_reasons_frees_explorer_and_preserves_originals(self):
        state,send=self.fixture();original=copy.deepcopy(state['shelf']['ideas'])
        for actor in ('author','v1','v2'):send('choice-vote',actor=actor,choice='review',idea=None,reason='No candidate advances the house enough')
        self.assertEqual(state['shelf']['choices']['review']['status'],'rejected')
        self.assertEqual(state['shelf']['projects'],{})
        for key,item in state['shelf']['ideas'].items():
            self.assertEqual(item['status'],'graveyard')
            self.assertEqual(item['what'],original[key]['what'])
            self.assertTrue(item['history'][-1]['rejected'])
        send('explore-start',actor='other',round='fresh',expect=1,token='fresh',seconds=60)
        self.assertEqual(state['shelf']['explorer'],'fresh')
        before=copy.deepcopy(state)
        with self.assertRaisesRegex(ValueError,'not open'):send('choice-vote',actor='v3',choice='review',idea='a',reason='Late')
        self.assertEqual(state,before)

    def test_split_votes_reject_but_two_votes_start_only_one_project(self):
        for picks in [('a','b','c'),('a',None,None),('a','a',None)]:
            state,send=self.fixture()
            for actor,pick in zip(('v1','v2','v3'),picks):send('choice-vote',actor=actor,choice='review',idea=pick,reason='Independent assessment')
            self.assertEqual(len(state['shelf']['projects']),int(picks==('a','a',None)))
        self.assertEqual(state['shelf']['projects']['review']['idea'],'a')

    def test_author_support_is_uncounted_and_cannot_vote_again(self):
        state,send=self.fixture()
        send('choice-vote',actor='author',choice='review',idea='a',reason='Mine')
        self.assertFalse(state['shelf']['choices']['review']['votes']['author']['counted'])
        with self.assertRaisesRegex(ValueError,'already weighed'):send('choice-vote',actor='author',choice='review',idea=None,reason='Change')
        for actor in ('v1','v2'):send('choice-vote',actor=actor,choice='review',idea=None,reason='Reject')
        self.assertEqual(state['shelf']['choices']['review']['status'],'open')
        send('choice-vote',actor='v3',choice='review',idea=None,reason='Reject')
        self.assertEqual(state['shelf']['choices']['review']['status'],'rejected')
