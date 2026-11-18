"""Check the exact arithmetic, the certificate, and the real command boundary."""

from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import unittest

import check


class ExactArithmeticTests(unittest.TestCase):
    def test_expansion_and_cancellation(self):
        u, v = check.u, check.v
        check.require_zero((u + v)**2 - u**2 - 2 * u * v - v**2, "binomial")
        self.assertEqual((u - u).terms, {})

    def test_rational_coefficients_and_laurent_derivative(self):
        b_inv = check.Poly.variable("b", -1)
        expression = Fraction(1, 3) * check.u**3 * b_inv
        self.assertEqual(expression.diff("u").evaluate(u=2, b=3), Fraction(4, 3))
        self.assertEqual(b_inv.diff("b").evaluate(b=3), Fraction(-1, 9))
        check.require_zero(check.b * b_inv - 1, "inverse")

    def test_exact_substitution_and_no_float_coefficients(self):
        p = (check.u + check.v)**2
        check.require_zero(p.substitute("v", check.u) - 4 * check.u**2, "substitution")
        with self.assertRaises(TypeError):
            _ = check.u + 0.1


class CertificateTests(unittest.TestCase):
    def test_all_symbolic_checks(self):
        labels = check.run_checks()
        self.assertIn("m=2 Dulac identity", labels)
        self.assertIn("symbolic m Dulac identity", labels)
        self.assertIn("negative control rejected (y loss coefficient 1 -> 2)", labels)

    def test_altered_coefficient_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "altered m=2 Dulac identity"):
            check.run_checks(altered_coefficient=True)

    def test_residual_is_independently_recoverable(self):
        f, g, h, p = check.field(y_loss=2)
        actual = check.residual(f, g, h, p).substitute("m", 2)
        expected = check.u * (check.alpha * check.u**2 - 2 * check.u + 2)
        check.require_zero(actual - expected, "damaged residual")
        self.assertEqual(actual.evaluate(u=2, alpha=1), 4)

    def test_strict_boundary_sign_at_exact_points(self):
        _, _, _, p = check.field()
        for u in (Fraction(1000001, 1000000), Fraction(2), Fraction(1000)):
            for alpha in (Fraction(1, 1000000), Fraction(1), Fraction(1000)):
                for m in (Fraction(2), Fraction(5, 2), Fraction(1000)):
                    with self.subTest(u=u, alpha=alpha, m=m):
                        self.assertGreater(p.evaluate(u=u, alpha=alpha, m=m), 0)
        # The sign proof, not these samples, establishes all parameter values.

    def test_cli_success_and_failure_survive_optimization(self):
        script = Path(check.__file__).resolve()
        for flags in ([], ["-O"]):
            good = subprocess.run([sys.executable, *flags, str(script)],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("Exact algebra passed", good.stdout)
            bad = subprocess.run([sys.executable, *flags, str(script), "--altered-coefficient"],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("nonzero residual", bad.stderr)
            self.assertNotIn("Exact algebra passed", bad.stdout)


if __name__ == "__main__":
    unittest.main()
