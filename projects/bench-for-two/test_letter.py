"""Run the shipped model's exhaustive readings through the house project gate."""
from pathlib import Path
import subprocess
import unittest


class LetterTests(unittest.TestCase):
    def test_all_offered_readings(self):
        result = subprocess.run(
            ["node", "--test", str(Path(__file__).with_name("letter.test.js"))],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
