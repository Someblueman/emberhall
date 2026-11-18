"""Keep the shipped film, Gallery preview and public file list together."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tests.test_gallery_room import HARNESS

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/lantern-loop"


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.videos = []

    def handle_starttag(self, tag, attrs):
        if tag == "video":
            self.videos.append(dict(attrs))
        for key, value in attrs:
            if key in {"href", "src"} and value and not value.startswith("#"):
                self.links.append(value)


@unittest.skipUnless(shutil.which("node"), "Node draws the actual film")
class LanternGalleryTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffprobe"), "FFprobe reads the shipped movie")
    def test_native_film_contains_six_seconds_of_silent_drawings(self):
        info = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,codec_name,width,height,nb_frames,r_frame_rate",
             "-of", "json", str(PROJECT / "lantern-loop.mp4")], timeout=15))
        self.assertEqual(float(info["format"]["duration"]), 6)
        self.assertEqual(info["streams"], [{
            "codec_type": "video", "codec_name": "h264", "width": 900, "height": 440,
            "nb_frames": "144", "r_frame_rate": "24/1",
        }])

    def test_native_players_are_labelled_local_and_do_not_autoplay(self):
        for path, movie in [(PROJECT / "index.html", "lantern-loop.mp4"),
                            (ROOT / "site/index.html", "projects/lantern-loop/lantern-loop.mp4")]:
            with self.subTest(page=path):
                parser = LocalLinks()
                parser.feed(path.read_text())
                videos = [video for video in parser.videos if video.get("src") == movie]
                self.assertEqual(len(videos), 1)
                video = videos[0]
                self.assertIn("controls", video)
                self.assertIn("playsinline", video)
                self.assertNotIn("autoplay", video)
                self.assertTrue(video.get("aria-label"))
        self.assertIn("media-src 'self'", (PROJECT / "index.html").read_text())

    def test_preview_matches_the_final_film_frame_with_valid_resources(self):
        generated = subprocess.check_output(
            ["node", str(PROJECT / "make-gallery-preview.cjs")], cwd=ROOT, timeout=15)
        self.assertEqual((PROJECT / "gallery-preview.svg").read_bytes(), generated)
        tree = ET.fromstring(generated)
        self.assertEqual((tree.attrib["width"], tree.attrib["height"]), ("1200", "700"))
        ids = [node.attrib["id"] for node in tree.iter() if "id" in node.attrib]
        self.assertEqual(len(ids), len(set(ids)))
        for resource in re.findall(rb"url\(#([^)]*)\)", generated):
            self.assertIn(resource.decode(), ids)
        self.assertIn(b"shot 2 at 6.00 seconds", generated)
        self.assertNotIn(b"<script", generated)
        self.assertNotRegex(generated.decode(), r'(?:href|src)="(?:https?:|//)')

    def test_manifest_ships_every_page_link_without_build_or_test_files(self):
        manifest = json.loads((ROOT / "site/projects.json").read_text())
        entry = next(p for p in manifest["projects"] if p["id"] == "lantern-loop")
        self.assertEqual(entry["href"], "projects/lantern-loop/index.html")
        self.assertEqual(entry["action"], "Play")
        self.assertEqual(len(entry["files"]), len(set(entry["files"])))
        parser = LocalLinks()
        parser.feed((PROJECT / "index.html").read_text())
        for link in parser.links:
            path = "projects/lantern-loop/" + link
            self.assertIn(path, entry["files"])
        for name in entry["files"]:
            self.assertTrue((ROOT / name).is_file(), name)
            self.assertFalse("test_" in name or "make-gallery" in name)
        self.assertNotIn("workprint awaiting", (PROJECT / "index.html").read_text())

    def test_gallery_reaches_film_after_completion_and_hides_future_picture(self):
        checks = r'''
catalog=[manifest.projects.find(p=>p.id==='lantern-loop')];
frame.shelf.projects=[{idea:'lantern-loop',status:'active'}];show();
assert.equal(all(root).filter(n=>n.className==='creation-action').length,0);
frame.shelf.projects[0].status='done';show();
assert.equal(images().length,1);assert.match(images()[0].alt,/Two moths/);
assert.equal(images()[0].src,'projects/lantern-loop/gallery-preview.svg');
const link=all(root).find(n=>n.className==='creation-action');
assert.equal(link.href,'projects/lantern-loop/index.html');assert.match(link.textContent,/Play Lantern Loop/);
current=false;show();assert.equal(images().length,0);
assert.equal(all(root).find(n=>n.className==='creation-action').href,link.href);
'''
        result = subprocess.run(
            ["node", "-e", HARNESS + "\nvm.runInContext(" + repr(checks) + ",ctx);",
             str(ROOT / "site/house.js"), str(ROOT / "site/projects.json")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
