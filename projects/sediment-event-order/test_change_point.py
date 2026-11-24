"""Independent small-case checks, including prior-count and estimand traps."""
import itertools
from decimal import Decimal, localcontext
from fractions import Fraction
import math
import unittest
from unittest.mock import patch

from change_point import (Prior, SegmentEvidence, interval, logsum,
                          mixing_counterexample, partition_count,
                          segment_posterior, response_moments,
                          population_segment_loss, population_window_scan,
                          RationalInterval, exp_negative_enclosure,
                          certified_mismatch, draw_prior, log_enclosure,
                          exact_unmixed_posterior, GaussianOneEventInference)


def covariance_evidence(x, y, prior):
    """Independent n-dimensional Student-t density via Cholesky.

    The implementation under test instead works in one/two coefficient
    dimensions. This checks constants, determinant and quadratic terms.
    """
    rows = [(1,) if len(prior.precision) == 1 else (1, t) for t in x]
    n = len(y)
    matrix = [[float(i == j)+sum(a*b/k for a, b, k in
               zip(rows[i], rows[j], prior.precision)) for j in range(n)] for i in range(n)]
    lower = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            value = matrix[i][j]-sum(lower[i][k]*lower[j][k] for k in range(j))
            lower[i][j] = math.sqrt(value) if i == j else value/lower[j][j]
    z = []
    for i in range(n):
        z.append((y[i]-sum(lower[i][j]*z[j] for j in range(i)))/lower[i][i])
    v, scale = prior.degrees, prior.variance
    return (math.lgamma((v+n)/2)-math.lgamma(v/2)
            -n/2*math.log(v*math.pi*scale)
            -sum(math.log(lower[i][i]) for i in range(n))
            -(v+n)/2*math.log1p(sum(t*t for t in z)/(v*scale)))


def exhaustive(x, y, prior):
    n = len(y)
    entries = []
    for k in range(prior.max_changes+1):
        partitions = []
        for cuts in itertools.combinations(range(1, n), k):
            ends = (0,)+cuts+(n,)
            if min(b-a for a, b in zip(ends, ends[1:])) < prior.min_length:
                continue
            value = sum(covariance_evidence(x[a:b], y[a:b], prior)
                        for a, b in zip(ends, ends[1:]))
            partitions.append((cuts, value))
        entries.extend((k, cuts, value-math.log(len(partitions))) for cuts, value in partitions)
    norm = logsum(value for _, _, value in entries)
    counts = [0.]*(prior.max_changes+1)
    boundaries = [0.]*(n+1)
    one = [0.]*(n+1)
    for k, cuts, value in entries:
        p = math.exp(value-norm)
        counts[k] += p
        for cut in cuts:
            boundaries[cut] += p
        if k == 1:
            one[cuts[0]] += p
    if prior.max_changes:
        one = [v/counts[1] for v in one]
    return counts, boundaries, one


