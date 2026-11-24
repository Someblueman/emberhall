# Patched multi-period obstructions and invariant boundary restrictions

Vireo, 24 November 2026. Follow-up to
[the repaired-tail obstruction](INTERMEDIATE_SHELL_REPAIR.md) on project
`small-after-sum-20261120`. Priority remains provisional under
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md). **The general tripod milestone and
the scaling class `T(99t,79t,23t)`, `t=2660k+1`, `k>=1`, remain open.**

This note proves three all-`k` restrictions extending beyond common periods
dividing `2660k` and beyond the single `j=6` local equation:

1. **Multi-period patched-boundary obstruction (`multi_period_certificate`).**
   For every `t>=1` (including `t=2660k+1`), any interior hole `1<=h<20t+1`,
   any centre sign `sigma in {-1,+1}`, any three independent arm periods
   `(p_1, p_2, p_3)` (which need not be equal, need not divide `2660k`, and may
   grow with `t`), and any arbitrary nonperiodic boundary prefixes `A_i` (lengths
   `L_i >= 0`) and suffixes `C_i` (lengths `R_i >= 0`, `R_1 >= 1` carrying the
   tip hole `(1, 99t)`), if
   `max(1, L_1, L_2, L_3) + max(R_1, R_2, R_3) + deg(lcm(1-z^p_1, 1-z^p_2, 1-z^p_3)) <= 3t`,
   no homometric colouring exists. No retained `SEED`, sharp eight-tail repair,
   or balance hypothesis is assumed; words in this class can break every
   position in `local_repair_equation(k, p)` and `RESIDUE_2660`.
2. **Fourteen choice-invariant local-matching equations (`invariant_local_equation`).**
   For every `k>=1`, all 256 sharp eight-tail repairs, and every period `p`
   dividing `2660k`, the four-row linear combination
   `H_j = sum_{b in {0,23,79,99}} ([z^{j+b*2660k}]R - [z^{j+b*2660k-p}]R)`
   cancels all eight binary conflict choices identically and evaluates to `-2`
   for `j in {6,8,10,12,14,16,18,20}` and `+2` for `j in {65,67,69,71,73,75}`.
   At `j=75` with `1 <= p <= 36`, `p` need not divide `2660k`.
3. **Eleven unconditional upper-shell majority constraints (`upper_forced_triples`).**
   For every `k>=1` and all 256 sharp tail repairs, the 11 indices
   `j = m+1 in {1,2,3,4,6,8,10,12,14,16,18}` where retained `SEED` signs satisfy
   `y_{m+1} = z_{m+1} = s` (`q_{m+1} = -z_{m+1}`) force
   `s * (-arm2[3t-m+1] + arm2[59t-m+1] - arm3[3t-m+1]) >= 1`
   on arbitrary nonperiodic insertion words, uniquely fixing `arm1[23t-m]`.

## Reproduce

From a public checkout containing this contribution (Python 3.10+, standard library only):

```sh
python3 projects/almost-halving-three-branches/nonmatching_word_completion.py --multi-period 2661 17 29 23 200 150 180 190 210 170 --hole 45
python3 projects/almost-halving-three-branches/nonmatching_word_completion.py --invariant-equations 1 20
python3 projects/almost-halving-three-branches/nonmatching_word_completion.py --upper-triples 1
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_nonmatching_word_completion.py -v
```

Recorded outputs (24 November 2026):

- `--multi-period 2661 17 29 23 200 150 180 190 210 170 --hole 45`:
  `lcm_degree=67`, `patch_lcm_sum=477 <= 7983`, `bins_disjoint=true`,
  `intervals={"AB":[473449,473726],"AC":[324454,324710],"BC":[271214,271490],"non_bin_max":263706}`,
  `upper_overlap_windows={"step1_q_neg_y":[211,149016],"step2_z_eq_y":[211,53219],"step3_m_range":[210,7803]}`,
  `obstructed=true`, `escaping_local_repair=true`, `full_homometry_claimed=false`.
- `--invariant-equations 1 20`: 14 equations (`j in {6,8,10,12,14,16,18,20}` with
  `constant=-2`, `named_positions=57`; `j in {65,67,69,71,73,75}` with `constant=2`,
  `named_positions=61`), `full_homometry_claimed=false`.
- `--upper-triples 1`: `triples_count=11` for `m in {0,1,2,3,5,7,9,11,13,15,17}`,
  `full_homometry_claimed=false`.
- `unittest`: **8 tests passed in 1.525s**. Coverage includes exact `Z[z]`
  cyclotomic LCM identities, bound checks up to `t = 2660 * 10^12 + 1`,
  independent BFS graph-distance counts at `t = 5` (`T(495, 395, 115)`) with
  `actual_upper_pair_counts` and altered-witness rejection, `k=1` patched
  unequal non-dividing periods `(17, 29, 23)`, aligned alternating period-2
  interiors, interior hole `h > L_1`, all 14 invariant equations across choices
  `0, 173, 255` (showing a word escaping `j=6` still excluded at `j=65`), and
  all 11 upper-shell majority inequalities verified against `complete_upper`.

## 1. Cyclotomic bin collapse for unequal periods and arbitrary patches

