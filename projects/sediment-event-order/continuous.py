#!/usr/bin/env python3
"""Continuous event-time prior with cell quadrature and refinement diagnostics.

This is a numerical baseline, not a certified error bound. Each posterior
uses only observed counts; true event times enter evaluation separately.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass, field
import json
import math
import random

from baseline import (Design, Observation, ks_uniform, normalize, response,
                      simulate, validate_observation)


@dataclass(frozen=True)
class Density:
    edges: tuple[float, ...]
    masses: tuple[float, ...]
    cumulative: tuple[float, ...] = field(init=False, repr=False)

    def __post_init__(self):
        if len(self.edges) != len(self.masses) + 1 or not self.masses:
            raise ValueError("one more edge than nonempty cell masses required")
        if any(not math.isfinite(x) for x in self.edges + self.masses):
            raise ValueError("finite density required")
        if any(a >= b for a, b in zip(self.edges, self.edges[1:])):
            raise ValueError("strictly increasing density edges required")
        if any(x < 0 for x in self.masses) or abs(math.fsum(self.masses) - 1) > 1e-10:
            raise ValueError("nonnegative normalized density required")
        cumulative = [0.0]
        for mass in self.masses:
            cumulative.append(cumulative[-1] + mass)
        object.__setattr__(self, 'cumulative', tuple(cumulative))

    def cdf(self, age):
        if not math.isfinite(age):
            raise ValueError("finite CDF argument required")
        if age <= self.edges[0]:
            return 0.0
        if age >= self.edges[-1]:
            return 1.0
        index = bisect_right(self.edges, age) - 1
        fraction = (age - self.edges[index]) / (self.edges[index + 1] - self.edges[index])
        return self.cumulative[index] + self.masses[index] * fraction

    def quantile(self, probability):
        if not 0 <= probability <= 1:
            raise ValueError("quantile probability must be in [0,1]")
        total = 0.0
        for left, right, mass in zip(self.edges, self.edges[1:], self.masses):
            if total + mass >= probability and mass:
                return left + (right - left) * (probability - total) / mass
            total += mass
        return self.edges[-1]


class ContinuousInference:
    """Uniform event prior on [lower,upper], uniform discrete mixing prior.

    Within each event-time cell we use the midpoint likelihood; the result
    is a continuous piecewise-uniform approximate posterior, not atoms at
    the midpoints. Precompute observation-independent log probabilities.
    """
    def __init__(self, design: Design, step=1.0, lower=-100.0, upper=100.0):
        if not all(math.isfinite(x) for x in (step, lower, upper)):
            raise ValueError("finite grid bounds and step required")
        if step <= 0 or lower >= upper:
            raise ValueError("positive step and increasing bounds required")
        if math.ceil((upper - lower) / step) > 20000:
            raise ValueError("at most 20000 cells per inference allowed")
        self.design = design
        # Split every zero-mixing jump and positive-mixing support boundary.
        # No cell straddles a nonsmooth point of any component likelihood.
        breaks = {lower, upper}
        for focal in design.focal_ages:
            for mixing in design.mixing_times:
                if lower < focal - mixing < upper:
                    breaks.add(focal - mixing)
        boundaries = sorted(breaks)
        edges = [lower]
        for left, right in zip(boundaries, boundaries[1:]):
            n = math.ceil((right - left) / step)
            edges.extend(left + (right - left) * i / n for i in range(1, n + 1))
        if len(edges) - 1 > 20000:
            raise ValueError("support splits exceed 20000-cell resource limit")
        self.edges = tuple(edges)
        self.components = []
        for left, right in zip(edges, edges[1:]):
            event = (left + right) / 2
            parts = []
            for mixing in design.mixing_times:
                probabilities = [response(design, f, event, mixing) for f in design.focal_ages]
                parts.append(tuple((math.log(p), math.log1p(-p)) for p in probabilities))
            self.components.append(parts)

    def fit(self, obs: Observation) -> Density:
        validate_observation(self.design, obs)
        logs = []
        n = obs.specimens
        for left, right, components in zip(self.edges, self.edges[1:], self.components):
            log_terms = [math.fsum(k * lp + (n - k) * lq
                                   for k, (lp, lq) in zip(obs.positive_counts, component))
                         for component in components]
            top = max(log_terms)
            mixed = top + math.log(math.fsum(math.exp(x - top) for x in log_terms))
            # Uniform h and uniform event prior constants cancel. Cell width
            # MUST remain: support-boundary splits can make unequal cells.
            logs.append(mixed + math.log(right - left))
        return Density(self.edges, normalize(logs))


def cdf_distance(first: Density, second: Density):
    # Both CDFs are piecewise linear, so the exact sup difference occurs at
    # an edge from one of the two partitions.
    return max(abs(first.cdf(x) - second.cdf(x)) for x in set(first.edges + second.edges))


def experiment(trials=2000, seed=20261124, steps=(.25, .125, .0625)):
    if type(trials) is not int or not 1 <= trials <= 10000:
        raise ValueError("trials must be from 1 to 10000")
    if not steps or any(x <= 0 or not math.isfinite(x) for x in steps):
        raise ValueError("finite positive steps required")
    design = Design()
    inference = [ContinuousInference(design, step) for step in steps]
    truth_rng = random.Random(seed)
    specimen_rng = random.Random(seed + 1)
    summaries = [{"pits": [], "covered": 0, "width": 0.0,
                  "below": [], "above": [], "max_cdf_difference_from_finest": 0.0}
                 for _ in steps]
    max_quantile_difference = [0.0] * len(steps)
    for _ in range(trials):
        event = truth_rng.uniform(-100, 100)
        mixing = truth_rng.choice(design.mixing_times)
        obs = simulate(design, event, mixing, specimen_rng)
        fitted = [model.fit(obs) for model in inference]
        finest = fitted[-1]
        group = "below" if 2 * sum(obs.positive_counts) < obs.specimens * len(obs.focal_ages) else "above"
        for i, (density, summary) in enumerate(zip(fitted, summaries)):
            pit = density.cdf(event)
            summary['pits'].append(pit)
            summary[group].append(pit)
            lo, hi = density.quantile(.05), density.quantile(.95)
            summary['covered'] += lo <= event <= hi
            summary['width'] += hi - lo
            difference = cdf_distance(density, finest)
            summary['max_cdf_difference_from_finest'] = max(summary['max_cdf_difference_from_finest'], difference)
            max_quantile_difference[i] = max(max_quantile_difference[i],
                abs(lo - finest.quantile(.05)), abs(hi - finest.quantile(.95)))
    results = []
    for step, model, summary, difference in zip(steps, inference, summaries, max_quantile_difference):
        distance = ks_uniform(summary['pits'])
        band = math.sqrt(math.log(200) / (2 * trials))
        groups = {}
        for key in ('below', 'above'):
            values = summary[key]
            groups[key] = {"trials": len(values), "pit_ks": ks_uniform(values)} if values else {"trials": 0}
        results.append({"step_years": step, "cells": len(model.edges) - 1,
                        "pit_ks": distance, "pit_99_percent_dkw_bound": band,
                        "pit_within_band": distance <= band,
                        "interval_coverage": summary['covered'] / trials,
                        "interval_width_mean_years": summary['width'] / trials,
                        "max_cdf_difference_from_finest": summary['max_cdf_difference_from_finest'],
                        "max_interval_endpoint_difference_years": difference,
                        "conditional_pit": groups})
    return {"version": 1, "law": "continuous event prior, discrete mixing prior; known chronology",
            "trials": trials, "seed": seed, "results": results,
            "warning": "Refinement differences are diagnostics, not certified integration error bounds."}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=20261124)
    args = parser.parse_args()
    print(json.dumps(experiment(args.trials, args.seed), indent=2, allow_nan=False))
