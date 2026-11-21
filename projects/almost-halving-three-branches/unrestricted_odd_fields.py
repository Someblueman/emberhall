"""A five-fold construction for every positive t divisible by nine.

Also retains the corrected sixteen-field reduction for the unresolved classes.
"""
from __future__ import annotations

import argparse
from itertools import product
from fractions import Fraction
from functools import reduce
import json
from math import gcd
from pathlib import Path

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


# Coarse vertices start at depth one; edge words start at index zero.
FAMILY_COARSE = (
    ('+++-----------++++++++++++++++++++++', '+++-----------+++++++++++++++++++++++++-----------++++'),
    ('---+++++++-------------+-+----------', '---+++++++-------------+-+-------------+++++++----'),
    ('+++++++----+-+--+-++-+--+-+----+++++', '+++++++----+-+--+-++-+--+-+----++++++++'),
)
FAMILY_EDGES = (
    ('--+-+--++-++--+-+-', '--+-+-+++-++--+-+---+-+-+++-++--+-+-', '--+-+-+++-++--+-+---+-+-+++-+++++-++'),
    ('-+---+-----+-+-+-+', '-+---+-----+---+---+---+-----+---+--', '-+---+-----+-----------+-----+--'),
    ('++++--+++++-++-++-', '++++--+++++-++-+++++++--+++++-++-+++', '+++++-+++++-++-+++++-'),
)


def family_proof(edges=FAMILY_EDGES):
    """Three exact identities in independent z,V, where V=z**(36*k)."""
    from paired_edge_five import word_polynomial
    if (len(edges) != 3 or any(tuple(map(len, row)) != (18, 36, tail)
                               for row, tail in zip(edges, (36, 32, 21)))):
        raise ValueError("require three edge prefix/block/tail patterns of the stated lengths")
    one, V = {(0, 0): 1}, {(0, 1): 1}
    D = add(one, {(36, 0): -1})
    ends = [{(n, 1): 1} for n in (54, 50, 39)]
    coarse, X, E = [], [], []
    p, q = masks()[1]
    for arm, ((block, tail), (prefix, repeat, suffix)) in enumerate(zip(FAMILY_COARSE, edges)):
        coarse.append(add(multiply(word_polynomial(block, 1), add(one, scale(V, -1))),
                          multiply(V, D, word_polynomial(tail, 1))))
        for masked, target in ((False, X), (True, E)):
            def poly(word, start):
                result = word_polynomial(word, start)
                if masked:
                    def epsilon(j):
                        return p[j % 3]*q[j % 2] if arm == 0 else q[j % 2] if arm == 1 else p[j % 3]
                    result = {key: value*epsilon(key[0]) for key, value in result.items()}
                return result
            target.append(add(multiply(D, poly(prefix, 0)),
                              multiply(add(one, scale(V, -1)), poly(repeat, 18)),
                              multiply(V, D, poly(suffix, 18))))
    shell = multiply(D, add(one, *(scale(a, -1) for a in ends)))
    first, second = {}, {}
    for i in range(3):
        j, k = (j for j in range(3) if j != i)
        K = add(one, scale(ends[j], -1), scale(ends[k], -1))
        star = {(-a, -b): c for (a, b), c in coarse[i].items()}
        shell = add(shell, multiply(coarse[i], K), multiply(ends[i], {(36, 0): 1}, star))
        first = add(first, multiply(X[i], K), scale(E[i], -1))
        second = add(second, multiply(add(E[i], scale(X[i], -1)), ends[j], ends[k]),
                     scale(multiply(E[i], add(ends[j], ends[k])), -1))
    return {"coarse_shell": shell, "first_edge_equation": first,
            "reversed_second_edge_equation": second}


