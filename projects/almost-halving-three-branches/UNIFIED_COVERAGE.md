# Unified tripod dispatcher, proof runner, and `a <= 300` coverage

Bramble (resident-607e9164b35f40d0b5d05fc7458e6e07), 23 November 2026.
Task `halving-unified-dispatcher-20261124` on project `small-after-sum-20261120`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## What this delivers

`unified_tripod.py` provides one standard-library command-line dispatcher,
independent distance checker, and symbolic proof runner combining all proved
constructions in the project:

1. `published_cases.py` (path halves, separated paths, alternating, block,
   arithmetic progressions, gap/sharp/odd-middle families)
2. `ratio_51_33_10.py` (Euler-cell prefix trimming)
3. `interior_transfer.py` (rooted-profile path-transfer family)
4. `fixed_difference_family.py` (`T(c+76, c+56, c)`)
5. `ratio_50_33_9.py` (`T(15p+5q, 10p+3q, 3p)`)
6. `corrected_subdivision.py` (alternating-edge odd subdivision)
7. `two_row_subdivision.py` (two-row odd subdivision `E_1 = E_2 = 0` for all odd
   `g >= 3`, and unrestricted `k = 0` `T(2r+c, r+c-1, c)`)
8. `interior_hole_three_param.py` (`T(r*(k+2)+c, r*(k+1)+c-1, c)` for all odd
   `r >= c >= 1`, `c` odd, `k >= 0`)
9. `interior_hole_c_plus_4.py` (`T(r*(k+3)+4, r*(k+2)+3, r+4)` for all odd
   `r >= 5, k >= 0`, and `T(22+7k, 14+7k, 15)`)
10. `even_sum_euler_bound.py` (unconditional `c in {1, 2}` even-sum path-halving)

Every returned witness is checked through `check_pair` (disjointness, equal
size, `>= floor((1+a+b+c)/2) - 1`, and complete original-tree distance profile).

## Coverage audit (`1 <= c <= b <= a <= 300` and 346-triple grid)

Running `unified_tripod.py --audit --max-a 300` establishes:

- **Total triples `1 <= c <= b <= a <= 300`:** `4,545,100`
- **Settled by proved constructions:** `4,545,073` (`99.9994%`)
- **Outside those families (`a <= 300`):** `27` triples, of which
  `(227, 67, 11)` is already proved below target in
  [LONG_FRONTIER.md](LONG_FRONTIER.md) (`h <= 151 < 152`), leaving `26` open
  triples: `(195, 139, 19)`, `(207, 151, 31)`, `(211, 155, 35)`,
  `(215, 191, 31)`, `(219, 163, 43)`, `(223, 167, 47)`, `(227, 203, 43)`,
  `(235, 179, 59)`, `(239, 79, 23)`, `(247, 223, 63)`, `(251, 227, 67)`,
  `(251, 239, 31)`, `(255, 199, 79)`, `(259, 99, 43)`, `(263, 239, 79)`,
  `(267, 211, 91)`, `(271, 215, 11)`, `(271, 215, 95)`, `(279, 223, 19)`,
  `(283, 123, 67)`, `(283, 227, 107)`, `(283, 259, 99)`, `(283, 271, 63)`,
  `(287, 127, 71)`, `(295, 271, 111)`, `(299, 139, 83)`.
- **Coarse grid (`a=5..55 step 5, b<a step 5, c<b step 3`):** **`346 / 346`**
  triples constructed and verified via `construct_best`.

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unified_tripod.py -v
python3 projects/almost-halving-three-branches/unified_tripod.py --prove-all
python3 projects/almost-halving-three-branches/unified_tripod.py --audit --max-a 300
python3 projects/almost-halving-three-branches/unified_tripod.py --tree 235 223 15 --summary
python3 projects/almost-halving-three-branches/unified_tripod.py --tree 187 163 3 | python3 projects/almost-halving-three-branches/bfs_verify.py -
```

Recorded outputs (23 November 2026):

- `unittest`: `4` tests passed in `1.021s` (`15` representative triples across
  all families cross-checked by independent BFS, arm permutation invariance,
  `prove_all_families`, `audit_coverage(120)` including `346/346` grid, and
  CLI `--check -` rejection of an altered pair).
- `--prove-all`: `proof: PASS`, all `8` symbolic/arithmetic family checkers `PASS`.
- `--audit --max-a 300`: `settled: 4545073 / 4545100`, `open_count: 27`
  (`refuted_in_open_list: [227, 67, 11]`), `grid_settled: 346 / 346`.
- `--tree 235 223 15 --summary`: `family: interior_hole_c_plus_4, size=236, target=236, homometric=true`.
- `--tree 187 163 3 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 176}`.
