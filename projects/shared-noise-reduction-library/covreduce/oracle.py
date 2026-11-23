"""Independent dense J C J^T oracle.

This module shares no propagation code with :mod:`covreduce.core`.  A program
written against a small array API is re-executed here on ``_DualArray``
objects that carry a dense Jacobian with respect to every element of every
*unique* primitive source.  The result covariance is the explicit dense
product ``J C J^T`` over the concatenated primitive covariance blocks.

Contract (tightened after the Stage-1 independent audit):

* Passing the same primitive source more than once combines it into one
  covariance block, so ``dense_jcjt_oracle([x, x], lambda a: a[0] - a[1])``
  is exactly zero, matching the library.
* Derived (non-primitive) arrays are rejected instead of being silently
  treated as fresh primitives with the wrong scale.
* ``reorder_dims`` is implemented independently as an index permutation.
"""
from __future__ import annotations

from itertools import product as _product
from math import prod

from .core import CovArray, UnsupportedOperationError


def _strides(shape):
    strides, step = [], 1
    for size in reversed(shape):
        strides.append(step)
        step *= size
    return tuple(reversed(strides))


class _DualArray:
    __slots__ = ("vals", "jac", "shape", "dims")

    def __init__(self, vals, jac, shape, dims):
        self.vals = list(vals)
        self.jac = [list(row) for row in jac]
        self.shape = tuple(shape)
        self.dims = tuple(dims)

    @property
    def size(self):
        return len(self.vals)

    @property
    def values(self):
        return tuple(self.vals)

    def _ncols(self):
        return len(self.jac[0]) if self.jac else 0

    def _coerce(self, other):
        if isinstance(other, _DualArray):
            return other
        if isinstance(other, (int, float)):
            return _DualArray([float(other)], [[0.0] * self._ncols()], (), ())
        raise TypeError(f"oracle cannot coerce {type(other)!r}")

    def _aligned(self, other):
        if self.shape == other.shape:
            return self, other
        if other.shape == ():
            return self, _DualArray(other.vals * self.size,
                                     other.jac * self.size,
                                     self.shape, self.dims)
        if self.shape == ():
            return _DualArray(self.vals * other.size, self.jac * other.size,
                              other.shape, other.dims), other
        raise ValueError("oracle shapes cannot be aligned")

    def _bin(self, other, value_fn, deriv_fn):
        other = self._coerce(other)
        left, right = self._aligned(other)
        vals, jac = [], []
        for i in range(left.size):
            a, b = left.vals[i], right.vals[i]
            da, db = deriv_fn(a, b)
            vals.append(value_fn(a, b))
            jac.append([da * x + db * y
                        for x, y in zip(left.jac[i], right.jac[i])])
        return _DualArray(vals, jac, left.shape, left.dims)

    def __add__(self, other):
        return self._bin(other, lambda a, b: a + b, lambda a, b: (1.0, 1.0))

    __radd__ = __add__

    def __sub__(self, other):
        return self._bin(other, lambda a, b: a - b, lambda a, b: (1.0, -1.0))

    def __rsub__(self, other):
        return self._coerce(other).__sub__(self)

    def __mul__(self, other):
        return self._bin(other, lambda a, b: a * b, lambda a, b: (b, a))

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self._bin(other, lambda a, b: a / b,
                         lambda a, b: (1.0 / b, -a / (b * b)))

    def __rtruediv__(self, other):
        return self._coerce(other).__truediv__(self)

    def __neg__(self):
        return _DualArray([-v for v in self.vals],
                           [[-x for x in row] for row in self.jac],
                           self.shape, self.dims)

    def __getitem__(self, item):
        if isinstance(item, int):
            return _DualArray([self.vals[item]], [self.jac[item]], (), ())
        raise TypeError("oracle indexing supports a single integer")

    def _linear_rows(self, rows, shape, dims):
        vals = [sum(w * self.vals[k] for k, w in row.items()) for row in rows]
        jac = []
        for row in rows:
            out = [0.0] * self._ncols()
            for k, w in row.items():
                for c in range(self._ncols()):
                    out[c] += w * self.jac[k][c]
            jac.append(out)
        return _DualArray(vals, jac, shape, dims)

    def sum(self, dim=None):
        if dim is not None:
            return self._reduce(dim, mean=False)
        return self._linear_rows([{k: 1.0 for k in range(self.size)}], (), ())

    def mean(self, dim=None):
        if dim is not None:
            return self._reduce(dim, mean=True)
        w = 1.0 / self.size
        return self._linear_rows([{k: w for k in range(self.size)}], (), ())

    def _reduce(self, dim, mean):
        axis = self.dims.index(dim)
        strides = _strides(self.shape)
        out_shape = self.shape[:axis] + self.shape[axis + 1:]
        out_dims = self.dims[:axis] + self.dims[axis + 1:]
        w = 1.0 / self.shape[axis] if mean else 1.0
        rows = []
        for out_idx in _product(*[range(s) for s in out_shape]) if out_shape else [()]:
            row = {}
            for k in range(self.shape[axis]):
                full = out_idx[:axis] + (k,) + out_idx[axis:]
                row[sum(i * s for i, s in zip(full, strides))] = w
            rows.append(row)
        return self._linear_rows(rows, out_shape, out_dims)

    def reorder_dims(self, *dims):
        if set(dims) != set(self.dims) or len(dims) != len(self.dims):
            raise ValueError("reorder_dims must permute the existing dims")
        perm = [self.dims.index(d) for d in dims]
        out_shape = tuple(self.shape[p] for p in perm)
        strides = _strides(self.shape)
        rows = []
        for out_idx in _product(*[range(s) for s in out_shape]):
            src = [0] * len(perm)
            for new_axis, old_axis in enumerate(perm):
                src[old_axis] = out_idx[new_axis]
            rows.append({sum(i * s for i, s in zip(src, strides)): 1.0})
        return self._linear_rows(rows, out_shape, tuple(dims))

    def moving_window(self, dim, weights, *, mode="valid"):
        return _oracle_moving_window(self, dim, weights, mode=mode)

    def rebin(self, dim, *args, **kwargs):
        return _oracle_rebin(self, dim, *args, **kwargs)

    def __floordiv__(self, other):
        raise UnsupportedOperationError("floor division is discontinuous")

    def __mod__(self, other):
        raise UnsupportedOperationError("modulo is discontinuous")


