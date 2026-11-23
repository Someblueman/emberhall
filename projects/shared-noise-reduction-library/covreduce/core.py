"""First-order covariance arrays with provenance and labelled dimensions.

The implementation deliberately uses only the Python standard library.  A
CovArray stores, for every independent primitive source, a sparse Jacobian of
its outputs with respect to that source.  Covariance is therefore J C J^T;
reusing a source preserves all cross terms.
"""
from __future__ import annotations

from bisect import bisect_right
from itertools import product
from math import prod, sqrt
from typing import Iterable, Mapping, Sequence


class DimensionMismatchError(ValueError):
    """Raised when named dimensions or their coordinates cannot be aligned."""


class UnsupportedOperationError(ValueError):
    """Raised for operations outside the first-order linear contract."""


def _real(value) -> float:
    if isinstance(value, bool):
        raise TypeError("values must be real numbers, not booleans")
    return float(value)


def _shape_and_flat(values) -> tuple[tuple[int, ...], tuple[float, ...]]:
    if isinstance(values, CovArray):
        raise TypeError("use an existing CovArray directly, not as primitive values")
    if isinstance(values, (str, bytes)):
        raise TypeError("values must be real numbers")
    if isinstance(values, Sequence):
        if not values:
            return (0,), ()
        child_shapes = []
        flat = []
        for item in values:
            shape, part = _shape_and_flat(item)
            child_shapes.append(shape)
            flat.extend(part)
        if any(shape != child_shapes[0] for shape in child_shapes[1:]):
            raise DimensionMismatchError("array values must be rectangular")
        return (len(values),) + child_shapes[0], tuple(flat)
    return (), (_real(values),)


def _flat_index(index: Sequence[int], shape: Sequence[int]) -> int:
    answer = 0
    for i, size in zip(index, shape):
        answer = answer * size + i
    return answer


def _indices(shape: Sequence[int]):
    if not shape:
        yield ()
    else:
        yield from product(*(range(n) for n in shape))


def _normalise_dims(dims, shape):
    if dims is None:
        return tuple(f"dim_{i}" for i in range(len(shape)))
    if isinstance(dims, str):
        dims = (dims,)
    dims = tuple(dims)
    if len(dims) != len(shape) or len(set(dims)) != len(dims):
        raise DimensionMismatchError("dims must uniquely name every array axis")
    return dims


def _normalise_coords(coords, dims, shape):
    if coords is None:
        return {d: tuple(range(n)) for d, n in zip(dims, shape)}
    if isinstance(coords, Mapping):
        answer = {d: tuple(coords[d]) if d in coords else tuple(range(n))
                  for d, n in zip(dims, shape)}
    else:
        if len(coords) != len(dims):
            raise DimensionMismatchError("coordinates must match dims")
        answer = {d: tuple(c) for d, c in zip(dims, coords)}
    for d, n in zip(dims, shape):
        # A coordinate may be bin centres (n) or bin edges (n+1).
        if len(answer[d]) not in (n, n + 1):
            raise DimensionMismatchError(f"coordinate {d!r} has the wrong length")
    return answer


def _merge(destination: dict[int, float], source: Mapping[int, float], factor=1.0):
    for key, value in source.items():
        value *= factor
        if value:
            destination[key] = destination.get(key, 0.0) + value
            if abs(destination[key]) < 1e-18:
                del destination[key]


def _cholesky_psd(matrix: Sequence[float], n: int) -> bool:
    # Every dense primitive matrix is checked, at any size.  Diagonal
    # matrices need only their diagonal check, avoiding an O(n^3) setup cost.
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            value = matrix[i * n + j] - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if value < -1e-12:
                    return False
                lower[i][j] = sqrt(max(0.0, value))
            else:
                if lower[j][j] == 0:
                    if abs(value) > 1e-10:
                        return False
                    lower[i][j] = 0.0
                else:
                    lower[i][j] = value / lower[j][j]
    return True


