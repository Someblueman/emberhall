# Four more shortfall triples attain their targets

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-shortfall-queue-20261124`, on project
`small-after-sum-20261120`.

[GRID_REFRESH.md](GRID_REFRESH.md) left `(40,20,5)` at the head of the
open queue after two 90 s seeds stopped at energy 2. With a 240 s
budget the annealer closed it, and three more queue triples fell in
the same pass. Each witness was recounted independently by
`bfs_verify.py` (standalone BFS, imports nothing from the project):

```sh
$ python3 open_triple_search.py 40 20 5 32 240 11
restarts=3 best_energy=0
FOUND size=32 wrote witness_40_20_5.json
$ python3 bfs_verify.py witness_40_20_5.json
{"difference": {}, "ok": true, "size": 32}
$ python3 open_triple_search.py 40 25 5 34 240 12   # FOUND size=34, bfs ok
$ python3 open_triple_search.py 35 30 8 36 240 13   # FOUND size=36, bfs ok
$ python3 open_triple_search.py 40 30 5 37 200 16   # FOUND size=37, bfs ok
```

Two attempts did not close and prove nothing: `(45,20,8)` at target
36 stopped at best energy 2 under seeds 14 (240 s) and 15 (200 s);
`(35,30,11)` at target 37 stopped at best energy 2 under seed 17
(200 s). Both stay open with no proved obstruction below target.

Count so far: of the grid's 68 shortfalls, 7 settled in
GRID_REFRESH plus these 4 makes 11 settled by explicit witnesses,
57 still open. These are single finite triples, not a general
construction; no pattern in the pairs is claimed.
