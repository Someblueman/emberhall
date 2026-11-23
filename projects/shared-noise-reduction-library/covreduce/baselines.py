"""Baseline comparisons for the first-order covariance contract.

Baselines are deliberately simple and independent of the sparse-Jacobian
engine: diagonal (independent-variance) propagation, seeded Monte Carlo,
an ESSreduce-style subspace-volume upper bound, a dense gvar-equivalent
propagation for scalar linear combinations, and an RME-style ellipse
mechanism attribution for two-output programs.
"""
from __future__ import annotations

import math
import random

from .core import CovArray


def _cholesky(matrix):
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            value = matrix[i][j] - sum(lower[i][k] * lower[j][k]
                                        for k in range(j))
            if i == j:
                lower[i][j] = math.sqrt(max(value, 0.0))
            else:
                lower[i][j] = value / lower[j][j] if lower[j][j] else 0.0
    return lower


def monte_carlo_covariance(arrays, program, *, draws=4000, seed=20261122):
    """Sample primitives jointly (repeated sources share one draw)."""
    arrays = list(arrays)
    blocks, seen = [], {}
    for array in arrays:
        if not array._primitive or array._source is None:
            raise ValueError("Monte Carlo inputs must be primitive sources")
        if id(array._source) not in seen:
            seen[id(array._source)] = len(blocks)
            blocks.append(array)
    rng = random.Random(seed)
    factors = []
    for array in blocks:
        src = array._source
        matrix = [[src.covariance[p * src.size + q] for q in range(src.size)]
                  for p in range(src.size)]
        factors.append(_cholesky(matrix))
    samples = []
    for _ in range(draws):
        drawn = []
        for array, factor in zip(blocks, factors):
            z = [rng.gauss(0.0, 1.0) for _ in range(array.size)]
            drawn.append([m + sum(factor[i][k] * z[k] for k in range(i + 1))
                          for i, m in enumerate(array.values)])
        flat = [drawn[seen[id(a._source)]] for a in arrays]
        out = program(flat)
        samples.append(list(out))
    n = len(samples[0])
    means = [sum(s[i] for s in samples) / draws for i in range(n)]
    return [[sum((s[i] - means[i]) * (s[j] - means[j]) for s in samples)
             / (draws - 1) for j in range(n)] for i in range(n)]


def independent_variance_covariance(covarray):
    """Covariance if every primitive element were (wrongly) independent."""
    out = [[0.0] * covarray.size for _ in range(covarray.size)]
    for src, rows in covarray._jacobians.items():
        for i in range(covarray.size):
            for j in range(covarray.size):
                for p, jp in rows[i].items():
                    jq = rows[j].get(p)
                    if jq is not None:
                        out[i][j] += jp * src.covariance[p * src.size + p] * jq
    return out


def essreduce_upper_bound(covarray, weights):
    """Subspace-volume style upper bound on ``w^T C w``.

    Treats each primitive block as an ellipsoid and bounds the quadratic
    form by the sum of per-block spectral bounds.  This is an upper bound
    in the spirit of ESSreduce, never an equality claim.
    """
    total = 0.0
    weights = list(weights)
    for src, rows in covarray._jacobians.items():
        contracted = [0.0] * src.size
        for w, row in zip(weights, rows):
            for p, jp in row.items():
                contracted[p] += w * jp
        radius = max(abs(src.covariance[p * src.size + q])
                     for p in range(src.size) for q in range(src.size))
        total += radius * sum(abs(v) for v in contracted) ** 2
    return total


def gvar_equivalent_variance(terms):
    """Dense correlated propagation for ``sum(coef * scalar_source)``.

    ``terms`` is a list of ``(coefficient, CovArray scalar)``.  Mirrors what
    a dense gvar-style graph computes: explicit sum over shared primitives.
    """
    total = 0.0
    for coef_a, arr_a in terms:
        for coef_b, arr_b in terms:
            for src, rows_a in arr_a._jacobians.items():
                rows_b = arr_b._jacobians.get(src)
                if rows_b is None:
                    continue
                for p, jp in rows_a[0].items():
                    for q, jq in rows_b[0].items():
                        total += (coef_a * coef_b * jp
                                  * src.covariance[p * src.size + q] * jq)
    return total


def rme_ellipse_attribution(covarray):
    """RME-style mechanism attribution for a two-output result.

    Returns the 1-sigma error-ellipse area of the full correlated output,
    the area under the (wrong) independent assumption, and each primitive
    source's share of the total variance trace.  This is an honest local
    implementation of the ellipse idea, not the external ``rmellipse``
    package; availability of that package is reported separately by
    :func:`rmellipse_available`.
    """
    if covarray.size != 2:
        raise ValueError("ellipse attribution needs exactly two outputs")
    cov = covarray.covariance()
    det = cov[0][0] * cov[1][1] - cov[0][1] ** 2
    indep = independent_variance_covariance(covarray)
    det_i = indep[0][0] * indep[1][1] - indep[0][1] ** 2
    shares, trace = [], cov[0][0] + cov[1][1]
    for index, (src, rows) in enumerate(covarray._jacobians.items()):
        block = 0.0
        for i in range(2):
            for p, jp in rows[i].items():
                for q, jq in rows[i].items():
                    block += jp * src.covariance[p * src.size + q] * jq
        shares.append((index, block / trace if trace else 0.0))
    return {
        "ellipse_area": math.pi * math.sqrt(max(det, 0.0)),
        "independent_ellipse_area": math.pi * math.sqrt(max(det_i, 0.0)),
        "correlation": cov[0][1] / math.sqrt(cov[0][0] * cov[1][1])
        if cov[0][0] > 0 and cov[1][1] > 0 else 0.0,
        "source_trace_shares": shares,
    }


def rmellipse_available():
    try:
        import rmellipse  # noqa: F401
        return True
    except ImportError:
        return False
