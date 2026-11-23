#!/usr/bin/env python3
"""Sweep split-block moving-hole slopes across all three arms at t=1 mod 2660.

Extends moving_hole_2660.py by sweeping intermediate linear hole depths
m(k) = m_0 + r1 * delta * k (0 < r1 < repeats[arm]) on all three arms,
plus testing SPLIT=(0,0,0) invariance, using a fast linear Hensel level-1
checker that precomputes the two unsplit arms once per delta.

Standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from moving_hole_2660 import _gf2_hensel1_from_rows
import residue_2660 as r2660

BASE = r2660.BASE
PERIOD = r2660.PERIOD


class SplitBlockAuditor:
    """Fast linear Hensel level-1 auditor for split-block moving holes."""

    def __init__(self, delta: int, plen: tuple[int, int, int] = (18, 18, 5), m_len: int = 5):
        self.delta = delta
        self.bases = BASE
        self.repeats = tuple(PERIOD * b // delta for b in BASE)
        self.plen = list(plen)
        self.m_len = m_len
        self.one = r2660._monomial()
        self.D = r2660._add(self.one, r2660._scale(r2660._monomial(delta), -1))
        self.omz = r2660._add(self.one, r2660._scale(r2660._monomial(1), -1))
        self.neg_omz = r2660._scale(self.omz, -1)
        self.ends = [r2660._monomial(BASE[i], self.repeats[i]) for i in range(3)]
        self.shell_unit = r2660._mul(
            r2660._monomial(1),
            r2660._mul(self.D, r2660._add(self.one, r2660._scale(r2660._add(*self.ends), -1))),
        )

    def check_split(self, split_arm: int, r1: int, m_pos: int, other_hole,
                    sigma: int = -1, plen_override=None, m_len_override=None) -> tuple[str, str]:
        """Check Hensel level-1 consistency for one split-block configuration."""
        plen = list(plen_override) if plen_override is not None else list(self.plen)
        m_len = m_len_override if m_len_override is not None else self.m_len
        if split_arm == 0 and m_pos >= m_len:
            plen[0] = 0
            m_len = m_pos + 2
        tlen = [BASE[i] - plen[i] - (m_len if i == split_arm else 0) for i in range(3)]
        if any(t < 1 for t in tlen):
            raise ValueError(f"invalid split lengths {plen}, {m_len}, {tlen}")

        varspec = []
        N_var = []
        var_arm = []
        in_low_split = []
        r2 = self.repeats[split_arm] - r1
        assert 0 < r1 < self.repeats[split_arm]

        for i in range(3):
            if i != split_arm:
                off = plen[i] + 1
                for pos in range(plen[i]):
                    varspec.append(("P", i, pos))
                    N_var.append(r2660._mul(self.D, {(pos + 1, 0): 1}))
                    var_arm.append(i)
                    in_low_split.append(False)
                for pos in range(tlen[i]):
                    if other_hole != "centre" and other_hole == (i, "tip", None) and pos == tlen[i] - 1:
                        continue
                    varspec.append(("T", i, pos))
                    N_var.append(r2660._mul(self.D, {(off + pos, self.repeats[i]): 1}))
                    var_arm.append(i)
                    in_low_split.append(False)
                for pos in range(self.delta):
                    varspec.append(("B", i, pos))
                    bt = {(off + pos, 0): 1}
                    N_var.append(r2660._add(bt, r2660._scale(r2660._shift(bt, 0, self.repeats[i]), -1)))
                    var_arm.append(i)
                    in_low_split.append(False)
            else:
                off1 = plen[i] + 1
                off2 = plen[i] + m_len + 1
                for pos in range(plen[i]):
                    varspec.append(("P", i, pos))
                    N_var.append(r2660._mul(self.D, {(pos + 1, 0): 1}))
                    var_arm.append(i)
                    in_low_split.append(True)
                for pos in range(self.delta):
                    varspec.append(("B1", i, pos))
                    bt = {(off1 + pos, 0): 1}
                    N_var.append(r2660._add(bt, r2660._scale(r2660._shift(bt, 0, r1), -1)))
                    var_arm.append(i)
                    in_low_split.append(True)
                for pos in range(m_len):
                    if pos == m_pos:
                        continue
                    varspec.append(("M", i, pos))
                    N_var.append(r2660._mul(self.D, {(off1 + pos, r1): 1}))
                    var_arm.append(i)
                    in_low_split.append(pos < m_pos)
                for pos in range(self.delta):
                    varspec.append(("B2", i, pos))
                    bt = {(off2 + pos, 0): 1}
                    N_var.append(r2660._add(
                        r2660._shift(bt, 0, r1),
                        r2660._scale(r2660._shift(bt, 0, self.repeats[i]), -1),
                    ))
                    var_arm.append(i)
                    in_low_split.append(False)
                for pos in range(tlen[i]):
                    if other_hole != "centre" and other_hole == (i, "tip", None) and pos == tlen[i] - 1:
                        continue
                    varspec.append(("T", i, pos))
                    N_var.append(r2660._mul(self.D, {(off2 + pos, self.repeats[i]): 1}))
                    var_arm.append(i)
                    in_low_split.append(False)

        m_dz = plen[split_arm] + 1 + m_pos
        m_dw = r1
        mon_m = r2660._monomial(m_dz, m_dw)
        mon_neg_m = r2660._monomial(-m_dz, -m_dw)

        const_corr = r2660._scale(r2660._mul(mon_m, self.D), sigma)
        if other_hole != "centre":
            o_arm, o_kind, _ = other_hole
            assert o_kind == "tip"
            const_corr = r2660._add(
                const_corr,
                r2660._scale(r2660._mul(self.ends[o_arm], self.D), sigma),
            )
        const_poly = r2660._add(
            r2660._scale(self.shell_unit, sigma),
            r2660._scale(r2660._mul(self.omz, const_corr), -1),
        )

        # Accumulate row sums and GF(2) masks linearly across varspec:
        row_sum = Counter()
        row_mask = {}
        for vi in range(len(varspec)):
            arm = var_arm[vi]
            N = N_var[vi]
            others = r2660._add(*(self.ends[j] for j in range(3) if j != arm))
            sh = r2660._add(
                r2660._mul(N, r2660._add(self.one, r2660._scale(others, -1))),
                r2660._mul(r2660._mul(r2660._monomial(self.delta), self.ends[arm]), r2660._star(N)),
            )
            corr = r2660._add({}, N) if sigma == 0 else {}
            if arm != split_arm:
                J_s = r2660._mul(mon_m, N)
            elif in_low_split[vi]:
                d_Sstar = {(z + self.delta, w): -c for (z, w), c in r2660._star(N).items()}
                J_s = r2660._mul(mon_m, d_Sstar)
            else:
                J_s = r2660._mul(mon_neg_m, N)
            corr = r2660._add(corr, J_s)
            if other_hole != "centre":
                o_arm = other_hole[0]
                if arm != o_arm:
                    J_o = r2660._mul(self.ends[o_arm], N)
                else:
                    neg_dNstar = {(z + self.delta, w): -c for (z, w), c in r2660._star(N).items()}
                    J_o = r2660._mul(self.ends[o_arm], neg_dNstar)
                corr = r2660._add(corr, J_o)

            poly = r2660._add(
                r2660._mul(r2660._monomial(1), sh),
                r2660._scale(r2660._mul(self.omz, corr), -1),
            )
            bit = 1 << vi
            for mon, c in poly.items():
                row_sum[mon] += c
                if c & 1:
                    row_mask[mon] = row_mask.get(mon, 0) ^ bit

        rows = []
        for mon in set(row_sum) | set(const_poly):
            rhs = -const_poly.get(mon, 0)
            r = rhs - row_sum.get(mon, 0)
            if r & 1:
                return "obstructed", "mod 2"
            y_bit = 1 if (r & 2) else 0
            msk = row_mask.get(mon, 0)
            if msk == 0:
                if y_bit:
                    return "obstructed", "mod 4 zero row"
            else:
                rows.append((msk, y_bit))
        if not _gf2_hensel1_from_rows(rows):
            return "obstructed", "Hensel level 1 (mod 4)"
        return "consistent", "passed Hensel level 1"


def sweep_all_arms_delta20() -> list[str]:
    """Sweep every proportional slope 0 < s < BASE[arm] across all 3 arms at delta=20."""
    aud = SplitBlockAuditor(20, plen=(18, 18, 5), m_len=5)
    scale = PERIOD // 20  # 133
    lines = []
    for arm in range(3):
        tested = 0
        for s in range(1, BASE[arm]):
            r1 = s * scale
            verdict, _ = aud.check_split(arm, r1, 2, (0, "tip", None), sigma=-1)
            assert verdict == "obstructed", (arm, s, r1)
            tested += 1
        lines.append(f"delta=20 arm {arm + 1}: all {tested} proportional split slopes obstructed (mod 4)")
    return lines


def sweep_flagship_arms() -> list[str]:
    """Check representative split slopes across all 3 arms and SPLIT=(0,0,0) at delta=2660."""
    aud = SplitBlockAuditor(PERIOD, plen=(18, 18, 5), m_len=5)
    lines = []
    samples = {
        0: [1, 20, 49, 79, 98],
        1: [1, 20, 39, 59, 78],
        2: [1, 5, 11, 17, 22],
    }
    for arm, slopes in samples.items():
        for r1 in slopes:
            for oh, sig in [((0, "tip", None), -1), ("centre", 0)]:
                verdict, _ = aud.check_split(arm, r1, 2, oh, sigma=sig)
                assert verdict == "obstructed", (arm, r1, oh, sig)
        lines.append(f"delta=2660 arm {arm + 1} slopes {slopes} (tip + centre): obstructed (mod 4)")
    # SPLIT = (0, 0, 0) invariance at delta=20 across all 3 arms:
    aud0 = SplitBlockAuditor(20, plen=(0, 0, 0), m_len=5)
    for arm in range(3):
        verdict, _ = aud0.check_split(arm, 133, 2, (arm, "tip", None), sigma=-1, plen_override=(0, 0, 0))
        assert verdict == "obstructed", (arm,)
    lines.append("delta=20 SPLIT=(0,0,0) all 3 arms obstructed (mod 4)")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sweep20", action="store_true")
    group.add_argument("--sweep2660", action="store_true")
    group.add_argument("--all", action="store_true")
    args = parser.parse_args(argv)
    if args.sweep20 or args.all:
        for line in sweep_all_arms_delta20():
            print("PASS:", line)
    if args.sweep2660 or args.all:
        for line in sweep_flagship_arms():
            print("PASS:", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
