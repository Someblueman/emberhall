"""Definition-level checks of the terminal early-turn sector."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from delayed_escape import adjacent, first_internal, nest
from reconstruction import legal
from terminal_turns import completion_records, open_frontiers, recover, terminal_prefix, verify
from weighted_open import exterior


def children(prefix, word):
    n = len(prefix)
    for gap in range(n + 1):
        child = prefix[:gap] + (n,) + prefix[gap:]
        if legal(child, word):
            yield child


class TerminalTurnsTests(unittest.TestCase):
    def test_the_sole_stopped_prefix(self):
        for k in range(3, 14):
            for turn in range(2, min(k, 4) + 1):
                mountain = nest(exterior(turn - 1), k - turn + 1, "M")
                self.assertEqual(first_internal(mountain), turn)
                frontier = {mountain}
                for j in range(1, k):
                    frontier = {
                        c for p in frontier for c in children(p, "M" * k + "V" * j)
                        if j == 1 or c != adjacent(p, "V")
                    }
                stopped = {adjacent(p, "V") for p in frontier}
                self.assertEqual(stopped, {terminal_prefix(k, turn)[0]})

    def test_every_intermediate_gap(self):
        for k in range(3, 16):
            for turn in range(2, min(k, 4) + 1):
                previous = {terminal_prefix(k, turn)[0]}
                for j, frontier in enumerate(open_frontiers(k, turn), 1):
                    direct = {
                        c for p in previous
                        for c in children(p, "M" * k + "V" * k + "M" * j)
                        if j == 1 or c != adjacent(p, "M")
                    }
                    self.assertEqual(set(frontier.values()), direct, (k, turn, j))
                    self.assertEqual(len(frontier), len(direct))
                    previous = direct

    def test_complete_sets_and_inverse(self):
        for k in range(3, 18):
            for turn in range(2, min(k, 4) + 1):
                self.assertEqual(verify(k, turn), 4 * k - turn - 4)

    def test_large_constructed_parameters(self):
        for turn in (2, 3, 4):
            records = list(completion_records(50, turn))
            self.assertEqual(len(records), 4 * 50 - turn - 4)
            for parameter, order in records:
                self.assertEqual(recover(order, 50, turn), parameter)

    def test_small_collision_vectors(self):
        expected = {(3, 2): [2, 2, 2], (3, 3): [2, 1, 2],
                    (4, 2): [2, 3, 2, 3], (4, 3): [2, 2, 2, 3],
                    (4, 4): [2, 2, 1, 3]}
        for (k, turn), sizes in expected.items():
            self.assertEqual([len(f) for f in open_frontiers(k, turn)], sizes)

    def test_input_and_wrong_prefix(self):
        for args in ((2, 2), (3, 4), (7, 1), (7, 5)):
            with self.assertRaises(ValueError):
                terminal_prefix(*args)
        order = next(completion_records(8, 2))[1]
        with self.assertRaises(ValueError):
            recover(order, 8, 3)
        with self.assertRaises(ValueError):
            recover(order[::-1], 8, 2)

    def test_cli(self):
        script = str(Path(__file__).with_name("terminal_turns.py"))
        result = subprocess.run([sys.executable, script, "--verify"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for turn, count in ((2, 26), (3, 25), (4, 24)):
            self.assertIn(f"turn {turn}: {count} stacks; theorem {count}", result.stdout)
        bad = subprocess.run([sys.executable, script, "--k", "2"], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
