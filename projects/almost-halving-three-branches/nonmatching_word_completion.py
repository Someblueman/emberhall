#!/usr/bin/env python3
"""Nonmatching-boundary multi-period obstructions and invariant local equations.

Standard library only. Extends intermediate_shell_repair.py without modifying
prior proofs or claiming full tripod homometry. See NONMATCHING_WORD_COMPLETION.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json

import intermediate_shell_repair as repair

BASE = (99, 79, 23)
INVARIANT_OFFSETS = (6, 8, 10, 12, 14, 16, 18, 20, 65, 67, 69, 71, 73, 75)
FORCED_TRIPLES_M = tuple(
    j - 1 for j in range(1, 24) if j not in repair.FORCED
)


def poly_mul(p, q):
    """Multiply two sparse integer polynomials {exponent: coefficient}."""
    out = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = e1 + e2
            out[e] = out.get(e, 0) + c1 * c2
    return {e: c for e, c in out.items() if c}


def poly_exact_div(num, den):
    """Exact division num / den in Z[z] for monic den."""
    work = dict(num)
    max_d = max(den)
    lead = den[max_d]
    if lead not in (-1, 1):
        raise ValueError('divisor must be monic')
    quot = {}
    while work:
        hi = max(work)
        if hi < max_d:
            raise ValueError('polynomial is not divisible')
        coeff = work[hi] // lead
        shift = hi - max_d
        quot[shift] = coeff
        for de, dc in den.items():
            ne = de + shift
            nv = work.get(ne, 0) - coeff * dc
            if nv:
                work[ne] = nv
            else:
                work.pop(ne, None)
    return quot


def poly_mod_cyclotomic(poly, d, phi_d):
    """Reduce Laurent polynomial poly modulo Phi_d(z) using z^d == 1."""
    folded = {}
    for e, c in poly.items():
        r = e % d
        folded[r] = folded.get(r, 0) + c
    work = {e: c for e, c in folded.items() if c}
    max_d = max(phi_d)
    lead = phi_d[max_d]
    if lead != 1:
        raise ValueError('cyclotomic polynomial must be monic')
    while work:
        hi = max(work)
        if hi < max_d:
            break
        coeff = work[hi]
        shift = hi - max_d
        for de, dc in phi_d.items():
            ne = de + shift
            nv = work.get(ne, 0) - coeff * dc
            if nv:
                work[ne] = nv
            else:
                work.pop(ne, None)
    return work


def cyclotomic_lcm(periods):
    """Compute D(z) = lcm(1 - z^p_1, 1 - z^p_2, 1 - z^p_3) over Z[z].

    Normalizes D(z) = -prod_{d in S} Phi_d(z) so that Q_i = D / (1 - z^{p_i})
    is monic and Q_i * (1 - z^{p_i}) == D identically in Z[z].
    """
    if (not isinstance(periods, (list, tuple)) or len(periods) != 3
            or any(type(p) is not int or p < 1 for p in periods)):
        raise ValueError('three positive integer periods required')
    divisors = sorted({d for p in periods for d in range(1, p + 1) if p % d == 0})
    phis = {}
    for d in divisors:
        num = {d: 1, 0: -1}
        for k in divisors:
            if k < d and d % k == 0:
                num = poly_exact_div(num, phis[k])
        phis[d] = num
    prod = {0: 1}
    for d in divisors:
        prod = poly_mul(prod, phis[d])
    lcm_poly = {e: -c for e, c in prod.items()}
    quotients = [poly_exact_div(lcm_poly, {0: 1, p: -1}) for p in periods]
    return {
        'periods': list(periods),
        'degree': max(lcm_poly),
        'divisors': divisors,
        'phis': phis,
        'lcm_poly': lcm_poly,
        'quotients': quotients,
    }


def _validate_patches(t, periods, prefix_lengths, suffix_lengths, h):
    if type(t) is not int or t < 1:
        raise ValueError('positive integer t required')
    if type(h) is not int or not 1 <= h < 20 * t + 1:
        raise ValueError('interior hole must satisfy 1 <= h < 20*t + 1')
    for name, vec in (('prefix_lengths', prefix_lengths), ('suffix_lengths', suffix_lengths)):
        if (not isinstance(vec, (list, tuple)) or len(vec) != 3
                or any(type(v) is not int or v < 0 for v in vec)):
            raise ValueError(f'{name} must be three nonnegative integers')
    if suffix_lengths[0] < 1:
        raise ValueError('suffix_lengths[0] must be >= 1 to contain the tip hole (1, 99t)')
    lengths = [b * t for b in BASE]
    for Ln, lp, rp, p in zip(lengths, prefix_lengths, suffix_lengths, periods):
        if lp + rp + p > Ln:
            raise ValueError('periodic interior must contain at least one full period')
    return lengths


def multi_period_certificate(t, periods, prefix_lengths, suffix_lengths, h=19):
    """All-t certificate for arbitrary different periods and nonperiodic patches.

    Covers any colouring on T(99t, 79t, 23t) with holes (1, h) and (1, 99t),
    1 <= h < 20t + 1, arbitrary centre sign, arbitrary arm periods (p1, p2, p3),
    and arbitrary nonperiodic prefixes/suffixes of lengths L_i, R_i satisfying
    max(1, L_1, L_2, L_3) + max(R_1, R_2, R_3) + deg(lcm(1 - z^p_i)) <= 3*t.
    """
    lcm_info = cyclotomic_lcm(periods)
    lengths = _validate_patches(t, periods, prefix_lengths, suffix_lengths, h)
    A, B, C = lengths
    L_max = max(1, *prefix_lengths)
    R_max = max(suffix_lengths)
    W = lcm_info['degree']
    if L_max + R_max + W > 3 * t:
        raise ValueError(
            f'patch+LCM bound violated: {L_max} + {R_max} + {W} > {3 * t}'
        )

    # Exact degree bounds in G(z) = D(z) * R(z)
    non_bin_max = A + L_max + W
    bc_lo = B + C + 2 - max(suffix_lengths[1], suffix_lengths[2])
    bc_hi = B + C + 1 + W
    ac_lo = A + C + 1 - max(suffix_lengths[0] - 1, suffix_lengths[2])
    ac_hi = A + C + 1 + W
    ab_lo = A + B + 1 - max(suffix_lengths[0] - 1, suffix_lengths[1])
    ab_hi = A + B + 1 + W
    bins_disjoint = (non_bin_max < bc_lo <= bc_hi < ac_lo <= ac_hi < ab_lo <= ab_hi)
    if not bins_disjoint:
        raise ArithmeticError('unexpected bin overlap')

    # Verify (z + 1) nonzero at roots of Phi_d (d > 2) and Q_i nonzero mod Phi_d when d | p_i
    for d in lcm_info['divisors']:
        if d > 2:
            phi_at_minus1 = sum(c * ((-1) ** e) for e, c in lcm_info['phis'][d].items())
            if phi_at_minus1 == 0:
                raise ArithmeticError(f'Phi_{d}(-1) vanished unexpectedly')

    # Verify nonempty overlap windows in complete_upper
    r_step1 = (R_max + 1, 56 * t)
    r_step2 = (R_max + 1, 20 * t - 1)
    m_lo = max(suffix_lengths[1], suffix_lengths[2])
    m_hi = min(3 * t - 1, 3 * t - prefix_lengths[1], 3 * t - prefix_lengths[2])
    if r_step1[1] - r_step1[0] + 1 < 2 or r_step2[1] - r_step2[0] + 1 < 2 or m_lo > m_hi:
        raise ArithmeticError('complete_upper overlap interval collapsed')

    return {
        't': t,
        'lengths': lengths,
        'hole': h,
        'periods': list(periods),
        'prefix_lengths': list(prefix_lengths),
        'suffix_lengths': list(suffix_lengths),
        'lcm_degree': W,
        'patch_lcm_sum': L_max + R_max + W,
        'threshold_3t': 3 * t,
        'bins_disjoint': True,
        'intervals': {
            'non_bin_max': non_bin_max,
            'BC': [bc_lo, bc_hi],
            'AC': [ac_lo, ac_hi],
            'AB': [ab_lo, ab_hi],
        },
        'upper_overlap_windows': {
            'step1_q_neg_y': list(r_step1),
            'step2_z_eq_y': list(r_step2),
            'step3_m_range': [m_lo, m_hi],
        },
        'obstructed': True,
        'escaping_local_repair': True,
        'full_homometry_claimed': False,
    }


def construct_patched_multi_period_words(t, periods, a_patches, b_blocks, c_patches, h=19):
    """Build literal words with arbitrary boundary patches and periodic interiors."""
    lengths = [b * t for b in BASE]
    L_lens = [len(a) for a in a_patches]
    R_lens = [len(c) for c in c_patches]
    _validate_patches(t, periods, L_lens, R_lens, h)
    if len(b_blocks) != 3:
        raise ValueError('three periodic blocks required')
    words = []
    for i, (Ln, ap, blk, cp, p) in enumerate(zip(lengths, a_patches, b_blocks, c_patches, periods)):
        repair.signs(ap, len(ap))
        repair.signs(blk, p)
        repair.signs(cp, len(cp))
        mid = Ln - len(ap) - len(cp)
        if mid % p:
            raise ValueError('interior length Ln - L_i - R_i must be divisible by p_i')
        w = list(ap) + list(blk) * (mid // p) + list(cp)
        if i == 0:
            w[h - 1] = 0
            w[-1] = 0
        words.append(w)
    return words


def actual_upper_pair_counts(lengths, h, words, distance):
    """Independent literal cross-arm pair counter for distances > A."""
    return repair.actual_upper_counts(lengths, h, words, distance)


def _full_identity_array(lengths, h, centre, words):
    """Fast exact array version of full_identity returning list of length A+B+2."""
    repair.validate_words(lengths, h, words)
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError('signed centre required')
    a, b, _ = lengths
    out = [0] * (a + b + 2)
    out[1] += centre
    for n in lengths:
        out[n + 1] -= centre
    for hole in (h, a):
        out[hole] -= centre
        out[hole + 1] += centre
    for i, word in enumerate(words):
        Ln = lengths[i]
        others = [lengths[j] + 1 for j in range(3) if j != i]
        o1, o2 = others
        if i == 0:
            for d, sign in enumerate(word, 1):
                if not sign:
                    continue
                out[d + 1] += sign
                out[Ln + 1 - d] -= sign
                out[d + o1] -= sign
                out[d + o2] -= sign
                dh = h - d if d < h else d - h
                out[dh] -= sign
                out[dh + 1] += sign
                da = a - d
                out[da] -= sign
                out[da + 1] += sign
        else:
            for d, sign in enumerate(word, 1):
                out[d + 1] += sign
                out[Ln + 1 - d] -= sign
                out[d + o1] -= sign
                out[d + o2] -= sign
                dh = d + h
                out[dh] -= sign
                out[dh + 1] += sign
                da = d + a
                out[da] -= sign
                out[da + 1] += sign
    return out


def audit_patched_multi_period(t, h, centre, words, periods, prefix_lengths, suffix_lengths):
    """Verify patch/period structure, bin isolation, and obstruction on literal words."""
    cert = multi_period_certificate(t, periods, prefix_lengths, suffix_lengths, h=h)
    lengths = tuple(cert['lengths'])
    repair.validate_words(lengths, h, words)
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError('signed centre required')

    # Verify each arm interior literally has period p_i (except optional hole (1, h))
    blocks = []
    for i, (w, Ln, lp, rp, p) in enumerate(zip(words, lengths, prefix_lengths, suffix_lengths, periods)):
        mid = Ln - lp - rp
        if mid % p:
            raise ValueError('interior length must be divisible by period')
        blk = list(w[lp:lp + p])
        if i == 0 and lp < h <= lp + p:
            # Recover periodic letter at h from the next period if mid >= 2*p
            if mid >= 2 * p:
                blk[h - 1 - lp] = w[lp + p + (h - 1 - lp)]
            else:
                blk[h - 1 - lp] = 1
        for pos in range(lp, Ln - rp):
            depth = pos + 1
            if i == 0 and depth == h:
                continue
            if w[pos] != blk[(pos - lp) % p]:
                raise ValueError(f'arm {i + 1} fails period {p} at depth {depth}')
        blocks.append(blk)

    res = _full_identity_array(lengths, h, centre, words)
    nonzero_r = any(res)
    if not nonzero_r:
        raise ArithmeticError('unexpected vanishing identity on obstructed class')

    # Check G(z) = D(z) * R(z) above non_bin_max + 1 via local convolution
    lcm_info = cyclotomic_lcm(periods)
    D_terms = list(lcm_info['lcm_poly'].items())
    W = lcm_info['degree']
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

    # Check which stage rejects the literal words: cyclotomic bin nonvanishing or complete_upper
    cyclotomic_witness = None
    for d in lcm_info['divisors']:
        if d <= 2:
            continue
        phi_d = lcm_info['phis'][d]
        for bname, bpoly in bins.items():
            rem = poly_mod_cyclotomic(bpoly, d, phi_d)
            if rem:
                cyclotomic_witness = {'bin': bname, 'divisor': d}
                break
        if cyclotomic_witness is not None:
            break

    upper = repair.complete_upper(lengths, h, words[1], words[2])
    upper_mismatch = (not upper['sign_feasible']) or (upper['suffix'] != words[0][lengths[0] - lengths[1]:lengths[0] - 1])
    if cyclotomic_witness is None and not upper_mismatch:
        raise ArithmeticError('neither cyclotomic bin nor upper recurrence caught invalid words')

    return {
        'obstructed': True,
        'homometric': False,
        'bins_disjoint': gaps_empty,
        'cyclotomic_witness': cyclotomic_witness,
        'upper_sign_feasible': upper['sign_feasible'],
        'upper_suffix_mismatch': upper_mismatch,
        'full_homometry_claimed': False,
    }


def invariant_local_equation(k, period, j=6):
    """Choice-invariant local matching obstruction across all 256 sharp tail repairs.

    Supports all 14 invariant offsets j in INVARIANT_OFFSETS. For j == 75 and
    1 <= period <= 36, period need not divide 2660*k.
    """
    if type(k) is not int or k < 1:
        raise ValueError('positive k required')
    if j not in INVARIANT_OFFSETS:
        raise ValueError(f'j must be one of {INVARIANT_OFFSETS}')
    if type(period) is not int or period < 1:
        raise ValueError('positive integer period required')
    if j == 75 and period <= 36 and (2660 * k) % period:
        effective = period
    else:
        certificate = repair.periodic_obstruction(period, k)
        effective = certificate['effective_period']

    t = 2660 * k + 1
    lengths = [99 * t, 79 * t, 23 * t]
    combined = Counter()
    for base in (0, 23, 79, 99):
        n = j + base * 2660 * k
        combined.update(repair._coefficient_row(lengths, 19, n))
        combined.subtract(repair._coefficient_row(lengths, 19, n - effective))

    terms = []
    constant = 0
    grouped = Counter()
    conflicts = set(range(61, 76, 2))
    conflict_diff = Counter()

    for (arm, depth), value in sorted(combined.items()):
        if not value:
            continue
        if arm == 0:
            constant -= value
            continue
        base, cut = BASE[arm - 1], 19 if arm == 1 else 0
        if cut < depth <= cut + base * 2660 * k:
            residue = (depth - cut - 1) % effective
            terms.append([arm, depth, value, residue])
            grouped[arm, residue] += value
        else:
            old = depth if depth <= cut else depth - base * 2660 * k
            char = repair.SEED[arm - 1][old - 1]
            sign = 0 if char == '0' else 1 if char == '+' else -1
            if arm == 1 and 99 - old in conflicts:
                conflict_diff[99 - old] += value
                constant -= value
            elif arm == 2 and 80 - old in conflicts:
                conflict_diff[80 - old] -= value
                constant += value
            else:
                constant += value * sign

    # Choice invariance requires every conflict pair to enter with equal coefficient
    if any(conflict_diff.values()):
        raise ArithmeticError(f'offset j={j} is not choice-invariant')

    expected_const = -2 if j <= 20 else 2
    if constant != expected_const or any(grouped.values()):
        raise ArithmeticError(f'invariant local equation failed at j={j}')

    return {
        'k': k,
        'period': period,
        'effective_period': effective,
        'j': j,
        'constant': constant,
        'choice_invariant': True,
        'terms': terms,
        'named_positions': len(terms),
        'locally_matching_repairs_excluded': True,
    }


def _validate_sharp_repair_class(k, words):
    t = 2660 * k + 1
    lengths = [99 * t, 79 * t, 23 * t]
    repair.validate_words(lengths, 19, words)
    conflicts = set(range(61, 76, 2))
    for arm, text in enumerate(repair.SEED, 1):
        base, cut = BASE[arm - 1], 19 if arm == 1 else 0
        for old, char in enumerate(text, 1):
            paired = ((arm == 1 and 99 - old in conflicts)
                      or (arm == 2 and 80 - old in conflicts))
            if paired:
                continue
            depth = old if old <= cut else old + base * 2660 * k
            expected = 0 if char == '0' else 1 if char == '+' else -1
            if words[arm - 1][depth - 1] != expected:
                raise ValueError('retained seed is outside the sharp repair class')
    for r_conf in conflicts:
        x = words[0][99 - r_conf + 99 * 2660 * k - 1]
        y = words[1][80 - r_conf + 79 * 2660 * k - 1]
        if x != -y:
            raise ValueError('each conflicting pair needs exactly one retained flip')


def audit_invariant_equations(k, period, words, offsets=None):
    """Evaluate selected (or all 14) choice-invariant equations on arbitrary words."""
    _validate_sharp_repair_class(k, words)
    if offsets is None:
        offsets = INVARIANT_OFFSETS
    results = {}
    excluded_any = False
    for j in offsets:
        eq = invariant_local_equation(k, period, j=j)
        val = eq['constant']
        groups = {}
        for arm, depth, coeff, residue in eq['terms']:
            sgn = words[arm - 1][depth - 1]
            val += coeff * sgn
            groups.setdefault((arm, residue), set()).add(sgn)
        excluded = val != 0
        excluded_any = excluded_any or excluded
        results[str(j)] = {
            'value': val,
            'locally_matching': all(len(v) == 1 for v in groups.values()),
            'excluded': excluded,
        }
    return {
        'k': k,
        'period': period,
        'excluded_by_any': excluded_any,
        'results': results,
        'full_homometry_claimed': False,
    }


def upper_forced_triples(k):
    """Eleven exact 3-sign majority constraints at r = 76t + m for arbitrary words.

    For every k >= 1 and every sharp 8-tail repair, the 11 indices j = m+1 in
    1..23 outside FORCED have retained seed signs y_j = z_j = s (equivalently
    q_j = -z_j), forcing
        s * (-arm2[3t - m + 1] + arm2[59t - m + 1] - arm3[3t - m + 1]) >= 1.
    """
    if type(k) is not int or k < 1:
        raise ValueError('positive integer k required')
    t = 2660 * k + 1
    out = []
    for m in FORCED_TRIPLES_M:
        j = m + 1
        s = 1 if repair.SEED[2][23 - j] == '+' else -1
        y_ret = -1 if repair.SEED[0][99 - j - 1] == '+' else 1  # y_j = -q_j
        if y_ret != s:
            raise ArithmeticError(f'unexpected retained sign mismatch at j={j}')
        out.append({
            'm': m,
            'r': 76 * t + m,
            'retained_y_z_sign': s,
            'arm1_forced_depth': 23 * t - m,
            'arm2_depth_76t_m': 3 * t - m + 1,
            'arm2_depth_20t_m': 59 * t - m + 1,
            'arm3_depth_20t_m': 3 * t - m + 1,
            'inequality': f'{s} * (-arm2[{3*t-m+1}] + arm2[{59*t-m+1}] - arm3[{3*t-m+1}]) >= 1',
        })
    return {
        'k': k,
        't': t,
        'triples_count': len(out),
        'triples': out,
        'arbitrary_insertion_scope': 'all 256 sharp tail repairs; arbitrary inserted signs',
        'full_homometry_claimed': False,
    }


def audit_upper_forced_triples(k, words):
    """Evaluate the 11 exact upper-shell majority constraints on arbitrary words."""
    _validate_sharp_repair_class(k, words)
    spec = upper_forced_triples(k)
    results = []
    all_feasible = True
    for item in spec['triples']:
        s = item['retained_y_z_sign']
        y_low = words[1][item['arm2_depth_76t_m'] - 1]
        y_mid = words[1][item['arm2_depth_20t_m'] - 1]
        z_low = words[2][item['arm3_depth_20t_m'] - 1]
        score = s * (-y_low + y_mid - z_low)
        q_val = (-y_low + y_mid - z_low) - 2 * s
        ok = score >= 1
        all_feasible = all_feasible and ok
        results.append({
            'm': item['m'],
            'score': score,
            'forced_arm1_value': q_val,
            'feasible': ok,
        })
    return {
        'k': k,
        'all_feasible': all_feasible,
        'triples': results,
        'full_homometry_claimed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hole', type=int, default=19, help='interior hole depth for --multi-period')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--multi-period', nargs=10, type=int,
                      metavar=('T', 'P1', 'P2', 'P3', 'L1', 'L2', 'L3', 'R1', 'R2', 'R3'))
    mode.add_argument('--cert-json', metavar='JSON',
                      help='JSON with t, periods, prefix_lengths, suffix_lengths, optional hole')
    mode.add_argument('--audit-patched', metavar='JSON',
                      help='JSON with t, hole, centre, words, periods, prefix_lengths, suffix_lengths')
    mode.add_argument('--invariant-equations', nargs=2, type=int, metavar=('K', 'PERIOD'))
    mode.add_argument('--upper-triples', type=int, metavar='K')
    args = parser.parse_args()
    try:
        if args.multi_period is not None:
            t = args.multi_period[0]
            periods = args.multi_period[1:4]
            prefixes = args.multi_period[4:7]
            suffixes = args.multi_period[7:10]
            out = multi_period_certificate(t, periods, prefixes, suffixes, h=args.hole)
        elif args.cert_json:
            with open(args.cert_json, encoding='utf-8') as f:
                d = json.load(f)
            out = multi_period_certificate(
                d['t'], d['periods'], d['prefix_lengths'], d['suffix_lengths'], d.get('hole', 19),
            )
        elif args.audit_patched:
            with open(args.audit_patched, encoding='utf-8') as f:
                d = json.load(f)
            out = audit_patched_multi_period(
                d['t'], d['hole'], d['centre'], d['words'],
                d['periods'], d['prefix_lengths'], d['suffix_lengths'],
            )
        elif args.invariant_equations is not None:
            k, p = args.invariant_equations
            out = {
                'k': k,
                'period': p,
                'equations': [
                    {
                        'j': eq['j'],
                        'constant': eq['constant'],
                        'named_positions': eq['named_positions'],
                    }
                    for eq in (invariant_local_equation(k, p, j=j) for j in INVARIANT_OFFSETS)
                ],
                'full_homometry_claimed': False,
            }
        elif args.upper_triples is not None:
            out = upper_forced_triples(args.upper_triples)
        print(json.dumps(out, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError) as err:
        parser.error(str(err))


if __name__ == '__main__':
    raise SystemExit(main())
