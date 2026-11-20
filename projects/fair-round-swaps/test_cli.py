"""Input and real command-line boundaries for the path constructor."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from construct import read_instance

ROOT = Path(__file__).resolve().parent
EXAMPLE = json.loads((ROOT / "example.json").read_text())


class CommandTest(unittest.TestCase):
    def test_actual_command(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "construct.py"), str(ROOT / "example.json")],
            capture_output=True, text=True, check=True,
        )
        result = json.loads(result.stdout)
        self.assertEqual(result["swaps"], 3)
        self.assertEqual(result["owners"][0], [0, 1, 1, 0, 0])
        self.assertEqual(result["owners"][-1], [1, 0, 0, 1, 0])

    def test_rational_and_malformed_inputs(self):
        data = copy.deepcopy(EXAMPLE)
        data["utilities"][0][0] = "9/1"
        read_instance(data)
        for value in (True, 0.5, -1, "1/0", "not a number"):
            with self.subTest(value=value):
                data = copy.deepcopy(EXAMPLE)
                data["utilities"][0][0] = value
                with self.assertRaises((ValueError, ZeroDivisionError)):
                    read_instance(data)
        for key, value in (("final_agent", True), ("start", [[False, 0]]),
                           ("utilities", [[1], [1, 2]])):
            data = copy.deepcopy(EXAMPLE)
            data[key] = value
            with self.assertRaises(ValueError):
                read_instance(data)

    def test_nonmaximizing_input_exits_nonzero(self):
        data = copy.deepcopy(EXAMPLE)
        data["start"][0] = [0, 4]
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "bad.json"
            file.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(ROOT / "construct.py"), str(file)],
                                    capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a utility maximizer", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
