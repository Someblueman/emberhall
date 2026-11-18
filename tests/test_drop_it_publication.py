"""The Gallery Play link ships the two-stage act and its browser dependencies."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from tests.test_terminal_public_player import PageLinks

SOURCE = Path(__file__).resolve().parents[1]


class DropItPublicationTests(unittest.TestCase):
    def test_gallery_entry_includes_the_playable_stage(self):
        manifest = json.loads((SOURCE / "site/projects.json").read_text())
        entry = next(p for p in manifest["projects"] if p["id"] == "you-were-supposed-to-drop-it")
        self.assertEqual((entry["category"], entry["action"]), ("creation", "Play"))
        folder = Path("projects/you-were-supposed-to-drop-it")
        self.assertEqual(entry["href"], (folder / "index.html").as_posix())

        links = PageLinks()
        links.feed((SOURCE / entry["href"]).read_text())
        required = {entry["href"], (folder / "gallery-preview.svg").as_posix()}
        for target in links.targets:
            url = urlsplit(target)
            if url.path and not url.scheme and not url.netloc:
                required.add((folder / url.path).as_posix())
        self.assertFalse(required.difference(entry["files"]))