def _covariance_matrix(covariance, n: int) -> tuple[float, ...]:
    if covariance is None:
        return (0.0,) * (n * n)
    if isinstance(covariance, bool):
        raise TypeError("covariance must be real numbers, not booleans")
    if isinstance(covariance, (int, float)):
        if covariance < 0:
            raise ValueError("variance cannot be negative")
        matrix = [0.0] * (n * n)
        for i in range(n):
            matrix[i * n + i] = _real(covariance)
        return tuple(matrix)
    if isinstance(covariance, Sequence) and covariance and isinstance(covariance[0], Sequence):
        if len(covariance) != n or any(len(row) != n for row in covariance):
            raise DimensionMismatchError("covariance must be n by n")
        matrix = tuple(_real(x) for row in covariance for x in row)
    else:
        flat = tuple(_real(x) for x in covariance)
        if len(flat) == n:
            matrix = [0.0] * (n * n)
            for i, value in enumerate(flat):
                matrix[i * n + i] = value
            matrix = tuple(matrix)
        elif len(flat) == n * n:
            matrix = flat
        else:
            raise DimensionMismatchError("covariance must be diagonal or n by n")
    for i in range(n):
        if matrix[i * n + i] < -1e-12:
            raise ValueError("variance cannot be negative")
        for j in range(i):
            if abs(matrix[i * n + j] - matrix[j * n + i]) > 1e-9:
                raise ValueError("covariance must be symmetric")
    dense = any(matrix[i * n + j] for i in range(n) for j in range(i))
    if dense and not _cholesky_psd(matrix, n):
        raise ValueError("covariance must be positive semidefinite")
    return matrix


class _Source:
    __slots__ = ("values", "covariance", "size")

    def __init__(self, values, covariance):
        self.values = tuple(values)
        self.size = len(values)
        self.covariance = _covariance_matrix(covariance, self.size)


