"""Exact unrestricted-word elimination, not an infinite homometry construction.

See UNRESTRICTED_INSERTION_LIFT.md. Standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json

from residue_2660 import BASE, FRONTIER


def add(*polys):
    out = Counter()
    for p in polys:
        out.update(p)
    return {e: c for e, c in out.items() if c}


def shift(p, d=0, factor=1):
    return {e+d: factor*c for e, c in p.items() if factor*c}


def star(p):
    return {-e: c for e, c in p.items()}


def mul(p, q):
    out = Counter()
    for e, c in p.items():
        out.update({e+f: c*d for f, d in q.items()})
    return {e: c for e, c in out.items() if c}


def polynomial(word):
    return {d: s for d, s in enumerate(word, 1) if s}


def validate(lengths, h, centre, words):
    if (len(lengths) != 3 or any(type(n) is not int for n in lengths)
            or not lengths[0] > lengths[1] > lengths[2] >= 1
            or type(h) is not int or not 1 <= h < lengths[0]
            or type(centre) is not int or centre not in (-1, 1)):
        raise ValueError('require A>B>C>=1, 1<=h<A and a signed centre')
    if len(words) != 3 or any(len(w) != n for w, n in zip(words, lengths)):
        raise ValueError('three complete arm words required')
    for i, w in enumerate(words):
        for d, s in enumerate(w, 1):
            allowed = (0,) if i == 0 and d in (h, lengths[0]) else (-1, 1)
            if type(s) is not int or s not in allowed:
                raise ValueError('only the two stated holes may have sign zero')


def reduction(lengths, h, centre, prefix, arm2, arm3):
    """Return Q,N with Q[0]=1 and Q*S1=N necessary for full homometry.

    Prefix is the fixed word at depths 1..h-1. No assumption on insertions.
    The returned D,M also allow a final, undivided identity check.
    """
    a, b, c = lengths
    if not a > b > c >= 1 or not 1 <= h < a or centre not in (-1, 1):
        raise ValueError('invalid geometry or centre')
    if (len(prefix) != h-1 or len(arm2) != b or len(arm3) != c
            or any(type(s) is not int or s not in (-1, 1)
                   for w in (prefix, arm2, arm3) for s in w)):
        raise ValueError('literal signed prefix and other two arms required')
    d = add({1: 1, b+1: -1, c+1: -1}, {-h: -1, 1-h: 1})
    hole_factor = mul({0: -1, 1: 1}, {h: 1, a: 1})
    r = shift(add({1: 1, a+1: -1, b+1: -1, c+1: -1},
                  hole_factor), factor=centre)
    for i, word in ((1, arm2), (2, arm3)):
        s = polynomial(word)
        coefficient = add({1: 1},
                          {lengths[j]+1: -1 for j in range(3) if j != i},
                          hole_factor)
        r = add(r, mul(coefficient, s), shift(star(s), lengths[i]+1, -1))
    p = polynomial(prefix)
    correction = add(shift(star(p), h), shift(p, -h, -1))
    r = add(r, mul({0: -1, 1: 1}, correction))
    m = shift(r, factor=-1)
    determinant = add(mul(d, star(d)), {0: -1})
    offset = b+h+1
    q = shift(determinant, offset)
    numerator = shift(add(mul(star(d), m), shift(star(m), a)), offset)
    assert min(q) == 0 and q[0] == 1
    return {'Q': q, 'N': numerator, 'D': d, 'M': m}


def complete(lengths, h, centre, prefix, arm2, arm3):
    """Unique possible first arm, or an exact obstruction to this other-arm pair."""
    system = reduction(lengths, h, centre, prefix, arm2, arm3)
    q, n = system['Q'], system['N']
    if any(e < 1 and v for e, v in n.items()):
        return {'valid': False, 'reason': 'numerator before first depth'}
    a = lengths[0]
    coefficients = [0]*(a+1)
    positive = [(e, v) for e, v in q.items() if 0 < e <= a]
    for depth in range(1, a+1):
        value = n.get(depth, 0) - sum(v*coefficients[depth-e]
                                    for e, v in positive if e <= depth)
        coefficients[depth] = value
        expected = (0,) if depth in (h, a) else (-1, 1)
        if value not in expected or (depth < h and value != prefix[depth-1]):
            return {'valid': False, 'reason': 'forced first-arm coefficient',
                    'depth': depth, 'coefficient': value}
    first = polynomial(coefficients[1:])
    residual = add(mul(system['D'], first), shift(star(first), a, -1),
                   shift(system['M'], factor=-1))
    balance = centre + sum(coefficients) + sum(arm2) + sum(arm3)
    if residual or balance:
        return {'valid': False, 'reason': 'terminal identity or balance',
                'balance': balance, 'residual_terms': len(residual)}
    return {'valid': True, 'arm1': coefficients[1:]}


def identity(lengths, h, centre, words):
    """(1-z) times the signed occupied-shell polynomial, for balanced words."""
    validate(lengths, h, centre, words)
    if centre + sum(map(sum, words)):
        raise ValueError('equal sizes required')
    system = reduction(lengths, h, centre, words[0][:h-1], words[1], words[2])
    s = polynomial(words[0])
    return add(mul(system['D'], s), shift(star(s), lengths[0], -1),
               shift(system['M'], factor=-1))


def prefix_realization(k):
    """Preserve every seed sign; take earliest inserted negatives per residue."""
    if type(k) is not int or k < 1:
        raise ValueError('positive integer k required')
    words = []
    for i, base in enumerate(BASE):
        cut = 19 if i == 0 else 0
        seed = [0 if ch == '0' else 1 if ch == '+' else -1 for ch in FRONTIER[i]]
        word = seed[:cut]
        remaining = [(k*base+(k % 2)*(-1)**r)//2 for r in range(2660)]
        for depth in range(cut+1, cut+2660*k*base+1):
            r = depth % 2660
            negative = remaining[r] > 0
            word.append(-1 if negative else 1)
            remaining[r] -= negative
        assert not any(remaining)
        words.append(word+seed[cut:])
    return words


def all_word_obstruction(k):
    """Literal actual-distance tail counter, independent of inserted signs.

    Every pair at A+B-61 lies in these retained seed tails. Enumerate
    vertices and compare distances, rather than using shell/elimination rows.
    """
    if type(k) is not int or k < 1:
        raise ValueError('positive integer k required')
    t = 2660*k+1
    a, b, c = (n*t for n in BASE)
    distance = a+b-61
    assert distance > a+c
    vertices1 = [(depth+99*(t-1), sign)
                 for depth, sign in enumerate(FRONTIER[0], 1)
                 if 38 <= depth <= 98]
    vertices2 = [(depth+79*(t-1), sign)
                 for depth, sign in enumerate(FRONTIER[1], 1)
                 if 19 <= depth <= 79]
    positive = negative = pairs = 0
    for depth1, sign1 in vertices1:
        for depth2, sign2 in vertices2:
            if depth1+depth2 == distance:
                pairs += 1
                positive += sign1 == sign2 == '+'
                negative += sign1 == sign2 == '-'
    assert pairs == 61 and positive-negative == 1
    return {'k': k, 'lengths': [a, b, c], 'distance': distance,
            'positive_pairs': positive, 'negative_pairs': negative,
            'pairs_in_shell': pairs, 'difference': positive-negative,
            'all_insertion_words_excluded': True,
            'scope': 'fixed FRONTIER signs, holes and cuts only',
            'arbitrary_tree_obstruction_claimed': False}


def distance_difference(lengths, h, centre, words, distance):
    """Independent shell count from interval sums, at an actual distance.

    This uses occupied neighbours, not the elimination identity or residues.
    Half the result is positive-pair minus negative-pair multiplicity.
    """
    validate(lengths, h, centre, words)
    if centre + sum(map(sum, words)) or not 1 <= distance <= sum(sorted(lengths)[-2:]):
        raise ValueError('balanced words and a positive distance through diameter required')
    prefixes = []
    for w in words:
        p = [0]
        for sign in w:
            p.append(p[-1]+sign)
        prefixes.append(p)
    def interval(i, lo, hi):
        lo, hi = max(1, lo), min(lengths[i], hi)
        return prefixes[i][hi]-prefixes[i][lo-1] if lo <= hi else 0
    def sign(i, depth):
        return words[i][depth-1] if 1 <= depth <= lengths[i] else 0
    holes = ((0, h), (0, lengths[0]))
    d = distance
    total = centre*(sum(n >= d for n in lengths)-sum(v == d for _, v in holes))
    for i, length in enumerate(lengths):
        total += interval(i, 1, length-d)+interval(i, d+1, length)+sign(i, d)
        for j, other in enumerate(lengths):
            if i != j:
                total += interval(i, d-other, d-1)
        for j, v in holes:
            total -= sign(i, v-d)+sign(i, v+d) if i == j else sign(i, d-v)
    assert total % 2 == 0
    return total//2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--k', type=int, default=1)
    parser.add_argument('--complete', action='store_true', help='force arm one from prefix-realized arms two and three')
    args = parser.parse_args()
    try:
        words = prefix_realization(args.k)
    except ValueError as error:
        parser.error(str(error))
    lengths = tuple(map(len, words))
    result = {'k': args.k, 'lengths': lengths, 'seed_preserved': True,
              'balance': -1+sum(map(sum, words)),
              'actual_distance_differences': {d: distance_difference(lengths, 19, -1, words, d) for d in (1, 2)},
              'prefix_class_obstructed_for_every_k': True,
              'all_word_obstruction': all_word_obstruction(args.k),
              'unrestricted_family_solved': False}
    if args.complete:
        result['completion'] = complete(lengths, 19, -1, words[0][:18], words[1], words[2])
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
