"""Prospective bounded population envelopes for fixed paired refinements.

Input is one independent community per row, with a fixed number of input
paths nested inside each community. No existing development result gains
validation coverage from this instrument. See RESOLUTION_PRECISION.md.
"""
import math

import numpy as np

from bounded_precision import confidence_sequence


def zero_sample_necessary_count(radius, epsilon, alpha):
    """Fixed-n lower bound, not a sufficient ecological sample size.

    Bernoulli contamination at the score-range endpoint proves the bound.
    See RESOLUTION_PRECISION.md. Assumes a deterministic upper interval.
    """
    if not np.isfinite([radius, epsilon, alpha]).all() or not 0 < epsilon < radius or not 0 < alpha < 1:
        raise ValueError('need 0 < epsilon < radius and 0 < alpha < 1')
    return math.ceil(math.log(alpha)/math.log1p(-epsilon/radius))


def _bounds(bounds):
    low, high = bounds
    if not np.isfinite([low, high]).all() or not low < high:
        raise ValueError('need finite increasing score bounds')
    return float(low), float(high)


def _score(value, bounds):
    low, high = bounds
    if value is None:
        return low, high
    if isinstance(value, bool) or not isinstance(value, (int, float, np.number)):
        raise ValueError('score must be a real number or None for failure')
    if not np.isfinite(value) or not low <= value <= high:
        raise ValueError('score outside declared bounds')
    return float(value), float(value)


def path_envelopes(primary, comparator, bounds):
    """Sharp score and absolute-difference envelopes, retaining failed paths."""
    bounds = _bounds(bounds)
    a, b = _score(primary, bounds), _score(comparator, bounds)
    least = max(0., a[0]-b[1], b[0]-a[1])
    most = max(abs(a[0]-b[1]), abs(a[1]-b[0]))
    return a, (least, most)


def community_envelopes(paths, bounds, path_count):
    """Average paired diagnostics within one community, never across pairs."""
    if not isinstance(path_count, int) or isinstance(path_count, bool) or path_count < 1:
        raise ValueError('path count must be a positive integer fixed before data')
    paths = list(paths)
    if len(paths) != path_count:
        raise ValueError('missing/extra path; represent failures explicitly with None')
    scores, deltas = zip(*(path_envelopes(a, b, bounds) for a, b in paths))
    return (tuple(math.fsum(x[i] for x in scores)/path_count for i in (0, 1)),
            tuple(math.fsum(x[i] for x in deltas)/path_count for i in (0, 1)))


def envelope_interval(envelopes, bounds, alpha):
    """Time-uniform outer interval for every bounded completion's mean.

    Use alpha/2 for each endpoint process, even with no observed failures.
    Endpoints are observable iid community functions under a fixed design.
    """
    low, high = _bounds(bounds)
    if not 0 < alpha < 1:
        raise ValueError('alpha must be strictly between zero and one')
    observations = np.asarray(list(envelopes), dtype=float)
    if observations.size == 0:
        return [low, high]
    if (observations.ndim != 2 or observations.shape[1] != 2 or
        not np.isfinite(observations).all() or
        np.any(observations[:, 0] > observations[:, 1]) or
        np.any(observations < low) or np.any(observations > high)):
        raise ValueError('invalid completion envelope')
    normalized = (observations-low)/(high-low)
    lower = confidence_sequence(normalized[:, 0], alpha/2)[0]
    upper = confidence_sequence(normalized[:, 1], alpha/2)[1]
    return [low+(high-low)*lower, low+(high-low)*upper]


def paired_population(rows, bounds, path_count, *, family_size, family_alpha=.05):
    """Intervals for one target in a predeclared family of paired studies.

    family_size counts score-mean and absolute-difference targets separately.
    For 12 score targets and 3 refinement comparisons it is 48. This call
    handles only one comparison; callers must retain the same community order,
    settings and failure policy across the fixed family, without selection.
    """
    bounds = _bounds(bounds)
    if not isinstance(family_size, int) or isinstance(family_size, bool) or family_size < 2:
        raise ValueError('family must include both reported targets')
    if not 0 < family_alpha < 1:
        raise ValueError('invalid family error probability')
    scores, deltas = [], []
    for paths in rows:
        a, b = community_envelopes(paths, bounds, path_count)
        scores.append(a)
        deltas.append(b)
    alpha = family_alpha/family_size
    return dict(communities=len(scores), paths_per_community=path_count,
                score_mean=envelope_interval(scores, bounds, alpha),
                mean_absolute_difference=envelope_interval(deltas, (0., bounds[1]-bounds[0]), alpha),
                family_size=family_size, family_alpha=family_alpha,
                scope='prospective fixed-design completion means; no stationary or continuum guarantee')


if __name__ == '__main__':
    import argparse
    import csv
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Constant-score mathematical budget controls; no ecological data')
    parser.add_argument('--controls-output', type=Path, required=True)
    args = parser.parse_args()
    records = []
    for n in (12, 48, 96, 192, 384, 768, 1536, 3072, 6144):
        result = paired_population([[(.8, .8)]]*n, (-1., 1.), 1, family_size=48)
        records.append(dict(communities=n, rank_mean_lower=result['score_mean'][0],
                            rank_mean_upper=result['score_mean'][1],
                            zero_rank_difference_upper=result['mean_absolute_difference'][1]))
    with args.controls_output.open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print('Controls only; necessary zero-sample rank counts:',
          zero_sample_necessary_count(2., .005, .05/48),
          zero_sample_necessary_count(2., .005, .05/96))