class CovArray:
    """An array and its sparse first-order derivatives by primitive source."""

    approximation = "first_order_linear"

    def __init__(self, values, covariance=None, dims=None, coords=None, *,
                 _parts=None):
        if _parts is not None:
            (flat, shape, dims, coordinates, jacobians, primitive) = _parts
            self._flat = tuple(flat)
            self.shape = tuple(shape)
            self.dims = tuple(dims)
            self.coords = dict(coordinates)
            self._jacobians = jacobians
            self._primitive = primitive
            self._source = None
            return
        shape, flat = _shape_and_flat(values)
        dims = _normalise_dims(dims, shape)
        coordinates = _normalise_coords(coords, dims, shape)
        source_object = _Source(flat, covariance)
        jacobians = {source_object: tuple({i: 1.0} for i in range(len(flat)))}
        self._flat = flat
        self.shape = shape
        self.dims = dims
        self.coords = coordinates
        self._jacobians = jacobians
        self._primitive = True
        self._source = source_object

    @classmethod
    def _from_parts(cls, flat, shape, dims, coords, jacobians):
        clean = {}
        for source_object, rows in jacobians.items():
            rows = tuple(dict(row) for row in rows)
            if any(rows):
                clean[source_object] = rows
        return cls((), _parts=(flat, shape, dims, coords, clean, False))

    @property
    def values(self):
        """Flat values in C order; use ``value`` for a scalar."""
        return self._flat

    @property
    def value(self):
        if self.size != 1:
            raise ValueError("value is only defined for a scalar")
        return self._flat[0]

    @property
    def size(self):
        return len(self._flat)

    def __len__(self):
        if not self.shape:
            raise TypeError("a scalar has no len()")
        return self.shape[0]

    def __repr__(self):
        if self.size == 1:
            return f"CovArray({self.value!r}, variance={self.variance!r})"
        return f"CovArray(shape={self.shape!r}, dims={self.dims!r})"

    @property
    def variance(self):
        diagonal = [self.covariance_entry(i, i) for i in range(self.size)]
        return diagonal[0] if self.size == 1 else diagonal

    @property
    def var(self):
        return self.variance

    def covariance_entry(self, i: int, j: int) -> float:
        total = 0.0
        for source_object, rows in self._jacobians.items():
            left, right = rows[i], rows[j]
            if not left or not right:
                continue
            for p, jp in left.items():
                for q, jq in right.items():
                    total += jp * source_object.covariance[p * source_object.size + q] * jq
        return total

    def covariance(self):
        return [[self.covariance_entry(i, j) for j in range(self.size)]
                for i in range(self.size)]

    dense_covariance = covariance

    def quadratic_form(self, weights: Sequence[float]) -> float:
        """Return w^T C w without materialising the output covariance."""
        weights = tuple(_real(w) for w in weights)
        if len(weights) != self.size:
            raise DimensionMismatchError("quadratic-form weights have the wrong length")
        total = 0.0
        for source_object, rows in self._jacobians.items():
            contracted = {}
            for w, row in zip(weights, rows):
                if w:
                    _merge(contracted, row, w)
            for p, jp in contracted.items():
                for q, jq in contracted.items():
                    total += jp * source_object.covariance[p * source_object.size + q] * jq
        return total

    def _constant(self, value: float):
        return CovArray._from_parts((_real(value),), (), (), {}, {})

    def _coerce(self, other):
        return other if isinstance(other, CovArray) else self._constant(other)

    def _broadcast_to(self, other: "CovArray"):
        if self.size != 1:
            raise DimensionMismatchError("only scalar arrays can be broadcast")
        flat = self._flat * other.size
        jacobians = {s: tuple(dict(rows[0]) for _ in range(other.size))
                     for s, rows in self._jacobians.items()}
        return CovArray._from_parts(flat, other.shape, other.dims, other.coords, jacobians)

    def _aligned_pair(self, other):
        other = self._coerce(other)
        if self.shape == () and other.shape != ():
            return self._broadcast_to(other), other
        if other.shape == () and self.shape != ():
            return self, other._broadcast_to(self)
        if self.size == 1 and other.size > 1:
            return self._broadcast_to(other), other
        if other.size == 1 and self.size > 1:
            return self, other._broadcast_to(self)
        if self.shape != other.shape:
            raise DimensionMismatchError("array shapes do not match")
        if self.dims != other.dims:
            if set(self.dims) != set(other.dims):
                raise DimensionMismatchError("array dimensions do not match")
            other = other.reorder_dims(self.dims)
        for dim in self.dims:
            if self.coords[dim] != other.coords[dim]:
                raise DimensionMismatchError(f"coordinates for {dim!r} do not match")
        return self, other

    def _binary(self, other, operation: str, reverse=False):
        left, right = self._aligned_pair(other)
        if reverse:
            left, right = right, left
        flat = []
        all_jacobians = {}
        source_objects = set(left._jacobians) | set(right._jacobians)
        for source_object in source_objects:
            all_jacobians[source_object] = []
        for i, (a, b) in enumerate(zip(left._flat, right._flat)):
            if operation == "add":
                value, da, db = a + b, 1.0, 1.0
            elif operation == "sub":
                value, da, db = a - b, 1.0, -1.0
            elif operation == "mul":
                value, da, db = a * b, b, a
            else:
                if abs(b) < 1e-15:
                    raise ZeroDivisionError("uncertain division by zero or near zero")
                value, da, db = a / b, 1.0 / b, -a / (b * b)
            flat.append(value)
            for source_object in source_objects:
                row = {}
                if source_object in left._jacobians:
                    _merge(row, left._jacobians[source_object][i], da)
                if source_object in right._jacobians:
                    _merge(row, right._jacobians[source_object][i], db)
                all_jacobians[source_object].append(row)
        return CovArray._from_parts(flat, left.shape, left.dims, left.coords, all_jacobians)

    def __add__(self, other):
        return self._binary(other, "add")

    def __radd__(self, other):
        return self._binary(other, "add", True)

    def __sub__(self, other):
        return self._binary(other, "sub")

    def __rsub__(self, other):
        return self._binary(other, "sub", True)

    def __mul__(self, other):
        return self._binary(other, "mul")

    def __rmul__(self, other):
        return self._binary(other, "mul", True)

    def __truediv__(self, other):
        return self._binary(other, "div")

    def __rtruediv__(self, other):
        return self._binary(other, "div", True)

    def __neg__(self):
        return self * -1.0

    def __abs__(self):
        raise UnsupportedOperationError("abs is not differentiable under the linear contract")

    def __floordiv__(self, other):
        raise UnsupportedOperationError("floor division is not first-order differentiable")

    def __mod__(self, other):
        raise UnsupportedOperationError("modulo is not first-order differentiable")

    def apply_discontinuous(self, *args, **kwargs):
        raise UnsupportedOperationError("discontinuous operations require explicit Monte Carlo")

    def _take(self, old_indices, shape, dims, coords):
        flat = [self._flat[i] for i in old_indices]
        jacobians = {s: tuple(dict(rows[i]) for i in old_indices)
                     for s, rows in self._jacobians.items()}
        return CovArray._from_parts(flat, shape, dims, coords, jacobians)

    def select(self, dim: str, index):
        if dim not in self.dims:
            raise DimensionMismatchError(f"unknown dimension {dim!r}")
        axis = self.dims.index(dim)
        if isinstance(index, int):
            index = index + self.shape[axis] if index < 0 else index
            if not 0 <= index < self.shape[axis]:
                raise IndexError(index)
            selected = [index]
            shape = self.shape[:axis] + self.shape[axis + 1:]
            dims = self.dims[:axis] + self.dims[axis + 1:]
            coords = {d: c for d, c in self.coords.items() if d != dim}
        elif isinstance(index, slice):
            selected = list(range(self.shape[axis]))[index]
            shape = self.shape[:axis] + (len(selected),) + self.shape[axis + 1:]
            dims = self.dims
            coords = dict(self.coords)
            coords[dim] = tuple(self.coords[dim][i] for i in selected)
        else:
            selected = [i + self.shape[axis] if i < 0 else i for i in index]
            if any(not 0 <= i < self.shape[axis] for i in selected):
                raise IndexError(index)
            shape = self.shape[:axis] + (len(selected),) + self.shape[axis + 1:]
            dims = self.dims
            coords = dict(self.coords)
            coords[dim] = tuple(self.coords[dim][i] for i in selected)
        old_indices = []
        for out_index in _indices(shape):
            chosen = selected[0] if isinstance(index, int) else selected[out_index[axis]]
            full = list(out_index[:axis]) + [chosen] + list(out_index[axis:])
            old_indices.append(_flat_index(full, self.shape))
        return self._take(old_indices, shape, dims, coords)

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        if len(item) > len(self.shape):
            raise IndexError("too many indices")
        result = self
        axis = 0
        for index in item:
            result = result.select(result.dims[axis], index)
            if not isinstance(index, int):
                axis += 1
        return result

    def _reduce(self, dim, mean=False):
        if dim is None:
            weights = [1.0 / self.size if mean else 1.0] * self.size
            return self._take_linear_all(weights)
        if isinstance(dim, int):
            dim = self.dims[dim]
        axis = self.dims.index(dim)
        n = self.shape[axis]
        shape = self.shape[:axis] + self.shape[axis + 1:]
        dims = self.dims[:axis] + self.dims[axis + 1:]
        coords = {d: c for d, c in self.coords.items() if d != dim}
        old_groups = []
        for out_index in _indices(shape):
            group = []
            for k in range(n):
                full = list(out_index[:axis]) + [k] + list(out_index[axis:])
                group.append(_flat_index(full, self.shape))
            old_groups.append(group)
        factor = 1.0 / n if mean else 1.0
        flat = [factor * sum(self._flat[i] for i in group) for group in old_groups]
        jacobians = {}
        for s, rows in self._jacobians.items():
            new_rows = []
            for group in old_groups:
                row = {}
                for i in group:
                    _merge(row, rows[i], factor)
                new_rows.append(row)
            jacobians[s] = tuple(new_rows)
        return CovArray._from_parts(flat, shape, dims, coords, jacobians)

    def _take_linear_all(self, weights):
        row_jacobians = {}
        for s, rows in self._jacobians.items():
            row = {}
            for weight, derivatives in zip(weights, rows):
                _merge(row, derivatives, weight)
            row_jacobians[s] = (row,)
        value = sum(w * x for w, x in zip(weights, self._flat))
        return CovArray._from_parts((value,), (), (), {}, row_jacobians)

    def sum(self, dim=None):
        return self._reduce(dim, False)

    def mean(self, dim=None):
        return self._reduce(dim, True)

    def reorder_dims(self, *dims):
        if len(dims) == 1 and not isinstance(dims[0], str):
            dims = tuple(dims[0])
        if len(dims) != len(self.dims) or set(dims) != set(self.dims):
            raise DimensionMismatchError("reordering must name every dimension exactly once")
        order = tuple(self.dims.index(d) for d in dims)
        shape = tuple(self.shape[i] for i in order)
        coords = {d: self.coords[d] for d in dims}
        old_indices = []
        for out_index in _indices(shape):
            old_index = [0] * len(shape)
            for out_axis, old_axis in enumerate(order):
                old_index[old_axis] = out_index[out_axis]
            old_indices.append(_flat_index(old_index, self.shape))
        return self._take(old_indices, shape, dims, coords)

    def moving_window(self, dim, weights, *, mode="valid"):
        return moving_window(self, dim, weights, mode=mode)

    def rebin(self, dim, *args, **kwargs):
        return rebin(self, dim, *args, **kwargs)


