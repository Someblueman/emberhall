"""A plain line that is ready to send says so; anything else lists why not."""
import subprocess
import sys
from pathlib import Path
import unittest

from scripts.plain_check import problems

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plain_check.py"
GOOD = "A helper tells you whether a task line is ready to send."


class PlainCheckTests(unittest.TestCase):
    def test_good_line_is_ready(self):
        self.assertEqual(problems(GOOD), [])

    def test_short_and_long_lines_fail(self):
        self.assertTrue(problems("Too short."))
        self.assertTrue(problems("x " * 150 + "."))
        self.assertIn("outside 30 to 200", problems("Too short.")[0])

    def test_two_sentences_fail(self):
        issues = problems("A good line is checked. It saves a round trip.")
        self.assertIn("one sentence", issues[0])

    def test_file_name_and_code_span_fail(self):
        issues = problems("Please check scripts/plain_check.py `main` first.")
        self.assertTrue(any("file name" in i for i in issues))
        self.assertTrue(any("code spans" in i for i in issues))

    def test_record_number_and_capitals_fail(self):
        issues = problems("The task wren-1 seq 35097 covers the JSON guide.")
        self.assertTrue(any("record numbers" in i for i in issues))
        issues = problems("The CLI guide covers the JSON shapes today.")
        self.assertTrue(any("capitals" in i for i in issues))

    def test_cli_exit_codes(self):
        ok = subprocess.run([sys.executable, str(SCRIPT), GOOD],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self.assertIn("ready", ok.stdout)
        bad = subprocess.run([sys.executable, str(SCRIPT), "Too short."],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("not ready", bad.stdout)
        empty = subprocess.run([sys.executable, str(SCRIPT)],
                               input="  ", capture_output=True, text=True)
        self.assertEqual(empty.returncode, 2)


if __name__ == "__main__":
    unittest.main()
