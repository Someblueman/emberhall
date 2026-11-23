"""Bit-reproducibility: one fixed construction, one fixed answer.

Covariance entries are sums over primitive sources in Jacobian-dict
order.  If that order ever comes from a set, the sum order depends on
object hashes and identical programs in different processes can print
values that differ in the last bit.  These tests pin the
left-then-right source order and require byte-identical output from
independent interpreter processes.
"""
import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from covreduce import source  # noqa: E402

SNIPPET = textwrap.dedent("""
    from covreduce import source

    total = None
    for k in range(40):
        s = source([10.0 ** (k % 9 - 4), 1.0 + 0.01 * k],
                   [10.0 ** (k % 7 - 3), 0.05], dims=("bin",))
        total = s if total is None else total + s * (1.0 + 0.1 * k)
    monitor = source(997.0, 13.0)
    rates = total / monitor
    print(repr((rates.values, rates.variance, rates.covariance(),
                rates.quadratic_form([0.7, -1.3]))))
    """)


class TestSourceOrder(unittest.TestCase):
    def test_binary_op_keeps_left_then_right_sources(self):
        a = source([1.0], [0.1], dims=("bin",))
        b = source([2.0], [0.2], dims=("bin",))
        c = source([3.0], [0.3], dims=("bin",))
        combined = (a + b) * (b + c)
        self.assertEqual(list(combined._jacobians),
                         [a._source, b._source, c._source])

    def test_shared_source_keeps_first_position(self):
        a = source([1.0], [0.1], dims=("bin",))
        b = source([2.0], [0.2], dims=("bin",))
        combined = (b - a) / (a + b)
        self.assertEqual(list(combined._jacobians),
                         [b._source, a._source])


class TestCrossProcessReproducibility(unittest.TestCase):
    def test_identical_output_across_processes(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(PROJECT) + os.pathsep + env.get(
            "PYTHONPATH", "")
        outputs = set()
        for _ in range(4):
            proc = subprocess.run(
                [sys.executable, "-c", SNIPPET], capture_output=True,
                text=True, env=env, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            outputs.add(proc.stdout)
        self.assertEqual(len(outputs), 1, outputs)


if __name__ == "__main__":
    unittest.main()
