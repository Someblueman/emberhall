"""The real room panel links only an opened Chronicle to its public page."""
from pathlib import Path
import shutil
import subprocess
import unittest

from tests.test_workshop_ui import HARNESS


@unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
class ChronicleDoorTests(unittest.TestCase):
    def test_recorded_opening_and_history(self):
        script = HARNESS + r'''
vm.runInContext(`
selected='chronicle';
frame={seq:5,at:1000,rooms:[],residents:[],runs:[],scars:[],tasks:[],floors:[{level:0,name:'Ground floor'}]};
const bookmarkLinks=()=>all(panel()).filter(n=>n.tag==='a'&&n.href==='#room/chronicle');
const nonBookmarkLinks=()=>all(panel()).filter(n=>n.tag==='a'&&!String(n.href).startsWith('#room/'));
roomPanel();assert.equal(all(panel()).filter(n=>n.tag==='a').length,0);
const room={id:'chronicle',name:'The Chronicle',floor:0,status:'construction'};
frame.rooms.push(room);
for(const status of ['construction','closed',undefined]) {
 room.status=status;roomPanel();
 assert.equal(bookmarkLinks().length,1);
 assert.equal(nonBookmarkLinks().length,0);
}
room.status='open';roomPanel();
assert.equal(bookmarkLinks().length,1);
assert.equal(nonBookmarkLinks().length,1);
assert.equal(nonBookmarkLinks()[0].href,'chronicle/index.html');
assert.match(text(panel()),/Read the Chronicle/);
current=false;roomPanel();assert.match(text(panel()),/latest published Chronicle/);
frame.rooms=[];roomPanel();assert.equal(all(panel()).filter(n=>n.tag==='a').length,0);
`,context);
'''
        result = subprocess.run(['node', '-e', script, str(Path(__file__).parents[1] / 'site/house.js')],
                                input='', capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
