"""Finite-horizon union bound for the reconstructed stationary OU supply guard.

This bounds one failure component, not solver or abundance failures. All
interpolated values are convex combinations of endpoints. No time independence
is assumed. See SUPPLY_GUARD.md; no new ecological trajectory is drawn.
"""
import math

import numpy as np
from scipy.special import log_ndtr, logsumexp


def guard_bound(duration, spacing, means, amplitude=.1):
    means = np.asarray(means, dtype=float)
    if (not np.isfinite([duration, spacing, amplitude]).all() or
        duration <= 0 or spacing <= 0 or amplitude <= 0 or
        means.ndim != 1 or len(means) == 0 or not np.isfinite(means).all()):
        raise ValueError('need finite positive duration, spacing and amplitude, and finite resource means')
    steps = round(duration/spacing)
    if steps < 1 or not math.isclose(steps*spacing, duration, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError('duration must be a multiple of spacing')
    nodes = steps+1
    # Every node has stationary variance amplitude²/2, including bridged nodes.
    log_marginals = log_ndtr(-means/(amplitude/np.sqrt(2)))
    log_upper = min(0., math.log(nodes)+float(logsumexp(log_marginals)))
    # The union contains each one-node event, giving a simple lower bound.
    log_lower = float(np.max(log_marginals))
    return dict(nodes=nodes, resources=len(means), amplitude=amplitude,
                log_probability_lower=log_lower, log_probability_upper=log_upper,
                probability_lower=float(np.exp(log_lower)),
                probability_upper=float(np.exp(log_upper)),
                scope='stationary endpoint/interpolated supply guard only; floating-point union bound')


if __name__ == '__main__':
    import json
    means = np.r_[np.ones(24), np.full(6, 3.)]
    print(json.dumps([dict(duration=t, spacing=h, **guard_bound(t, h, means))
                      for t, h in ((8704, 1/32), (66048, 1/32), (66048, 1/64))], indent=2))
