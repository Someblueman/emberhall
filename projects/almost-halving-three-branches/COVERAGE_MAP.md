# Coverage map: which tripod triples the current proofs settle

Wren, 24 November 2026. Companion to [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md).
No code or proof changed; every claim below is either cited to a proved
document or marked as an empirical probe.

## Settled (target attained, proved for every length in the domain)

- Published formulas ([PUBLISHED_CASES.md](PUBLISHED_CASES.md)): path halves
  (all parities), separated paths (meets target iff `|a-(b+c+1)| ≤ 3`),
  alternating (equal arms every parity), odd-quotient block (domain
  check in code; the checker refuses the even-quotient overrun).
- Gap family `T(4t-1,2t,t)`, `t ≥ 2`: maximum `floor(7t/2)` (signed shells).
- Sharp family `T(4t-1,3t-1,2t-1)`, even `t`: `h = 9t/2 - 2`.
- `T(10t,7t,4t)`, `t ≥ 2`: optimum `floor(21t/2)` ([NEXT_FAMILY.md](NEXT_FAMILY.md)).
- `T(7t,5t,3t)`, all `t`: `floor(15t/2)` ([ODD_MIDDLE.md](ODD_MIDDLE.md)
  closes odd scales; PROGRESSION_TARGET covers even).
- `T(11t,8t,5t)`, all `t`: `h = 12t` ([ARITHMETIC_FAMILY.md](ARITHMETIC_FAMILY.md)).
- `T(15p+5q,10p+3q,3p)`, `p ≥ 1, q ≥ 0` (includes `T(50t,33t,9t)`, size
  `46t-1`), general block form and companion family
  ([RATIO_50_33_9.md](RATIO_50_33_9.md)).
- Arithmetic progressions `T(b+d,b,b-d)` for every `1 ≤ d < b`, `b ≥ 2`:
  full partitions classified ([PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md));
  when no full partition exists the menu attains `(3b-1)/2`.
  Odd-middle even/odd spacing families
  ([NEXT_ODD_FAMILY.md](NEXT_ODD_FAMILY.md), [ODD_SPACING.md](ODD_SPACING.md),
  [GENERAL_ODD_SPACING.md](GENERAL_ODD_SPACING.md)) are dispatched inside
  this coverage.
- Scaling `T(99t,79t,23t)`: every `t ≢ 1 (mod 2660)` attains the target
  `floor((201t+1)/2)-1` by full-prefix Euler cells, and the target is
  optimal at odd `t` ([GAP_99_79_23.md](GAP_99_79_23.md),
  [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md)).

## The open region

1. **Scaling class `t ≡ 1 (mod 2660)`, `t > 1`** (first `t = 2661`).
   Target is proved to be an upper bound and proved unattainable by any
   full-prefix pair; no affine exact-polynomial certificate exists
   ([RESIDUE_2660.md](RESIDUE_2660.md)). Attainment by an interior-hole
   pair is neither proved nor refuted.
2. **General unsolved triples.** The menu's maximum is often 1–2 below
   the target. An empirical probe on a coarse grid (`a=5..55 step 5`,
   `b<a step 5`, `c<b step 3`) through the default `published_cases.py`
   `best` construction settled 278 triples and left 68 open, e.g.
   `(25,20,8)` size 25 vs target 26, `(40,35,17)` 43 vs 45. Annealing
   has since settled 11 of those 68 by explicit BFS-verified
   witnesses ([GRID_REFRESH.md](GRID_REFRESH.md),
   [OPEN_TRIPLE_40_20_5.md](OPEN_TRIPLE_40_20_5.md)); 57 remain open.
   These are
   **unsettled here, not counterexamples**: the only certified upper
   bounds in the project are disjointness (`floor((1+a+b+c)/2)`) and the
   residue / progression obstructions to full partitions, and none of
   the open triples meets a condition for a proved obstruction below
   the target. A menu shortfall proves nothing about the tree — as the
   history shows: `(99,79,23)` looked one-short at 99 until the
   interior-certificate pair of size 100 was found, and `T(10t,7t,4t)`
   was bounded by `10t+3` by the old menu before the exact construction
   gave `floor(21t/2)`.

## What would close the milestone

- A construction (not necessarily a full-prefix or affine-cell form)
  attaining the target at `t = 2661`, or an all-pairs obstruction family
  with a rigorous upper bound below the target — either would settle
  the scaling class; only the latter refutes anything.
- For arbitrary triples, a general construction or a general
  obstruction family. Finite censuses settle neither.
