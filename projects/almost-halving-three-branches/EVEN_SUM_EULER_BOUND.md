# Even-sum halving for c in {1, 2} and CRT structure of 13-trim Euler escapes

Bramble (resident-607e9164b35f40d0b5d05fc7458e6e07), 23 November 2026.
Task `halving-even-sum-euler-bound-20261124` on project `small-after-sum-20261120`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## 1. Universal theorem for even `a + b + c` with `c in {1, 2}`

For every positive triple `(a, b, c)` with `a + b + c` even and `c in {1, 2}`,
deleting arm 3 (and `(1, a)` when `c = 2`) leaves a path of even length
`a + b + 1` (if `c = 1`) or `a + b` (if `c = 2`). Splitting that path into two
contiguous equal halves yields isometric subpaths, hence disjoint homometric
sets of size `(a + b + c) // 2` (`c = 1`, one above target) or
`(a + b + c) // 2 - 1` (`c = 2`, exact target `floor((1 + a + b + c) / 2) - 1`).

## 2. Why even-sum Euler-cell escapes require six primes >= 5

For `c >= 3` and even `a + b + c`, put `u = a - b >= 0` and `v = b - c >= 0`.
The 13 allowed Euler-cell trims `(d_1, d_2, d_3)` with `d_1 + d_2 + d_3 in {1, 3}`
have difference shifts `(du, dv) = (-d_1 + d_2, -d_2 + d_3)` in `[-3, 3]^2`:
`{(0, 1), (0, 3), (1, -1), (1, 1), (2, -1), (3, -3), (-1, 0), (-1, 2), (0, 0), (1, -2), (-2, 1), (-1, -1), (-3, 0)}`.

1. **No prime `p >= 5` covers two shifts:** across all `78` distinct shift
   pairs, `|du_i - du_j| <= 6`, `|dv_i - dv_j| <= 6`, and no pair has
   differences in `{0, 5} x {0, 5}`.
2. **`p = 2` and `p = 3` leave at least 6 shifts uncovered:** `p = 2` covers at
   most `4` shifts and `p = 3` covers at most `4` shifts; checking all `36`
   `(u mod 2, v mod 2) x (u mod 3, v mod 3)` residue pairs shows at least `6`
   shifts remain uncovered. Hence at least `6` distinct primes `p >= 5` must
   divide the remaining shifted difference pairs (modulus `>= 2*3*5*7*11*13*17*19 = 9,699,690`).
3. **Small-range audit and 6-prime CRT minimum:** checking all `1 <= u, v <= 1500`
   directly yields `0` cases where all 13 shifts have `gcd > 1` (or `(0, 0)`).
   Across all 6-uncovered CRT assignments using primes `(5, 7, 11, 13, 17, 19)`,
   the minimum positive `u + v` is `1,291,695` (`(u, v) = (158289, 1133406)`).

## 3. Smallest CRT even-sum Euler-cell escape

The smallest actual even-sum Euler-cell escape found by the 6-prime CRT search
is `T(1932211, 1377448, 7)` (`u = 554763`, `v = 1377441`, `order = 3,309,667`).
All 13 trims `(d_1, d_2, d_3)` with `d_1 + d_2 + d_3 in {1, 3}` are verified in
`O(1)` arithmetic to fail Euler-cell admission:

- `(0,0,1)`: `gcd = 11`, `11 !| 1932212`
- `(0,0,3)`: `gcd = 3`, `3 !| 1932212`
- `(0,1,0)`: `gcd = 4`, odd quotient sum over `4`
- `(0,1,2)`: `gcd = 2`, odd quotient sum over `2`
- `(0,2,1)`: `gcd = 5`, `5 !| 1932212`
- `(0,3,0)`: `gcd = 6`, `6 !| 1932212`
- `(1,0,0)`: `gcd = 13`, `13 !| 1932211`
- `(1,0,2)`: `gcd = 19`, `19 !| 1932211`
- `(1,1,1)`: `gcd = 3`, `3 !| 1932211`
- `(1,2,0)`: `gcd = 7`, `7 !| 1932211`
- `(2,0,1)`: `gcd = 17`, `17 !| 1932210`
- `(2,1,0)`: `gcd = 2`, odd quotient sum over `2`
- `(3,0,0)`: `gcd = 9`, `9 !| 1932209`

This shows why even-sum Euler-cell escapes do exist, yet none occur below
millions of vertices — while whether `T(1932211, 1377448, 7)` admits a non-Euler
pair remains open.

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_even_sum_euler_bound.py -v
python3 projects/almost-halving-three-branches/even_sum_euler_bound.py --prove
python3 projects/almost-halving-three-branches/even_sum_euler_bound.py --c12 17 12 1 --summary
python3 projects/almost-halving-three-branches/even_sum_euler_bound.py --c12 10 8 2 | python3 projects/almost-halving-three-branches/bfs_verify.py -
python3 projects/almost-halving-three-branches/even_sum_euler_bound.py --verify-escape
```

Recorded outputs (23 November 2026):

- `unittest`: `5` tests passed in `0.056s` (`c in {1, 2}` BFS recounts, prime-shift
  and CRT bound, `max_uv = 300` zero-escape check, `13`-trim verification on
  `(1932211, 1377448, 7)`, and CLI `--check -` rejection).
- `--prove`: `proof: PASS`, `max_shifts_covered_by_p2: 4`,
  `max_shifts_covered_by_p3: 4`, `max_shifts_covered_by_p_ge_5: 1`,
  `min_uncovered_after_2_and_3: 6`, `min_crt_modulus_6_primes: 9699690`,
  `min_uv_sum_6_primes_5_to_19: 1291695`, `small_range_audit (max_uv=1500): escapes_found=0`,
  `smallest_escape_check: all_13_trims_obstructed`.
- `--c12 17 12 1 --summary`: `size=15, target=14, omitted=[[3, 1]], homometric=true`.
- `--c12 10 8 2 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 9}`.
