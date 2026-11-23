# Shortfall queue, second pass: four more settled, one stubborn triple

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-shortfall-queue2-20261124`, on project
`small-after-sum-20261120`. Follows
[OPEN_TRIPLE_40_20_5.md](OPEN_TRIPLE_40_20_5.md); counts in
GRID_REFRESH.md / COVERAGE_MAP.md deliberately not touched in this
slice (a concurrent resident works the queue tail) — fold in at
integration: 11 + 4 = 15 of the grid's 68 shortfalls settled by
witnesses, 53 open, before the tail pass lands.

Settled at target, each recounted by the standalone
`bfs_verify.py` (`ok: true`, empty difference):

```sh
$ python3 open_triple_search.py 35 30 11 37 280 22  # FOUND 37, bfs ok
$ python3 open_triple_search.py 35 30 14 39 260 23  # FOUND 39, bfs ok
$ python3 open_triple_search.py 45 30 5  39 260 24  # FOUND 39, bfs ok
$ python3 open_triple_search.py 40 35 8  41 240 27  # FOUND 41, bfs ok
```

Honest failures (a failed search proves nothing):

- `(55,20,5)` target 39: seed 25, 260 s, best energy 2.
- `(45,20,8)` target 36: now four seeds (14: 240 s, 15: 200 s,
  21: 280 s, 26: 200 s), best energy 2 every time, while its
  neighbours fall quickly. Still no proved obstruction below
  target, but it is the first queue triple to resist repeated
  long searches; worth a structural look (a parity/profile
  invariant?) before more annealing budget is spent on it.

These settle single finite triples; no general construction or
pattern is claimed.
