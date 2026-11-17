"""Expose the shipped JavaScript checks to the house's existing unittest gate."""
from pathlib import Path
import shutil
import subprocess
import unittest

PROJECT = Path(__file__).resolve().parent


class CueRehearsalChecks(unittest.TestCase):
    def test_shipped_model(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is unavailable; shipped JavaScript checks not executed")
        result = subprocess.run(
            [node, "--test", str(PROJECT / "model.test.js")],
            capture_output=True, text=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_page_loads_shared_model_and_local_assets(self):
        html = (PROJECT / "index.html").read_text()
        self.assertLess(html.index('src="model.js"'), html.index('src="app.js"'))
        for asset in ("model.js", "app.js", "style.css", "README.md"):
            self.assertTrue((PROJECT / asset).is_file(), asset)
        app = (PROJECT / "app.js").read_text()
        self.assertIn("globalThis.CueRehearsal", app)
        self.assertIn("model.compare(project)", app)
        self.assertIn("model.timelineData(project)", app)
        self.assertIn("model.parseJSON($('json').value)", app)
        self.assertIn("label.htmlFor = input.id", app)
        self.assertNotIn("innerHTML", app)
        self.assertIn('id="timeline"', html)
        self.assertIn('id="undo"', html)

    def test_gallery_preview_matches_generator(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is unavailable; gallery preview generator not executed")
        preview = PROJECT / "gallery-preview.svg"
        generator = PROJECT / "make-gallery-preview.js"
        self.assertTrue(preview.is_file(), "gallery-preview.svg missing")
        self.assertTrue(generator.is_file(), "make-gallery-preview.js missing")
        result = subprocess.run(
            [node, str(generator)],
            capture_output=True, timeout=30, check=True,
        )
        self.assertEqual(preview.read_bytes(), result.stdout)


if __name__ == "__main__":
    unittest.main()
