"""Corrected paired-edge equations: four odd-arm residue fields remain free.

This is a reduction, not a construction or obstruction for the other 24 classes.
"""
from __future__ import annotations

import argparse
from itertools import product
from fractions import Fraction
from functools import reduce
import json
from math import gcd

from paired_edge_five import add, multiply, scale, nonperiodic_rows


def masks():
    return [(p, q) for p in product((-1, 1), repeat=3) if p.count(-1) == 1
            for q in product((-1, 1), repeat=2)]


def root_identity():
    """At C=1, reversed(second)-first=(A-1)(B-1)(E_c-X_c)."""
    one, A, B = {(0, 0): 1}, {(1, 0): 1}, {(0, 1): 1}
    ends = A, B, one
    difference_x, difference_e = [], []
    for i in range(3):
        j, k = (j for j in range(3) if i != j)
        first_x = add(one, scale(ends[j], -1), scale(ends[k], -1))
        second_x = scale(multiply(ends[j], ends[k]), -1)
        second_e = add(multiply(ends[j], ends[k]), scale(ends[j], -1), scale(ends[k], -1))
        difference_x.append(add(second_x, scale(first_x, -1)))
        difference_e.append(add(second_e, one))
    factor = multiply(add(A, scale(one, -1)), add(B, scale(one, -1)))
    return [*difference_x[:2], add(difference_x[2], factor),
            *difference_e[:2], add(difference_e[2], scale(factor, -1))]


