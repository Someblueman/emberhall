#!/usr/bin/env python3
"""Universal tip-hole closure for patched multi-period obstructions on T(99t,79t,23t).

Closes the tip1+tip3 (4 | p_i) and tip1 (restricted upper-overlap) exceptions in
general_hole_multi_period.py via the exact cross-arm bin determinant 2*z^(3-s1-s2-s3)
and d >= 1 cyclotomic evaluation across BC, AC, and AB. Standard library only.
"""
from __future__ import annotations

import argparse
import json

import general_hole_multi_period as ghmp
import nonmatching_word_completion as nwc


def _poly_add(p, q, sign=1):
    out = dict(p)
    for e, c in q.items():
        nv = out.get(e, 0) + sign * c
        if nv:
            out[e] = nv
        else:
            out.pop(e, None)
    return out


def bin_matrix_determinant(s_tip):
    """Exact 3x3 determinant of the (BC, AC, AB) bin system in (U_1, U_2, U_3).

    For tip-omission indicators s_tip = (s_1, s_2, s_3) in {0, 1}^3, the top edges
    of BC, AC, and AB impose:
        BC: z^(1-s_3) U_2 + z^(1-s_2) U_3 == 0
        AC: z^(1-s_3) U_1 + z^(1-s_1) U_3 == 0
        AB: z^(1-s_2) U_1 + z^(1-s_1) U_2 == 0
    modulo Phi_d(z) for every divisor d >= 1 of lcm(p_1, p_2, p_3).
    """
    if (not isinstance(s_tip, (list, tuple)) or len(s_tip) != 3
            or any(type(s) is not int or s not in (0, 1) for s in s_tip)):
        raise ValueError('s_tip must be three 0/1 tip indicators')
    s1, s2, s3 = s_tip
    m = [
        [{}, {1 - s3: 1}, {1 - s2: 1}],
        [{1 - s3: 1}, {}, {1 - s1: 1}],
        [{1 - s2: 1}, {1 - s1: 1}, {}],
    ]
    det = {}
    for col, sign in ((0, 1), (1, -1), (2, 1)):
        c1, c2 = (j for j in range(3) if j != col)
        minor = _poly_add(
            nwc.poly_mul(m[1][c1], m[2][c2]),
            nwc.poly_mul(m[1][c2], m[2][c1]),
            sign=-1,
        )
        det = _poly_add(det, nwc.poly_mul(m[0][col], minor), sign=sign)
    return det


def _validate_bounds_only(t, raw_holes, periods, prefix_lengths, suffix_lengths):
    if type(t) is not int or t < 1:
        raise ValueError('positive integer t required')
    lcm_info = nwc.cyclotomic_lcm(periods)
    lengths = [b * t for b in nwc.BASE]
    A, B, C = lengths
    holes = ghmp._normalize_holes(lengths, raw_holes)

    for name, vec in (('prefix_lengths', prefix_lengths), ('suffix_lengths', suffix_lengths)):
        if (not isinstance(vec, (list, tuple)) or len(vec) != 3
                or any(type(v) is not int or v < 0 for v in vec)):
            raise ValueError(f'{name} must be three nonnegative integers')
    for Ln, lp, rp, p in zip(lengths, prefix_lengths, suffix_lengths, periods):
        if lp + rp + p > Ln:
            raise ValueError('periodic interior must contain at least one full period')

    tip_set = {(arm, lengths[arm - 1]) for arm in (1, 2, 3)}
    tip_holes = {h for h in holes if h in tip_set}
    interior_holes = [h for h in holes if h not in tip_set]
    s_tip = tuple(1 if (arm, lengths[arm - 1]) in tip_holes else 0 for arm in (1, 2, 3))
    for arm, st in enumerate(s_tip, 1):
        if st and suffix_lengths[arm - 1] < 1:
            raise ValueError(f'suffix_lengths[{arm - 1}] must be >= 1 to carry tip hole')

    for arm, d in interior_holes:
        if arm == 1 and d >= 20 * t + 1:
            raise ValueError('arm-1 interior hole must satisfy d < 20*t + 1')
        if arm in (2, 3) and d >= 3 * t:
            raise ValueError(f'arm-{arm} interior hole must satisfy d < 3*t')

    hole_shift = max([0] + [d - (A - B) if a == 1 else d for a, d in interior_holes if a != 0])
    L_eff = max(1, *prefix_lengths, hole_shift)
    R_max = max(suffix_lengths)
    W = lcm_info['degree']
    lower_shift = 1 - s_tip[0]
    upper_shift = max(s_tip[1], s_tip[2])
    if L_eff + R_max + W + lower_shift + upper_shift > 3 * t + 1:
        raise ValueError(
            f'patch+hole+LCM bound violated: {L_eff + R_max + W + lower_shift + upper_shift} > {3 * t + 1}'
        )

    non_bin_max = A + lower_shift + L_eff + W
    bc_lo = B + C + 2 - max(suffix_lengths[1] + s_tip[2], suffix_lengths[2] + s_tip[1])
    bc_hi = B + C + 1 + W
    ac_lo = A + C + 2 - max(suffix_lengths[0] + s_tip[2], suffix_lengths[2] + s_tip[0])
    ac_hi = A + C + 1 + W
    ab_lo = A + B + 2 - max(suffix_lengths[0] + s_tip[1], suffix_lengths[1] + s_tip[0])
    ab_hi = A + B + 1 + W
    if not (non_bin_max < bc_lo <= bc_hi < ac_lo <= ac_hi < ab_lo <= ab_hi):
        raise ArithmeticError('unexpected bin overlap')

    return lengths, holes, s_tip, tip_holes, lcm_info, L_eff, R_max, {
        'non_bin_max': non_bin_max,
        'BC': [bc_lo, bc_hi],
        'AC': [ac_lo, ac_hi],
        'AB': [ab_lo, ab_hi],
    }


