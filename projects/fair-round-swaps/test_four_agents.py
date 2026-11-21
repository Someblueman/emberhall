"""Real command boundary and the distinction between greedy and arbitrary EF1."""

from itertools import permutations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from four_agents import construct, example
from swaps import picking_outcomes, rounds_for


def fair(u, a):
    bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(4)]
    return all(any(sum(u[i][g] for g in bundles[i]) >=
                       sum(u[i][g] for g in bundles[j] if g != removed)
                       for removed in bundles[j])
               for i in range(4) for j in range(4) if i != j)


def adjacent(a, b):
    changed = [g for g in range(len(a)) if a[g] != b[g]]
    return (len(changed) == 2 and a[changed[0]] == b[changed[1]]
            and a[changed[1]] == b[changed[0]])


class FourAgentCommandTests(unittest.TestCase):
    def test_real_command_all_three_remainders_and_nonstandard_recipients(self):
        command = str(Path(__file__).with_name('four_agents.py'))
        for remainder in (1, 2, 3):
            result = subprocess.run([sys.executable, command, '--example', str(remainder)],
                                    capture_output=True, text=True, check=True)
            out = json.loads(result.stdout)
            data = example(remainder)
            states = [tuple(a) for a in out['owners']]
            self.assertEqual(out['swaps'], len(states) - 1)
            self.assertEqual(out['sizes'], [1 + (i in data['final_recipients']) for i in range(4)])
            self.assertTrue(all(fair(data['utilities'], a) for a in states))
            self.assertTrue(all(adjacent(a, b) for a, b in zip(states, states[1:])))

    def test_rational_input_file_and_rejected_boundaries(self):
        command = str(Path(__file__).with_name('four_agents.py'))
        data = example(2)
        data['utilities'] = [[f'{v}/7' for v in row] for row in data['utilities']]
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'instance.json'
            file.write_text(json.dumps(data))
            success = subprocess.run([sys.executable, command, '--input', str(file)],
                                     capture_output=True, text=True)
            self.assertEqual(success.returncode, 0, success.stderr)
            bad = example(2)
            bad['utilities'][0][0] = 1.5
            file.write_text(json.dumps(bad))
            failure = subprocess.run([sys.executable, command, '--input', str(file)],
                                     capture_output=True, text=True)
            self.assertEqual(failure.returncode, 2)
            self.assertIn('exact integers', failure.stderr)
        for field, value in [('final_recipients', [True, 3]), ('final_recipients', [1, 1]),
                             ('start', [[7, 0]]), ('start', [[0, 5]])]:
            bad = example(2)
            bad[field] = value
            with self.assertRaises(ValueError):
                construct(bad)

    def test_full_ef1_graph_really_can_be_disconnected(self):
        u = ((0, 8, 10, 6, 2, 3), (0, 1, 6, 2, 0, 4),
             (4, 0, 3, 4, 2, 1), (3, 1, 4, 2, 0, 4))
        isolated = (3, 1, 1, 0, 2, 0)
        states = set(permutations((0, 0, 1, 1, 2, 3)))
        allowed = {a for a in states if fair(u, a)}
        self.assertEqual(len(allowed), 35)
        self.assertIn(isolated, allowed)
        self.assertFalse(any(adjacent(isolated, a) for a in allowed))
        todo, sizes = set(allowed), []
        while todo:
            reached = {todo.pop()}
            while True:
                new = {b for b in todo if any(adjacent(a, b) for a in reached)}
                if not new:
                    break
                todo -= new
                reached |= new
            sizes.append(len(reached))
        self.assertEqual(sorted(sizes), [1, 34])
        greedy = picking_outcomes(u, rounds_for(4, 6, (0, 1)))
        self.assertEqual(len(greedy), 16)
        self.assertNotIn(isolated, greedy)


if __name__ == '__main__':
    unittest.main()
