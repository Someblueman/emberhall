"""Policy fixtures use simulated clocks; they do not enact Emberhall's real rules."""
import copy
from pathlib import Path
import unittest

from house import shelf_gate
from tests import test_council as fixtures
from tests.test_shelf import idea


class ShelfGateTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.CouncilTests(); self.h.setUp(); self.h.authorize()
        self.text = (Path(__file__).parents[1] / 'docs/WORK_SELECTION_PROPOSAL.md').read_text()
        self.h.propose('selection', self.text)
        self.h.event('life', {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6.1-sol'})

    def start(self, **extra):
        self.h.event('shelf', {'kind': 'explore-start', 'round': 'round', 'expect': 0,
                             'token': 'token', 'seconds': 30, **extra})

    def publish(self, **extra):
        self.h.event('shelf', {'kind': 'explore-publish', 'round': 'round', 'token': 'token',
                             'ideas': [idea('a'), idea('b')], **extra})

    def choice(self, **extra):
        return {'kind': 'choice-open', 'choice': 'choice',
                'milestones': {k: {'milestone': 'Working example'} for k in ('a', 'b')}, **extra}

    def test_research_needs_no_enactment_but_real_decisions_do(self):
        self.start(); self.publish()
        self.h.reject('shelf', self.choice(), 'require the enacted')
        self.assertIsNone(shelf_gate.policy(self.h.state))
        self.h.trial('selection'); self.h.endorse('selection', 'bob'); self.h.endorse('selection', 'carol')
        self.h.notice('selection'); self.h.now += fixtures.council.WAIT_SECONDS
        self.h.sync(); self.h.enact('selection')
        self.h.event('shelf', self.choice())
        self.assertEqual('selection', shelf_gate.policy(self.h.state))
        self.h.sync([self.h.comment('REPEAL selection')])
        self.h.reject('shelf', {'kind': 'choice-vote', 'choice': 'choice', 'idea': 'a', 'reason': 'Useful'}, 'require the enacted', 'bob')

    def test_trial_votes_never_populate_real_shelf_or_amend_rules(self):
        rules = self.h.state['rule_revision']
        self.start(trial='selection'); self.publish(trial='selection')
        self.h.event('shelf', self.choice(trial='selection'))
        for actor in ('bob', 'carol', 'dana'):
            self.h.event('shelf', {'kind': 'choice-vote', 'trial': 'selection', 'choice': 'choice', 'idea': 'a', 'reason': 'Fixture vote'}, actor)
        self.assertNotIn('shelf', self.h.state)
        self.assertEqual('active', self.h.state['shelf_trials']['selection']['projects']['choice']['status'])
        self.assertEqual(rules, self.h.state['rule_revision'])
        self.assertEqual('pending', self.h.state['proposals']['selection']['status'])
        self.h.reject('shelf', self.choice(), 'require the enacted')
        self.h.now += 14 * 86400
        self.h.event('say', {'text': 'A later unrelated wake reconciles both kinds of shelf.'})
        self.assertEqual('dropped', self.h.state['shelf_trials']['selection']['projects']['choice']['status'])

    def test_trial_rejects_unknown_changed_vetoed_and_stale_proposals(self):
        self.h.propose('different', self.text + '\nA changed policy.')
        for name in ('missing', 'different'):
            self.h.reject('shelf', self.choice(trial=name), 'supported pending')
        self.h.sync([self.h.comment('VETO selection')])
        self.h.reject('shelf', self.choice(trial='selection'), 'supported pending')
        self.h.propose('supported', self.text)
        self.h.ready('unrelated'); self.h.now += fixtures.council.WAIT_SECONDS
        self.h.sync(); self.h.enact('unrelated')
        self.h.reject('shelf', self.choice(trial='supported'), 'stale rule base')

    def test_lifecycle_hook_closes_explorer_on_sleep_before_rewake(self):
        self.start()
        self.h.event('sleep', {'through': self.h.state['sequence'], 'note': 'Interrupted draft'})
        self.h.event('wake', {})
        before = copy.deepcopy(self.h.state)
        with self.assertRaisesRegex(ValueError, 'no longer active'):
            self.publish()
        self.assertEqual(before, self.h.state)
        self.assertEqual('slept', self.h.state['shelf']['rounds']['round']['status'])

    def test_exact_text_in_another_council_mode_does_not_grant_project_authority(self):
        for mode in ('wake-prompt', 'floor'):
            state = copy.deepcopy(self.h.state)
            state['council']['rules']['wrong-purpose'] = {'status': 'active', 'mode': mode, 'text': self.text}
            self.assertIsNone(shelf_gate.policy(state))
