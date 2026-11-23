# Coverage grid, recomputed — and its smallest shortfalls attacked

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-coverage-grid-refresh-20261124`, on project
`small-after-sum-20261120`.

## The grid reproduces

[COVERAGE_MAP.md](COVERAGE_MAP.md) reports an empirical probe: on the
grid `a=5..55 step 5`, `b<a step 5`, `c<b step 3` (c from 2), the default
`published_cases.py` `best` construction settled 278 triples and left 68
open. Recomputed today with `construct((a,b,c), "best")` and `check_pair`
(`meets_target`), the count is identical: **346 triples, 278 settled, 68
short**. The 68 shortfalls, smallest trees first, are listed at the end.

## Seven of the 68 now attain their targets

Annealing (`open_triple_search.py`) plus independent `bfs_verify.py`
checks settled these today, each by an explicit witness file verified
`ok` at target size: `(25,20,8)` 26, `(30,20,5)` 27, `(40,10,5)` 27,
`(30,25,8)` 31, `(35,25,5)` 32, `(30,25,11)` 32, `(40,35,17)` 45
(see OPEN_TRIPLE_25_20_8.md and OPEN_TRIPLE_40_35_17.md for the first
and last). Budgets were 90 s per triple except 240–560 s for the two
documented separately.

One attempt did not close: `(40,20,5)` at target 32 stopped at best
energy 2 under two seeds (90 s each). That proves nothing; the triple
remains open, at the head of the queue below.

## Update, later the same day (task volmer-shortfall-queue-20261124)

`(40,20,5)` closed at 240 s (seed 11), as did `(40,25,5)` 34,
`(35,30,8)` 36 and `(40,30,5)` 37 — all BFS-verified; see
[OPEN_TRIPLE_40_20_5.md](OPEN_TRIPLE_40_20_5.md). `(45,20,8)` and
`(35,30,11)` resisted (best energy 2). That makes 11 of the 68
settled by witnesses, 57 open.

## Update, at integration (task volmer-gridfold-20261124)

All three later passes are now integrated, so the tally can be
folded in. Queue two settled `(35,30,11)` 37, `(35,30,14)` 39,
`(45,30,5)` 39 and `(40,35,8)` 41 (all BFS-verified; see
[OPEN_TRIPLES_QUEUE2.md](OPEN_TRIPLES_QUEUE2.md)); queue three
added no witness ([OPEN_TRIPLES_QUEUE3.md](OPEN_TRIPLES_QUEUE3.md));
the concurrent tail pass settled `(55,45,29)` 64 (BFS-verified; see
[OPEN_TRIPLE_TAIL_20261124.md](OPEN_TRIPLE_TAIL_20261124.md)).
That makes **16 of the 68 shortfalls settled by witnesses, 52 open**.

The resistant set — best energy 2 in every failed run, never 0 —
is `(45,20,8)` (four seeds), `(55,20,5)`, `(45,30,8)` and
`(40,30,14)`, with `(55,50,35)` and `(55,50,23)` also reaching
energy 2 in the tail pass. A failed search proves nothing and no
obstruction is claimed for any of them; the uniform near-miss is
the next thing to look at structurally (a profile-parity invariant
these shapes share?) before more annealing budget is spent.

## What this means

Fifty-two grid triples remain unsettled, all in the menu-shortfall
sense only; none carries a proved obstruction below target. Seven of
eight attempts closed quickly, which is more evidence — not proof —
that the shortfall is the menu's. Finite witnesses settle single
triples. The milestone still needs a general construction or a general
obstruction (or settling `t = 2661`); the searcher is now the cheap way
to clear specific triples off this list. The tallies above are now
folded into this file; COVERAGE_MAP.md still carries the older count
and should be updated from the 16-settled / 52-open tally here.

## The 68 menu shortfalls (smallest first)

```
(25,20,8) menu 25 target 26
(30,20,5) menu 26 target 27
(40,10,5) menu 26 target 27
(30,25,8) menu 30 target 31
(35,25,5) menu 31 target 32
(40,20,5) menu 31 target 32
(30,25,11) menu 30 target 32
(40,25,5) menu 33 target 34
(35,30,8) menu 35 target 36
(45,20,8) menu 35 target 36
(40,30,5) menu 36 target 37
(35,30,11) menu 35 target 37
(35,30,14) menu 37 target 39
(45,30,5) menu 38 target 39
(55,20,5) menu 38 target 39
(40,35,8) menu 40 target 41
(45,30,8) menu 39 target 41
(40,30,14) menu 40 target 41
(40,25,20) menu 41 target 42
(45,35,5) menu 41 target 42
(50,30,5) menu 40 target 42
(55,25,5) menu 41 target 42
(40,35,11) menu 40 target 42
(40,35,14) menu 42 target 44
(50,35,5) menu 43 target 44
(55,25,11) menu 44 target 45
(40,35,17) menu 43 target 45
(45,40,8) menu 45 target 46
(50,35,8) menu 44 target 46
(55,30,8) menu 45 target 46
(45,35,14) menu 45 target 46
(40,35,20) menu 46 target 47
(50,40,5) menu 46 target 47
(55,35,5) menu 45 target 47
(45,40,11) menu 45 target 47
(45,35,17) menu 47 target 48
(55,35,8) menu 45 target 48
(45,40,14) menu 47 target 49
(55,40,5) menu 48 target 49
(55,35,11) menu 49 target 50
(45,40,17) menu 48 target 50
(50,45,8) menu 50 target 51
(55,40,8) menu 49 target 51
(50,40,14) menu 50 target 51
(45,40,20) menu 50 target 52
(55,45,5) menu 51 target 52
(50,45,11) menu 50 target 52
(50,40,17) menu 50 target 53
(50,45,14) menu 52 target 54
(50,45,17) menu 53 target 55
(55,50,8) menu 55 target 56
(55,45,14) menu 55 target 56
(50,45,20) menu 55 target 57
(55,40,20) menu 56 target 57
(55,50,11) menu 55 target 57
(55,45,17) menu 55 target 58
(50,45,23) menu 56 target 58
(55,50,14) menu 57 target 59
(55,45,20) menu 55 target 59
(55,50,17) menu 58 target 60
(55,45,23) menu 56 target 61
(55,50,20) menu 60 target 62
(50,45,32) menu 62 target 63
(55,50,23) menu 61 target 63
(55,45,29) menu 63 target 64
(55,50,26) menu 63 target 65
(55,50,29) menu 65 target 66
(55,50,35) menu 68 target 69
```
