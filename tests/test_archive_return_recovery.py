"""Recover from missing public snapshots without poisoning a new Archive trip."""
import shutil
import unittest

from tests import test_archive_lesson_trail as trail


@unittest.skipUnless(shutil.which("node"), "Node executes the Archive renderer")
class ArchiveReturnRecoveryTests(unittest.TestCase):
    run_renderer = trail.ArchiveLessonTrailTests.run_renderer

    def test_missing_source_allows_fresh_trip_and_exact_return(self):
        self.run_renderer(r'''
show();get('archive-follow-10').listeners.click();get('archive-visit-10-20').listeners.click();
data.frames=data.frames.filter(f=>f.seq!==25);show();
assert.equal(get('archive-return'),null);assert.match(text(root),/original Archive moment is absent/);
search('shared');filter('reviewed');get('archive-compare-lesson-10').listeners.click();
const saved=JSON.stringify(archiveState),before=JSON.stringify(data);
get('archive-visit-10-12').listeners.click();
assert.equal(archiveReturn.sequence,20);assert.equal(frame.seq,12);
assert.doesNotMatch(text(get('archive-trail')),/event 20|Contested|replaced by/);
assert(get('archive-return'));get('archive-return').listeners.click();
assert.equal(frame.seq,20);assert.equal(JSON.stringify(archiveState),saved);
assert.equal(document.activeElement,get('archive-visit-10-12'));
assert.equal(archiveReturn,null);assert.equal(JSON.stringify(data),before);
''')

    def test_retained_origin_still_survives_nested_trips(self):
        self.run_renderer(r'''
show();search('shared');get('archive-follow-10').listeners.click();
const saved=JSON.stringify(archiveState);get('archive-visit-10-20').listeners.click();
get('archive-visit-10-12').listeners.click();
assert.equal(archiveReturn.sequence,25);get('archive-return').listeners.click();
assert.equal(frame.seq,25);assert.equal(JSON.stringify(archiveState),saved);
assert.equal(document.activeElement,get('archive-visit-10-20'));
''')

    def test_origin_disappears_between_draw_and_click(self):
        self.run_renderer(r'''
show();get('archive-follow-10').listeners.click();get('archive-visit-10-20').listeners.click();
const visit=get('archive-visit-10-12');
data.frames=data.frames.filter(f=>f.seq!==25);
visit.listeners.click();assert.equal(archiveReturn.sequence,20);
get('archive-return').listeners.click();assert.equal(frame.seq,20);
''')
