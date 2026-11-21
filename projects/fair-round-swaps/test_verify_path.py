"""Standalone certificate boundaries, including nongreedy intermediate states."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from verify_path import verify


EXAMPLE = {
    "utilities": [[0, 100, 0, 0], [30, 0, 11, 10], [30, 0, 10, 11]],
    "final_recipients": [0],
    "start": [[1, 0], [0, 1], [2, 3], [0, 2]],
    "target": [[2, 0], [0, 1], [1, 2], [0, 3]],
}
ROUTE = [[1, 0, 0, 2], [0, 0, 1, 2], [2, 0, 1, 0]]
TRADES = [{"goods": [0, 2], "agents": [1, 0]}, {"goods": [0, 3], "agents": [0, 2]}]


def command(instance, path=None):
    """Copy only the checker and run with isolated stdlib imports."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        script = root / "verify_path.py"
        shutil.copyfile(Path(__file__).with_name("verify_path.py"), script)
        first = root / "input.json"
        first.write_text(instance if isinstance(instance, str) else json.dumps(instance), encoding="utf-8")
        args = [sys.executable, "-I", "-S", str(script), str(first)]
        if path is not None:
            second = root / "path.json"
            second.write_text(path if isinstance(path, str) else json.dumps(path), encoding="utf-8")
            args.append(str(second))
        return subprocess.run(args, capture_output=True, text=True, timeout=10)


