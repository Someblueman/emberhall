"""A return keeps its identity while repairing only a name that needs it."""
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from house import home
from tests import test_resident_returns as fixtures


class NamePromptTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ReturnProjectionTests()
        self.fixture.setUp()
        self.fixture.start("return")
        self.state = self.fixture.h.state
        self.state["maintenance"]["resident_names"] = True
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.coordinator = home.Coordinator.__new__(home.Coordinator)
        self.coordinator.private = Path(self.temp.name)
        self.coordinator.record = SimpleNamespace(read=lambda: (self.state, [], "fixture"))

    def prompt(self):
        with patch("house.home.active_prompt", return_value="Fixture council text"):
            return self.coordinator.prompt(self.state, "return", "fern", Path(self.temp.name), Path("/fixture/client"), None)

    def test_technical_or_duplicate_name_gets_self_rename_after_wake(self):
        for name in ("Hydrogen", "Emberkeeper-23", "bob"):
            self.state["residents"]["fern"]["name"] = name
            text = self.prompt()
            self.assertIn("do not call arrive", text)
            self.assertIn("After wake, use rename --as fern", text)
            self.assertIn("--request return-name", text)
            self.assertIn('"cursor"', text)
            self.assertIn("never a new identity", text)

    def test_distinct_name_stays_and_old_runtime_contract_has_no_rename(self):
        text = self.prompt()
        self.assertIn("keep it when returning", text)
        self.assertNotIn("rename --as", text)
        self.state["maintenance"]["resident_names"] = False
        self.state["residents"]["fern"]["name"] = "Hydrogen"
        text = self.prompt()
        self.assertNotIn("rename --as", text)
        self.assertIn("Preserve your existing name", text)


if __name__ == "__main__":
    unittest.main()
