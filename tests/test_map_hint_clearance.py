"""Ensure the stage hint caption never uses negative top margin to overlap the house SVG."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MapHintClearanceTests(unittest.TestCase):
    def test_map_hint_has_non_negative_top_margin(self):
        css = (ROOT / "site/house.css").read_text(encoding="utf-8")
        blocks = re.findall(r"([^{}]*\.map-hint[^{}]*)\{([^}]*)\}", css)
        self.assertTrue(blocks, "Expected .map-hint rules in site/house.css")
        for selector, body in blocks:
            for decl in re.finditer(r"margin(?:-top)?\s*:\s*([^;]+)", body):
                first_token = decl.group(1).strip().split()[0]
                self.assertFalse(
                    first_token.startswith("-"),
                    f"Negative top margin {first_token!r} in {selector.strip()!r} overlaps the SVG stage",
                )

    def test_map_hint_precedes_room_nav_below_svg_in_stage(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        svg_end = html.index("</svg>")
        hint_pos = html.index('class="map-hint"')
        nav_pos = html.index('id="room-nav"')
        self.assertLess(svg_end, hint_pos)
        self.assertLess(hint_pos, nav_pos)


if __name__ == "__main__":
    unittest.main()
