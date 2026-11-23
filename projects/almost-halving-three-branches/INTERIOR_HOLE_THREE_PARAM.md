# A three-parameter interior-hole family and Euler-cell escape taxonomy

Bramble (resident-607e9164b35f40d0b5d05fc7458e6e07), 23 November 2026.
Task `halving-three-param-interior-20261124` on project `small-after-sum-20261120`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Main result

For every odd integer `r >= 1`, every odd integer `c` with `1 <= c <= r`, and
every integer `k >= 0`, the tripod

```text
T(r*(k + 2) + c,  r*(k + 1) + c - 1,  c)
```

has disjoint equal-size subsets with identical multisets of all original-tree
pairwise distances, each of size `floor((1 + a + b + c) / 2) - 1 = r*(k + 1) + (r + 3*c - 1) // 2`,
omitting exactly the interior vertex `(1, r)` and the longest-arm tip `(1, a)`.
In particular, this settles the previously open `a <= 300` Euler-cell escapes
`(187, 163, 3)` (`r=23, c=3, k=6`), `(203, 179, 19)` (`r=23, c=19, k=6`), and
`(227, 215, 7)` (`r=11, c=7, k=18`), along with infinitely many shifted/scaled
triples. The universal conjecture remains false (`h(T(227,67,11)) <= 151 < 152`
in [LONG_FRONTIER.md](LONG_FRONTIER.md)), and the remaining open triples and
infinite obstruction question remain open.

## Explicit construction

Let `s_0 = -1` at `[0, 0]`, and define the three arm words over `{+, -, 0}`:

- `alt = "+-" * ((r - 1) // 2)` (length `r - 1`)
- `B_1 = ("-" * c) + ("+-" * ((r - c) // 2))` (length `r`), `B_2 = -B_1`
- `t_1 = "+-" * ((c - 1) // 2)`, `t_2 = "-+" * ((c - 1) // 2)` (each length `c - 1`)
- `W_1 = alt + "0" + B_1^(k+1) + t_1 + "0"` (length `r*(k + 2) + c`)
- `W_2 = alt + "+" + B_2^k + t_2` (length `r*(k + 1) + c - 1`)
- `W_3 = "+" * c` (length `c`)

Positive signs form `left` and negative signs (including `[0, 0]`) form `right`.
Because `sum(alt) = 0`, `sum(t_1) = sum(t_2) = 0`, `sum(B_1) + sum(B_2) = 0`,
and `B_1` has `c` minuses (`sum(B_1) = -c`), the total sign sum is
`s_0 + sum(B_1) + sum(W_3) + 1 = -1 - c + c + 1 = 0`, giving balanced sets of
size `(a + b + c - 1) / 2 = floor((1 + a + b + c) / 2) - 1`.

## Exact 4-variable Laurent-ring proof

Work over `Z[z, z^-1, R, R^-1, C, C^-1, W, W^-1]` with `R = z^r`, `C = z^c`,
`W = z^(r*k)`, and common denominator `D(z, R) = (1 - z^2)(1 - R)`:

- `N_alt = D * P_alt = (1 - z)(1 - R)(z - R)`
- `B_1,num = -z(1 + z)(1 - C) + z(1 - z)(C - R)`
- `N_1 = N_alt + R * B_1,num * (1 - R*W) + R^2*W*(1 - z)(1 - R)(z - C)`
- `N_2 = N_alt + D*R - R * B_1,num * (1 - W) - R*W*(1 - z)(1 - R)(z - C)`
- `N_3 = z(1 + z)(1 - R)(1 - C)`

Using `D* = z^-2 R^-1 D` (since `r` is odd, `z^2` and `R` are independent) and
`E_1 = R^2 W C`, `E_2 = R W C z^-1`, `E_3 = C`, the cleared shell-and-hole
polynomial `D * E(z) = D * Q(z) - (z^-1 - 1)(D * C_tip + D * C_hole)` vanishes
identically in all four variables (`0` nonzero terms). Clearing `(1 - z^2)(1 - R)`
in the integral domain `Z[z, z^-1]` at every concrete `(r, c, k)` proves
`D_left(z) = D_right(z)` identically for all distances. Corrupting `s_0`,
omitting `C_hole`, or flipping the first letter of `B_1` yields nonzero
residuals (`16`, `25`, and `23` terms respectively), and the `(r=7, c=3, k=1)`
corrupted specialization matches `2*(1 - z)/z * (D_left - D_right)*D - 2*(|L|-|R|)*D`
term by term.

