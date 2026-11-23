#!/usr/bin/env python3
"""Moving-hole affine obstructions at t=1 mod 2660 and a 3-parameter transfer.

Extends RESIDUE_2660.md and INTERIOR_TRANSFER.md in two directions:

1. Moving interior holes and omitted centre on T(99t, 79t, 23t), t = 2660k + 1.
   Generalizes the two-variable identity R(z, w), w = z^(delta*k), to:
   - tail moving holes ('T', arm, pos) at depth m_0 + e_arm * delta * k,
   - centre omission (sigma = 0), correcting for the missing unsigned centre,
   - split-block moving holes P + B1^(r1*k) + M + B2^((e-r1)*k) + T
     (including depth (1, 20t - 1), scaling the t=1 (1, 19) split).
   Hensel level 1 (mod 4) obstructs every tested configuration across all
   24 divisors delta | 2660. This excludes affine word certificates with
   these moving holes; arbitrary non-affine colourings at t > 1 stay open.

2. Three-parameter even-order interior-hole transfer family.
   For all integers k, r, h >= 1, T((2k+1)r - 1, (k+1)r + h, kr + h) has an
   explicit O(1) homometric pair of exact target size (2k+1)r + h - 1
   omitting two interior vertices (2, (k+1)r) and (3, kr). Proven by an
   exact three-variable identity in (z, R=z^r, K=z^(kr)); ratio_51_33_10
   already admits these tree lengths via tip deletions, so this supplies an
   independent closed-form interior-hole witness rather than new tree lengths.

Standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from published_cases import check_pair as pc_check_pair
import residue_2660 as r2660

BASE = r2660.BASE
PERIOD = r2660.PERIOD
SPLIT = r2660.SPLIT
DIVISORS_2660 = tuple(d for d in range(1, PERIOD + 1) if PERIOD % d == 0)


def _hole_J_numerator_and_monomials(delta, repeats, bases, prefixes, tails,
                                    blocks, numerators, ends, D, sigma, hole):
    """Return corr contribution J for one non-centre hole."""
    arm, kind, pos = hole
    others_N = r2660._add(*(numerators[j] for j in range(3) if j != arm))
    if kind == "tip":
        neg_dNstar = {(z + delta, w): -c
                      for (z, w), c in r2660._star(numerators[arm]).items()}
        return r2660._mul(ends[arm], r2660._add(
            neg_dNstar, others_N, r2660._scale(D, sigma)))
    if kind == "P":
        m = pos + 1
        low = r2660._word(prefixes[arm][:m])
        J = r2660._add(
            r2660._mul(r2660._monomial(m), r2660._add(r2660._scale(D, -1), others_N)),
            r2660._mul(r2660._mul(r2660._monomial(m), D), r2660._star(low)),
            r2660._mul(r2660._monomial(-m),
                       r2660._add(numerators[arm], r2660._scale(r2660._mul(D, low), -1))),
        )
        if sigma != -1:
            J = r2660._add(J, r2660._scale(r2660._mul(r2660._monomial(m), D), sigma + 1))
        return J
    if kind == "T":
        plen = len(prefixes[arm])
        dz = plen + 1 + pos
        dw = repeats[arm]
        mon_m = r2660._monomial(dz, dw)
        mon_neg_m = r2660._monomial(-dz, -dw)
        bterm = r2660._word(blocks[arm], plen + 1)
        bpart = r2660._add(bterm, r2660._scale(r2660._shift(bterm, 0, repeats[arm]), -1))
        tlow = r2660._word(tails[arm][:pos], plen + 1)
        low_N = r2660._add(
            r2660._mul(D, r2660._word(prefixes[arm])),
            bpart,
            r2660._mul(r2660._mul(D, r2660._monomial(0, repeats[arm])), tlow),
        )
        high_N = r2660._add(numerators[arm], r2660._scale(low_N, -1))
        d_Slow_star = {(z + delta, w): -c for (z, w), c in r2660._star(low_N).items()}
        J = r2660._add(
            r2660._mul(mon_m, r2660._add(r2660._scale(D, -1), others_N)),
            r2660._mul(mon_m, d_Slow_star),
            r2660._mul(mon_neg_m, high_N),
        )
        if sigma != -1:
            J = r2660._add(J, r2660._scale(r2660._mul(mon_m, D), sigma + 1))
        return J
    raise ValueError(f"unknown hole kind {kind!r}")


def make_moving_identity(delta, repeats, bases, prefixes, tails, blocks, holes, sigma=-1):
    """Exact R(z, w) supporting P-holes, T-tail moving holes, tips, and sigma=0."""
    one = r2660._monomial()
    D = r2660._add(one, r2660._scale(r2660._monomial(delta), -1))
    numerators = []
    for i in range(3):
        offset = len(prefixes[i]) + 1
        bterm = r2660._word(blocks[i], offset)
        bpart = r2660._add(bterm, r2660._scale(r2660._shift(bterm, 0, repeats[i]), -1))
        numerators.append(r2660._add(
            r2660._mul(D, r2660._word(prefixes[i])),
            bpart,
            r2660._mul(r2660._mul(D, r2660._monomial(0, repeats[i])),
                       r2660._word(tails[i], offset)),
        ))
    ends = [r2660._monomial(bases[i], repeats[i]) for i in range(3)]
    shell = r2660._scale(
        r2660._mul(D, r2660._add(one, r2660._scale(r2660._add(*ends), -1))), sigma)
    for i, numerator in enumerate(numerators):
        others = r2660._add(*(ends[j] for j in range(3) if j != i))
        shell = r2660._add(
            shell,
            r2660._mul(numerator, r2660._add(one, r2660._scale(others, -1))),
            r2660._mul(r2660._mul(r2660._monomial(delta), ends[i]), r2660._star(numerator)),
        )
    corr = r2660._add(*numerators) if sigma == 0 else {}
    for hole in holes:
        if hole == "centre":
            continue
        J = _hole_J_numerator_and_monomials(
            delta, repeats, bases, prefixes, tails, blocks, numerators, ends, D, sigma, hole)
        corr = r2660._add(corr, J)
    one_minus_z = r2660._add(one, r2660._scale(r2660._monomial(1), -1))
    return r2660._add(
        r2660._mul(r2660._monomial(1), shell),
        r2660._scale(r2660._mul(one_minus_z, corr), -1),
    )


def make_split_identity(delta, repeats, bases, prefixes, tails, blocks,
                        split_arm, r1, M_word, B2_word, hole_in_M, other_hole, sigma=-1):
    """Exact R(z, w) with split_arm = P + B1^(r1*k) + M + B2^((e-r1)*k) + T."""
    one = r2660._monomial()
    D = r2660._add(one, r2660._scale(r2660._monomial(delta), -1))
    one_minus_z = r2660._add(one, r2660._scale(r2660._monomial(1), -1))
    ends = [r2660._monomial(bases[i], repeats[i]) for i in range(3)]
    numerators = []
    low_N_split = None
    m_dz = m_dw = None
    for i in range(3):
        if i != split_arm:
            offset = len(prefixes[i]) + 1
            bterm = r2660._word(blocks[i], offset)
            bpart = r2660._add(bterm, r2660._scale(r2660._shift(bterm, 0, repeats[i]), -1))
            numerators.append(r2660._add(
                r2660._mul(D, r2660._word(prefixes[i])),
                bpart,
                r2660._mul(r2660._mul(D, r2660._monomial(0, repeats[i])),
                           r2660._word(tails[i], offset)),
            ))
        else:
            p, t = prefixes[i], tails[i]
            off1 = len(p) + 1
            off2 = len(p) + len(M_word) + 1
            b1t = r2660._word(blocks[i], off1)
            b1p = r2660._add(b1t, r2660._scale(r2660._shift(b1t, 0, r1), -1))
            mw = r2660._mul(r2660._mul(D, r2660._monomial(0, r1)), r2660._word(M_word, off1))
            b2t = r2660._word(B2_word, off2)
            b2p = r2660._add(r2660._shift(b2t, 0, r1),
                             r2660._scale(r2660._shift(b2t, 0, repeats[i]), -1))
            tw = r2660._mul(r2660._mul(D, r2660._monomial(0, repeats[i])),
                            r2660._word(t, off2))
            numerators.append(r2660._add(r2660._mul(D, r2660._word(p)), b1p, mw, b2p, tw))
            m_dz = off1 + hole_in_M
            m_dw = r1
            mlow = r2660._mul(r2660._mul(D, r2660._monomial(0, r1)),
                              r2660._word(M_word[:hole_in_M], off1))
            low_N_split = r2660._add(r2660._mul(D, r2660._word(p)), b1p, mlow)

    shell = r2660._scale(
        r2660._mul(D, r2660._add(one, r2660._scale(r2660._add(*ends), -1))), sigma)
    for i, numerator in enumerate(numerators):
        others = r2660._add(*(ends[j] for j in range(3) if j != i))
        shell = r2660._add(
            shell,
            r2660._mul(numerator, r2660._add(one, r2660._scale(others, -1))),
            r2660._mul(r2660._mul(r2660._monomial(delta), ends[i]), r2660._star(numerator)),
        )
    corr = r2660._add(*numerators) if sigma == 0 else {}

    others_N = r2660._add(*(numerators[j] for j in range(3) if j != split_arm))
    mon_m = r2660._monomial(m_dz, m_dw)
    mon_neg_m = r2660._monomial(-m_dz, -m_dw)
    high_N = r2660._add(numerators[split_arm], r2660._scale(low_N_split, -1))
    d_Slow_star = {(z + delta, w): -c for (z, w), c in r2660._star(low_N_split).items()}
    J_split = r2660._add(
        r2660._mul(mon_m, r2660._add(r2660._scale(D, -1), others_N)),
        r2660._mul(mon_m, d_Slow_star),
        r2660._mul(mon_neg_m, high_N),
    )
    if sigma != -1:
        J_split = r2660._add(J_split, r2660._scale(r2660._mul(mon_m, D), sigma + 1))
    corr = r2660._add(corr, J_split)

    if other_hole != "centre":
        J_o = _hole_J_numerator_and_monomials(
            delta, repeats, bases, prefixes, tails, blocks,
            numerators, ends, D, sigma, other_hole)
        corr = r2660._add(corr, J_o)

    return r2660._add(
        r2660._mul(r2660._monomial(1), shell),
        r2660._scale(r2660._mul(one_minus_z, corr), -1),
    )


def _gf2_hensel1_from_rows(rows):
    """Return True if GF(2) system is consistent, False if obstructed."""
    basis = {}
    for m, v in rows:
        while m:
            piv = (m & -m).bit_length() - 1
            if piv not in basis:
                basis[piv] = (m, v)
                break
            bm, bv = basis[piv]
            m ^= bm
            v ^= bv
        else:
            if v:
                return False
    return True


class MovingHoleAuditor:
    """Precomputed linear decomposition for fast Hensel level-1 hole audits."""

    def __init__(self, delta: int, splits: tuple[int, int, int] = SPLIT):
        self.delta = delta
        self.bases = BASE
        self.repeats = tuple(PERIOD * b // delta for b in BASE)
        self.plen = list(splits)
        self.tlen = [BASE[i] - self.plen[i] for i in range(3)]
        one = r2660._monomial()
        self.D = r2660._add(one, r2660._scale(r2660._monomial(delta), -1))
        one_minus_z = r2660._add(one, r2660._scale(r2660._monomial(1), -1))
        self.neg_omz = r2660._scale(one_minus_z, -1)
        ends = [r2660._monomial(BASE[i], self.repeats[i]) for i in range(3)]

        self.varspec = []
        for i in range(3):
            for pos in range(self.plen[i]):
                self.varspec.append(("P", i, pos))
            for pos in range(self.tlen[i]):
                self.varspec.append(("T", i, pos))
        for i in range(3):
            for pos in range(delta):
                self.varspec.append(("B", i, pos))
        self.vindex = {v: idx for idx, v in enumerate(self.varspec)}

        self.N_var = []
        self.shell_var = []
        for kind, arm, pos in self.varspec:
            offset = self.plen[arm] + 1
            if kind == "P":
                N = r2660._mul(self.D, {(pos + 1, 0): 1})
            elif kind == "T":
                N = r2660._mul(self.D, {(offset + pos, self.repeats[arm]): 1})
            else:
                bt = {(offset + pos, 0): 1}
                N = r2660._add(bt, r2660._scale(r2660._shift(bt, 0, self.repeats[arm]), -1))
            self.N_var.append(N)
            others = r2660._add(*(ends[j] for j in range(3) if j != arm))
            sh = r2660._add(
                r2660._mul(N, r2660._add(one, r2660._scale(others, -1))),
                r2660._mul(r2660._mul(r2660._monomial(delta), ends[arm]), r2660._star(N)),
            )
            self.shell_var.append(r2660._mul(r2660._monomial(1), sh))

        self.shell_unit = r2660._mul(
            r2660._monomial(1),
            r2660._mul(self.D, r2660._add(one, r2660._scale(r2660._add(*ends), -1))),
        )
        self.base_sum = Counter()
        self.base_mask = {}
        for vi, p in enumerate(self.shell_var):
            bit = 1 << vi
            for mon, c in p.items():
                self.base_sum[mon] += c
                if c & 1:
                    self.base_mask[mon] = self.base_mask.get(mon, 0) ^ bit

        self.centre_sum = Counter(self.base_sum)
        self.centre_mask = dict(self.base_mask)
        self.centre_vars = []
        for vi in range(len(self.varspec)):
            cv = r2660._mul(self.neg_omz, self.N_var[vi])
            self.centre_vars.append(cv)
            bit = 1 << vi
            for mon, c in cv.items():
                self.centre_sum[mon] += c
                if c & 1:
                    self.centre_mask[mon] = self.centre_mask.get(mon, 0) ^ bit
        self._hole_cache = {}

    def hole_summary(self, hole):
        if hole in self._hole_cache:
            return self._hole_cache[hole]
        arm, kind, pos = hole
        if kind == "tip":
            hole = (arm, "T", self.tlen[arm] - 1)
            arm, kind, pos = hole
        if kind == "P":
            killed = ("P", arm, pos)
            m = pos + 1
            mon_m = r2660._monomial(m)
            mon_neg_m = r2660._monomial(-m)
            j_sig = r2660._mul(self.neg_omz, r2660._mul(mon_m, self.D))
            jv = {}
            for vi, (vk, va, vp) in enumerate(self.varspec):
                if (vk, va, vp) == killed:
                    continue
                if va != arm:
                    p = r2660._mul(mon_m, self.N_var[vi])
                elif vk == "P" and vp < pos:
                    p = r2660._mul(r2660._mul(mon_m, self.D), {(-(vp + 1), 0): 1})
                else:
                    p = r2660._mul(mon_neg_m, self.N_var[vi])
                p = r2660._mul(self.neg_omz, p)
                if p:
                    jv[vi] = p
        elif kind == "T":
            killed = ("T", arm, pos)
            dz = self.plen[arm] + 1 + pos
            dw = self.repeats[arm]
            mon_m = r2660._monomial(dz, dw)
            mon_neg_m = r2660._monomial(-dz, -dw)
            j_sig = r2660._mul(self.neg_omz, r2660._mul(mon_m, self.D))
            jv = {}
            for vi, (vk, va, vp) in enumerate(self.varspec):
                if (vk, va, vp) == killed:
                    continue
                if va != arm:
                    p = r2660._mul(mon_m, self.N_var[vi])
                elif vk == "P" or vk == "B" or (vk == "T" and vp < pos):
                    d_Sstar = {(z + self.delta, w): -c
                               for (z, w), c in r2660._star(self.N_var[vi]).items()}
                    p = r2660._mul(mon_m, d_Sstar)
                else:
                    p = r2660._mul(mon_neg_m, self.N_var[vi])
                p = r2660._mul(self.neg_omz, p)
                if p:
                    jv[vi] = p
        else:
            raise ValueError(f"unsupported hole {hole!r}")
        kvi = self.vindex[killed]
        jsum = Counter()
        jmask = {}
        for vi, p in jv.items():
            bit = 1 << vi
            for mon, c in p.items():
                jsum[mon] += c
                if c & 1:
                    jmask[mon] = jmask.get(mon, 0) ^ bit
        summary = (kvi, j_sig, jsum, jmask, jv)
        self._hole_cache[hole] = summary
        return summary

    def check_holes(self, h1, h2, sigma: int) -> tuple[str, str]:
        """Test Hensel level-1 consistency for (h1, h2) with centre sign sigma."""
        centre_mode = (h2 == "centre" or h1 == "centre")
        if centre_mode:
            assert sigma == 0
            h = h1 if h2 == "centre" else h2
            s1 = self.hole_summary(h)
            k_set = {s1[0]}
            hdata = [s1]
            b_sum, b_mask = self.centre_sum, self.centre_mask
            const_poly = {}
        else:
            assert sigma in (-1, 1)
            s1 = self.hole_summary(h1)
            s2 = self.hole_summary(h2)
            k_set = {s1[0], s2[0]}
            hdata = [s1, s2]
            b_sum, b_mask = self.base_sum, self.base_mask
            const_poly = r2660._add(
                r2660._scale(self.shell_unit, sigma),
                r2660._scale(r2660._add(s1[1], s2[1]), sigma),
            )

        d_sum = Counter()
        d_mask = {}
        for kvi in k_set:
            bit = 1 << kvi
            for mon, c in self.shell_var[kvi].items():
                d_sum[mon] -= c
                if c & 1:
                    d_mask[mon] = d_mask.get(mon, 0) ^ bit
            if centre_mode:
                for mon, c in self.centre_vars[kvi].items():
                    d_sum[mon] -= c
                    if c & 1:
                        d_mask[mon] = d_mask.get(mon, 0) ^ bit
        for kvi_self, _, jsum, jmask, jv in hdata:
            for mon, c in jsum.items():
                d_sum[mon] += c
            for mon, msk in jmask.items():
                d_mask[mon] = d_mask.get(mon, 0) ^ msk
            for kvi_other in k_set:
                if kvi_other != kvi_self and kvi_other in jv:
                    bit = 1 << kvi_other
                    for mon, c in jv[kvi_other].items():
                        d_sum[mon] -= c
                        if c & 1:
                            d_mask[mon] = d_mask.get(mon, 0) ^ bit

        rows = []
        for mon in set(b_sum) | set(d_sum) | set(const_poly):
            csum = b_sum.get(mon, 0) + d_sum.get(mon, 0)
            rhs = -const_poly.get(mon, 0)
            r = rhs - csum
            if r & 1:
                return "obstructed", "mod 2"
            y_bit = 1 if (r & 2) else 0
            msk = b_mask.get(mon, 0) ^ d_mask.get(mon, 0)
            if msk == 0:
                if y_bit:
                    return "obstructed", "mod 4 zero row"
            else:
                rows.append((msk, y_bit))
        if not _gf2_hensel1_from_rows(rows):
            return "obstructed", "Hensel level 1 (mod 4)"
        return "consistent", "passed Hensel level 1"


def split_level01_obstruction(delta: int, split_arm: int, r1: int, m_pos: int,
                              other_hole, sigma: int = -1) -> tuple[str, str]:
    """Hensel level-1 check for a split-block moving hole P + B1^(r1*k) + M + B2^(r2*k) + T."""
    repeats = tuple(PERIOD * b // delta for b in BASE)
    plen = [0, 18, 5] if (split_arm == 0 and m_pos < 20) else [18, 18, 5]
    M_len = 25 if (split_arm == 0 and m_pos < 20) else 5
    tlen = [BASE[i] - plen[i] - (M_len if i == split_arm else 0) for i in range(3)]
    varspec = []
    for i in range(3):
        for pos in range(plen[i]):
            varspec.append(("P", i, pos))
        for pos in range(tlen[i]):
            if other_hole != "centre" and other_hole == (i, "tip", None) and pos == tlen[i] - 1:
                continue
            varspec.append(("T", i, pos))
    for i in range(3):
        for pos in range(delta):
            varspec.append(("B", i, pos))
    for pos in range(M_len):
        if pos != m_pos:
            varspec.append(("M", split_arm, pos))
    for pos in range(delta):
        varspec.append(("B2", split_arm, pos))

    def mk(var=None):
        P = ["0" * plen[i] for i in range(3)]
        T = ["0" * tlen[i] for i in range(3)]
        B = ["0" * delta for _ in range(3)]
        M = "0" * M_len
        B2 = "0" * delta
        if var is not None:
            vk, va, vp = var
            if vk == "P":
                s = list(P[va]); s[vp] = "+"; P[va] = "".join(s)
            elif vk == "T":
                s = list(T[va]); s[vp] = "+"; T[va] = "".join(s)
            elif vk == "B":
                s = list(B[va]); s[vp] = "+"; B[va] = "".join(s)
            elif vk == "M":
                s = list(M); s[vp] = "+"; M = "".join(s)
            elif vk == "B2":
                s = list(B2); s[vp] = "+"; B2 = "".join(s)
        return P, T, B, M, B2

    P0, T0, B0, M0, B20 = mk()
    R0 = make_split_identity(
        delta, repeats, BASE, P0, T0, B0, split_arm, r1, M0, B20, m_pos, other_hole, sigma=sigma)
    rowmap = {}
    for vi, var in enumerate(varspec):
        P, T, B, M, B2 = mk(var)
        Cr = make_split_identity(
            delta, repeats, BASE, P, T, B, split_arm, r1, M, B2, m_pos, other_hole, sigma=sigma)
        for mon in set(Cr) | set(R0):
            c = Cr.get(mon, 0) - R0.get(mon, 0)
            if c:
                rowmap.setdefault(mon, []).append((vi, c))
    for mon, c0 in R0.items():
        if mon not in rowmap and c0 != 0:
            return "obstructed", "const"
    rows = []
    for mon, cs in rowmap.items():
        rhs = -R0.get(mon, 0)
        r = rhs - sum(c for _, c in cs)
        if r & 1:
            return "obstructed", "mod 2"
        y_bit = 1 if (r & 2) else 0
        msk = 0
        for vi, c in cs:
            if c & 1:
                msk |= (1 << vi)
        if msk == 0:
            if y_bit:
                return "obstructed", "mod 4 zero row"
        else:
            rows.append((msk, y_bit))
    if not _gf2_hensel1_from_rows(rows):
        return "obstructed", "Hensel level 1 (mod 4)"
    return "consistent", "passed"


# --------------------------------------------------------------------------
# Part 2: Three-parameter even-order interior-hole transfer family.
# --------------------------------------------------------------------------

def three_param_pair(k: int, r: int, h: int) -> dict:
    """Explicit O(1) homometric pair for T((2k+1)r - 1, (k+1)r + h, kr + h)."""
    if any(type(v) is not int or v < 1 for v in (k, r, h)):
        raise ValueError("k, r, h must be positive integers")
    n1, n2, n3 = (2 * k + 1) * r, (k + 1) * r, k * r
    w1 = "".join(("-" if idx % 2 == 0 else "+") * r for idx in range(2 * k + 1))
    left, right = [], [(0, 0)]
    for d in range(1, n1):
        (left if w1[d] == "+" else right).append((1, d))
    for d in range(1, n2):
        left.append((2, d))
    for d in range(1, n3):
        right.append((3, d))
    for j in range(1, h + 1):
        left.append((2, n2 + j))
        right.append((3, n3 + j))
    lengths = [n1 - 1, n2 + h, n3 + h]
    target = (1 + sum(lengths)) // 2 - 1
    return {
        "k": k, "r": r, "h": h,
        "lengths": lengths,
        "size": len(left),
        "target": target,
        "holes": [[2, n2], [3, n3]],
        "left": left,
        "right": right,
    }


def verify_three_param_symbolic() -> dict:
    """Verify both 3-variable identities in (z, R=z^r, K=z^(kr)) with zero search."""
    def add(*ps):
        c = {}
        for p in ps:
            for e, v in p.items():
                c[e] = c.get(e, 0) + v
        return {e: v for e, v in c.items() if v}

    def mul(a, b):
        c = {}
        for (z1, r1, k1), v1 in a.items():
            for (z2, r2, k2), v2 in b.items():
                e = (z1 + z2, r1 + r2, k1 + k2)
                c[e] = c.get(e, 0) + v1 * v2
        return {e: v for e, v in c.items() if v}

    def neg(p):
        return {e: -v for e, v in p.items()}

    one = {(0, 0, 0): 1}
    z = {(1, 0, 0): 1}
    R = {(0, 1, 0): 1}
    K = {(0, 0, 1): 1}
    RK = mul(R, K)
    RK2 = mul(R, mul(K, K))

    # Full-word Euler-cell polynomials (index 0..n_i-1) multiplied by (1-z)(1+R):
    # W1(z) = -(1-R)(1 + RK^2) / ((1-z)(1+R)), W2(z) = (1-RK)/(1-z), W3(z) = -(1-K)/(1-z).
    W1s = neg(mul(add(one, neg(R)), add(one, RK2)))
    W2s = mul(add(one, R), add(one, neg(RK)))
    W3s = mul(add(one, R), neg(add(one, neg(K))))
    cell_residual = add(
        mul(W1s, add(RK, K)),
        mul(W2s, add(RK2, K)),
        mul(W3s, add(RK2, RK)),
    )

    # Interior-vertex polynomials F_i(z) = sum_{d=1}^{n_i-1} w_i[d] z^d, scaled by (1-z)(1+R):
    # Note F1(z) = W1(z) + 1, F2(z) = W2(z) - 1, F3(z) = W3(z) + 1.
    one_mz_pR = mul(add(one, neg(z)), add(one, R))
    F1s = add(W1s, one_mz_pR)
    F2s = add(W2s, neg(one_mz_pR))
    F3s = add(W3s, one_mz_pR)

    # Rooted difference U_u - U_v = (RK - K)(z + ... + z^(n1-1)) -> scaled by (1-z)(1+R):
    Uu_minus_Uv_s = mul(add(one, R), mul(add(RK, neg(K)), add(z, neg(RK2))))
    # F_u + F_v = F2 + F3 - (RK + K) + RK*(F1 + F3) + K*(F1 + F2)
    Fu_plus_Fv_s = add(
        F2s, F3s,
        neg(mul(one_mz_pR, add(RK, K))),
        mul(RK, add(F1s, F3s)),
        mul(K, add(F1s, F2s)),
    )
    transfer_residual = add(Fu_plus_Fv_s, Uu_minus_Uv_s)
    return {
        "cell_residual": cell_residual,
        "transfer_residual": transfer_residual,
    }


def _eval_at_k(poly, delta: int, k: int) -> dict[int, int]:
    out = Counter()
    for (z, w), c in poly.items():
        out[z + w * delta * k] += c
    return {e: c for e, c in out.items() if c}


def _poly1_mul(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
    out = Counter()
    for e1, c1 in a.items():
        for e2, c2 in b.items():
            out[e1 + e2] += c1 * c2
    return {e: c for e, c in out.items() if c}


def verify_finite_identities() -> list[str]:
    """Verify moving-hole, centre-hole, and split-block identities vs brute force."""
    from itertools import combinations
    lines = []

    def prof_diff_scaled(delta_t, lengths, left, right):
        def prof(vs):
            return Counter(abs(u[1] - v[1]) if u[0] == v[0] else u[1] + v[1]
                           for u, v in combinations(vs, 2))
        lp, rp = prof(left), prof(right)
        diff = {d: 2 * (lp[d] - rp[d]) for d in set(lp) | set(rp) if lp[d] != rp[d]}
        return _poly1_mul({0: 1, 1: -1}, _poly1_mul({0: 1, delta_t: -1}, diff))

    cases = [
        ("T+tip", ["+--", "-+", ""], ["0+", "+", "0"], ["+-", "-+", "+-"],
         ((0, "T", 0), (2, "tip", None)), -1),
        ("T+centre", ["+--", "+-", "+"], ["+0", "-", ""], ["+-", "-+", "+-"],
         ((0, "T", 1), "centre"), 0),
        ("T+P", ["+--", "0+", "+"], ["+0", "-", ""], ["+-", "-+", "+-"],
         ((0, "T", 1), (1, "P", 0)), -1),
        ("P+centre", ["0+-", "+-", "+"], ["+-", "-", ""], ["+-", "-+", "+-"],
         ((0, "P", 0), "centre"), 0),
    ]
    for label, P_t, T_t, B_t, holes_t, sig in cases:
        R_poly = make_moving_identity(2, (5, 3, 1), (5, 3, 1), P_t, T_t, B_t, holes_t, sigma=sig)
        for k in (0, 1, 2):
            words = [P_t[i] + B_t[i] * ((5, 3, 1)[i] * k) + T_t[i] for i in range(3)]
            left = [(0, 0)] if sig == 1 else []
            right = [(0, 0)] if sig == -1 else []
            for arm, w in enumerate(words, 1):
                for d, ch in enumerate(w, 1):
                    if ch == "+":
                        left.append((arm, d))
                    elif ch == "-":
                        right.append((arm, d))
            assert len(left) == len(right)
            exp = prof_diff_scaled(2, (5, 3, 1), left, right)
            assert _eval_at_k(R_poly, 2, k) == exp
        lines.append(f"moving identity ({label}): exact profile match for k=0,1,2")

    # Split-block check:
    P_s, M_s, T_s = ["+-", "+-", "+"], "0+", ["0", "-", ""]
    B1_s, B2_s = ["+-", "-+", "+-"], "-+"
    R_s = make_split_identity(
        2, (5, 3, 1), (5, 3, 1), P_s, T_s, B1_s, 0, 2, M_s, B2_s, 0, (0, "tip", None), sigma=-1)
    for k in (0, 1, 2):
        w0 = P_s[0] + B1_s[0] * (2 * k) + M_s + B2_s * (3 * k) + T_s[0]
        w1 = P_s[1] + B1_s[1] * (3 * k) + T_s[1]
        w2 = P_s[2] + B1_s[2] * k + T_s[2]
        left, right = [], [(0, 0)]
        for arm, w in enumerate((w0, w1, w2), 1):
            for d, ch in enumerate(w, 1):
                if ch == "+":
                    left.append((arm, d))
                elif ch == "-":
                    right.append((arm, d))
        exp = prof_diff_scaled(2, (5, 3, 1), left, right)
        assert _eval_at_k(R_s, 2, k) == exp
    lines.append("split-block identity: exact profile match for k=0,1,2")
    return lines


def prove() -> list[str]:
    lines = verify_finite_identities()
    sym = verify_three_param_symbolic()
    assert not sym["cell_residual"] and not sym["transfer_residual"]
    lines.append("3-parameter transfer: exact 3-variable symbolic identities vanish identically")
    for k, r, h in ((1, 2, 1), (1, 3, 2), (2, 3, 4), (2, 4, 5)):
        w = three_param_pair(k, r, h)
        res = pc_check_pair(w["lengths"], w["left"], w["right"])
        assert res["homometric"] and res["meets_target"]
        lines.append(
            f"3-parameter witness (k={k},r={r},h={h}) T{tuple(w['lengths'])}: "
            f"size={res['size']} == target={res['target']}, {sum(res['left_profile'].values())} pairs/side"
        )
    return lines


def audit() -> list[str]:
    """Audit moving-hole, centre-hole, and split-block obstructions across all 24 delta | 2660."""
    lines = []
    for delta in DIVISORS_2660:
        aud = MovingHoleAuditor(delta)
        configs = [
            ((0, "T", 9), (0, "tip", None), -1),
            ((0, "T", 9), (0, "tip", None), 1),
            ((0, "T", 9), "centre", 0),
            ((0, "P", 18), "centre", 0),
            ((1, "T", 0), (0, "tip", None), -1),
            ((2, "T", 0), (0, "tip", None), -1),
            ((0, "T", 0), (1, "T", 0), -1),
        ]
        for h1, h2, sig in configs:
            verdict, _ = aud.check_holes(h1, h2, sig)
            assert verdict == "obstructed", (delta, h1, h2, sig)
        lines.append(f"delta={delta}: all {len(configs)} moving/centre configs obstructed (mod 4)")
    for oh, sig in [((0, "tip", None), -1), ((1, "tip", None), -1),
                    ((2, "tip", None), -1), ("centre", 0)]:
        verdict, _ = split_level01_obstruction(PERIOD, 0, 20, 18, oh, sigma=sig)
        assert verdict == "obstructed", (oh, sig)
    lines.append("delta=2660 split-block (1, 20t-1): all 4 tip/centre partners obstructed (mod 4)")
    return lines


def full_scan(delta: int) -> list[str]:
    """Run full 1,801-configuration anchor/moving/centre scan at a divisor delta | 2660."""
    if PERIOD % delta != 0:
        raise ValueError(f"delta={delta} must divide {PERIOD}")
    aud = MovingHoleAuditor(delta)
    candidates = ([(arm, "P", pos) for arm in range(3) for pos in range(aud.plen[arm])] +
                  [(arm, "T", pos) for arm in range(3) for pos in range(aud.tlen[arm])])
    anchors = [(arm, "T", aud.tlen[arm] - 1) for arm in range(3)] + [(0, "P", 18)]
    tested = 0
    for h in candidates:
        verdict, _ = aud.check_holes(h, "centre", 0)
        assert verdict == "obstructed", (delta, h, "centre")
        tested += 1
        for anc in anchors:
            if anc == h:
                continue
            for sig in (-1, 1):
                verdict, _ = aud.check_holes(h, anc, sig)
                assert verdict == "obstructed", (delta, h, anc, sig)
                tested += 1
    return [f"delta={delta}: all {tested} moving/centre/anchor hole configurations obstructed"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prove", action="store_true")
    group.add_argument("--audit", action="store_true")
    group.add_argument("--full-scan", type=int, metavar="DELTA")
    group.add_argument("--witness", nargs=3, type=int, metavar=("K", "R", "H"))
    group.add_argument("--check", metavar="FILE")
    parser.add_argument("--summary", action="store_true",
                        help="with --witness, omit vertex lists")
    args = parser.parse_args(argv)
    try:
        if args.prove:
            for line in prove():
                print("PASS:", line)
        elif args.audit:
            for line in audit():
                print("PASS:", line)
        elif args.full_scan is not None:
            for line in full_scan(args.full_scan):
                print("PASS:", line)
        elif args.witness is not None:
            res = three_param_pair(*args.witness)
            res["left"] = [list(v) for v in res["left"]]
            res["right"] = [list(v) for v in res["right"]]
            if args.summary:
                res = {k: v for k, v in res.items() if k not in ("left", "right")}
            print(json.dumps(res, sort_keys=True))
        else:
            text = (sys.stdin.read() if args.check == "-"
                    else open(args.check, encoding="utf-8").read())
            data = json.loads(text)
            res = pc_check_pair(data["lengths"], data.get("left", []), data.get("right", []))
            out = {k: v for k, v in res.items() if k not in ("left_profile", "right_profile")}
            print(json.dumps(out, sort_keys=True))
            return 0 if res["homometric"] else 1
    except (ValueError, ArithmeticError, KeyError, OSError) as err:
        print(f"REFUSED: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
