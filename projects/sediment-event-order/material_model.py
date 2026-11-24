#!/usr/bin/env python3
"""Finite-layer mixing and explicit shared specimen ancestry.

Synthetic linear age measurements only: NOT radiocarbon or calibration.
No chronology inference is performed. See MATERIAL_MODEL.md.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import random

from baseline import finite, mixed_fraction, normalize, ks_uniform


def layer_fraction(focal, event, mixing, half_width):
    """CDF of focal + Uniform(-L,L) - h + Exp(mean=h). Units: years."""
    if not all(finite(x) for x in (focal, event, mixing, half_width)):
        raise ValueError("finite arguments required")
    if mixing < 0 or half_width < 0:
        raise ValueError("mixing time and layer half-width cannot be negative")
    if half_width == 0:
        return mixed_fraction(focal, event, mixing)
    if mixing == 0:
        return min(1.0, max(0.0, (event - focal + half_width) / (2 * half_width)))
    z = event - focal + mixing
    if z <= -half_width:
        return 0.0
    if z > half_width:
        u = 2 * (half_width / mixing)
        # Log of (1-exp(-u))/u, with its removable singularity handled
        # analytically. Unlike subtracting two large CDF primitives this
        # remains stable far into the older tail and as layer width vanishes.
        if u < 1e-4:
            log_ratio = -u / 2 + u * u / 24 - u ** 4 / 2880 + u ** 6 / 181440
        else:
            log_ratio = math.log(-math.expm1(-u) / u) if math.isfinite(u) else -math.inf
        return -math.expm1(-(z - half_width) / mixing + log_ratio)

    def primitive(x):
        if x <= 0:
            return 0.0
        u = x / mixing
        # Integrate 1-exp(-u). Avoid cancellation near the support boundary.
        if u < 1e-4:
            return mixing * u * u * (.5 - u / 6 + u * u / 24 - u ** 3 / 120 + u ** 4 / 720)
        return x + mixing * math.expm1(-u)

    value = primitive(z + half_width) / (2 * half_width)
    return min(1.0, max(0.0, value))


def material_age(focal, mixing, half_width, rng):
    if not all(finite(x) for x in (focal, mixing, half_width)) or min(mixing, half_width) < 0:
        raise ValueError("finite focal age and nonnegative mixing and half-width required")
    offset = rng.uniform(-half_width, half_width) if half_width else 0.0
    return focal + offset + (rng.expovariate(1 / mixing) - mixing if mixing else 0.0)


@dataclass(frozen=True)
class Specimen:
    identifier: str
    true_age: float
    positive: bool | None
    measured_age: float | None


@dataclass(frozen=True)
class Sample:
    depth_cm: float
    dating_sigma_years: float
    specimens: tuple[Specimen, ...]

    def observed(self):
        """Explicit allowlist export; no nominal/true age or climate parameters."""
        return {"depth_cm": self.depth_cm, "dating_sigma_years": self.dating_sigma_years,
                "proxy_measurements": [{"specimen_id": s.identifier, "positive": s.positive}
                                       for s in self.specimens if s.positive is not None],
                "date_measurements": [{"specimen_id": s.identifier, "measured_age": s.measured_age}
                                      for s in self.specimens if s.measured_age is not None]}

    def means(self):
        proxy = [s.positive for s in self.specimens if s.positive is not None]
        dates = [s.measured_age for s in self.specimens if s.measured_age is not None]
        return math.fsum(proxy) / len(proxy), math.fsum(dates) / len(dates)


def draw_sample(*, depth_cm, focal, event, mixing, half_width, proxy_count, date_count,
                overlap, dating_sigma, age_rng, proxy_rng, date_rng, prefix="layer"):
    """Fresh distinct specimens, except the explicitly shared overlap.

    Proxy and dating noise are conditionally independent given material age.
    Pool allocation is fixed by design, never selected by proxy or true age.
    """
    if not all(finite(x) for x in (depth_cm, focal, event, mixing, half_width, dating_sigma)):
        raise ValueError("finite design values required")
    if min(mixing, half_width, dating_sigma) < 0:
        raise ValueError("nonnegative mixing, width and noise required")
    if any(type(n) is not int for n in (proxy_count, date_count, overlap)):
        raise ValueError("integer specimen counts required")
    if min(proxy_count, date_count) < 1 or not 0 <= overlap <= min(proxy_count, date_count):
        raise ValueError("positive sample counts and valid overlap required")
    if proxy_count + date_count - overlap > 100000:
        raise ValueError("at most 100000 unique specimens per layer")
    if not isinstance(prefix, str) or not prefix or any(ord(c) < 32 for c in prefix):
        raise ValueError("nonempty printable specimen prefix required")
    specimens = []
    for role, count in (("shared", overlap), ("proxy", proxy_count - overlap),
                        ("date", date_count - overlap)):
        for index in range(count):
            age = material_age(focal, mixing, half_width, age_rng)
            positive = (proxy_rng.random() < (.9 if age <= event else .1)
                        if role != "date" else None)
            measured = age + date_rng.gauss(0, dating_sigma) if role != "proxy" else None
            specimens.append(Specimen(f"{prefix}:{role}:{index}", age, positive, measured))
    return Sample(depth_cm, dating_sigma, tuple(specimens))


def zero_width_covariance(focal, event, mixing, proxy_count, date_count, overlap):
    """Cov(mean binary proxy, mean synthetic date), conditional on focal/tau/h.

    Only L=0. Independent zero-mean dating noise does not change covariance.
    """
    if any(type(n) is not int for n in (proxy_count, date_count, overlap)):
        raise ValueError("integer counts required")
    if min(proxy_count, date_count) < 1 or not 0 <= overlap <= min(proxy_count, date_count):
        raise ValueError("invalid counts")
    if not all(finite(x) for x in (focal, event, mixing)) or mixing < 0:
        raise ValueError("invalid ages or mixing time")
    if mixing == 0:
        return 0.0
    z = (event - focal) / mixing + 1
    if z <= 0 or z > 745:
        return 0.0
    return -.8 * mixing * (z * math.exp(-z)) * overlap / (proxy_count * date_count)


def mills_denominator(z):
    denominator = z
    for k in range(40, 0, -1):
        denominator = z + k / denominator
    return denominator


def normal_log_survival(z):
    """Log P(N(0,1)>z), including the far positive tail.

    Laplace's Mills-ratio continued fraction avoids erfc underflow. Forty
    terms are used only at z>=8 and checked against erfc in their overlap.
    """
    if not finite(z):
        raise ValueError("finite standardized normal argument required")
    if z < 8:
        return math.log(.5 * math.erfc(z / math.sqrt(2)))
    return -.5 * z * z - .5 * math.log(2 * math.pi) - math.log(mills_denominator(z))


def date_density_and_young_fraction(measured, focal, event, mixing, sigma):
    """L=0: log density of noisy material age and P(A<=event | measured).

    Completing the square yields an exponentially modified normal density
    and a lower-truncated normal conditional material age. sigma must be
    positive; noiseless dating introduces singular measures at h=0.
    """
    if not all(finite(x) for x in (measured, focal, event, mixing, sigma)) or mixing < 0 or sigma <= 0:
        raise ValueError("finite values, nonnegative mixing and positive dating sigma required")
    if mixing == 0:
        log_density = -.5 * ((measured - focal) / sigma) ** 2 - math.log(sigma * math.sqrt(2 * math.pi))
        return log_density, float(focal <= event)
    lower = focal - mixing
    r = (lower - measured) / sigma
    a = r + sigma / mixing
    log_tail = normal_log_survival(a)
    if a >= 8:
        # Complete cancellation algebraically, rather than subtracting two
        # terms of order (sigma/h)^2 as h approaches zero.
        log_density = (-.5 * r * r - .5 * math.log(2 * math.pi)
                       - math.log(mixing) - math.log(mills_denominator(a)))
    else:
        log_density = ((lower - measured) / mixing + .5 * (sigma / mixing) ** 2
                       - math.log(mixing) + log_tail)
    if event <= lower:
        return log_density, 0.0
    delta = (event - lower) / sigma
    b = a + delta
    if a >= 8:
        da, db = mills_denominator(a), mills_denominator(b)
        log_ratio = -a * delta - .5 * delta * delta - math.log1p((db - da) / da)
    else:
        log_ratio = normal_log_survival(b) - log_tail
    fraction = -math.expm1(min(0.0, log_ratio))
    return log_density, fraction


def sample_log_likelihood(observed, *, focal, event, mixing, half_width):
    """Joint individual-measurement law, respecting shared specimen IDs.

    Only L=0 is implemented. A positive dating sigma is required. Candidate
    model parameters are explicit and are never recovered from simulation
    truth. Repeated IDs within either measurement list are rejected.
    """
    if half_width != 0:
        raise ValueError("joint date/proxy likelihood currently requires zero layer width")
    sigma = observed['dating_sigma_years']
    if not finite(sigma) or sigma <= 0:
        raise ValueError("joint likelihood requires positive finite dating noise")
    if not all(finite(x) for x in (focal, event, mixing)) or mixing < 0:
        raise ValueError("invalid candidate parameters")
    proxies, dates = {}, {}
    for row in observed['proxy_measurements']:
        key, value = row['specimen_id'], row['positive']
        if not isinstance(key, str) or not key or key in proxies or type(value) is not bool:
            raise ValueError("unique proxy IDs and boolean responses required")
        proxies[key] = value
    for row in observed['date_measurements']:
        key, value = row['specimen_id'], row['measured_age']
        if not isinstance(key, str) or not key or key in dates or not finite(value):
            raise ValueError("unique date IDs and finite measured ages required")
        dates[key] = value
    if not proxies or not dates:
        raise ValueError("at least one proxy and one dating measurement required")
    terms = []
    unconditioned = .1 + .8 * mixed_fraction(focal, event, mixing)
    for key in sorted(proxies.keys() | dates.keys()):
        if key in dates:
            log_density, young = date_density_and_young_fraction(dates[key], focal, event, mixing, sigma)
            terms.append(log_density)
            p = .1 + .8 * young
        else:
            p = unconditioned
        if key in proxies:
            terms.append(math.log(p) if proxies[key] else math.log1p(-p))
    return math.fsum(terms)


class Moments:
    """Online mean and variance of a scalar, without storing simulated trials."""
    def __init__(self):
        self.n, self.mean, self.m2 = 0, 0.0, 0.0

    def add(self, value):
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (value - self.mean)

    def standard_error(self):
        return math.sqrt(self.m2 / (self.n - 1) / self.n) if self.n > 1 else None


def covariance_check(trials=20000, seed=20261125):
    if type(trials) is not int or not 2 <= trials <= 1000000:
        raise ValueError("trials must be an integer from 2 to 1000000")
    result = []
    focal, event, mixing, count, dating_sigma = 1000, 1000, 75, 8, 20
    expected_proxy = .1 + .8 * mixed_fraction(focal, event, mixing)
    for overlap in (0, 4, 8):
        age_rng, proxy_rng, date_rng = (random.Random(seed + i) for i in range(3))
        products, proxies, dates = Moments(), Moments(), Moments()
        for _ in range(trials):
            sample = draw_sample(depth_cm=10, focal=focal, event=event, mixing=mixing,
                                 half_width=0, proxy_count=count, date_count=count,
                                 overlap=overlap, dating_sigma=dating_sigma, age_rng=age_rng,
                                 proxy_rng=proxy_rng, date_rng=date_rng)
            proxy, date = sample.means()
            products.add((proxy - expected_proxy) * (date - focal))
            proxies.add(proxy)
            dates.add(date)
        analytic = zero_width_covariance(focal, event, mixing, count, count, overlap)
        se = products.standard_error()
        result.append({"overlap": overlap, "analytic_covariance": analytic,
                       "estimated_covariance_known_centers": products.mean,
                       "estimated_product_standard_error": se,
                       "error_in_standard_errors": (products.mean - analytic) / se,
                       "proxy_mean": proxies.mean, "expected_proxy_mean": expected_proxy,
                       "date_mean": dates.mean, "expected_date_mean": focal})
    return {"trials_per_case": trials, "development_seed": seed,
            "model": "L=0; focal=event=1000; mixing=75; 8 proxy,8 dating; date noise sigma20",
            "cases": result,
            "warning": "Known-center covariance check; synthetic linear dates, not radiocarbon or chronology inference."}


def joint_calibration(trials=1000, seed=20261126):
    """Exact finite-prior joint-law development check, with a broken-ID control.

    Known focal ages are a chronology oracle. This is neither a continuous
    event-time approximation nor a held-out paired-archive experiment.
    """
    if type(trials) is not int or not 2 <= trials <= 10000:
        raise ValueError("joint calibration trials must be from 2 to 10000")
    events = tuple(range(900, 1101, 25))
    mixing_times = (0, 25, 75)
    focals = (900, 1000, 1100)
    states = tuple((event, mixing) for event in events for mixing in mixing_times)
    truth_rng, age_rng, proxy_rng, date_rng, pit_rng = (random.Random(seed + i) for i in range(5))
    pits = {'joint': [], 'ignore_shared_ids': []}
    score_gain = Moments()
    for _ in range(trials):
        event, mixing = truth_rng.choice(states)
        observed = []
        independent = []
        for i, focal in enumerate(focals):
            sample = draw_sample(depth_cm=i+1, focal=focal, event=event, mixing=mixing,
                                 half_width=0, proxy_count=4, date_count=4, overlap=4,
                                 dating_sigma=20, age_rng=age_rng, proxy_rng=proxy_rng,
                                 date_rng=date_rng, prefix=f'layer-{i}')
            data = sample.observed()
            observed.append(data)
            independent.append(data | {'date_measurements':
                [row | {'specimen_id': 'unshared:' + row['specimen_id']} for row in data['date_measurements']]})
        scores = {}
        for name, data in (('joint', observed), ('ignore_shared_ids', independent)):
            log_weights = [math.fsum(sample_log_likelihood(row, focal=focal, event=tau,
                                    mixing=h, half_width=0) for focal, row in zip(focals, data))
                           for tau, h in states]
            weights = normalize(log_weights)
            marginal = tuple(math.fsum(weights[i*3:(i+1)*3]) for i in range(len(events)))
            index = events.index(event)
            pits[name].append(math.fsum(marginal[:index]) + pit_rng.random() * marginal[index])
            scores[name] = log_weights[states.index((event, mixing))]
        score_gain.add(scores['joint'] - scores['ignore_shared_ids'])
    band = math.sqrt(math.log(200) / (2 * trials))
    result = {}
    for name, values in pits.items():
        d = ks_uniform(values)
        result[name] = {'pit_ks': d, 'pit_99_percent_dkw_bound': band, 'pit_within_band': d <= band}
    return {'trials':trials, 'development_seed':seed, 'event_support':events,
            'mixing_support':mixing_times, 'known_focal_ages':focals,
            'specimens_per_measurement_per_layer':4, 'all_specimens_shared':True,
            'calibration':result, 'truth_log_score_gain_mean':score_gain.mean,
            'truth_log_score_gain_standard_error':score_gain.standard_error(),
            'warning':'Finite-prior check with known chronology; coarse event support is not a continuous time approximation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=int)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--joint-check', action='store_true')
    args = parser.parse_args()
    calculation = joint_calibration if args.joint_check else covariance_check
    trials = args.trials if args.trials is not None else (1000 if args.joint_check else 20000)
    seed = args.seed if args.seed is not None else (20261126 if args.joint_check else 20261125)
    print(json.dumps(calculation(trials, seed), indent=2, allow_nan=False))
