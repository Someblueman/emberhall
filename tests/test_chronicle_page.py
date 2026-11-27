"""Publishing must retain the reviewed standalone Chronicle spacing repair."""
from pathlib import Path
import re
from types import SimpleNamespace
import unittest

from house import chronicle_page, publish


class ChronicleSpacingTests(unittest.TestCase):
    def test_generated_and_published_controls_retain_static_repair(self):
        root = Path(__file__).resolve().parents[1]
        static = (root / "site/chronicle/index.html").read_text()
        record = SimpleNamespace(read=lambda: ({"house_id": "fixture"}, [], "head"))
        pages = [chronicle_page.render_html([]),
                 publish.chronicle_body(record, {}).decode()]
        selectors = ("header a, .site-footer a", ".browse-options label",
                     ".earlier-control", "summary", ".links a")

        def declarations(page, selector):
            css = re.search(r"<style>(.*?)</style>", page, re.S)[1]
            block = re.search(r"(?:^|\n)\s*" + re.escape(selector)
                              + r"\s*\{([^{}]*)\}", css)[1]
            return dict(item.strip().split(":", 1)
                        for item in block.split(";") if item.strip())

        for page in pages:
            for selector in selectors:
                with self.subTest(selector=selector, published=page is pages[1]):
                    actual = declarations(page, selector)
                    self.assertEqual(actual, declarations(static, selector))
                    self.assertEqual(actual["min-height"].strip(), "44px")
            # Leave summaries as native list items, preserving disclosure markers.
            self.assertNotIn("display", declarations(page, "summary"))


if __name__ == "__main__":
    unittest.main()