class EvidenceTests(unittest.TestCase):
    def test_one_event_gap_weights_against_observation_space_density(self):
        try:
            from baseline import Observation
            import continuous
        except ModuleNotFoundError:
            self.skipTest('foundation required for shared density representation')
        x, counts = (-3., 0., 1., 4., 7., 10.), (8, 6, 7, 3, 1, 0)
        prior = Prior((.1, .2), 3, .7, 1, 1)
        model = GaussianOneEventInference(x, prior, -1, 8)
        fit = model.fit(Observation(x, 8, counts))
        y = tuple(v/8 for v in counts)
        logs = []
        for a, b, cut in zip(model.edges, model.edges[1:], model.cuts):
            logs.append(covariance_evidence(x[:cut], y[:cut], prior)
                        +covariance_evidence(x[cut:], y[cut:], prior)+math.log(b-a))
        norm = logsum(logs)
        for p, log_p in zip(fit.masses, logs):
            self.assertAlmostEqual(p, math.exp(log_p-norm), places=11)
        # Uninformative evidence must recover uniform TIME, not uniform gaps.
        with patch.object(SegmentEvidence, '__call__', return_value=0.):
            flat = model.fit(Observation(x, 8, counts))
        for time in (-1., -.5, 0., 2., 4., 7.5, 8.):
            self.assertAlmostEqual(flat.cdf(time), (time+1)/9, places=12)
        with self.assertRaises(ValueError):
            GaussianOneEventInference(x, prior, -4, 8)

    def test_segment_against_independent_student_density(self):
        x, y = (-2., -.2, 1., 3., 4.), (.5, -1., 2., 1., 0.)
        for precision in ((.01,), (.3, .7)):
            prior = Prior(precision, 3., 2., 1, 0)
            evidence = SegmentEvidence(x, y, prior)
            for a in range(len(x)):
                for b in range(a+1, len(x)+1):
                    self.assertAlmostEqual(evidence(a, b), covariance_evidence(x[a:b], y[a:b], prior), places=11)

    def test_dynamic_programming_against_enumerated_partitions(self):
        x = (-3., -1., 0., 1., 2., 4., 5.)
        y = (1., .2, -.4, .3, 2., 3., 4.)
        for precision in ((.1,), (.2, .3)):
            for minimum in (1, 2):
                prior = Prior(precision, 2., .7, minimum, 2)
                result = segment_posterior(x, y, prior)
                reference = exhaustive(x, y, prior)
                for actual, expected in zip((result.count_probabilities,
                         result.boundary_probabilities, result.one_change_probabilities), reference):
                    for a, b in zip(actual, expected):
                        self.assertAlmostEqual(a, b, places=10)
                self.assertAlmostEqual(sum(result.boundary_probabilities), result.expected_changes, places=11)

    def test_no_data_information_returns_uniform_count_prior(self):
        # Without partition-count correction, this strongly favors larger K.
        with patch.object(SegmentEvidence, '__call__', return_value=0.):
            fit = segment_posterior(tuple(range(12)), (0.,)*12, Prior((.1,), 1, 1, 2, 3))
        for p in fit.count_probabilities:
            self.assertAlmostEqual(p, .25, places=12)
        self.assertAlmostEqual(sum(fit.boundary_probabilities), 1.5, places=12)

    def test_composition_counts_against_enumeration(self):
        for n in range(1, 12):
            for minimum in range(1, 4):
                for segments in range(1, 5):
                    count = sum(all(b-a >= minimum for a, b in zip((0,)+cuts, cuts+(n,)))
                                for cuts in itertools.combinations(range(1, n), segments-1))
                    self.assertEqual(partition_count(n, segments, minimum), count)

    def test_zero_change_model_has_no_boundary(self):
        fit = segment_posterior((0., 1., 2.), (.1, .2, .3), Prior((.1,), 1, 1, 1, 0))
        self.assertEqual(fit.count_probabilities, (1.,))
        self.assertEqual(sum(fit.boundary_probabilities), 0.)

    def test_rejects_invalid_inputs(self):
        for kwargs in ({'precision': (0.,)}, {'precision': (1., 2., 3.)},
                       {'degrees': math.nan}, {'variance': 0}, {'min_length': True},
                       {'max_changes': -1}):
            with self.assertRaises(ValueError):
                Prior(**kwargs)
        for x, y in (((), ()), ((1, 1), (0, 1)), ((0, 1), (0, math.inf)), ((0, 1), (0,))):
            with self.assertRaises(ValueError):
                segment_posterior(x, y, Prior((.1,), 1, 1, 1, 0))
        with self.assertRaises(ValueError):
            segment_posterior((0, 1), (0, 1), Prior(min_length=2, max_changes=1))
        with self.assertRaises(ValueError):
            SegmentEvidence((0., 1.), (1e308, 0.), Prior())

    def test_prior_sampler_uniform_partition_construction(self):
        # Enumerate every equiprobable stars-and-bars choice, then verify the
        # generated physical cuts equal every valid partition exactly once.
        n, d, k = 10, 2, 2
        spare = n-(k+1)*d
        class ControlledRandom:
            def __init__(self, bars):
                self.bars = bars
            def randrange(self, maximum):
                return k
            def sample(self, population, size):
                return self.bars
            def gammavariate(self, shape, scale):
                return 1.
            def gauss(self, mean, deviation):
                return mean
        got = []
        for bars in itertools.combinations(range(spare+k), k):
            rng = ControlledRandom(bars)
            cuts, y = draw_prior(tuple(range(n)), Prior((.1,), 4, 1, d, k), rng, rng)
            got.append(cuts)
            self.assertEqual(len(y), n)
        expected = [cuts for cuts in itertools.combinations(range(1, n), k)
                    if min(b-a for a, b in zip((0,)+cuts, cuts+(n,))) >= d]
        self.assertEqual(sorted(got), expected)


