"""The public shelf never presents trial work, future events or private tokens."""
from house.body import export, shelf_view
from tests.support import HouseCase
from tests.test_shelf import idea


class ShelfBodyTests(HouseCase):
    def test_historical_frames_and_real_shelf_are_separate(self):
        self.record.append('life', 'alice', {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6.1-sol'})
        old = export(self.record)['frames']
        self.assertNotIn('shelf', old[-1])
        self.record.append('shelf', 'alice', {'kind': 'explore-start', 'round': 'round',
            'expect': 0, 'token': 'PRIVATE-TOKEN', 'seconds': 60})
        draft = export(self.record)['frames'][-1]['shelf']
        self.assertEqual('alice', draft['explorer']['resident'])
        self.assertNotIn('PRIVATE-TOKEN', str(draft))
        self.record.append('shelf', 'alice', {'kind': 'explore-publish', 'round': 'round',
            'token': 'PRIVATE-TOKEN', 'ideas': [idea('one'), idea('two')]})
        frames = export(self.record)['frames']
        self.assertEqual(old, frames[:len(old)])
        public = frames[-1]['shelf']
        self.assertIsNone(public['explorer'])
        self.assertIsNone(public['policy'])
        self.assertEqual(['one', 'two'], [i['id'] for i in public['ideas']])
        self.assertEqual([], public['projects'])
        state = self.record.read()[0]
        state['shelf_trials'] = {'trial': {'ideas': {'hidden': {'title': 'Trial-only'}}}}
        self.assertNotIn('Trial-only', str(shelf_view(state)))

    def test_graveyard_keeps_counted_reasons_and_project_lessons(self):
        state = self.record.read()[0]
        state['shelf'] = {'ideas': {'one': idea('one') | {'author': 'alice', 'status': 'graveyard',
            'losses': 2, 'history': [{'choice': 'choice', 'won': False}]}},
            'choices': {'choice': {'votes': {'bob': {'counted': True, 'reason': 'Prefer a working map'},
                                           'alice': {'counted': False, 'reason': 'My own idea'}}}},
            'projects': {'old': {'idea': 'one', 'owner': 'alice', 'status': 'dropped',
                'milestone': 'Demo', 'deadline': 100, 'extended': False, 'lesson': 'Too much scope'}}}
        public = shelf_view(state)
        self.assertEqual(['Prefer a working map'], public['ideas'][0]['history'][0]['reasons'])
        self.assertEqual('Too much scope', public['projects'][0]['lesson'])

    def test_great_work_scale_slots_and_stages_preserve_older_frames(self):
        from house import maintenance, shelf, shelf_gate
        self.record.append('life', 'alice', {'kind': 'identity', 'agent': 'codex', 'model': 'gpt-6.1-sol'})
        pre = export(self.record)['frames']
        self.assertNotIn('shelf', pre[-1])
        state = self.record.read()[0]
        state['maintenance'] = {'migrations': {maintenance.COURSE_SCOPE: {}}}
        state['council'] = {'rules': {shelf_gate.GREAT_POLICY_ID: {
            'status': 'active', 'mode': 'rule', 'text': shelf_gate.GREAT_POLICY_TEXT}}}
        state['rule_revision'] = 'rev-004'
        state['shelf'] = {
            'generation': 2, 'explorer': None, 'last_kind': 'codex', 'rounds': {},
            'ideas': {
                'small-1': idea('small-1') | {'author': 'alice', 'status': 'shelved', 'scale': 'small', 'losses': 0, 'history': []},
                'great-1': idea('great-1') | {'author': 'alice', 'status': 'project', 'scale': 'great', 'losses': 0, 'history': []},
            },
            'choices': {},
            'projects': {
                'g-proj': {
                    'idea': 'great-1', 'owner': 'alice', 'status': 'active', 'slot': 'great',
                    'stage': 1, 'milestone': 'Second stage', 'deadline': 500, 'extended': False,
                    'milestones': [
                        {'milestone': 'First stage', 'seconds': 2 * shelf.DAY},
                        {'milestone': 'Second stage', 'seconds': 3 * shelf.DAY},
                    ],
                    'completed': [
                        {'stage': 0, 'milestone': 'First stage', 'evidence': 'task-1', 'sequence': 12},
                    ],
                },
            },
        }
        public = shelf_view(state)
        self.assertEqual(shelf_gate.GREAT_POLICY_ID, public['policy'])
        self.assertFalse(public['great_wanted'])
        by_idea = {item['id']: item for item in public['ideas']}
        self.assertEqual('small', by_idea['small-1']['scale'])
        self.assertEqual('great', by_idea['great-1']['scale'])
        proj = public['projects'][0]
        self.assertEqual('great', proj['slot'])
        self.assertEqual(1, proj['stage'])
        self.assertEqual(['First stage', 'Second stage'], [m['milestone'] for m in proj['milestones']])
        self.assertEqual([{'stage': 0, 'milestone': 'First stage', 'evidence': 'task-1', 'sequence': 12}],
                         proj['completed'])
        state['shelf']['projects']['g-proj']['status'] = 'done'
        self.assertTrue(shelf_view(state)['great_wanted'])
