"""Fixed-size necessary equations for arbitrary holes; not a homometry solver.

Only standard-library integer arithmetic. See LONG_FRONTIER_INFINITE.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from published_cases import check_pair, validate_lengths, validate_vertices


def distance(u, v):
    return abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]


def shell_terms(lengths, vertex, holes):
    """(Exponent, coefficient, slope) as the vertex advances by g depths.

    Slope measures exponent change divided by g; it is constant inside
    each hole-cut interval. The centre does not advance.
    """
    arm, depth = vertex
    terms = []
    if arm == 0:
        terms.append((0, 1, 0))
        for length in lengths:
            terms.append((length, -1, 0))
    else:
        terms.extend([(depth, 1, 1), (lengths[arm - 1] - depth, -1, -1)])
        for other, length in enumerate(lengths, 1):
            if other != arm:
                terms.append((depth + length, -1, 1))
    for hole in holes:
        delta = distance(vertex, hole)
        slope = 0 if arm == 0 else (-1 if arm == hole[0] and depth < hole[1] else 1)
        terms.extend([(delta - 1, -1, slope), (delta, 1, slope)])
    return terms


def column(lengths, vertex, holes, modulus):
    """Coefficients of balance and the normalized shell modulo z^g-1."""
    result = [1] + [0] * modulus
    for power, value, _ in shell_terms(lengths, vertex, holes):
        result[1 + power % modulus] += value
    return result


def compressed_system(lengths, holes=(), modulus=8):
    """At most 1+g*(3+|H|) cells, independent of arm lengths.

    A cell is a depth residue within an arm interval cut at each omitted
    vertex. Its integer variable is a signed count, not an individual sign.
    """
    lengths = validate_lengths(lengths)
    holes = validate_vertices(lengths, holes)
    if type(modulus) is not int or not 2 <= modulus <= 256:
        raise ValueError("modulus must be an integer from 2 through 256")
    if len(holes) > 2:
        raise ValueError("this reduction accepts at most two omitted vertices")
    if (1 + sum(lengths) - len(holes)) % 2:
        raise ValueError("the retained order must be even")
    cells = []

    def append(arm, lo, hi, residue, first, count):
        moment_constant, moment_linear = [0]*modulus, [0]*modulus
        for power, value, slope in shell_terms(lengths, (arm, first), holes):
            quotient, remainder = divmod(power, modulus)
            moment_constant[remainder] += value * quotient
            moment_linear[remainder] += value * slope
        cells.append({"arm": arm, "lo": lo, "hi": hi, "residue": residue,
                      "first": first, "count": count,
                      "column": column(lengths, (arm, first), holes, modulus),
                      "moment_constant": moment_constant, "moment_linear": moment_linear})

    if (0, 0) not in holes:
        append(0, 0, 0, 0, 0, 1)
    for arm, length in enumerate(lengths, 1):
        cuts = [0] + sorted(d for i, d in holes if i == arm) + [length + 1]
        for left, right in zip(cuts, cuts[1:]):
            lo, hi = left + 1, right - 1
            for residue in range(modulus):
                first = lo + (residue - lo) % modulus
                if first <= hi:
                    append(arm, lo, hi, residue, first,
                           (hi - first) // modulus + 1)
    return {"lengths": list(lengths), "holes": [list(h) for h in holes],
            "modulus": modulus, "cells": cells, "equations": modulus + 1,
            "retained": 1 + sum(lengths) - len(holes),
            "cell_bound": 1 + modulus * (3 + len(holes)),
            "status": "necessary_equations_only", "infinite_family_proved": False}


def verify_counts(system, counts):
    """Validate an aggregate witness by rebuilding, never trusting saved cells."""
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    cells = rebuilt["cells"]
    if len(counts) != len(cells):
        raise ValueError("one signed count is required for each rebuilt cell")
    for cell, value in zip(cells, counts):
        if type(value) is not int or abs(value) > cell["count"] or (
                value - cell["count"]) % 2:
            raise ValueError("signed count violates a cell's bounds or parity")
    residual = [sum(value * cell["column"][row]
                    for cell, value in zip(cells, counts))
                for row in range(rebuilt["equations"])]
    return {"aggregate_equations_hold": not any(residual), "residual": residual,
            "homometric_pair_proved": False}


def verify_moments(system, counts, moments):
    """Necessary double-root equations, with exact local attainability bounds.

    A moment is sum(j * sign_j) over the cell's positions j=0,...,n-1.
    Passing is not an exact-distance verdict.
    """
    checked = verify_counts(system, counts)
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    if len(moments) != len(counts):
        raise ValueError("one signed first moment is required for each cell")
    for cell, value, moment in zip(rebuilt["cells"], counts, moments):
        n = cell["count"]
        plus = (n + value) // 2
        total = n*(n-1)//2
        low = plus*(plus-1) - total
        high = plus*(2*n-plus-1) - total
        if type(moment) is not int or not low <= moment <= high or (moment + total) % 2:
            raise ValueError("signed moment is not attainable with this cell count")
    residual = [sum(value*cell["moment_constant"][r] + moment*cell["moment_linear"][r]
                    for cell, value, moment in zip(rebuilt["cells"], counts, moments))
                for r in range(rebuilt["modulus"])]
    checked.update(first_moment_equations_hold=checked["aggregate_equations_hold"] and not any(residual),
                   moment_residual=residual)
    return checked


def _second_moment_coefficients(lengths, holes, modulus, cells):
    """Coefficients of X_c, Y_c=sum j*s_j, and Z_c=sum C(j,2)*s_j in u^2 ((z^g-1)^2)."""
    const_rows, lin_rows, quad_rows = [], [], []
    for cell in cells:
        c0, c1, c2 = [0] * modulus, [0] * modulus, [0] * modulus
        for power, value, slope in shell_terms(lengths, (cell["arm"], cell["first"]), holes):
            q, r = divmod(power, modulus)
            c0[r] += value * (q * (q - 1) // 2)
            c1[r] += value * (q * slope + (slope * (slope - 1) // 2))
            c2[r] += value * (slope * slope)
        const_rows.append(c0)
        lin_rows.append(c1)
        quad_rows.append(c2)
    return const_rows, lin_rows, quad_rows


def second_moment_bounds(n, count, moment):
    """Exact Schur bounds [low, high] and mod-2 parity for Z = sum_{j=0}^{n-1} C(j,2)*s_j."""
    if type(n) is not int or n < 1:
        raise ValueError("cell size n must be a positive integer")
    if type(count) is not int or abs(count) > n or (count - n) % 2:
        raise ValueError("invalid cell count parity or bounds")
    p = (n + count) // 2
    tot_y = n * (n - 1) // 2
    y_lo = p * (p - 1) - tot_y
    y_hi = p * (2 * n - p - 1) - tot_y
    if type(moment) is not int or not y_lo <= moment <= y_hi or (moment + tot_y) % 2:
        raise ValueError("signed moment is not attainable with this cell count")
    tot_z = n * (n - 1) * (n - 2) // 6
    if p == 0:
        return -tot_z, -tot_z, (-tot_z) % 2
    if p == n:
        return tot_z, tot_z, tot_z % 2
    m_sum = (moment + tot_y) // 2

    def sum_c2(u):
        return u * (u - 1) * (u - 2) // 6

    b, rem = divmod(m_sum - p * (p - 1) // 2, p)
    s2_min = (sum_c2(b + p - rem) - sum_c2(b)) + (sum_c2(b + p + 1) - sum_c2(b + p - rem + 1))
    max_sum = p * (2 * n - p - 1) // 2
    q = (max_sum - m_sum) // (n - p)
    if q == p:
        s2_max = sum_c2(p)
    else:
        r_top = p - q - 1
        mid_pos = m_sum - q * (q - 1) // 2 - r_top * (2 * n - r_top - 1) // 2
        s2_max = sum_c2(q) + mid_pos * (mid_pos - 1) // 2 + (sum_c2(n) - sum_c2(n - r_top))
    return 2 * s2_min - tot_z, 2 * s2_max - tot_z, (-tot_z) % 2


def verify_triple_moments(system, counts, moments, second_moments):
    """Validate all 25 equations E(z) == 0 mod (z^g-1)^3 plus exact (Y, Z) Schur bounds."""
    checked = verify_moments(system, counts, moments)
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    cells = rebuilt["cells"]
    if len(second_moments) != len(cells):
        raise ValueError("one signed second moment is required for each cell")
    for cell, count, moment, z_val in zip(cells, counts, moments, second_moments):
        z_lo, z_hi, z_par = second_moment_bounds(cell["count"], count, moment)
        if type(z_val) is not int or not z_lo <= z_val <= z_hi or z_val % 2 != z_par:
            raise ValueError("signed second moment is not attainable with this count and first moment")
    lengths = tuple(system["lengths"])
    holes = tuple(tuple(h) for h in system["holes"])
    c0, c1, c2 = _second_moment_coefficients(lengths, holes, rebuilt["modulus"], cells)
    residual = [
        sum(counts[j] * c0[j][r] + moments[j] * c1[j][r] + second_moments[j] * c2[j][r]
            for j in range(len(cells)))
        for r in range(rebuilt["modulus"])
    ]
    checked.update(
        second_moment_equations_hold=checked["first_moment_equations_hold"] and not any(residual),
        second_moment_residual=residual,
    )
    return checked


EVEN_COUNTS = (1, 0, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, -1, -1, 1, 1,
               1, 1, 1, 1, 0, 1, 1, -1, -1, -1, 0, 0, 0, -1, -1, -1, -1)


def even_barrier(t):
    """Exact modular-distance witness for every even t, without a search."""
    if type(t) is not int or t < 0 or t % 2:
        raise ValueError("the proved modular barrier requires even nonnegative t")
    system = compressed_system(tuple(n + 7560*t for n in (227, 67, 11)),
                               [(2, 4), (2, 10)])
    system["signed_counts"] = list(EVEN_COUNTS)
    system.update(verify_counts(system, EVEN_COUNTS))
    return system


def moment_obstruction(t):
    """Reject the displayed counts at t=0 mod 4, for every possible local order.

    This does not reject other signed counts, or other omitted vertices.
    """
    if type(t) is not int or t < 0 or t % 4:
        raise ValueError("the first-moment obstruction requires t divisible by four")
    system = even_barrier(t)
    weights = (0, -1, 1, 2, 2, 1, -1, 0)
    coefficients = [sum(w*v for w, v in zip(weights, cell["moment_linear"]))
                    for cell in system["cells"]]
    constant = sum(value*sum(w*v for w, v in zip(weights, cell["moment_constant"]))
                   for cell, value in zip(system["cells"], system["signed_counts"]))
    parity_term = sum(coefficient*(-cell["count"]*(cell["count"]-1)//2 % 2)
                      for coefficient, cell in zip(coefficients, system["cells"]))
    actual = (constant + parity_term) % 8
    valid = all(c % 4 == 0 for c in coefficients) and actual != 0
    return {"t": t, "weights": weights, "modulus": 8, "constant": constant,
            "parity_term": parity_term, "weighted_residual_modulus": actual,
            "fixed_counts_obstructed": valid, "arbitrary_counts_obstructed": False,
            "all_omissions_obstructed": False, "infinite_family_proved": False}


MOMENTS_WITNESS_BRANCHES = {
    1: (
        (-1, -1, 3, 2, 0, -3, -3, 1, 3, 1, -1, -2, 0, -1, 3, -1, -1, -2, -1, -1, 3, 2, 2, -2, 0),
        (0, 88808, -61752, -106513, 141895, 0, 0, -130668, 6796, 0, 0, -1, -1, 0, 0, 0, 0, -1, -1, -1, -186705, 25633, -1, -1, -1),
        (0, 385560, -268380, -457380, 616140, 0, 0, -563220, 30240, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -808920, 113400, 0, 0, 0),
    ),
    2: (
        (-1, 2, 0, 1, -1, -2, -2, 0, 0, -2, 2, -1, 1, -2, 2, 0, 2, -1, -2, 0, 2, 3, 1, -1, -1),
        (0, -115241, 82579, 107695, -188197, -1, -1, 146071, -13425, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 234352, -46043, -1, -1, -1),
        (0, -226800, 162540, 211680, -370440, 0, 0, 287280, -26460, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 461160, -90720, 0, 0, 0),
    ),
    3: (
        (1, -3, 3, -2, 0, -3, 3, -1, 1, -1, 3, -2, 0, -1, 1, 1, 1, 0, -1, 3, 3, 0, -2, -2, -2),
        (0, 691051, -492915, -780660, 1118798, -1, -1, -987385, 59367, -1, -1, 0, 0, -1, -1, -1, -1, 0, 0, 0, -1446080, 230746, 0, 0, 0),
        (0, 884520, -631260, -1001700, 1432620, 0, 0, -1266300, 75600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1852200, 294840, 0, 0, 0),
    ),
    4: (
        (1, 0, -2, 1, 1, 4, -4, 2, 2, -2, 0, -1, -1, -2, -2, 2, -2, 3, 0, 0, 2, -1, 1, -1, -1),
        (0, 1216558, -854630, -1245878, 1940448, 0, 0, -1619194, 123218, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -2485193, 440618, 0, 0, 0),
        (0, 1232280, -865620, -1262520, 1965600, 0, 0, -1640520, 124740, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2517480, 446040, 0, 0, 0),
    ),
}


def moments_witness(t):
    """Explicit 17-equation witness (mod (z^8-1)^2 and quadratic bounds) for every t>=1."""
    if type(t) is not int or t < 1:
        raise ValueError("the 17-equation parametric witness requires integer t>=1")
    t0 = ((t - 1) % 4) + 1
    k = (t - t0) // 4
    counts, y0, dy = MOMENTS_WITNESS_BRANCHES[t0]
    moments = [base + k * slope for base, slope in zip(y0, dy)]
    system = compressed_system(tuple(n + 7560 * t for n in (227, 67, 11)), [(1, 1), (2, 1)], 8)
    system["t"] = t
    system["branch_base_t"] = t0
    system["signed_counts"] = list(counts)
    system["signed_moments"] = moments
    system.update(verify_moments(system, counts, moments))
    return system


TRIPLE_ROOT_WITNESS_BRANCHES = {
    1: (
        (-1, -1, 3, 2, 0, -3, -3, 1, 3, 1, -1, -2, 0, -1, 3, -1, -1, -2, -1, -1, 3, 2, 2, -2, 0),
        (0, -158618, 47900, -165755, 89809, -118926, 95458, -181316, 51486, 80590, 27450, 94703, -25777, 39994, -34898, 83234, 27902, 64609, -73423, 62719, -63069, 91801, -59311, 91069, -76449),
        (0, -922688, 632368, -1208678, 785790, -811922, 793942, -1215868, 638646, 282720, 9078, 575346, -159988, 169862, -151824, 568156, 12676, 618560, -627756, 618074, -625934, 636520, -637710, 632420, -636066),
        (0, -1717256, 1704710, -2071980, 1730500, -1273148, 1689526, -2070922, 1703388, 580864, -482102, 935588, -507892, 136756, -466918, 934530, -480780, 1136392, -1222608, 1136392, -1222608, 1136392, -1222608, 1136392, -1222608),
        (0, -75220824, 22522344, -81274228, 43492494, -59646414, 47235056, -86305492, 25554006, 39904592, 12670182, 44782734, -12424532, 16885052, -16223170, 41504732, 14189378, 31453348, -34140235, 29400403, -29985705, 41359334, -27822654, 45360342, -36137192),
        (0, -752894012, 397801938, -890687216, 554855306, -613330818, 557331982, -929483276, 412596804, 278162404, 43324614, 422826472, -121650462, 137116558, -143365136, 423494854, 49170910, 455570678, -424152760, 414124136, -413829538, 466851192, -399832238, 511499756, -433734706),
        (0, -2565271812, 2022089912, -3291285766, 2335828964, -2151983640, 2330381620, -3301305156, 2027119790, 821477940, -206010546, 1544028974, -534471048, 387090268, -509096482, 1524584482, -203089530, 1710039880, -1758399358, 1707694590, -1756163834, 1737039954, -1785911444, 1737548116, -1780966434),
        (0, -3245640032, 3221898262, -3916010972, 3270650852, -2406199800, 3193151580, -3914057230, 3219426004, 1097743332, -911189586, 1768155284, -959910028, 258435092, -882493840, 1766208226, -908724676, 2147901686, -2310698576, 2147784780, -2310723534, 2147769212, -2310674622, 2147888826, -2310690240),
    ),
    2: (
        (-1, 2, 0, 1, -1, -2, -2, 0, 0, -2, 2, -1, 1, -2, 2, 0, 2, -1, -2, 0, 2, 3, 1, -1, -1),
        (0, -224133, 230987, -221581, 195003, -230341, 195335, -222887, 231769, 65519, -68143, 63299, -37557, 67887, -35321, 63901, -67365, 153969, -160254, 154226, -156238, 160289, -158449, 155781, -161011),
        (0, -919110, 897998, -820484, 849820, -915068, 853862, -809982, 902214, 296910, -279020, 181084, -230186, 288328, -226142, 191586, -274802, 627618, -610446, 629088, -618422, 616234, -624828, 609244, -619240),
        (0, -892228, 1050064, -967562, 819772, -454960, 788022, -967628, 1050064, 387164, -382728, 462498, -152436, -50104, -120686, 462564, -382728, 505064, -667336, 505064, -667336, 505064, -667336, 505064, -667336),
        (0, -214398892, 221769936, -212005127, 187953573, -220067090, 188168810, -213270362, 222063388, 63728148, -64762684, 60969835, -35230365, 64844770, -33748284, 60833532, -64509242, 146536751, -150099728, 145964956, -147718650, 150417281, -149615883, 147951121, -151689815),
        (0, -1294062660, 1293398878, -1202370990, 1192327650, -1303843310, 1172172050, -1206511364, 1291453738, 424037740, -397300874, 304168986, -300887752, 410122372, -278068756, 293104240, -395254532, 854009322, -867601366, 878163548, -876883408, 881263696, -861265134, 880364236, -876815158),
        (0, -2600164630, 2706797186, -2470949244, 2399965224, -2160119090, 2371176270, -2461028298, 2708909692, 924846130, -889817520, 790271366, -572375154, 502638410, -547616560, 797433518, -888073142, 1664466948, -1781461692, 1675474598, -1798589272, 1637953718, -1816484824, 1629215254, -1803005568),
        (0, -1686269852, 1984591072, -1828689260, 1549377166, -859863032, 1489309196, -1828837634, 1984579968, 731791728, -723366290, 874134054, -288143384, -94680952, -228076496, 874225246, -723370848, 954470554, -1261228260, 954525366, -1261258448, 954556860, -1261158140, 954578436, -1261197050),
    ),
    3: (
        (1, -3, 3, -2, 0, -3, 3, -1, 1, -1, 3, -2, 0, -1, 1, 1, 1, 0, -1, 3, 3, 0, -2, -2, -2),
        (0, -1237811, 1215369, -1232948, 1273544, -1230515, 1203223, -1239043, 1215917, 350903, -347215, 352024, -409604, 350919, -336611, 349377, -347265, 873532, -857730, 868174, -851778, 879462, -854878, 876950, -856530),
        (0, -3417694, 3196134, -3186696, 3272564, -3309978, 3272110, -3188996, 3199866, 1078560, -859702, 847060, -933028, 980828, -933478, 844764, -861858, 2327702, -2324532, 2318078, -2325810, 2324668, -2324332, 2323718, -2322520),
        (0, -2118580, 2155942, -2239394, 2142746, -2054742, 2142262, -2239394, 2155944, 559148, -616414, 679962, -603218, 495310, -602734, 679962, -616416, 1559432, -1539528, 1559432, -1539528, 1559432, -1539528, 1559432, -1539528),
        (0, -1767674041, 1734019441, -1764797810, 1820475584, -1762590125, 1718437943, -1768790825, 1739076337, 499527485, -497654623, 499666344, -584013164, 494050247, -478963855, 498196183, -493632343, 1236699554, -1215078088, 1226997656, -1211813676, 1241830516, -1210122334, 1246982204, -1213547502),
        (0, -7213390614, 6876500256, -6867033876, 7081150264, -7067626736, 6928266604, -6915209268, 6890870208, 2190992920, -1915274786, 1861158674, -2108871328, 2062597058, -1957998376, 1887779326, -1914885926, 4956970660, -4910881200, 4926519204, -4921027996, 4948687594, -4908449328, 4979230708, -4906076594),
        (0, -9486949444, 9117925138, -9223823936, 9253582412, -9195717842, 9245567464, -9222127192, 9129109216, 2834171056, -2500183588, 2574720294, -2618428770, 2550857970, -2625361178, 2562794014, -2500066734, 6603608654, -6570840758, 6591138620, -6583447846, 6596848042, -6570233172, 6608561498, -6570043998),
        (0, -4004108636, 4074814086, -4232395472, 4049762286, -3883495090, 4048788778, -4232526682, 4074800672, 1056764102, -1165124950, 1285079078, -1140109674, 936206304, -1139100492, 1285194014, -1165156714, 2947380908, -2909708044, 2947342626, -2909717336, 2947331346, -2909720228, 2947397712, -2909698594),
    ),
    4: (
        (1, 0, -2, 1, 1, 4, -4, 2, 2, -2, 0, -1, -1, -2, -2, 2, -2, 3, 0, 0, 2, -1, 1, -1, -1),
        (0, 1338998, -1256662, 1332472, -1305512, 1322148, -1304628, 1337364, -1254618, -401452, 316980, -396452, 372712, -377524, 368660, -397948, 317792, -923654, 932239, -927805, 924355, -934214, 930766, -933270, 928318),
        (0, 2719454, -2554338, 2633654, -2531248, 2656978, -2529996, 2628004, -2551664, -858578, 688716, -760834, 663302, -787154, 664930, -766108, 686754, -1857376, 1858350, -1862772, 1855986, -1857528, 1858092, -1853942, 1856874),
        (0, 1228472, -1269766, 1328158, -1323114, 1394260, -1293480, 1328160, -1269766, -326800, 375598, -426486, 428946, -492588, 399312, -426488, 375598, -901672, 894168, -901672, 894168, -901672, 894168, -901672, 894168),
        (0, 2544691096, -2390426954, 2533830376, -2486359616, 2509336886, -2480534254, 2542406162, -2390935794, -760664248, 598227242, -750386638, 707382748, -712666216, 697225146, -756016368, 603663300, -1755274958, 1759791664, -1751912478, 1743836670, -1766777294, 1753736012, -1760669354, 1756409882),
        (0, 7701781872, -7204331004, 7540785146, -7297788672, 7529252502, -7286698374, 7513901806, -7216296416, -2382923262, 1887578858, -2225659034, 1992575412, -2194545348, 1962050340, -2194671370, 1902353296, -5265907570, 5261940256, -5271564278, 5255449228, -5279103928, 5271959228, -5265445238, 5260318452),
        (0, 7481298032, -7245420326, 7499930128, -7300993556, 7669092742, -7236258312, 7494166440, -7243994880, -2234813828, 2013817582, -2243278938, 2065288776, -2419782342, 2013895776, -2257800756, 2011811400, -5218721158, 5202795912, -5226426564, 5197848948, -5213690408, 5194345196, -5202260976, 5203553032),
        (0, 2321805256, -2399763778, 2510249226, -2500718986, 2635115788, -2444735248, 2510200614, -2399806502, -617662188, 709834430, -806142048, 810802026, -930964684, 754715262, -806026940, 709878208, -1704151952, 1689938316, -1704159904, 1689985112, -1704173410, 1690022848, -1704184818, 1689943372),
    ),
}


def triple_moments_witness(t):
    """Explicit 25-equation witness (mod (z^8-1)^3 and exact Schur bounds) for all t>=1."""
    if type(t) is not int or t < 1:
        raise ValueError("the 25-equation parametric witness requires integer t>=1")
    t0 = ((t - 1) % 4) + 1
    k = (t - t0) // 4
    counts, y0, y1, y2, z0, z1, z2, z3 = TRIPLE_ROOT_WITNESS_BRANCHES[t0]
    k2 = k * k
    k3 = k2 * k
    moments = [a + k * b + k2 * c for a, b, c in zip(y0, y1, y2)]
    second_moments = [a + k * b + k2 * c + k3 * d for a, b, c, d in zip(z0, z1, z2, z3)]
    system = compressed_system(tuple(n + 7560 * t for n in (227, 67, 11)), [(1, 1), (2, 1)], 8)
    system["t"] = t
    system["branch_base_t"] = t0
    system["signed_counts"] = list(counts)
    system["signed_moments"] = moments
    system["signed_second_moments"] = second_moments
    system.update(verify_triple_moments(system, counts, moments, second_moments))
    return system


def bramble_second_moment_defect(t):
    """Prove the earlier 17-equation witness cannot lift to (z^8-1)^3 at any t>=1."""
    if type(t) is not int or t < 1:
        raise ValueError("defect check requires integer t>=1")
    w = moments_witness(t)
    lam = (-1, 1, -1, 1, -1, 1, -1, 1)
    c0, c1, c2 = _second_moment_coefficients(tuple(w["lengths"]), ((1, 1), (2, 1)), 8, w["cells"])
    lam_c2 = [sum(lam[r] * c2[j][r] for r in range(8)) for j in range(len(w["cells"]))]
    defect = sum(lam[r] * sum(w["signed_counts"][j] * c0[j][r] + w["signed_moments"][j] * c1[j][r]
                              for j in range(len(w["cells"])))
                 for r in range(8))
    return {
        "t": t, "branch_base_t": w["branch_base_t"], "weights_E_double_prime_at_minus_1": list(lam),
        "second_moment_quadratic_annihilated": not any(lam_c2),
        "weighted_second_moment_defect": defect,
        "triple_root_lift_possible_for_earlier_witness": not any(lam_c2) and defect == 0,
    }


def structural_tail_obstructions(t):
    """Verify synchronized periodic fixed-prefix-hole and terminal constant-run obstructions."""
    if type(t) is not int or t < 1:
        raise ValueError("structural tail obstructions require integer t>=1")
    a, b, c = (n + 7560 * t for n in (227, 67, 11))
    return {
        "t": t, "lengths": [a, b, c],
        "synchronized_periodic_fixed_hole_Q2_possible": False,
        "synchronized_periodic_reason": "B_1[j]+B_2[j]+B_3[j] in {-3,-1,1,3} is odd and nonzero",
        "terminal_constant_run_possible": False,
        "terminal_constant_run_intervals": [[a - 216, a], [b - 216, b], [c - 160, c]],
        "cross_arm_23_exceeds_max_arm": b + c > a,
        "bramble_17eq_defect": bramble_second_moment_defect(t),
    }


def lift_counts(system, counts, max_vertices=512):
    """Realize signed counts by choosing the earliest depths in each cell.

    This constructs a modular-distance pair only, not an exact-distance pair.
    The explicit bound prevents accidental expansion of a huge symbolic tree.
    """
    rebuilt = compressed_system(system["lengths"], system["holes"], system["modulus"])
    if 1 + sum(rebuilt["lengths"]) > max_vertices:
        raise ValueError("lift size limit exceeded; no exact-distance verdict")
    if not verify_counts(rebuilt, counts)["aggregate_equations_hold"]:
        raise ValueError("cannot lift a failed aggregate certificate")
    left, right = [], []
    for cell, value in zip(rebuilt["cells"], counts):
        plus = (cell["count"] + value) // 2
        for j in range(cell["count"]):
            vertex = (cell["arm"], cell["first"] + j * rebuilt["modulus"])
            (left if j < plus else right).append(vertex)
    return left, right


def small_counts(system, max_odd=32):
    """Try only zero on even cells and +/-1 on odd cells, by meet in the middle.

    Failure is inconclusive even for the compressed equations. This search
    finds small aggregate witnesses; it does not assign homometric sets.
    """
    cells = system["cells"]
    odd = [i for i, cell in enumerate(cells) if cell["count"] % 2]
    if len(odd) > max_odd:
        return None
    # Simultaneous negation permits fixing the first nonzero count to +1.
    fixed = odd[:1]
    rest = odd[1:]
    middle = len(rest) // 2

    def vectors(indices):
        width = system["equations"]
        value = [-sum(cells[i]["column"][r] for i in indices) for r in range(width)]
        previous = 0
        yield tuple(value), 0
        for word in range(1, 1 << len(indices)):
            gray = word ^ (word >> 1)
            changed = gray ^ previous
            bit = changed.bit_length() - 1
            step = 2 if gray & changed else -2
            for r, coefficient in enumerate(cells[indices[bit]]["column"]):
                value[r] += step * coefficient
            yield tuple(value), gray
            previous = gray

    left, right = rest[:middle], rest[middle:]
    lookup = {value: word for value, word in vectors(left)}
    base = cells[fixed[0]]["column"] if fixed else [0] * system["equations"]
    for value, right_word in vectors(right):
        wanted = tuple(-a - b for a, b in zip(base, value))
        if wanted in lookup:
            result = [0] * len(cells)
            for i in fixed:
                result[i] = 1
            for indices, word in [(left, lookup[wanted]), (right, right_word)]:
                for bit, index in enumerate(indices):
                    result[index] = 1 if word >> bit & 1 else -1
            return result
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int, nargs="?", default=0)
    parser.add_argument("--omit", nargs=2, type=int, action="append", default=[])
    parser.add_argument("--modulus", type=int, default=8)
    parser.add_argument("--system", action="store_true", help="include exact integer columns")
    parser.add_argument("--small-counts", action="store_true")
    parser.add_argument("--barrier-even", action="store_true",
                        help="use the proved modular witness for even t")
    parser.add_argument("--lift-check", action="store_true",
                        help="check the canonical lift on the original tree (at most 512 vertices)")
    parser.add_argument("--first-moments", action="store_true",
                        help="test the earliest-plus lift's normalized shell at double roots")
    parser.add_argument("--moment-obstruction", action="store_true",
                        help="reject the displayed signed counts for every order, at t=0 mod 4")
    parser.add_argument("--moments-witness", action="store_true",
                        help="emit a proved 17-equation witness for holes (1,1),(2,1) and any t>=1")
    parser.add_argument("--triple-moments-witness", action="store_true",
                        help="emit a proved 25-equation (z^8-1)^3 witness for holes (1,1),(2,1) and any t>=1")
    parser.add_argument("--structural-obstructions", action="store_true",
                        help="verify synchronized-periodic, constant-run, and 17-eq defect obstructions for t>=1")
    parser.add_argument("--verify", type=Path, help="verify a saved aggregate witness")
    args = parser.parse_args()
    try:
        if args.verify:
            saved = json.loads(args.verify.read_text())
            if "signed_second_moments" in saved:
                result = verify_triple_moments(saved, saved["signed_counts"],
                                               saved["signed_moments"], saved["signed_second_moments"])
                ok_key = "second_moment_equations_hold"
            elif "signed_moments" in saved:
                result = verify_moments(saved, saved["signed_counts"], saved["signed_moments"])
                ok_key = "first_moment_equations_hold"
            else:
                result = verify_counts(saved, saved["signed_counts"])
                ok_key = "aggregate_equations_hold"
            print(json.dumps(result, sort_keys=True))
            return 0 if result[ok_key] else 1
        if args.t < 0:
            raise ValueError("t must be nonnegative")
        if args.structural_obstructions:
            if args.omit or args.modulus != 8 or args.moments_witness or args.triple_moments_witness:
                raise ValueError("structural obstructions do not combine with witness or system options")
            print(json.dumps(structural_tail_obstructions(args.t), sort_keys=True))
            return 0
        if args.moment_obstruction:
            if args.omit or args.modulus != 8 or args.moments_witness or args.triple_moments_witness:
                raise ValueError("the moment obstruction fixes holes (2,4),(2,10) and modulus eight")
            print(json.dumps(moment_obstruction(args.t), sort_keys=True))
            return 0
        if args.triple_moments_witness:
            if args.omit or args.modulus != 8 or args.barrier_even or args.small_counts or args.lift_check or args.moments_witness:
                raise ValueError("the 25-equation witness fixes holes (1,1),(2,1) and modulus eight")
            result = triple_moments_witness(args.t)
            result["cell_count"] = len(result["cells"])
            if not args.system:
                del result["cells"]
            print(json.dumps(result, sort_keys=True))
            return 0
        if args.moments_witness:
            if args.omit or args.modulus != 8 or args.barrier_even or args.small_counts or args.lift_check:
                raise ValueError("the 17-equation witness fixes holes (1,1),(2,1) and modulus eight")
            result = moments_witness(args.t)
            result["cell_count"] = len(result["cells"])
            if not args.system:
                del result["cells"]
            print(json.dumps(result, sort_keys=True))
            return 0
        lengths = tuple(n + 7560 * args.t for n in (227, 67, 11))
        if args.barrier_even and (args.omit or args.modulus != 8):
            raise ValueError("the proved barrier fixes holes (2,4),(2,10) and modulus eight")
        result = (even_barrier(args.t) if args.barrier_even else
                  compressed_system(lengths, args.omit, args.modulus))
        if args.small_counts:
            counts = small_counts(result)
            result["signed_counts"] = counts
            result["small_counts_search"] = "found" if counts is not None else "inconclusive"
            if counts is not None:
                result.update(verify_counts(result, counts))
        if args.lift_check:
            if result.get("signed_counts") is None:
                raise ValueError("lift checking requires a signed-count witness")
            left, right = lift_counts(result, result["signed_counts"])
            checked = check_pair(lengths, left, right)
            result["lift_check"] = {key: checked[key] for key in
                                    ("homometric", "size", "target", "meets_target")}
            difference = checked["difference"]
            result["lift_check"]["first_mismatch"] = (
                [min(difference), difference[min(difference)]] if difference else None)
        if args.first_moments:
            if result.get("signed_counts") is None:
                raise ValueError("first moments require a signed-count witness")
            counts = result["signed_counts"]
            moments = []
            for cell, value in zip(result["cells"], counts):
                n = cell["count"]
                plus = (n + value)//2
                moments.append(plus*(plus-1) - n*(n-1)//2)
            result["signed_moments"] = moments
            result.update(verify_moments(result, counts, moments))
        result["cell_count"] = len(result["cells"])
        if not args.system:
            del result["cells"]
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
