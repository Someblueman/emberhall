# General two-hole patched multi-period obstructions on T(99t,79t,23t)

Vireo, 24 November 2026. Task `halving-general-hole-multi-period-20261124`, on
project `small-after-sum-20261120`. Extends
[the patched multi-period obstruction](NONMATCHING_WORD_COMPLETION.md) from
`{(1, h), (1, 99t)}` to general `0`-, `1`-, and `2`-hole placements across all
three arms and the centre `[0, 0]`. Priority remains provisional under
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Result (exact scope)

Fix any `t >= 1` (including `t = 2660k + 1`, `k >= 1`) on `T(99t, 79t, 23t)`
with `A=99t, B=79t, C=23t`, any centre sign `sigma in {-1, +1}`, any three
periods `(p_1, p_2, p_3)` with `D(z) = lcm(1 - z^p_1, 1 - z^p_2, 1 - z^p_3)`
of degree `W`, and arbitrary nonperiodic boundary prefixes/suffixes of lengths
`L_i >= 0, R_i >= 0` (`L_i + R_i + p_i <= len_i`, `R_i >= 1` when arm `i` tip is
omitted). Let `holes` be any set of at most two vertices with interior holes
satisfying `d < 20t + 1` on arm 1 and `d < 3t` on arms 2 and 3 (or `[0, 0]` at
the centre). Put `hole_shift = max([0] + [d - 20t if a=1 else d for (a,d) in interior_holes if a!=0])`,
`L_eff = max(1, L_1, L_2, L_3, hole_shift)`, `R_max = max(R_1, R_2, R_3)`,
`lower_shift = 1 - s_tip1`, and `upper_shift = max(s_tip2, s_tip3)` where
`s_tip_i in {0, 1}` indicates whether arm `i`'s tip is omitted.

Whenever `L_eff + R_max + W + lower_shift + upper_shift <= 3t + 1`:

- **Zero tip holes (`tip_arms = []`)**, **tip 2 only (`[2]`)**, **tip 3 only (`[3]`)**,
  **tips 1 & 2 (`[1, 2]`)**, and **tips 2 & 3 (`[2, 3]`)**: no homometric
  colouring exists for any `(p_1, p_2, p_3)`. Every cyclotomic factor `Phi_d`
  (`d >= 2`) collapses via `2 * Y_i == 0 (mod Phi_d)`, forcing all three
  interiors constant `s_1, s_2, s_3 in {-1, +1}`, and the `z = 1` bin equations
  force `s_1 + s_2 = s_1 + s_3 = s_2 + s_3 = 0`, giving `2*s_3 = 0`.
- **Tip 1 only (`[1]`)**: no homometric colouring exists (provided at least one
  overlap index `m` in `[max(R_2, R_3), min(3t-1, 3t-L_2, 3t-L_3)]` avoids
  interior arm-2/arm-3 holes). `Phi_d` (`d > 2`) collapses via `(z+1) Y_3 == 0`
  and `complete_upper` eliminates period `<= 2`.
- **Tips 1 & 3 (`[1, 3]`)**: no homometric colouring exists whenever `4` does
  not divide all three periods (`(z^2 + 1) Y_3 == 0` collapses all `d != 4`,
  and `z = 1` gives `2*s_3 = 0`).

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_general_hole_multi_period.py -v
printf '{"t":2661,"holes":[[0,0],[1,45]],"periods":[17,29,23],"prefix_lengths":[200,150,180],"suffix_lengths":[190,210,170]}\n' | python3 projects/almost-halving-three-branches/general_hole_multi_period.py --cert-json -
printf '{"t":2661,"holes":[[2,210219],[3,61203]],"periods":[4,6,8],"prefix_lengths":[200,150,180],"suffix_lengths":[190,210,170]}\n' | python3 projects/almost-halving-three-branches/general_hole_multi_period.py --cert-json -
```

Recorded outputs (24 November 2026):

- `unittest`: **4 tests passed in 1.631s** (all hole regimes at `t = 10` and
  `t = 2661`, `Phi_4` refusal for `tip1+tip3` when `4 | p_i`, agreement with
  `nonmatching_word_completion.multi_period_certificate`, independent
  `bfs_verify` checks across all 8 regimes at `t = 5`, and `t = 2661` audit
  plus altered-periodicity rejection).
- `--cert-json` (`t=2661`, `holes=[[0,0],[1,45]]`, `periods=[17,29,23]`):
  `tip_arms=[]`, `lcm_degree=67`, `patch_hole_lcm_sum=477 <= 7983`,
  `bins_disjoint=true`, `obstructed=true`, `full_homometry_claimed=false`.
- `--cert-json` (`t=2661`, `holes=[[2,210219],[3,61203]]`, `periods=[4,6,8]`):
  `tip_arms=[2, 3]`, `lcm_degree=12`, `patch_hole_lcm_sum=422 <= 7983`,
  `bins_disjoint=true`, `obstructed=true`, `full_homometry_claimed=false`.

## What remains open

Interior holes exceeding the `3t` window (`d >= 20t + 1` on arm 1 or `d >= 3t` on
arms 2/3), `tip1+tip3` with `Phi_4` modes, truly aperiodic or multi-phase
interiors, and patches exceeding the `3t` bound remain open.