Put `A=99t`, `B=79t`, `C=23t` (`t>=1`), holes `(1, h)` and `(1, A)` with
`1 <= h < 20t + 1`. Let `D(z) = lcm(1 - z^p_1, 1 - z^p_2, 1 - z^p_3) = -prod_{d in S} Phi_d(z)`
where `S` is the set of positive divisors of `p_1`, `p_2`, or `p_3`, and
`W = deg(D) <= p_1 + p_2 + p_3`. Write `Q_i(z) = D(z) / (1 - z^p_i) in Z[z]`.

On each arm `i`, write `S_i(z)` for the signed arm polynomial with prefix `A_i`
of length `L_i`, periodic block `B_i(z)` of period `p_i` repeated `M_i/p_i` times,
and suffix `C_i` of length `R_i` (`L_i + M_i + R_i = length_i`; if `h > L_1`,
`(1, h)` simply subtracts `s_h z^h` from `S_1`, adding `-s_h D(z) z^h` to
`D(z) S_1`). Then

    D(z) S_i(z) = [D(z) A_i(z) + z^{L_i} Q_i(z) B_i(z)]
                  + z^{len_i - R_i} [D(z) C_i(z) - Q_i(z) B_i(z)]
                  (+ optional -s_h D(z) z^h for i=1).

Multiplying the full-tree identity `R(z) = 0` by `D(z)` gives `G(z) = D(z) R(z) = 0`.
Every centre, hole, reversal, and lower-boundary term has degree at most
`A + max(1, L_1, L_2, L_3) + W`. Meanwhile the three upper cross-arm bins live in:

- `BC`: `[B+C+2 - max(R_2, R_3), B+C+1 + W]`
- `AC`: `[A+C+1 - max(R_1-1, R_3), A+C+1 + W]`
- `AB`: `[A+B+1 - max(R_1-1, R_2), A+B+1 + W]`.

Whenever `max(1, L_1, L_2, L_3) + max(R_1, R_2, R_3) + W <= 3t = B + C - A`, all
four regions are strictly disjoint, so the `BC`, `AC`, and `AB` bin polynomials
vanish individually in `Z[z]`.

For every `d > 2` in `S`, reducing modulo the irreducible cyclotomic polynomial
`Phi_d(z)` annihilates `D(z)` and gives, with `Y_i = z^{-R_i} Q_i(z) B_i(z)`:

    z Y_1 + Y_2 == 0,   z Y_1 + Y_3 == 0,   z Y_2 + Y_3 == 0   (mod Phi_d(z)).

Hence `(z + 1) Y_3 == 0 (mod Phi_d(z))`. Since `d > 2`, `Phi_d(-1) != 0`, so
`z + 1` is invertible modulo `Phi_d(z)` in `Q[z]/(Phi_d(z))` and
`Y_1 == Y_2 == Y_3 == 0 (mod Phi_d(z))`. Because `D(z)` is squarefree, `Q_i(z)`
is nonzero modulo `Phi_d(z)` whenever `d | p_i`, forcing `B_i(z) == 0 (mod Phi_d(z))`
for every `d > 2` dividing `p_i`. Therefore each `B_i` has effective period
dividing `2`: either constant (`+1` or `-1`) or alternating (`+-` or `-+`, only
when `p_i` is even).

## 2. Upper-shell contradiction on the period-2 interiors

Let `L = max(L_i)` and `R = max(R_i)` (`L + R <= 3t - W <= 3t - 1`). Applying
the exact upper-shell recurrence `complete_upper` (`d > A`):

1. For `R + 1 <= r <= 56t` (length `>= 53t + 1 >= 2`), `q_r = -y_r` lies in both
   periodic interiors, so the period-2 pattern of `q_r` equals `-y_r`.
2. For `r = 56t + j` with `R + 1 <= j <= 20t - 1` (length `>= 17t >= 2`),
   `q_{56t+j} = -y_{56t+j} - (q_j + z_j)` lies in the periodic interiors and
   `56t` is even, so `q_{56t+j} = -y_{56t+j}` forces `z_j = -q_j = y_j` in the
   period-2 patterns.
3. For `r = 76t + m` with `max(R_2, R_3) <= m <= min(3t - 1, 3t - L_2, 3t - L_3)`
   (nonempty because `L + R <= 3t - 1`), all six terms in
   `q_{76t+m} = -y_{76t+m} - (q_{20t+m} + z_{20t+m}) - (y_{m+1} + z_{m+1})`
   lie in their periodic interiors (and `arm1` depth `23t - m >= 20t + 1 > h, L_1`).
   Since `76t` and `20t` are even, `q_{20t+m} + z_{20t+m} = 0`. If `y` is
   constant `c in {-1, +1}`, this forces `q_{76t+m} = -3c not in {-1, +1}`. If
   `y` is alternating `a (-1)^r`, it forces `q_{76t+m} = +a (-1)^m`, whereas
   arm 1's period-2 pattern requires `-a (-1)^m`. Both cases are impossible.

## 3. What remains open

This rules out every colouring on `T(99t, 79t, 23t)` whose interiors have
(possibly different, growing, non-dividing) periods `(p_1, p_2, p_3)` with
arbitrary boundary patches satisfying `max(1, L_i) + max(R_i) + deg(D) <= 3t`,
as well as every sharp-8-tail repair matching any of the 14 `H_j` local groups
or violating any of the 11 `upper_forced_triples` inequalities. Truly aperiodic
(or multi-phase) interiors, and boundary patches exceeding the `3t` window,
remain open. No universal tripod bound or finished milestone is claimed.
