# Shortfall queue, third pass: two honest failures at target 41

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-shortfall-queue3-20261124`, on project
`small-after-sum-20261120`.

Neither triple closed, and a failed search proves nothing:

```sh
$ python3 open_triple_search.py 45 30 8  41 240 31
restarts=72 best_energy=2
$ python3 open_triple_search.py 40 30 14 41 240 32
restarts=66 best_energy=2
```

Running tally across the three passes today (before the concurrent
tail pass lands): 15 of the grid's 68 shortfalls settled by
BFS-verified witnesses, 53 open. The resistant set is now
`(45,20,8)` (four seeds), `(55,20,5)`, `(45,30,8)`, `(40,30,14)` —
best energy 2 in every failed run, never worse, never 0. That
uniform near-miss is itself a hint worth a structural look (is
there a profile-parity invariant these shapes share?) before more
annealing budget is spent; it is not evidence of an obstruction.
