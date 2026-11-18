"""Exercise the shipped inheritance model with Node, without another dependency."""
from pathlib import Path
import subprocess
import unittest


class DanceTests(unittest.TestCase):
    def test_inherited_performances(self):
        result = subprocess.run(
            ["node", "--test", str(Path(__file__).with_name("dance.test.js"))],
            capture_output=True, text=True, timeout=15, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
