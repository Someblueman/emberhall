#!/usr/bin/env python3
"""First sediment event-time baseline. Python standard library only.

All ages are years before an arbitrary reference; larger means older.
See README.md for the probability law, sources, and unimplemented physics.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import random


def finite(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def mixed_fraction(focal: float, event: float, mixing: float) -> float:
    """P(material age <= event), integrating sedproxy Eq. 1, without truncation."""
    if not all(finite(x) for x in (focal, event, mixing)) or mixing < 0:
        raise ValueError("finite ages and nonnegative mixing time required")
    if mixing == 0:
        return float(focal <= event)
    z = (event - focal) / mixing + 1
    return -math.expm1(-z) if z > 0 else 0.0


@dataclass(frozen=True)
class Design:
    events: tuple[float, ...] = tuple(range(-100, 101, 25))
    mixing_times: tuple[float, ...] = (0.0, 25.0, 75.0)
    focal_ages: tuple[float, ...] = tuple(range(-200, 201, 25))
    specimens: int = 16
    old_probability: float = 0.1
    young_probability: float = 0.9

    def __post_init__(self):
        for name in ("events", "mixing_times", "focal_ages"):
            values = getattr(self, name)
            if not values or any(not finite(x) for x in values):
                raise ValueError(f"{name} must be finite and nonempty")
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} must be strictly increasing")
        if self.mixing_times[0] < 0:
            raise ValueError("mixing time cannot be negative")
        if type(self.specimens) is not int or self.specimens < 1:
            raise ValueError("positive integer specimen count required")
        if not 0 < self.old_probability < self.young_probability < 1:
            raise ValueError("response probabilities must satisfy 0 < old < young < 1")

    def states(self):
        # Independent uniform discrete priors. These are an exact finite model,
        # NOT numerical quadrature of a continuous prior.
        return tuple((event, mixing) for event in self.events for mixing in self.mixing_times)


@dataclass(frozen=True)
class Observation:
    focal_ages: tuple[float, ...]
    specimens: int
    positive_counts: tuple[int, ...]


def response(design: Design, focal: float, event: float, mixing: float) -> float:
    q = mixed_fraction(focal, event, mixing)
    return design.old_probability + (design.young_probability - design.old_probability) * q


def simulate(design: Design, event: float, mixing: float, rng: random.Random) -> Observation:
    """Draw actual independent material ages, then noisy binary proxy responses.

    Unlike inference, the generator does not evaluate the integrated CDF.
    This provides a separate implementation of the observation law.
    """
    if not finite(event) or not finite(mixing) or mixing < 0:
        raise ValueError("invalid event or mixing time")
    counts = []
    for focal in design.focal_ages:
        count = 0
        for _ in range(design.specimens):
            age = focal if mixing == 0 else focal - mixing + rng.expovariate(1 / mixing)
            p = design.young_probability if age <= event else design.old_probability
            count += rng.random() < p
        counts.append(count)
    return Observation(design.focal_ages, design.specimens, tuple(counts))


def validate_observation(design: Design, obs: Observation):
    if obs.focal_ages != design.focal_ages or obs.specimens != design.specimens:
        raise ValueError("observation does not match declared sampling design")
    if len(obs.positive_counts) != len(obs.focal_ages):
        raise ValueError("one count per focal age required")
    if any(type(k) is not int or not 0 <= k <= obs.specimens for k in obs.positive_counts):
        raise ValueError("counts must be integers within specimen count")


def normalize(log_weights):
    top = max(log_weights)
    weights = [math.exp(w - top) for w in log_weights]
    total = math.fsum(weights)
    return tuple(w / total for w in weights)


def posterior(design: Design, obs: Observation):
    """Exact joint (event, mixing) posterior; receives no simulated truth."""
    validate_observation(design, obs)
    log_weights = []
    for event, mixing in design.states():
        terms = []
        for focal, k in zip(obs.focal_ages, obs.positive_counts):
            p = response(design, focal, event, mixing)
            # Binomial coefficients cancel across states, so omit them here.
            terms.append(k * math.log(p) + (obs.specimens - k) * math.log1p(-p))
        log_weights.append(math.fsum(terms))
    return normalize(log_weights)


def event_marginal(design: Design, weights):
    n = len(design.mixing_times)
    return tuple(math.fsum(weights[i * n:(i + 1) * n]) for i in range(len(design.events)))


def quantile(values, weights, probability):
    cumulative = 0.0
    for value, weight in zip(values, weights):
        cumulative += weight
        if cumulative >= probability:
            return value
    return values[-1]


def poisson_change_point(counts, early_rate_prior=1.0, late_rate_prior=1.0):
    """Stan User's Guide change-point law, rates integrated analytically.

    s is 1..T; observations t<s have early rate, t>=s late rate.
    Each rate has its own exponential prior (Gamma shape=1, rate=r).
    """
    if not counts or any(type(k) is not int or k < 0 for k in counts):
        raise ValueError("nonempty nonnegative integer counts required")
    if any(not finite(r) or r <= 0 for r in (early_rate_prior, late_rate_prior)):
        raise ValueError("positive finite exponential prior rates required")

    def integrated(total, n, rate):
        # Constants prod(1/k!) and uniform(s) cancel across change points.
        return math.log(rate) + math.lgamma(total + 1) - (total + 1) * math.log(rate + n)

    total = sum(counts)
    prefix = 0
    log_weights = []
    for before in range(len(counts)):
        log_weights.append(integrated(prefix, before, early_rate_prior)
                           + integrated(total - prefix, len(counts) - before, late_rate_prior))
        prefix += counts[before]
    return normalize(log_weights)


def ks_uniform(values):
    values = sorted(values)
    n = len(values)
    return max(max((i + 1) / n - u, u - i / n) for i, u in enumerate(values))


def calibration(trials=2000, seed=20261124, ignore_mixing=False, prior_only=False,
                continuous_truth=False):
    """Own-law randomized posterior CDF check, or explicitly wrong control.

    Uniform PIT is an exact identity for this finite prior-predictive law.
    Randomization over each atom is essential for a discrete event time.
    """
    if type(trials) is not int or not 1 <= trials <= 100000:
        raise ValueError("trials must be an integer from 1 to 100000")
    if sum((ignore_mixing, prior_only, continuous_truth)) > 1:
        raise ValueError("select only one negative control")
    design = Design()
    fitted = Design(mixing_times=(0.0,)) if ignore_mixing else design
    # Keep truth, specimen, and diagnostic randomness separate. No held-out
    # seed is used or claimed here; this is a development verification run.
    truth_rng = random.Random(seed)
    specimen_rng = random.Random(seed + 1)
    diagnostic_rng = random.Random(seed + 2)
    bins = [0] * 10
    pits = []
    covered = 0
    posterior_mass = []
    errors = []
    widths = []
    information = []
    conditional_pits = {"below_half_positive": [], "at_least_half_positive": []}
    for _ in range(trials):
        event = (truth_rng.uniform(design.events[0], design.events[-1]) if continuous_truth
                 else truth_rng.choice(design.events))
        mixing = truth_rng.choice(design.mixing_times)
        obs = simulate(design, event, mixing, specimen_rng)
        marginal = ((1 / len(design.events),) * len(design.events) if prior_only
                    else event_marginal(fitted, posterior(fitted, obs)))
        below = math.fsum(p for t, p in zip(design.events, marginal) if t < event)
        equal = math.fsum(p for t, p in zip(design.events, marginal) if t == event)
        pit = below + diagnostic_rng.random() * equal
        pits.append(pit)
        group = ("below_half_positive" if 2 * sum(obs.positive_counts)
                 < obs.specimens * len(obs.focal_ages) else "at_least_half_positive")
        conditional_pits[group].append(pit)
        bins[min(int(pit * 10), 9)] += 1
        lo = quantile(design.events, marginal, 0.05)
        hi = quantile(design.events, marginal, 0.95)
        covered += lo <= event <= hi
        posterior_mass.append(math.fsum(p for t, p in zip(design.events, marginal) if lo <= t <= hi))
        errors.append(quantile(design.events, marginal, 0.5) - event)
        widths.append(hi - lo)
        # KL(posterior event || event prior), natural-log units.
        information.append(math.fsum(p * math.log(p * len(design.events)) for p in marginal if p))
    d = ks_uniform(pits)
    # DKW bound: simultaneous CDF band with failure probability <= .01.
    bound = math.sqrt(math.log(200) / (2 * trials))
    # For discrete intervals the prior-predictive coverage target is their
    # mean actual posterior mass, usually above .90, not exactly .90.
    coverage = covered / trials
    target = math.fsum(posterior_mass) / trials
    groups = {}
    for group, values in conditional_pits.items():
        if not values:
            groups[group] = {"trials": 0, "pit_ks": None, "pit_within_band": None}
            continue
        distance = ks_uniform(values)
        group_bound = math.sqrt(math.log(200) / (2 * len(values)))
        groups[group] = {"trials": len(values), "pit_ks": distance,
                         "pit_99_percent_dkw_bound": group_bound,
                         "pit_within_band": distance <= group_bound}
    return {
        "law": ("prior-only defective inference control" if prior_only else
                "continuous-event misspecification control" if continuous_truth else
                "ignored-mixing negative control" if ignore_mixing else "own prior-predictive"),
        "trials": trials, "seed": seed, "pit_bins": bins,
        "pit_ks": d, "pit_99_percent_dkw_bound": bound, "pit_within_band": d <= bound,
        "interval_coverage": coverage, "interval_mean_posterior_mass": target,
        "coverage_minus_mass": coverage - target,
        "median_error_mean_years": math.fsum(errors) / trials,
        "interval_width_mean_years": math.fsum(widths) / trials,
        "event_information_mean_nats": math.fsum(information) / trials,
        "data_conditional_pit": groups,
        "numerical_failures": 0,
    }


def experiment(trials=2000, seed=20261124):
    design = Design()
    counts = (8, 7, 9, 6, 8, 1, 0, 2, 1, 0)
    cp = poisson_change_point(counts)
    return {
        "version": 1,
        "scope": "single archive; exact finite prior; known age-depth; binary specimen proxy",
        "design": {"events_years_bp": design.events, "mixing_times_years": design.mixing_times,
                   "focal_ages_years_bp": design.focal_ages, "specimens_per_layer": design.specimens,
                   "old_probability": design.old_probability, "young_probability": design.young_probability},
        "mixing_check": {"depth_cm": 10, "accumulation_cm_per_kyr": 50,
                         "mixing_time_years": 200,
                         "cdf_at_focal": mixed_fraction(1000, 1000, 200),
                         "apparent_midpoint_older_offset_years": 200 * (1 - math.log(2))},
        "poisson_synthetic_example": {"counts": counts, "exponential_prior_rates": [1, 1],
                                      "s_support": list(range(1, len(counts) + 1)),
                                      "posterior": cp, "mode": 1 + cp.index(max(cp))},
        "calibration": calibration(trials, seed),
        "negative_control": calibration(trials, seed, ignore_mixing=True),
        "prior_only_control": calibration(trials, seed, prior_only=True),
        "continuous_event_control": calibration(trials, seed, continuous_truth=True),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261124)
    args = parser.parse_args()
    print(json.dumps(experiment(args.trials, args.seed), indent=2, allow_nan=False))
