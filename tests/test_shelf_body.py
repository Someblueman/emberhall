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
