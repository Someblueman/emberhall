"""Acceptance tests for Night Ferry player, live reach model, and Gallery preview."""

from pathlib import Path
import re
import shutil
import subprocess
import unittest

PROJECT_DIR = Path(__file__).resolve().parent


@unittest.skipUnless(shutil.which("node"), "Node is required for Night Ferry tests")
class NightFerryProjectTests(unittest.TestCase):
    def test_node_unit_tests_and_syntax(self):
        for rel in (
            "player/reach-model.js",
            "player/player.js",
            "player/player.test.js",
            "make-gallery-preview.js",
        ):
            check = subprocess.run(
                ["node", "--check", str(PROJECT_DIR / rel)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(check.returncode, 0, f"{rel}: {check.stdout}{check.stderr}")

        run = subprocess.run(
            ["node", "--test", str(PROJECT_DIR / "player/player.test.js")],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_gallery_preview_matches_generator_bytes(self):
        result = subprocess.run(
            ["node", str(PROJECT_DIR / "make-gallery-preview.js")],
            capture_output=True,
            timeout=15,
            check=True,
        )
        preview = PROJECT_DIR / "gallery-preview.svg"
        self.assertTrue(preview.is_file(), "gallery-preview.svg is missing")
        self.assertEqual(preview.read_bytes(), result.stdout)

    def test_player_html_has_no_external_urls(self):
        html = (PROJECT_DIR / "player/index.html").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?:https?:)?//", html, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
