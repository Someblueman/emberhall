"""Anytime bounded-mean confidence sequences for a future fresh-community study.

These do not repair post-selection coverage in existing development results.
See FRESH_PRECISION.md for the martingale argument and scientific prerequisites.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

FRACTIONS = np.array([.01, .03, .1, .2, .4, .7, .9, .99])


def _observations(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all() or np.any((values < 0) | (values > 1)):
        raise ValueError('need finite observations in [0, 1]')
    return values


def log_wealth(mean, values):
    """Log of an equally weighted, two-sided mixture of bounded betting wealth."""
    values = _observations(values)
    if not 0 <= mean <= 1:
        raise ValueError('mean must be in [0, 1]')
    n = len(values)
    if mean == 0:
        positive = np.full(len(FRACTIONS), np.inf) if np.any(values > 0) else n*np.log1p(-FRACTIONS)
    else:
        positive = np.log1p(FRACTIONS[:, None]*(values/mean-1)).sum(axis=1)
    if mean == 1:
        negative = np.full(len(FRACTIONS), np.inf) if np.any(values < 1) else n*np.log1p(-FRACTIONS)
    else:
        negative = np.log1p(FRACTIONS[:, None]*((1-values)/(1-mean)-1)).sum(axis=1)
    return float(logsumexp(np.r_[positive, negative])-np.log(2*len(FRACTIONS)))


def confidence_sequence(values, alpha=.05):
    """One interval; simultaneous over every sample size under a fixed mean.

    Return conservative outer bisection endpoints of {m: wealth(m)<1/alpha}.
    The sample mean is inside this convex sublevel set by AM-GM.
    """
    values = _observations(values)
    if not 0 < alpha < 1:
        raise ValueError('alpha must be strictly between zero and one')
    if not len(values):
        return [0., 1.]
    middle = float(values.mean())
    threshold = -np.log(alpha)
    lower, upper = 0., 1.
    if log_wealth(0, values) > threshold:
        outside, inside = 0., middle
        for _ in range(55):
            point = (outside+inside)/2
            if log_wealth(point, values) > threshold:
                outside = point
            else:
                inside = point
        lower = max(0., outside-1e-12)
    if log_wealth(1, values) > threshold:
        inside, outside = middle, 1.
        for _ in range(55):
            point = (inside+outside)/2
            if log_wealth(point, values) > threshold:
                outside = point
            else:
                inside = point
        upper = min(1., outside+1e-12)
    return [lower, upper]


def completion_interval(values, bounds, alpha=.05):
    """Enclose means of every bounded completion of failed observations (None).

    Split alpha between lower and upper completion processes *in advance*.
    For a family of targets pass alpha/family; do not pool species pairs.
    """
    low, high = bounds
    if not np.isfinite([low, high]).all() or not low < high:
        raise ValueError('need finite increasing bounds')
    lower = [(low if x is None else x) for x in values]
    upper = [(high if x is None else x) for x in values]
    a = confidence_sequence((np.array(lower)-low)/(high-low), alpha/2)[0]
    b = confidence_sequence((np.array(upper)-low)/(high-low), alpha/2)[1]
    return [low+(high-low)*a, low+(high-low)*b]


def controls():
    """Analytical constant-score controls, not simulated ecological evidence."""
    records = []
    for n in (12, 24, 48, 96, 192, 384, 768):
        row = dict(communities=n)
        for name, value, bounds in [('rank_0_8', .8, (-1., 1.)),
                                    ('auc_0_98', .98, (0., 1.)),
                                    ('perfect_auc', 1., (0., 1.))]:
            ci = completion_interval([value]*n, bounds, .05/12)
            row[name] = dict(interval=ci, half_width=(ci[1]-ci[0])/2)
        records.append(row)
    return dict(scope='constant-score numerical controls only, no ecological population or sample-size guarantee',
                family_targets=12, family_alpha=.05,
                fractions=FRACTIONS.tolist(), controls=records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls-output', required=True, type=Path)
    args = parser.parse_args()
    result = controls()
    args.controls_output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for row in result['controls']:
        print(row['communities'], {k: round(v['half_width'], 4) for k, v in row.items() if k != 'communities'})
