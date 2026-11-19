"""Exercise the time and completion contracts through the standalone Rust solver."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).with_name("search.rs")


@unittest.skipUnless(shutil.which("rustc"), "solver checks require rustc")
class SearchLimitsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = tempfile.TemporaryDirectory()
        cls.addClassCleanup(scratch.cleanup)
        cls.room = Path(scratch.name)
        cls.solver = cls.room / "search"
        subprocess.run(["rustc", "-O", SOURCE, "-o", cls.solver], check=True)

    def test_zero_budget_preserves_existing_output(self):
        output = self.room / "existing.txt"
        output.write_text("previous result\n")
        result = subprocess.run(
            [self.solver, "--budget-secs", "0", "--out", output],
            capture_output=True, text=True, timeout=3, check=True,
        )
        self.assertIn("no codebook written", result.stdout)
        self.assertNotIn("exact a(", result.stdout)
        self.assertEqual(output.read_text(), "previous result\n")

    def test_short_budget_interrupts_calibration(self):
        result = subprocess.run(
            [self.solver, "--budget-secs", "0.1", "--max-exact-n", "10",
             "--out", self.room / "short.txt"],
            capture_output=True, text=True, timeout=3, check=True,
        )
        self.assertIn("no codebook written", result.stdout)
        self.assertNotIn("exact a(10)", result.stdout)
        self.assertFalse((self.room / "short.txt").exists())

    def test_node_cap_reports_an_incumbent(self):
        test_binary = self.room / "solver-tests"
        subprocess.run(["rustc", "--test", "-O", SOURCE, "-o", test_binary], check=True)
        result = subprocess.run(
            [test_binary, "--nocapture"], capture_output=True, text=True, check=True,
        )
        self.assertIn("n=3: incomplete, incumbent", result.stdout)
        self.assertIn("exact a(3)", result.stdout)

    def test_later_phases_get_no_minimum_time_extension(self):
        output = self.room / "diagnostic.txt"
        result = subprocess.run(
            [self.solver, "--max-exact-n", "3", "--budget-secs", "0.1", "--out", output],
            capture_output=True, text=True, timeout=3, check=True,
        )
        self.assertIn("exact a(3)", result.stdout)
        if output.exists():
            self.assertIn("Regime C (unrestricted starts", result.stdout)
            self.assertIn("FINAL:", result.stdout)
        else:
            self.assertIn("no codebook written", result.stdout)
