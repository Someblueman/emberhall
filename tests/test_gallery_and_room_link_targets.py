"""Regression tests for R53: 44px touch targets on .gallery-invitation and .room-shelf-link."""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


def rule_declarations(css: str, selector: str) -> dict[str, str]:
    pattern = re.compile(r"(?:^|[}\n])\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", re.S)
    matches = pattern.findall(css)
    if not matches:
        return {}
    decls: dict[str, str] = {}
    for body in matches:
        for raw in body.split(";"):
            if ":" in raw:
                prop, val = raw.split(":", 1)
                decls[prop.strip()] = " ".join(val.split())
    return decls


def px_value(raw: str | None) -> float:
    if not raw:
        return 0.0
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)px$", raw.strip())
    return float(m.group(1)) if m else 0.0


class GalleryAndRoomLinkTargetTests(unittest.TestCase):
    def test_gallery_invitation_has_44px_minimum_height_and_centered_flex_box(self):
        css = (ROOT / "site/house.css").read_text(encoding="utf-8")
        decls = rule_declarations(css, ".gallery-invitation")
        self.assertEqual(decls.get("display"), "inline-flex")
        self.assertEqual(decls.get("align-items"), "center")
        self.assertGreaterEqual(px_value(decls.get("min-height")), 44.0)
        self.assertEqual(decls.get("color"), "var(--gold)")
        self.assertEqual(decls.get("border-bottom"), "1px solid var(--gold)")
        self.assertIn("padding", decls)

    def test_gallery_invitation_stays_hidden_when_composed_room_is_open(self):
        css = (ROOT / "site/house.css").read_text(encoding="utf-8")
        self.assertRegex(
            css,
            r"\.house-layout\.room-open:has\(\.composed-room\)\s+\.house-pane\s*>\s*:is\([^)]*\.gallery-invitation[^)]*\)[^{]*\{\s*display:\s*none\s*;\s*\}",
        )

    def test_room_shelf_link_has_44px_minimum_height_and_preserves_context_overrides(self):
        css = (ROOT / "site/house.css").read_text(encoding="utf-8")
        decls = rule_declarations(css, ".room-shelf-link")
        self.assertEqual(decls.get("display"), "inline-flex")
        self.assertEqual(decls.get("align-items"), "center")
        self.assertGreaterEqual(px_value(decls.get("min-height")), 44.0)
        self.assertEqual(decls.get("color"), "var(--gold)")
        self.assertEqual(decls.get("font-size"), "13px")
        self.assertEqual(decls.get("text-decoration"), "underline")
        self.assertEqual(decls.get("text-underline-offset"), "3px")
        self.assertIn("padding", decls)

        actions_decls = rule_declarations(css, ".shelf-project-actions .room-shelf-link")
        self.assertEqual(actions_decls.get("margin-top"), "0")

        gallery_decls = rule_declarations(css, ".composed-gallery > .room-shelf-link")
        self.assertEqual(gallery_decls.get("color"), "#ede0ba")

    def test_front_page_markup_contains_gallery_invitation_anchor(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        self.assertIn('<a class="gallery-invitation" href="#gallery-view">Explore what we’ve made →</a>', html)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
    def test_room_renderers_emit_room_shelf_links_with_navigation_destinations(self):
        source = ROOT / "site/house.js"
        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
const code = fs.readFileSync(process.argv[1], "utf8");
assert.match(code, /html\("a","room-shelf-link","Open Household Accounts →",panel\)/);
assert.match(code, /html\("a","room-shelf-link","Follow house work in the Workshop",section\)/);
assert.match(code, /html\("a","room-shelf-link","View the public shelf",summary\)/);
assert.match(code, /html\("a","room-shelf-link","Read the Chronicle →",content\)/);
assert.match(code, /html\("a","room-shelf-link","Explore all creations in the Gallery →",panel\)/);
assert.match(code, /html\("a",\s*"room-shelf-link",\s*"Read voting history and rule notices →",\s*panel\)/);
'''
        res = subprocess.run(["node", "-e", script, str(source)], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