def corrected_system(p, q, negative_sign=1):
    """Return (free columns, matrix, rhs) in w,V for c=6h+3, V=w**h.

    Only the odd-arm component where p=-1 is fixed to a constant sign.
    Its two mod-six fields are known. The other sixteen fields are free.
    """
    if (p, q) not in masks() or type(negative_sign) is not int or negative_sign not in (-1, 1):
        raise ValueError("require a one-minus odd mask, a two-sign even mask and sign +/-1")
    eps = ([p[i % 3]*q[i % 2] for i in range(6)],
           [q[i % 2] for i in range(6)], [p[i % 3] for i in range(6)])
    ends = ((0, 3), (2, 2), (3, 0))
    matrix = [[{} for _ in range(18)] for _ in range(12)]
    for arm in range(3):
        others = [i for i in range(3) if i != arm]
        for residue in range(6):
            column, e = 6*arm+residue, eps[arm][residue]
            matrix[residue][column] = {(0, 0): 1-e} if e != 1 else {}
            for other in others:
                shift, power = ends[other]
                total = residue+shift
                j = total % 6
                matrix[j][column] = add(matrix[j][column], {(power+total//6, 1): -1})
                matrix[6+j][column] = add(matrix[6+j][column], {(power+total//6, 0): -e})
            total = residue+sum(ends[i][0] for i in others)
            if e != 1:
                term = (sum(ends[i][1] for i in others)+total//6, 1)
                matrix[6+total % 6][column] = add(matrix[6+total % 6][column], {term: e-1})
    phase = p.index(-1)
    fixed = {12+phase: {(0, 0): negative_sign, (1, 1): -negative_sign},
             15+phase: {(0, 0): negative_sign, (0, 1): -negative_sign}}
    columns = [(arm, residue) for arm in range(3) for residue in range(6)
               if 6*arm+residue not in fixed]
    rhs = [scale(add(*(multiply(row[i], value) for i, value in fixed.items())), -1)
           for row in matrix]
    return columns, [[row[6*arm+residue] for arm, residue in columns] for row in matrix], rhs


def lengths(h):
    if type(h) is not int or h < 0:
        raise ValueError("h must be a nonnegative integer")
    return 6*h+18, 6*h+14, 6*h+3


def field_residuals(h, p, q, x):
    """Check a supplied sign row in the corrected system, coefficient by coefficient."""
    ns = lengths(h)
    if len(x) != 3 or any(len(row) != n for row, n in zip(x, ns)):
        raise ValueError("one sign per original edge is required")
    if any(type(s) is not int or s not in (-1, 1) for row in x for s in row):
        raise ValueError("edge signs must be integers +/-1")
    if (p, q) not in masks():
        raise ValueError("unsupported mask")
    phase = p.index(-1)
    fixed_sign = x[2][phase]
    if any(s != fixed_sign for s in x[2][phase::3]):
        raise ValueError("the single negative odd component must be constant")
    columns, matrix, rhs = corrected_system(p, q, fixed_sign)
    fields = [multiply({(0, 0): 1, (1, 0): -1},
                       {(j, 0): s for j, s in enumerate(x[arm][residue::6])})
              for arm, residue in columns]
    def specialize(poly):
        return add(*({(a+h*b, 0): c} for (a, b), c in poly.items()))
    return [add(*(multiply(specialize(a), f) for a, f in zip(row, fields)),
                scale(specialize(target), -1)) for row, target in zip(matrix, rhs)]


def counterexample_check(k):
    x_words, _ = nonperiodic_rows(k)
    x = [[1 if c == "+" else -1 for c in row] for row in x_words]
    residuals = field_residuals(6+5*k, (1, -1, 1), (1, 1), x)
    return {"counterexample_k": k, "lengths": lengths(6+5*k),
            "whole_odd_row_has_period_three": all(x[2][i] == x[2][i % 3] for i in range(len(x[2]))),
            "residual_coefficients": sum(map(len, residuals)),
            "free_fields": len(corrected_system((1, -1, 1), (1, 1))[0]),
            "remaining_24_classes_solved": False}



def endpoint_system(p, q):
    """Necessary endpoint equations for all h>=100, with all 16 free fields."""
    columns, matrix, rhs = corrected_system(p, q)
    rows = []
    for equation, (row, target) in enumerate(zip(matrix, rhs)):
        if any(not (0 <= a <= 8 and 0 <= b <= 2) for poly in [*row, target] for a, b in poly):
            raise ArithmeticError("endpoint degree bound changed")
        for alpha in range(3):
            for beta in range(-6, 7):
                terms = {}
                for column, ((arm, residue), poly) in enumerate(zip(columns, row)):
                    n = 3 if arm == 0 or arm == 1 and residue < 2 else (
                        2 if arm == 1 else 1 if residue < 3 else 0)
                    for (a, b), coefficient in poly.items():
                        power, offset = alpha-b, beta-a
                        if (power == 0 and offset >= 0) or (power == 1 and offset < n):
                            key = column, power, offset
                            terms[key] = terms.get(key, 0)+coefficient
                terms = {v: c for v, c in terms.items() if c}
                value = sum(c for (a, b), c in target.items()
                            if b < alpha or b == alpha and a <= beta)
                if terms or value:
                    rows.append((equation, alpha, beta, terms, value))
    return columns, rows


def endpoint_certificate(rows):
    """Derive forced signs; returning no certificate does not assert feasibility."""
    known, steps = {}, []
    while True:
        changed = False
        for index, (_, _, _, row, target) in enumerate(rows):
            unknown = [(v, c) for v, c in row.items() if v not in known]
            residual = target-sum(c*known[v] for v, c in row.items() if v in known)
            bound = sum(abs(c) for v, c in unknown)
            if abs(residual) > bound or (residual-bound) % 2:
                return steps, (index, None)
            for variable, coefficient in unknown:
                other = bound-abs(coefficient)
                plus = abs(residual-coefficient) <= other
                minus = abs(residual+coefficient) <= other
                if not plus and not minus:
                    return steps, (index, variable)
                if plus != minus:
                    sign = 1 if plus else -1
                    known[variable] = sign
                    steps.append((index, variable, sign))
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return None


def verify_endpoint_certificate(rows, certificate):
    if certificate is None:
        return False
    steps, (last, variable) = certificate
    known = {}
    for index, key, sign in steps:
        row, target = rows[index][3:]
        if key in known or key not in row or sign not in (-1, 1):
            return False
        residual = target-sum(c*known[v] for v, c in row.items() if v in known)
        others = sum(abs(c) for v, c in row.items() if v not in known and v != key)
        if abs(residual+row[key]*sign) <= others:
            return False
        known[key] = sign
    row, target = rows[last][3:]
    residual = target-sum(c*known[v] for v, c in row.items() if v in known)
    unknown = {v: c for v, c in row.items() if v not in known}
    if variable is None:
        bound = sum(map(abs, unknown.values()))
        return abs(residual) > bound or (residual-bound) % 2 != 0
    if variable not in unknown:
        return False
    c = unknown[variable]
    bound = sum(abs(v) for key, v in unknown.items() if key != variable)
    return abs(residual-c) > bound and abs(residual+c) > bound



def linear_consequences(rows):
    """Integer elimination with exact rational row-combination certificates."""
    basis = {}
    for index, (_, _, _, original, target) in enumerate(rows):
        row, weights = original.copy(), {index: Fraction(1)}
        while row:
            pivot = min(row)
            if pivot not in basis:
                basis[pivot] = row, target, weights
                break
            old, rhs, coefficients = basis[pivot]
            a, b = old[pivot], row[pivot]
            target = a*target-b*rhs
            row = {j: a*row.get(j, 0)-b*old.get(j, 0) for j in row.keys() | old.keys()}
            row = {j: c for j, c in row.items() if c}
            weights = {j: a*weights.get(j, 0)-b*coefficients.get(j, 0)
                       for j in weights.keys() | coefficients.keys()}
            divisor = reduce(gcd, [abs(c) for c in row.values()]+[abs(target)], 0)
            if divisor > 1:
                row, target = {j: c//divisor for j, c in row.items()}, target//divisor
                weights = {j: c/divisor for j, c in weights.items()}
            weights = {j: c for j, c in weights.items() if c}
        else:
            if target:
                basis[(99, index, 0)] = row, target, weights
    derived = [(None, None, None, row, target) for row, target, weights in basis.values()]
    return derived, [weights for row, target, weights in basis.values()]


def verify_linear_consequences(rows, derived, weights):
    if len(derived) != len(weights):
        return False
    for result, coefficients in zip(derived, weights):
        actual, rhs = {}, Fraction(0)
        for index, weight in coefficients.items():
            rhs += weight*rows[index][4]
            for key, coefficient in rows[index][3].items():
                actual[key] = actual.get(key, 0)+weight*coefficient
        actual = {key: c for key, c in actual.items() if c}
        if actual != result[3] or rhs != result[4]:
            return False
    return True


def prove_seven_masks():
    """Exclude seven masks, retaining all sixteen fields and exact row proofs."""
    if any(root_identity()):
        raise ArithmeticError("the root elimination identity failed")
    excluded = (0, 2, 4, 5, 6, 8, 9)
    for index in excluded:
        _, rows = endpoint_system(*masks()[index])
        derived, weights = linear_consequences(rows)
        if not verify_linear_consequences(rows, derived, weights):
            raise ArithmeticError("linear-combination certificate failed")
        combined = rows+derived
        if not verify_endpoint_certificate(combined, endpoint_certificate(combined)):
            raise ArithmeticError("the claimed mask exclusion failed")
    return excluded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--counterexample-k", type=int)
    parser.add_argument("--h", type=int, default=4256)
    mode.add_argument("--prove-seven-masks", action="store_true")
    args = parser.parse_args()
    try:
        if args.prove_seven_masks:
            result = {"excluded_nonconstant_masks": list(prove_seven_masks()),
                      "condition": "h>=100; the corrected root hypotheses hold",
                      "remaining_nonconstant_masks": 5, "remaining_24_classes_solved": False}
        elif args.counterexample_k is not None:
            result = counterexample_check(args.counterexample_k)
        else:
            ns = lengths(args.h)
            result = {"h": args.h, "lengths": ns, "masks": len(masks()),
                      "matrix_shape": [12, 16], "known_odd_fields": 2,
                      "free_odd_fields": 4, "root_identity_verified": not any(root_identity()),
                      "pairwise_gcds": [gcd(ns[0], ns[2]), gcd(ns[1], ns[2]), gcd(ns[0], ns[1])],
                      "remaining_24_classes_solved": False}
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
