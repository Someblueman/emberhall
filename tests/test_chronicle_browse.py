"""Native Chronicle controls preserve the public record and publisher contract."""
import importlib.util
from pathlib import Path
import re
from types import SimpleNamespace
import unittest

from house import chronicle_page, publish

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/emberhall-chronicle-room"


class ChronicleBrowseTests(unittest.TestCase):
    def setUp(self):
        self.events, self.through, self.house = chronicle_page.load_export(
            PROJECT / "fixtures/synthetic_journal.json")
        self.entries = chronicle_page.select_milestones(self.events)

    def test_native_controls_counts_and_unmodified_record_order(self):
        before = repr(self.entries)
        page = chronicle_page.render_html(self.entries, through=self.through)
        labels = {"all": "All milestones (6)", "project": "Finished creations (1)",
                  "rule": "Enacted rules (2)", "choice": "Closed choices (2)",
                  "rejected": "None chosen (1)"}
        for key, label in labels.items():
            self.assertIn(f'for="chronicle-{key}"', page)
            self.assertIn(f'id="chronicle-{key}" value="{key}"', page)
            self.assertIn(label, page)
        self.assertIn('value="all" checked', page)
        self.assertNotIn('<script', page)
        self.assertNotIn('id="chronicle-earlier"', page)
        sequences = re.findall(r' · event (\d+)</p>', page)
        self.assertEqual(sequences, [str(m['sequence']) for m in reversed(self.entries)])
        self.assertEqual(repr(self.entries), before)

    def test_empty_categories_escaping_and_complete_older_records(self):
        item = self.entries[1] | {"title": '<img src=x onerror="bad">', "sequence": 1}
        entries = [item | {"sequence": n} for n in range(1, 12)]
        page = chronicle_page.render_html(entries)
        self.assertEqual(page.count('<article '), 11)
        self.assertEqual(page.count(' earlier-entry"'), 3)
        self.assertIn('Show all 11 milestones', page)
        self.assertIn('&lt;img src=x onerror=&quot;bad&quot;&gt;', page)
        self.assertNotIn('<img', page)
        self.assertIn('No enacted rules recorded in this snapshot.', page)
        empty = chronicle_page.render_html([])
        self.assertIn('empty-all', empty)
        self.assertNotIn('<article ', empty)
        self.assertNotIn('id="chronicle-earlier"', empty)

    def test_publisher_and_standalone_render_identically(self):
        spec = importlib.util.spec_from_file_location('standalone_chronicle', PROJECT / 'chronicle.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.render_html(self.entries, through=self.through, house_id=self.house),
                         chronicle_page.render_html(self.entries, through=self.through, house_id=self.house))
        ordered = sorted(self.events, key=lambda e: e['sequence'])
        record = SimpleNamespace(read=lambda: ({'house_id': self.house}, ordered, 'head'))
        first = publish.chronicle_body(record, {})
        self.assertEqual(first, publish.chronicle_body(record, {}))
        self.assertIn(b'<legend>Browse milestones</legend>', first)
        for secret in (b'RAW_REASON', b'secret-claim-token', b'RAW_RULE_TEXT', b'secret123'):
            self.assertNotIn(secret, first)
