# Universal tip-hole closure on T(99t,79t,23t)

Vireo, 24 November 2026. Task `halving-universal-tip-multi-period-20261124`, on
project `small-after-sum-20261120`. Closes the two remaining exceptions left open in
[GENERAL_HOLE_MULTI_PERIOD.md](GENERAL_HOLE_MULTI_PERIOD.md):

1. `tip1+tip3` when `4` divides all three periods `(p_1, p_2, p_3)` (`Phi_4` modes), and
2. `tip1` when interior holes hit all upper-overlap indices `m` in `[m_lo, m_hi]`.

## Mechanism

Let `s_1, s_2, s_3 in {0, 1}` indicate whether the tips `(1, 99t)`, `(2, 79t)`,
and `(3, 23t)` belong to the `<= 2`-hole set. Outside `A + lower_shift + L_eff + W`,
all interior-hole terms lie strictly below `bc_lo` whenever interior holes satisfy
`d < 20t + 1` on arm 1 or `d < 3t` on arms 2 and 3. After multiplying `(1-z)F(z) - 2zS(z)`
by `D(z) = lcm(1 - z^{p_1}, 1 - z^{p_2}, 1 - z^{p_3})` and restricting to the disjoint
top bins `BC`, `AC`, and `AB`, the finite suffix-patch terms vanish modulo every
cyclotomic factor `Phi_d(z)` (`d | lcm(p_1, p_2, p_3)`, including `d = 1`), leaving
the exact `3 x 3` linear system in `U_i = Q_i Y_i`:

```text
BC:          z^(1-s_3) U_2 + z^(1-s_2) U_3 == 0  (mod Phi_d)
AC: z^(1-s_3) U_1          + z^(1-s_1) U_3 == 0  (mod Phi_d)
AB: z^(1-s_2) U_1 + z^(1-s_1) U_2          == 0  (mod Phi_d)
```

Its exact determinant is `2 * z^(3 - s_1 - s_2 - s_3)`, which is nonzero in the
cyclotomic integral domain `Z[zeta_d]` for **every** `d >= 1` and **every** tip-hole
indicator `(s_1, s_2, s_3) in {0, 1}^3` (including `(1, 0, 1)` at `d = 4`, where
`det = 2z` gives `2 i != 0`). Hence `Y_i == 0 (mod Phi_d)` for all `d >= 2`
dividing `p_i` (forcing constant interiors `c_i in {-1, +1}`), and then `d = 1`
gives `Q_i(1) * p_i * c_i == 0` with `Q_i(1) >= 1`, an immediate contradiction from
the bins alone.

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_universal_tip_multi_period.py -v
printf '{"t":2661,"holes":[[1,263439],[3,61203]],"periods":[4,8,12],"prefix_lengths":[200,150,180],"suffix_lengths":[190,210,170]}\n' | python3 projects/almost-halving-three-branches/universal_tip_multi_period.py --cert-json -
```

Recorded outputs (24 November 2026):

- `unittest`: **4 tests passed in 1.767s** (symbolic `2 * z^(3 - s_1 - s_2 - s_3)`
  across all 8 tip-hole vectors, `tip1+tip3` with `periods=(4,4,4)` and `(4,8,12)`
  including `t = 2661`, `tip1` with `periods=(1,1,1)` and `(2,2,2)`, `bfs_verify`
  checks at `t = 7`, and `t = 2661` audit plus altered-periodicity rejection).
- `--cert-json` (`t=2661`, `holes=[[1,263439],[3,61203]]`, `periods=[4,8,12]`):
  `bin_det_exponent=1`, `lcm_degree=16`, `patch_hole_lcm_sum=426 <= 7983`,
  `bins_disjoint=true`, `obstructed=true`, `full_homometry_claimed=false`.
