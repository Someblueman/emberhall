# Three-parameter interior-hole family with c = r + 4m

Vireo, 24 November 2026. Task `halving-c-plus-4m-three-param-20261124`, on
project `small-after-sum-20261120`. Generalizes
[the c = r + 4 family](INTERIOR_HOLE_C_PLUS_4.md) (`m = 1`) to all `m >= 1`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Main result

For **every integer `m >= 1`**, **every odd integer `r >= max(5, 4m - 1)`**,
and **every integer `k >= 0`**, the tripod

```text
T(r*(k + 3) + 4m,  r*(k + 2) + 4m - 1,  r + 4m)
```

has disjoint equal-size subsets with identical multisets of all original-tree
pairwise distances, each of size `floor((1 + a + b + c)/2) - 1 = r*(k + 3) + 6m - 1`,
omitting `[1, r]` and `[1, a]`.

In particular, beyond `(211, 187, 27)` and `(235, 223, 15)` (`m = 1`), this
settles the previously open `a <= 300` Euler-cell escapes `(215, 191, 31)`
(`r=23, m=2, k=6`, size `218`) and `(227, 203, 43)` (`r=23, m=5, k=6`, size
`236`), reducing the remaining `1 <= c <= b <= a <= 300` count from `29` to `25`
(`24` open triples plus `(227, 67, 11)` already proved below target in
[LONG_FRONTIER.md](LONG_FRONTIER.md)).

## Explicit construction

Let `s_0 = -1` at `[0, 0]`, `alt = "+-" * ((r - 1) // 2)`,
`rev_alt = "-+" * ((r - 1) // 2)`, and put:

- `B_1 = "-+" * (2m - 1) + "-" + "+" * (r - (4m - 1))` (length `r`, sum `r - 4m`)
- `B_2 = "-+" * (2m - 1) + "-" * (r - (4m - 1)) + "+"` (length `r`, sum `4m - r`)
- `t_1 = "-+" * (2m - 1) + "--"` (length `4m`, sum `-2`)
- `t_2 = "-+" * (2m - 1) + "+"` (length `4m - 1`, sum `+1`)
- `W_1 = alt + "0" + B_1^(k + 1) + t_1 + alt + "0"`
- `W_2 = alt + "++" + B_2^k + t_2 + rev_alt`
- `W_3 = "+-" * (2m - 1) + "+" + "-" * (r - (4m - 2)) + "+-" * (2m - 1) + "+"`
  (length `r + 4m`, sum `4m - r`).

Total sign sum is `-1 + (r - 4m) - 2 + 2 + 1 + (4m - r) = 0`, giving balanced
sets of size `(a + b + c - 1) / 2 = r*(k + 3) + 6m - 1`. At `m = 1` this
reproduces `interior_hole_c_plus_4.py` identically.

## Exact 4-variable Laurent-ring proof

Work over `Z[z, z^-1, R, R^-1, M, M^-1, W, W^-1]` with `R = z^r`, `M = z^(4m)`,
`W = z^(rk)`, and denominator `D(z, R) = (1 - z^2)(1 - R)`. With
`N_alt = (1 - z)(1 - R)(z - R)`, the cleared arm polynomials are:

- `N_1 = N_alt + R * b1_num * (1 - R*W) + R^2 * W * (1 - R) * t1_num + R^2 * M * W * N_alt`
- `N_2 = N_alt + D * R * (1 + z) + R * z * b2_num * (1 - W) + R * z * W * t2_num - R * M * W * N_alt`
- `N_3 = (1 - R) * (z - z^2 - 2*z*M + 2*z^2*R + z*R*M - z^2*R*M)`.

With `E_1 = R^3 M W`, `E_2 = z^-1 R^2 M W`, `E_3 = R M` and `D^* = z^-2 R^-1 D`,
the cleared identity `D * E(z) = D * Q(z) - (z^-1 - 1)(DC_tip + DC_hole)`
vanishes identically (`0` nonzero terms across all four variables). Flipping
`s_0` to `+1`, omitting `DC_hole`, or corrupting the block produces `16`, `30`,
and `43` nonzero terms respectively, and the `(r=7, m=2, k=1)` corrupted `s_0`
specialization matches `2*(z^-1 - 1)*(D_left - D_right)*D - 2*(|L| - |R|)*D`
term by term.

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_interior_hole_c_plus_4m.py -v
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4m.py --prove
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4m.py --tree 215 191 31 --summary
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4m.py --tree 227 203 43 --summary
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4m.py --witness 23 2 6 | python3 projects/almost-halving-three-branches/bfs_verify.py -
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4m.py --audit-escapes --max-a 300
```

Recorded outputs (24 November 2026):

- `unittest`: **5 tests passed in 0.218s** (4-variable Laurent proof and
  corruptions, `m=1` parity with `interior_hole_c_plus_4.py`, standalone
  `bfs_verify` checks across `(5,1,0)`, `(7,2,0)`, `(7,2,1)`, `(9,2,1)`,
  `(11,3,1)`, `(23,2,6)`, `(23,5,6)`, arm permutations, altered-pair rejection
  moving `[0, 0]` to `[1, 7]`, and parameter validation).
- `--prove`: `proof: PASS`, `residual_terms: 0`, `corrupt_s0_terms: 16`,
  `corrupt_hole_terms: 30`, `corrupt_block_terms: 43`,
  `specialization_matches_difference: true`.
- `--tree 215 191 31 --summary`: `r=23, m=2, c=31, k=6, size=218, target=218, omitted=[[1, 23], [1, 215]], homometric=true`.
- `--tree 227 203 43 --summary`: `r=23, m=5, c=43, k=6, size=236, target=236, omitted=[[1, 23], [1, 227]], homometric=true`.
- `--witness 23 2 6 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 218}`.
- `--audit-escapes --max-a 300`: `prior_remaining_count: 29`,
  `newly_settled_by_c_plus_4m: [[211, 187, 27], [215, 191, 31], [227, 203, 43], [235, 223, 15]]`,
  `remaining_open_count: 25`.