def source(values, covariance=None, dims=None, coords=None) -> CovArray:
    """Create an independent primitive source.

    Distinct calls are independent even when all values and covariances agree;
    reusing the returned object retains provenance and exact cancellation.
    """
    return CovArray(values, covariance, dims, coords)


def constant(values, dims=None, coords=None) -> CovArray:
    return CovArray(values, None, dims, coords)


def select(array: CovArray, dim: str, index):
    return array.select(dim, index)


def reduce_sum(array: CovArray, dim=None):
    return array.sum(dim)


def reduce_mean(array: CovArray, dim=None):
    return array.mean(dim)


def reorder_dims(array: CovArray, *dims):
    return array.reorder_dims(*dims)


def _linear_axis_transform(array: CovArray, dim: str, rows, out_coordinate):
    axis = array.dims.index(dim)
    shape = array.shape[:axis] + (len(rows),) + array.shape[axis + 1:]
    coords = dict(array.coords)
    coords[dim] = tuple(out_coordinate)
    flat = []
    jacobians = {s: [] for s in array._jacobians}
    before_shape = array.shape[:axis]
    after_shape = array.shape[axis + 1:]
    for before in _indices(before_shape):
        for row_spec in rows:
            for after in _indices(after_shape):
                value = 0.0
                for k, weight in row_spec.items():
                    old = _flat_index(tuple(before) + (k,) + tuple(after), array.shape)
                    value += weight * array._flat[old]
                flat.append(value)
                for s, source_rows in array._jacobians.items():
                    source_row = {}
                    for k, weight in row_spec.items():
                        old = _flat_index(tuple(before) + (k,) + tuple(after), array.shape)
                        _merge(source_row, source_rows[old], weight)
                    jacobians[s].append(source_row)
    return CovArray._from_parts(flat, shape, array.dims, coords, jacobians)


