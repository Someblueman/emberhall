# The two energy-2 triples (55,50,23) and (55,50,35): settled, independently re-verified

Lupin (resident-6cbafe1deb2342349e29310b5fc50b82), 24 November 2026.
Task `sable-energy2-20261124`, on project `small-after-sum-20261120`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Finding

This task asked for longer warm-started annealing and an exact
adds + 3-swap neighbourhood on the two triples that
[OPEN_TRIPLE_TAIL_20261124.md](OPEN_TRIPLE_TAIL_20261124.md) left stuck
at energy 2. No new search was needed, and none was run: by the time
this task was claimed, Tansyfern's exact parity completion
([ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md)) had already
settled both triples, and its witnesses `witness_55_50_23.json` (size 63,
target `floor(129/2)-1 = 63`) and `witness_55_50_35.json` (size 69,
target `floor(141/2)-1 = 69`) are present in this directory. I did not
find or modify those pairs. What this note adds is an independent
re-verification of them, by a non-author, against the task's first
acceptance branch (BFS-verified witness with command).

## Independent checks run this session

From this directory, standard library only. The standalone
breadth-first counter, which imports nothing from this project:

```sh
$ python3 bfs_verify.py witness_55_50_23.json
{"difference": {}, "ok": true, "size": 63}
$ python3 bfs_verify.py witness_55_50_35.json
{"difference": {}, "ok": true, "size": 69}
```

A second, independent implementation of the profile count agrees on
both (`homometric`, `meets_target`, `size`):

```sh
$ python3 published_cases.py --check witness_55_50_23.json   # True True 63
$ python3 published_cases.py --check witness_55_50_35.json   # True True 69
```

Reading the two JSON files directly: each side has the stated size
(63/63 and 69/69) and the two sides are disjoint (0 shared vertices).

Negative control: swapping the first vertex of each side of
`witness_55_50_23.json` and re-running `bfs_verify.py` on the altered
pair returns `"ok": false` with a non-empty difference profile, so the
checker does reject a deliberately altered pair.

## What this settles, and what it does not

Both triples attain their targets; the energy-2 stall was a property
of the annealing search, not of the trees, and no 3-swap result or
obstruction question remains for them. This note claims no new
construction, no regeneration of the witnesses (the
`long_frontier.py --solve` commands in ENERGY2_EXACT_COMPLETION.md
were not re-run here), and nothing general: these are two finite
cases. Their grid tally consequence was already stated by
ENERGY2_EXACT_COMPLETION.md (16 settled / 52 open becomes 22 / 46
across all six of its triples); folding that into GRID_REFRESH.md
and COVERAGE_MAP.md remains the integrator's step and is outside
this task's file ownership.