## Euler-cell escape taxonomy (`1 <= c <= b <= a <= 300` and 346-triple grid)

Auditing all `4,545,100` triples `1 <= c <= b <= a <= 300` against Euler-cell
prefix trimming ([RATIO_51_33_10.md](RATIO_51_33_10.md)) and equal-arms
alternating:

- **Even `a + b + c`**: `0` escapes out of all triples with `a <= 300` (13 allowed
  1-tip and 3-tip trims suffice everywhere in this range).
- **Odd `a + b + c`**: `57` triples escape Euler-cell prefix trimming:
  - `33` retain at least one `r = 0` prefix trim not obstructed by the
    root-residue lemma (`g | L_1, L_2, L_3` with `g >= 3` odd);
  - `24` have all 7 full-prefix trims root-residue obstructed.
- Combining Euler-cell trimming with [FIXED_DIFFERENCE_FAMILY.md](FIXED_DIFFERENCE_FAMILY.md)
  (`T(c+76, c+56, c)`), [CORRECTED_SUBDIVISION.md](CORRECTED_SUBDIVISION.md),
  and the present three-parameter family leaves `29` triples in `1 <= c <= b <= a <= 300`
  (of which `(227, 67, 11)` is already proved below target in
  [LONG_FRONTIER.md](LONG_FRONTIER.md), and `28` remain open).
- On the `346`-triple coarse grid (`a=5..55 step 5, b<a step 5, c<b step 3`)
  from [GRID_REFRESH.md](GRID_REFRESH.md), `published_cases.py`,
  `ratio_51_33_10.py`, and `interior_transfer.py` already settle **346 / 346**
  triples (including all previously noted energy-2 cases `(45, 20, 8)`,
  `(55, 20, 5)`, and `(40, 30, 14)`).

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_interior_hole_three_param.py -v
python3 projects/almost-halving-three-branches/interior_hole_three_param.py --prove
python3 projects/almost-halving-three-branches/interior_hole_three_param.py --tree 187 163 3 --summary
python3 projects/almost-halving-three-branches/interior_hole_three_param.py --tree 203 179 19 --summary
python3 projects/almost-halving-three-branches/interior_hole_three_param.py --tree 227 215 7 --summary
python3 projects/almost-halving-three-branches/interior_hole_three_param.py --witness 23 3 6 | python3 projects/almost-halving-three-branches/bfs_verify.py -
python3 projects/almost-halving-three-branches/interior_hole_three_param.py --audit-escapes --max-a 300
```

Recorded outputs (23 November 2026):

- `unittest`: `6` tests passed (independent BFS recounts across 10 `(r, c, k)`
  cases, permutation matching, CLI rejection of an altered pair moving `[0, 0]`
  to `[1, 7]`, symbolic proof + corruptions, and small escape audit).
- `--prove`: `proof: PASS`, `residual_terms: 0`, `corrupt_s0_terms: 16`,
  `corrupt_hole_terms: 25`, `corrupt_block_terms: 23`,
  `specialization_matches_difference: true`.
- `--tree 187 163 3 --summary`: `r=23, c=3, k=6`, `size=176, target=176`,
  `omitted=[[1, 23], [1, 187]]`, `homometric=true`.
- `--tree 203 179 19 --summary`: `r=23, c=19, k=6`, `size=200, target=200`,
  `omitted=[[1, 23], [1, 203]]`, `homometric=true`.
- `--tree 227 215 7 --summary`: `r=11, c=7, k=18`, `size=224, target=224`,
  `omitted=[[1, 11], [1, 227]]`, `homometric=true`.
- `--witness 23 3 6 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 176}`.
- `--audit-escapes --max-a 300`: `total_triples: 4545100`,
  `even_sum_euler_escapes: 0`, `odd_sum_euler_escapes: 57`
  (`r0_surviving_prefix_escapes: 33`, `all_prefix_dead_escapes: 24`),
  `newly_settled_by_three_param: [[187, 163, 3], [203, 179, 19], [227, 215, 7]]`,
  `remaining_open_count: 29`, `grid_settled: 346 / 346`.
