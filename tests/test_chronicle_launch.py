"""Chronicle launch links use published catalogue files and recorded completion."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from house import chronicle_page, publish

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'projects/emberhall-chronicle-room/fixtures/synthetic_journal.json'


class ChronicleLaunchTests(unittest.TestCase):
    def setUp(self):
        self.events, self.through, self.house = chronicle_page.load_export(FIXTURE)
        # The fixture records a real choice closure followed by project-done.
        self.events = json.loads(json.dumps(self.events).replace('alpha-tool', 'night-ferry'))
        self.catalog = json.loads((ROOT / 'site/projects.json').read_text())
        self.entries = chronicle_page.select_milestones(self.events)

    def render(self, catalog=None):
        return chronicle_page.render_html(self.entries, catalog=catalog or self.catalog)

    def test_completed_creation_launch_and_source_link(self):
        page = self.render()
        self.assertEqual(page.count('class="launch"'), 1)
        self.assertIn('href="../projects/night-ferry/player/index.html">Play Alpha Tool', page)
        self.assertIn('https://github.com/Someblueman/emberhall/tree/main/projects/night-ferry/', page)
        self.assertIn('#gallery-view', page)
        self.assertIn('current published versions', page)
        # Every accepted route has an actual file in the repository catalogue.
        actions = chronicle_page._browser_actions(self.catalog)
        self.assertGreaterEqual(len(actions), 7)
        for _, href in actions.values():
            self.assertTrue(href.endswith('.html'), href)
            target = href.removeprefix('../')
            if target.endswith('/'):
                target += 'index.html'
            self.assertTrue((ROOT / target).is_file(), target)

    def test_no_launch_before_completion_or_for_tool_guides(self):
        before = [e for e in self.events if e['sequence'] < 16]
        page = chronicle_page.render_html(chronicle_page.select_milestones(before), catalog=self.catalog)
        self.assertNotIn('class="launch"', page)
        guide = copy.deepcopy(self.catalog)
        for entry in guide['projects']:
            if entry['id'] == 'night-ferry':
                entry['action'] = 'Read guide'
        self.assertNotIn('class="launch"', self.render(guide))
        self.assertNotIn('class="launch"', chronicle_page.render_html(self.entries))

    def test_invalid_or_unshipped_routes_never_launch(self):
        original = next(p for p in self.catalog['projects'] if p['id'] == 'night-ferry')
        for href in ('javascript:alert(1)', '//example.org/', 'https://example.org/',
                     'projects/night-ferry/../private.html', 'projects/night-ferry/%2e%2e/',
                     'projects/other/index.html', 'projects/night-ferry/missing.html',
                     'projects/night-ferry/player/?token=secret', 'projects/night-ferry/"bad.html'):
            with self.subTest(href=href):
                entry = original | {'href': href}
                self.assertNotIn('class="launch"', self.render({'version': 1, 'projects': [entry]}))
        self.assertEqual(chronicle_page._browser_actions({'version': True, 'projects': [original]}), {})
        self.assertEqual(chronicle_page._browser_actions({'version': 1, 'projects': [original | {'files': []}]}), {})

    def test_publisher_and_standalone_generator_use_supplied_catalogue(self):
        ordered = sorted(self.events, key=lambda event: event['sequence'])
        record = SimpleNamespace(read=lambda: ({'house_id': self.house}, ordered, 'head'))
        page = publish.chronicle_body(record, {'projects.json': json.dumps(self.catalog).encode()})
        self.assertIn(b'class="launch"', page)
        self.assertNotIn(b'class="launch"', publish.chronicle_body(record, {}))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export = root / 'prefix.json'
            export.write_text(json.dumps({'events': self.events, 'through': self.through, 'house_id': self.house}))
            first = chronicle_page.generate(export, root / 'first', ROOT / 'site/projects.json')
            second = chronicle_page.generate(export, root / 'second', ROOT / 'site/projects.json')
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertIn(b'class="launch"', first.read_bytes())