class PathCertificateTests(unittest.TestCase):
    def test_nongreedy_intermediate_and_explicit_trade_orientation(self):
        # In the middle, agent 0 owns good 0. They must pick good 1 first;
        # both singleton agents would take good 0 before agent 0's final turn.
        # Thus this valid intermediate has no balanced greedy witness.
        result = verify(EXAMPLE, {"owners": ROUTE, "exchanges": TRADES})
        self.assertTrue(result["valid"])
        self.assertEqual((result["swaps"], result["sizes"]), (2, [2, 1, 1]))
        reverse = [{k: list(reversed(v)) for k, v in trade.items()} for trade in TRADES]
        self.assertEqual(verify(EXAMPLE, {"owners": ROUTE, "exchanges": reverse}), result)

    def test_rational_scaling_zeros_ties_and_unchanged_endpoints(self):
        data = copy.deepcopy(EXAMPLE)
        denominator = 10**120 + 37
        data["utilities"] = [[f"{v}/{denominator}" for v in row] for row in data["utilities"]]
        self.assertEqual(verify(data, {"owners": ROUTE})["swaps"], 2)
        data["target"] = data["start"]
        self.assertEqual(verify(data, {"owners": [ROUTE[0]]})["swaps"], 0)
        data = {"utilities": [[0, "0.0"], [0, 0], [0, 0], [0, 0]],
                "final_recipients": [3, 1], "start": [[3, 0], [1, 1]],
                "target": [[1, 0], [3, 1]]}
        self.assertEqual(verify(data, {"owners": [[3, 1], [1, 3]]})["sizes"], [0, 1, 0, 1])

    def test_complete_rounds_with_three_good_bundles(self):
        data = {"utilities": [[10, 10, 10, 0, 0, 0]] * 2, "final_recipients": [],
                "start": [[0, 0], [1, 1], [0, 2], [1, 3], [0, 4], [1, 5]],
                "target": [[1, 0], [0, 1], [1, 2], [0, 3], [1, 4], [0, 5]]}
        route = [[0, 1, 0, 1, 0, 1], [1, 0, 0, 1, 0, 1],
                 [1, 0, 1, 0, 0, 1], [1, 0, 1, 0, 1, 0]]
        self.assertEqual(verify(data, {"owners": route})["swaps"], 3)
        with self.assertRaisesRegex(ValueError, "not EF1"):
            verify(data, {"owners": [route[0], [0, 0, 0, 1, 1, 1], route[-1]]})

    def test_utility_and_instance_failures(self):
        for value in (True, None, 0.1, -1, "-1/7", "1/0", "NaN", "Infinity", "bad", [], {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                data = copy.deepcopy(EXAMPLE)
                data["utilities"][0][0] = value
                verify(data, {"owners": ROUTE})
        for rows in ([], [[1]], [[], []], [[0], [0, 1]], [0, 0], None):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                verify({**EXAMPLE, "utilities": rows}, {"owners": ROUTE})
        for data in (None, [], {}, {**EXAMPLE, "extra": 1}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                verify(data, {"owners": ROUTE})

    def test_final_recipients_and_witness_failures(self):
        for final in (None, True, [], [True], [3], [-1], [0, 0], [0.0]):
            with self.subTest(final=final), self.assertRaises(ValueError):
                verify({**EXAMPLE, "final_recipients": final}, {"owners": ROUTE})
        witnesses = [[], EXAMPLE["start"][:-1], [[False, 0]] * 4,
                     [[1, 0], [0, 1], [2, 3], [1, 2]],
                     [[1, 0], [0, 1], [2, 3], [0, 0]],
                     [[1, 0], [0, 1], [2, 3], [0, 4]],
                     [[1, 0], [0, 1], [0, 2], [2, 3]],
                     [[0, 0], [1, 2], [2, 3], [0, 1]], None]
        for name in ("start", "target"):
            for witness in witnesses:
                with self.subTest(name=name, witness=witness), self.assertRaises(ValueError):
                    verify({**EXAMPLE, name: witness}, {"owners": ROUTE})
        denominator = 10**100
        tiny = {"utilities": [[1, f"{denominator+1}/{denominator}"], [0, 0], [0, 0]],
                "final_recipients": [0, 1], "start": [[0, 0], [1, 1]], "target": [[0, 0], [1, 1]]}
        with self.assertRaisesRegex(ValueError, "not a utility maximizer"):
            verify(tiny, {"owners": [[0, 1]]})

    def test_route_failures(self):
        bad = [(None, "nonempty"), ([], "nonempty"), ([ROUTE[-1], ROUTE[0]], "endpoints"),
               ([ROUTE[0], ROUTE[-1]], "exactly two"),
               ([ROUTE[0], ROUTE[0], *ROUTE[1:]], "exactly two"),
               ([ROUTE[0], [1, 1, 0, 2], ROUTE[-1]], "bundle sizes"),
               ([ROUTE[0], [1, 2, 0, 0], ROUTE[-1]], "not EF1")]
        for state in ([False, 0, 1, 2], [0, 0, 1, 3], [-1, 0, 1, 2],
                      [0, 0, 1], [0, 0, 1, 2, 2], [0.0, 0, 1, 2], None):
            bad.append(([ROUTE[0], state, ROUTE[-1]], "valid integer owner"))
        for route, message in bad:
            with self.subTest(route=route), self.assertRaisesRegex(ValueError, message):
                verify(EXAMPLE, {"owners": route})
        cycle = {"utilities": [[0] * 3] * 3, "final_recipients": [],
                 "start": [[0, 0], [1, 1], [2, 2]], "target": [[1, 0], [2, 1], [0, 2]]}
        with self.assertRaisesRegex(ValueError, "exactly two"):
            verify(cycle, {"owners": [[0, 1, 2], [1, 2, 0]]})

    def test_optional_trade_log_is_checked_other_claims_are_not_trusted(self):
        saved = {"owners": ROUTE, "verified": False, "swaps": 999, "sizes": []}
        self.assertEqual(verify(EXAMPLE, saved)["swaps"], 2)
        for trades in (None, [], TRADES[:1], [*TRADES, TRADES[0]],
                       [{"goods": [0, 2], "agents": [0, 1]}, TRADES[1]],
                       [{"goods": [0, 2], "agents": [True, 0]}, TRADES[1]],
                       [{"goods": [0, 0], "agents": [1, 0]}, TRADES[1]],
                       [None, TRADES[1]], [{**TRADES[0], "extra": 1}, TRADES[1]]):
            with self.subTest(trades=trades), self.assertRaises(ValueError):
                verify(EXAMPLE, {"owners": ROUTE, "exchanges": trades})

    def test_isolated_real_command_and_combined_certificate(self):
        saved = {"owners": ROUTE, "exchanges": TRADES}
        for run in (command(EXAMPLE, saved), command({"instance": EXAMPLE, "path": saved})):
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), verify(EXAMPLE, saved))
        failed = command(EXAMPLE, {"owners": [ROUTE[0], ROUTE[-1]]})
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, "")
        self.assertNotIn("Traceback", failed.stderr)

    def test_json_errors_fail_without_output_or_traceback(self):
        for raw in ('{"instance": {}, "instance": {}, "path": {}}', '{', '[]',
                    '{"instance": NaN, "path": {}}',
                    '{"instance": {}, "path": {}, "extra": 1}'):
            with self.subTest(raw=raw):
                result = command(raw)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