class EstimandTests(unittest.TestCase):
    @staticmethod
    def fraction(f, event, h):
        # Independent direct exponential expression, not foundation import.
        return 1-math.exp(-(event-f+h)/h) if f < event+h else 0.

    def test_midpoint_and_kink_are_different_from_latent_event(self):
        for event, h in ((0., 200.), (-20., 25.), (100., 75.)):
            result = mixing_counterexample(event, h)
            self.assertAlmostEqual(self.fraction(result['half_height'], event, h), .5)
            self.assertEqual(self.fraction(result['support_kink'], event, h), 0.)
            self.assertGreater(result['half_height'], event)
            self.assertGreater(result['support_kink'], result['half_height'])

    def test_unmixed_continuous_prior_exact_three_intervals(self):
        try:
            from baseline import Design, Observation
            from continuous import ContinuousInference
        except ModuleNotFoundError:
            self.skipTest('foundation modules not yet integrated; supply verified reference on PYTHONPATH')
        design = Design(focal_ages=(-1., 1.), mixing_times=(0.,), specimens=2)
        obs = Observation(design.focal_ages, 2, (2, 0))
        # Exact piecewise likelihoods on [-2,-1],[-1,1],[1,2].
        side, center = .1**2*.9**2, .9**4
        normalizer = 2*side+2*center
        for step in (.25, .0625):
            fit = ContinuousInference(design, step=step, lower=-2, upper=2).fit(obs)
            for value, expected in ((-1, side/normalizer), (0, .5), (1, 1-side/normalizer)):
                self.assertAlmostEqual(fit.cdf(value), expected, places=12)
            expected_lo = -1+(.05*normalizer-side)/center
            self.assertAlmostEqual(fit.quantile(.05), expected_lo, places=12)
            self.assertAlmostEqual(fit.quantile(.95), -expected_lo, places=12)
        exact = exact_unmixed_posterior(design.focal_ages, obs.positive_counts, 2, -2, 2)
        self.assertEqual(exact.masses, (Fraction(1, 164), Fraction(81, 82), Fraction(1, 164)))
        self.assertAlmostEqual(exact.quantile(.05), expected_lo, places=12)
        self.assertEqual(exact.cdf(-3), 0.)
        self.assertEqual(exact.cdf(3), 1.)

    def test_unmixed_sampling_gap_is_an_exact_resolution_limit(self):
        focal = (-2., -1., 0., 1., 2.)
        # Arbitrarily many specimens cannot distinguish .25 from .75: every
        # specimen probability at every sampled layer is exactly the same.
        for tau in (Fraction(1, 4), Fraction(3, 4)):
            probabilities = tuple(Fraction(9 if f <= tau else 1, 10) for f in focal)
            self.assertEqual(probabilities, (Fraction(9, 10),)*3+(Fraction(1, 10),)*2)
        for counts in ((0,)*5, (8, 8, 8, 0, 0), (4,)*5, (8,)*5):
            fit = exact_unmixed_posterior(focal, counts, 8, -2, 2)
            # Unit-width prior cells force density <=1, hence any 90% interval
            # has width at least .9. No midpoint atom may beat this limit.
            self.assertGreaterEqual(fit.quantile(.95)-fit.quantile(.05), .9-1e-12)
            for left, right, mass in zip(fit.edges, fit.edges[1:], fit.masses):
                midpoint = (left+right)/2
                self.assertAlmostEqual(fit.cdf(midpoint)-fit.cdf(left), float(mass)/2, places=12)

    def test_event_is_smooth_with_nonzero_curvature(self):
        h, event, delta = 75., -10., .01
        result = mixing_counterexample(event, h)
        q = self.fraction
        slope = (q(event+delta, event, h)-q(event-delta, event, h))/(2*delta)
        curvature = (q(event+delta, event, h)-2*q(event, event, h)+q(event-delta, event, h))/delta**2
        self.assertAlmostEqual(slope, result['mean_slope_at_event'], places=9)
        self.assertAlmostEqual(curvature, result['mean_curvature_at_event'], places=10)

    def test_boundary_alone_does_not_identify_event(self):
        # Same support boundary, distinct latent events.
        a, b = mixing_counterexample(0., 75.), mixing_counterexample(50., 25.)
        self.assertEqual(a['support_kink'], b['support_kink'])
        self.assertNotEqual(a['latent_event'], b['latent_event'])
        # Even the entire observation law can agree for a badly placed window.
        for focal in (75., 100., 125.):
            self.assertEqual(self.fraction(focal, 0., 75.), self.fraction(focal, 50., 25.))

    def test_interval_requires_conditional_normalization(self):
        self.assertEqual(interval((0, 1, 2), (.1, .8, .1)), (0, 2))
        with self.assertRaises(ValueError):
            interval((0, 1, 2), (.1, .1, .1))

    def test_response_integrals_against_simpson_quadrature(self):
        for left, right in ((-4., .5), (-1., 3.), (1., 3.)):
            end = min(right, 1.)
            expected = []
            for power in (0, 1, 2):
                def f(t):
                    q = self.fraction(t, 0., 1.)
                    return (q, t*q, q*q)[power]
                if left >= end:
                    expected.append(0.)
                    continue
                steps = 4000
                h = (end-left)/steps
                value = f(left)+f(end)+sum((4 if i % 2 else 2)*f(left+i*h)
                                         for i in range(1, steps))
                expected.append(value*h/3)
            for actual, numerical in zip(response_moments(left, right), expected):
                self.assertAlmostEqual(actual, numerical, places=11)

    def test_exact_certificate_and_window_effect(self):
        proof = certified_mismatch()
        self.assertTrue(proof['exact_rational_positive_gap_verified'])
        self.assertTrue(proof['binomial_gaussian_profile_positive_gap_verified'])
        at_tau = population_segment_loss(-4., 0.)+population_segment_loss(0., 3.)
        alternative = population_segment_loss(-4., .5)+population_segment_loss(.5, 3.)
        self.assertAlmostEqual(at_tau-alternative, proof['gap_display_only'][0], places=12)
        a, b = population_window_scan(-4., 3.), population_window_scan(-1., 3.)
        self.assertGreater(b['best_grid_boundary_in_mixing_units']-a['best_grid_boundary_in_mixing_units'], .3)

    def test_rational_enclosures(self):
        a, b = RationalInterval(Fraction(-2), Fraction(3)), RationalInterval(Fraction(4), Fraction(5))
        self.assertEqual((a*b).low, -10)
        self.assertEqual((a*b).high, 15)
        self.assertEqual((a/b).low, Fraction(-1, 2))
        self.assertEqual((a/b).high, Fraction(3, 4))
        with self.assertRaises(ZeroDivisionError):
            b/a
        # Decimal's independent exponential is only a check of the enclosure;
        # the certificate's validity comes from its explicit Taylor-tail bound.
        with localcontext() as ctx:
            ctx.prec = 70
            for x in (Fraction(0), Fraction(1, 2), Fraction(5)):
                bound = exp_negative_enclosure(x, terms=30)
                decimal_x = Decimal(x.numerator)/Decimal(x.denominator)
                target = (-decimal_x).exp()
                lower = Decimal(bound.low.numerator)/Decimal(bound.low.denominator)
                upper = Decimal(bound.high.numerator)/Decimal(bound.high.denominator)
                self.assertLessEqual(lower, target)
                self.assertGreaterEqual(upper, target)
            for x in (Fraction(1, 3), Fraction(1), Fraction(5)):
                bound = log_enclosure(RationalInterval.exact(x), terms=50)
                target = (Decimal(x.numerator)/Decimal(x.denominator)).ln()
                lower = Decimal(bound.low.numerator)/Decimal(bound.low.denominator)
                upper = Decimal(bound.high.numerator)/Decimal(bound.high.denominator)
                self.assertLessEqual(lower, target)
                self.assertGreaterEqual(upper, target)


if __name__ == '__main__':
    unittest.main()
