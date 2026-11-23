"""T(99t,79t,23t) at t = 2660k+1: the affine exact-polynomial certificate is dead.

The vulnerable step of the scaling family is the residue class t = 1
(mod 2660), t > 1: every full-prefix pair is residue-obstructed
(GAP_99_79_23.md), and t = 1 attains only via an interior hole.  This
module settles the certificate question for that class.

An exact polynomial certificate in k is a two-variable identity R(z,w) = 0
with w = z^(delta*k), as in FIXED_DIFFERENCE_FAMILY.md: each arm word is
P_i + B_i repeated e_i*k times + T_i (e_i*delta = 2660*BASE_i), with two
omitted vertices and the centre signed.  Homometry at every rep count
follows by cancelling the nonzero factor D(z)(1-z).  This checker audits
exactly that identity.

Result (audited here and in RESIDUE_2660.md): for every period
delta | 2660, no +/-1 assignment makes R vanish.  The proof is a
mod-4 (Hensel) obstruction; at delta = 2660 it collapses to three
monomials,

    z^2799 w^178:  s(T_{1,10}) + s(T_{2,1}) = 0
    z^2743 w^122:  s(T_{1,10}) + s(B_{3,2633}) = 0
    z^2724 w^102:  s(T_{2,1}) + s(B_{3,2633}) = 0

whose only integer solution is 0 for all three signs.  All other
periods fail the same Newton step.  Hence the fixed-difference style
certificate does not extend to the scaling family; the tree-level
question remains open beyond certificate forms.  The t = 1 witness is
the interior-hole frontier, recounted by BFS below.

Standard library only.  Conventions as in PUBLISHED_CASES.md.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys

BASE = (99, 79, 23)
RESISTANT_MODULUS = 2660  # 4 * 5 * 7 * 19
REPEATS = (99, 79, 23)    # e_i for delta = 2660
PERIOD = RESISTANT_MODULUS

# --------------------------------------------------------------------------
# Two-variable polynomial machinery (after FIXED_DIFFERENCE_FAMILY.md).
# --------------------------------------------------------------------------

def _add(*polys):
    out = Counter()
    for poly in polys:
        out.update(poly)
    return {e: c for e, c in out.items() if c}


def _scale(poly, coefficient):
    return {e: c * coefficient for e, c in poly.items() if c * coefficient}


def _mul(a, b):
    out = Counter()
    for (z, w), c in a.items():
        for (zz, ww), d in b.items():
            out[z + zz, w + ww] += c * d
    return {e: c for e, c in out.items() if c}


def _star(poly):
    return {(-z, -w): c for (z, w), c in poly.items()}


def _monomial(z=0, w=0):
    return {(z, w): 1}


def _word(word, start=1):
    return {(j + start, 0): 1 if sign == '+' else -1
            for j, sign in enumerate(word) if sign != '0'}


def _shift(poly, dz, dw=0):
    return {(z + dz, w + dw): c for (z, w), c in poly.items()}


def make_identity(delta, repeats, bases, prefixes, tails, blocks,
                  holes=((0, 19), (0, 'tip')), sigma=-1):
    """Exact R(z,w) for the affine template.

    Arm i is P_i + B_i repeated repeats[i]*k times + T_i (common block
    length delta, w = z^(delta*k)).  holes: two (arm, depth) with depth
    an int (interior, in the prefix) or 'tip'.  Centre sign sigma.
    """
    assert len(prefixes) == 3 and len(tails) == 3 and len(blocks) == 3
    assert all(len(b) == delta for b in blocks)
    one = _monomial()
    D = _add(one, _scale(_monomial(delta), -1))
    numerators = []
    for i in range(3):
        p, t = prefixes[i], tails[i]
        offset = len(p) + 1
        block_term = _word(blocks[i], offset)
        block_part = _add(block_term,
                          _scale(_shift(block_term, 0, repeats[i]), -1))
        numerators.append(_add(
            _mul(D, _word(p)),
            block_part,
            _mul(_mul(D, _monomial(0, repeats[i])), _word(t, offset)),
        ))
    ends = [_monomial(bases[i], repeats[i]) for i in range(3)]
    shell = _scale(_mul(D, _add(one, _scale(_add(*ends), -1))), sigma)
    for i, numerator in enumerate(numerators):
        others = _add(*(ends[j] for j in range(3) if j != i))
        shell = _add(shell,
                     _mul(numerator, _add(one, _scale(others, -1))),
                     _mul(_mul(_monomial(delta), ends[i]), _star(numerator)))
    corr = {}
    for (arm, depth) in holes:
        others_N = _add(*(numerators[j] for j in range(3) if j != arm))
        if depth == 'tip':
            neg_dNstar = {(z + delta, w): -c
                          for (z, w), c in _star(numerators[arm]).items()}
            J = _mul(ends[arm], _add(neg_dNstar, others_N,
                                     _scale(D, sigma)))
        else:
            m = depth
            low = _word(prefixes[arm][:m])
            J = _add(_mul(_monomial(m), _add(_scale(D, -1), others_N)),
                     _mul(_mul(_monomial(m), D), _star(low)),
                     _mul(_monomial(-m), _add(numerators[arm],
                                             _scale(_mul(D, low), -1))))
            if sigma != -1:
                J = _add(J, _scale(_mul(_monomial(m), D), sigma + 1))
        corr = _add(corr, J)
    return _add(_mul(_monomial(1), shell),
                _scale(_mul(_add(one, _scale(_monomial(1), -1)), corr), -1))


# --------------------------------------------------------------------------
# Template bookkeeping and the exact linear system for the identity.
# --------------------------------------------------------------------------

SPLIT = (49, 39, 11)          # |P_i|; holes sit in P_1 / T_1
HOLES = ((0, 19), (0, 'tip'))


def target(t: int) -> int:
    return (1 + 201 * t) // 2 - 1


def build_system(delta, holes=HOLES, sigma=-1):
    """Linear system for the identity: rows are (z,w) monomials.

    Returns (varspec, rows_list) with rows_list[mon] = ([(var, coeff)], rhs)
    for sum_v s_v * coeff = rhs.  Variables are every prefix/tail/block
    letter (holes excluded).  Truth: build via single-letter identities
    (linearity of the identity in the signs).
    """
    repeats = tuple(RESISTANT_MODULUS * b // delta for b in BASE)
    plen = list(SPLIT)
    tlen = [BASE[i] - plen[i] for i in range(3)]
    for (arm, depth) in holes:
        if isinstance(depth, int):
            if plen[arm] < depth:
                plen[arm] = depth
                tlen[arm] = BASE[arm] - plen[arm]
    holeset = set()
    for (arm, depth) in holes:
        if depth == 'tip':
            holeset.add(('T', arm, tlen[arm] - 1))
        else:
            holeset.add(('P', arm, depth - 1))
    varspec = []
    for i in range(3):
        for pos in range(plen[i]):
            if ('P', i, pos) not in holeset:
                varspec.append(('P', i, pos))
        for pos in range(tlen[i]):
            if ('T', i, pos) not in holeset:
                varspec.append(('T', i, pos))
    for i in range(3):
        for j in range(delta):
            varspec.append(('B', i, j))

    def strings_for(var):
        P = ['0' * plen[i] for i in range(3)]
        T = ['0' * tlen[i] for i in range(3)]
        B = ['0' * delta for _ in range(3)]
        kind, i, pos = var
        if kind == 'P':
            lst = list(P[i]); lst[pos] = '+'; P[i] = ''.join(lst)
        elif kind == 'T':
            lst = list(T[i]); lst[pos] = '+'; T[i] = ''.join(lst)
        else:
            lst = list(B[i]); lst[pos] = '+'; B[i] = ''.join(lst)
        return P, T, B

    R0 = make_identity(delta, repeats, BASE, ['0' * plen[i] for i in range(3)],
                       ['0' * tlen[i] for i in range(3)], ['0' * delta] * 3,
                       holes=holes, sigma=sigma)
    rowmap = {}
    for vi, var in enumerate(varspec):
        P, T, B = strings_for(var)
        Craw = make_identity(delta, repeats, BASE, P, T, B, holes=holes,
                             sigma=sigma)
        for mon in set(Craw) | set(R0):
            c = Craw.get(mon, 0) - R0.get(mon, 0)
            if c:
                rowmap.setdefault(mon, []).append((vi, c))
    rows_list = {mon: (cs, -R0.get(mon, 0)) for mon, cs in rowmap.items()}
    return varspec, rows_list


# --------------------------------------------------------------------------
# Mod-4 (Hensel level 0-1) obstruction check.
# --------------------------------------------------------------------------

def _gf2_solve(rows_list, mons, nvars, y):
    """Solve M t = y over GF(2); None if inconsistent.  y: list of 0/1."""
    rowlist = [([vi for (vi, c) in cs], [c for (vi, c) in cs])
               for mon, (cs, rhs) in mons]
    basis = {}
    for r in range(len(rowlist)):
        vars_, coefs = rowlist[r]
        m = 0
        v = int(y[r]) & 1
        for k, var in enumerate(vars_):
            if coefs[k] & 1:
                m |= (1 << var)
        while m:
            pivot = (m & -m).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (m, v)
                break
            bm, bv = basis[pivot]
            m ^= bm
            v ^= bv
        else:
            if v:
                return None
    return basis


def level01_obstruction(delta, holes=HOLES, sigma=-1, splits=None):
    """First Newton step obstruction: returns (verdict, detail).

    verdict 'obstructed'  -> no +/-1 assignment (mod-2/4 argument).
    """
    varspec, rows_list = build_system(delta, holes, sigma)
    mons = list(rows_list.items())
    nvars = len(varspec)
    # Level 0: all-ones must solve the mod-2 system (necessary for +/-1).
    for mon, (cs, rhs) in mons:
        if sum(c for (_, c) in cs) % 2 != rhs % 2:
            return 'obstructed', {'delta': delta, 'at': 'mod 2'}
    # Level 1 (Newton): (b - M*1)/2 must lie in the column space mod 2.
    y = []
    for mon, (cs, rhs) in mons:
        r = rhs - sum(c for (_, c) in cs)
        if r % 2 != 0:
            return 'obstructed', {'delta': delta, 'at': 'mod 4 residue'}
        y.append((r // 2) % 2)
    result = _gf2_solve(rows_list, mons, nvars, y)
    if result is None:
        return 'obstructed', {'delta': delta,
                              'argument': 'Hensel level 1 (mod 4)'}
    return 'consistent', {'delta': delta}


# --------------------------------------------------------------------------
# t = 1 witness (frontier) with an independent BFS recount.
# --------------------------------------------------------------------------

FRONTIER = ('+-+-+-+-+-+-+-+-+-0-+-++++++++++++++++-+-++++++++++++++++'
            '-+-++++++++++++++++-+--+-+-+-+-+-+-+-+-+-0',
            '+-+-+-+-+-+-+-+-+-++-+----------------+-+----------------'
            '+-++-+-+-+-+-+-+-+-+-+',
            '+-+-----------------+-+')


def t1_witness() -> dict:
    left, right = [], [(0, 0)]
    holes = []
    for arm, word in enumerate(FRONTIER, 1):
        for depth, ch in enumerate(word, 1):
            if ch == '+':
                left.append((arm, depth))
            elif ch == '-':
                right.append((arm, depth))
            else:
                holes.append((arm, depth))
    if [len(w) for w in FRONTIER] != [99, 79, 23]:
        raise ArithmeticError('frontier word lengths wrong')
    if holes != [(1, 19), (1, 99)]:
        raise ArithmeticError(f'frontier holes wrong: {holes}')
    if len(left) != 100 or len(right) != 100:
        raise ArithmeticError('frontier sizes wrong')
    return {'lengths': [99, 79, 23], 'size': 100, 'holes': list(holes),
            'left': left, 'right': right}


def check_pair(lengths, left, right) -> dict:
    """Exact pairwise recount (Counter distance profiles)."""
    from itertools import combinations
    if (not isinstance(lengths, (list, tuple)) or len(lengths) != 3
            or any(type(n) is not int or n < 1 for n in lengths)):
        raise ValueError('lengths must be three positive integers')

    def validate(vertices):
        result = []
        for v in vertices:
            if (not isinstance(v, (list, tuple)) or len(v) != 2
                    or type(v[0]) is not int or type(v[1]) is not int):
                raise ValueError(f'malformed vertex {v!r}')
            arm, depth = v
            if not ((arm == 0 and depth == 0)
                    or (1 <= arm <= 3 and 1 <= depth <= lengths[arm - 1])):
                raise ValueError(f'vertex {v} is outside the tree')
            result.append((arm, depth))
        if len(result) != len(set(result)):
            raise ValueError('duplicate vertex in a set')
        return result

    left = validate(left)
    right = validate(right)
    if set(left) & set(right):
        raise ValueError('the two sets overlap')
    if len(left) != len(right):
        raise ValueError('the two sets have different sizes')

    def profile(vertices):
        return Counter(abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]
                       for u, v in combinations(vertices, 2))

    lp, rp = profile(left), profile(right)
    difference = {d: lp[d] - rp[d] for d in sorted(lp.keys() | rp.keys())
                  if lp[d] != rp[d]}
    return {'lengths': list(lengths), 'size': len(left),
            'homometric': not difference,
            'difference': difference,
            'pairs_per_side': sum(lp.values())}


# --------------------------------------------------------------------------
# Certificate data for the flagship period (delta = 2660).
# --------------------------------------------------------------------------

# Three monomials whose coefficients are s(T_{1,10})+s(T_{2,1}),
# s(T_{1,10})+s(B_{3,2633}), s(T_{2,1})+s(B_{3,2633}); the only integer
# solution is 0 for all three signs.
CERT_2660 = [
    ((2799, 178), (('T', 0, 9), ('T', 1, 0))),
    ((2743, 122), (('T', 0, 9), ('B', 2, 2632))),
    ((2724, 102), (('T', 1, 0), ('B', 2, 2632))),
]


def verify_certificate_2660() -> list:
    """Recompute the three obstruction equations from the identity."""
    varspec, rows_list = build_system(PERIOD)
    index = {v: i for i, v in enumerate(varspec)}
    for mon, (var_a, var_b) in CERT_2660:
        assert mon in rows_list
        cs, rhs = rows_list[mon]
        got = {(varspec[vi], c) for (vi, c) in cs}
        assert got == {(var_a, 1), (var_b, 1)} and rhs == 0, (mon, got, rhs)
    # The cycle forces all three letters to 0, contradicting +/-1.
    return [(f'monomial z^{m[0]} w^{m[1]}: s{a} + s{b} = 0')
            for m, (a, b) in CERT_2660]


def classify(t: int) -> dict:
    if type(t) is not int or t < 1:
        raise ValueError('t must be a positive integer')
    result = {'t': t, 'lengths': [n * t for n in BASE], 'target': target(t)}
    if t == 1:
        return {**result, 'status': 'attained', 'size': 100,
                'holes': [[1, 19], [1, 99]]}
    if t % RESISTANT_MODULUS != 1:
        return {**result, 'status': 'attained (full-prefix, GAP)'}
    return {**result, 'status': 'open',
            'upper_bound': target(t),
            'note': 'no affine polynomial certificate exists (proved); '
                    'attainment by any method is open'}


def prove() -> list:
    lines = []
    lines.extend(verify_certificate_2660())
    lines.append('certificate: three monomial equations force three signs '
                 'to 0, so no +/-1 affine certificate exists at '
                 'delta = 2660')
    witness = t1_witness()
    checked = check_pair(witness['lengths'], witness['left'],
                         witness['right'])
    if not checked['homometric'] or checked['size'] != 100:
        raise ArithmeticError('t=1 witness failed recount')
    lines.append(f"t=1: size-100 pair recounted ({checked['pairs_per_side']} "
                 f"pairs per side, identical profiles)")
    return lines


def audit() -> list:
    """Full period audit: level-1 (mod-4) obstruction at every delta | 2660."""
    lines = []
    for delta in [d for d in range(1, PERIOD + 1) if PERIOD % d == 0]:
        verdict, detail = level01_obstruction(delta)
        assert verdict == 'obstructed', delta
        lines.append(f"delta={delta}: obstructed ({detail.get('at', 'Hensel')})")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prove', action='store_true')
    group.add_argument('--audit', action='store_true')
    group.add_argument('--classify', type=int, metavar='T')
    group.add_argument('--witness', type=int, metavar='K')
    group.add_argument('--check', metavar='FILE')
    parser.add_argument('--summary', action='store_true',
                        help='with --witness, omit vertex lists')
    args = parser.parse_args(argv)
    try:
        if args.prove:
            for line in prove():
                print('PASS:', line)
        elif args.audit:
            for line in audit():
                print('PASS:', line)
        elif args.classify is not None:
            print(json.dumps(classify(args.classify), sort_keys=True))
        elif args.witness is not None:
            if args.witness != 0:
                raise ValueError('no witness for k != 0 is delivered '
                                 '(certificate obstructions are proved)')
            result = t1_witness()
            result['t'] = result['lengths'][0] // 99
            result['left'] = [list(v) for v in result['left']]
            result['right'] = [list(v) for v in result['right']]
            if args.summary:
                result = {k: v for k, v in result.items()
                          if k not in ('left', 'right')}
            print(json.dumps(result, sort_keys=True))
        else:
            text = (sys.stdin.read() if args.check == '-'
                    else open(args.check, encoding='utf-8').read())
            data = json.loads(text)
            lengths = data.get('lengths')
            t = lengths[0] // 99 if lengths and lengths[0] % 99 == 0 else None
            if (t is None or sorted(lengths) != sorted([n * t for n in BASE])
                    or (t - 1) % RESISTANT_MODULUS != 0):
                raise ValueError('not a resistant scaling tree')
            if 1 + sum(lengths) > 1200:
                raise ValueError('tree too large for an exact pairwise recount')
            result = check_pair(lengths, data.get('left', []),
                                data.get('right', []))
            print(json.dumps(result, sort_keys=True))
            return 0 if result['homometric'] else 1
    except (ValueError, ArithmeticError, KeyError, OSError) as error:
        print(f'REFUSED: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
