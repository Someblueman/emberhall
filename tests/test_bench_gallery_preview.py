"""The poem's real opening uses the existing dated Gallery and picture controls."""
from pathlib import Path
import shutil
import subprocess
import unittest

from tests.test_gallery_room import HARNESS
from tests.test_gallery_picture import PICTURE_DOM

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node executes the real renderer")
class BenchGalleryTests(unittest.TestCase):
    def test_picture_credit_launch_and_keyboard_return(self):
        checks = r'''
const entry=manifest.projects.find(p=>p.id==='bench-for-two');
catalog=[entry];show();const small=images()[0];assert(small);
assert.equal(small.src,'projects/bench-for-two/gallery-preview.svg');
assert.equal(small.width,800);assert.equal(small.height,340);
assert.match(small.alt,/two worn places/i);assert.match(small.alt,/two envelopes/i);
assert(entry.files.includes(small.src));assert.match(text(root),/Fern/);
const opener=openPicture(),dialog=get('gallery-picture');
assert.equal(document.activeElement,get('gallery-picture-close'));
assert.equal(all(dialog).find(n=>n.tag==='img').src,small.src);
assert.equal(all(dialog).find(n=>n.tag==='a').href,entry.href);
show();get('gallery-picture-close').listeners.click();
assert.notEqual(pictureButton(),opener);assert.equal(document.activeElement,pictureButton());
assert.equal(all(root).find(n=>n.className==='creation-action').href,entry.href);
openPicture();current=false;show();assert.equal(creationPicture,null);
assert.equal(images().length,0);assert.equal(pictureButton(),undefined);
assert.equal(all(root).find(n=>n.className==='creation-action').href,entry.href);
current=true;frame.shelf.projects=[{idea:entry.id,status:'active'}];show();
assert.equal(images().length,0);assert.equal(pictureButton(),undefined);
assert.equal(all(root).find(n=>n.className==='creation-action'),undefined);
frame.shelf.projects[0].status='done';catalog=[{...entry,files:[]}];show();
assert.equal(images().length,0);assert.equal(pictureButton(),undefined);
'''
        result = subprocess.run(
            ["node", "-e", HARNESS + PICTURE_DOM + "\nvm.runInContext(" + repr(checks) + ",ctx);",
             str(ROOT / "site/house.js"), str(ROOT / "site/projects.json")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