def family_rows(k):
    if type(k) is not int or k < 0:
        raise ValueError("family k must be a nonnegative integer")
    coarse = [block*k+tail for block, tail in FAMILY_COARSE]
    x = [prefix+block*k+tail for prefix, block, tail in FAMILY_EDGES]
    p, q = masks()[1]
    y = []
    for arm, row in enumerate(x):
        eps = [p[j % 3]*q[j % 2] if arm == 0 else q[j % 2] if arm == 1 else p[j % 3]
               for j in range(len(row))]
        y.append("".join(c if e == 1 else "+" if c == "-" else "-"
                         for c, e in zip(row, eps))[::-1])
    return coarse, x, y


def family_pair(k):
    """Construct on (271+180k,251+180k,195+180k), keeping original distances."""
    coarse, x, y = family_rows(k)
    lengths = (271+180*k, 251+180*k, 195+180*k)
    left, right = [(0, 0)], []
    for arm, (old, first, second) in enumerate(zip(coarse, x, y), 1):
        for edge, signs in enumerate(zip(first, second, old)):
            a, b, c = signs
            for offset, sign in enumerate((a, a, b, b, c), 1):
                (left if sign == "+" else right).append((arm, 5*edge+offset))
    return {"lengths": lengths, "left": left, "right": right, "family_k": k,
            "omitted": [(1, lengths[0]), (2, lengths[1])]}


