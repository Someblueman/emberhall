"""Exact fixed-graph death-Birth calculations; not a universal reducer proof."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from itertools import combinations, permutations
from pathlib import Path


def rational(value: int | F) -> F:
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise ValueError("use exact integers or Fractions, never floats")
    return F(value)


def validate(weights, fitness):
    """Validate the selected symmetric, connected, row-normalized domain."""
    r = rational(fitness)
    if r <= 0:
        raise ValueError("fitness must be positive")
    n = len(weights)
    if n < 2 or any(len(row) != n for row in weights):
        raise ValueError("weights must be a square matrix of size at least two")
    w = tuple(tuple(rational(x) for x in row) for row in weights)
    for i, row in enumerate(w):
        if row[i] != 0 or any(x < 0 for x in row) or sum(row) != 1:
            raise ValueError("weights must be nonnegative, loop-free and sum to one per row")
        if any(row[j] != w[j][i] for j in range(n)):
            raise ValueError("weights must be symmetric")
    seen, pending = {0}, [0]
    while pending:
        i = pending.pop()
        for j, weight in enumerate(w[i]):
            if weight and j not in seen:
                seen.add(j)
                pending.append(j)
    if len(seen) != n:
        raise ValueError("graph must be connected")
    return w, r


def transition_row(w, r, state):
    """Aggregate by the type replacing each uniformly chosen dead vertex."""
    n = len(w)
    out = {}
    for dead in range(n):
        a = sum(w[dead][j] for j in range(n) if state & (1 << j))
        mutant = r * a / (1 + (r - 1) * a)
        for target, chance in ((state | (1 << dead), mutant),
                               (state & ~(1 << dead), 1 - mutant)):
            out[target] = out.get(target, F(0)) + chance / n
    return out


def _linear_solve(a, b):
    """Rational elimination with row pivoting; inputs are private fresh rows."""
    size = len(b)
    for col in range(size):
        pivot = next((i for i in range(col, size) if a[i][col]), None)
        if pivot is None:
            raise ValueError("singular transient system")
        a[col], a[pivot] = a[pivot], a[col]
        b[col], b[pivot] = b[pivot], b[col]
        for row in range(col + 1, size):
            if not a[row][col]:
                continue
            factor = a[row][col] / a[col][col]
            a[row][col] = F(0)
            for j in range(col + 1, size):
                a[row][j] -= factor * a[col][j]
            b[row] -= factor * b[col]
    x = [F(0)] * size
    for row in range(size - 1, -1, -1):
        x[row] = (b[row] - sum(a[row][j] * x[j]
                              for j in range(row + 1, size))) / a[row][row]
    return x


def _system(w, r):
    full = (1 << len(w)) - 1
    a = [[F(i == j) for j in range(full - 1)] for i in range(full - 1)]
    b = [F(0)] * (full - 1)
    for state in range(1, full):
        for target, chance in transition_row(w, r, state).items():
            if target == full:
                b[state - 1] += chance
            elif target:
                a[state - 1][target - 1] -= chance
    return a, b


def solve(weights, fitness):
    """Return fixation probabilities indexed by mutant-set bitmask, including 0/full."""
    w, r = validate(weights, fitness)
    a, b = _system(w, r)
    return [F(0), *_linear_solve(a, b), F(1)]


def neutral_derivatives(weights):
    """First and second fitness derivatives at r=1, by differentiating the system."""
    w, _ = validate(weights, F(1))
    n, full = len(w), (1 << len(w)) - 1
    u0 = [F(state.bit_count(), n) for state in range(full + 1)]
    matrix, _ = _system(w, F(1))
    rhs1 = [F(0)] * (full - 1)
    terms = []
    for state in range(1, full):
        row = []
        for dead in range(n):
            a = sum(w[dead][j] for j in range(n) if state & (1 << j))
            up, down = state | (1 << dead), state & ~(1 << dead)
            first, second = a * (1 - a) / n, -2 * a*a * (1 - a) / n
            rhs1[state - 1] += first * (u0[up] - u0[down])
            row.append((up, down, first, second))
        terms.append(row)
    u1 = [F(0), *_linear_solve([row[:] for row in matrix], rhs1), F(0)]
    rhs2 = [sum(second * (u0[up] - u0[down]) + 2 * first * (u1[up] - u1[down])
                for up, down, first, second in row) for row in terms]
    u2 = [F(0), *_linear_solve(matrix, rhs2), F(0)]
    return u1, u2


def uniform_fixation(values, n):
    return sum(values[1 << i] for i in range(n)) / n


def complete_probability(n, r):
    """Loop-free complete graph: (N-1)/N times Moran probability on N-1 sites."""
    r = rational(r)
    if n < 2 or r <= 0:
        raise ValueError("positive fitness and at least two vertices required")
    return F(n - 1, n) / sum(r ** (-j) for j in range(n - 1))


def cycle_probability(n, r):
    """Independent contiguous-mutant birth/death chain formula, N >= 3."""
    r = rational(r)
    if n < 3 or r <= 0:
        raise ValueError("positive fitness and at least three vertices required")
    return 1 / (1 + (r + 1) / 2 * sum(r ** (-j) for j in range(1, n - 1))
                + r ** (-(n - 2)))


def certificate(weights, fitness):
    w, r = validate(weights, fitness)
    values = solve(w, r)
    return {"version": 1, "model": "death-Birth", "fitness": str(r),
            "weights": [[str(x) for x in row] for row in w],
            "probabilities": [str(x) for x in values]}


def _parse_fraction(value):
    if not isinstance(value, str):
        raise ValueError("certificate rationals must be strings")
    return F(value)


def verify(data):
    """Check elementary death/parent events, without solving or using transition_row."""
    keys = {"version", "model", "fitness", "weights", "probabilities"}
    if not isinstance(data, dict) or set(data) != keys:
        raise ValueError("unexpected certificate fields")
    if type(data["version"]) is not int or data["version"] != 1:
        raise ValueError("unsupported certificate version")
    if data["model"] != "death-Birth":
        raise ValueError("unsupported update model")
    w, r = validate([[_parse_fraction(x) for x in row] for row in data["weights"]],
                    _parse_fraction(data["fitness"]))
    n, full = len(w), (1 << len(w)) - 1
    u = [_parse_fraction(x) for x in data["probabilities"]]
    if len(u) != full + 1 or u[0] != 0 or u[full] != 1:
        raise ValueError("wrong probability count or absorbing boundary")
    if any(x < 0 or x > 1 for x in u):
        raise ValueError("probability outside zero to one")
    for state in range(1, full):
        expected = F(0)
        for dead in range(n):
            denominator = sum(w[dead][parent] * (r if state & (1 << parent) else 1)
                              for parent in range(n))
            for parent in range(n):
                mutant = bool(state & (1 << parent))
                target = ((state & ~(1 << dead)) | (int(mutant) << dead))
                event = w[dead][parent] * (r if mutant else 1) / (n * denominator)
                expected += event * u[target]
        if expected != u[state]:
            raise ValueError(f"harmonic residual at state {state}: {u[state] - expected}")
    return uniform_fixation(u, n)


def complete(n):
    return [[F(i != j, n - 1) for j in range(n)] for i in range(n)]


def cycle(order):
    n = len(order)
    w = [[F(0)] * n for _ in range(n)]
    for i, j in zip(order, order[1:] + order[:1]):
        w[i][j] = w[j][i] = F(1, 2)
    return w


def five_vertex_extremes():
    """12 half-weight five-cycles and 10 half-weight triangles plus an edge."""
    out = [cycle((0,) + tail) for tail in permutations(range(1, 5)) if tail[0] < tail[-1]]
    for tri in combinations(range(5), 3):
        w = [[F(0)] * 5 for _ in range(5)]
        for i, j in combinations(tri, 2):
            w[i][j] = w[j][i] = F(1, 2)
        i, j = sorted(set(range(5)) - set(tri))
        w[i][j] = w[j][i] = F(1)
        out.append(w)
    return out


def mixture(graphs, coefficients):
    if len(graphs) != len(coefficients) or not graphs:
        raise ValueError("one coefficient required per graph")
    cs = [rational(x) for x in coefficients]
    if min(cs) < 0 or sum(cs) != 1:
        raise ValueError("convex coefficients required")
    n = len(graphs[0])
    return [[sum(c * g[i][j] for c, g in zip(cs, graphs))
             for j in range(n)] for i in range(n)]


def screen():
    """Frozen finite screen: useful counterexamples are possible, proof is not."""
    vertices = five_vertex_extremes()
    cases = [("complete", complete(5)), ("cycle", vertices[0])]
    for numerator in (1, 20, 80, 99):
        cases.append((f"cycle-triangle-{numerator}/100",
                      mixture([vertices[0], vertices[12]], [F(numerator, 100),
                                                           1 - F(numerator, 100)])))
    # Frozen from seed 20261119; do not depend on a runtime's sampling algorithm.
    samples = [([15, 16, 19, 6], [1, 5, 8, 6]),
               ([1, 8, 19, 21], [3, 5, 1, 8]),
               ([16, 10, 9, 17], [9, 4, 1, 1]),
               ([7, 15, 1, 5], [6, 7, 1, 1]),
               ([4, 17, 10, 6], [4, 5, 2, 7]),
               ([14, 19, 7, 16], [5, 1, 4, 6])]
    for sample, (indices, counts) in enumerate(samples):
        chosen = [vertices[i] for i in indices]
        cases.append((f"mixture-{sample}", mixture(chosen, [F(c, sum(counts)) for c in counts])))
    count = 0
    for name, weights in cases:
        first, second = neutral_derivatives(weights)
        if uniform_fixation(first, 5) != F(3, 10):
            raise ValueError(f"neutral slope control failed for {name}")
        curvature_gap = F(-1, 10) - uniform_fixation(second, 5)
        if curvature_gap < 0:
            raise ValueError(f"positive near-neutral counterexample curvature for {name}")
        for r in (F(1, 4), F(9, 10), F(11, 10), F(4)):
            data = certificate(weights, r)
            value = verify(data)
            gap = complete_probability(5, r) - value
            if gap < 0:
                print(json.dumps(data, indent=2))
                raise ValueError(f"COUNTEREXAMPLE {name}, fitness={r}, exact gap={gap}")
            count += 1
        print(f"PASS {name}: four exact fitness values, 30 equations, neutral slope and curvature")
    print(f"PASS {count} fixed cases; no counterexample in this finite screen")
    print("OPEN: all weights, all positive fitness, equality cases and current priority")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--solve", type=Path, help="JSON containing weights and fitness as strings")
    group.add_argument("--verify", type=Path, help="check a complete state-probability certificate")
    group.add_argument("--screen", action="store_true", help="run the frozen finite screen")
    args = parser.parse_args()
    try:
        if args.screen:
            screen()
        elif args.verify:
            print(f"VERIFIED uniform fixation probability: {verify(json.loads(args.verify.read_text()))}")
        else:
            data = json.loads(args.solve.read_text())
            if not isinstance(data, dict) or set(data) != {"weights", "fitness"}:
                raise ValueError("input needs exactly weights and fitness")
            w = [[_parse_fraction(x) for x in row] for row in data["weights"]]
            print(json.dumps(certificate(w, _parse_fraction(data["fitness"])), indent=2))
    except (ValueError, TypeError, KeyError, ZeroDivisionError, OSError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
