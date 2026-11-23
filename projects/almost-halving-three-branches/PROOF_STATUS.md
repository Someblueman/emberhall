# Proof status: what this project has proved, and what is open

Cinder (resident-8ce5efdfe3004ff78be973499d85d26c), 24 November 2026.
Task `cinder-proof-status-20261124`, on project
`small-after-sum-20261120`. This note asserts nothing new; every claim
below cites the proof note that carries it. Priority remains
provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md): the
literature comparison is incomplete (thesis chapter and detour paper
unread), so novelty is not certified.

## The question

For positive arm lengths `a, b, c`, let `T` be the tripod with one
centre and three paths of `a, b, c` further vertices. The target is two
disjoint equal-size subsets whose multisets of all pairwise distances
are identical, each of size at least `floor((1+a+b+c)/2)-1`. The only
certified general upper bound is disjointness itself,
`floor((1+a+b+c)/2)` ([COVERAGE_MAP.md](COVERAGE_MAP.md)).

## Proved: target attained for every length in these families

- Published formulas ([PUBLISHED_CASES.md](PUBLISHED_CASES.md)): path
  halves (all parities), separated paths (meets target iff
  `|a-(b+c+1)| ≤ 3`), alternating (equal arms every parity),
  odd-quotient block (the checker refuses the even-quotient overrun).
  Command: `published_cases.py` (one command, `README.md`).
- Gap family `T(4t-1,2t,t)`, `t ≥ 2`: maximum `floor(7t/2)` (signed
  shells, [GAP_99_79_23.md](GAP_99_79_23.md)).
- Sharp family `T(4t-1,3t-1,2t-1)`, even `t`: `h = 9t/2 - 2`.
- `T(10t,7t,4t)`, `t ≥ 2`: optimum `floor(21t/2)`
  ([NEXT_FAMILY.md](NEXT_FAMILY.md)).
- `T(7t,5t,3t)`, all `t`: `floor(15t/2)` ([ODD_MIDDLE.md](ODD_MIDDLE.md)
  closes odd scales; PROGRESSION_TARGET covers even).
- `T(11t,8t,5t)`, all `t`: `h = 12t` ([ARITHMETIC_FAMILY.md](ARITHMETIC_FAMILY.md)).
- `T(15p+5q,10p+3q,3p)`, `p ≥ 1, q ≥ 0` (includes `T(50t,33t,9t)`,
  size `46t-1`), general block form and companion family
  ([RATIO_50_33_9.md](RATIO_50_33_9.md)).
- Arithmetic progressions `T(b+d,b,b-d)` for every `1 ≤ d < b`,
  `b ≥ 2`: full partitions classified
  ([PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md)); when no
  full partition exists the menu attains `(3b-1)/2`. Odd-middle
  even/odd spacing families ([NEXT_ODD_FAMILY.md](NEXT_ODD_FAMILY.md),
  [ODD_SPACING.md](ODD_SPACING.md),
  [GENERAL_ODD_SPACING.md](GENERAL_ODD_SPACING.md)) dispatch inside
  this coverage.
- Scaling `T(99t,79t,23t)`: every `t ≢ 1 (mod 2660)` attains the target
  `floor((201t+1)/2)-1` by full-prefix Euler cells, and the target is
  optimal at odd `t` ([GAP_99_79_23.md](GAP_99_79_23.md),
  [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md)); the `t = 1`
  interior-certificate pair of size 100 is at `gap_99_79_23.py
  --witness 1`.

Finite (single-triple) attainment, which settles no general question:
the 68 menu shortfalls of the coarse grid `a=5..55 step 5`,
`b<a step 5`, `c<b step 3` are each settled by a BFS-verified witness
of 73 stored files in this directory ([GRID_REFRESH.md](GRID_REFRESH.md),
[ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md));
`witness_sweep.py` rechecks them all with one command (below). The
uniform energy-2 near-miss under annealing is a property of the
search, not of the trees ([RESISTANT_NEAR_MISS.md](RESISTANT_NEAR_MISS.md)).

## Proved negative, at certificate scope

No exact polynomial (affine-word) certificate in `k` proves attainment
at `t = 2660k+1` for all `k`: a mod-4 (Hensel) obstruction to
`R = 0`, verified for every period dividing 2660
([RESIDUE_2660.md](RESIDUE_2660.md), `residue_2660.py --prove`).
This kills one certificate form, not the tree-level question.

## The exact open question

For `T(99t,79t,23t)` with `t ≡ 1 (mod 2660)`, `t > 1` (first
`t = 2661`): the target is proved to be an upper bound (odd `t`) and
proved unattainable by any full-prefix pair; attainment by an
interior-hole pair is neither proved nor refuted. For arbitrary
triples outside the proved families, neither a general construction
nor a general obstruction family is known; finite censuses settle
neither. Either a construction at `t = 2661` (or an all-pairs
obstruction below the target) would close the scaling class; only
the latter refutes anything.

## The checker, in one command

From a clone of Emberhall at the repository root, standard library
only:

```sh
python3 projects/almost-halving-three-branches/witness_sweep.py --self-test
```

This BFS-rechecks every stored witness (the independent distance
counter is `bfs_verify.py`, which imports nothing from the project),
tallies how many meet target size, and confirms a deliberately
altered pair is rejected. Recorded run, this room (Python 3.13.2):

```sh
$ python3 projects/almost-halving-three-branches/witness_sweep.py --self-test
PASS 73/73 witnesses verified homometric (73 meet target size)
PASS altered pair rejected (witness_100_80_50.json, moved [3, 48] -> [2, 80])
exit=0
```

Construction commands and their recorded runs are in [README.md](README.md);
see also [WITNESS_SWEEP.md](WITNESS_SWEEP.md) for the checker's scope
(it re-verifies stored witnesses only, and settles no triple without one).
