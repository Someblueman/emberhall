"""The live exhibit belongs to a completed, currently published Signal Garden."""
import json
import shutil
import subprocess
import unittest

from tests.test_gallery_room import HARNESS, ROOT


@unittest.skipUnless(shutil.which("node"), "Node executes the Gallery renderer")
class GallerySignalTrialTests(unittest.TestCase):
    def test_only_the_current_shipped_exhibit_loads_and_refresh_keeps_it_open(self):
        checks = """
        nodes.creations = root;
        const exhibit = nodes['gallery-signal-trial'] = new Element('iframe');
        exhibit.tagName = 'IFRAME';
        exhibit.getAttribute = name => exhibit.attrs[name] ?? null;
        exhibit.hasAttribute = name => Object.hasOwn(exhibit.attrs, name);
        exhibit.removeAttribute = name => delete exhibit.attrs[name];
        let loads = 0;
        Object.defineProperty(exhibit, 'src', {set(path) { this.attrs.src = path; loads++; }});
        const entry = catalog.find(p => p.id === 'signal-garden');
        const page = 'projects/signal-garden/gallery.html';
        const gallery = nodes['gallery-view'] = new Element('section');
        gallery.hidden = true;
        renderCollection();
        assert.equal(loads, 0);
        gallery.hidden = false;
        function check(visible) {
          renderCollection();
          assert.equal(exhibit.hidden, !visible);
          assert.equal(exhibit.attrs.src, visible ? page : undefined);
        }
        check(true); check(true); assert.equal(loads, 1);
        current = false; check(false);
        current = true; check(true); assert.equal(loads, 2);
        for (const missing of [page, 'projects/signal-garden/model.js']) {
          catalog = [{...entry, files: entry.files.filter(path => path !== missing)}];
          check(false);
        }
        catalog = [entry];
        frame.shelf.projects.find(p => p.idea === entry.id).status = 'active';
        check(false);
        catalog = null; check(false);
        """
        script = HARNESS + "\nvm.runInContext(" + json.dumps(checks) + ", ctx);"
        subprocess.run(["node", "-e", script, str(ROOT / "site/house.js"),
                        str(ROOT / "site/projects.json")], check=True, timeout=15)