def _axis_rows(array, dim, axis_rows):
    """Expand per-axis linear rows into flat linear rows (oracle-local)."""
    axis = array.dims.index(dim)
    strides = _strides(array.shape)
    other_shape = array.shape[:axis] + array.shape[axis + 1:]
    out_shape = array.shape[:axis] + (len(axis_rows),) + array.shape[axis + 1:]
    rows = []
    for out_idx in _product(*[range(s) for s in out_shape]) if out_shape else [()]:
        base = out_idx[:axis] + out_idx[axis + 1:]
        row = {}
        for k, w in axis_rows[out_idx[axis]].items():
            full = base[:axis] + (k,) + base[axis:]
            row[sum(i * s for i, s in zip(full, strides))] = w
        rows.append(row)
    return array._linear_rows(rows, out_shape, array.dims)


def _oracle_moving_window(array, dim, weights, *, mode="valid"):
    weights = tuple(float(w) for w in weights)
    axis = array.dims.index(dim)
    n, width = array.shape[axis], len(weights)
    output_n = n - width + 1 if mode == "valid" else n
    left = width // 2
    rows = []
    for out in range(output_n):
        start = out if mode == "valid" else out - left
        rows.append({start + k: w for k, w in enumerate(weights)
                     if 0 <= start + k < n and w})
    return _axis_rows(array, dim, rows)


def _oracle_rebin(array, dim, *args, intensive=False, old_edges=None,
                  new_edges=None):
    if len(args) == 1:
        new_edges = args[0]
    elif len(args) == 2:
        old_edges, new_edges = args
    if old_edges is None or new_edges is None:
        raise TypeError("oracle rebin needs explicit old_edges and new_edges")
    old_edges = tuple(float(x) for x in old_edges)
    new_edges = tuple(float(x) for x in new_edges)
    rows = []
    for new_left, new_right in zip(new_edges, new_edges[1:]):
        row = {}
        for k, (left, right) in enumerate(zip(old_edges, old_edges[1:])):
            overlap = max(0.0, min(right, new_right) - max(left, new_left))
            if overlap:
                row[k] = overlap / ((new_right - new_left) if intensive
                                    else (right - left))
        rows.append(row)
    return _axis_rows(array, dim, rows)


def dense_jcjt_oracle(arrays, program):
    """Run ``program`` on duals of primitive ``arrays``; return (values, cov).

    ``program`` receives a list of oracle arrays, one per entry in
    ``arrays`` (repeated primitives share one block), and returns one oracle
    array.  The returned covariance is the dense ``J C J^T`` as nested lists.
    """
    arrays = list(arrays)
    blocks, offsets, total = [], {}, 0
    for array in arrays:
        if not isinstance(array, CovArray):
            raise TypeError("oracle inputs must be CovArray primitives")
        if not array._primitive or array._source is None:
            raise ValueError(
                "oracle inputs must be primitive sources; derived arrays "
                "would be silently rescaled and are rejected")
        key = id(array._source)
        if key not in offsets:
            offsets[key] = total
            blocks.append(array)
            total += array.size
    duals = []
    for array in arrays:
        off = offsets[id(array._source)]
        jac = [[1.0 if off + i == j else 0.0 for j in range(total)]
               for i in range(array.size)]
        duals.append(_DualArray(array.values, jac, array.shape, array.dims))
    result = program(duals)
    if isinstance(result, (int, float)):
        return (float(result),), [[0.0]]
    big_c = [[0.0] * total for _ in range(total)]
    for array in blocks:
        off = offsets[id(array._source)]
        src = array._source
        for p in range(src.size):
            for q in range(src.size):
                big_c[off + p][off + q] = src.covariance[p * src.size + q]
    cov = [[sum(result.jac[i][p] * big_c[p][q] * result.jac[j][q]
                 for p in range(total) for q in range(total))
            for j in range(result.size)] for i in range(result.size)]
    return tuple(result.vals), cov


def max_covariance_difference(covarray, arrays, program):
    """Largest absolute entry difference between library and oracle."""
    _, oracle_cov = dense_jcjt_oracle(arrays, program)
    lib_cov = covarray.covariance()
    return max(abs(a - b) for ra, rb in zip(lib_cov, oracle_cov)
               for a, b in zip(ra, rb))
