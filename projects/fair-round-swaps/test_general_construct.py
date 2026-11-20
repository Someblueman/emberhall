"""Real command boundaries and independent replay of supplied-instance paths."""

import copy
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from general_construct import read_instance

ROOT = Path(__file__).resolve().parent
EXAMPLE = json.loads((ROOT / "general_example.json").read_text())
ROUTE = [[1, 0, 0, 2], [0, 0, 1, 2], [2, 0, 1, 0]]


def command(data, saved=None, isolated=False):
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        source = ROOT / "general_construct.py"
        env = os.environ.copy()
        if isolated:
            for name in ("general_construct.py", "swaps.py"):
                (folder / name).write_bytes((ROOT / name).read_bytes())
            source = folder / source.name
            env.pop("PYTHONPATH", None)
        file = folder / "input.json"
        file.write_text(json.dumps(data), encoding="utf-8")
        args = [sys.executable, "-S", str(source), str(file)]
        if saved is not None:
            output = folder / "output.json"
            output.write_text(json.dumps(saved), encoding="utf-8")
            args += ["--verify", str(output)]
        return subprocess.run(args, capture_output=True, text=True, env=env, timeout=30)


class GeneralCommandTest(unittest.TestCase):
    def assert_literal_path(self, data, result):
        u, final, a, b = read_instance(data)
        states = result["owners"]
        for witness, state in ((a, states[0]), (b, states[-1])):
            self.assertEqual({g: i for i, g in witness}, dict(enumerate(state)))
        for state in states:
            bundles = [[g for g, owner in enumerate(state) if owner == i] for i in range(len(u))]
            self.assertEqual([len(bundle) for bundle in bundles], result["sizes"])
            for i, row in enumerate(u):
                own = sum(row[g] for g in bundles[i])
                for bundle in bundles:
                    self.assertTrue(not bundle or any(
                        own >= sum(row[g] for g in bundle if g != removed) for removed in bundle))
        self.assertEqual(len(states) - 1, result["swaps"])
        for before, after, trade in zip(states, states[1:], result["exchanges"]):
            changed = [g for g in range(len(before)) if before[g] != after[g]]
            self.assertEqual(changed, trade["goods"])
            self.assertEqual(len(changed), 2)
            x, y = changed
            self.assertEqual((before[x], before[y]), (after[y], after[x]))
            self.assertEqual(trade["agents"], [before[x], before[y]])

    def test_example_and_saved_replay(self):
        process = command(EXAMPLE)
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["owners"], ROUTE)
        self.assertEqual(result["swaps"], 2)
        self.assertNotIn("picking_witnesses", result)
        self.assert_literal_path(EXAMPLE, result)
        # Replaying requires only the exact model, not the general constructor.
        replay = command(EXAMPLE, result, isolated=True)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(json.loads(replay.stdout), result)

    def test_all_remainder_boundaries_and_arbitrary_labels(self):
        from arbitrary_few_final import braid_example

        for n, q, r in ((4, 0, 2), (4, 2, 0), (5, 2, 1), (4, 1, 3), (8, 2, 5)):
            with self.subTest(n=n, q=q, r=r):
                u, a, b, final = braid_example(n, q, r)
                labels = tuple(reversed(range(n)))
                data = {"utilities": [[str(Fraction(x, 7)) for x in u[labels.index(i)]] for i in range(n)],
                        "final_recipients": [labels[i] for i in final],
                        "start": [[labels[i], g] for i, g in a],
                        "target": [[labels[i], g] for i, g in b]}
                process = command(data)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assert_literal_path(data, json.loads(process.stdout))

    def test_replay_checks_owners_instead_of_trusting_metadata(self):
        saved = {"owners": ROUTE, "verified": False, "swaps": 999, "exchanges": []}
        process = command(EXAMPLE, saved, isolated=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["swaps"], 2)
        bad = [([], "nonempty"), ([ROUTE[-1], ROUTE[0]], "endpoints"),
               ([ROUTE[0], ROUTE[-1]], "single exchange"),
               ([ROUTE[0], ROUTE[0], *ROUTE[1:]], "single exchange"),
               ([ROUTE[0], [1, 1, 0, 2], ROUTE[-1]], "bundle sizes"),
               ([ROUTE[0], [1, 2, 0, 0], ROUTE[-1]], "not EF1"),
               ([ROUTE[0], [False, 0, 1, 2], ROUTE[-1]], "valid integer owner")]
        for owners, error in bad:
            with self.subTest(owners=owners):
                process = command(EXAMPLE, {"owners": owners}, isolated=True)
                self.assertEqual(process.returncode, 2)
                self.assertIn(error, process.stderr)
                self.assertEqual(process.stdout, "")
                self.assertNotIn("Traceback", process.stderr)

    def test_schema_and_greedy_input_failures(self):
        cases = [("final_recipients", [True]), ("final_recipients", [0, 0]),
                 ("final_recipients", [3]), ("start", [[0, 0], [1, 1], [2, 3], [0, 2]]),
                 ("start", EXAMPLE["start"][:-1]), ("target", [[False, 0]]),
                 ("utilities", [[1], [1, 2]])]
        for value in (True, 0.5, -1, "1/0", "NaN", "not a number"):
            rows = copy.deepcopy(EXAMPLE["utilities"])
            rows[0][0] = value
            cases.append(("utilities", rows))
        for key, value in cases:
            with self.subTest(key=key, value=value):
                data = copy.deepcopy(EXAMPLE)
                data[key] = value
                process = command(data)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertNotIn("Traceback", process.stderr)
        for data in ([], {}, {**EXAMPLE, "extra": 1}):
            with self.assertRaises(ValueError):
                read_instance(data)

    def test_missing_prerequisite_is_reported(self):
        process = command(EXAMPLE, isolated=True)
        self.assertEqual(process.returncode, 2)
        self.assertIn("missing constructor prerequisite arbitrary_few_final", process.stderr)
        self.assertNotIn("Traceback", process.stderr)


if __name__ == "__main__":
    unittest.main()
