"""The small-triples census is exact, and the document's table is the command's table.

The document SMALL_TRIPLES.md quotes the census.  These tests read that
document and compare it with what the command computes, so the numbers in the
document are checked by the house's own suite rather than trusted.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import small_triples


def document_table(limit: int) -> list[str]:
    """The census lines quoted in SMALL_TRIPLES.md."""
    text = (HERE / "SMALL_TRIPLES.md").read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        match = re.fullmatch(r"(\d+) (\d+) (\d+) (\d+) (\d+) (yes|no)", line.strip())
        if match:
            rows.append(" ".join(match.groups()))
    return rows


class SmallTriplesTest(unittest.TestCase):
    def test_the_document_table_is_the_computed_table(self):
        computed = small_triples.table(12).splitlines()
        self.assertEqual(document_table(12), computed[:-1])
        self.assertTrue(computed[-1].startswith("TOTAL "))
        self.assertTrue(computed[-1].endswith(" attained 53"))

    def test_a_broken_search_would_be_caught(self):
        """The census is not the target: for (2,1,1) the truth is above it."""
        self.assertEqual(small_triples.optimum(2, 1, 1), 2)
        self.assertEqual(small_triples.target(2, 1, 1), 1)
        self.assertEqual(small_triples.optimum(1, 1, 1), 1)
        self.assertEqual(small_triples.optimum(3, 3, 3), 4)
        self.assertEqual(small_triples.optimum(2, 2, 2), 3)

    def test_distances_agree_with_the_projects_rule(self):
        """Same arm: the difference of depths; different arms: the sum."""
        self.assertEqual(small_triples.distance(2, 4, 5, 4), 2)   # arm 1, depths 2 and 4
        self.assertEqual(small_triples.distance(3, 7, 5, 4), 3 + 2)  # arm 1 and arm 2
        self.assertEqual(small_triples.distance(0, 4, 5, 4), 4)   # the centre
        self.assertEqual(small_triples.arm_of(7, 5, 4), 2)
        self.assertEqual(small_triples.depth_of(7, 5, 4), 2)

    def test_the_command_prints_the_table(self):
        result = subprocess.run([sys.executable, str(HERE / "small_triples.py"), "--limit", "12"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 54)
        self.assertTrue(lines[0].startswith("1 1 1 "))
        self.assertEqual(lines[-1], "TOTAL 53 attained 53")


if __name__ == "__main__":
    unittest.main()
