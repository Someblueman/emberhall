import math
import unittest

from baseline import Design, Observation
from continuous import ContinuousInference, Density, cdf_distance
from reference import Reference
from audit import audit


class ContinuousTests(unittest.TestCase):
    def test_unmixed_exact_piecewise_example(self):
        design = Design(events=(0,), mixing_times=(0,), focal_ages=(-1, 1), specimens=1)
        obs = Observation((-1, 1), 1, (1, 0))
        # Likelihood .09, .81, .09 on widths 1,2,1 => masses .05,.90,.05.
        for step in (.3, 1, 4):
            fitted = ContinuousInference(design, step, -2, 2).fit(obs)
            self.assertAlmostEqual(fitted.cdf(-1), .05)
            self.assertAlmostEqual(fitted.cdf(0), .5)
            self.assertAlmostEqual(fitted.cdf(1), .95)
            self.assertAlmostEqual(fitted.quantile(.05), -1)
            self.assertAlmostEqual(fitted.quantile(.95), 1)

    def test_single_mixed_layer_against_analytic_integration(self):
        design = Design(events=(0,), mixing_times=(1,), focal_ages=(0,), specimens=1)
        fitted = ContinuousInference(design, .01, -2, 2).fit(Observation((0,), 1, (1,)))

        def primitive(age):
            z = max(0, age + 1)
            return .1 * age + .8 * (z + math.expm1(-z))

        normalizer = primitive(2) - primitive(-2)
        for age in (-2, -1, -.7, 0, .3, 1, 2):
            exact = (primitive(age) - primitive(-2)) / normalizer
            self.assertLess(abs(fitted.cdf(age) - exact), 3e-6)

    def test_quantile_cdf_inverse_and_distance(self):
        density = Density((0, 1, 3, 5), (.25, 0, .75))
        for probability in (0, .05, .25, .5, .95, 1):
            self.assertAlmostEqual(density.cdf(density.quantile(probability)), probability)
        other = Density((0, 5), (1,))
        # Difference at x=3 is |.25-.6|=.35, its global maximum.
        self.assertAlmostEqual(cdf_distance(density, other), .35)

    def test_refinement_and_state_validation(self):
        design = Design()
        obs = Observation(design.focal_ages, 16, (12,) * len(design.focal_ages))
        coarse = ContinuousInference(design, 1).fit(obs)
        fine = ContinuousInference(design, .5).fit(obs)
        finer = ContinuousInference(design, .25).fit(obs)
        reference = ContinuousInference(design, .125).fit(obs)
        # Preserve the witnessed one-year failure rather than widening its
        # proposed one-percent tolerance. Refinement resolves this witness.
        self.assertGreater(cdf_distance(coarse, fine), .01)
        self.assertLess(cdf_distance(fine, finer), .004)
        self.assertLess(cdf_distance(finer, reference), .001)
        for step in (0, -1, math.nan, 1e-10):
            with self.assertRaises(ValueError):
                ContinuousInference(design, step)
        with self.assertRaises(ValueError):
            Density((0, 1), (.9,))
        with self.assertRaises(ValueError):
            coarse.quantile(math.nan)

    def test_reference_against_analytic_single_layer_integral(self):
        design = Design(events=(0,), mixing_times=(1,), focal_ages=(0,), specimens=1)
        fitted = Reference(design, Observation((0,), 1, (1,)))

        def primitive(age):
            z = max(0, age + 1)
            return .1 * age + .8 * (z + math.expm1(-z))

        for age in (-99, -1, -.7, 0, .3, 1, 99):
            exact = (primitive(age) - primitive(-100)) / (primitive(100) - primitive(-100))
            self.assertAlmostEqual(fitted.cdf(age), exact, places=9)
        with self.assertRaises(ArithmeticError):
            Reference(design, Observation((0,), 1, (1,)), max_evaluations=1)

    def test_fixed_extreme_observation_audit(self):
        result = audit()
        self.assertGreater(result['max_probe_cdf_errors'][0], .01)
        self.assertLess(result['max_probe_cdf_errors'][-1], .001)
        self.assertLess(result['max_reference_tolerance_difference'], 1e-7)


if __name__ == '__main__':
    unittest.main()
