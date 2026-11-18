"""Hidden paging groups must survive their shared flex styling."""
from pathlib import Path
import re
import shutil
import unittest

from tests import test_archive_lessons, test_counting_room


class HiddenPagerTests(unittest.TestCase):
    def test_shared_pager_style_respects_hidden(self):
        css = (Path(__file__).parents[1] / "site/house.css").read_text()
        # The browser's hidden rule loses to author-level display:flex. Require
        # an author rule scoped to hidden pagers; real layout is tried separately.
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        self.assertIsNotNone(re.search(
            r"\.workshop-pages\[hidden\]\s*\{\s*display\s*:\s*none\s*;?\s*\}", css))

    @unittest.skipUnless(shutil.which("node"), "Node executes the shipped renderers")
    def test_archive_sets_hidden_only_when_results_fit(self):
        test_archive_lessons.ArchiveLessonsTests().run_renderer(r'''
const pages=()=>all(root).find(n=>n.attrs['aria-label']==='Lesson pages');
show();assert.equal(pages().className,'workshop-pages');assert.equal(pages().hidden,false);
get('archive-next').listeners.click();assert.match(text(get('archive-results')),/showing 6–10/);
search('lesson-1');assert.equal(articles().length,3);assert.equal(pages().hidden,true);
search('absent');assert.equal(articles().length,0);assert.equal(pages().hidden,true);
search('');assert.equal(pages().hidden,false);assert.equal(archiveState.page,0);
frame.archive=frame.archive.slice(0,5);show();assert.equal(pages().hidden,true);
frame.archive.push(lesson('sixth'));show();assert.equal(pages().hidden,false);
''')

    @unittest.skipUnless(shutil.which("node"), "Node executes the shipped renderers")
    def test_counting_sets_hidden_only_when_results_fit(self):
        renderer = test_counting_room.CountingRoomTests()
        result = renderer.run_harness({
            "data": renderer.paging_data(), "index": 1, "current": False,
            "selected": "counting",
            "actions": [
                {"id": "counting-agent", "value": "codex"},  # nine runs
                {"id": "counting-next"},
                {"id": "counting-agent", "value": "agy"},  # eight runs
                {"id": "counting-agent", "value": "muse"},  # zero runs
                {"index": 0},  # one run
                {"id": "counting-agent", "value": "all"},
                {"index": 1},  # seventeen runs again
            ],
        })
        self.assertEqual([s["pagesHidden"] for s in result["pageStates"]],
                         [False, False, True, True, True, True, False])
        self.assertEqual(result["pageStates"][1]["focus"], "counting-runs")
        self.assertIn("showing 9–9", result["pageStates"][1]["results"])
