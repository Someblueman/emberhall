"""Follow stable public lesson identities through the actual Archive renderer."""
from pathlib import Path
import shutil
import subprocess
import unittest

from tests.test_archive_lessons import HARNESS

ROOT = Path(__file__).resolve().parents[1]
SETUP = r'''
const a=(reviews=0,status='observed')=>({...lesson('shared',status,reviews,'Alder','Keep each line.'),id:10});
const b={...lesson('shared','contested',1,'Bay','Keep whole batches.'),id:11};
const snap=(seq,item)=>({seq,archive:[item,b],rooms:[{id:'archive',floor:0}]});
data={frames:[{seq:1,archive:2},snap(12,a()),snap(15,a()),snap(20,a(1)),
 snap(25,a(1,'contested')),snap(30,a(2,'superseded'))]};
frame=data.frames[4];index=4;current=false;
render=()=>{frame=data.frames[index];show();};
choose=id=>{selected=id;show();};
'''


@unittest.skipUnless(shutil.which('node'), 'Node executes the Archive renderer')
class ArchiveLessonTrailTests(unittest.TestCase):
    def run_renderer(self, checks):
        result = subprocess.run(
            ['node', '-e', HARNESS + '\nvm.runInContext(' + repr(SETUP + checks) + ',ctx);',
             str(ROOT / 'site/house.js')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_snapshot_only_trail_loads_history_and_preserves_search(self):
        self.run_renderer(r'''
(async()=>{
const full=data;frame=full.frames[4];
data={frames:[frame],history:{current_only:true,total_frames:25,last_sequence:25}};
selected='archive';show();search('shared');get('archive-follow-10').listeners.click();
assert.doesNotMatch(text(get('archive-trail')),/First available view/);
const load=get('archive-history-load');load.focus();let calls=0;
assert(get('archive-trail-close'));
ensureHistory=async()=>{calls++;data=full;show();return true;};
await load.listeners.click();
assert.equal(calls,1);assert.equal(archiveState.query,'shared');assert.equal(archiveState.trailId,10);
assert.equal(get('archive-history-load'),null);
assert.match(text(get('archive-trail')),/First available view · event 12/);
assert.equal(document.activeElement,get('archive-trail'));
get('archive-visit-10-20').listeners.click();assert.equal(frame.seq,20);
get('archive-return').listeners.click();assert.equal(frame.seq,25);
assert.equal(archiveState.query,'shared');
})();
''')

    def test_history_failure_retries_and_navigation_keeps_focus(self):
        self.run_renderer(r'''
(async()=>{
data.history={current_only:true,total_frames:25,last_sequence:25};
selected='archive';show();get('archive-follow-10').listeners.click();
const load=get('archive-history-load');load.focus();let calls=0;
ensureHistory=async()=>{calls++;return false;};
await load.listeners.click();assert(!load.disabled);
assert.match(text(get('archive-trail')),/could not be loaded. Try again/);
await load.listeners.click();assert.equal(calls,2);
ensureHistory=async()=>{delete data.history;show();get('archive-search').focus();return true;};
await load.listeners.click();assert.equal(document.activeElement,get('archive-search'));
})();
''')

    def test_sparse_observations_keep_identity_and_hide_future(self):
        self.run_renderer(r'''
const before=JSON.stringify(data);
assert.equal(archiveLessonChanges(10,data.frames,frame).map(c=>c.sequence).join(','),'12,20,25');
assert.equal(archiveLessonChanges(11,data.frames,frame).length,1);
show();get('archive-follow-10').listeners.click();
const trail=get('archive-trail');
assert.match(text(trail),/First available view · event 12/);
assert.match(text(trail),/Contested.*checked by 1/);
assert.doesNotMatch(text(trail),/replaced by|event 30|Keep whole batches/);
assert.match(text(trail),/Missing snapshots can hide earlier changes/);
assert.equal(all(trail).filter(n=>n.tag==='button'&&n.id.startsWith('archive-visit-')).length,3);
assert(get('archive-visit-10-25').disabled);
assert.equal(document.activeElement,trail);assert(trail.scrolled);
assert.equal(JSON.stringify(data),before);
''')

    def test_visit_and_return_restore_search_comparison_page_and_focus_after_refresh(self):
        self.run_renderer(r'''
current=true;data.frames.pop();show();search('shared');filter('contested');
get('archive-compare-lesson-10').listeners.click();get('archive-compare-lesson-11').listeners.click();
get('archive-follow-10').listeners.click();
const saved=JSON.stringify(archiveState);get('archive-visit-10-20').listeners.click();
assert.equal(frame.seq,20);assert(!current);assert.equal(archiveState.query,'');
assert.equal(archiveState.status,'all');assert.equal(archiveState.compare.length,0);
assert.match(text(get('archive-trail')),/checked by 1 other resident/);
assert.doesNotMatch(text(get('archive-trail')),/event 25|Contested/);
assert.equal(document.activeElement,get('archive-trail'));
data.frames.push(snap(40,a(3,'superseded')));show();
get('archive-return').listeners.click();
assert.equal(frame.seq,25);assert(!current,'An old latest is now a historical moment');
assert.equal(selected,'archive');assert.equal(JSON.stringify(archiveState),saved);
assert.equal(document.activeElement,get('archive-visit-10-20'));assert.equal(archiveReturn,null);
assert.match(text(get('archive-comparison')),/Keep each line.*Keep whole batches/);
''')

    def test_paging_close_and_refresh_keep_keyboard_place(self):
        self.run_renderer(r'''
data.frames=Array.from({length:10},(_,i)=>snap(12+i,a(i)));
frame=data.frames[9];current=true;show();get('archive-follow-10').listeners.click();
assert.equal(all(get('archive-trail')).filter(n=>n.id?.startsWith('archive-visit-')).length,4);
get('archive-trail-older').listeners.click();assert.equal(archiveState.trailPage,1);
assert.equal(document.activeElement,get('archive-trail'));
get('archive-trail-older').focus();
roomPanel=show;lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=renderLately=()=>{};
refreshView();assert.equal(archiveState.trailPage,1);
assert.equal(document.activeElement,get('archive-trail-older'));
get('archive-visit-10-16').listeners.click();get('archive-return').listeners.click();
assert.equal(archiveState.trailPage,1);assert.equal(document.activeElement,get('archive-visit-10-16'));
get('archive-trail-close').listeners.click();assert(get('archive-trail').hidden);
assert.equal(document.activeElement,get('archive-follow-10'));
get('archive-follow-10').listeners.click();search('absent');
get('archive-trail-close').listeners.click();assert.equal(document.activeElement,get('archive-search'));
''')

    def test_legacy_same_subject_and_missing_return_snapshot_are_explicit(self):
        self.run_renderer(r'''
frame={seq:40,archive:[{...a(),id:undefined}, {...a(),id:undefined}]};show();
assert(!all(root).some(n=>n.id?.startsWith('archive-follow-')));
assert.match(text(root),/no stable lesson identity/);
frame=data.frames[4];show();get('archive-follow-10').listeners.click();
get('archive-visit-10-12').listeners.click();
data.frames=data.frames.filter(f=>f.seq!==25);show();
assert.equal(get('archive-return'),null);assert.match(text(root),/original Archive moment is absent/);
frame={seq:1};show();assert.match(text(root),/not their text/);
assert.match(text(root),/original Archive moment is absent/);
''')

    def test_claim_changes_and_names_remain_literal_text(self):
        self.run_renderer(r'''
data.frames[2].archive[0]={...a(),claim:'<script>old text</script>',author:'<img src=x>'};
frame=data.frames[4];show();get('archive-follow-10').listeners.click();
const trail=get('archive-trail');assert.match(text(trail),/Claim then: <script>old text/);
assert.match(text(trail),/<img src=x>/);assert(!all(trail).some(n=>['script','img'].includes(n.tag)));
''')

    def test_return_keeps_original_result_page_through_nested_visits(self):
        self.run_renderer(r'''
data.frames.pop();current=true;
frame.archive.push(...Array.from({length:6},(_,i)=>({...a(),id:50+i,key:'other-'+i})));
show();get('archive-next').listeners.click();assert.equal(archiveState.page,1);
get('archive-follow-10').listeners.click();get('archive-visit-10-20').listeners.click();
get('archive-visit-10-12').listeners.click();
assert.equal(archiveReturn.sequence,25);get('archive-return').listeners.click();
assert.equal(frame.seq,25);assert(current);assert.equal(archiveState.page,1);
assert.equal(document.activeElement,get('archive-visit-10-20'));
''')
