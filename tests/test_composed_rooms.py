"""The real room renderer: record relationships, entry and return boundaries."""
from pathlib import Path
import shutil
import subprocess
import unittest

from tests.test_gallery_room import HARNESS
from tests.test_gallery_picture import PICTURE_DOM

ROOT = Path(__file__).resolve().parents[1]
SETUP = r'''
vm.runInContext(`
globalThis.window={scrollY:285,scrollTo:options=>{window.scrollY=options.top;}};
data={timezone:'UTC',observed_at:1000,frames:[frame]};
frame.at=1000;frame.work=[];frame.residents=[{id:'fern',name:'Fern'}];
selected='gallery';
const attempt=()=>get('gallery-room-try-tessera-loom');
`,ctx);
'''


@unittest.skipUnless(shutil.which('node'), 'Node executes the actual renderer')
class ComposedRoomTests(unittest.TestCase):
    def check(self, script):
        result = subprocess.run(
            ['node', '-e', HARNESS + PICTURE_DOM + SETUP +
             '\nvm.runInContext(' + repr(script) + ',ctx);',
             str(ROOT / 'site/house.js'), str(ROOT / 'site/projects.json')],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bench_keeps_holder_project_and_real_account_together(self):
        self.check(r'''
frame.shelf.projects=[{id:'project-one',title:'The real work',owner:'fern',status:'active',
 plain:'A result another mind can check.',milestone:'One working result'},
 {id:'done',title:'Already accepted',owner:'fern',status:'done'}];
frame.tasks=[{id:'finished-task',status:'done',project:'project-one'}];
const before=JSON.stringify(frame);root.replaceChildren();renderWorkshopInterior(root);
assert.match(text(root),/Project held by Fern.*The real work/);
assert.match(text(root),/One working result/); // The existing account is present, not a mock.
assert.doesNotMatch(text(root),/Already accepted/);
assert.match(text(root),/In progress/); // A finished task did not turn its project into accepted work.
assert(get('bench-account-project-one'));
const detail=all(root).find(node=>node.className==='bench-account');
detail.open=true;detail.listeners.toggle();root.replaceChildren();renderWorkshopInterior(root);
assert(all(root).find(node=>node.className==='bench-account').open);
assert.equal(JSON.stringify(frame),before);
frame.residents=[];root.replaceChildren();renderWorkshopInterior(root);
assert.match(text(root),/Holder not named in this snapshot/);
assert.doesNotMatch(text(root),/Project held by Fern/);
frame.shelf.projects=[];root.replaceChildren();renderWorkshopInterior(root);
assert.match(text(root),/No active project is recorded/);
assert(!get('bench-account-project-one'));
''')

    def test_hearth_uses_the_speakers_name_at_the_time_and_excludes_future_words(self):
        self.check(r'''
const old={seq:4,at:4,name:'Earlier Fern',resident:'fern',text:'The first words'};
const latest={seq:8,at:8,name:'Fern',resident:'fern',text:'A later voice'};
const future={seq:100,at:100,name:'Future person',text:'Future words'};
data.frames=[{seq:4,hearth:[old]},{seq:8,hearth:[latest,future]}];
frame={seq:4,at:4,hearth:[old],residents:[{id:'fern',name:'Fern today'}]};
root.replaceChildren();renderHearthInterior(root);
assert.match(text(root),/Earlier Fern.*The first words/);
assert.doesNotMatch(text(root),/Fern today|A later voice|Future/);
let focused;roomPanel=()=>{};workshopFocus=id=>{focused=id;};
get('room-voice-1').listeners.click();
assert.equal(hearthState.speaker,'resident:fern');assert.equal(focused,'hearth-messages');
frame={seq:1};root.replaceChildren();renderHearthInterior(root);
assert.match(text(root),/does not publish the words/);assert(!get('room-voice-1'));
''')

    def test_creation_uses_manifest_path_and_returns_to_exact_display_after_refresh(self):
        self.check(r'''
show();const opener=pictureButton();
assert.match(opener.attrs['aria-label'],/Try Tessera Loom here/);opener.listeners.click();
const dialog=get('room-creation');assert(dialog.open);
const iframe=all(dialog).find(n=>n.tag==='iframe');
assert.equal(iframe.src,'projects/tessera-loom/index.html');
assert.equal(iframe.attrs.sandbox,'allow-scripts');assert.equal(iframe.title,'Try Tessera Loom');
assert.equal(document.activeElement,get('room-creation-close'));
const selectedWork=galleryRoomChoice;show();assert.equal(galleryRoomChoice,selectedWork);
window.scrollY=400;get('room-creation-close').listeners.click();
assert.equal(roomCreation,null);assert.equal(get('room-creation'),null);
assert.equal(document.activeElement,pictureButton());assert.notEqual(pictureButton(),opener);
assert.equal(window.scrollY,285);
''')

    def test_history_missing_files_and_room_changes_unload_the_live_creation(self):
        self.check(r'''
show();attempt().listeners.click();current=false;reconcileRoomCreation();
assert.equal(roomCreation,null);show();assert(!attempt());
assert(!all(root).some(n=>n.tag==='img')); // Today's artwork never depicts an old visit.
current=true;show();attempt().listeners.click();selected='workshop';reconcileRoomCreation();
assert.equal(roomCreation,null);
selected='gallery';show();attempt().listeners.click();frame.rooms[0].status='closed';reconcileRoomCreation();
assert.equal(roomCreation,null);frame.rooms[0].status='open';
selected='gallery';show();const entry=completedCatalog()[0];
openRoomCreation({...entry,href:'https://outside.invalid'},attempt());assert.equal(roomCreation,null);
openRoomCreation({...entry,files:[]},attempt());assert.equal(roomCreation,null);
frame.shelf.projects=[];openRoomCreation(entry,attempt());assert.equal(roomCreation,null);
''')

    def test_only_script_sandbox_compatible_exhibits_get_an_in_room_action(self):
        self.check(r'''
frame.shelf.projects=frame.shelf.projects.map(project=>({...project,
 completed:project.idea==='bench-for-two'?[{sequence:89}]:[]}));
show();assert.equal(galleryRoomChoice,'bench-for-two'); // Keep the chronological display.
get('gallery-room-invite-tessera-loom').listeners.click();
assert.equal(galleryRoomChoice,'tessera-loom');assert(get('room-creation').open);
get('room-creation-close').listeners.click();assert.equal(document.activeElement,attempt());
const signalWork=completedCatalog().find(entry=>entry.id==='signal-garden');
assert.equal(roomCreationUrl(signalWork),'projects/signal-garden/gallery.html');
openRoomCreation(signalWork,{id:'opener'});
assert.equal(all(get('room-creation')).find(node=>node.tag==='iframe').src,
 'projects/signal-garden/gallery.html');
get('room-creation-close').listeners.click();
assert.equal(roomCreationUrl({...signalWork,files:[]}),null);
assert.equal(roomCreationUrl(completedCatalog().find(entry=>entry.id==='night-ferry')),null);
assert.equal(roomCreationUrl({...signalWork,id:'__proto__'}),null);
''')


if __name__ == '__main__':
    unittest.main()