def universal_tip_certificate(t, raw_holes, periods, prefix_lengths, suffix_lengths):
    """Unrestricted all-tip all-period patched obstruction on T(99t,79t,23t)."""
    lengths, holes, s_tip, tip_holes, lcm_info, L_eff, R_max, intervals = _validate_bounds_only(
        t, raw_holes, periods, prefix_lengths, suffix_lengths,
    )
    det_poly = bin_matrix_determinant(s_tip)
    if len(det_poly) != 1 or next(iter(det_poly.values())) != 2:
        raise ArithmeticError('unexpected bin matrix determinant')
    det_exp = next(iter(det_poly))
    for d in lcm_info['divisors']:
        if not nwc.poly_mod_cyclotomic(det_poly, d, lcm_info['phis'][d]):
            raise ArithmeticError(f'bin determinant vanished modulo Phi_{d}')
    if any(sum(q.values()) == 0 for q in lcm_info['quotients']):
        raise ArithmeticError('quotient vanished at z=1')

    tip_arms = sorted(arm for arm, _ in tip_holes)
    return {
        't': t,
        'lengths': lengths,
        'holes': [list(h) for h in holes],
        'tip_arms': tip_arms,
        'periods': list(periods),
        'prefix_lengths': list(prefix_lengths),
        'suffix_lengths': list(suffix_lengths),
        'lcm_degree': lcm_info['degree'],
        'patch_hole_lcm_sum': L_eff + R_max + lcm_info['degree'],
        'threshold_3t': 3 * t,
        'bin_det_exponent': det_exp,
        'bins_disjoint': True,
        'intervals': intervals,
        'obstructed': True,
        'full_homometry_claimed': False,
    }


def audit_universal_tip_multi_period(t, raw_holes, centre, words, periods, prefix_lengths, suffix_lengths):
    """Verify patched multi-period structure and produce a d >= 1 bin cyclotomic witness."""
    cert = universal_tip_certificate(t, raw_holes, periods, prefix_lengths, suffix_lengths)
    lengths = tuple(cert['lengths'])
    holes = ghmp._normalize_holes(lengths, raw_holes)
    ghmp._validate_words_general(lengths, holes, centre, words)
    hole_set = set(holes)

    for i, (w, Ln, lp, rp, p) in enumerate(zip(words, lengths, prefix_lengths, suffix_lengths, periods), 1):
        mid = Ln - lp - rp
        if mid % p:
            raise ValueError('interior length must be divisible by period')
        blk = list(w[lp:lp + p])
        for off in range(p):
            if (i, lp + off + 1) in hole_set:
                blk[off] = w[lp + p + off] if mid >= 2 * p else 1
        for pos in range(lp, Ln - rp):
            depth = pos + 1
            if (i, depth) in hole_set:
                continue
            if w[pos] != blk[(pos - lp) % p]:
                raise ValueError(f'arm {i} fails period {p} at depth {depth}')

    res = ghmp.general_full_identity_array(lengths, holes, centre, words)
    if not any(res):
        raise ArithmeticError('unexpected vanishing identity on obstructed class')

    lcm_info = nwc.cyclotomic_lcm(periods)
    D_terms = list(lcm_info['lcm_poly'].items())
    iv = cert['intervals']
    gaps_empty = True
    bins = {'BC': {}, 'AC': {}, 'AB': {}}
    for n in range(iv['non_bin_max'] + 1, iv['AB'][1] + 1):
        val = 0
        for de, dc in D_terms:
            idx = n - de
            if 0 <= idx < len(res):
                val += dc * res[idx]
        if val:
            if iv['BC'][0] <= n <= iv['BC'][1]:
                bins['BC'][n] = val
            elif iv['AC'][0] <= n <= iv['AC'][1]:
                bins['AC'][n] = val
            elif iv['AB'][0] <= n <= iv['AB'][1]:
                bins['AB'][n] = val
            else:
                gaps_empty = False

    cyclotomic_witness = None
    for d in lcm_info['divisors']:
        phi_d = lcm_info['phis'][d]
        for bname, bpoly in bins.items():
            if nwc.poly_mod_cyclotomic(bpoly, d, phi_d):
                cyclotomic_witness = {'bin': bname, 'divisor': d}
                break
        if cyclotomic_witness is not None:
            break

    if not gaps_empty or cyclotomic_witness is None:
        raise ArithmeticError('universal bin check failed unexpectedly')

    return {
        'obstructed': True,
        'homometric': False,
        'tip_arms': cert['tip_arms'],
        'bins_disjoint': gaps_empty,
        'cyclotomic_witness': cyclotomic_witness,
        'full_homometry_claimed': False,
    }


def _load_json(path):
    if path == '-':
        import sys
        return json.load(sys.stdin)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--cert-json', metavar='JSON')
    mode.add_argument('--audit-json', metavar='JSON')
    args = parser.parse_args()
    try:
        if args.cert_json:
            d = _load_json(args.cert_json)
            out = universal_tip_certificate(
                d['t'], d['holes'], d['periods'], d['prefix_lengths'], d['suffix_lengths'],
            )
        else:
            d = _load_json(args.audit_json)
            out = audit_universal_tip_multi_period(
                d['t'], d['holes'], d['centre'], d['words'],
                d['periods'], d['prefix_lengths'], d['suffix_lengths'],
            )
        print(json.dumps(out, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError) as err:
        parser.error(str(err))


if __name__ == '__main__':
    raise SystemExit(main())
