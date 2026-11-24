"""Independent adaptive integration reference for the continuous baseline.

Simpson residual estimates are diagnostics, not rigorous interval arithmetic.
This slow reference is intended for selected observations, not the benchmark.
"""
from __future__ import annotations

import math

from baseline import Design, Observation, response, validate_observation


class Reference:
    def __init__(self, design: Design, obs: Observation, tolerance=1e-10,
                 max_evaluations=250000):
        validate_observation(design, obs)
        if not math.isfinite(tolerance) or tolerance <= 0:
            raise ValueError("positive finite integration tolerance required")
        if type(max_evaluations) is not int or max_evaluations < 1:
            raise ValueError("positive integer evaluation budget required")
        self.design, self.obs = design, obs
        self.tolerance = tolerance
        self.evaluations = 0
        self.max_evaluations = max_evaluations
        self.estimated_error = 0.0
        # A fixed, observation-only scan supplies a stable common log scale.
        # It affects numerical units, not the probability law or prior.
        self.scale = max(self.log_likelihood(-100 + i * .5, h)
                         for h in design.mixing_times for i in range(401))
        self.normalizer = self.integral(-100, 100)
        if self.normalizer <= 0 or not math.isfinite(self.normalizer):
            raise ArithmeticError("reference normalizer is invalid")

    def log_likelihood(self, event, mixing):
        terms = []
        for focal, count in zip(self.obs.focal_ages, self.obs.positive_counts):
            p = response(self.design, focal, event, mixing)
            terms.append(count * math.log(p) + (self.obs.specimens - count) * math.log1p(-p))
        return math.fsum(terms)

    def likelihood(self, event, mixing):
        self.evaluations += 1
        if self.evaluations > self.max_evaluations:
            raise ArithmeticError("reference integration exhausted its evaluation budget")
        return math.exp(self.log_likelihood(event, mixing) - self.scale)

    def integrate_smooth(self, left, right, mixing):
        def f(x):
            return self.likelihood(x, mixing)

        def simpson(a, b, fa, fm, fb):
            return (b - a) * (fa + 4 * fm + fb) / 6

        def refine(a, b, fa, fm, fb, estimate, tolerance, depth):
            midpoint = (a + b) / 2
            fl, fr = f((a + midpoint) / 2), f((midpoint + b) / 2)
            first = simpson(a, midpoint, fa, fl, fm)
            second = simpson(midpoint, b, fm, fr, fb)
            delta = first + second - estimate
            if abs(delta) <= 15 * tolerance:
                self.estimated_error += abs(delta) / 15
                return first + second + delta / 15
            if depth == 0:
                raise ArithmeticError("reference integration did not reach its tolerance")
            return (refine(a, midpoint, fa, fl, fm, first, tolerance / 2, depth - 1)
                    + refine(midpoint, b, fm, fr, fb, second, tolerance / 2, depth - 1))

        # Begin with eight panels per smooth interval. This prevents a narrow
        # peak from being judged flat solely from two endpoints and a midpoint.
        results = []
        for i in range(8):
            a = left + (right - left) * i / 8
            b = left + (right - left) * (i + 1) / 8
            fa, fm, fb = f(a), f((a + b) / 2), f(b)
            results.append(refine(a, b, fa, fm, fb, simpson(a, b, fa, fm, fb),
                                  self.tolerance * (b - a) / 200, 20))
        return math.fsum(results)

    def integral(self, left, right):
        if right <= left:
            return 0.0
        terms = []
        for mixing in self.design.mixing_times:
            boundaries = sorted({left, right} | {f - mixing for f in self.design.focal_ages
                                                if left < f - mixing < right})
            for a, b in zip(boundaries, boundaries[1:]):
                if mixing == 0:
                    terms.append((b - a) * self.likelihood((a + b) / 2, mixing))
                else:
                    terms.append(self.integrate_smooth(a, b, mixing))
        return math.fsum(terms)

    def cdf(self, age):
        if not math.isfinite(age):
            raise ValueError("finite CDF argument required")
        if age <= -100:
            return 0.0
        if age >= 100:
            return 1.0
        return self.integral(-100, age) / self.normalizer
