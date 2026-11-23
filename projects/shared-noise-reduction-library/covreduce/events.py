"""Streaming event-to-bin reduction with shared covariance sources.

Events arrive as an iterable of mappings with ``bin`` (integer index),
optional ``weight``, ``variance`` and ``group``.  Per-event variances are
independent; group scale factors, the monitor and the background are shared
primitive sources, so their covariance is preserved exactly to first order
without materialising per-event Jacobians.
"""
from __future__ import annotations

import time
import tracemalloc

from .core import CovArray, UnsupportedOperationError, source


def reduce_events_to_bins(events, n_bins, *, group_scales=None, monitor=None,
                          background=None, bin_edges=None, dims=("bin",)):
    """Reduce an event stream to a binned :class:`CovArray`.

    ``group_scales`` maps a group label to a scalar primitive CovArray.
    ``monitor`` is a shared scalar normalisation source; ``background`` is a
    shared per-bin source subtracted after binning.  Uncertain bin edges
    are rejected: under ``first_order_linear`` an event's bin membership
    must be exact.
    """
    if bin_edges is not None:
        raise UnsupportedOperationError(
            "uncertain bin edges are discontinuous under first_order_linear; "
            "assign exact integer bins instead")
    totals = [0.0] * n_bins
    variances = [0.0] * n_bins
    scale_forms: dict[object, list[float]] = {}
    group_scales = group_scales or {}
    for event in events:
        idx = event["bin"]
        if type(idx) is not int:
            raise TypeError("event bin must be an exact integer")
        if not 0 <= idx < n_bins:
            raise IndexError("event bin out of range")
        weight = float(event.get("weight", 1.0))
        variance = float(event.get("variance", 0.0))
        group = event.get("group")
        scale = 1.0
        if group is not None:
            scale_value = group_scales[group].value
            form = scale_forms.setdefault(group, [0.0] * n_bins)
            form[idx] += weight
            scale = scale_value
        totals[idx] += scale * weight
        variances[idx] += (scale * scale) * variance
    coords = dict(background.coords) if background is not None else None
    independent = source(totals, variances, dims=dims, coords=coords)
    result = independent
    for group, form in scale_forms.items():
        # First-order correction as a linear map of the group primitive:
        # totals used the scale's central value; add form * (scale - value)
        # by attaching Jacobian rows directly to its primitive source.
        primitive = group_scales[group]
        rows = tuple({0: form[i]} if form[i] else {} for i in range(n_bins))
        delta = CovArray._from_parts((0.0,) * n_bins, (n_bins,), tuple(dims),
                                     dict(independent.coords),
                                     {primitive._source: rows})
        result = result + delta
    if monitor is not None:
        result = result / monitor
    if background is not None:
        result = result - background
    return result


def benchmark_100k_events(n_events=100_000, n_bins=128):
    """Frozen-scale streaming benchmark (tracemalloc peak, wall time)."""
    def stream():
        for i in range(n_events):
            yield {"bin": i % n_bins, "weight": 1.0 + (i % 7) * 0.01,
                   "variance": 0.25, "group": i % 4}
    # Measure from before source construction so the peak includes setup.
    tracemalloc.start()
    scales = {g: source(1.0 + 0.01 * g, 0.0004) for g in range(4)}
    monitor = source(1000.0, 25.0)
    background = source([0.5] * n_bins, [0.01] * n_bins, dims=("bin",))
    start = time.perf_counter()
    result = reduce_events_to_bins(stream(), n_bins, group_scales=scales,
                                   monitor=monitor, background=background)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"events": n_events, "bins": n_bins, "seconds": elapsed,
            "peak_bytes": peak, "first_bin_value": result.values[0],
            "total_variance": sum(result.variance)}
