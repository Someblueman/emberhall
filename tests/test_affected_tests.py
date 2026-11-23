import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("affected_tests", ROOT / "scripts" / "affected_tests.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SYNTHETIC = {
    "house/__init__.py": "",
    "house/leaf.py": "VALUE = 1\n",
    "house/mid.py": "from . import leaf\n",
    "house/unused.py": "VALUE = 2\n",
    "house/reader.py": "DATA = 'data/names.txt'\n",
    "tests/__init__.py": "",
    "tests/support.py": "HELPER = 1\n",
    "tests/test_direct.py": "from house import leaf\nimport unittest\n",
    "tests/test_transitive.py": "from house.mid import leaf\nimport unittest\n",
    "tests/test_reader.py": "from house import reader\nimport unittest\n",
    "tests/test_chained.py": "from tests import test_transitive\nimport unittest\n",
    "tests/test_other.py": "import unittest\n",
    "scripts/tool.py": "def run():\n    return 'pages/guide'\n",
    "tests/test_tool.py": "import tool\nimport unittest\n",
}


class SelectionRules(unittest.TestCase):
    def setUp(self):
        self.graph = MODULE.Graph(dict(SYNTHETIC))

    def picked(self, changed):
        return MODULE.select(self.graph, changed)

    def test_direct_importer_is_selected(self):
        result = self.picked([("house/leaf.py", "M")])
        self.assertFalse(result["full"])
        self.assertIn("tests.test_direct", result["tests"])

    def test_transitive_importer_is_selected(self):
        result = self.picked([("house/leaf.py", "M")])
        self.assertIn("tests.test_transitive", result["tests"])
        self.assertNotIn("tests.test_other", result["tests"])

    def test_importer_through_another_test_is_selected(self):
        result = self.picked([("house/leaf.py", "M")])
        self.assertIn("tests.test_chained", result["tests"])

    def test_changed_test_runs_itself(self):
        result = self.picked([("tests/test_other.py", "M")])
        self.assertEqual(["tests.test_other"], result["tests"])
        self.assertFalse(result["full"])

    def test_unimported_house_module_falls_back_to_full(self):
        self.assertTrue(self.picked([("house/unused.py", "M")])["full"])

    def test_shared_support_falls_back_to_full(self):
        self.assertTrue(self.picked([("tests/support.py", "M")])["full"])

    def test_deleted_house_module_falls_back_to_full(self):
        self.assertTrue(self.picked([("house/leaf.py", "D")])["full"])

    def test_deleted_test_maps_to_nothing_without_full(self):
        result = self.picked([("tests/test_direct.py", "D")])
        self.assertFalse(result["full"])
        self.assertEqual([], result["tests"])

    def test_unknown_path_falls_back_to_full(self):
        self.assertTrue(self.picked([("mystery/blob.bin", "A")])["full"])

    def test_data_file_referenced_by_module_is_mapped(self):
        result = self.picked([("data/names.txt", "M")])
        self.assertFalse(result["full"])
        self.assertEqual(["tests.test_reader"], result["tests"])

    def test_one_unmapped_path_forces_full_even_with_mapped_ones(self):
        result = self.picked([("house/leaf.py", "M"), ("mystery/blob.bin", "A")])
        self.assertTrue(result["full"])
        self.assertIn("tests.test_direct", result["tests"])

    def test_script_imported_by_bare_stem_is_mapped(self):
        result = self.picked([("scripts/tool.py", "M")])
        self.assertFalse(result["full"], result["full_reasons"])
        self.assertEqual(["tests.test_tool"], result["tests"])

    def test_file_under_a_named_directory_is_mapped(self):
        result = self.picked([("pages/guide/intro.md", "A")])
        self.assertFalse(result["full"], result["full_reasons"])
        self.assertEqual(["tests.test_tool"], result["tests"])

    def test_no_changes_selects_nothing(self):
        result = self.picked([])
        self.assertFalse(result["full"])
        self.assertEqual([], result["tests"])


class RealRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = MODULE.Graph(MODULE.worktree_sources())

    def test_graph_sees_the_suite(self):
        self.assertGreater(len(self.graph.test_imports), 100)
        self.assertGreater(len(self.graph.house_modules), 30)

    def test_one_module_change_is_a_proper_nonempty_subset(self):
        result = MODULE.select(self.graph, [("house/digest.py", "M")])
        self.assertFalse(result["full"], result["full_reasons"])
        self.assertIn("tests.test_digest_command", result["tests"])
        self.assertLess(len(result["tests"]), len(self.graph.test_imports))

    def test_this_script_is_mapped_to_this_test(self):
        result = MODULE.select(self.graph, [("scripts/affected_tests.py", "M")])
        self.assertFalse(result["full"], result["full_reasons"])
        self.assertIn("tests.test_affected_tests", result["tests"])


if __name__ == "__main__":
    unittest.main()
