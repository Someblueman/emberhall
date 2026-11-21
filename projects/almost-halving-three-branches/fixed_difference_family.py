"""Exact optimal pairs on T(c+76,c+56,c), every positive integer c.

Six affine word certificates, a finite published-in-project control, and the
Euler-cell theorem cover the domain. See FIXED_DIFFERENCE_FAMILY.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from published_cases import check_pair
from ratio_51_33_10 import original_tree

# Each row is prefix, repeat block, tail. These are constructive proof data.
FAMILIES = {
    23: (
        ('+-+-+-+-+-+-+-+-+-0-+-++++++++++++++++-+-++++++++',
         '++++++++++++++++++++++++++++++++++++++++++++++++++++++++',
         '++++++++-+-++++++++++++++++-+--+-+-+-+-+-+-+-+-+-0'),
        ('+-+-+-+-+-+-+-+-+-++-+----------------+',
         '-+-------------------+-+-+-+-+-+-+-+-------------------+',
         '-+----------------+-++-+-+-+-+-+-+-+-+-+'),
        ('+-+--------',
         '---------+-+-+-+-+-+-+-+-+-----+-+-+-+-+-+-+-+-+--------',
         '---------+-+'),
    ),
    31: (
        ('+-+-+-+-+-+-+-+-+-0-+-+-+-+-+-++++++++-+-+-+-+-+-++++',
         '++++++++++++++++++++++++++++++++++++++++++++++++++++++++',
         '++++-+-+-+-+-+-++++++++-+-+-+-+-+--+-+-+-+-+-+-+-+-+-0'),
        ('+-+-+-+-+-+-+-+-+-++-+-+-+-+-+--------+-+-+',
         '-+-+-+-------------------+-+-+-+-------------------+-+-+',
         '-+-+-+--------+-+-+-+-+-++-+-+-+-+-+-+-+-+-+'),
        ('+-+-+-+-+-+----',
         '-----+-+-+-+-+-+-+-+-+-------------+-+-+-+-+-+-+-+-+----',
         '-----+-+-+-+-+-+'),
    ),
    39: (
        ('+-+-+-+-+-+-+-+-+-0-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-',
         '--------------------------------------------------------',
         '-+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-0'),
        ('+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+',
         '-+-+-+-+-+++++++++++++++++++++++++++++++++++++++-+-+-+-+',
         '-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+'),
        ('+-+-+-+-+-+-+-+-+-+',
         '-+-+-+-+-+-+-+-+-+-+++++++++++++++++++-+-+-+-+-+-+-+-+-+',
         '-+-+-+-+-+-+-+-+-+-+'),
    ),
    47: (
        ('+-+-+-+-+-+-+-+-+-0-----+-+-+-+-+-+-+------+-+-+-+-+-+-+-----',
         '--------------------------------------------------------',
         '-----+-+-+-+-+-+-+------+-+-+-+-+-+-+------+-+-+-+-+-+-+-+-+-0'),
        ('+-+-+-+-+-+-+-+-+-++++++-+-+-+-+-+-+-++++++-+-+-+-+',
         '-+-+-+-+-+++++++++++++++++++++++++++++++++++++++-+-+-+-+',
         '-+-+-+-+-++++++-+-+-+-+-+-+-++++++-+-+-+-+-+-+-+-+-+'),
        ('+++++-+-+-+-+-+-+-+-+-+',
         '-+-+-+-+-+-+-+-+-+-+++++++++++++++++++-+-+-+-+-+-+-+-+-+',
         '-+-+-+-+-+-+-+-+-+-+++++'),
    ),
    55: (
        ('+-+-+-+-+-+-+-+-+-0-+-+-+++++-++++++++-+-+-+++++-++++++++++++++++',
         '++++++++++++++++++++++++++++++++++++++++++++++++++++++++',
         '++++++++++++++++-+++++-+-+-++++++++-+++++-+-+--+-+-+-+-+-+-+-+-+-0'),
        ('+-+-+-+---+-+-+-+--+-+-+-----+------+-+-+-+---+-+------',
         '-------+-----+-+-+-------------------+-+-+-+---+-+------',
         '-------+-----+-+-+--------+-----+-+-++-+-+-+-+-+-+-+-+-+'),
        ('+-+-+---+-+-------+-+-+-+-+',
         '-+-+-+-+---------+-----+-+-+-+-+-+---+-+-------+-+-+-+-+',
         '-+-+-+-+---------+-----+-+-+'),
    ),
    71: (
        ('+-+-+-+-+-+-+-+-+-0-+++++++-----+++++--+++++-+-----+++-+--+++++-------+++',
         '--------------------------------------------------------',
         '+++-------+++++--+-+++-----+-+++++--+++++-----+++++++--+-+-+-+-+-+-+-+-+-0'),
        ('+-+-+-+-+-+-+-+-+-++-------+++++-----++-----+-+++++---+-+++-+-+',
         '++-+-+++-+++++++++-+++++++++-+++++++++-+++++++++-+++-+-+',
         '++-+-+++-+---+++++-+-----++-----+++++-------++-+-+-+-+-+-+-+-+-+'),
        ('+-------+++++-----+-+-+-+++-+-+-+-+',
         '++-+-+-+-+++-+-+-+-+++-+++++-+++++-+++-+-+-+-+++-+-+-+-+',
         '++-+-+-+-+++-+-+-+-----+++++-------+'),
    ),
}

# Mallow's finite c=15 witness from BEYOND_REFLECTIONS.md; centre positive.
SEED_15 = (
    '++---++++------++++------++---++-----++------++++--------++---++---++------++++---++---++-0',
    '+++++----+++--+++--++++++----++++++++--+++--+++--++++++----+++--+++--+0',
    '----++++++--+++',
)


def _add(*polys):
    out = Counter()
    for poly in polys:
        out.update(poly)
    return {e: c for e, c in out.items() if c}


def _scale(poly, coefficient):
    return {e: c*coefficient for e, c in poly.items() if c*coefficient}


def _mul(a, b):
    out = Counter()
    for (z, w), coefficient in a.items():
        for (zz, ww), other in b.items():
            out[z+zz, w+ww] += coefficient*other
    return {e: c for e, c in out.items() if c}


def _star(poly):
    return {(-z, -w): c for (z, w), c in poly.items()}


def _monomial(z=0, w=0):
    return {(z, w): 1}


def _word(word, start=1):
    return {(j+start, 0): 1 if sign == '+' else -1
            for j, sign in enumerate(word) if sign != '0'}


def identity_residual(base: int, rows=None):
    """An exact two-variable corrected-shell identity, before W=z^(56k)."""
    rows = FAMILIES[base] if rows is None else rows
    lengths = (base+76, base+56, base)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError('three prefix/block/tail rows are required')
    for arm, (prefix, block, tail) in enumerate(rows):
        if (len(prefix)+len(tail) != lengths[arm] or len(block) != 56
                or (arm == 0 and (len(prefix) < 19 or not tail))):
            raise ValueError('wrong affine word lengths')
        if set(prefix+block+tail)-set('+-0') or '0' in block:
            raise ValueError('invalid affine sign word')
        holes = [j+1 for j, sign in enumerate(prefix+tail) if sign == '0']
        if holes != ([19, lengths[arm]] if arm == 0 else []):
            raise ValueError('wrong affine omissions')
    if sum(p.count('+')+t.count('+')-p.count('-')-t.count('-') for p, b, t in rows) != 1:
        raise ValueError('the base words are not balanced with the negative centre')
    if sum(b.count('+')-b.count('-') for p, b, t in rows):
        raise ValueError('the repeated blocks are not balanced')
    one, z, w = _monomial(), _monomial(1), _monomial(w=1)
    denominator = _add(one, _scale(_monomial(56), -1))
    numerators = []
    for prefix, block, tail in rows:
        offset = len(prefix)+1
        numerators.append(_add(_mul(denominator, _word(prefix)),
                               _mul(_add(one, _scale(w, -1)), _word(block, offset)),
                               _mul(_mul(denominator, w), _word(tail, offset))))
    ends = [_monomial(n, 1) for n in lengths]
    shell = _scale(_mul(denominator, _add(one, _scale(_add(*ends), -1))), -1)
    for i, numerator in enumerate(numerators):
        others = _add(*(end for j, end in enumerate(ends) if j != i))
        shell = _add(shell, _mul(numerator, _add(one, _scale(others, -1))),
                     _mul(_mul(_monomial(56), ends[i]), _star(numerator)))
    low = _word(rows[0][0][:19])
    # Rooted signed enumerators of the omitted tip and depth 19, multiplied by D.
    tip = _add(_scale(_mul(ends[0], denominator), -1),
               _scale(_mul(_mul(_monomial(56), ends[0]), _star(numerators[0])), -1),
               _mul(ends[0], _add(numerators[1], numerators[2])))
    hole = _add(_mul(_monomial(19), _add(_scale(denominator, -1),
                                        numerators[1], numerators[2])),
                _mul(_mul(_monomial(19), denominator), _star(low)),
                _mul(_monomial(-19), _add(numerators[0],
                                          _scale(_mul(denominator, low), -1))))
    return _add(_mul(z, shell),
                _scale(_mul(_add(one, _scale(z, -1)), _add(tip, hole)), -1))


def _positive(value):
    if type(value) is not int or value < 1:
        raise ValueError('c must be a positive integer')
    return value


def bound(c: int) -> dict:
    c = _positive(c)
    upper = (3*c+133)//2 - int(c % 2 == 1 and c % 8 != 3)
    return {'c': c, 'lengths': [c+76, c+56, c], 'optimal_size': upper,
            'target': (3*c+133)//2-1, 'domain': 'every positive integer c'}


def _literal_pair(lengths, words, center):
    left, right = ([(0, 0)], []) if center == 1 else ([], [(0, 0)])
    for arm, word in enumerate(words, 1):
        for depth, sign in enumerate(word, 1):
            if sign != '0':
                (left if sign == '+' else right).append((arm, depth))
    return {'lengths': lengths, 'left': left, 'right': right,
            **check_pair(lengths, left, right)}


def construct(c: int) -> dict:
    c = _positive(c)
    lengths = [c+76, c+56, c]
    if c % 8 != 7 or c % 56 == 7:
        witness = original_tree(lengths)
        method = 'Euler-cell prefix'
    elif c == 15:
        witness = _literal_pair(lengths, SEED_15, 1)
        method = 'Mallow finite c=15 control'
    else:
        base = 71 if c % 56 == 15 else c % 56
        rows = FAMILIES[base]
        k = (c-base)//56
        witness = _literal_pair(lengths, [p+b*k+t for p, b, t in rows], -1)
        method = f'affine word certificate, base {base}, repeat {k}'
    expected = bound(c)
    if not witness['homometric'] or witness['size'] != expected['optimal_size']:
        raise ArithmeticError('the full original-tree check failed the proved optimal size')
    return {**witness, **expected, 'construction': method, 'optimal': True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--witness', type=int, metavar='C')
    mode.add_argument('--frontier', type=int, metavar='T', help='c=23+5320t, t>=0')
    mode.add_argument('--bound', type=int, metavar='C')
    mode.add_argument('--prove', action='store_true')
    mode.add_argument('--check', metavar='FILE')
    args = parser.parse_args()
    try:
        if args.prove:
            checks = {base: not identity_residual(base) for base in FAMILIES}
            if not all(checks.values()):
                raise ArithmeticError('an exact affine identity failed')
            result = {'affine_identities': checks, 'domain': 'every positive integer c',
                      'general_tripod_target_proved': False}
        elif args.witness is not None:
            result = construct(args.witness)
        elif args.frontier is not None:
            if args.frontier < 0:
                raise ValueError('frontier t must be nonnegative')
            result = construct(23+5320*args.frontier)
        elif args.bound is not None:
            result = bound(args.bound)
        else:
            data = sys.stdin.read() if args.check == '-' else Path(args.check).read_text()
            pair = json.loads(data)
            result = check_pair(pair['lengths'], pair['left'], pair['right'])
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get('homometric', True) else 1
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