def moving_window(array: CovArray, dim: str, weights: Sequence[float], *, mode="valid") -> CovArray:
    """Apply a finite linear stencil along a named dimension.

    ``valid`` returns only complete windows.  ``same`` zero-pads the input and
    keeps the input length.  Negative and non-normalised weights are allowed.
    """
    weights = tuple(_real(w) for w in weights)
    if not weights:
        raise ValueError("moving-window weights cannot be empty")
    axis = array.dims.index(dim)
    n, width = array.shape[axis], len(weights)
    if mode not in ("valid", "same"):
        raise ValueError("mode must be 'valid' or 'same'")
    if mode == "valid" and width > n:
        raise ValueError("window is wider than the dimension")
    rows = []
    coordinates = []
    output_n = n - width + 1 if mode == "valid" else n
    left = width // 2
    for out in range(output_n):
        start = out if mode == "valid" else out - left
        rows.append({start + k: weight for k, weight in enumerate(weights)
                     if 0 <= start + k < n and weight})
        centre = start + left
        centre = min(n - 1, max(0, centre))
        coordinates.append(array.coords[dim][centre])
    return _linear_axis_transform(array, dim, rows, coordinates)


def _centres_to_edges(centres):
    if len(centres) == 1:
        return (_real(centres[0]) - 0.5, _real(centres[0]) + 0.5)
    centres = tuple(_real(x) for x in centres)
    edges = [centres[0] - (centres[1] - centres[0]) / 2]
    edges.extend((a + b) / 2 for a, b in zip(centres, centres[1:]))
    edges.append(centres[-1] + (centres[-1] - centres[-2]) / 2)
    return tuple(edges)


