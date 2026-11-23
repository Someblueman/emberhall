"""covreduce: first-order covariance propagation over labelled arrays.

Standard library only, Python 3.10+.  Import the package and compose:

    from covreduce import source
    monitor = source(1000.0, 25.0)
    counts = source([120.0, 80.0], [12.0, 9.0], dims=("bin",))
    rates = counts / monitor
    rates.covariance()  # keeps the shared-monitor cross terms
"""
from .core import (
    CovArray, DimensionMismatchError, UnsupportedOperationError, constant,
    moving_window, quadratic_form, rebin, reduce_mean, reduce_sum,
    reorder_dims, select, source,
)
from .oracle import dense_jcjt_oracle, max_covariance_difference

__all__ = [
    "CovArray", "DimensionMismatchError", "UnsupportedOperationError",
    "constant", "dense_jcjt_oracle", "max_covariance_difference",
    "moving_window", "quadratic_form", "rebin", "reduce_mean",
    "reduce_sum", "reorder_dims", "select", "source",
]
__version__ = "0.1.0"
