"""Exact eventual finite criterion; see SHORT_ARM_EVENTUAL.md. Standard library."""
from __future__ import annotations
import argparse
import json


def threshold(b):
    if type(b) is not int or b < 2 or b % 2:
        raise ValueError('b must be an even integer at least two')
    return 3*b*(b-1)+2


def add(*ps):
    out = {}
    for p in ps:
        for k, v in p.items():
            out[k] = out.get(k, 0)+v
    return {k: v for k, v in out.items() if v}


def scale(p, c):
    return {k: c*v for k, v in p.items() if c*v}


def mul(p, q):
    out = {}
    for i, v in p.items():
        for j, w in q.items():
            k = tuple(a+b for a, b in zip(i, j)) if isinstance(i, tuple) else i+j
            out[k] = out.get(k, 0)+v*w
    return {k: v for k, v in out.items() if v}


def star(p):
    return {tuple(-a for a in k) if isinstance(k, tuple) else -k: v for k, v in p.items()}


def shifted(p, n):
    return {k+n: v for k, v in p.items()}


def equations(X, Y):
    """Original Laurent E1/E2, with no eliminated or periodic equations."""
    if len(X) != 3 or len(Y) != 3 or list(map(len, X)) != list(map(len, Y)):
        raise ValueError('three paired words required')
    lengths = list(map(len, X))
    result = []
    for left, right in ((X, Y), (Y, X)):
        parts = []
        for i, word in enumerate(left):
            other = [lengths[j] for j in range(3) if j != i]
            parts.append(mul(dict(enumerate(word)), add({0: 1}, {other[0]: -1}, {other[1]: -1})))
            parts.append(scale(shifted(star(dict(enumerate(right[i]))), lengths[i]-1), -1))
        result.append(add(*parts))
    return result


def candidate(a, x, y, q):
    """Finite words forced by a survivor boundary, including both tip repairs."""
    b = len(x)
    threshold(b)
    if a <= b or a % 2 or len(y) != b or any(v not in (-1, 1) for v in (*x, *y, q)):
        raise ValueError('even a>b and paired sign boundaries required')
    L = b-1
    if q == -1 and tuple(x) == (-1,)*b and tuple(y) == (1,)*b:
        U = [-1 if n//L % 2 == 0 else 1 for n in range(a)]
        V = [-v for v in U]
    elif q == 1 and tuple(y) == tuple(x)[::-1] and x[0] == x[-1]:
        def stream(word):
            out = []
            for n in range(a):
                j, k = divmod(n, L)
                out.append(-word[0] if n == 0 else ((-1)**j if k == 0 else -(-1)**j*word[k]))
            return out
        U, V = stream(x), stream(y)
    else:
        raise ValueError('boundary is not an infinite survivor')
    U[-1] -= y[-1]+q
    V[-1] -= x[-1]+1
    return [U, list(x), [1]], [V, list(y), [q]]


def solve_eventual(a, b):
    bound = threshold(b)
    if type(a) is not int or a % 2 or a < bound:
        raise ValueError(f'a must be even and at least {bound}; smaller cases are unclassified here')
    if a % (2*(b-1)):
        return {'a': a, 'b': b, 'threshold': bound, 'solvable': False, 'solutions_up_to_global_sign': 0}
    X, Y = candidate(a, (-1,)*b, (1,)*b, -1)
    if any(equations(X, Y)):
        raise ArithmeticError('construction contradicts original equations')
    return {'a': a, 'b': b, 'threshold': bound, 'solvable': True,
            'solutions_up_to_global_sign': 1, 'X': X, 'Y': Y}


def prove_identities():
    """Clear the type-B identity with independent z,R,A, not sampled lengths."""
    one = {(0, 0, 0): 1}
    z, R, A = ({(1, 0, 0): 1}, {(0, 1, 0): 1}, {(0, 0, 1): 1})
    sub = lambda p, q: add(p, scale(q, -1))
    D = mul(sub(one, z), add(one, R))
    B = mul(z, R)
    words = [scale(mul(sub(one, R), sub(one, A)), -1),
             scale(mul(sub(one, B), add(one, R)), -1), D]
    ends = [A, B, z]
    residual = []
    for i in range(3):
        j, k = [j for j in range(3) if j != i]
        residual.extend([mul(words[i], sub(sub(one, ends[j]), ends[k])),
                         scale(mul(mul(ends[i], R), star(words[i])), -1)])
    if add(*residual):
        raise ArithmeticError('uniform identity failed')
    if add(star(D), mul({(-1, -1, 0): 1}, D)):
        raise ArithmeticError('denominator reflection failed')
    # The parity obstruction uses only the interior short signs. Check its
    # coefficient identity: all variables cancel, leaving +2.
    parity_checks = 0
    for b in range(2, 34, 2):
        L = b-1
        u = [{0: 1}]+[{i: -1} for i in range(1, L)]
        v = [{0: 1}]+[{L-i: -1} for i in range(1, L)]
        u += [scale(p, -1) for p in u[:]]
        v += [scale(p, -1) for p in v[:]]
        difference = add(*(u[::2]+[scale(p, -1) for p in v[1::2]]))
        if difference != {0: 2}:
            raise ArithmeticError('parity identity failed')
        parity_checks += 1
    # Exact rejection control: alter a long coefficient of a true finite pair.
    X, Y = candidate(12, (-1,)*4, (1,)*4, -1)
    if any(equations(X, Y)):
        raise ArithmeticError('finite positive control failed')
    X[0][2] *= -1
    if not any(equations(X, Y)):
        raise ArithmeticError('corruption was not detected')
    return {'independent_variable_typeB_identity': True, 'denominator_reflection': True,
            'symbolic_parity_examples': parity_checks, 'altered_pair_rejected': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prove', action='store_true')
    p.add_argument('--solve', nargs=2, type=int, metavar=('A', 'B'))
    args = p.parse_args()
    try:
        result = solve_eventual(*args.solve) if args.solve else prove_identities()
    except ValueError as e:
        p.error(str(e))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