def rebin(array: CovArray, dim: str, *args, intensive=False, extensive=None,
          old_edges=None, new_edges=None) -> CovArray:
    """Linearly rebin one labelled dimension using overlap fractions.

    Accepted forms are ``rebin(a, dim, new_edges)`` and
    ``rebin(a, dim, old_edges, new_edges)``.  Extensive values conserve their
    sum; intensive values conserve the coordinate-weighted average.
    """
    if len(args) == 1:
        if new_edges is not None:
            raise TypeError("new_edges supplied twice")
        new_edges = args[0]
    elif len(args) == 2:
        if old_edges is not None or new_edges is not None:
            raise TypeError("bin edges supplied twice")
        old_edges, new_edges = args
    elif args:
        raise TypeError("rebin expects new_edges or old_edges, new_edges")
    if new_edges is None:
        raise TypeError("new_edges is required")
    if extensive is not None:
        intensive = not extensive
    axis = array.dims.index(dim)
    n = array.shape[axis]
    if old_edges is None:
        coordinate = array.coords[dim]
        old_edges = coordinate if len(coordinate) == n + 1 else _centres_to_edges(coordinate)
    old_edges = tuple(_real(x) for x in old_edges)
    new_edges = tuple(_real(x) for x in new_edges)
    if len(old_edges) != n + 1 or len(new_edges) < 2:
        raise DimensionMismatchError("bin edges must have n+1 entries")
    if any(b <= a for a, b in zip(old_edges, old_edges[1:])) or any(
            b <= a for a, b in zip(new_edges, new_edges[1:])):
        raise ValueError("bin edges must be strictly increasing")
    rows = []
    for new_left, new_right in zip(new_edges, new_edges[1:]):
        row = {}
        new_width = new_right - new_left
        for k, (left, right) in enumerate(zip(old_edges, old_edges[1:])):
            overlap = max(0.0, min(right, new_right) - max(left, new_left))
            if overlap:
                row[k] = overlap / (new_width if intensive else right - left)
        rows.append(row)
    return _linear_axis_transform(array, dim, rows, new_edges)


def quadratic_form(array: CovArray, weights: Sequence[float]) -> float:
    return array.quadratic_form(weights)
