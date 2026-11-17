"""The Gallery picture is a reproducible excerpt of the packet it opens."""
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/review-skein"
SPEC = importlib.util.spec_from_file_location("skein_preview", PROJECT / "make-gallery-preview.py")
preview = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


class SkeinGalleryPreviewTests(unittest.TestCase):
    def test_picture_matches_generator_and_linked_sample(self):
        entry = next(p for p in json.loads((ROOT / "site/projects.json").read_text())["projects"]
                     if p["id"] == "review-skein")
        self.assertEqual(entry["href"], preview.SAMPLE.relative_to(ROOT).as_posix())
        self.assertIn("projects/review-skein/gallery-preview.svg", entry["files"])
        source = preview.SAMPLE.read_text()
        generated = preview.svg(source)
        self.assertEqual((PROJECT / "gallery-preview.svg").read_bytes(), generated.encode())
        text = " ".join(ET.fromstring(generated).itertext())
        for value in ["The board says: ferry at nine.", "The board says: ferry at ten.",
                      "Invented open question: confirm the departure change from nine to ten."]:
            self.assertIn(value, source)
            self.assertIn(value, text)
        self.assertIn("INVENTED SAMPLE", text)

    def test_source_changes_flow_into_picture_and_stay_text(self):
        source = preview.SAMPLE.read_text().replace("The board says: ferry at ten.",
                                                   "Boat &lt;later&gt; &amp; safer.")
        generated = preview.svg(source)
        root = ET.fromstring(generated)
        self.assertIn("Boat <later> & safer.", " ".join(root.itertext()))
        self.assertNotIn("The board says: ferry at ten.", generated)
        self.assertFalse(root.findall(".//{http://www.w3.org/2000/svg}later"))
        with self.assertRaisesRegex(ValueError, "expected changed row"):
            preview.svg("<html><p>Sample removed</p></html>")
