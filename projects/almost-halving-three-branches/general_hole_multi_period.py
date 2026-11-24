#!/usr/bin/env python3
"""General zero-, one-, and two-hole patched multi-period obstructions on T(99t,79t,23t).

Generalizes nonmatching_word_completion.py from {(1, h), (1, 99t)} to arbitrary
hole sets of size <= 2 across all three arms and the centre [0, 0].
Standard library only. See GENERAL_HOLE_MULTI_PERIOD.md.
"""
from __future__ import annotations

import argparse
import json

import intermediate_shell_repair as repair
import nonmatching_word_completion as nwc


def _normalize_holes(lengths, raw_holes):
    if not isinstance(raw_holes, (list, tuple)) or len(raw_holes) > 2:
        raise ValueError('holes must be a list of at most two [arm, depth] pairs')
    holes = []
    seen = set()
    for item in raw_holes:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError('each hole must be [arm, depth]')
        arm, depth = item
        if type(arm) is not int or type(depth) is not int:
            raise ValueError('hole coordinates must be integers')
        if arm == 0:
            if depth != 0:
                raise ValueError('centre hole must be [0, 0]')
        elif arm in (1, 2, 3):
            if not 1 <= depth <= lengths[arm - 1]:
                raise ValueError(f'hole {[arm, depth]} out of range for {lengths}')
        else:
            raise ValueError('hole arm must be 0, 1, 2, or 3')
        key = (arm, depth)
        if key in seen:
            raise ValueError('duplicate hole coordinate')
        seen.add(key)
        holes.append(key)
    return holes


def _validate_words_general(lengths, holes, centre, words):
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError('signed centre in (-1, 1) required')
    if not isinstance(words, (list, tuple)) or len(words) != 3:
        raise ValueError('three arm words required')
    hole_set = set(holes)
    for arm, (word, Ln) in enumerate(zip(words, lengths), 1):
        if len(word) != Ln:
            raise ValueError('word length mismatch')
        for d, v in enumerate(word, 1):
            allowed = (0,) if (arm, d) in hole_set else (-1, 1)
            if type(v) is not int or v not in allowed:
                raise ValueError('zero signs allowed only at stated holes')


def general_hole_certificate(t, raw_holes, periods, prefix_lengths, suffix_lengths):
    """All-t patched multi-period obstruction for general 0/1/2-hole placements."""
    if type(t) is not int or t < 1:
        raise ValueError('positive integer t required')
    lcm_info = nwc.cyclotomic_lcm(periods)
    lengths = [b * t for b in nwc.BASE]
    A, B, C = lengths
    holes = _normalize_holes(lengths, raw_holes)

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
    s_tip = [1 if (arm, lengths[arm - 1]) in tip_holes else 0 for arm in (1, 2, 3)]
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
    # When (1, A) is occupied, -z^(A+1) S_2/S_3 shifts lower boundary terms by +1
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

    tip_arms = tuple(sorted(arm for arm, _ in tip_holes))
    if tip_arms == (1, 3):
        # Phi_4 annihilates z^2 + 1; exclude only when Phi_4 cannot appear in all three arms
        if all(p % 4 == 0 for p in periods):
            raise ValueError('tip1+tip3 with all periods divisible by 4 admits Phi_4 modes')

    if tip_arms == (1,):
        # Verify an intact period-2 contradiction index m exists away from interior holes
        hole_m = {3 * t - d + 1 for a, d in interior_holes if a in (2, 3)}
        m_lo = max(suffix_lengths[1], suffix_lengths[2])
        m_hi = min(3 * t - 1, 3 * t - prefix_lengths[1], 3 * t - prefix_lengths[2])
        if not any(m not in hole_m for m in range(m_lo, m_hi + 1)):
            raise ValueError('no hole-free upper-overlap index m remains for tip1')

    return {
        't': t,
        'lengths': lengths,
        'holes': [list(h) for h in holes],
        'tip_arms': list(tip_arms),
        'periods': list(periods),
        'prefix_lengths': list(prefix_lengths),
        'suffix_lengths': list(suffix_lengths),
        'lcm_degree': W,
        'patch_hole_lcm_sum': L_eff + R_max + W,
        'threshold_3t': 3 * t,
        'bins_disjoint': True,
        'intervals': {
            'non_bin_max': non_bin_max,
            'BC': [bc_lo, bc_hi],
            'AC': [ac_lo, ac_hi],
            'AB': [ab_lo, ab_hi],
        },
        'obstructed': True,
        'full_homometry_claimed': False,
    }


