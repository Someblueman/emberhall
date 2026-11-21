"""Exact-distance lifting criteria and obstructions beyond low-order moments.

Standard-library exact integer and rational arithmetic only. See EXACT_LIFTING.md.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from long_frontier_infinite import compressed_system, shell_terms, verify_moments
from published_cases import check_pair

# Exact triple-root (z^8 - 1)^3 witnesses from finish 29561 of run e4c753e724c941c587d4ffff0f61eed9.
# Retained locally so verification works cleanly before or after e4c753 integration.
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

_PRIME_CERT = 1000000007


def _add_term(poly: dict[int, int], deg: int, coeff: int) -> None:
    if coeff == 0:
        return
    val = poly.get(deg, 0) + coeff
    if val:
        poly[deg] = val
    elif deg in poly:
        del poly[deg]


def exact_e_polynomial(
    lengths: tuple[int, int, int],
    s0: int,
    s1: list[int],
    s2: list[int],
    s3: list[int],
) -> dict[int, int]:
    """Build exact E(z) in Z[z] for T(a, b, c) with holes (1, 1), (2, 1)."""
    a, b, c = lengths
    if len(s1) != a - 1 or len(s2) != b - 1 or len(s3) != c:
        raise ValueError("sign word lengths must match retained depths 2..a, 2..b, 1..c")
    poly: dict[int, int] = {}
    for deg, coeff in ((0, -s0), (1, 2 * s0), (a, -s0), (b, -s0), (c, -s0)):
        _add_term(poly, deg, coeff)
    for k, val in enumerate(s1, 2):
        for deg, mult in ((k + 1, 1), (k - 2, -1), (k - 1, 1), (k + b, -1), (k + c, -1), (a - k, -1)):
            _add_term(poly, deg, mult * val)
    for k, val in enumerate(s2, 2):
        for deg, mult in ((k + 1, 1), (k - 2, -1), (k - 1, 1), (k + a, -1), (k + c, -1), (b - k, -1)):
            _add_term(poly, deg, mult * val)
    for k, val in enumerate(s3, 1):
        for deg, mult in ((k + 1, 2), (k, -1), (k + a, -1), (k + b, -1), (c - k, -1)):
            _add_term(poly, deg, mult * val)
    return poly


def e_hi_polynomial(
    lengths: tuple[int, int, int],
    s1: list[int],
    s2: list[int],
    s3: list[int],
) -> dict[int, int]:
    """Build E_hi(z) = -(z^b+z^c)S_1(z) - (z^a+z^c)S_2(z) - (z^a+z^b)S_3(z)."""
    a, b, c = lengths
    poly: dict[int, int] = {}
    for k, val in enumerate(s1, 2):
        _add_term(poly, k + b, -val)
        _add_term(poly, k + c, -val)
    for k, val in enumerate(s2, 2):
        _add_term(poly, k + a, -val)
        _add_term(poly, k + c, -val)
    for k, val in enumerate(s3, 1):
        _add_term(poly, k + a, -val)
        _add_term(poly, k + b, -val)
    return poly


def e_lo_polynomial(
    lengths: tuple[int, int, int],
    s0: int,
    s1: list[int],
    s2: list[int],
    s3: list[int],
) -> dict[int, int]:
    """Build E_lo(z) = E(z) - E_hi(z), all terms having degree <= a + 1."""
    a, b, c = lengths
    poly: dict[int, int] = {}
    for deg, coeff in ((0, -s0), (1, 2 * s0), (a, -s0), (b, -s0), (c, -s0)):
        _add_term(poly, deg, coeff)
    for k, val in enumerate(s1, 2):
        for deg, mult in ((k + 1, 1), (k - 2, -1), (k - 1, 1), (a - k, -1)):
            _add_term(poly, deg, mult * val)
    for k, val in enumerate(s2, 2):
        for deg, mult in ((k + 1, 1), (k - 2, -1), (k - 1, 1), (b - k, -1)):
            _add_term(poly, deg, mult * val)
    for k, val in enumerate(s3, 1):
        for deg, mult in ((k + 1, 2), (k, -1), (c - k, -1)):
            _add_term(poly, deg, mult * val)
    return poly


def e_hi_window_bounds() -> dict[str, list[int]]:
    """Exact t-independent bounds on (1+u)^{-945t} E_hi(z) mod (z^8-1)^3 for t >= 1."""
    max_r0 = [0] * 8
    max_r1 = [0] * 8
    max_r2 = [0] * 8
    for d in range(13, 229):
        coeff_bound = (
            (1 if 13 <= d <= 228 else 0)   # z^{11} S_1(z)
            + (1 if 13 <= d <= 228 else 0) # z^{11} S_2(z)
            + (1 if 69 <= d <= 228 else 0) # z^{67} S_1(z)
            + (1 if 68 <= d <= 228 else 0) # z^{67} S_3(z)
            + (1 if d == 228 else 0)       # z^{227} S_3(1)
        )
        q, r = divmod(d, 8)
        max_r0[r] += coeff_bound
        max_r1[r] += coeff_bound * q
        max_r2[r] += coeff_bound * (q * (q - 1) // 2)
    return {"max_r0": max_r0, "max_r1": max_r1, "max_r2": max_r2}


def shifted_e_hi_window_coeffs(
    t: int,
    s1: list[int],
    s2: list[int],
    s3: list[int],
) -> dict[str, list[int]]:
    """Compute R(z) = z^{-7560t} trunc_{<=a+1}(E_hi(z)) mod (z^8-1)^3 for a full sign word."""
    if type(t) is not int or t < 1:
        raise ValueError("shifted E_hi window requires integer t >= 1")
    shift = 7560 * t
    a = 227 + shift
    hi = e_hi_polynomial((a, 67 + shift, 11 + shift), s1, s2, s3)
    r0, r1, r2 = [0] * 8, [0] * 8, [0] * 8
    for deg, coeff in hi.items():
        if deg <= a + 1:
            q, r = divmod(deg - shift, 8)
            r0[r] += coeff
            r1[r] += coeff * q
            r2[r] += coeff * (q * (q - 1) // 2)
    return {"r0": r0, "r1": r1, "r2": r2}


def _mul_mod_u3(p: tuple[int, int, int], q: tuple[int, int, int]) -> tuple[int, int, int]:
    return (
        p[0] * q[0],
        p[0] * q[1] + p[1] * q[0],
        p[0] * q[2] + p[1] * q[1] + p[2] * q[0],
    )


def _binom2(n: int) -> int:
    return n * (n - 1) // 2


def _second_moment_coeffs(lengths: tuple[int, int, int], holes: tuple[tuple[int, int], ...], cells: list[dict]) -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    c0_rows, c1_rows, c2_rows = [], [], []
    for cell in cells:
        c0, c1, c2 = [0] * 8, [0] * 8, [0] * 8
        for power, value, slope in shell_terms(lengths, (cell["arm"], cell["first"]), holes):
            q, r = divmod(power, 8)
            c0[r] += value * _binom2(q)
            c1[r] += value * (q * slope + _binom2(slope))
            c2[r] += value * (slope * slope)
        c0_rows.append(c0)
        c1_rows.append(c1)
        c2_rows.append(c2)
    return c0_rows, c1_rows, c2_rows


def _triple_witness_arrays(t: int) -> tuple[int, tuple[int, ...], list[int], list[int]]:
    t0 = ((t - 1) % 4) + 1
    k = (t - t0) // 4
    counts, y0, y1, y2, z0, z1, z2, z3 = TRIPLE_ROOT_WITNESS_BRANCHES[t0]
    k2 = k * k
    k3 = k2 * k
    moments = [a + k * b + k2 * c for a, b, c in zip(y0, y1, y2)]
    second_moments = [a + k * b + k2 * c + k3 * d for a, b, c, d in zip(z0, z1, z2, z3)]
    return t0, counts, moments, second_moments


def check_triple_witness_t(t: int) -> dict:
    """Test Pippin's (z^8-1)^3 witness at t >= 1 against both mod (z^8-1)^3 and E_hi window bounds."""
    if type(t) is not int or t < 1:
        raise ValueError("t must be a positive integer")
    lengths = tuple(n + 7560 * t for n in (227, 67, 11))
    holes = ((1, 1), (2, 1))
    system = compressed_system(lengths, holes, 8)
    t0, counts, moments, second_moments = _triple_witness_arrays(t)
    m_res = verify_moments(system, counts, moments)
    c0_rows, c1_rows, c2_rows = _second_moment_coeffs(lengths, holes, system["cells"])
    z_res = [
        sum(counts[j] * c0_rows[j][r] + moments[j] * c1_rows[j][r] + second_moments[j] * c2_rows[j][r]
            for j in range(len(system["cells"])))
        for r in range(8)
    ]
    triple_ok = m_res["first_moment_equations_hold"] and not any(z_res)

    q_l = 945 * t
    qa, qb, qc = 28 + q_l, 8 + q_l, 1 + q_l
    arm_series: dict[int, list[tuple[int, int, int]]] = {
        1: [(0, 0, 0)] * 8,
        2: [(0, 0, 0)] * 8,
        3: [(0, 0, 0)] * 8,
    }
    for cell, x, y, z in zip(system["cells"], counts, moments, second_moments):
        arm = cell["arm"]
        if arm == 0:
            continue
        r = cell["residue"]
        q0 = cell["first"] // 8
        arm_series[arm][r] = (x, y, z) if q0 == 0 else (x, x + y, y + z)

    m1 = (2, qb + qc, _binom2(qb) + _binom2(qc))
    m2 = (2, qa + qc, _binom2(qa) + _binom2(qc))
    m3 = (2, qa + qb, _binom2(qa) + _binom2(qb))
    inv_shift = (1, -q_l, q_l * (q_l + 1) // 2)
    r0_out, r1_out, r2_out = [0] * 8, [0] * 8, [0] * 8
    for r in range(8):
        t1 = _mul_mod_u3(m1, arm_series[1][r])
        t2 = _mul_mod_u3(m2, arm_series[2][r])
        t3 = _mul_mod_u3(m3, arm_series[3][r])
        p_vec = (-(t1[0] + t2[0] + t3[0]), -(t1[1] + t2[1] + t3[1]), -(t1[2] + t2[2] + t3[2]))
        rv = _mul_mod_u3(inv_shift, p_vec)
        # z^(r+3) = z^out_r (1+u)^carry, not just z^out_r.
        carry, out_r = divmod(r + 3, 8)
        rv = _mul_mod_u3(rv, (1, carry, 0))
        r0_out[out_r], r1_out[out_r], r2_out[out_r] = rv

    bounds = e_hi_window_bounds()
    bounds_ok = all(
        abs(r0_out[r]) <= bounds["max_r0"][r]
        and abs(r1_out[r]) <= bounds["max_r1"][r]
        and abs(r2_out[r]) <= bounds["max_r2"][r]
        for r in range(8)
    )
    return {
        "t": t,
        "branch_base_t": t0,
        "triple_root_equations_hold": triple_ok,
        "e_hi_window_bounds_hold": bounds_ok,
        "r0": r0_out,
        "r1": r1_out,
        "r2": r2_out,
        "max_r0_bound": bounds["max_r0"],
        "max_r1_bound": bounds["max_r1"],
        "max_r2_bound": bounds["max_r2"],
    }


def refute_pippin_triple_witness_all_t() -> dict:
    """Certify that TRIPLE_ROOT_WITNESS_BRANCHES violates |R_{1,r}| bounds for every t >= 1."""
    bounds = e_hi_window_bounds()["max_r1"]
    branches = {}
    for t0 in (1, 2, 3, 4):
        c0 = check_triple_witness_t(t0)["r1"]
        c1 = check_triple_witness_t(t0 + 4)["r1"]
        c2 = check_triple_witness_t(t0 + 8)["r1"]
        deltas2 = [c2[r] - 2 * c1[r] + c0[r] for r in range(8)]
        linear_in_k = not any(deltas2)
        violated = []
        for r in range(8):
            slope = c1[r] - c0[r]
            if (c0[r] > bounds[r] and slope >= 0) or (c0[r] < -bounds[r] and slope <= 0):
                violated.append({
                    "residue": r,
                    "r1_at_k0": c0[r],
                    "slope": slope,
                    "delta2": deltas2[r],
                    "bound": bounds[r],
                })
        branches[t0] = {
            "linear_in_k": linear_in_k,
            "monotone_violated_residues": violated,
        }
    all_refuted = all(b["linear_in_k"] and len(b["monotone_violated_residues"]) > 0 for b in branches.values())
    return {"all_t_ge_1_refuted": all_refuted, "branches": branches}


def phi3_center_constraint(s3: list[int]) -> int:
    """Exact mod-3 centre sign sum_{k=1}^c chi_3(k) * s_3(k) forced by Im(E(omega)) = 0."""
    total = 0
    for k, val in enumerate(s3, 1):
        rem = k % 3
        if rem == 1:
            total += val
        elif rem == 0:
            total -= val
    return total


def phi3_imag_residual(
    lengths: tuple[int, int, int],
    s0: int,
    s1: list[int],
    s2: list[int],
    s3: list[int],
) -> int:
    """Coefficient of z in E(z) mod (z^2 + z + 1), proportional to Im(E(omega))."""
    poly = exact_e_polynomial(lengths, s0, s1, s2, s3)
    rem = [0, 0, 0]
    for deg, coeff in poly.items():
        rem[deg % 3] += coeff
    # Modulo z^2 + z + 1 = 0, r0 + r1*z + r2*z^2 == (r0 - r2) + (r1 - r2)*z.
    return rem[1] - rem[2]


def z0_enclosure() -> tuple[Fraction, Fraction]:
    """Certified rational interval bracketing the unique real root of z^3 + z - 1 = 0."""
    z_lo = Fraction(682327803828, 10**12)
    z_hi = Fraction(682327803829, 10**12)
    return z_lo, z_hi


def e_at_z_split(
    lengths: tuple[int, int, int],
    s0: int,
    s1: list[int],
    s2: list[int],
    s3: list[int],
    z: Fraction,
) -> Fraction:
    """Exact algebraic split of E(z) at nonzero z isolating (z + z^-1 - z^-2) multipliers."""
    a, b, c = lengths
    k1 = z + Fraction(1) / z - Fraction(1) / (z * z)
    s1_z = sum(Fraction(v) * (z ** k) for k, v in enumerate(s1, 2))
    s2_z = sum(Fraction(v) * (z ** k) for k, v in enumerate(s2, 2))
    s3_z = sum(Fraction(v) * (z ** k) for k, v in enumerate(s3, 1))
    s1_rev = sum(Fraction(v) * (z ** (a - k)) for k, v in enumerate(s1, 2))
    s2_rev = sum(Fraction(v) * (z ** (b - k)) for k, v in enumerate(s2, 2))
    s3_rev = sum(Fraction(v) * (z ** (c - k)) for k, v in enumerate(s3, 1))
    return (
        Fraction(s0) * (2 * z - 1 - z**a - z**b - z**c)
        + s1_z * (k1 - z**b - z**c) - s1_rev
        + s2_z * (k1 - z**a - z**c) - s2_rev
        + s3_z * (2 * z - 1 - z**a - z**b) - s3_rev
    )


def z0_tail_upper_bound(t: int) -> Fraction:
    """Rigorous rational upper bound on |(2 z_0 - 1)(s_0 + S_3(z_0)) - z_0^c S_3(1/z_0)|."""
    if type(t) is not int or t < 1:
        raise ValueError("t must be a positive integer")
    _, z_hi = z0_enclosure()
    a, b, c = (n + 7560 * t for n in (227, 67, 11))
    inv_one_minus_z = Fraction(1) / (1 - z_hi)
    # Remainder from tip-antisymmetry cancellation (r >= b - c = 56) plus suppressed z_0^{a,b,c} terms.
    return (
        2 * (z_hi ** (b - c)) * inv_one_minus_z
        + (z_hi**a + z_hi**b + z_hi**c)
        + (z_hi**2 * inv_one_minus_z) * (z_hi**b + z_hi**c + z_hi**a + z_hi**c)
        + (z_hi * inv_one_minus_z) * (z_hi**a + z_hi**b)
    )


def unsynchronized_divisor_obstruction(period: int) -> dict:
    """Certify the parity obstruction for fixed-prefix holes and B | 7560.

    All holes must have depths independent of t and lie in the finite prefixes.
    Moving suffix holes are excluded: they change the reduced Q^2 coefficient.
    The common-period blocks each contain B signs, including when the three
    primitive periods differ. See Theorem 3 for the expansion and quantifiers.
    """
    if type(period) is not int or period < 1 or 7560 % period != 0:
        raise ValueError("period must be a positive divisor of 7560")
    g = 1
    tmp = period
    while tmp % 2 == 0 and g < 8:
        g *= 2
        tmp //= 2
    odd_block_length = period // g
    return {
        "period": period,
        "hole_scope": "fixed_prefix_only",
        "moving_suffix_holes_covered": False,
        "aligned_modulus_g": g,
        "odd_block_length": odd_block_length,
        "sum_parity_mod_2": (3 * odd_block_length) % 2,
        "obstructed": odd_block_length % 2 == 1,
    }


def periodic_template_q_rank(period: int, d1: int, d2: int, d3: int) -> dict:
    """Compute rank modulo a prime for fixed holes (1,1),(2,1) and given cuts.

    Full column rank certifies full rank over Q; a deficient modular rank is
    only a lower bound on rational rank. No other cuts or holes are tested.
    """
    a0, b0, c0 = 227, 67, 11
    if not (1 <= d1 <= a0 and 1 <= d2 <= b0 and 0 <= d3 <= c0 and period >= 1):
        raise ValueError("invalid periodic cut depths or period")
    vars_list: list[tuple[str, int]] = [("s0", 0)]
    for arm, d_cut, L0, start_k in ((1, d1, a0, 2), (2, d2, b0, 2), (3, d3, c0, 1)):
        for k in range(start_k, d_cut + 1):
            vars_list.append((f"P{arm}", k))
        for k in range(period):
            vars_list.append((f"B{arm}", k))
        for k in range(d_cut + 1, L0 + 1):
            vars_list.append((f"T{arm}", k))
    vidx = {v: i for i, v in enumerate(vars_list)}
    nv = len(vars_list)
    eqs: dict[tuple[int, int], dict[int, int]] = {}

    def add_poly(q_pow: int, poly: dict[int, int], var_i: int) -> None:
        for deg, coeff in poly.items():
            if coeff:
                row = eqs.setdefault((q_pow, deg), {})
                val = row.get(var_i, 0) + coeff
                if val:
                    row[var_i] = val
                elif var_i in row:
                    del row[var_i]

    def mul_zb_m1(p: dict[int, int]) -> dict[int, int]:
        out = {d: -c for d, c in p.items()}
        for d, c in p.items():
            _add_term(out, d + period, c)
        return out

    def mul_k(p: dict[int, int], kpoly: dict[int, int]) -> dict[int, int]:
        out: dict[int, int] = {}
        for d1_, c1 in p.items():
            for d2_, c2 in kpoly.items():
                _add_term(out, d1_ + d2_, c1 * c2)
        return out

    def add_p(p: dict[int, int], q: dict[int, int], sign: int = 1) -> dict[int, int]:
        out = dict(p)
        for d, c in q.items():
            _add_term(out, d, sign * c)
        return out

    add_poly(0, mul_zb_m1({0: -1, 1: 2}), vidx[("s0", 0)])
    add_poly(1, mul_zb_m1({a0: -1, b0: -1, c0: -1}), vidx[("s0", 0)])
    k1 = {1: 1, -1: 1, -2: -1}
    k3 = {1: 2, 0: -1}
    for arm, d_cut, L0, other_sum, start_k in (
        (1, d1, a0, {b0: 1, c0: 1}, 2),
        (2, d2, b0, {a0: 1, c0: 1}, 2),
        (3, d3, c0, {a0: 1, b0: 1}, 1),
    ):
        k_poly = k3 if arm == 3 else k1
        for kind, rng in (("P", range(start_k, d_cut + 1)), ("B", range(period)), ("T", range(d_cut + 1, L0 + 1))):
            for k in rng:
                vi = vidx[(f"{kind}{arm}", k)]
                v_p: dict[int, int] = {}
                u_p: dict[int, int] = {}
                w_p: dict[int, int] = {}
                r_p: dict[int, int] = {}
                if kind == "P":
                    v_p, r_p = mul_zb_m1({k: 1}), mul_zb_m1({L0 - k: 1})
                elif kind == "B":
                    v_p, u_p = {d_cut + 1 + k: -1}, {d_cut + 1 + k: 1}
                    w_p, r_p = {L0 + period - d_cut - 1 - k: -1}, {L0 + period - d_cut - 1 - k: 1}
                else:
                    u_p, w_p = mul_zb_m1({k: 1}), mul_zb_m1({L0 - k: 1})
                add_poly(0, add_p(mul_k(v_p, k_poly), w_p, -1), vi)
                add_poly(1, add_p(add_p(mul_k(u_p, k_poly), mul_k(v_p, other_sum), -1), r_p, -1), vi)
                add_poly(2, mul_k(u_p, other_sum), vi)

    pivs: dict[int, list[int]] = {}
    for key in sorted(eqs):
        row = [0] * nv
        for c, val in eqs[key].items():
            row[c] = val % _PRIME_CERT
        if not any(row):
            continue
        for c in range(nv):
            if row[c]:
                if c in pivs:
                    prow = pivs[c]
                    f = row[c]
                    row = [(row[j] - f * prow[j]) % _PRIME_CERT for j in range(nv)]
                else:
                    inv = pow(row[c], _PRIME_CERT - 2, _PRIME_CERT)
                    pivs[c] = [(x * inv) % _PRIME_CERT for x in row]
                    break
    rank = len(pivs)
    return {
        "period": period,
        "holes": [[1, 1], [2, 1]],
        "cuts": [d1, d2, d3],
        "variables": nv,
        "equations": len(eqs),
        "rank": rank,
        "nullity": nv - rank,
        "trivial_over_Q": rank == nv,
        "prime_certificate": _PRIME_CERT,
        "rank_field": f"F_{_PRIME_CERT}",
    }


def positive_control_5_4_2(k: int) -> tuple[tuple[int, int, int], list[tuple[int, int]], list[tuple[int, int]]]:
    """Infinite exact positive control on H=[(1,1),(2,1)] outside 3 mod 4: T(5+4k, 4, 2)."""
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    return _positive_control_family(5 + 4 * k, 4, 2)


def positive_control_9_5_3(k: int) -> tuple[tuple[int, int, int], list[tuple[int, int]], list[tuple[int, int]]]:
    """Infinite exact positive control on H=[(1,1),(2,1)] outside 3 mod 4: T(9+4k, 5, 3)."""
    if type(k) is not int or k < 0:
        raise ValueError("k must be a nonnegative integer")
    return _positive_control_family(9 + 4 * k, 5, 3)


def _positive_control_family(
    a: int,
    b: int,
    c: int,
) -> tuple[tuple[int, int, int], list[tuple[int, int]], list[tuple[int, int]]]:
    left = [(2, d) for d in range(2, b + 1)] + [(1, j) for j in range(2, a + 1) if (j - 2) % 4 in (0, 1)]
    right = [(0, 0)] + [(3, d) for d in range(1, c + 1)] + [(1, j) for j in range(2, a + 1) if (j - 2) % 4 in (2, 3)]
    return (a, b, c), left, right


def pair_to_signs(
    lengths: tuple[int, int, int],
    left: list[tuple[int, int]],
    right: list[tuple[int, int]],
) -> tuple[int, list[int], list[int], list[int]]:
    """Convert an H=[(1,1),(2,1)] vertex pair into (s0, s1, s2, s3) sign arrays."""
    a, b, c = lengths
    left_set = {tuple(v) for v in left}
    right_set = {tuple(v) for v in right}
    if left_set & right_set:
        raise ValueError("left and right sets must be disjoint")
    s0 = 1 if (0, 0) in left_set else (-1 if (0, 0) in right_set else 0)
    s1 = [1 if (1, d) in left_set else (-1 if (1, d) in right_set else 0) for d in range(2, a + 1)]
    s2 = [1 if (2, d) in left_set else (-1 if (2, d) in right_set else 0) for d in range(2, b + 1)]
    s3 = [1 if (3, d) in left_set else (-1 if (3, d) in right_set else 0) for d in range(1, c + 1)]
    if s0 not in (-1, 1) or any(v not in (-1, 1) for v in s1 + s2 + s3):
        raise ValueError("pair must cover every retained vertex with holes (1,1),(2,1)")
    return s0, s1, s2, s3


def verify_sign_witness(payload: dict) -> dict:
    """Verify a saved exact sign witness on H=[(1,1),(2,1)] by rebuilding E(z) and check_pair."""
    lengths = tuple(payload["lengths"])
    s0 = payload["s0"]
    s1, s2, s3 = payload["s1"], payload["s2"], payload["s3"]
    if s0 not in (-1, 1) or any(v not in (-1, 1) for v in s1 + s2 + s3):
        return {"valid": False, "lengths": list(lengths), "reason": "signs must be in {-1, +1}"}
    poly = exact_e_polynomial(lengths, s0, s1, s2, s3)
    left = [(0, 0)] if s0 == 1 else []
    right = [(0, 0)] if s0 == -1 else []
    for arm, seq, start in ((1, s1, 2), (2, s2, 2), (3, s3, 1)):
        for d, val in enumerate(seq, start):
            (left if val == 1 else right).append((arm, d))
    if len(left) != len(right):
        return {
            "valid": False,
            "lengths": list(lengths),
            "e_poly_zero": poly == {},
            "homometric": False,
            "meets_target": False,
            "reason": "sets have unequal sizes",
        }
    chk = check_pair(lengths, left, right)
    valid = poly == {} and chk["homometric"] and chk["meets_target"]
    return {
        "valid": valid,
        "lengths": list(lengths),
        "e_poly_zero": poly == {},
        "homometric": chk["homometric"],
        "meets_target": chk["meets_target"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exact lifting criteria and obstructions on H=[(1,1),(2,1)].")
    parser.add_argument("--check-triple-witness", action="store_true", help="evaluate TRIPLE_ROOT_WITNESS_BRANCHES against E_hi bounds")
    parser.add_argument("--t", type=int, default=1, help="frontier parameter t")
    parser.add_argument("--refute-all-t", action="store_true", help="certify E_hi refutation of triple-root witnesses for all t >= 1")
    parser.add_argument("--periodic-obstruction", type=int, help="check periodic insertion obstruction for period B")
    parser.add_argument("--positive-control", type=int, help="emit exact positive-control witness T(9+4k, 5, 3)")
    parser.add_argument("--verify", type=Path, help="verify a saved exact sign witness JSON")
    args = parser.parse_args(argv)
    try:
        if args.verify:
            saved = json.loads(args.verify.read_text())
            res = verify_sign_witness(saved)
            print(json.dumps(res, sort_keys=True))
            return 0 if res["valid"] else 1
        if args.check_triple_witness:
            print(json.dumps(check_triple_witness_t(args.t), sort_keys=True))
            return 0
        if args.refute_all_t:
            print(json.dumps(refute_pippin_triple_witness_all_t(), sort_keys=True))
            return 0
        if args.periodic_obstruction is not None:
            b = args.periodic_obstruction
            if 7560 % b == 0:
                print(json.dumps(unsynchronized_divisor_obstruction(b), sort_keys=True))
            else:
                print(json.dumps(periodic_template_q_rank(b, 2, 2, 1), sort_keys=True))
            return 0
        if args.positive_control is not None:
            lengths, left, right = positive_control_9_5_3(args.positive_control)
            s0, s1, s2, s3 = pair_to_signs(lengths, left, right)
            print(json.dumps({"lengths": list(lengths), "s0": s0, "s1": s1, "s2": s2, "s3": s3}, sort_keys=True))
            return 0
        summary = {
            "e_hi_window_bounds": e_hi_window_bounds(),
            "refutation_all_t_ge_1": refute_pippin_triple_witness_all_t()["all_t_ge_1_refuted"],
            "z0_bound_t1_lt_3_2e_minus_9": z0_tail_upper_bound(1) < Fraction(32, 10**10),
            "b16_q_rank_2_2_1": periodic_template_q_rank(16, 2, 2, 1),
        }
        print(json.dumps(summary, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