def family_parameter(t):
    if type(t) is not int or t <= 0 or t % 9:
        raise ValueError("family t must be a positive integer divisible by nine")
    return 266*(t//9)-1


# Explicit row-combination certificates; each token is w-power,V-power,coefficient.
PARITY_CERTIFICATES = {
    1: {
        "weights": (
            '8,5,-1 7,4,1 6,2,-1 5,4,3 4,3,-3 3,5,1 2,3,-1 1,2,1',
            '6,3,1 5,1,-1 4,4,-2 2,0,2 1,3,1 0,1,-1',
            '6,4,1 5,2,-1 1,4,1 0,2,-1',
            '8,4,-1 5,4,-2 5,3,3 4,2,-1 3,4,1 2,3,1 2,2,-1',
            '7,4,2 6,2,-2 4,3,-2 3,1,2',
            '4,4,-2 3,2,2 1,3,2 0,1,-2',
            '8,6,1 7,5,1 6,3,-1 5,5,-3 4,4,1 3,6,-1 3,2,2 2,4,1 1,3,-1',
            '6,4,-1 5,2,1 3,3,2 2,1,-2 1,4,1 0,2,-1',
            '6,5,1 5,3,-1 3,4,-2 2,2,2 1,5,-1 0,3,1',
            '8,5,1 5,4,-3 4,3,3 3,5,-1 2,4,1 2,3,1 1,2,-2',
            '',
            '',
        ),
        "row": {
            (0, 0): '3,0,-1 0,0,1',
            (2, 1): '2,0,2',
            (2, 2): '4,0,-2',
            (2, 4): '5,0,-2',
            (2, 5): '2,0,2',
        },
        "rhs": '5,1,-1 4,1,-1 3,1,1 2,0,-1 1,0,-1 0,0,-1',
        "lift": '2,0,-1 3,0,-3 4,0,-2',
    },
    3: {
        "weights": (
            '8,1,1 6,2,-1 3,2,-1 0,1,1',
            '5,2,2 4,0,-2',
            '7,2,-2 6,0,2',
            '9,2,1 6,1,-1 3,1,-1 1,2,1',
            '3,2,-2 2,0,2',
            '5,2,2 4,0,-2',
            '8,2,-1 6,3,1 3,3,-1 2,1,2 0,2,-1',
            '',
            '',
            '9,3,-1 6,2,1 3,2,1 1,3,1 0,1,-2',
            '',
            '',
        ),
        "row": {
            (1, 0): '5,0,1 0,0,-1',
            (1, 1): '7,0,-1 2,0,1',
            (1, 2): '9,0,1 4,0,-1',
            (2, 1): '7,0,-1 2,0,-1',
            (2, 2): '9,0,1 4,0,1',
            (2, 4): '5,0,2',
            (2, 5): '7,0,-2',
        },
        "rhs": '10,1,1 9,1,1 8,1,-1 7,1,-1 6,1,-1 4,0,-1 3,0,-1 2,0,1 1,0,1 0,0,1',
        "lift": '8,0,1 7,0,1 5,0,-1 4,0,1 3,0,1',
    },
    7: {
        "weights": (
            '11,2,-1 9,3,2 8,1,-1 3,2,1 2,0,-2 0,1,1',
            '13,2,1 11,3,-1 5,2,1 3,3,-1',
            '5,3,2 4,1,-2',
            '12,3,-2 11,1,2',
            '6,3,2 5,1,-2',
            '8,3,-2 7,1,2',
            '11,3,1 8,2,-1 3,3,-1 2,1,2 0,2,-1',
            '13,3,-1 11,4,1 5,3,-1 3,4,-1 2,2,2',
            '',
            '',
            '',
            '',
        ),
        "row": {
            (0, 0): '8,0,1 3,0,-1',
            (1, 3): '11,0,1 6,0,-1',
            (1, 4): '5,0,-1 0,0,1',
            (1, 5): '7,0,1 2,0,-1',
            (2, 0): '8,0,-1 3,0,-1',
            (2, 2): '4,0,-2',
            (2, 3): '11,0,1 6,0,1',
            (2, 5): '7,0,1 2,0,1',
        },
        "rhs": '12,1,1 11,1,1 10,1,-1 9,1,-1 8,1,-1 4,0,1 3,0,1 2,0,1 1,0,-1 0,0,-1',
        "lift": '10,0,2 9,0,2 8,0,2 7,0,1 6,0,1 5,0,1 3,0,-1 2,0,-1',
    },
}


def parity_proof(certificates=PARITY_CERTIFICATES):
    """Prove necessary h residues for three masks, keeping every free field."""
    def unpack(text):
        triples = [tuple(map(int, token.split(","))) for token in text.split()]
        return {(a, b): c for a, b, c in triples}
    one, w, V = {(0, 0): 1}, {(1, 0): 1}, {(0, 1): 1}
    D = add(one, scale(w, -1))
    factor = add({(1, 2): 1}, scale(one, -1))
    conclusions = {}
    for mask in (1, 3, 7):
        item = certificates[mask]
        columns, matrix, rhs = corrected_system(*masks()[mask])
        weights = [unpack(text) for text in item["weights"]]
        row = {column: unpack(text) for column, text in item["row"].items()}
        target = unpack(item["rhs"])
        if (len(weights) != 12 or not row.keys() <= set(columns)
                or any(a < 0 or b for poly in row.values() for a, b in poly)
                or any(a < 0 or b not in (0, 1) for a, b in target)):
            raise ArithmeticError("unsupported parity certificate shape")
        denominator = multiply({(0, 0): 2}, V, factor)
        if mask != 3:
            denominator = multiply(denominator, V, {(1 if mask == 1 else 3, 0): 1})
        if mask == 1:
            denominator = multiply(denominator, add({(3, 1): 1}, scale(one, -1)))
        for j, column in enumerate(columns):
            if add(*(multiply(weights[i], matrix[i][j]) for i in range(12)),
                   scale(multiply(denominator, row.get(column, {})), -1)):
                raise ArithmeticError("parity row-combination certificate failed")
        if add(*(multiply(weight, value) for weight, value in zip(weights, rhs)),
               scale(multiply(denominator, D, target), -1)):
            raise ArithmeticError("parity right-side certificate failed")
        period = 3 if mask == 1 else 5
        delta = add({(period, 0): 1}, scale(one, -1))
        geometric = {(j, 0): 1 for j in range(period)}
        offsets = {col: 3 if col[0] == 0 or col[0] == 1 and col[1] < 2 else
                   2 if col[0] == 1 else 1 if col[1] < 3 else 0 for col in row}
        slope = {(a, 0): c for (a, b), c in target.items() if b == 1}
        increment = add(multiply(delta, slope), scale(multiply(geometric,
                        add(*(multiply(poly, {(offsets[col], 0): 1})
                              for col, poly in row.items()))), -1))
        if add(increment, multiply({(0, 0): 2}, delta, unpack(item["lift"]))):
            raise ArithmeticError("parity periodicity certificate failed")
        # Each coefficient of the unknown correction has factor 1-w**period modulo two.
        for poly in row.values():
            for residue in range(period):
                if sum(c for (a, b), c in poly.items() if a % period == residue) % 2:
                    raise ArithmeticError("uncancelled parity correction")
        allowed = []
        for h in range(period):
            residual = add(*({(a+h*b, 0): c} for (a, b), c in target.items()),
                           *(scale(multiply(poly, {(j, 0): 1 for j in range(h+offsets[col])}), -1)
                             for col, poly in row.items()))
            if any(c % 2 for c in residual.values()):
                raise ArithmeticError("odd reference-row residual")
            remainder = [sum(c//2 for (a, b), c in residual.items() if a % period == r) % 2
                         for r in range(period)]
            if not any(remainder):
                allowed.append(h)
        conclusions[mask] = {"modulus": period, "necessary_residues": allowed}
    return conclusions


def constant_mask_proof():
    """Exact elimination checks supporting the four constant-mask exclusions."""
    from progression_target import _add, _mul, _scale, _mon
    one, A, B, C = _mon(), _mon(1), _mon(r=1), _mon(s=1)
    ends = A, B, C
    for i in range(3):
        j, k = (j for j in range(3) if j != i)
        difference = _scale(_add(_mul(ends[j], ends[k]),
                                 _scale(ends[j], -1), _scale(ends[k], -1), one), -2)
        if _add(difference, _scale(_mul(_add(one, _scale(ends[j], -1)),
                                       _add(one, _scale(ends[k], -1))), 2)):
            raise ArithmeticError("difference-field elimination failed")
    numerator = _add(_scale(_mul(_add(_scale(one, 2), _scale(A, -1), _scale(C, -1)),
                                  _add(one, _scale(B, -1))), -1),
                     _mul(_add(_scale(one, 2), _scale(A, -1), _scale(B, -1)),
                          _add(one, _scale(C, -1))))
    if _add(numerator, _scale(_mul(_add(B, _scale(C, -1)),
                                  _add(one, _scale(A, -1))), -1)):
        raise ArithmeticError("constant-row quotient failed")
    # At a primitive thirteenth root, the two parity equations are inconsistent
    # with |C|=1. Check the exact denominator-cleared compatibility polynomial.
    one, z, C = {(0, 0): 1}, {(1, 0): 1}, {(0, 1): 1}
    A, B = {(15, 1): 1}, {(11, 1): 1}
    ao = scale(multiply(z, add(one, scale(A, -1))), -1)
    be = scale(add(one, scale(B, -1)), -1)
    ce, co = add(one, scale(multiply(z, C), -1)), add(z, scale(C, -1))
    common = add(scale(one, 2), scale(A, -1), scale(B, -1))
    first = add(scale(multiply(C, ao), -1),
                multiply(add(scale(one, 2), scale(A, -1)), be), multiply(common, ce))
    second = add(multiply(add(scale(one, 2), scale(B, -1)), ao),
                 scale(multiply(C, be), -1), multiply(common, co))
    actual = multiply({(2, 0): 1}, add(multiply(C, first), scale(multiply(B, second), -1)))
    expected = multiply({(0, 2): 2}, add(one, scale(z, -1)),
                        add(multiply(C, z), one, z, {(2, 0): 1}))
    reduced = add(*({(a % 13, b): c} for (a, b), c in add(actual, scale(expected, -1)).items()))
    if reduced:
        raise ArithmeticError("alternating-mask root compatibility failed")
    return True


def obstruction_proof():
    """No paired edge rows on the remaining affine classes; not a target refutation."""
    prove_seven_masks()
    if parity_proof() != {1: {"modulus": 3, "necessary_residues": [0]},
                          3: {"modulus": 5, "necessary_residues": []},
                          7: {"modulus": 5, "necessary_residues": [1]}}:
        raise ArithmeticError("unexpected surviving nonconstant mask")
    constant_mask_proof()
    residues = [t for t in range(495) if t % 3 == 0 and t % 15 in (0, 6, 12)
                and t % 11 not in (1, 6, 9) and t % 9]
    for t in residues:
        a, b, c = 18+1064*t, 14+1064*t, 3+1064*t
        h = 532*(t//3)
        if ((gcd(a, b), gcd(a, c), gcd(b, c)) != (2, 3, 1) or a % 22 == 0
                or h < 100 or h % 3 == 0 or h % 5 == 1):
            raise ArithmeticError("affine root hypotheses failed")
    return {"proof": "PASS", "excluded_residues_mod_495": residues,
            "excluded_construction": "all paired edge rows and full five-fold prefixes",
            "original_target_ruled_out": False}


# Each arm is prefix + block*k + tail. Zero marks an actual omitted vertex.
INTERIOR_FAMILY = (
    ('-+-+-+-+-+-+-+-+-+0-+-+----+-+++++-++-+-+-+-+-+-+-+-+-+--+-+-+-+++++++++-+-+-+-+++++++-+-++--++++++++',
     '++++++++++++++++++++++++++++++++++++++++++++++++++++++++',
     '++++++++--++-+-+++++++-+-+-+-+++++++++-+-+-+--+-+-+-+-+-+-+-+-+-++-+++++-+----+-+-+-+-+-+-+-+-+-+-+-+0'),
    ('-+-+-+-+-+-+-+-+-+-+-+-++++-+-----+--+-+-+-+-+-+-+-+-+-+-+-+-------+-+--++-+-+-+-+---------',
     '+---------+-+-+-+-----------------------+-+-+-+---------',
     '+---------+-+-+-+-++--+-+-------+-+-+-+-+-+-+-+-+-+-+-+--+-----+-++++-+-+-+-+-+-+-+-+-+-+-+-'),
    ('+-+-++++-+-----+--+-+-+----+-+++++-+++-+-+-+---------+-+-+-+-+-',
     '+-+-+-+-+-+---------+-+-+-+---+-+-+-+---------+-+-+-+-+-',
     '+-+-+-+-+-+---------+-+-+-+++-+++++-+----+-+-+--+-----+-++++-+-+'),
)


def interior_proof(patterns=INTERIOR_FAMILY):
    """Return the exact corrected shell numerator in independent z,V.

    V later becomes z**(56*k). Distances still use the original tree,
    including paths through the missing long-arm vertex at depth 19.
    """
    if len(patterns) != 3:
        raise ValueError("require three prefix/block/tail rows")
    for i, (prefix, block, tail) in enumerate(patterns):
        if (len(prefix) != (101, 91, 63)[i] or len(block) != 56
                or len(prefix)+len(tail) != (203, 183, 127)[i]
                or set(prefix+block+tail)-set("+-0")):
            raise ValueError("invalid interior-family word")
        zeros = [(part, j) for part, word in enumerate((prefix, block, tail))
                 for j, s in enumerate(word) if s == "0"]
        if zeros != ([(0, 18), (2, 101)] if i == 0 else []):
            raise ValueError("the two actual omitted vertices must stay fixed")

    def word(text, start):
        return {(start+j, 0): 1 if s == "+" else -1
                for j, s in enumerate(text) if s != "0"}

    D = {(0, 0): 1, (56, 0): -1}
    V = {(0, 1): 1}
    one_minus_V = {(0, 0): 1, (0, 1): -1}
    ends = [{(n, 1): 1} for n in (203, 183, 127)]
    prefixes = [word(p, 1) for p, _, _ in patterns]
    nums = [add(multiply(D, prefixes[i]),
                multiply(word(block, len(prefix)+1), one_minus_V),
                multiply(D, V, word(tail, len(prefix)+1)))
            for i, (prefix, block, tail) in enumerate(patterns)]
    star = lambda p: {(-a, -b): c for (a, b), c in p.items()}
    shift = lambda p, n: multiply({(n, 0): 1}, p)
    kernels = [add({(0, 0): 1}, *(scale(e, -1) for j, e in enumerate(ends) if j != i))
               for i in range(3)]
    shell = add(multiply(D, add({(0, 0): 1}, *(scale(e, -1) for e in ends))),
                *(multiply(n, kernel) for n, kernel in zip(nums, kernels)),
                *(shift(multiply(e, star(n)), 56) for e, n in zip(ends, nums)))
    # D times the signed distance enumerator seen from the fixed hole.
    near = add(shift(D, 19),
               multiply(D, add(*({(abs(p-19), 0): c} for (p, _), c in prefixes[0].items()))),
               shift(add(nums[0], scale(multiply(D, prefixes[0]), -1)), -19),
               shift(add(nums[1], nums[2]), 19))
    # All long-arm retained vertices are before its omitted terminal tip.
    far = add(multiply(D, ends[0]),
              scale(shift(multiply(ends[0], star(nums[0])), 56), -1),
              multiply(ends[0], add(nums[1], nums[2])))
    return add(shift(shell, 1),
               scale(multiply({(0, 0): 1, (1, 0): -1}, add(near, far)), -1))


def interior_pair(k):
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    left, right = [(0, 0)], []
    for arm, (prefix, block, tail) in enumerate(INTERIOR_FAMILY, 1):
        for depth, sign in enumerate(prefix+block*k+tail, 1):
            if sign != "0":
                (left if sign == "+" else right).append((arm, depth))
    ns = tuple(n+56*k for n in (203, 183, 127))
    return {"lengths": ns, "left": left, "right": right,
            "omitted": [(1, 19), (1, ns[0])],
            "construction": "interior-hole family T(203+56k,183+56k,127+56k)"}


def interior_parameter(t):
    if type(t) is not int or t < 1:
        raise ValueError("t must be a positive integer")
    return 95*t-2


def bipartition_hole_cases():
    """Exhaust the parity-colouring ansatz on (91+2r,71+2r,15+2r).

    r and x are formal variables. A triple (a,b,c) denotes a*r+b*x+c.
    Matching the three monomials leaves 36 exact linear systems, not a
    bounded search over r or hole depths. See UNRESTRICTED_ODD_FIELDS.md.
    """
    from itertools import permutations

    A = [(1, 0, n) for n in (46, 36, 8)]
    X = (0, 1, 0)

    def plus(*terms):
        return tuple(sum(t[k] for t in terms) for k in range(3))

    def minus(term):
        return tuple(-v for v in term)

    cases = set()
    for i in (0, 1):  # A diameter pair forces one of these two tips to be omitted.
        for j in range(3):
            others = [k for k in range(3) if k != i]
            left = [X, A[i], plus(*(A[k] for k in others))]
            if i == j:
                right = [plus(A[i], minus(X)), *(plus(X, A[k]) for k in others)]
            else:
                k = 3-i-j
                right = [plus(A[j], (0, 0, 1), minus(X)), plus(X, A[k]),
                         plus(A[i], X, (0, 0, -1))]
            for perm in permutations(right):
                rows = [plus(u, minus(v)) for u, v in zip(left, perm)]
                independent = next(((u, v) for u, v in permutations(rows, 2)
                                    if u[0]*v[1] != v[0]*u[1]), None)
                if independent is None:
                    nonzero = next((u for u in rows if u[:2] != (0, 0)), None)
                    if nonzero is None:
                        inconsistent = any(u[2] for u in rows)
                    else:
                        k = 0 if nonzero[0] else 1
                        inconsistent = any(nonzero[k]*u[2] != u[k]*nonzero[2]
                                           for u in rows)
                    if not inconsistent:
                        raise ArithmeticError("an unexamined affine branch remains")
                    continue
                u, v = independent
                determinant = u[0]*v[1]-v[0]*u[1]
                r = Fraction(u[1]*v[2]-v[1]*u[2], determinant)
                x = Fraction(u[2]*v[0]-v[2]*u[0], determinant)
                if any(a*r+b*x+c for a, b, c in rows):
                    continue
                if r.denominator != 1 or x.denominator != 1 or r < 0:
                    continue
                lengths = tuple(int(r)+n for n in (46, 36, 8))
                if not 1 <= x <= lengths[j] or (i == j and x == lengths[i]):
                    continue
                cases.add((int(2*r), i+1, j+1, int(2*x-1)))
    return [{"offset": q, "lengths": tuple(q+n for n in (91, 71, 15)),
             "omitted": ((i, q+(91, 71, 15)[i-1]), (j, depth))}
            for q, i, j, depth in sorted(cases)]


def bipartition_hole_proof():
    cases = bipartition_hole_cases()
    if any(case["offset"] % 5320 == 0 for case in cases):
        raise ArithmeticError("the affine family has a parity-colouring candidate")
    return {"proof": "PASS", "construction": "the two depth-parity classes, minus two odd vertices",
            "all_even_offsets_exhausted": True, "cases": cases,
            "affine_parity_colouring_excluded": True,
            "original_target_ruled_out": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--counterexample-k", type=int)
    parser.add_argument("--h", type=int, default=4256)
    mode.add_argument("--prove-seven-masks", action="store_true")
    mode.add_argument("--prove-family", action="store_true")
    mode.add_argument("--prove-parity", action="store_true")
    mode.add_argument("--prove-obstruction", action="store_true")
    mode.add_argument("--prove-bipartition-holes", action="store_true")
    mode.add_argument("--prove-interior", action="store_true")
    mode.add_argument("--interior-k", type=int)
    mode.add_argument("--interior-t", type=int)
    mode.add_argument("--family-k", type=int)
    mode.add_argument("--family-t", type=int)
    mode.add_argument("--check", type=Path)
    parser.add_argument("--witness", type=Path)
    args = parser.parse_args()
    try:
        if args.witness and all(x is None for x in (args.family_k, args.family_t, args.interior_k, args.interior_t)):
            parser.error("--witness requires a family parameter")
        if args.prove_interior:
            if interior_proof():
                raise ArithmeticError("the interior-hole shell identity failed")
            result = {"proof": "PASS", "family": "T(203+56k,183+56k,127+56k)",
                      "affine_parameters": "every positive t; k=95t-2",
                      "affine_family_solved": True, "universal_milestone_solved": False}
        elif args.prove_bipartition_holes:
            result = bipartition_hole_proof()
        elif args.prove_obstruction:
            result = obstruction_proof()
        elif args.prove_parity:
            result = parity_proof()
        elif args.prove_family:
            if any(family_proof().values()):
                raise ArithmeticError("the new family identity failed")
            result = {"proof": "PASS", "family": "every positive t divisible by nine",
                      "universal_milestone_solved": False}
        elif args.check or any(x is not None for x in (args.family_k, args.family_t, args.interior_k, args.interior_t)):
            from paired_edge_five import check_pair
            if args.check:
                pair = json.loads(args.check.read_text())
            elif args.interior_k is not None or args.interior_t is not None:
                pair = interior_pair(args.interior_k if args.interior_k is not None else interior_parameter(args.interior_t))
            else:
                pair = family_pair(args.family_k if args.family_k is not None else family_parameter(args.family_t))
            result = check_pair(pair)
            if args.witness:
                args.witness.write_text(json.dumps(pair, separators=(",", ":"))+"\n")
            print(json.dumps(result, sort_keys=True))
            return 0 if result["homometric"] else 1
        elif args.prove_seven_masks:
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
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
