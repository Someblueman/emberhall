"""Regression test for full-width column stretch when a room is opened."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOUSE_CSS = ROOT / "site" / "house.css"


class OpenRoomStretchTests(unittest.TestCase):
    def test_open_room_column_flex_resets_grid_align_items_start(self) -> None:
        css = HOUSE_CSS.read_text(encoding="utf-8")

        base_match = re.search(r"\.house-layout\s*\{([^}]*)\}", css)
        self.assertIsNotNone(base_match)
        self.assertIn("align-items:start", base_match.group(1))

        flex_rules = [
            match.group(1)
            for match in re.finditer(
                r"\.house-layout\.room-open(?::has\([^)]*\))?\s*\{([^}]*)\}", css
            )
            if "flex-direction:column" in match.group(1)
        ]
        self.assertEqual(len(flex_rules), 2)
        for body in flex_rules:
            self.assertIn("align-items:stretch", body)


if __name__ == "__main__":
    unittest.main()
