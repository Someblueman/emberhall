"""Checks for the You Were Supposed to Drop It cut-paper stage."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent


class StageBundleTests(unittest.TestCase):
    def test_no_external_urls_in_runtime_files(self) -> None:
        for name in ("index.html", "stage.css", "stage-rig.js", "show.js"):
            text = (ROOT / name).read_text(encoding="utf-8").replace("http://www.w3.org/2000/svg", "")
            self.assertNotIn("http://", text, f"unexpected http:// in {name}")
            self.assertNotIn("https://", text, f"unexpected https:// in {name}")

    def test_html_assets_and_stage_ids_exist(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for asset in ("stage.css", "stage-rig.js", "show.js"):
            self.assertIn(asset, html)
            self.assertTrue((ROOT / asset).is_file())
        for rig in ("rook", "shrikhande"):
            for prefix in ("card", "role", "status", "caption", "marks-layer", "wire-layer", "puppets-layer", "drummer-layer", "hat-layer", "buttons"):
                self.assertIn(f'id="{prefix}-{rig}"', html)
        self.assertIn('id="curtain-notes"', html)
        self.assertNotIn("<details open", html)

    def test_js_syntax_and_node_unit_tests(self) -> None:
        for script in ("stage-rig.js", "show.js"):
            res = subprocess.run(["node", "--check", str(ROOT / script)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
        res = subprocess.run(["node", "--test", str(ROOT / "stage-rig.test.js")], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(len(re.findall(r"^✔ ", res.stdout, re.MULTILINE)), 9)


if __name__ == "__main__":
    unittest.main()