def construct_general_hole_words(t, raw_holes, periods, a_patches, b_blocks, c_patches):
    """Build concrete patched multi-period words with zeros at the stated holes."""
    lengths = [b * t for b in nwc.BASE]
    holes = _normalize_holes(lengths, raw_holes)
    L_lens = [len(a) for a in a_patches]
    R_lens = [len(c) for c in c_patches]
    general_hole_certificate(t, holes, periods, L_lens, R_lens)
    if len(b_blocks) != 3:
        raise ValueError('three periodic blocks required')
    hole_set = set(holes)
    words = []
    for i, (Ln, ap, blk, cp, p) in enumerate(zip(lengths, a_patches, b_blocks, c_patches, periods), 1):
        repair.signs(ap, len(ap))
        repair.signs(blk, p)
        repair.signs(cp, len(cp))
        mid = Ln - len(ap) - len(cp)
        if mid % p:
            raise ValueError('interior length must be divisible by period')
        w = list(ap) + list(blk) * (mid // p) + list(cp)
        for ha, hd in hole_set:
            if ha == i:
                w[hd - 1] = 0
        words.append(w)
    return words


def general_full_identity_array(lengths, raw_holes, centre, words):
    """Exact array of coefficients of (1-z)F(z) - 2zS for arbitrary hole sets."""
    holes = _normalize_holes(lengths, raw_holes)
    _validate_words_general(lengths, holes, centre, words)
    a, b, _ = lengths
    out = [0] * (a + b + 2)
    hole_set = set(holes)
    s_centre = 0 if (0, 0) in hole_set else centre
    if s_centre:
        out[1] += s_centre
        for Ln in lengths:
            out[Ln + 1] -= s_centre
        for ha, hd in hole_set:
            if ha != 0:
                out[hd] -= s_centre
                out[hd + 1] += s_centre
    for i, word in enumerate(words, 1):
        Ln = lengths[i - 1]
        others = [lengths[j] + 1 for j in range(3) if j != i - 1]
        o1, o2 = others
        for d, sign in enumerate(word, 1):
            if not sign:
                continue
            out[d + 1] += sign
            out[Ln + 1 - d] -= sign
            out[d + o1] -= sign
            out[d + o2] -= sign
            for ha, hd in hole_set:
                if ha == 0:
                    dist = d
                elif ha == i:
                    dist = hd - d if d < hd else d - hd
                else:
                    dist = d + hd
                out[dist] -= sign
                out[dist + 1] += sign
    return out


def audit_general_hole_multi_period(t, raw_holes, centre, words, periods, prefix_lengths, suffix_lengths):
    """Verify patched multi-period structure, bin isolation, and obstruction for any hole set."""
    cert = general_hole_certificate(t, raw_holes, periods, prefix_lengths, suffix_lengths)
    lengths = tuple(cert['lengths'])
    holes = _normalize_holes(lengths, raw_holes)
    _validate_words_general(lengths, holes, centre, words)
    hole_set = set(holes)

    for i, (w, Ln, lp, rp, p) in enumerate(zip(words, lengths, prefix_lengths, suffix_lengths, periods), 1):
        mid = Ln - lp - rp
        if mid % p:
            raise ValueError('interior length must be divisible by period')
        blk = list(w[lp:lp + p])
        for off in range(p):
            if (i, lp + off + 1) in hole_set:
                if mid >= 2 * p:
                    blk[off] = w[lp + p + off]
                else:
                    blk[off] = 1
        for pos in range(lp, Ln - rp):
            depth = pos + 1
            if (i, depth) in hole_set:
                continue
            if w[pos] != blk[(pos - lp) % p]:
                raise ValueError(f'arm {i} fails period {p} at depth {depth}')

    res = general_full_identity_array(lengths, holes, centre, words)
    if not any(res):
        raise ArithmeticError('unexpected vanishing identity on obstructed class')

    lcm_info = nwc.cyclotomic_lcm(periods)
    D_terms = list(lcm_info['lcm_poly'].items())
    iv = cert['intervals']
    lo_scan = iv['non_bin_max'] + 1
    hi_scan = iv['AB'][1]
    gaps_empty = True
    bins = {'BC': {}, 'AC': {}, 'AB': {}}
    for n in range(lo_scan, hi_scan + 1):
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
        if d < 2:
            continue
        phi_d = lcm_info['phis'][d]
        for bname, bpoly in bins.items():
            if nwc.poly_mod_cyclotomic(bpoly, d, phi_d):
                cyclotomic_witness = {'bin': bname, 'divisor': d}
                break
        if cyclotomic_witness is not None:
            break

    # Check (1 - z) bin sum at z = 1 (for tip_arms != (1,)) or upper-shell discrepancy above A
    upper_nonzero = any(res[lengths[0] + 2:])
    if cyclotomic_witness is None and not upper_nonzero:
        raise ArithmeticError('bin and upper checks both vanished unexpectedly')

    return {
        'obstructed': True,
        'homometric': False,
        'tip_arms': cert['tip_arms'],
        'bins_disjoint': gaps_empty,
        'cyclotomic_witness': cyclotomic_witness,
        'upper_shell_nonzero': upper_nonzero,
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
            out = general_hole_certificate(
                d['t'], d['holes'], d['periods'], d['prefix_lengths'], d['suffix_lengths'],
            )
        else:
            d = _load_json(args.audit_json)
            out = audit_general_hole_multi_period(
                d['t'], d['holes'], d['centre'], d['words'],
                d['periods'], d['prefix_lengths'], d['suffix_lengths'],
            )
        print(json.dumps(out, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError) as err:
        parser.error(str(err))


if __name__ == '__main__':
    raise SystemExit(main())
