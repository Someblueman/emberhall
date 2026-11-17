"""The mathematical encounter ships with its complete, navigable account."""
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import unittest
from urllib.parse import urlsplit

from tests.test_gallery_room import HARNESS

ROOT = Path(__file__).resolve().parents[1]


class PageLinks(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.ids = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)
            if key == "id":
                self.ids.append(value)


class FiveMarksPublicationTests(unittest.TestCase):
    def test_public_packet_has_no_missing_local_destinations(self):
        manifest = json.loads((ROOT / "site/projects.json").read_text())
        entry, = [p for p in manifest["projects"] if p["id"] == "five-mark-packing"]
        self.assertEqual(entry["href"], "projects/five-marks/index.html")
        files = set(entry["files"])
        self.assertEqual(len(files), len(entry["files"]))
        for name in files:
            with self.subTest(file=name):
                path = ROOT / name
                self.assertTrue(path.is_file(), name)
                source = path.read_text()
                if path.suffix == ".html":
                    page = PageLinks(source)
                    self.assertEqual(len(page.ids), len(set(page.ids)), name)
                    links = page.links
                elif path.suffix == ".md":
                    links = re.findall(r"\]\(([^)]+)\)", source)
                else:
                    continue
                for link in links:
                    target = urlsplit(link)
                    if target.scheme or target.netloc:
                        self.assertEqual(target.scheme, "https", link)
                        continue
                    # The companion's return is to the house Gallery, not
                    # another file in the mathematical packet.
                    if link == "../../#gallery-view":
                        self.assertIn("gallery-view", PageLinks(
                            (ROOT / "site/index.html").read_text()).ids)
                        continue
                    dest = posixpath.normpath(posixpath.join(
                        posixpath.dirname(name), target.path)) if target.path else name
                    self.assertIn(dest, files, f"{name} -> {link}")
                    if target.fragment and dest.endswith(".html"):
                        self.assertIn(target.fragment, PageLinks(
                            (ROOT / dest).read_text()).ids, f"{name} -> {link}")
        self.assertIn("projects/five-marks/check.py", files)
        self.assertIn("projects/five-marks/test_exhibit.cjs", files)
        self.assertIn("projects/five-marks/PUBLICATION_LITERATURE.md", files)

    @unittest.skipUnless(shutil.which("node"), "Node executes the real Gallery renderer")
    def test_gallery_waits_for_completion_and_search_reaches_the_encounter(self):
        checks = r'''
nodes.creations=root;
const entry=manifest.projects.find(p=>p.id==='five-mark-packing');
catalog=[entry];frame.shelf.projects=[{idea:entry.id,status:'active'}];
const action=()=>all(root).find(n=>n.className==='creation-action');
show();assert.equal(action(),undefined);
renderCollection();assert.equal(action(),undefined);
frame.shelf.projects[0].status='done';show();assert.equal(action().href,entry.href);
renderCollection();
const search=get('gallery-search');search.value='FIVE MARKS';search.listeners.input();
assert.equal(action().href,entry.href);assert.match(action().textContent,/Open Five Marks/);
current=false;show();assert.equal(action().href,entry.href);
frame.shelf.projects[0].status='active';show();assert.equal(action(),undefined);
'''
        result = subprocess.run(
            ["node", "-e", HARNESS + "\nvm.runInContext(" + repr(checks) + ",ctx);",
             str(ROOT / "site/house.js"), str(ROOT / "site/projects.json")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
