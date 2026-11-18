"""The public poem ships its real drawing and every local reading asset."""
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import shutil
import subprocess
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/bench-for-two"


class Links(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs
                          if key in {"src", "href"} and value)


class PublicationTests(unittest.TestCase):
    def test_packet_contains_the_entry_and_its_local_destinations(self):
        manifest = json.loads((ROOT / "site/projects.json").read_text())
        entry, = [p for p in manifest["projects"] if p["id"] == "bench-for-two"]
        self.assertEqual(entry["href"], "projects/bench-for-two/index.html")
        self.assertEqual(entry["action"], "Play")
        files = entry["files"]
        self.assertEqual(len(files), len(set(files)))
        for name in files:
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertIn("projects/bench-for-two/gallery-preview.svg", files)
        for link in Links((PROJECT / "index.html").read_text()).links:
            target = urlsplit(link)
            if target.scheme:
                self.assertEqual(target.scheme, "https")
            elif link == "../../#gallery-view":
                self.assertIn('id="gallery-view"', (ROOT / "site/index.html").read_text())
            else:
                destination = posixpath.normpath(posixpath.join("projects/bench-for-two", target.path))
                self.assertIn(destination, files, link)

    def test_preview_is_the_actual_closed_bench_drawing(self):
        source = (PROJECT / "index.html").read_text()
        start = source.index("<svg ")
        original = ET.fromstring(source[start:source.index("</svg>", start) + 6])
        for parent in original.iter():
            for child in list(parent):
                if "open-lid" in child.get("class", "").split():
                    parent.remove(child)
        preview = ET.parse(PROJECT / "gallery-preview.svg").getroot()
        self.assertEqual((preview.attrib.pop("width"), preview.attrib.pop("height")), ("800", "340"))
        background, = [e for e in preview if e.get("id") == "preview-background"]
        self.assertEqual(background.attrib, {"id": "preview-background", "width": "800", "height": "340", "fill": "#20312e"})
        preview.remove(background)

        def shape(element):
            return (element.tag.rsplit("}", 1)[-1], element.attrib,
                    (element.text or "").strip(), [shape(e) for e in element])

        self.assertEqual(shape(preview), shape(original))

    @unittest.skipUnless(shutil.which("node"), "Node executes the real Gallery renderer")
    def test_gallery_link_waits_for_completion(self):
        from tests.test_gallery_room import HARNESS
        checks = r'''
nodes.creations=root;
const entry=manifest.projects.find(p=>p.id==='bench-for-two');
assert(entry);catalog=[entry];frame.shelf.projects=[{idea:entry.id,status:'active'}];
const action=()=>all(root).find(n=>n.className==='creation-action');
show();assert.equal(action(),undefined);renderCollection();assert.equal(action(),undefined);
frame.shelf.projects[0].status='done';show();assert.equal(action().href,entry.href);
renderCollection();const search=get('gallery-search');search.value='BENCH';search.listeners.input();
assert.equal(action().href,entry.href);assert.match(action().textContent,/Play The Bench Was for Two/);
current=false;show();assert.equal(action().href,entry.href);assert.equal(images().length,0);
frame.shelf.projects[0].status='active';show();assert.equal(action(),undefined);
'''
        result = subprocess.run(
            ["node", "-e", HARNESS + "\nvm.runInContext(" + repr(checks) + ",ctx);",
             str(ROOT / "site/house.js"), str(ROOT / "site/projects.json")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
